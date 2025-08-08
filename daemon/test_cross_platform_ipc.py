#!/usr/bin/env python3
"""
跨平台IPC兼容性和性能测试套件
验证Unix Socket和Windows Named Pipe的功能和性能一致性
"""

import asyncio
import json
import logging
import platform
import statistics
import time
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

# 设置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class CrossPlatformIPCTestSuite:
    """跨平台IPC测试套件"""

    def __init__(self):
        self.platform = platform.system()
        self.results = {}

    async def test_basic_connectivity(self) -> bool:
        """测试基础连接性"""
        logger.info("🔌 测试基础连接性...")

        try:
            from services.cross_platform_ipc import create_ipc_client

            # 直接使用底层IPC客户端
            from services.ipc_client import IPCClient

            # 从socket文件读取正确的socket路径
            socket_info_path = "/Users/laofahai/.linch-mind/daemon.socket"
            with open(socket_info_path, "r") as f:
                socket_info = json.loads(f.read())

            socket_path = socket_info["path"]
            client = IPCClient(socket_path=socket_path)
            await client.connect()

            try:
                # 发送健康检查请求
                response = await client.request("GET", "/health")
            finally:
                await client.disconnect()

            logger.info(f"健康检查响应: {response}")
            if (
                response
                and response.get("success")
                and response.get("data", {}).get("status") == "healthy"
            ):
                logger.info("✅ 基础连接性测试通过")
                return True
            else:
                logger.error(f"❌ 健康检查响应无效: {response}")
                return False

        except Exception as e:
            logger.error(f"❌ 基础连接性测试失败: {e}")
            return False

    async def test_request_response(self) -> bool:
        """测试请求-响应功能"""
        logger.info("🔄 测试请求-响应功能...")

        test_cases = [
            ("GET", "/health", None),
            ("GET", "/api/connectors", None),
            ("POST", "/api/test", {"test": "data"}),
        ]

        try:
            from services.cross_platform_ipc import create_ipc_client

            with create_ipc_client() as client:
                success_count = 0

                for method, path, data in test_cases:
                    response = client.send_request(method, path, data)
                    if response:
                        logger.debug(
                            f"✅ {method} {path}: {response.get('status', 'unknown')}"
                        )
                        success_count += 1
                    else:
                        logger.warning(f"⚠️  {method} {path}: 无响应")

                if success_count == len(test_cases):
                    logger.info("✅ 请求-响应功能测试完全通过")
                    return True
                elif success_count > 0:
                    logger.info(
                        f"⚠️  请求-响应功能部分通过 ({success_count}/{len(test_cases)})"
                    )
                    return True
                else:
                    logger.error("❌ 请求-响应功能测试完全失败")
                    return False

        except Exception as e:
            logger.error(f"❌ 请求-响应功能测试失败: {e}")
            return False

    async def benchmark_performance(self, num_requests: int = 1000) -> Dict[str, float]:
        """性能基准测试"""
        logger.info(f"⚡ 开始性能基准测试 ({num_requests} 请求)...")

        try:
            from services.cross_platform_ipc import create_ipc_client

            latencies = []
            errors = 0

            with create_ipc_client() as client:
                # 预热
                for _ in range(10):
                    client.send_request("GET", "/health")

                # 实际测试
                start_time = time.time()

                for i in range(num_requests):
                    request_start = time.time()
                    response = client.send_request("GET", f"/health?test={i}")
                    request_end = time.time()

                    if response:
                        latencies.append(
                            (request_end - request_start) * 1000
                        )  # 转换为毫秒
                    else:
                        errors += 1

                end_time = time.time()
                duration = end_time - start_time

                # 计算统计指标
                successful_requests = len(latencies)
                qps = successful_requests / duration if duration > 0 else 0
                avg_latency = statistics.mean(latencies) if latencies else 0
                p50_latency = statistics.median(latencies) if latencies else 0
                p95_latency = self._percentile(latencies, 95) if latencies else 0
                p99_latency = self._percentile(latencies, 99) if latencies else 0
                success_rate = (
                    (successful_requests / num_requests * 100)
                    if num_requests > 0
                    else 0
                )

                results = {
                    "platform": self.platform,
                    "total_requests": num_requests,
                    "successful_requests": successful_requests,
                    "errors": errors,
                    "duration": duration,
                    "qps": qps,
                    "avg_latency": avg_latency,
                    "p50_latency": p50_latency,
                    "p95_latency": p95_latency,
                    "p99_latency": p99_latency,
                    "success_rate": success_rate,
                }

                # 记录结果
                logger.info(f"📊 {self.platform} 性能测试结果:")
                logger.info(f"  QPS: {qps:.1f}")
                logger.info(f"  平均延迟: {avg_latency:.2f}ms")
                logger.info(f"  P95延迟: {p95_latency:.2f}ms")
                logger.info(f"  P99延迟: {p99_latency:.2f}ms")
                logger.info(f"  成功率: {success_rate:.1f}%")

                return results

        except Exception as e:
            logger.error(f"❌ 性能基准测试失败: {e}")
            return {}

    async def test_concurrent_clients(
        self, num_clients: int = 10, requests_per_client: int = 100
    ) -> Dict[str, float]:
        """测试并发客户端性能"""
        logger.info(
            f"🚀 测试并发性能 ({num_clients} 客户端, 每个 {requests_per_client} 请求)..."
        )

        try:

            async def client_worker(client_id: int) -> Tuple[int, List[float], int]:
                """单个客户端工作函数"""
                from services.cross_platform_ipc import create_ipc_client

                latencies = []
                errors = 0

                try:
                    with create_ipc_client() as client:
                        for i in range(requests_per_client):
                            start_time = time.time()
                            response = client.send_request(
                                "GET", f"/health?client={client_id}&req={i}"
                            )
                            end_time = time.time()

                            if response:
                                latencies.append((end_time - start_time) * 1000)
                            else:
                                errors += 1

                except Exception as e:
                    logger.warning(f"客户端 {client_id} 错误: {e}")
                    errors = requests_per_client

                return client_id, latencies, errors

            # 创建并发任务
            tasks = [client_worker(i) for i in range(num_clients)]

            start_time = time.time()
            results = await asyncio.gather(*tasks)
            end_time = time.time()

            # 汇总结果
            all_latencies = []
            total_errors = 0

            for client_id, latencies, errors in results:
                all_latencies.extend(latencies)
                total_errors += errors
                logger.debug(
                    f"客户端 {client_id}: {len(latencies)} 成功, {errors} 错误"
                )

            duration = end_time - start_time
            total_requests = num_clients * requests_per_client
            successful_requests = len(all_latencies)

            concurrent_results = {
                "platform": self.platform,
                "concurrent_clients": num_clients,
                "requests_per_client": requests_per_client,
                "total_requests": total_requests,
                "successful_requests": successful_requests,
                "total_errors": total_errors,
                "duration": duration,
                "overall_qps": successful_requests / duration if duration > 0 else 0,
                "avg_latency": statistics.mean(all_latencies) if all_latencies else 0,
                "p95_latency": (
                    self._percentile(all_latencies, 95) if all_latencies else 0
                ),
                "success_rate": (
                    (successful_requests / total_requests * 100)
                    if total_requests > 0
                    else 0
                ),
            }

            logger.info(f"🚀 {self.platform} 并发测试结果:")
            logger.info(f"  整体QPS: {concurrent_results['overall_qps']:.1f}")
            logger.info(f"  平均延迟: {concurrent_results['avg_latency']:.2f}ms")
            logger.info(f"  P95延迟: {concurrent_results['p95_latency']:.2f}ms")
            logger.info(f"  成功率: {concurrent_results['success_rate']:.1f}%")

            return concurrent_results

        except Exception as e:
            logger.error(f"❌ 并发客户端测试失败: {e}")
            return {}

    async def test_error_handling(self) -> bool:
        """测试错误处理"""
        logger.info("🛡️ 测试错误处理...")

        error_scenarios = [
            ("GET", "/nonexistent", None, "404路径测试"),
            ("INVALID", "/health", None, "无效方法测试"),
            ("POST", "/health", {"invalid": "json"}, "无效数据测试"),
        ]

        try:
            from services.cross_platform_ipc import create_ipc_client

            with create_ipc_client() as client:
                error_handled_count = 0

                for method, path, data, description in error_scenarios:
                    response = client.send_request(method, path, data)

                    # 检查是否正确处理错误
                    if response and (
                        response.get("error") or response.get("status_code", 200) >= 400
                    ):
                        logger.debug(f"✅ {description}: 错误正确处理")
                        error_handled_count += 1
                    else:
                        logger.warning(f"⚠️  {description}: 错误处理可能有问题")

                if (
                    error_handled_count >= len(error_scenarios) // 2
                ):  # 至少一半的错误场景正确处理
                    logger.info("✅ 错误处理测试通过")
                    return True
                else:
                    logger.warning("⚠️  错误处理测试部分通过")
                    return False

        except Exception as e:
            logger.error(f"❌ 错误处理测试失败: {e}")
            return False

    def _percentile(self, data: List[float], percentile: int) -> float:
        """计算百分位数"""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = int((percentile / 100) * len(sorted_data))
        return sorted_data[min(index, len(sorted_data) - 1)]

    def _evaluate_performance(self, results: Dict[str, float]) -> str:
        """评估性能等级"""
        if not results:
            return "❌ 未知"

        avg_latency = results.get("avg_latency", 999)
        qps = results.get("qps", 0)
        success_rate = results.get("success_rate", 0)

        # 延迟评级
        if avg_latency < 1.0:
            latency_grade = "🏆 优秀"
        elif avg_latency < 5.0:
            latency_grade = "✅ 良好"
        else:
            latency_grade = "⚠️ 需要改进"

        # QPS评级
        if qps > 5000:
            qps_grade = "🏆 优秀"
        elif qps > 1000:
            qps_grade = "✅ 良好"
        else:
            qps_grade = "⚠️ 需要改进"

        # 可靠性评级
        if success_rate > 99:
            reliability_grade = "🏆 优秀"
        elif success_rate > 95:
            reliability_grade = "✅ 良好"
        else:
            reliability_grade = "⚠️ 需要改进"

        return (
            f"延迟: {latency_grade}, 吞吐量: {qps_grade}, 可靠性: {reliability_grade}"
        )

    async def run_full_test_suite(self) -> Dict[str, any]:
        """运行完整的测试套件"""
        logger.info("=" * 60)
        logger.info(f"跨平台IPC测试套件开始 - {self.platform}")
        logger.info("=" * 60)

        test_results = {"platform": self.platform, "timestamp": time.time()}

        # 1. 基础连接测试
        connectivity_ok = await self.test_basic_connectivity()
        test_results["connectivity"] = connectivity_ok

        if not connectivity_ok:
            logger.error("❌ 基础连接失败，跳过后续测试")
            return test_results

        # 2. 功能测试
        functionality_ok = await self.test_request_response()
        test_results["functionality"] = functionality_ok

        # 3. 错误处理测试
        error_handling_ok = await self.test_error_handling()
        test_results["error_handling"] = error_handling_ok

        # 4. 性能测试
        performance_results = await self.benchmark_performance(1000)
        test_results["performance"] = performance_results

        # 5. 并发测试
        concurrent_results = await self.test_concurrent_clients(5, 50)
        test_results["concurrent_performance"] = concurrent_results

        # 生成最终报告
        logger.info("\n" + "=" * 60)
        logger.info(f"{self.platform} IPC测试套件完成 - 最终报告")
        logger.info("=" * 60)

        logger.info(f"📋 测试结果概览:")
        logger.info(f"  连接性测试: {'✅ 通过' if connectivity_ok else '❌ 失败'}")
        logger.info(f"  功能测试: {'✅ 通过' if functionality_ok else '❌ 失败'}")
        logger.info(f"  错误处理: {'✅ 通过' if error_handling_ok else '❌ 失败'}")

        if performance_results:
            performance_grade = self._evaluate_performance(performance_results)
            logger.info(f"  性能评级: {performance_grade}")

        # 综合评分
        passed_tests = sum([connectivity_ok, functionality_ok, error_handling_ok])
        total_tests = 3
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        logger.info(
            f"\n🎯 综合评分: {pass_rate:.1f}% ({passed_tests}/{total_tests} 测试通过)"
        )

        if pass_rate >= 80:
            logger.info("🏆 总体评级: 优秀")
        elif pass_rate >= 60:
            logger.info("✅ 总体评级: 良好")
        else:
            logger.info("⚠️  总体评级: 需要改进")

        test_results["pass_rate"] = pass_rate
        test_results["overall_grade"] = (
            "优秀" if pass_rate >= 80 else "良好" if pass_rate >= 60 else "需要改进"
        )

        return test_results


async def main():
    """主函数"""
    test_suite = CrossPlatformIPCTestSuite()
    results = await test_suite.run_full_test_suite()

    # 根据测试结果设置退出码
    success = results.get("pass_rate", 0) >= 60
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
