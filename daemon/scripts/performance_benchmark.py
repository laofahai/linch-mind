#!/usr/bin/env python3
"""
架构优化性能基准测试
验证统一服务架构的性能改进效果
"""

import asyncio
import time
import logging
import statistics
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class BenchmarkResult:
    """基准测试结果"""
    test_name: str
    iterations: int
    total_time: float
    avg_time: float
    min_time: float
    max_time: float
    throughput: float  # operations per second
    memory_usage_mb: float
    error_count: int = 0


class PerformanceBenchmark:
    """性能基准测试器"""
    
    def __init__(self):
        self.results: List[BenchmarkResult] = []
        
    async def run_all_benchmarks(self) -> Dict[str, BenchmarkResult]:
        """运行所有基准测试"""
        logger.info("🚀 开始架构优化性能基准测试")
        
        benchmarks = [
            ("unified_search_performance", self.benchmark_unified_search),
            ("unified_cache_performance", self.benchmark_unified_cache),
            ("shared_executor_performance", self.benchmark_shared_executor),
            ("servicefacade_performance", self.benchmark_servicefacade),
            ("memory_usage_comparison", self.benchmark_memory_usage),
        ]
        
        results = {}
        
        for test_name, benchmark_func in benchmarks:
            logger.info(f"🏃 运行基准测试: {test_name}")
            try:
                result = await benchmark_func()
                results[test_name] = result
                self.results.append(result)
                logger.info(f"✅ {test_name} 完成: {result.avg_time:.3f}s avg, {result.throughput:.1f} ops/s")
            except Exception as e:
                logger.error(f"❌ {test_name} 失败: {e}")
        
        return results
    
    async def benchmark_unified_search(self) -> BenchmarkResult:
        """测试统一搜索服务性能"""
        from services.unified_search_service import get_unified_search_service, SearchQuery, SearchType
        
        search_service = await get_unified_search_service()
        iterations = 100
        times = []
        error_count = 0
        
        # 预热
        try:
            query = SearchQuery(
                query="test",
                search_type=SearchType.SEMANTIC,
                limit=10
            )
            await search_service.search(query)
        except:
            pass  # 预热可能失败，因为没有数据
        
        start_memory = self._get_memory_usage()
        
        for i in range(iterations):
            start_time = time.perf_counter()
            
            try:
                # 测试多种搜索类型
                queries = [
                    SearchQuery(query=f"test_{i}", search_type=SearchType.SEMANTIC, limit=5),
                    SearchQuery(query=f"test_{i}", search_type=SearchType.TEXT, limit=5),
                    SearchQuery(query="", search_type=SearchType.GRAPH, start_entity_id="test_id", limit=5),
                ]
                
                for query in queries:
                    await search_service.search(query)
                
            except Exception:
                error_count += 1
            
            end_time = time.perf_counter()
            times.append(end_time - start_time)
        
        end_memory = self._get_memory_usage()
        
        return BenchmarkResult(
            test_name="unified_search_performance",
            iterations=iterations,
            total_time=sum(times),
            avg_time=statistics.mean(times),
            min_time=min(times),
            max_time=max(times),
            throughput=iterations / sum(times),
            memory_usage_mb=end_memory - start_memory,
            error_count=error_count
        )
    
    async def benchmark_unified_cache(self) -> BenchmarkResult:
        """测试统一缓存服务性能"""
        from services.unified_cache_service import get_unified_cache_service, CacheType
        
        cache_service = get_unified_cache_service()
        iterations = 1000
        times = []
        error_count = 0
        
        start_memory = self._get_memory_usage()
        
        for i in range(iterations):
            start_time = time.perf_counter()
            
            try:
                # 测试缓存操作
                key = f"test_key_{i % 100}"  # 复用一些键来测试缓存命中
                value = f"test_value_{i}"
                
                # 设置缓存
                await cache_service.set(key, value, CacheType.MEMORY)
                
                # 获取缓存
                result = await cache_service.get(key, CacheType.MEMORY)
                
                # 批量操作
                if i % 10 == 0:
                    batch_items = {f"batch_{j}": f"value_{j}" for j in range(5)}
                    await cache_service.mset(batch_items, CacheType.MEMORY)
                    await cache_service.mget(list(batch_items.keys()), CacheType.MEMORY)
                
            except Exception:
                error_count += 1
            
            end_time = time.perf_counter()
            times.append(end_time - start_time)
        
        end_memory = self._get_memory_usage()
        
        return BenchmarkResult(
            test_name="unified_cache_performance",
            iterations=iterations,
            total_time=sum(times),
            avg_time=statistics.mean(times),
            min_time=min(times),
            max_time=max(times),
            throughput=iterations / sum(times),
            memory_usage_mb=end_memory - start_memory,
            error_count=error_count
        )
    
    async def benchmark_shared_executor(self) -> BenchmarkResult:
        """测试共享执行器服务性能"""
        from services.shared_executor_service import get_shared_executor_service, TaskType
        
        executor_service = get_shared_executor_service()
        iterations = 100
        times = []
        error_count = 0
        
        def cpu_task(n):
            """CPU密集型任务"""
            return sum(i * i for i in range(n))
        
        def io_task():
            """IO模拟任务"""
            time.sleep(0.001)  # 模拟IO延迟
            return "io_result"
        
        start_memory = self._get_memory_usage()
        
        for i in range(iterations):
            start_time = time.perf_counter()
            
            try:
                # 提交多种类型的任务
                tasks = [
                    executor_service.submit(lambda: cpu_task(100), TaskType.CPU),
                    executor_service.submit(io_task, TaskType.IO),
                    executor_service.submit(lambda: f"result_{i}", TaskType.GENERAL),
                ]
                
                # 等待所有任务完成
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
            except Exception:
                error_count += 1
            
            end_time = time.perf_counter()
            times.append(end_time - start_time)
        
        end_memory = self._get_memory_usage()
        
        return BenchmarkResult(
            test_name="shared_executor_performance",
            iterations=iterations,
            total_time=sum(times),
            avg_time=statistics.mean(times),
            min_time=min(times),
            max_time=max(times),
            throughput=iterations / sum(times),
            memory_usage_mb=end_memory - start_memory,
            error_count=error_count
        )
    
    async def benchmark_servicefacade(self) -> BenchmarkResult:
        """测试ServiceFacade性能"""
        from core.service_facade import get_service_facade
        from services.unified_cache_service import UnifiedCacheService, get_unified_cache_service
        from core.container import get_container
        
        # 确保服务已注册
        cache_service = get_unified_cache_service()
        container = get_container()
        container.register_instance(UnifiedCacheService, cache_service)
        
        facade = get_service_facade()
        iterations = 1000
        times = []
        error_count = 0
        
        start_memory = self._get_memory_usage()
        
        for i in range(iterations):
            start_time = time.perf_counter()
            
            try:
                # 测试服务获取（应该有缓存）
                service = facade.get_service(UnifiedCacheService)
                
                # 测试服务状态检查
                available = facade.is_service_available(UnifiedCacheService)
                
                # 测试安全获取
                result = facade.get_service_safe(UnifiedCacheService)
                
            except Exception:
                error_count += 1
            
            end_time = time.perf_counter()
            times.append(end_time - start_time)
        
        end_memory = self._get_memory_usage()
        
        # 获取缓存统计
        stats = facade.get_service_stats()
        logger.info(f"ServiceFacade统计: {stats}")
        
        return BenchmarkResult(
            test_name="servicefacade_performance",
            iterations=iterations,
            total_time=sum(times),
            avg_time=statistics.mean(times),
            min_time=min(times),
            max_time=max(times),
            throughput=iterations / sum(times),
            memory_usage_mb=end_memory - start_memory,
            error_count=error_count
        )
    
    async def benchmark_memory_usage(self) -> BenchmarkResult:
        """测试内存使用情况"""
        import gc
        
        # 强制垃圾回收
        gc.collect()
        start_memory = self._get_memory_usage()
        
        # 初始化所有统一服务
        from services.unified_search_service import get_unified_search_service
        from services.unified_cache_service import get_unified_cache_service
        from services.shared_executor_service import get_shared_executor_service
        
        search_service = await get_unified_search_service()
        cache_service = get_unified_cache_service()
        executor_service = get_shared_executor_service()
        
        # 执行一些操作
        for i in range(100):
            await cache_service.set(f"key_{i}", f"value_{i}")
        
        gc.collect()
        end_memory = self._get_memory_usage()
        
        return BenchmarkResult(
            test_name="memory_usage_comparison",
            iterations=1,
            total_time=0.0,
            avg_time=0.0,
            min_time=0.0,
            max_time=0.0,
            throughput=0.0,
            memory_usage_mb=end_memory - start_memory,
            error_count=0
        )
    
    def _get_memory_usage(self) -> float:
        """获取当前内存使用量(MB)"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            return 0.0
    
    def generate_report(self) -> str:
        """生成性能报告"""
        report = []
        report.append("=" * 80)
        report.append("🏆 架构优化性能基准测试报告")
        report.append("=" * 80)
        report.append(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"测试项目数: {len(self.results)}")
        report.append("")
        
        # 详细结果
        for result in self.results:
            report.append(f"📊 {result.test_name}")
            report.append("-" * 60)
            report.append(f"  迭代次数: {result.iterations}")
            report.append(f"  总时间: {result.total_time:.3f}s")
            report.append(f"  平均时间: {result.avg_time:.3f}s")
            report.append(f"  最小时间: {result.min_time:.3f}s")
            report.append(f"  最大时间: {result.max_time:.3f}s")
            report.append(f"  吞吐量: {result.throughput:.1f} ops/s")
            report.append(f"  内存使用: {result.memory_usage_mb:.1f} MB")
            if result.error_count > 0:
                report.append(f"  错误数: {result.error_count}")
            report.append("")
        
        # 性能总结
        report.append("🎯 性能总结")
        report.append("-" * 60)
        
        total_throughput = sum(r.throughput for r in self.results if r.throughput > 0)
        total_memory = sum(r.memory_usage_mb for r in self.results)
        total_errors = sum(r.error_count for r in self.results)
        
        report.append(f"  总吞吐量: {total_throughput:.1f} ops/s")
        report.append(f"  总内存使用: {total_memory:.1f} MB")
        report.append(f"  总错误数: {total_errors}")
        
        # 架构优化效果评估
        report.append("")
        report.append("🚀 架构优化效果评估")
        report.append("-" * 60)
        
        # 根据性能结果给出评估
        if total_throughput > 1000:
            report.append("  ✅ 高性能: 系统吞吐量优异")
        elif total_throughput > 500:
            report.append("  ✅ 良好性能: 系统吞吐量良好")
        else:
            report.append("  ⚠️  性能需要优化")
        
        if total_memory < 100:
            report.append("  ✅ 内存使用合理")
        elif total_memory < 200:
            report.append("  ⚠️  内存使用较高")
        else:
            report.append("  ❌ 内存使用过高")
        
        if total_errors == 0:
            report.append("  ✅ 零错误: 系统稳定性优异")
        else:
            report.append(f"  ⚠️  发现 {total_errors} 个错误，需要检查")
        
        return "\n".join(report)


async def main():
    """主函数"""
    benchmark = PerformanceBenchmark()
    
    try:
        # 运行所有基准测试
        results = await benchmark.run_all_benchmarks()
        
        # 生成报告
        report = benchmark.generate_report()
        print(report)
        
        # 保存报告到文件
        report_file = Path("performance_benchmark_report.txt")
        report_file.write_text(report, encoding='utf-8')
        logger.info(f"📄 性能报告已保存到: {report_file}")
        
        # 返回简要结果
        return {
            "success": True,
            "total_tests": len(results),
            "total_throughput": sum(r.throughput for r in benchmark.results if r.throughput > 0),
            "total_memory_mb": sum(r.memory_usage_mb for r in benchmark.results),
            "total_errors": sum(r.error_count for r in benchmark.results)
        }
        
    except Exception as e:
        logger.error(f"基准测试失败: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    result = asyncio.run(main())
    print(f"\n📊 基准测试结果: {result}")