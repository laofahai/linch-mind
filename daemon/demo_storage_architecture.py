#!/usr/bin/env python3
"""
三层存储架构演示脚本
展示SQLite + NetworkX + FAISS的协同工作
"""

import asyncio
import logging
import sys
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from services.storage.data_migration import get_migration_service
from services.storage.storage_orchestrator import get_storage_orchestrator

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def demo_basic_operations():
    """演示基础操作"""
    logger.info("🚀 开始三层存储架构演示")

    try:
        # 获取存储编排器
        storage = await get_storage_orchestrator()

        logger.info("📊 获取系统指标...")
        metrics = await storage.get_metrics()
        logger.info(f"系统状态: {metrics.health_status}")
        logger.info(f"总实体数: {metrics.total_entities}")
        logger.info(f"总关系数: {metrics.total_relationships}")
        logger.info(f"总向量数: {metrics.total_vectors}")

        # 演示创建实体
        logger.info("📝 创建示例实体...")

        entities = [
            {
                "id": "demo_ai_001",
                "name": "人工智能概述",
                "type": "concept",
                "content": "人工智能(AI)是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。包括机器学习、深度学习、自然语言处理等技术。",
            },
            {
                "id": "demo_ml_001",
                "name": "机器学习基础",
                "type": "concept",
                "content": "机器学习是人工智能的核心子领域，通过算法使计算机能够从数据中自动学习和改进，而无需明确编程。主要包括监督学习、无监督学习和强化学习。",
            },
            {
                "id": "demo_dl_001",
                "name": "深度学习原理",
                "type": "concept",
                "content": "深度学习是机器学习的一个子集，使用多层神经网络来学习数据的复杂模式。在图像识别、自然语言处理等领域取得了突破性进展。",
            },
        ]

        for entity in entities:
            success = await storage.create_entity(
                entity_id=entity["id"],
                name=entity["name"],
                entity_type=entity["type"],
                content=entity["content"],
                auto_embed=True,
            )

            if success:
                logger.info(f"✅ 创建实体: {entity['name']}")
            else:
                logger.error(f"❌ 创建实体失败: {entity['name']}")

        # 演示创建关系
        logger.info("🔗 创建实体关系...")

        relationships = [
            ("demo_ai_001", "demo_ml_001", "includes", 0.9),
            ("demo_ml_001", "demo_dl_001", "includes", 0.8),
            ("demo_ai_001", "demo_dl_001", "includes", 0.7),
        ]

        for source, target, rel_type, strength in relationships:
            success = await storage.create_relationship(
                source_entity=source,
                target_entity=target,
                relationship_type=rel_type,
                strength=strength,
                confidence=0.9,
            )

            if success:
                logger.info(f"✅ 创建关系: {source} -> {target}")
            else:
                logger.error(f"❌ 创建关系失败: {source} -> {target}")

        # 演示语义搜索
        logger.info("🔍 演示语义搜索...")

        search_queries = ["什么是人工智能？", "机器学习算法", "神经网络深度学习"]

        for query in search_queries:
            logger.info(f"搜索查询: '{query}'")
            results = await storage.semantic_search(query=query, k=3)

            for i, result in enumerate(results, 1):
                logger.info(
                    f"  {i}. {result.metadata.get('entity_name', 'Unknown')} "
                    f"(相似度: {result.score:.3f})"
                )

        # 演示图搜索
        logger.info("📊 演示图结构搜索...")

        neighbors = await storage.graph_search(
            entity_id="demo_ai_001", max_depth=2, max_results=10
        )

        logger.info(f"AI实体的邻居节点 (2度内): {neighbors}")

        # 演示智能推荐
        logger.info("🎯 演示智能推荐...")

        recommendations = await storage.get_smart_recommendations(
            max_recommendations=5, algorithm="hybrid"
        )

        logger.info("推荐结果:")
        for i, rec in enumerate(recommendations, 1):
            logger.info(
                f"  {i}. {rec.entity_name} (分数: {rec.score:.3f}, "
                f"来源: {rec.source}, 原因: {rec.reason})"
            )

        # 最终系统指标
        logger.info("📈 更新后的系统指标...")
        final_metrics = await storage.get_metrics()
        logger.info(f"总实体数: {final_metrics.total_entities}")
        logger.info(f"总关系数: {final_metrics.total_relationships}")
        logger.info(f"总向量数: {final_metrics.total_vectors}")
        logger.info(f"存储使用量: {final_metrics.storage_usage_mb:.2f} MB")

        logger.info("✅ 三层存储架构演示完成！")

    except Exception as e:
        logger.error(f"❌ 演示过程出错: {e}")
        import traceback

        logger.error(traceback.format_exc())


async def demo_data_migration():
    """演示数据迁移功能"""
    logger.info("🔄 演示数据迁移功能...")

    try:
        migration_service = await get_migration_service()

        # 检查迁移状态
        logger.info("检查当前迁移状态...")
        status = await migration_service.check_migration_status()

        logger.info(
            f"SQLite实体数: {status.get('sqlite_stats', {}).get('entities', 0)}"
        )
        logger.info(f"图数据库节点数: {status.get('graph_stats', {}).get('nodes', 0)}")
        logger.info(
            f"向量数据库文档数: {status.get('vector_stats', {}).get('documents', 0)}"
        )
        logger.info(f"需要迁移: {status.get('needs_migration', False)}")

        if status.get("needs_migration", False):
            logger.info("执行数据迁移...")
            stats = await migration_service.migrate_all_data(
                force_rebuild=False, batch_size=50, auto_embed=True
            )

            logger.info("迁移结果:")
            logger.info(
                f"  实体: {stats.migrated_entities}/{stats.total_entities} "
                f"({stats.entity_success_rate:.1f}%)"
            )
            logger.info(
                f"  关系: {stats.migrated_relationships}/{stats.total_relationships} "
                f"({stats.relationship_success_rate:.1f}%)"
            )
            logger.info(f"  向量: {stats.migrated_embeddings}")
            logger.info(f"  耗时: {stats.duration_seconds:.2f} 秒")

    except Exception as e:
        logger.error(f"❌ 数据迁移演示失败: {e}")


async def main():
    """主演示函数"""
    logger.info("🎬 Linch Mind 三层存储架构演示开始")
    logger.info("架构: SQLite (关系型) + NetworkX (图数据库) + FAISS (向量数据库)")

    try:
        # 基础操作演示
        await demo_basic_operations()

        # 数据迁移演示
        await demo_data_migration()

        logger.info("🎉 演示完成！三层存储架构工作正常")

    except Exception as e:
        logger.error(f"❌ 演示失败: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
