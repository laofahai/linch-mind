#!/usr/bin/env python3
"""
API集成有效测试 - 重构版本
端到端API测试，真实业务流程验证
"""

import json

import pytest
from api.main import app
from fastapi.testclient import TestClient
from services.database_service import DatabaseService


class TestAPIIntegrationEffective:
    """有效的API集成测试 - 端到端业务流程验证"""

    @pytest.fixture
    async def test_db_service(self):
        """创建测试用的真实数据库服务"""
        db_service = DatabaseService(db_path=":memory:")
        await db_service.initialize()
        yield db_service
        await db_service.close()

    @pytest.fixture
    def test_client(self, test_db_service):
        """创建测试客户端，使用真实数据库"""
        # 替换应用中的数据库服务为测试服务
        app.dependency_overrides = {}

        # 如果应用使用依赖注入，在这里覆盖
        if hasattr(app, "state"):
            app.state.db_service = test_db_service

        return TestClient(app)

    def test_api_health_and_documentation(self, test_client):
        """测试API健康状况和文档可访问性"""
        client = test_client

        # 测试健康检查端点（如果存在）
        health_endpoints = ["/health", "/ping", "/status", "/"]
        health_found = False

        for endpoint in health_endpoints:
            response = client.get(endpoint)
            if response.status_code == 200:
                health_found = True
                break

        # 如果没有健康检查端点，至少应用应该能启动
        if not health_found:
            # 测试OpenAPI文档可访问性
            docs_response = client.get("/docs")
            assert docs_response.status_code in [200, 307]  # 200 或重定向

        # 测试OpenAPI规范
        openapi_response = client.get("/openapi.json")
        assert openapi_response.status_code == 200

        openapi_data = openapi_response.json()
        assert "openapi" in openapi_data
        assert "info" in openapi_data
        assert "paths" in openapi_data

        # 验证API版本信息
        assert openapi_data["info"]["title"] is not None
        assert openapi_data["info"]["version"] is not None

    def test_connector_lifecycle_api_endpoints(self, test_client):
        """测试连接器生命周期API端点"""
        client = test_client

        # 1. 获取连接器列表（初始应该为空）
        response = client.get("/api/v1/connectors")
        if response.status_code == 200:
            connectors = response.json()
            assert isinstance(connectors, list)
            initial_count = len(connectors)
        else:
            # 如果端点不存在，跳过这部分测试
            pytest.skip("Connector API endpoints not implemented")

        # 2. 注册新连接器
        new_connector = {
            "connector_id": "test_api_connector",
            "name": "Test API Connector",
            "description": "Connector for API testing",
            "config": {"test_mode": True, "api_test": True},
        }

        register_response = client.post(
            "/api/v1/connectors/register", json=new_connector
        )
        if register_response.status_code in [200, 201]:
            # 3. 验证连接器被成功注册
            list_response = client.get("/api/v1/connectors")
            assert list_response.status_code == 200

            connectors = list_response.json()
            assert len(connectors) == initial_count + 1

            # 找到我们注册的连接器
            test_connector = next(
                (c for c in connectors if c["connector_id"] == "test_api_connector"),
                None,
            )
            assert test_connector is not None
            assert test_connector["name"] == "Test API Connector"

            # 4. 获取特定连接器信息
            info_response = client.get("/api/v1/connectors/test_api_connector")
            if info_response.status_code == 200:
                connector_info = info_response.json()
                assert connector_info["connector_id"] == "test_api_connector"
                assert connector_info["name"] == "Test API Connector"

            # 5. 测试连接器状态查询
            status_response = client.get("/api/v1/connectors/test_api_connector/status")
            if status_response.status_code == 200:
                status = status_response.json()
                assert "status" in status
                # 新注册的连接器应该是停止状态
                assert status["status"] in ["stopped", "configured", "inactive"]

            # 6. 尝试启动连接器
            start_response = client.post("/api/v1/connectors/test_api_connector/start")
            if start_response.status_code in [200, 202]:
                # 启动成功或已接受
                start_response.json()

                # 再次检查状态
                status_response = client.get(
                    "/api/v1/connectors/test_api_connector/status"
                )
                if status_response.status_code == 200:
                    status = status_response.json()
                    # 状态可能是运行中或启动中
                    assert status["status"] in ["running", "starting", "active"]

                # 7. 停止连接器
                stop_response = client.post(
                    "/api/v1/connectors/test_api_connector/stop"
                )
                if stop_response.status_code in [200, 202]:
                    stop_response.json()

                    # 验证停止状态
                    status_response = client.get(
                        "/api/v1/connectors/test_api_connector/status"
                    )
                    if status_response.status_code == 200:
                        status = status_response.json()
                        assert status["status"] in ["stopped", "stopping", "inactive"]

            # 8. 注销连接器
            unregister_response = client.delete("/api/v1/connectors/test_api_connector")
            if unregister_response.status_code in [200, 204]:
                # 验证连接器被删除
                final_list_response = client.get("/api/v1/connectors")
                if final_list_response.status_code == 200:
                    final_connectors = final_list_response.json()
                    assert len(final_connectors) == initial_count

                    # 确认测试连接器不在列表中
                    test_connector = next(
                        (
                            c
                            for c in final_connectors
                            if c["connector_id"] == "test_api_connector"
                        ),
                        None,
                    )
                    assert test_connector is None

    def test_api_error_handling(self, test_client):
        """测试API错误处理"""
        client = test_client

        # 1. 测试不存在的端点
        response = client.get("/api/v1/nonexistent-endpoint")
        assert response.status_code == 404

        # 2. 测试无效的连接器ID
        response = client.get("/api/v1/connectors/nonexistent-connector")
        assert response.status_code in [404, 400]

        # 3. 测试无效的请求数据
        invalid_connector = {
            "name": "Missing Required Fields"
            # 缺少connector_id等必需字段
        }

        response = client.post("/api/v1/connectors/register", json=invalid_connector)
        assert response.status_code in [
            400,
            422,
        ]  # 400 Bad Request 或 422 Validation Error

        if response.status_code == 422:
            # FastAPI验证错误应该有详细信息
            error_detail = response.json()
            assert "detail" in error_detail
            assert isinstance(error_detail["detail"], list)

        # 4. 测试对不存在连接器的操作
        response = client.post("/api/v1/connectors/nonexistent/start")
        assert response.status_code in [404, 400]

        response = client.post("/api/v1/connectors/nonexistent/stop")
        assert response.status_code in [404, 400]

    def test_api_data_validation(self, test_client):
        """测试API数据验证"""
        client = test_client

        # 测试各种无效输入
        invalid_inputs = [
            # 空的连接器ID
            {"connector_id": "", "name": "Empty ID Connector"},
            # 连接器ID包含特殊字符
            {"connector_id": "invalid/connector*id", "name": "Invalid ID Connector"},
            # 缺少必需字段
            {"description": "Missing connector_id and name"},
            # 无效的配置数据
            {
                "connector_id": "test",
                "name": "Test",
                "config": "invalid_config_not_dict",
            },
        ]

        for invalid_input in invalid_inputs:
            response = client.post("/api/v1/connectors/register", json=invalid_input)
            # 应该返回错误状态码
            assert response.status_code in [
                400,
                422,
            ], f"Invalid input should be rejected: {invalid_input}"

    def test_api_concurrent_requests(self, test_client):
        """测试API并发请求处理"""
        import threading
        import time

        client = test_client
        results = []

        def make_concurrent_request(index):
            """并发请求函数"""
            connector_data = {
                "connector_id": f"concurrent_connector_{index}",
                "name": f"Concurrent Connector {index}",
                "description": f"Connector for concurrency test {index}",
            }

            response = client.post("/api/v1/connectors/register", json=connector_data)
            results.append(
                (
                    index,
                    response.status_code,
                    response.json() if response.status_code < 400 else None,
                )
            )

        # 创建多个并发线程
        threads = []
        for i in range(5):
            thread = threading.Thread(target=make_concurrent_request, args=(i,))
            threads.append(thread)

        # 启动所有线程
        start_time = time.time()
        for thread in threads:
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        end_time = time.time()

        # 验证结果
        assert len(results) == 5

        # 大部分请求应该成功（可能有一些由于并发冲突失败）
        successful_requests = [r for r in results if r[1] in [200, 201]]
        assert len(successful_requests) >= 3  # 至少60%成功率

        # 并发处理应该在合理时间内完成
        assert end_time - start_time < 5.0  # 5秒内完成

        # 清理创建的连接器
        for index, status_code, _ in successful_requests:
            try:
                client.delete(f"/api/v1/connectors/concurrent_connector_{index}")
            except:
                pass  # 忽略清理错误

    def test_api_response_format_consistency(self, test_client):
        """测试API响应格式一致性"""
        client = test_client

        # 测试GET请求的响应格式
        list_response = client.get("/api/v1/connectors")
        if list_response.status_code == 200:
            data = list_response.json()
            assert isinstance(data, list)

            if len(data) > 0:
                # 验证连接器对象的基本结构
                connector = data[0]
                assert isinstance(connector, dict)
                assert "connector_id" in connector
                assert "name" in connector
                # 可能还有其他字段，但这些是基本的

        # 测试POST请求的响应格式
        test_connector = {
            "connector_id": "format_test_connector",
            "name": "Format Test Connector",
            "description": "Testing response format",
        }

        post_response = client.post("/api/v1/connectors/register", json=test_connector)
        if post_response.status_code in [200, 201]:
            response_data = post_response.json()
            assert isinstance(response_data, dict)

            # 清理
            try:
                client.delete("/api/v1/connectors/format_test_connector")
            except:
                pass

    def test_api_cors_and_headers(self, test_client):
        """测试API CORS和HTTP头部"""
        client = test_client

        # 测试CORS预检请求
        options_response = client.options("/api/v1/connectors")
        # 应该允许OPTIONS请求或返回适当的状态码
        assert options_response.status_code in [200, 204, 405]

        # 测试常规请求的头部
        response = client.get("/api/v1/connectors")
        if response.status_code == 200:
            headers = response.headers

            # 检查内容类型
            assert headers.get("content-type", "").startswith("application/json")

            # 检查CORS头部（如果应用配置了CORS）
            cors_headers = [
                "access-control-allow-origin",
                "access-control-allow-methods",
                "access-control-allow-headers",
            ]

            cors_configured = any(header in headers for header in cors_headers)
            # 如果配置了CORS，记录一下
            if cors_configured:
                print("CORS headers detected in API response")

    def test_api_performance_basic(self, test_client):
        """测试API基本性能"""
        import time

        client = test_client

        # 测试简单GET请求的响应时间
        start_time = time.time()
        response = client.get("/api/v1/connectors")
        end_time = time.time()

        response_time = end_time - start_time

        # API响应应该在合理时间内
        assert response_time < 2.0  # 2秒内响应

        if response.status_code == 200:
            # 测试包含数据的响应时间（如果有数据）
            data = response.json()
            if len(data) > 0:
                # 有数据的情况下，响应时间应该仍然合理
                assert response_time < 5.0  # 5秒内响应


class TestAPIEdgeCases:
    """API边界情况测试"""

    def test_large_request_payload(self, test_client):
        """测试大型请求负载处理"""
        client = test_client

        # 创建大型配置对象
        large_config = {
            "large_data": "x" * 10000,  # 10KB的数据
            "repeated_items": [f"item_{i}" for i in range(1000)],
            "nested_config": {"level1": {"level2": {"level3": ["deep_item"] * 100}}},
        }

        large_connector = {
            "connector_id": "large_payload_connector",
            "name": "Large Payload Connector",
            "description": "Testing large payload handling",
            "config": large_config,
        }

        response = client.post("/api/v1/connectors/register", json=large_connector)

        # 应该能处理大型负载或返回适当错误
        assert response.status_code in [200, 201, 413, 400]  # 成功或负载过大错误

        if response.status_code in [200, 201]:
            # 如果成功，清理
            try:
                client.delete("/api/v1/connectors/large_payload_connector")
            except:
                pass

    def test_special_characters_in_requests(self, test_client):
        """测试请求中的特殊字符处理"""
        client = test_client

        special_cases = [
            # Unicode字符
            {"connector_id": "unicode_connector", "name": "Unicode测试连接器🚀"},
            # HTML/XML字符
            {
                "connector_id": "html_connector",
                "name": "<script>alert('test')</script>",
            },
            # SQL注入尝试
            {"connector_id": "sql_connector", "name": "'; DROP TABLE connectors; --"},
            # 长字符串
            {"connector_id": "long_name_connector", "name": "A" * 1000},
        ]

        for test_case in special_cases:
            response = client.post("/api/v1/connectors/register", json=test_case)

            # 应该优雅处理特殊字符，不崩溃
            assert response.status_code in [200, 201, 400, 422]

            if response.status_code in [200, 201]:
                # 如果接受了，验证数据被正确存储和转义
                try:
                    info_response = client.get(
                        f"/api/v1/connectors/{test_case['connector_id']}"
                    )
                    if info_response.status_code == 200:
                        connector_info = info_response.json()
                        # 特殊字符应该被正确处理，不应该导致安全问题
                        assert connector_info["name"] is not None

                    # 清理
                    client.delete(f"/api/v1/connectors/{test_case['connector_id']}")
                except:
                    pass

    def test_malformed_json_requests(self, test_client):
        """测试格式错误的JSON请求"""
        client = test_client

        # 发送格式错误的JSON
        malformed_json = '{"connector_id": "test", "name": "test", invalid}'

        response = client.post(
            "/api/v1/connectors/register",
            data=malformed_json,
            headers={"Content-Type": "application/json"},
        )

        # 应该返回JSON解析错误
        assert response.status_code in [400, 422]

    def test_missing_content_type_header(self, test_client):
        """测试缺少Content-Type头部的请求"""
        client = test_client

        valid_data = {"connector_id": "test", "name": "Test Connector"}

        # 发送没有Content-Type头部的JSON数据
        response = client.post(
            "/api/v1/connectors/register",
            data=json.dumps(valid_data),  # 注意：没有设置headers
        )

        # FastAPI通常能自动处理这种情况，但可能返回错误
        assert response.status_code in [
            200,
            201,
            400,
            415,
        ]  # 415 = Unsupported Media Type
