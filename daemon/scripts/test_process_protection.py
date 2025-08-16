#!/usr/bin/env python3
"""
测试进程保护机制的脚本
验证修复后的多进程问题和性能改进
"""

import asyncio
import sys
import time
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
from core.service_facade import get_service
from services.connectors.connector_manager import ConnectorManager
from services.connectors.process_manager import ProcessManager
from services.connectors.resource_monitor import ResourceProtectionMonitor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_singleton_protection():
    """测试单例保护机制"""
    logger.info("🔒 测试单例保护机制...")
    
    try:
        connector_manager = get_service(ConnectorManager)
        
        # 尝试多次并发启动同一个连接器
        connector_id = "filesystem"
        
        logger.info(f"尝试并发启动连接器 {connector_id}...")
        
        # 创建多个并发启动任务
        tasks = []
        for i in range(5):  # 5个并发启动尝试
            task = asyncio.create_task(connector_manager.start_connector(connector_id))
            tasks.append(task)
        
        # 等待所有任务完成
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 检查结果
        successful_starts = sum(1 for result in results if result is True)
        
        logger.info(f"并发启动结果: {successful_starts} 个成功启动")
        
        # 验证只有一个进程在运行
        process_info = connector_manager.get_process_info(connector_id)
        if process_info and process_info.get("pid"):
            logger.info(f"✅ 单例保护成功: 只有一个进程运行 (PID: {process_info['pid']})")
        else:
            logger.warning("⚠️  未找到运行中的进程")
        
        return successful_starts == 1
        
    except Exception as e:
        logger.error(f"单例保护测试失败: {e}")
        return False


async def test_resource_monitoring():
    """测试资源监控功能"""
    logger.info("📊 测试资源监控功能...")
    
    try:
        resource_monitor = get_service(ResourceProtectionMonitor)
        
        # 启动资源监控
        await resource_monitor.start_monitoring()
        
        # 等待几秒收集资源数据
        await asyncio.sleep(10)
        
        # 检查资源统计
        stats = resource_monitor.get_system_protection_stats()
        logger.info(f"资源监控统计: {stats}")
        
        # 检查单个连接器资源使用
        connector_id = "filesystem"
        connector_stats = resource_monitor.get_resource_stats(connector_id)
        
        if connector_stats.get("status") == "active":
            latest = connector_stats["latest"]
            logger.info(f"连接器 {connector_id} 资源使用:")
            logger.info(f"  CPU: {latest['cpu_percent']:.1f}%")
            logger.info(f"  内存: {latest['memory_percent']:.1f}% ({latest['memory_mb']:.1f}MB)")
            logger.info(f"  系统调用速率: {latest['syscall_rate']:.0f}/s")
            
            # 检查是否在正常范围内
            if latest['cpu_percent'] < 50.0:  # CPU使用率低于50%
                logger.info("✅ CPU使用率正常")
                return True
            else:
                logger.warning(f"⚠️  CPU使用率较高: {latest['cpu_percent']:.1f}%")
                return False
        else:
            logger.warning("⚠️  无法获取资源数据")
            return False
            
    except Exception as e:
        logger.error(f"资源监控测试失败: {e}")
        return False


async def test_startup_sequence():
    """测试启动序列化"""
    logger.info("⚡ 测试启动序列化...")
    
    try:
        connector_manager = get_service(ConnectorManager)
        
        # 先停止所有连接器
        logger.info("停止所有连接器...")
        await connector_manager.stop_all_connectors()
        await asyncio.sleep(2)
        
        # 记录启动时间
        start_time = time.time()
        
        # 启动所有注册的连接器
        logger.info("开始序列化启动...")
        await connector_manager.start_all_registered_connectors()
        
        # 计算启动时间
        startup_duration = time.time() - start_time
        logger.info(f"启动完成，耗时: {startup_duration:.2f}秒")
        
        # 验证最终状态
        connectors = connector_manager.get_all_connectors()
        running_count = len([c for c in connectors if c["status"] == "running"])
        total_count = len(connectors)
        
        logger.info(f"启动结果: {running_count}/{total_count} 个连接器运行中")
        
        # 检查是否有重复进程
        process_manager = connector_manager.process_manager
        running_processes = process_manager.list_running_connectors()
        
        connector_counts = {}
        for proc in running_processes:
            connector_id = proc["connector_id"]
            connector_counts[connector_id] = connector_counts.get(connector_id, 0) + 1
        
        duplicates = {k: v for k, v in connector_counts.items() if v > 1}
        
        if duplicates:
            logger.error(f"❌ 发现重复进程: {duplicates}")
            return False
        else:
            logger.info("✅ 没有重复进程")
            return True
            
    except Exception as e:
        logger.error(f"启动序列化测试失败: {e}")
        return False


async def test_cleanup_script():
    """测试清理脚本"""
    logger.info("🧹 测试清理脚本...")
    
    try:
        from scripts.cleanup_duplicate_connectors import (
            find_linch_mind_processes,
            find_duplicate_connectors,
            cleanup_stale_locks
        )
        
        # 查找进程
        processes = find_linch_mind_processes()
        logger.info(f"找到 {len(processes)} 个相关进程")
        
        # 查找重复进程
        duplicates = find_duplicate_connectors(processes)
        
        if duplicates:
            logger.warning(f"发现重复进程: {list(duplicates.keys())}")
        else:
            logger.info("✅ 没有发现重复进程")
        
        # 清理陈旧锁文件
        cleanup_stale_locks()
        
        return len(duplicates) == 0
        
    except Exception as e:
        logger.error(f"清理脚本测试失败: {e}")
        return False


async def main():
    """主测试函数"""
    logger.info("🚀 开始多进程保护机制综合测试...")
    
    test_results = {
        "singleton_protection": False,
        "resource_monitoring": False, 
        "startup_sequence": False,
        "cleanup_script": False
    }
    
    try:
        # 初始化依赖注入容器
        from daemon.main import initialize_di_container
        initialize_di_container()
        
        # 执行各项测试
        logger.info("=" * 50)
        test_results["singleton_protection"] = await test_singleton_protection()
        
        logger.info("=" * 50)
        test_results["resource_monitoring"] = await test_resource_monitoring()
        
        logger.info("=" * 50) 
        test_results["startup_sequence"] = await test_startup_sequence()
        
        logger.info("=" * 50)
        test_results["cleanup_script"] = await test_cleanup_script()
        
    except Exception as e:
        logger.error(f"测试过程中出现异常: {e}")
    
    # 输出测试结果总结
    logger.info("=" * 50)
    logger.info("🎯 测试结果总结:")
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"  {test_name}: {status}")
        if result:
            passed_tests += 1
    
    success_rate = (passed_tests / total_tests) * 100
    logger.info(f"总体通过率: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate >= 75:
        logger.info("🎉 多进程保护机制测试基本通过!")
    else:
        logger.warning("⚠️  多进程保护机制仍需改进")
    
    return success_rate >= 75


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)