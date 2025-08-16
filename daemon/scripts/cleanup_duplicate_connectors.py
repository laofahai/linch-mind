#!/usr/bin/env python3
"""
紧急清理重复连接器进程的脚本
用于处理多进程CPU风暴等紧急情况
"""

import sys
import psutil
import logging
from pathlib import Path
from typing import List, Dict, Set

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.connectors.process_manager import ProcessManager
from core.service_facade import get_service

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def find_linch_mind_processes() -> List[Dict]:
    """查找所有Linch Mind相关进程"""
    processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_percent', 'create_time']):
        try:
            proc_info = proc.info
            
            # 检查是否为Linch Mind相关进程
            name = proc_info.get('name', '').lower()
            cmdline_list = proc_info.get('cmdline', [])
            cmdline = ' '.join(cmdline_list) if cmdline_list else ''
            cmdline = cmdline.lower()
            
            if any(keyword in name or keyword in cmdline for keyword in [
                'linch-mind', 'linch_mind', 'filesystem', 'clipboard'
            ]):
                processes.append({
                    'pid': proc_info['pid'],
                    'name': proc_info['name'],
                    'cmdline': proc_info.get('cmdline', []),
                    'cpu_percent': proc_info.get('cpu_percent', 0),
                    'memory_percent': proc_info.get('memory_percent', 0),
                    'create_time': proc_info.get('create_time', 0)
                })
                
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    
    return processes


def find_duplicate_connectors(processes: List[Dict]) -> Dict[str, List[Dict]]:
    """查找重复的连接器进程"""
    connector_processes = {}
    
    for proc in processes:
        cmdline = ' '.join(proc['cmdline'])
        
        # 识别连接器类型
        connector_type = None
        if 'filesystem' in cmdline.lower():
            connector_type = 'filesystem'
        elif 'clipboard' in cmdline.lower():
            connector_type = 'clipboard'
        elif 'linch-mind' in cmdline.lower():
            # 通用连接器检测
            for part in cmdline.split():
                if 'linch-mind-' in part:
                    connector_type = part.replace('linch-mind-', '').split('.')[0]
                    break
        
        if connector_type:
            if connector_type not in connector_processes:
                connector_processes[connector_type] = []
            connector_processes[connector_type].append(proc)
    
    # 过滤出有重复进程的连接器
    duplicates = {k: v for k, v in connector_processes.items() if len(v) > 1}
    
    return duplicates


def cleanup_duplicate_processes(duplicates: Dict[str, List[Dict]], dry_run: bool = True) -> int:
    """清理重复进程"""
    cleaned_count = 0
    
    for connector_type, processes in duplicates.items():
        logger.info(f"处理重复的 {connector_type} 连接器进程:")
        
        # 按创建时间排序，保留最新的进程
        processes_sorted = sorted(processes, key=lambda x: x['create_time'])
        
        # 保留最新进程，清理其他
        to_keep = processes_sorted[-1]
        to_kill = processes_sorted[:-1]
        
        logger.info(f"  保留进程: PID {to_keep['pid']} (创建于 {to_keep['create_time']})")
        
        for proc in to_kill:
            logger.info(f"  {'[DRY RUN] ' if dry_run else ''}准备清理: PID {proc['pid']} (CPU: {proc['cpu_percent']:.1f}%)")
            
            if not dry_run:
                try:
                    psutil_proc = psutil.Process(proc['pid'])
                    psutil_proc.terminate()
                    
                    # 等待进程终止
                    try:
                        psutil_proc.wait(timeout=10)
                        logger.info(f"  ✅ 进程 {proc['pid']} 已终止")
                        cleaned_count += 1
                    except psutil.TimeoutExpired:
                        # 强制杀死
                        psutil_proc.kill()
                        logger.info(f"  ⚡ 强制杀死进程 {proc['pid']}")
                        cleaned_count += 1
                        
                except psutil.NoSuchProcess:
                    logger.info(f"  ⚠️  进程 {proc['pid']} 已不存在")
                except Exception as e:
                    logger.error(f"  ❌ 清理进程 {proc['pid']} 失败: {e}")
    
    return cleaned_count


def cleanup_stale_locks():
    """清理陈旧的锁文件"""
    try:
        from services.connectors.process_manager import ProcessManager
        
        process_manager = ProcessManager()
        cleaned_locks = process_manager.cleanup_zombies()
        
        logger.info(f"清理了 {cleaned_locks} 个陈旧的锁文件")
        
    except Exception as e:
        logger.error(f"清理锁文件失败: {e}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='清理重复的连接器进程')
    parser.add_argument('--dry-run', action='store_true', help='仅显示要清理的进程，不执行清理')
    parser.add_argument('--force', action='store_true', help='强制清理，跳过确认')
    
    args = parser.parse_args()
    
    logger.info("🔍 扫描Linch Mind相关进程...")
    
    # 1. 查找所有相关进程
    all_processes = find_linch_mind_processes()
    
    if not all_processes:
        logger.info("✅ 未发现任何Linch Mind相关进程")
        return
    
    logger.info(f"发现 {len(all_processes)} 个相关进程:")
    for proc in all_processes:
        logger.info(f"  PID {proc['pid']}: {proc['name']} (CPU: {proc['cpu_percent']:.1f}%)")
    
    # 2. 查找重复进程
    duplicates = find_duplicate_connectors(all_processes)
    
    if not duplicates:
        logger.info("✅ 未发现重复的连接器进程")
    else:
        logger.warning(f"⚠️  发现 {len(duplicates)} 种连接器有重复进程:")
        for connector_type, processes in duplicates.items():
            logger.warning(f"  {connector_type}: {len(processes)} 个进程")
        
        # 3. 确认清理操作
        if not args.dry_run and not args.force:
            confirm = input("\n是否继续清理重复进程? (y/N): ")
            if confirm.lower() != 'y':
                logger.info("操作已取消")
                return
        
        # 4. 执行清理
        cleaned_count = cleanup_duplicate_processes(duplicates, dry_run=args.dry_run)
        
        if args.dry_run:
            logger.info(f"[DRY RUN] 将清理 {len([p for processes in duplicates.values() for p in processes[:-1]])} 个重复进程")
        else:
            logger.info(f"✅ 成功清理了 {cleaned_count} 个重复进程")
    
    # 5. 清理陈旧锁文件
    logger.info("🧹 清理陈旧锁文件...")
    cleanup_stale_locks()
    
    logger.info("🎉 清理操作完成")


if __name__ == "__main__":
    main()