#!/usr/bin/env python3
"""
Windows Named Pipe IPC 客户端测试工具
用于验证Windows IPC服务器的功能和性能
"""

import json
import logging
import platform
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from statistics import mean, median
from typing import Dict

logger = logging.getLogger(__name__)

# Windows特定导入
if platform.system() == "Windows":
    try:
        import pywintypes
        import win32file
        import win32pipe

        WINDOWS_SUPPORT = True
    except ImportError:
        WINDOWS_SUPPORT = False
        logger.error("需要pywin32库支持: pip install pywin32")
else:
    WINDOWS_SUPPORT = False


class WindowsIPCTestClient:
    """Windows IPC测试客户端"""

    def __init__(self, pipe_name: str = "linch-mind-test"):
        self.pipe_name = pipe_name
        self.full_pipe_name = f"\\\\.\\pipe\\{pipe_name}"

    def _connect_to_pipe(self, timeout_ms: int = 5000):
        """连接到Named Pipe"""
        if not WINDOWS_SUPPORT:
            raise RuntimeError("Windows Named Pipe需要pywin32库支持")

        try:
            # 等待Named Pipe可用
            win32pipe.WaitNamedPipe(self.full_pipe_name, timeout_ms)

            # 连接到Named Pipe
            handle = win32file.CreateFile(
                self.full_pipe_name,
                win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                0,  # 不共享
                None,  # 默认安全属性
                win32file.OPEN_EXISTING,
                0,  # 默认属性
                None,  # 无模板文件
            )

            if handle == win32file.INVALID_HANDLE_VALUE:
                raise Exception("无法连接到Named Pipe")

            return handle

        except pywintypes.error as e:
            raise Exception(f"连接Named Pipe失败: {e}")

    def _send_message(self, handle, message: Dict) -> Dict:
        """发送消息并接收响应"""
        try:
            # 序列化消息
            message_str = json.dumps(message)
            message_bytes = message_str.encode("utf-8")
            length_bytes = len(message_bytes).to_bytes(4, byteorder="big")

            # 发送长度前缀和消息
            win32file.WriteFile(handle, length_bytes)
            win32file.WriteFile(handle, message_bytes)

            # 读取响应长度
            result, length_data = win32file.ReadFile(handle, 4)
            if result != 0:
                raise Exception(f"读取响应长度失败: {result}")

            response_length = int.from_bytes(length_data, byteorder="big")

            # 读取完整响应
            result, response_data = win32file.ReadFile(handle, response_length)
            if result != 0:
                raise Exception(f"读取响应数据失败: {result}")

            response_str = response_data.decode("utf-8")
            return json.loads(response_str)

        except Exception as e:
            logger.error(f"发送消息失败: {e}")
            raise

    def _close_connection(self, handle):
        """关闭连接"""
        try:
            win32file.CloseHandle(handle)
        except Exception as e:
            logger.warning(f"关闭连接时出错: {e}")

    def test_single_request(self, message: Dict = None) -> Dict:
        """测试单个请求"""
        if message is None:
            message = {
                "method": "GET",
                "path": "/test",
                "data": {"test": True, "timestamp": time.time()},
                "headers": {},
                "query_params": {},
            }

        start_time = time.perf_counter()

        try:
            handle = self._connect_to_pipe()
            response = self._send_message(handle, message)
            self._close_connection(handle)

            end_time = time.perf_counter()
            response_time = end_time - start_time

            return {
                "success": True,
                "response": response,
                "response_time_ms": response_time * 1000,
                "request": message,
            }

        except Exception as e:
            end_time = time.perf_counter()
            response_time = end_time - start_time

            return {
                "success": False,
                "error": str(e),
                "response_time_ms": response_time * 1000,
                "request": message,
            }

    def test_concurrent_requests(
        self, num_requests: int = 10, num_workers: int = 5
    ) -> Dict:
        """测试并发请求"""
        logger.info(f"开始并发测试: {num_requests} 请求, {num_workers} 工作线程")

        def worker_task(request_id: int):
            message = {
                "method": "POST",
                "path": f"/test/concurrent/{request_id}",
                "data": {
                    "request_id": request_id,
                    "timestamp": time.time(),
                    "test_type": "concurrent",
                },
                "headers": {"X-Request-ID": str(request_id)},
                "query_params": {"concurrent": "true"},
            }
            return self.test_single_request(message)

        start_time = time.perf_counter()
        results = []

        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(worker_task, i) for i in range(num_requests)]

            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"并发请求失败: {e}")
                    results.append(
                        {"success": False, "error": str(e), "response_time_ms": 0}
                    )

        end_time = time.perf_counter()
        total_time = end_time - start_time

        # 统计分析
        successful_requests = [r for r in results if r["success"]]
        failed_requests = [r for r in results if not r["success"]]

        response_times = [r["response_time_ms"] for r in successful_requests]

        stats = {
            "total_requests": num_requests,
            "successful_requests": len(successful_requests),
            "failed_requests": len(failed_requests),
            "success_rate": len(successful_requests) / num_requests * 100,
            "total_time_seconds": total_time,
            "requests_per_second": num_requests / total_time,
        }

        if response_times:
            stats.update(
                {
                    "avg_response_time_ms": mean(response_times),
                    "median_response_time_ms": median(response_times),
                    "min_response_time_ms": min(response_times),
                    "max_response_time_ms": max(response_times),
                }
            )
        else:
            stats.update(
                {
                    "avg_response_time_ms": 0,
                    "median_response_time_ms": 0,
                    "min_response_time_ms": 0,
                    "max_response_time_ms": 0,
                }
            )

        return {"stats": stats, "results": results, "failed_requests": failed_requests}

    def test_stress_load(
        self, duration_seconds: int = 30, max_workers: int = 20
    ) -> Dict:
        """压力测试"""
        logger.info(f"开始压力测试: {duration_seconds} 秒, 最大 {max_workers} 工作线程")

        start_time = time.perf_counter()
        end_time = start_time + duration_seconds

        results = []
        request_counter = 0

        def stress_worker():
            nonlocal request_counter
            while time.perf_counter() < end_time:
                request_id = request_counter
                request_counter += 1

                message = {
                    "method": "GET",
                    "path": f"/stress/{request_id}",
                    "data": {
                        "request_id": request_id,
                        "timestamp": time.time(),
                        "stress_test": True,
                    },
                }

                try:
                    result = self.test_single_request(message)
                    results.append(result)

                    # 短暂延迟避免过载
                    time.sleep(0.001)
                except Exception as e:
                    results.append(
                        {"success": False, "error": str(e), "response_time_ms": 0}
                    )

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(stress_worker) for _ in range(max_workers)]

            # 等待所有工作完成或超时
            for future in as_completed(futures, timeout=duration_seconds + 5):
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"压力测试工作线程失败: {e}")

        actual_duration = time.perf_counter() - start_time

        # 分析结果
        successful_requests = [r for r in results if r["success"]]
        failed_requests = [r for r in results if not r["success"]]

        response_times = [r["response_time_ms"] for r in successful_requests]

        stats = {
            "duration_seconds": actual_duration,
            "total_requests": len(results),
            "successful_requests": len(successful_requests),
            "failed_requests": len(failed_requests),
            "success_rate": (
                len(successful_requests) / len(results) * 100 if results else 0
            ),
            "requests_per_second": len(results) / actual_duration,
        }

        if response_times:
            stats.update(
                {
                    "avg_response_time_ms": mean(response_times),
                    "median_response_time_ms": median(response_times),
                    "min_response_time_ms": min(response_times),
                    "max_response_time_ms": max(response_times),
                }
            )

        return {
            "stats": stats,
            "sample_failures": failed_requests[:10],  # 只保留前10个失败示例
        }

    def test_large_payload(self, payload_size_kb: int = 100) -> Dict:
        """测试大负载"""
        large_data = "A" * (payload_size_kb * 1024)  # 创建指定大小的数据

        message = {
            "method": "POST",
            "path": "/test/large-payload",
            "data": {
                "large_field": large_data,
                "size_kb": payload_size_kb,
                "timestamp": time.time(),
            },
        }

        logger.info(f"测试大负载: {payload_size_kb} KB")
        return self.test_single_request(message)


def run_comprehensive_test(pipe_name: str = "linch-mind-test"):
    """运行综合测试"""
    if not WINDOWS_SUPPORT:
        print("❌ Windows Named Pipe测试需要pywin32库支持")
        print("请安装: pip install pywin32")
        return False

    client = WindowsIPCTestClient(pipe_name)

    print("=" * 60)
    print("🧪 Windows Named Pipe IPC 综合测试")
    print("=" * 60)

    # 1. 基本连接测试
    print("\n1️⃣ 基本连接测试")
    print("-" * 30)

    try:
        result = client.test_single_request()
        if result["success"]:
            print(f"✅ 连接成功 (响应时间: {result['response_time_ms']:.2f}ms)")
            print(f"   服务器响应: {result['response']['success']}")
        else:
            print(f"❌ 连接失败: {result['error']}")
            return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

    # 2. 并发测试
    print("\n2️⃣ 并发性能测试")
    print("-" * 30)

    concurrent_result = client.test_concurrent_requests(num_requests=20, num_workers=5)
    stats = concurrent_result["stats"]

    print(f"总请求数: {stats['total_requests']}")
    print(f"成功请求: {stats['successful_requests']}")
    print(f"失败请求: {stats['failed_requests']}")
    print(f"成功率: {stats['success_rate']:.1f}%")
    print(f"平均响应时间: {stats['avg_response_time_ms']:.2f}ms")
    print(f"中位响应时间: {stats['median_response_time_ms']:.2f}ms")
    print(f"最大响应时间: {stats['max_response_time_ms']:.2f}ms")
    print(f"吞吐量: {stats['requests_per_second']:.1f} req/s")

    if stats["success_rate"] < 95:
        print("⚠️  成功率较低，可能存在稳定性问题")
    elif stats["avg_response_time_ms"] > 100:
        print("⚠️  响应时间较高，可能存在性能问题")
    else:
        print("✅ 并发测试通过")

    # 3. 压力测试
    print("\n3️⃣ 压力测试 (30秒)")
    print("-" * 30)

    stress_result = client.test_stress_load(
        duration_seconds=10, max_workers=10
    )  # 缩短测试时间
    stress_stats = stress_result["stats"]

    print(f"测试时长: {stress_stats['duration_seconds']:.1f}s")
    print(f"总请求数: {stress_stats['total_requests']}")
    print(f"成功率: {stress_stats['success_rate']:.1f}%")
    print(f"平均吞吐量: {stress_stats['requests_per_second']:.1f} req/s")

    if "avg_response_time_ms" in stress_stats:
        print(f"平均响应时间: {stress_stats['avg_response_time_ms']:.2f}ms")

    if stress_stats["requests_per_second"] > 1000:
        print("✅ 压力测试: 高性能 (>1000 req/s)")
    elif stress_stats["requests_per_second"] > 500:
        print("✅ 压力测试: 良好性能 (>500 req/s)")
    else:
        print("⚠️  压力测试: 性能需优化")

    # 4. 大负载测试
    print("\n4️⃣ 大负载测试")
    print("-" * 30)

    for size_kb in [10, 50, 100]:
        result = client.test_large_payload(size_kb)
        if result["success"]:
            print(f"✅ {size_kb}KB 负载: {result['response_time_ms']:.2f}ms")
        else:
            print(f"❌ {size_kb}KB 负载失败: {result['error']}")

    print("\n🎉 测试完成!")
    return True


if __name__ == "__main__":
    import sys

    # 设置日志
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # 从命令行参数获取pipe名称
    pipe_name = sys.argv[1] if len(sys.argv) > 1 else "linch-mind-test"

    success = run_comprehensive_test(pipe_name)
    sys.exit(0 if success else 1)
