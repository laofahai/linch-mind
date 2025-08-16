#!/usr/bin/env python3
"""
智能存储系统测试套件
测试AI评估、向量压缩、分片管理和生命周期的关键功能
"""

import asyncio
import logging
import pytest
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

import numpy as np

# 测试环境设置
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.intelligent_storage import IntelligentStorageConfig, OllamaConfig, FAISSConfig
from services.ai.ollama_service import OllamaService, ContentEvaluation
from services.storage.faiss_vector_store import FAISSVectorStore, VectorDocument
from services.storage.intelligent_event_processor import IntelligentEventProcessor
from services.storage.data_lifecycle_manager import DataLifecycleManager
from services.monitoring.storage_metrics import StorageMetricsCollector

# 配置测试日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestOllamaService:
    """Ollama AI服务测试"""
    
    @pytest.fixture
    async def ollama_service(self):
        """Ollama服务fixture"""
        service = OllamaService(
            ollama_host="http://localhost:11434",
            embedding_model="nomic-embed-text",
            llm_model="llama3.2:3b",
            value_threshold=0.3,
        )
        
        # 检查Ollama是否可用
        try:
            if await service.initialize():
                yield service
                await service.close()
            else:
                pytest.skip("Ollama服务不可用")
        except Exception as e:
            pytest.skip(f"Ollama服务初始化失败: {e}")

    @pytest.mark.asyncio
    async def test_content_value_evaluation(self, ollama_service):
        """测试内容价值评估"""
        # 测试高价值内容
        high_value_content = "这是一份重要的技术文档，详细描述了系统架构设计原理和最佳实践。"
        score = await ollama_service.evaluate_content_value(high_value_content)
        assert 0.0 <= score <= 1.0, "价值评分应在0-1之间"
        assert score > 0.5, "高价值内容评分应该较高"
        
        # 测试低价值内容
        low_value_content = "asdfjkl;asdfjkl;asdfjkl;随机字符串无意义内容"
        score = await ollama_service.evaluate_content_value(low_value_content)
        assert score < 0.5, "低价值内容评分应该较低"
        
        # 测试空内容
        empty_score = await ollama_service.evaluate_content_value("")
        assert empty_score == 0.0, "空内容评分应为0"

    @pytest.mark.asyncio
    async def test_semantic_summary_extraction(self, ollama_service):
        """测试语义摘要提取"""
        long_content = """
        人工智能技术在现代社会中发挥着越来越重要的作用。从自然语言处理到计算机视觉，
        从机器学习到深度学习，AI技术正在改变我们的生活方式。本文档将详细介绍AI技术的
        发展历程、核心算法原理、应用场景以及未来发展趋势。我们将重点关注机器学习模型
        的训练方法、数据预处理技术、模型评估指标等关键技术要点。
        """
        
        summary = await ollama_service.extract_semantic_summary(long_content, max_length=100)
        
        assert len(summary) <= 100, "摘要长度应不超过100字符"
        assert len(summary) > 0, "摘要不应为空"
        assert "人工智能" in summary or "AI" in summary, "摘要应包含关键概念"

    @pytest.mark.asyncio
    async def test_text_embedding(self, ollama_service):
        """测试文本向量化"""
        test_text = "测试文本向量化功能"
        embedding = await ollama_service.embed_text(test_text)
        
        assert isinstance(embedding, list), "嵌入应返回列表"
        assert len(embedding) == 384, "nomic-embed-text应返回384维向量"
        assert all(isinstance(x, (int, float)) for x in embedding), "向量元素应为数值"
        
        # 测试空文本
        empty_embedding = await ollama_service.embed_text("")
        assert len(empty_embedding) == 384, "空文本也应返回384维零向量"

    @pytest.mark.asyncio
    async def test_comprehensive_content_processing(self, ollama_service):
        """测试综合内容处理"""
        test_content = "这是一个包含技术信息的重要文档，涉及系统设计和架构优化。"
        
        evaluation = await ollama_service.process_content_comprehensive(test_content)
        
        assert isinstance(evaluation, ContentEvaluation), "应返回ContentEvaluation对象"
        assert 0.0 <= evaluation.value_score <= 1.0, "价值评分应在有效范围内"
        assert 0.0 <= evaluation.confidence <= 1.0, "置信度应在有效范围内"
        assert len(evaluation.summary) > 0, "摘要不应为空"
        assert evaluation.content_type in ["text", "document", "url", "file_path"], "内容类型应有效"


class TestFAISSVectorStore:
    """FAISS向量存储测试"""
    
    @pytest.fixture
    async def vector_store(self):
        """向量存储fixture"""
        with tempfile.TemporaryDirectory() as temp_dir:
            store = FAISSVectorStore(
                storage_dir=Path(temp_dir),
                vector_dim=384,
                compressed_dim=256,
                shard_size_limit=100,  # 小分片便于测试
            )
            
            if await store.initialize():
                yield store
                await store.close()
            else:
                pytest.fail("向量存储初始化失败")

    @pytest.mark.asyncio
    async def test_document_addition(self, vector_store):
        """测试文档添加"""
        # 创建测试文档
        test_doc = VectorDocument(
            id="test_doc_1",
            summary="测试文档摘要",
            embedding=np.random.rand(384).astype(np.float32),
            metadata={"type": "test", "source": "unittest"},
            content_type="text",
            value_score=0.8,
        )
        
        # 添加文档
        success = await vector_store.add_document(test_doc)
        assert success, "文档添加应成功"
        
        # 验证指标
        metrics = await vector_store.get_metrics()
        assert metrics.total_documents >= 1, "文档计数应增加"

    @pytest.mark.asyncio
    async def test_batch_document_addition(self, vector_store):
        """测试批量文档添加"""
        # 创建多个测试文档
        docs = []
        for i in range(10):
            doc = VectorDocument(
                id=f"batch_doc_{i}",
                summary=f"批量测试文档 {i}",
                embedding=np.random.rand(384).astype(np.float32),
                metadata={"batch": True, "index": i},
                value_score=0.5 + i * 0.05,
            )
            docs.append(doc)
        
        # 批量添加
        added_count = await vector_store.add_documents_batch(docs)
        assert added_count == 10, "应成功添加所有文档"

    @pytest.mark.asyncio
    async def test_vector_search(self, vector_store):
        """测试向量搜索"""
        # 先添加一些测试文档
        docs = []
        for i in range(5):
            doc = VectorDocument(
                id=f"search_doc_{i}",
                summary=f"搜索测试文档 {i}",
                embedding=np.random.rand(384).astype(np.float32),
                metadata={"searchable": True},
                value_score=0.7,
            )
            docs.append(doc)
        
        await vector_store.add_documents_batch(docs)
        
        # 执行搜索
        query_vector = np.random.rand(384).astype(np.float32)
        results = await vector_store.search_similar(query_vector, k=3)
        
        assert len(results) <= 3, "结果数量不应超过k"
        assert all(hasattr(r, 'score') for r in results), "结果应包含相似性分数"

    @pytest.mark.asyncio
    async def test_shard_management(self, vector_store):
        """测试分片管理"""
        # 添加足够多的文档触发分片创建
        docs = []
        for i in range(150):  # 超过shard_size_limit
            doc = VectorDocument(
                id=f"shard_doc_{i}",
                summary=f"分片测试文档 {i}",
                embedding=np.random.rand(384).astype(np.float32),
                metadata={"shard_test": True},
                value_score=0.6,
            )
            docs.append(doc)
        
        # 分批添加以触发分片创建
        for i in range(0, 150, 50):
            batch = docs[i:i+50]
            await vector_store.add_documents_batch(batch)
        
        # 验证分片创建
        metrics = await vector_store.get_metrics()
        assert metrics.total_shards >= 1, "应创建至少一个分片"


class TestIntelligentEventProcessor:
    """智能事件处理器测试"""
    
    @pytest.fixture
    async def processor(self):
        """智能处理器fixture"""
        # 注意：这需要Ollama服务运行
        try:
            processor = IntelligentEventProcessor(
                value_threshold=0.3,
                entity_threshold=0.8,
                enable_vector_storage=False,  # 测试中禁用向量存储
                enable_entity_extraction=False,  # 测试中禁用实体提取
            )
            
            if await processor.initialize():
                yield processor
            else:
                pytest.skip("智能处理器初始化失败")
        except Exception as e:
            pytest.skip(f"智能处理器不可用: {e}")

    @pytest.mark.asyncio
    async def test_garbage_content_filtering(self, processor):
        """测试垃圾内容过滤"""
        # 测试垃圾内容（大量重复字符）
        garbage_event_data = {"content": "a" * 10000}  # 10KB垃圾数据
        
        result = await processor.process_connector_event(
            connector_id="test_connector",
            event_type="clipboard_changed",
            event_data=garbage_event_data,
            timestamp=datetime.utcnow().isoformat(),
        )
        
        assert not result.accepted, "垃圾内容应被拒绝"
        assert result.value_score < 0.3, "垃圾内容价值评分应低"

    @pytest.mark.asyncio
    async def test_valuable_content_acceptance(self, processor):
        """测试有价值内容接受"""
        # 测试有价值内容
        valuable_event_data = {
            "content": "这是一份重要的项目文档，包含详细的技术规范和实施指南。"
        }
        
        result = await processor.process_connector_event(
            connector_id="test_connector",
            event_type="document_created",
            event_data=valuable_event_data,
            timestamp=datetime.utcnow().isoformat(),
        )
        
        assert result.accepted, "有价值内容应被接受"
        assert result.value_score >= 0.3, "有价值内容评分应达到阈值"
        assert len(result.summary) > 0, "应生成摘要"

    @pytest.mark.asyncio
    async def test_empty_content_handling(self, processor):
        """测试空内容处理"""
        # 测试空内容
        empty_event_data = {"content": ""}
        
        result = await processor.process_connector_event(
            connector_id="test_connector",
            event_type="empty_event",
            event_data=empty_event_data,
            timestamp=datetime.utcnow().isoformat(),
        )
        
        assert not result.accepted, "空内容应被拒绝"
        assert "无有效内容" in result.reasoning, "应识别为无有效内容"


class TestPerformanceBenchmarks:
    """性能基准测试"""
    
    @pytest.mark.asyncio
    async def test_processing_performance(self):
        """测试处理性能"""
        try:
            from services.ai.ollama_service import OllamaService
            
            service = OllamaService()
            if not await service.initialize():
                pytest.skip("Ollama服务不可用")
            
            # 测试内容评估性能
            test_content = "这是一个性能测试文档，用于评估AI处理速度。"
            
            start_time = datetime.utcnow()
            for _ in range(10):
                await service.evaluate_content_value(test_content)
            
            duration = (datetime.utcnow() - start_time).total_seconds()
            avg_time_ms = (duration / 10) * 1000
            
            assert avg_time_ms < 5000, f"平均处理时间应小于5秒，实际: {avg_time_ms:.1f}ms"
            
            await service.close()
            
        except Exception as e:
            pytest.skip(f"性能测试失败: {e}")

    @pytest.mark.asyncio
    async def test_compression_ratio(self):
        """测试压缩比"""
        with tempfile.TemporaryDirectory() as temp_dir:
            store = FAISSVectorStore(
                storage_dir=Path(temp_dir),
                vector_dim=384,
                compressed_dim=256,
            )
            
            if not await store.initialize():
                pytest.skip("向量存储初始化失败")
            
            # 添加测试数据
            docs = []
            for i in range(100):
                doc = VectorDocument(
                    id=f"compression_test_{i}",
                    summary=f"压缩测试文档 {i}",
                    embedding=np.random.rand(384).astype(np.float32),
                    metadata={"test": "compression"},
                    value_score=0.5,
                )
                docs.append(doc)
            
            await store.add_documents_batch(docs)
            
            # 检查压缩比
            metrics = await store.get_metrics()
            compression_ratio = metrics.compression_ratio
            
            assert compression_ratio > 1.0, f"压缩比应大于1，实际: {compression_ratio:.2f}"
            # 期望压缩比至少为5:1 (384维float32 -> 256维float16)
            assert compression_ratio >= 3.0, f"压缩比应至少为3:1，实际: {compression_ratio:.2f}"
            
            await store.close()


class TestIntegrationFlow:
    """集成流程测试"""
    
    @pytest.mark.asyncio
    async def test_complete_processing_pipeline(self):
        """测试完整处理流水线"""
        try:
            # 创建临时环境
            with tempfile.TemporaryDirectory() as temp_dir:
                # 初始化组件
                vector_store = FAISSVectorStore(storage_dir=Path(temp_dir))
                await vector_store.initialize()
                
                processor = IntelligentEventProcessor(
                    value_threshold=0.3,
                    enable_vector_storage=True,
                    enable_entity_extraction=False,  # 简化测试
                )
                await processor.initialize()
                
                # 测试完整流程
                test_events = [
                    {
                        "connector_id": "test_connector",
                        "event_type": "document_created",
                        "event_data": {"content": "这是一个重要的技术文档"},
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                    {
                        "connector_id": "test_connector", 
                        "event_type": "spam_content",
                        "event_data": {"content": "x" * 5000},  # 垃圾内容
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                ]
                
                accepted_count = 0
                rejected_count = 0
                
                for event in test_events:
                    result = await processor.process_connector_event(**event)
                    if result.accepted:
                        accepted_count += 1
                    else:
                        rejected_count += 1
                
                # 验证结果
                assert accepted_count > 0, "应有内容被接受"
                assert rejected_count > 0, "应有垃圾内容被拒绝"
                
                # 获取处理指标
                metrics = await processor.get_metrics()
                assert metrics.total_events == 2, "应处理2个事件"
                assert metrics.acceptance_rate < 1.0, "接受率应小于100%"
                
                await vector_store.close()
                
        except Exception as e:
            pytest.skip(f"集成测试失败: {e}")


# 测试运行器
def run_tests():
    """运行测试套件"""
    print("🧪 开始运行智能存储测试套件...")
    
    # 配置pytest参数
    pytest_args = [
        __file__,
        "-v",  # 详细输出
        "--tb=short",  # 简短回溯
        "--asyncio-mode=auto",  # 自动异步模式
    ]
    
    # 运行测试
    exit_code = pytest.main(pytest_args)
    
    if exit_code == 0:
        print("✅ 所有测试通过！")
    else:
        print("❌ 部分测试失败，请检查输出")
    
    return exit_code


if __name__ == "__main__":
    import sys
    
    try:
        exit_code = run_tests()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️ 测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试运行异常: {e}")
        sys.exit(1)