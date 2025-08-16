#!/usr/bin/env python3
"""
Filesystem连接器性能分析工具
分析高CPU使用率问题并提供优化建议
"""

import os
import sys
import time
import json
import psutil
import threading
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict, deque
from typing import Dict, List, Any, Optional
import signal

class PerformanceAnalyzer:
    def __init__(self, connector_process_name: str = "linch-mind-filesystem"):
        self.connector_process_name = connector_process_name
        self.process: Optional[psutil.Process] = None
        self.monitoring = False
        self.metrics = defaultdict(list)
        self.fs_events = deque(maxlen=1000)  # 保持最近1000个FS事件
        self.analysis_results = {}
        
    def find_connector_process(self) -> Optional[psutil.Process]:
        """查找filesystem连接器进程"""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_info']):
            try:
                if self.connector_process_name in proc.info['name'] or \
                   any(self.connector_process_name in arg for arg in proc.info['cmdline'] or []):
                    return psutil.Process(proc.info['pid'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return None
    
    def collect_system_metrics(self) -> Dict[str, Any]:
        """收集系统和进程性能指标"""
        if not self.process:
            return {}
        
        try:
            # 进程基础指标
            cpu_percent = self.process.cpu_percent()
            memory_info = self.process.memory_info()
            
            # I/O计数器（可能不支持所有平台）
            try:
                io_counters = self.process.io_counters()
                io_read_count = io_counters.read_count
                io_write_count = io_counters.write_count
                io_read_bytes = io_counters.read_bytes
                io_write_bytes = io_counters.write_bytes
            except (AttributeError, psutil.AccessDenied):
                io_read_count = io_write_count = io_read_bytes = io_write_bytes = 0
            
            # 系统整体指标
            system_cpu = psutil.cpu_percent(interval=0.1)
            system_memory = psutil.virtual_memory()
            
            # 线程和文件描述符
            num_threads = self.process.num_threads()
            try:
                if hasattr(self.process, 'num_fds'):
                    num_fds = self.process.num_fds()
                else:
                    # macOS/Windows fallback
                    num_fds = len(self.process.open_files())
            except (AttributeError, psutil.AccessDenied):
                num_fds = 0
            
            return {
                'timestamp': datetime.now(),
                'process': {
                    'cpu_percent': cpu_percent,
                    'memory_rss': memory_info.rss,
                    'memory_vms': memory_info.vms,
                    'io_read_count': io_read_count,
                    'io_write_count': io_write_count,
                    'io_read_bytes': io_read_bytes,
                    'io_write_bytes': io_write_bytes,
                    'num_threads': num_threads,
                    'num_fds': num_fds,
                },
                'system': {
                    'cpu_percent': system_cpu,
                    'memory_percent': system_memory.percent,
                    'memory_available': system_memory.available,
                }
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            print(f"无法收集进程指标: {e}")
            return {}
    
    def monitor_fs_events(self):
        """监控文件系统事件（通过系统调用监控）"""
        try:
            if sys.platform == 'darwin':
                # macOS: 使用fs_usage监控
                cmd = ['sudo', 'fs_usage', '-f', 'filesys', '-p', str(self.process.pid)]
            elif sys.platform.startswith('linux'):
                # Linux: 使用strace监控系统调用
                cmd = ['strace', '-p', str(self.process.pid), '-e', 'trace=file']
            else:
                print("不支持的操作系统")
                return
            
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                  text=True, preexec_fn=os.setsid)
            
            while self.monitoring:
                line = proc.stdout.readline()
                if line:
                    self.fs_events.append({
                        'timestamp': datetime.now(),
                        'event': line.strip()
                    })
                    
        except Exception as e:
            print(f"监控FS事件失败: {e}")
    
    def analyze_monitored_directories(self) -> Dict[str, Any]:
        """分析被监控的目录统计信息"""
        # 读取连接器配置
        config_path = Path(__file__).parent.parent.parent / "connectors/official/filesystem/connector.toml"
        
        if not config_path.exists():
            return {"error": "连接器配置文件不存在"}
        
        # 从配置获取监控目录
        watch_dirs = ["~/Desktop", "~/Documents"]  # 默认配置
        
        analysis = {
            'directories': [],
            'total_files': 0,
            'total_size': 0,
            'file_types': defaultdict(int),
            'large_files': [],
            'deep_directories': []
        }
        
        for watch_dir in watch_dirs:
            expanded_dir = Path(watch_dir).expanduser()
            if not expanded_dir.exists():
                continue
            
            dir_analysis = self._analyze_directory(expanded_dir)
            analysis['directories'].append(dir_analysis)
            analysis['total_files'] += dir_analysis['file_count']
            analysis['total_size'] += dir_analysis['total_size']
            
            # 合并文件类型统计
            for ext, count in dir_analysis['file_types'].items():
                analysis['file_types'][ext] += count
        
        return analysis
    
    def _analyze_directory(self, directory: Path, max_depth: int = 5) -> Dict[str, Any]:
        """分析单个目录的详细信息"""
        analysis = {
            'path': str(directory),
            'file_count': 0,
            'directory_count': 0,
            'total_size': 0,
            'max_depth_reached': 0,
            'file_types': defaultdict(int),
            'large_files': [],  # > 10MB
            'recent_files': [],  # 最近修改的文件
            'problematic_paths': []  # 可能导致高频事件的路径
        }
        
        try:
            for item in directory.rglob('*'):
                try:
                    # 检查深度
                    depth = len(item.relative_to(directory).parts)
                    analysis['max_depth_reached'] = max(analysis['max_depth_reached'], depth)
                    
                    if depth > max_depth:
                        continue
                    
                    if item.is_file():
                        analysis['file_count'] += 1
                        size = item.stat().st_size
                        analysis['total_size'] += size
                        
                        # 文件类型统计
                        ext = item.suffix.lower()
                        analysis['file_types'][ext] += 1
                        
                        # 大文件
                        if size > 10 * 1024 * 1024:  # > 10MB
                            analysis['large_files'].append({
                                'path': str(item),
                                'size': size,
                                'size_mb': size / (1024 * 1024)
                            })
                        
                        # 最近修改的文件
                        mtime = datetime.fromtimestamp(item.stat().st_mtime)
                        if mtime > datetime.now() - timedelta(minutes=30):
                            analysis['recent_files'].append({
                                'path': str(item),
                                'mtime': mtime
                            })
                        
                        # 检查问题路径
                        if self._is_problematic_path(item):
                            analysis['problematic_paths'].append(str(item))
                    
                    elif item.is_dir():
                        analysis['directory_count'] += 1
                        
                except (OSError, PermissionError):
                    continue
                    
        except Exception as e:
            analysis['error'] = str(e)
        
        return analysis
    
    def _is_problematic_path(self, path: Path) -> bool:
        """识别可能导致高频事件的路径"""
        problematic_patterns = [
            '.DS_Store', 'Thumbs.db', '~$', '.tmp', '.log',
            '__pycache__', 'node_modules', '.git', '.cache',
            'Cache', 'Logs', 'Temp'
        ]
        
        path_str = str(path).lower()
        return any(pattern.lower() in path_str for pattern in problematic_patterns)
    
    def start_monitoring(self, duration: int = 60):
        """开始性能监控"""
        self.process = self.find_connector_process()
        if not self.process:
            print(f"未找到{self.connector_process_name}进程")
            return
        
        print(f"开始监控进程 PID {self.process.pid} 持续 {duration} 秒...")
        self.monitoring = True
        
        # 启动FS事件监控线程
        fs_thread = threading.Thread(target=self.monitor_fs_events, daemon=True)
        fs_thread.start()
        
        # 收集性能指标
        start_time = time.time()
        while time.time() - start_time < duration and self.monitoring:
            metrics = self.collect_system_metrics()
            if metrics:
                self.metrics['timeline'].append(metrics)
            time.sleep(1)
        
        self.monitoring = False
        print("监控完成")
    
    def analyze_performance_issues(self) -> Dict[str, Any]:
        """分析性能问题并生成报告"""
        if not self.metrics['timeline']:
            return {"error": "没有收集到性能数据"}
        
        # CPU使用率分析
        cpu_values = [m['process']['cpu_percent'] for m in self.metrics['timeline']]
        avg_cpu = sum(cpu_values) / len(cpu_values)
        max_cpu = max(cpu_values)
        
        # 内存使用分析
        memory_values = [m['process']['memory_rss'] for m in self.metrics['timeline']]
        avg_memory = sum(memory_values) / len(memory_values)
        max_memory = max(memory_values)
        
        # I/O分析
        if len(self.metrics['timeline']) > 1:
            io_read_diff = (self.metrics['timeline'][-1]['process']['io_read_count'] - 
                           self.metrics['timeline'][0]['process']['io_read_count'])
            io_write_diff = (self.metrics['timeline'][-1]['process']['io_write_count'] - 
                            self.metrics['timeline'][0]['process']['io_write_count'])
        else:
            io_read_diff = io_write_diff = 0
        
        # 线程和文件描述符分析
        thread_values = [m['process']['num_threads'] for m in self.metrics['timeline']]
        fd_values = [m['process']['num_fds'] for m in self.metrics['timeline']]
        
        analysis = {
            'performance_summary': {
                'avg_cpu_percent': avg_cpu,
                'max_cpu_percent': max_cpu,
                'avg_memory_mb': avg_memory / (1024 * 1024),
                'max_memory_mb': max_memory / (1024 * 1024),
                'io_read_operations': io_read_diff,
                'io_write_operations': io_write_diff,
                'avg_threads': sum(thread_values) / len(thread_values),
                'max_file_descriptors': max(fd_values),
            },
            'issues_identified': [],
            'recommendations': []
        }
        
        # 问题识别
        if avg_cpu > 50:
            analysis['issues_identified'].append({
                'type': 'high_cpu_usage',
                'severity': 'critical' if avg_cpu > 80 else 'high',
                'description': f'平均CPU使用率 {avg_cpu:.1f}% 过高',
                'impact': 'CPU资源过度消耗，影响系统整体性能'
            })
        
        if max_memory > 500 * 1024 * 1024:  # > 500MB
            analysis['issues_identified'].append({
                'type': 'high_memory_usage',
                'severity': 'high',
                'description': f'内存使用峰值 {max_memory/(1024*1024):.1f}MB 过高',
                'impact': '内存消耗过大，可能导致系统响应缓慢'
            })
        
        if io_read_diff > 10000:  # 高频I/O
            analysis['issues_identified'].append({
                'type': 'excessive_io',
                'severity': 'high',
                'description': f'I/O操作过于频繁 ({io_read_diff} 次读取)',
                'impact': '频繁的磁盘I/O操作消耗CPU和系统资源'
            })
        
        if max(fd_values) > 100:
            analysis['issues_identified'].append({
                'type': 'too_many_file_descriptors',
                'severity': 'medium',
                'description': f'文件描述符使用过多 ({max(fd_values)})',
                'impact': '可能存在文件描述符泄漏或监控过多文件'
            })
        
        # FS事件分析
        if len(self.fs_events) > 500:  # 高频事件
            analysis['issues_identified'].append({
                'type': 'excessive_fs_events',
                'severity': 'critical',
                'description': f'文件系统事件过于频繁 ({len(self.fs_events)} 个事件)',
                'impact': '文件系统事件处理过载，导致CPU使用率飙升'
            })
        
        # 生成优化建议
        self._generate_recommendations(analysis)
        
        return analysis
    
    def _generate_recommendations(self, analysis: Dict[str, Any]):
        """生成优化建议"""
        recommendations = []
        
        issues = {issue['type'] for issue in analysis['issues_identified']}
        
        if 'high_cpu_usage' in issues:
            recommendations.append({
                'priority': 'critical',
                'category': 'configuration',
                'title': '调整事件批处理配置',
                'description': '增加batch_interval和debounce_time以减少事件处理频率',
                'implementation': '将batch_interval从300ms增加到1000ms，debounce_time从300ms增加到2000ms'
            })
        
        if 'excessive_fs_events' in issues:
            recommendations.append({
                'priority': 'critical',
                'category': 'filtering',
                'title': '优化路径过滤策略',
                'description': '排除更多不必要的文件和目录以减少事件噪音',
                'implementation': '添加更多排除模式，如临时文件、缓存目录、系统文件等'
            })
        
        if 'excessive_io' in issues:
            recommendations.append({
                'priority': 'high',
                'category': 'algorithm',
                'title': '优化FSEvents处理逻辑',
                'description': '改进事件处理算法，减少不必要的文件系统访问',
                'implementation': '延迟文件大小检查，优化路径匹配算法，实施事件聚合'
            })
        
        recommendations.append({
            'priority': 'medium',
            'category': 'monitoring',
            'title': '实施监控目录预分析',
            'description': '在启动时分析监控目录，识别和排除高频变化的路径',
            'implementation': '添加目录预扫描逻辑，自动检测和排除缓存、日志等目录'
        })
        
        recommendations.append({
            'priority': 'medium',
            'category': 'configuration',
            'title': '启用智能监控模式',
            'description': '根据目录特征自动调整监控策略',
            'implementation': '对大目录使用更长的去重时间，对小目录保持快速响应'
        })
        
        analysis['recommendations'] = recommendations
    
    def generate_report(self) -> str:
        """生成性能分析报告"""
        # 分析监控目录
        dir_analysis = self.analyze_monitored_directories()
        
        # 分析性能问题
        perf_analysis = self.analyze_performance_issues()
        
        report = []
        report.append("# Filesystem连接器性能分析报告")
        report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # 监控目录概况
        report.append("## 监控目录概况")
        if 'error' not in dir_analysis:
            report.append(f"- 总文件数: {dir_analysis['total_files']:,}")
            report.append(f"- 总大小: {dir_analysis['total_size'] / (1024*1024*1024):.2f} GB")
            report.append("- 文件类型分布:")
            for ext, count in sorted(dir_analysis['file_types'].items(), key=lambda x: x[1], reverse=True)[:10]:
                report.append(f"  - {ext or '无扩展名'}: {count} 个文件")
        else:
            report.append(f"❌ 分析失败: {dir_analysis['error']}")
        report.append("")
        
        # 性能问题总结
        if 'error' not in perf_analysis:
            summary = perf_analysis['performance_summary']
            report.append("## 性能指标总结")
            report.append(f"- 平均CPU使用率: {summary['avg_cpu_percent']:.1f}%")
            report.append(f"- 峰值CPU使用率: {summary['max_cpu_percent']:.1f}%")
            report.append(f"- 平均内存使用: {summary['avg_memory_mb']:.1f} MB")
            report.append(f"- 峰值内存使用: {summary['max_memory_mb']:.1f} MB")
            report.append(f"- I/O读取操作: {summary['io_read_operations']:,}")
            report.append(f"- 平均线程数: {summary['avg_threads']:.1f}")
            report.append(f"- 最大文件描述符: {summary['max_file_descriptors']}")
            report.append("")
            
            # 问题识别
            if perf_analysis['issues_identified']:
                report.append("## 🚨 识别的性能问题")
                for issue in perf_analysis['issues_identified']:
                    severity_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡"}.get(issue['severity'], "⚪")
                    report.append(f"### {severity_emoji} {issue['description']}")
                    report.append(f"**严重级别**: {issue['severity']}")
                    report.append(f"**影响**: {issue['impact']}")
                    report.append("")
            
            # 优化建议
            if perf_analysis['recommendations']:
                report.append("## 💡 优化建议")
                for i, rec in enumerate(perf_analysis['recommendations'], 1):
                    priority_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(rec['priority'], "⚪")
                    report.append(f"### {priority_emoji} {i}. {rec['title']}")
                    report.append(f"**优先级**: {rec['priority']}")
                    report.append(f"**类别**: {rec['category']}")
                    report.append(f"**描述**: {rec['description']}")
                    report.append(f"**实施方案**: {rec['implementation']}")
                    report.append("")
        else:
            report.append(f"❌ 性能分析失败: {perf_analysis['error']}")
        
        # FS事件统计
        if self.fs_events:
            report.append("## 文件系统事件统计")
            report.append(f"- 监控期间捕获事件: {len(self.fs_events)}")
            recent_events = [e for e in self.fs_events if e['timestamp'] > datetime.now() - timedelta(minutes=5)]
            report.append(f"- 最近5分钟事件: {len(recent_events)}")
            if recent_events:
                report.append("- 最近事件样例:")
                for event in list(recent_events)[-5:]:
                    report.append(f"  - {event['timestamp'].strftime('%H:%M:%S')}: {event['event'][:100]}...")
        
        return "\n".join(report)

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Filesystem连接器性能分析工具")
    parser.add_argument("--duration", "-d", type=int, default=60, help="监控时长（秒）")
    parser.add_argument("--output", "-o", help="输出报告文件路径")
    parser.add_argument("--process-name", default="linch-mind-filesystem", help="连接器进程名称")
    
    args = parser.parse_args()
    
    analyzer = PerformanceAnalyzer(args.process_name)
    
    # 处理Ctrl+C
    def signal_handler(signum, frame):
        print("\n收到中断信号，停止监控...")
        analyzer.monitoring = False
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # 开始监控
        analyzer.start_monitoring(args.duration)
        
        # 生成报告
        report = analyzer.generate_report()
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"报告已保存到: {args.output}")
        else:
            print(report)
            
    except KeyboardInterrupt:
        print("\n监控被用户中断")
    except Exception as e:
        print(f"分析失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()