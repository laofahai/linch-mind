#!/usr/bin/env python3
"""
直接测试服务注册状态 - 通过检查DI容器的服务
"""

import sys
from pathlib import Path

# 添加daemon路径
daemon_path = Path(__file__).parent / "daemon"
sys.path.insert(0, str(daemon_path))


def test_service_registration():
    """测试服务注册状态"""
    try:
        # 初始化配置和依赖注入容器
        from config.core_config import get_core_config

        # 获取配置管理器
        get_core_config()
        print(f"✅ 配置管理器初始化成功")

        # 初始化DI容器（模拟main.py的initialize_di_container）
        from main import initialize_di_container

        container = initialize_di_container()

        print(f"🏗️ DI容器初始化完成")

        # 检查智能服务注册状态
        services_to_check = [
            "VectorService",
            "EmbeddingService",
            "GraphService",
            "StorageOrchestrator",
        ]

        for service_name in services_to_check:
            # 检查服务是否在容器中注册
            all_services = container.get_all_services()
            registered = any(
                service_name in str(svc_type) for svc_type in all_services.keys()
            )

            if registered:
                print(f"✅ {service_name}: 已注册")

                # 尝试获取服务实例（测试创建）
                try:
                    if service_name == "VectorService":
                        from services.storage.vector_service import VectorService

                        service = container.get_service(VectorService)
                    elif service_name == "EmbeddingService":
                        from services.storage.embedding_service import EmbeddingService

                        service = container.get_service(EmbeddingService)
                    elif service_name == "GraphService":
                        from services.storage.graph_service import GraphService

                        service = container.get_service(GraphService)
                    elif service_name == "StorageOrchestrator":
                        from services.storage.storage_orchestrator import (
                            StorageOrchestrator,
                        )

                        service = container.get_service(StorageOrchestrator)

                    print(f"   ✅ 服务实例创建成功: {type(service).__name__}")

                except Exception as e:
                    print(f"   ❌ 服务实例创建失败: {e}")
            else:
                print(f"❌ {service_name}: 未注册")

        # 显示所有注册的服务
        all_services = container.get_all_services()
        print(f"\n📦 总共注册了 {len(all_services)} 个服务:")
        for i, (service_type, _) in enumerate(all_services.items(), 1):
            service_name = (
                service_type.__name__
                if hasattr(service_type, "__name__")
                else str(service_type)
            )
            print(f"   {i}. {service_name}")

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback

        print(f"详细错误: {traceback.format_exc()}")


if __name__ == "__main__":
    test_service_registration()
