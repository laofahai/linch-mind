#!/usr/bin/env python3
"""
三层存储架构集成测试
验证SQLite + NetworkX + FAISS的协同工作
"""

import tempfile
from pathlib import Path

import pytest

from config.core_config import StorageConfig
from services.database_service import DatabaseService
from services.storage.embedding_service import EmbeddingService
from services.storage.graph_service import GraphService
from services.storage.storage_orchestrator import StorageOrchestrator
from services.storage.vector_service import VectorService


@pytest.fixture
async def temp_storage_config():
    """创建临时存储配置"""
    with tempfile.TemporaryDirectory() as temp_dir:
        config = StorageConfig(
            data_directory=temp_dir,
            vector_dimension=384,
            vector_index_type="Flat",  # 测试用简单索引
            graph_enable_cache=True,
            embedding_model_name="all-MiniLM-L6-v2",
            embedding_cache_enabled=True,
            auto_sync_enabled=False,  # 测试时关闭自动同步
        )
        yield config


@pytest.fixture
async def storage_orchestrator(temp_storage_config):
    """创建存储编排器实例"""
    # 手动创建各个服务实例，避免全局单例
    db_service = DatabaseService()
    await db_service.initialize()

    graph_service = GraphService(
        data_dir=Path(temp_storage_config.data_directory) / "graph",
        max_workers=2,
        enable_cache=True,
    )
    await graph_service.initialize()

    vector_service = VectorService(
        data_dir=Path(temp_storage_config.data_directory) / "vectors",
        dimension=temp_storage_config.vector_dimension,
        index_type=temp_storage_config.vector_index_type,
        max_workers=2,
    )
    await vector_service.initialize()

    embedding_service = EmbeddingService(
        model_name=temp_storage_config.embedding_model_name,
        cache_dir=Path(temp_storage_config.data_directory) / "embeddings",
        max_workers=2,
        enable_cache=False,  # 测试时关闭缓存加速
    )
    await embedding_service.initialize()

    # 创建编排器
    orchestrator = StorageOrchestrator()
    orchestrator.db_service = db_service
    orchestrator.graph_service = graph_service
    orchestrator.vector_service = vector_service
    orchestrator.embedding_service = embedding_service

    yield orchestrator

    # 清理
    try:
        await graph_service.close()
        await vector_service.close()
        await embedding_service.close()
    except Exception as e:
        print(f"清理存储服务时出错: {e}")


class TestStorageIntegration:
    """三层存储架构集成测试"""

    async def test_create_entity_with_embedding(self, storage_orchestrator):
        """测试创建实体并自动生成embedding"""
        # 创建测试实体
        success = await storage_orchestrator.create_entity(
            entity_id="test_doc_001",
            name="测试文档",
            entity_type="document",
            description="这是一个测试文档，用于验证存储系统功能",
            content="测试文档内容：人工智能是一门计算机科学分支，致力于创建能够执行通常需要人类智能的任务的系统。",
            auto_embed=True,
        )

        assert success, "实体创建应该成功"

        # 验证实体在图数据库中存在
        graph_entity = await storage_orchestrator.graph_service.get_entity(
            "test_doc_001"
        )
        assert graph_entity is not None, "实体应该在图数据库中存在"
        assert graph_entity.name == "测试文档"
        assert graph_entity.entity_type == "document"

        # 验证向量文档存在
        vector_doc = await storage_orchestrator.vector_service.get_document(
            "emb_test_doc_001"
        )
        assert vector_doc is not None, "向量文档应该存在"
        assert vector_doc.entity_id == "test_doc_001"
        assert len(vector_doc.embedding) == 384, "向量维度应该正确"

    async def test_create_relationship(self, storage_orchestrator):
        """测试创建实体关系"""
        # 创建两个测试实体
        await storage_orchestrator.create_entity(
            entity_id="entity_a",
            name="实体A",
            entity_type="concept",
            content="实体A的内容",
        )

        await storage_orchestrator.create_entity(
            entity_id="entity_b",
            name="实体B",
            entity_type="concept",
            content="实体B的内容",
        )

        # 创建关系
        success = await storage_orchestrator.create_relationship(
            source_entity="entity_a",
            target_entity="entity_b",
            relationship_type="related_to",
            strength=0.8,
            confidence=0.9,
        )

        assert success, "关系创建应该成功"

        # 验证图中存在关系
        neighbors = await storage_orchestrator.graph_service.find_neighbors(
            "entity_a", max_depth=1
        )
        assert "entity_b" in neighbors, "entity_b应该是entity_a的邻居"

    async def test_semantic_search(self, storage_orchestrator):
        """测试语义搜索功能"""
        # 创建多个测试文档
        test_docs = [
            {
                "id": "doc_ai_001",
                "name": "人工智能基础",
                "content": "人工智能是计算机科学的一个分支，致力于创建智能机器。",
            },
            {
                "id": "doc_ml_001",
                "name": "机器学习原理",
                "content": "机器学习是人工智能的一个子领域，通过算法让计算机从数据中学习。",
            },
            {
                "id": "doc_cook_001",
                "name": "烹饪技巧",
                "content": "烹饪是一门艺术，需要掌握火候、调料和食材的搭配。",
            },
        ]

        # 创建所有文档
        for doc in test_docs:
            await storage_orchestrator.create_entity(
                entity_id=doc["id"],
                name=doc["name"],
                entity_type="document",
                content=doc["content"],
                auto_embed=True,
            )

        # 执行语义搜索
        results = await storage_orchestrator.semantic_search(
            query="人工智能和机器学习", k=3
        )

        assert len(results) >= 2, "应该返回相关结果"

        # 验证搜索结果的相关性
        result_ids = [r.entity_id for r in results]
        assert "doc_ai_001" in result_ids, "AI文档应该在搜索结果中"
        assert "doc_ml_001" in result_ids, "ML文档应该在搜索结果中"

        # 验证分数排序
        ai_result = next(r for r in results if r.entity_id == "doc_ai_001")
        cook_result = next((r for r in results if r.entity_id == "doc_cook_001"), None)

        if cook_result:
            assert ai_result.score > cook_result.score, "AI文档的相关性分数应该更高"

    async def test_graph_search(self, storage_orchestrator):
        """测试图结构搜索"""
        # 创建一个简单的图结构: A -> B -> C
        entities = ["node_a", "node_b", "node_c"]
        for entity_id in entities:
            await storage_orchestrator.create_entity(
                entity_id=entity_id,
                name=f"节点{entity_id[-1].upper()}",
                entity_type="node",
                content=f"这是节点{entity_id[-1].upper()}的内容",
            )

        # 创建关系
        await storage_orchestrator.create_relationship(
            "node_a", "node_b", "connects_to"
        )
        await storage_orchestrator.create_relationship(
            "node_b", "node_c", "connects_to"
        )

        # 测试深度1搜索
        neighbors_depth1 = await storage_orchestrator.graph_search(
            entity_id="node_a", max_depth=1
        )
        assert "node_b" in neighbors_depth1, "深度1搜索应该找到node_b"
        assert "node_c" not in neighbors_depth1, "深度1搜索不应该找到node_c"

        # 测试深度2搜索
        neighbors_depth2 = await storage_orchestrator.graph_search(
            entity_id="node_a", max_depth=2
        )
        assert "node_b" in neighbors_depth2, "深度2搜索应该找到node_b"
        assert "node_c" in neighbors_depth2, "深度2搜索应该找到node_c"

    async def test_smart_recommendations(self, storage_orchestrator):
        """测试智能推荐功能"""
        # 创建一些测试实体
        entities = [
            {
                "id": "tech_001",
                "name": "Python编程",
                "type": "skill",
                "content": "Python是一种高级编程语言",
            },
            {
                "id": "tech_002",
                "name": "机器学习",
                "type": "skill",
                "content": "机器学习是人工智能的核心技术",
            },
            {
                "id": "tech_003",
                "name": "数据分析",
                "type": "skill",
                "content": "数据分析帮助理解数据背后的信息",
            },
        ]

        for entity in entities:
            await storage_orchestrator.create_entity(
                entity_id=entity["id"],
                name=entity["name"],
                entity_type=entity["type"],
                content=entity["content"],
                auto_embed=True,
            )

        # 创建一些关系
        await storage_orchestrator.create_relationship(
            "tech_001", "tech_002", "enables"
        )
        await storage_orchestrator.create_relationship(
            "tech_002", "tech_003", "requires"
        )

        # 获取推荐
        recommendations = await storage_orchestrator.get_smart_recommendations(
            max_recommendations=5, algorithm="hybrid"
        )

        assert len(recommendations) > 0, "应该返回推荐结果"

        # 验证推荐结果格式
        for rec in recommendations:
            assert rec.entity_id, "推荐应该有实体ID"
            assert rec.entity_name, "推荐应该有实体名称"
            assert rec.score > 0, "推荐分数应该大于0"
            assert rec.source in [
                "graph",
                "vector",
                "behavior",
                "hybrid",
            ], "推荐来源应该有效"

    async def test_storage_metrics(self, storage_orchestrator):
        """测试存储系统指标"""
        # 创建一些测试数据
        await storage_orchestrator.create_entity(
            entity_id="metric_test_001",
            name="指标测试",
            entity_type="test",
            content="用于测试系统指标的实体",
        )

        await storage_orchestrator.create_entity(
            entity_id="metric_test_002",
            name="指标测试2",
            entity_type="test",
            content="另一个测试实体",
        )

        await storage_orchestrator.create_relationship(
            "metric_test_001", "metric_test_002", "test_relation"
        )

        # 获取指标
        metrics = await storage_orchestrator.get_metrics()

        assert metrics.total_entities >= 2, "实体数量应该正确"
        assert metrics.total_relationships >= 1, "关系数量应该正确"
        assert metrics.health_status == "healthy", "系统状态应该健康"

    async def test_entity_lifecycle(self, storage_orchestrator):
        """测试实体生命周期管理"""
        entity_id = "lifecycle_test_001"

        # 创建实体
        success = await storage_orchestrator.create_entity(
            entity_id=entity_id,
            name="生命周期测试",
            entity_type="test",
            description="用于测试实体生命周期",
            content="测试内容",
        )
        assert success, "实体创建应该成功"

        # 获取实体
        entity = await storage_orchestrator.get_entity(entity_id)
        assert entity is not None, "应该能获取到实体"
        assert entity.name == "生命周期测试"

        # 更新实体
        success = await storage_orchestrator.update_entity(
            entity_id, {"name": "更新后的测试", "description": "更新后的描述"}
        )
        assert success, "实体更新应该成功"

        # 验证更新
        updated_entity = await storage_orchestrator.get_entity(entity_id)
        assert updated_entity.name == "更新后的测试"

        # 删除实体
        success = await storage_orchestrator.delete_entity(entity_id)
        assert success, "实体删除应该成功"

        # 验证删除
        deleted_entity = await storage_orchestrator.get_entity(entity_id)
        assert deleted_entity is None, "删除后不应该能获取到实体"


@pytest.mark.asyncio
class TestEmbeddingService:
    """嵌入服务独立测试"""

    async def test_text_encoding(self):
        """测试文本编码功能"""
        with tempfile.TemporaryDirectory() as temp_dir:
            service = EmbeddingService(
                model_name="all-MiniLM-L6-v2",
                cache_dir=Path(temp_dir),
                enable_cache=False,
            )

            await service.initialize()

            try:
                # 测试单个文本编码
                embedding = await service.encode_text("这是一个测试文本")
                assert len(embedding) == 384, "嵌入向量维度应该正确"
                assert embedding.dtype.name == "float32", "数据类型应该正确"

                # 测试批量编码
                texts = ["文本1", "文本2", "文本3"]
                embeddings = await service.encode_texts(texts)
                assert embeddings.shape == (3, 384), "批量编码结果形状应该正确"

                # 测试相似性计算
                similarity = await service.compute_similarity("苹果", "水果")
                assert 0 <= similarity <= 1, "相似性分数应该在0-1之间"

            finally:
                await service.close()


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
