#!/usr/bin/env python3
"""
数据归档器
专门负责数据归档相关功能
从data_lifecycle_manager.py中拆分出来
"""

import asyncio
import json
import logging
import shutil
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

from core.service_facade import get_database_service
from models.database_models import (
    AIConversation,
    EntityMetadata,
    EntityRelationship,
    UserBehavior,
)

logger = logging.getLogger(__name__)


class DataArchiver:
    """数据归档器"""

    def __init__(self, config):
        self.config = config
        self.db_service = None
        self.archive_base_path = Path("data/archives")

    async def initialize(self):
        """初始化归档器"""
        try:
            self.db_service = get_database_service()
            
            # 确保归档目录存在
            self.archive_base_path.mkdir(parents=True, exist_ok=True)
            
            logger.info("数据归档器初始化完成")
            return True
        except Exception as e:
            logger.error(f"数据归档器初始化失败: {e}")
            return False

    async def archive_old_data(self) -> Dict[str, int]:
        """归档旧数据"""
        if not self.config.archive_enabled:
            logger.debug("数据归档功能未启用")
            return {}

        archive_stats = {
            "entities": 0,
            "relationships": 0,
            "behaviors": 0,
            "conversations": 0,
        }

        try:
            logger.info("开始归档旧数据...")

            # 创建归档批次目录
            archive_batch = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            batch_path = self.archive_base_path / f"batch_{archive_batch}"
            batch_path.mkdir(exist_ok=True)

            # 1. 归档行为数据
            if self.config.behavior_retention_days > 0:
                archive_stats["behaviors"] = await self._archive_behaviors(batch_path)

            # 2. 归档对话数据
            if self.config.conversation_retention_days > 0:
                archive_stats["conversations"] = await self._archive_conversations(batch_path)

            # 3. 归档实体和关系数据
            archive_stats["entities"] = await self._archive_entities(batch_path)
            archive_stats["relationships"] = await self._archive_relationships(batch_path)

            # 4. 如果启用压缩，压缩归档文件
            if self.config.compressed_archive:
                await self._compress_archive_batch(batch_path)

            # 5. 创建归档元数据
            await self._create_archive_metadata(batch_path, archive_stats)

            logger.info(f"数据归档完成: {archive_stats}")
            return archive_stats

        except Exception as e:
            logger.error(f"归档旧数据失败: {e}")
            return archive_stats

    async def _archive_behaviors(self, batch_path: Path) -> int:
        """归档行为数据"""
        try:
            if not self.db_service:
                return 0

            archive_date = datetime.utcnow() - timedelta(
                days=self.config.archive_threshold_days
            )

            with self.db_service.get_session() as session:
                behaviors_to_archive = (
                    session.query(UserBehavior)
                    .filter(UserBehavior.created_at < archive_date)
                    .all()
                )

                if not behaviors_to_archive:
                    return 0

                # 导出到JSON文件
                behaviors_data = []
                for behavior in behaviors_to_archive:
                    behaviors_data.append({
                        "id": behavior.id,
                        "user_id": behavior.user_id,
                        "action_type": behavior.action_type,
                        "target_type": behavior.target_type,
                        "target_id": behavior.target_id,
                        "metadata": behavior.metadata,
                        "created_at": behavior.created_at.isoformat() if behavior.created_at else None,
                    })

                archive_file = batch_path / "behaviors.json"
                with open(archive_file, 'w', encoding='utf-8') as f:
                    json.dump(behaviors_data, f, indent=2, ensure_ascii=False)

                # 从数据库中删除已归档的数据
                count = len(behaviors_to_archive)
                for behavior in behaviors_to_archive:
                    session.delete(behavior)

                session.commit()

                logger.info(f"归档行为数据: {count} 条 -> {archive_file}")
                return count

        except Exception as e:
            logger.error(f"归档行为数据失败: {e}")
            return 0

    async def _archive_conversations(self, batch_path: Path) -> int:
        """归档对话数据"""
        try:
            if not self.db_service:
                return 0

            archive_date = datetime.utcnow() - timedelta(
                days=self.config.archive_threshold_days
            )

            with self.db_service.get_session() as session:
                conversations_to_archive = (
                    session.query(AIConversation)
                    .filter(AIConversation.created_at < archive_date)
                    .all()
                )

                if not conversations_to_archive:
                    return 0

                conversations_data = []
                for conversation in conversations_to_archive:
                    conversations_data.append({
                        "id": conversation.id,
                        "user_id": conversation.user_id,
                        "conversation_type": conversation.conversation_type,
                        "messages": conversation.messages,
                        "metadata": conversation.metadata,
                        "created_at": conversation.created_at.isoformat() if conversation.created_at else None,
                        "updated_at": conversation.updated_at.isoformat() if conversation.updated_at else None,
                    })

                archive_file = batch_path / "conversations.json"
                with open(archive_file, 'w', encoding='utf-8') as f:
                    json.dump(conversations_data, f, indent=2, ensure_ascii=False)

                count = len(conversations_to_archive)
                for conversation in conversations_to_archive:
                    session.delete(conversation)

                session.commit()

                logger.info(f"归档对话数据: {count} 条 -> {archive_file}")
                return count

        except Exception as e:
            logger.error(f"归档对话数据失败: {e}")
            return 0

    async def _archive_entities(self, batch_path: Path) -> int:
        """归档实体数据"""
        try:
            if not self.db_service:
                return 0

            archive_date = datetime.utcnow() - timedelta(
                days=self.config.archive_threshold_days
            )

            with self.db_service.get_session() as session:
                entities_to_archive = (
                    session.query(EntityMetadata)
                    .filter(EntityMetadata.created_at < archive_date)
                    .all()
                )

                if not entities_to_archive:
                    return 0

                entities_data = []
                for entity in entities_to_archive:
                    entities_data.append({
                        "id": entity.id,
                        "entity_type": entity.entity_type,
                        "entity_id": entity.entity_id,
                        "display_name": entity.display_name,
                        "description": entity.description,
                        "metadata": entity.metadata,
                        "created_at": entity.created_at.isoformat() if entity.created_at else None,
                        "updated_at": entity.updated_at.isoformat() if entity.updated_at else None,
                    })

                archive_file = batch_path / "entities.json"
                with open(archive_file, 'w', encoding='utf-8') as f:
                    json.dump(entities_data, f, indent=2, ensure_ascii=False)

                count = len(entities_to_archive)
                for entity in entities_to_archive:
                    session.delete(entity)

                session.commit()

                logger.info(f"归档实体数据: {count} 条 -> {archive_file}")
                return count

        except Exception as e:
            logger.error(f"归档实体数据失败: {e}")
            return 0

    async def _archive_relationships(self, batch_path: Path) -> int:
        """归档关系数据"""
        try:
            if not self.db_service:
                return 0

            archive_date = datetime.utcnow() - timedelta(
                days=self.config.archive_threshold_days
            )

            with self.db_service.get_session() as session:
                relationships_to_archive = (
                    session.query(EntityRelationship)
                    .filter(EntityRelationship.created_at < archive_date)
                    .all()
                )

                if not relationships_to_archive:
                    return 0

                relationships_data = []
                for relationship in relationships_to_archive:
                    relationships_data.append({
                        "id": relationship.id,
                        "source_entity_id": relationship.source_entity_id,
                        "target_entity_id": relationship.target_entity_id,
                        "relationship_type": relationship.relationship_type,
                        "strength": relationship.strength,
                        "metadata": relationship.metadata,
                        "created_at": relationship.created_at.isoformat() if relationship.created_at else None,
                        "updated_at": relationship.updated_at.isoformat() if relationship.updated_at else None,
                    })

                archive_file = batch_path / "relationships.json"
                with open(archive_file, 'w', encoding='utf-8') as f:
                    json.dump(relationships_data, f, indent=2, ensure_ascii=False)

                count = len(relationships_to_archive)
                for relationship in relationships_to_archive:
                    session.delete(relationship)

                session.commit()

                logger.info(f"归档关系数据: {count} 条 -> {archive_file}")
                return count

        except Exception as e:
            logger.error(f"归档关系数据失败: {e}")
            return 0

    async def _compress_archive_batch(self, batch_path: Path):
        """压缩归档批次"""
        try:
            import tarfile

            archive_name = f"{batch_path.name}.tar.gz"
            archive_file = batch_path.parent / archive_name

            with tarfile.open(archive_file, "w:gz") as tar:
                tar.add(batch_path, arcname=batch_path.name)

            # 删除原始目录
            shutil.rmtree(batch_path)

            logger.info(f"归档批次已压缩: {archive_file}")

        except Exception as e:
            logger.error(f"压缩归档批次失败: {e}")

    async def _create_archive_metadata(self, batch_path: Path, stats: Dict[str, int]):
        """创建归档元数据"""
        try:
            metadata = {
                "batch_id": batch_path.name,
                "created_at": datetime.utcnow().isoformat(),
                "archive_threshold_days": self.config.archive_threshold_days,
                "compressed": self.config.compressed_archive,
                "statistics": stats,
                "total_archived": sum(stats.values()),
            }

            metadata_file = batch_path / "metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            logger.debug(f"归档元数据已创建: {metadata_file}")

        except Exception as e:
            logger.error(f"创建归档元数据失败: {e}")

    async def list_archives(self) -> List[Dict]:
        """列出所有归档"""
        try:
            archives = []
            
            for archive_path in self.archive_base_path.iterdir():
                if archive_path.is_dir():
                    # 目录形式的归档
                    metadata_file = archive_path / "metadata.json"
                    if metadata_file.exists():
                        with open(metadata_file, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                        archives.append({
                            "type": "directory",
                            "path": str(archive_path),
                            "size_mb": self._get_directory_size_mb(archive_path),
                            **metadata
                        })
                elif archive_path.suffix == ".gz":
                    # 压缩归档
                    archives.append({
                        "type": "compressed",
                        "path": str(archive_path),
                        "size_mb": archive_path.stat().st_size / (1024 * 1024),
                        "created_at": datetime.fromtimestamp(archive_path.stat().st_mtime).isoformat(),
                    })

            # 按创建时间排序
            archives.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            
            return archives

        except Exception as e:
            logger.error(f"列出归档失败: {e}")
            return []

    def _get_directory_size_mb(self, directory: Path) -> float:
        """获取目录大小(MB)"""
        try:
            total_size = 0
            for file_path in directory.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
            return total_size / (1024 * 1024)
        except Exception:
            return 0.0

    async def restore_archive(self, archive_id: str) -> bool:
        """恢复归档数据"""
        try:
            # TODO: 实现归档恢复功能
            logger.warning(f"归档恢复功能暂未实现: {archive_id}")
            return False

        except Exception as e:
            logger.error(f"恢复归档失败 {archive_id}: {e}")
            return False

    async def delete_archive(self, archive_id: str) -> bool:
        """删除归档"""
        try:
            archive_path = self.archive_base_path / archive_id
            
            if archive_path.exists():
                if archive_path.is_dir():
                    shutil.rmtree(archive_path)
                else:
                    archive_path.unlink()
                
                logger.info(f"归档已删除: {archive_path}")
                return True
            else:
                logger.warning(f"归档不存在: {archive_path}")
                return False

        except Exception as e:
            logger.error(f"删除归档失败 {archive_id}: {e}")
            return False