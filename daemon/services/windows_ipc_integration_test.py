#!/usr/bin/env python3
"""
Windows Named Pipe IPC 集成测试
测试完整的Windows IPC服务器与真实IPC应用的集成
"""

import asyncio
import logging
import os
import platform
import signal
import sys
import time
from pathlib import Path

# 添加daemon目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.ipc_protocol import IPCRequest, IPCResponse, success_response
from services.ipc_router import IPCApplication, IPCRouter
from services.windows_ipc_server import WindowsIPCServer, check_windows_ipc_support

logger = logging.getLogger(__name__)


class TestIPCApplication:
    """测试用的IPC应用"""

    def __init__(self):
        self.app = IPCApplication()
        self.router = IPCRouter(prefix="/api/v1")
        self.setup_routes()
        self.app.include_router(self.router)

    def setup_routes(self):
        """设置测试路由"""

        @self.router.get("/health")
        async def health_check(request: IPCRequest) -> IPCResponse:
            """健康检查端点"""
            return success_response(
                {
                    "status": "healthy",
                    "timestamp": time.time(),
                    "server": "WindowsIPCServer",
                },
                request.request_id,
            )

        @self.router.get("/echo")
        async def echo_handler(request: IPCRequest) -> IPCResponse:
            """回声测试端点"""
            return success_response(
                {
                    "method": request.method,
                    "path": request.path,
                    "data": request.data,
                    "query_params": request.query_params,
                    "timestamp": time.time(),
                },
                request.request_id,
            )

        @self.router.post("/process")
        async def process_data(request: IPCRequest) -> IPCResponse:
            """数据处理端点"""
            data = request.data or {}

            # 模拟一些处理时间
            await asyncio.sleep(0.01)

            processed_data = {
                "original": data,
                "processed": True,
                "processing_time": 0.01,
                "size": len(str(data)),
                "timestamp": time.time(),
            }

            return success_response(processed_data, request.request_id)

        @self.router.get("/stats")
        async def get_stats(request: IPCRequest) -> IPCResponse:
            """获取统计信息端点"""
            return success_response(
                {
                    "total_requests": getattr(self, "request_count", 0),
                    "uptime": time.time() - getattr(self, "start_time", time.time()),
                    "memory_usage": "N/A",  # 可以添加真实的内存使用情况
                },
                request.request_id,
            )

    async def handle_request(
        self,
        method: str,
        path: str,
        data=None,
        query_params=None,
        headers=None,
        request_id=None,
    ):
        """处理请求的入口点"""
        # 增加请求计数
        if not hasattr(self, "request_count"):
            self.request_count = 0
            self.start_time = time.time()
        self.request_count += 1

        return await self.app.handle_request(
            method, path, data, query_params, headers, request_id
        )


class WindowsIPCIntegrationTest:
    """Windows IPC集成测试"""

    def __init__(self):
        self.server = None
        self.test_app = None
        self.test_pipe_name = f"linch-mind-integration-test-{os.getpid()}"
        self.is_running = False

    async def setup_test_environment(self):
        """设置测试环境"""
        logger.info("🚀 设置Windows IPC集成测试环境")

        if not check_windows_ipc_support():
            raise RuntimeError("Windows IPC不支持，无法进行集成测试")

        # 创建测试IPC应用
        self.test_app = TestIPCApplication()

        # 创建Windows IPC服务器
        self.server = WindowsIPCServer(self.test_pipe_name)
        self.server.set_ipc_app(self.test_app)

        # 启动服务器
        await self.server.start()
        self.is_running = True

        # 等待服务器完全启动
        await asyncio.sleep(0.5)

        logger.info(f"✅ 测试环境已设置，管道名: {self.test_pipe_name}")

    async def cleanup_test_environment(self):
        """清理测试环境"""
        if self.server and self.is_running:
            logger.info("🧹 清理测试环境")
            await self.server.stop()
            self.is_running = False

    async def run_integration_test(self):
        """运行集成测试"""
        try:
            await self.setup_test_environment()

            print("=" * 70)
            print("🧪 Windows Named Pipe IPC 集成测试")
            print("=" * 70)

            # 显示服务器统计信息
            await self.show_server_stats()

            # 运行外部客户端测试
            await self.run_external_client_test()

            # 显示最终统计信息
            await self.show_final_stats()

            print("\n🎉 集成测试完成!")
            return True

        except Exception as e:
            logger.error(f"集成测试失败: {e}", exc_info=True)
            print(f"❌ 集成测试失败: {e}")
            return False

        finally:
            await self.cleanup_test_environment()

    async def show_server_stats(self):
        """显示服务器统计信息"""
        if not self.server:
            return

        stats = self.server.get_stats()

        print("\n📊 服务器状态:")
        print(f"   启动时间: {stats['uptime_seconds']:.1f}s")
        print(f"   活跃连接: {stats['active_connections']}")
        print(f"   总请求数: {stats['total_requests']}")
        print(f"   失败请求: {stats['failed_requests']}")
        print(f"   平均响应时间: {stats['avg_response_time']:.3f}s")
        print(f"   安全启用: {'是' if stats['security_enabled'] else '否'}")
        print(f"   授权SID数: {stats['allowed_sids_count']}")

    async def show_final_stats(self):
        """显示最终统计信息"""
        print("\n📈 最终统计:")
        await self.show_server_stats()

    async def run_external_client_test(self):
        """运行外部客户端测试"""
        logger.info("运行外部客户端测试")

        try:
            # 动态导入测试客户端
            from services.windows_ipc_test_client import WindowsIPCTestClient

            client = WindowsIPCTestClient(self.test_pipe_name)

            print(f"\n🔗 使用管道: {client.full_pipe_name}")

            # 基本连接测试
            print("\n1️⃣ 健康检查测试")
            health_result = client.test_single_request(
                {
                    "method": "GET",
                    "path": "/api/v1/health",
                    "data": {},
                    "headers": {},
                    "query_params": {},
                }
            )

            if health_result["success"]:
                response_data = health_result["response"]
                if response_data.get("success"):
                    health_data = response_data["data"]
                    print("   ✅ 健康检查通过")
                    print(f"   状态: {health_data.get('status')}")
                    print(f"   响应时间: {health_result['response_time_ms']:.2f}ms")
                else:
                    print(f"   ❌ 健康检查失败: {response_data}")
            else:
                print(f"   ❌ 连接失败: {health_result['error']}")
                return

            # 回声测试
            print("\n2️⃣ 回声测试")
            echo_data = {"message": "Hello Windows IPC!", "test_id": 123}
            echo_result = client.test_single_request(
                {
                    "method": "GET",
                    "path": "/api/v1/echo",
                    "data": echo_data,
                    "headers": {"X-Test": "Echo"},
                    "query_params": {"format": "json"},
                }
            )

            if echo_result["success"] and echo_result["response"]["success"]:
                returned_data = echo_result["response"]["data"]["data"]
                if returned_data == echo_data:
                    print("   ✅ 数据回声正确")
                    print(f"   响应时间: {echo_result['response_time_ms']:.2f}ms")
                else:
                    print("   ❌ 数据不匹配")
                    print(f"   发送: {echo_data}")
                    print(f"   接收: {returned_data}")
            else:
                print("   ❌ 回声测试失败")

            # 数据处理测试
            print("\n3️⃣ 数据处理测试")
            process_result = client.test_single_request(
                {
                    "method": "POST",
                    "path": "/api/v1/process",
                    "data": {
                        "input_data": [1, 2, 3, 4, 5],
                        "operation": "sum",
                        "metadata": {"test": True},
                    },
                }
            )

            if process_result["success"] and process_result["response"]["success"]:
                processed = process_result["response"]["data"]
                print("   ✅ 数据处理成功")
                print(f"   处理时间: {processed.get('processing_time', 0)*1000:.1f}ms")
                print(f"   数据大小: {processed.get('size', 0)} 字符")
                print(f"   响应时间: {process_result['response_time_ms']:.2f}ms")
            else:
                print("   ❌ 数据处理失败")

            # 并发测试
            print("\n4️⃣ 并发测试")
            concurrent_result = client.test_concurrent_requests(
                num_requests=10, num_workers=3
            )

            stats = concurrent_result["stats"]
            print(f"   总请求: {stats['total_requests']}")
            print(f"   成功率: {stats['success_rate']:.1f}%")
            print(f"   平均响应时间: {stats.get('avg_response_time_ms', 0):.2f}ms")
            print(f"   吞吐量: {stats['requests_per_second']:.1f} req/s")

            if stats["success_rate"] >= 90:
                print("   ✅ 并发测试通过")
            else:
                print("   ⚠️  并发成功率较低")

        except ImportError as e:
            logger.error(f"无法导入测试客户端: {e}")
            print("❌ 无法运行外部客户端测试: 缺少测试客户端")
        except Exception as e:
            logger.error(f"外部客户端测试失败: {e}")
            print(f"❌ 外部客户端测试失败: {e}")


async def main():
    """主函数"""
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # 检查Windows支持
    if platform.system() != "Windows":
        print("❌ 此测试仅支持Windows系统")
        return False

    if not check_windows_ipc_support():
        print("❌ Windows IPC支持不可用")
        print("请安装依赖: pip install pywin32")
        return False

    # 运行集成测试
    integration_test = WindowsIPCIntegrationTest()
    success = await integration_test.run_integration_test()

    return success


def signal_handler(signum, frame):
    """信号处理器"""
    print(f"\n⚠️  收到信号 {signum}，正在退出...")
    sys.exit(0)


if __name__ == "__main__":
    # 注册信号处理器
    if platform.system() == "Windows":
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  测试被用户中断")
        sys.exit(130)
    except Exception as e:
        logger.error(f"测试执行失败: {e}", exc_info=True)
        sys.exit(1)
