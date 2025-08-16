#!/usr/bin/env python3
"""
存储架构迁移脚本
清理现有垃圾数据并迁移到新的智能存储架构
"""

import asyncio
import json
import logging
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.service_facade import get_service
from config.intelligent_storage import get_intelligent_storage_config
from services.ai.ollama_service import get_ollama_service
from services.storage.faiss_vector_store import get_faiss_vector_store, VectorDocument
from services.storage.intelligent_event_processor import get_intelligent_event_processor
from services.unified_database_service import UnifiedDatabaseService
from models.database_models import EntityMetadata, ConnectorLog

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class MigrationStats:
    """迁移统计信息"""
    total_entities: int = 0
    garbage_entities: int = 0
    valuable_entities: int = 0
    migrated_entities: int = 0
    failed_migrations: int = 0
    storage_before_mb: float = 0.0
    storage_after_mb: float = 0.0
    processing_time_seconds: float = 0.0


class StorageMigration:
    """存储架构迁移器"""
    
    def __init__(self):
        self.config = get_intelligent_storage_config()
        self.stats = MigrationStats()
        
        # 服务依赖
        self._db_service = None
        self._ollama_service = None
        self._vector_store = None
        self._intelligent_processor = None
        
        # 垃圾数据识别规则
        self.garbage_patterns = [
            # 10KB+剪贴板日志
            lambda props: (
                props.get("event_type") == "clipboard_changed" and
                len(str(props.get("event_data", ""))) > 10000
            ),
            # 重复的临时文件事件
            lambda props: (
                "temp" in str(props.get("event_data", "")).lower() or
                "tmp" in str(props.get("event_data", "")).lower()
            ),
            # 空内容事件
            lambda props: (
                not props.get("event_data") or
                str(props.get("event_data", "")).strip() == ""
            ),
            # 系统日志噪音
            lambda props: (
                props.get("event_type") in ["system_log", "debug_log"] and
                len(str(props.get("event_data", ""))) > 5000
            ),
            # 无意义的重复数据
            lambda props: (
                str(props.get("event_data", "")).count("\\n") > 100 or
                str(props.get("event_data", "")).count(" ") > 2000
            ),
        ]

    async def initialize(self) -> bool:
        """初始化迁移器"""
        try:
            self._db_service = get_service(UnifiedDatabaseService)
            self._ollama_service = await get_ollama_service()
            self._vector_store = await get_faiss_vector_store()
            self._intelligent_processor = await get_intelligent_event_processor()
            
            logger.info("迁移器初始化完成")
            return True
            
        except Exception as e:
            logger.error(f"迁移器初始化失败: {e}")
            return False

    async def run_complete_migration(self, dry_run: bool = False) -> MigrationStats:
        """执行完整的存储迁移"""
        start_time = datetime.utcnow()
        
        try:
            logger.info("🚀 开始存储架构迁移...")
            
            # 1. 分析现有数据
            await self._analyze_existing_data()
            
            # 2. 识别和备份垃圾数据
            garbage_entities = await self._identify_garbage_data()
            
            if not dry_run:
                # 3. 备份垃圾数据
                await self._backup_garbage_data(garbage_entities)
                
                # 4. 清理垃圾数据
                await self._cleanup_garbage_data(garbage_entities)
            
            # 5. 迁移有价值数据
            valuable_entities = await self._identify_valuable_data()
            
            if not dry_run:
                await self._migrate_valuable_data(valuable_entities)
            
            # 6. 验证迁移结果
            await self._verify_migration()
            
            # 7. 生成迁移报告
            await self._generate_migration_report(dry_run)
            
            self.stats.processing_time_seconds = (datetime.utcnow() - start_time).total_seconds()
            
            if dry_run:
                logger.info("✅ 迁移分析完成（试运行模式）")
            else:
                logger.info("✅ 存储架构迁移完成")
            
            return self.stats
            
        except Exception as e:
            logger.error(f"存储迁移失败: {e}")
            raise

    # === 数据分析 ===

    async def _analyze_existing_data(self):
        """分析现有数据"""
        logger.info("🔍 分析现有数据...")
        
        with self._db_service.get_session() as session:
            # 统计总实体数
            total_entities = session.query(EntityMetadata).count()
            self.stats.total_entities = total_entities
            
            # 统计连接器事件
            connector_events = session.query(EntityMetadata).filter(
                EntityMetadata.type == "connector_event"
            ).count()
            
            # 统计智能事件
            intelligent_events = session.query(EntityMetadata).filter(
                EntityMetadata.type == "intelligent_event"
            ).count()
            
            logger.info(f"数据概览:")
            logger.info(f"  总实体数: {total_entities}")
            logger.info(f"  连接器事件: {connector_events}")
            logger.info(f"  智能事件: {intelligent_events}")

    async def _identify_garbage_data(self) -> List[EntityMetadata]:
        """识别垃圾数据"""
        logger.info("🗑️  识别垃圾数据...")
        
        garbage_entities = []
        
        with self._db_service.get_session() as session:
            # 获取所有连接器事件
            entities = session.query(EntityMetadata).filter(
                EntityMetadata.type == "connector_event"
            ).all()
            
            for entity in entities:
                properties = entity.properties or {}
                
                # 应用垃圾识别规则
                is_garbage = False
                for pattern in self.garbage_patterns:
                    try:
                        if pattern(properties):
                            is_garbage = True
                            break
                    except Exception as e:
                        logger.debug(f"垃圾识别规则异常: {e}")
                
                if is_garbage:
                    garbage_entities.append(entity)
        
        self.stats.garbage_entities = len(garbage_entities)
        logger.info(f"识别到垃圾数据: {len(garbage_entities)} 条")
        
        return garbage_entities

    async def _identify_valuable_data(self) -> List[EntityMetadata]:
        """识别有价值数据"""
        logger.info("💎 识别有价值数据...")
        
        valuable_entities = []
        
        with self._db_service.get_session() as session:
            # 获取所有连接器事件
            entities = session.query(EntityMetadata).filter(
                EntityMetadata.type == "connector_event"
            ).all()
            
            for entity in entities:
                properties = entity.properties or {}
                
                # 跳过垃圾数据
                is_garbage = False
                for pattern in self.garbage_patterns:
                    try:
                        if pattern(properties):
                            is_garbage = True
                            break
                    except Exception:
                        pass
                
                if not is_garbage:
                    # 检查是否有有价值的内容
                    event_data = properties.get("event_data", {})
                    content = self._extract_content_from_event_data(event_data)
                    
                    if content and len(content.strip()) > 10:  # 至少10个字符
                        valuable_entities.append(entity)
        
        self.stats.valuable_entities = len(valuable_entities)
        logger.info(f"识别到有价值数据: {len(valuable_entities)} 条")
        
        return valuable_entities

    # === 数据清理 ===

    async def _backup_garbage_data(self, garbage_entities: List[EntityMetadata]):
        """备份垃圾数据"""
        logger.info("💾 备份垃圾数据...")
        
        backup_dir = self.config.storage_dir / "backups" / "migration"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        backup_file = backup_dir / f"garbage_data_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        
        backup_data = []
        for entity in garbage_entities:
            backup_data.append({
                "entity_id": entity.entity_id,
                "name": entity.name,
                "type": entity.type,
                "description": entity.description,
                "properties": entity.properties,
                "created_at": entity.created_at.isoformat() if entity.created_at else None,
                "updated_at": entity.updated_at.isoformat() if entity.updated_at else None,
            })
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"垃圾数据已备份到: {backup_file}")

    async def _cleanup_garbage_data(self, garbage_entities: List[EntityMetadata]):
        """清理垃圾数据"""
        logger.info("🧹 清理垃圾数据...")
        
        cleaned_count = 0
        batch_size = 100
        
        # 分批删除
        for i in range(0, len(garbage_entities), batch_size):
            batch = garbage_entities[i:i + batch_size]
            
            with self._db_service.get_session() as session:
                for entity in batch:
                    try:
                        # 删除相关连接器日志
                        session.query(ConnectorLog).filter(
                            ConnectorLog.details.contains(entity.entity_id)
                        ).delete(synchronize_session=False)
                        
                        # 删除实体
                        session.delete(entity)
                        cleaned_count += 1
                        
                    except Exception as e:
                        logger.error(f"删除实体失败 [{entity.entity_id}]: {e}")
                
                session.commit()
            
            logger.debug(f"已清理 {cleaned_count}/{len(garbage_entities)} 条垃圾数据")
        
        logger.info(f"✅ 垃圾数据清理完成: {cleaned_count} 条")

    # === 数据迁移 ===

    async def _migrate_valuable_data(self, valuable_entities: List[EntityMetadata]):
        """迁移有价值数据到智能存储"""
        logger.info("🚀 迁移有价值数据到智能存储...")
        
        migrated_count = 0
        failed_count = 0
        batch_size = 50
        
        # 分批处理
        for i in range(0, len(valuable_entities), batch_size):
            batch = valuable_entities[i:i + batch_size]
            
            for entity in batch:
                try:
                    # 提取事件信息
                    properties = entity.properties or {}
                    connector_id = properties.get("connector_id", "unknown")
                    event_type = properties.get("event_type", "unknown")
                    event_data = properties.get("event_data", {})
                    timestamp = properties.get("timestamp", datetime.utcnow().isoformat())
                    metadata = properties.get("metadata", {})
                    
                    # 使用智能处理器重新处理
                    result = await self._intelligent_processor.process_connector_event(
                        connector_id=connector_id,
                        event_type=event_type,
                        event_data=event_data,
                        timestamp=timestamp,
                        metadata=metadata,
                    )
                    
                    if result.accepted:
                        migrated_count += 1
                        logger.debug(f"迁移成功: {entity.entity_id}, 价值={result.value_score:.3f}")
                        
                        # 删除原有记录
                        with self._db_service.get_session() as session:
                            session.delete(entity)
                            session.commit()
                    else:
                        failed_count += 1
                        logger.debug(f"迁移拒绝: {entity.entity_id}, 原因={result.reasoning}")
                        
                except Exception as e:
                    failed_count += 1
                    logger.error(f"迁移失败 [{entity.entity_id}]: {e}")
            
            logger.info(f"迁移进度: {migrated_count + failed_count}/{len(valuable_entities)}")
        
        self.stats.migrated_entities = migrated_count
        self.stats.failed_migrations = failed_count
        
        logger.info(f"✅ 数据迁移完成 - 成功: {migrated_count}, 失败: {failed_count}")

    # === 验证和报告 ===

    async def _verify_migration(self):
        """验证迁移结果"""
        logger.info("🔍 验证迁移结果...")
        
        with self._db_service.get_session() as session:
            # 检查剩余的连接器事件
            remaining_events = session.query(EntityMetadata).filter(
                EntityMetadata.type == "connector_event"
            ).count()
            
            # 检查新的智能事件
            intelligent_events = session.query(EntityMetadata).filter(
                EntityMetadata.type == "intelligent_event"
            ).count()
            
            logger.info(f"迁移验证结果:")
            logger.info(f"  剩余连接器事件: {remaining_events}")
            logger.info(f"  新智能事件: {intelligent_events}")
            
            if remaining_events > 0:
                logger.warning(f"仍有 {remaining_events} 个连接器事件未处理")

    async def _generate_migration_report(self, dry_run: bool = False):
        """生成迁移报告"""
        logger.info("📊 生成迁移报告...")
        
        report = {
            "migration_summary": {
                "execution_mode": "dry_run" if dry_run else "full_migration",
                "start_time": datetime.utcnow().isoformat(),
                "processing_time_seconds": self.stats.processing_time_seconds,
            },
            "data_analysis": {
                "total_entities": self.stats.total_entities,
                "garbage_entities": self.stats.garbage_entities,
                "valuable_entities": self.stats.valuable_entities,
                "garbage_percentage": (self.stats.garbage_entities / self.stats.total_entities * 100) if self.stats.total_entities > 0 else 0,
            },
            "migration_results": {
                "migrated_entities": self.stats.migrated_entities,
                "failed_migrations": self.stats.failed_migrations,
                "migration_success_rate": (self.stats.migrated_entities / self.stats.valuable_entities * 100) if self.stats.valuable_entities > 0 else 0,
            },
            "storage_optimization": {
                "estimated_storage_reduction_mb": self.stats.storage_before_mb - self.stats.storage_after_mb,
                "compression_ratio": self.stats.storage_before_mb / self.stats.storage_after_mb if self.stats.storage_after_mb > 0 else 0,
            },
            "recommendations": self._generate_recommendations(),
        }
        
        # 保存报告
        report_dir = self.config.storage_dir / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        
        mode_suffix = "dry_run" if dry_run else "migration"
        report_file = report_dir / f"storage_{mode_suffix}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # 打印关键指标
        logger.info("📊 迁移报告:")
        logger.info(f"  总实体数: {self.stats.total_entities}")
        logger.info(f"  垃圾数据: {self.stats.garbage_entities} ({report['data_analysis']['garbage_percentage']:.1f}%)")
        logger.info(f"  有价值数据: {self.stats.valuable_entities}")
        logger.info(f"  成功迁移: {self.stats.migrated_entities}")
        logger.info(f"  迁移成功率: {report['migration_results']['migration_success_rate']:.1f}%")
        
        logger.info(f"📄 详细报告已保存到: {report_file}")

    def _generate_recommendations(self) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        # 垃圾数据比例过高
        if self.stats.total_entities > 0:
            garbage_rate = self.stats.garbage_entities / self.stats.total_entities
            if garbage_rate > 0.3:
                recommendations.append("垃圾数据比例过高，建议调整连接器配置以减少无用数据采集")
        
        # 迁移失败率过高
        if self.stats.valuable_entities > 0:
            failure_rate = self.stats.failed_migrations / self.stats.valuable_entities
            if failure_rate > 0.1:
                recommendations.append("迁移失败率较高，建议检查AI模型配置和网络连接")
        
        # 数据量建议
        if self.stats.total_entities < 100:
            recommendations.append("数据量较少，建议运行一段时间后再次迁移以获得更好的AI评估效果")
        
        # 性能建议
        if self.stats.processing_time_seconds > 300:  # 5分钟
            recommendations.append("迁移耗时较长，建议在系统空闲时段执行或调整批处理大小")
        
        if not recommendations:
            recommendations.append("迁移过程正常，建议定期执行数据清理维护")
        
        return recommendations

    # === 工具方法 ===

    def _extract_content_from_event_data(self, event_data: Any) -> Optional[str]:
        """从事件数据中提取内容"""
        if isinstance(event_data, dict):
            content_fields = ["content", "text", "data", "message", "body", "value"]
            for field in content_fields:
                if field in event_data:
                    content = event_data[field]
                    if isinstance(content, str) and content.strip():
                        return content.strip()
        elif isinstance(event_data, str):
            return event_data.strip()
        
        return None

    # === 公共接口 ===

    async def analyze_only(self) -> Dict[str, Any]:
        """仅分析数据，不执行迁移"""
        await self._analyze_existing_data()
        garbage_entities = await self._identify_garbage_data()
        valuable_entities = await self._identify_valuable_data()
        
        return {
            "total_entities": self.stats.total_entities,
            "garbage_entities": self.stats.garbage_entities,
            "valuable_entities": self.stats.valuable_entities,
            "garbage_samples": [
                {
                    "entity_id": entity.entity_id,
                    "name": entity.name,
                    "size_kb": len(str(entity.properties)) / 1024,
                }
                for entity in garbage_entities[:5]  # 显示前5个样本
            ],
            "valuable_samples": [
                {
                    "entity_id": entity.entity_id,
                    "name": entity.name,
                    "event_type": entity.properties.get("event_type", "unknown"),
                }
                for entity in valuable_entities[:5]  # 显示前5个样本
            ],
        }


async def main():
    """主函数"""
    print("🚀 Linch Mind 存储架构迁移工具")
    print("=" * 50)
    
    migration = StorageMigration()
    
    if not await migration.initialize():
        print("❌ 迁移工具初始化失败")
        return 1
    
    # 命令行参数处理
    mode = "interactive"
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ("analyze", "dry-run", "migrate"):
            mode = arg
    
    try:
        if mode == "analyze":
            # 仅分析模式
            print("🔍 分析现有数据...")
            analysis = await migration.analyze_only()
            
            print("\n📊 数据分析结果:")
            print(f"  总实体数: {analysis['total_entities']}")
            print(f"  垃圾数据: {analysis['garbage_entities']}")
            print(f"  有价值数据: {analysis['valuable_entities']}")
            print(f"  垃圾比例: {analysis['garbage_entities']/analysis['total_entities']*100:.1f}%")
            
            if analysis['garbage_samples']:
                print("\n🗑️  垃圾数据样本:")
                for sample in analysis['garbage_samples']:
                    print(f"    - {sample['entity_id']}: {sample['size_kb']:.1f}KB")
            
        elif mode == "dry-run":
            # 试运行模式
            print("🧪 执行迁移试运行...")
            stats = await migration.run_complete_migration(dry_run=True)
            print(f"\n✅ 试运行完成，处理时间: {stats.processing_time_seconds:.1f}秒")
            
        elif mode == "migrate":
            # 完整迁移模式
            print("⚠️  即将执行完整迁移，这将删除垃圾数据！")
            confirm = input("确认继续? (yes/no): ")
            if confirm.lower() == "yes":
                print("🚀 执行完整迁移...")
                stats = await migration.run_complete_migration(dry_run=False)
                print(f"\n✅ 迁移完成，处理时间: {stats.processing_time_seconds:.1f}秒")
            else:
                print("取消迁移")
                return 0
                
        else:
            # 交互模式
            print("请选择操作模式:")
            print("1. 分析数据 (analyze)")
            print("2. 试运行 (dry-run)")
            print("3. 完整迁移 (migrate)")
            
            choice = input("输入选择 (1-3): ").strip()
            
            if choice == "1":
                analysis = await migration.analyze_only()
                print(f"\n📊 分析完成 - 垃圾数据: {analysis['garbage_entities']}, 有价值数据: {analysis['valuable_entities']}")
            elif choice == "2":
                stats = await migration.run_complete_migration(dry_run=True)
                print(f"\n✅ 试运行完成")
            elif choice == "3":
                confirm = input("⚠️  确认执行完整迁移? (yes/no): ")
                if confirm.lower() == "yes":
                    stats = await migration.run_complete_migration(dry_run=False)
                    print(f"\n✅ 迁移完成")
                else:
                    print("取消迁移")
            else:
                print("无效选择")
                return 1
        
        return 0
        
    except Exception as e:
        print(f"\n❌ 迁移过程中出现错误: {e}")
        logger.exception("迁移异常详情")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断迁移")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 程序异常: {e}")
        sys.exit(1)