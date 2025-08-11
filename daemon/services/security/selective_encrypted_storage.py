#!/usr/bin/env python3
"""
选择性加密存储 - 基于数据敏感度的智能加密存储
针对NetworkX图数据实施分层安全保护
"""

import logging
import pickle
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import networkx as nx

try:
    from .field_encryption import get_encryption_manager
except ImportError:
    from field_encryption import get_encryption_manager

logger = logging.getLogger(__name__)


class SelectiveEncryptedStorage:
    """
    选择性加密存储 - 基于数据敏感度分级保护

    设计理念:
    1. 高敏感度数据 -> 加密存储
    2. 低敏感度数据 -> 明文存储 (性能优化 + 调试友好)
    3. 动态敏感度判断 -> 基于节点数量、边类型、用户交互频率
    """

    def __init__(self):
        """初始化选择性加密存储"""
        self.encryption_manager = get_encryption_manager()
        self.sensitive_edge_types = {
            "personal_contact",  # 个人联系人
            "private_message",  # 私人消息
            "location",  # 位置信息
            "financial",  # 财务相关
            "medical",  # 医疗信息
            "password",  # 密码相关
            "credential",  # 凭据信息
            "personal_document",  # 个人文档
            "browsing_history",  # 浏览历史
            "search_query",  # 搜索查询
            "user_behavior",  # 用户行为
            "social_connection",  # 社交连接
        }

        self.sensitive_node_types = {
            "person",  # 人员信息
            "contact",  # 联系人
            "account",  # 账户信息
            "credential",  # 凭据
            # 'document' 移除 - 普通文档不应被视为敏感
            "personal_document",  # 个人文档 (特指)
            "location",  # 位置
            "transaction",  # 交易
            "conversation",  # 对话
        }

        # 敏感度阈值配置
        self.sensitivity_thresholds = {
            "large_graph_node_count": 100,  # 大型图节点数阈值
            "high_connectivity_degree": 10,  # 高连接度阈值
            "sensitive_ratio_threshold": 0.3,  # 敏感边比例阈值
        }

    def save_graph_data(self, graph_data: nx.MultiDiGraph, filepath: Path) -> bool:
        """
        保存图数据 - 基于敏感度智能选择加密策略

        Args:
            graph_data: NetworkX图数据
            filepath: 存储文件路径

        Returns:
            bool: 保存是否成功
        """
        try:
            # 分析数据敏感度
            sensitivity_analysis = self._analyze_graph_sensitivity(graph_data)

            logger.info(f"图数据敏感度分析: {sensitivity_analysis}")

            if sensitivity_analysis["is_sensitive"]:
                # 高敏感度: 加密存储
                return self._save_encrypted(graph_data, filepath, sensitivity_analysis)
            else:
                # 低敏感度: 明文存储 (性能优先)
                return self._save_plaintext(graph_data, filepath, sensitivity_analysis)

        except Exception as e:
            logger.error(f"保存图数据失败: {e}")
            return False

    def load_graph_data(self, filepath: Path) -> Optional[nx.MultiDiGraph]:
        """
        加载图数据 - 自动检测加密状态并解密

        Args:
            filepath: 数据文件路径

        Returns:
            nx.MultiDiGraph: 加载的图数据，失败返回None
        """
        try:
            # 检查加密文件
            encrypted_file = filepath.with_suffix(".enc")
            if encrypted_file.exists():
                logger.info(f"检测到加密图数据，正在解密: {encrypted_file}")
                return self._load_encrypted(encrypted_file)

            # 检查明文文件
            if filepath.exists():
                logger.info(f"加载明文图数据: {filepath}")
                return self._load_plaintext(filepath)

            logger.warning(f"图数据文件不存在: {filepath}")
            return None

        except Exception as e:
            logger.error(f"加载图数据失败: {e}")
            return None

    def _analyze_graph_sensitivity(self, graph_data: nx.MultiDiGraph) -> Dict[str, Any]:
        """
        分析图数据敏感度

        Args:
            graph_data: NetworkX图数据

        Returns:
            Dict: 敏感度分析结果
        """
        analysis = {
            "node_count": graph_data.number_of_nodes(),
            "edge_count": graph_data.number_of_edges(),
            "sensitive_nodes": 0,
            "sensitive_edges": 0,
            "high_degree_nodes": 0,
            "sensitive_node_types": set(),
            "sensitive_edge_types": set(),
            "is_sensitive": False,
            "sensitivity_reasons": [],
        }

        try:
            # 分析节点敏感度
            for node_id, node_data in graph_data.nodes(data=True):
                node_type = node_data.get("entity_type", "").lower()

                # 检查敏感节点类型
                if node_type in self.sensitive_node_types:
                    analysis["sensitive_nodes"] += 1
                    analysis["sensitive_node_types"].add(node_type)

                # 检查高连接度节点
                degree = graph_data.degree(node_id)
                if degree >= self.sensitivity_thresholds["high_connectivity_degree"]:
                    analysis["high_degree_nodes"] += 1

            # 分析边敏感度
            for source, target, edge_data in graph_data.edges(data=True):
                edge_type = edge_data.get("relationship_type", "").lower()

                if edge_type in self.sensitive_edge_types:
                    analysis["sensitive_edges"] += 1
                    analysis["sensitive_edge_types"].add(edge_type)

            # 敏感度判断逻辑
            reasons = []

            # 规则1: 大型图（节点数 > 100）
            if (
                analysis["node_count"]
                > self.sensitivity_thresholds["large_graph_node_count"]
            ):
                reasons.append(f"大型图数据 ({analysis['node_count']} 节点)")

            # 规则2: 包含敏感边类型
            if analysis["sensitive_edges"] > 0:
                sensitive_ratio = analysis["sensitive_edges"] / max(
                    analysis["edge_count"], 1
                )
                if (
                    sensitive_ratio
                    > self.sensitivity_thresholds["sensitive_ratio_threshold"]
                ):
                    reasons.append(f"高敏感边比例 ({sensitive_ratio:.2%})")
                elif analysis["sensitive_edges"] > 5:  # 绝对数量阈值
                    reasons.append(f"敏感边数量较多 ({analysis['sensitive_edges']} 条)")

            # 规则3: 包含敏感节点类型
            if analysis["sensitive_nodes"] > 0:
                sensitive_node_ratio = analysis["sensitive_nodes"] / max(
                    analysis["node_count"], 1
                )
                if sensitive_node_ratio > 0.2:  # 20%以上节点为敏感类型
                    reasons.append(f"高敏感节点比例 ({sensitive_node_ratio:.2%})")

            # 规则4: 高连接度节点较多（可能包含重要用户关系）
            if analysis["high_degree_nodes"] > 3:
                reasons.append(f"高连接度节点较多 ({analysis['high_degree_nodes']} 个)")

            analysis["sensitivity_reasons"] = reasons
            analysis["is_sensitive"] = len(reasons) > 0

            # 转换set为list便于序列化
            analysis["sensitive_node_types"] = list(analysis["sensitive_node_types"])
            analysis["sensitive_edge_types"] = list(analysis["sensitive_edge_types"])

            return analysis

        except Exception as e:
            logger.error(f"敏感度分析失败: {e}")
            # 失败时默认为敏感，采用安全优先策略
            analysis["is_sensitive"] = True
            analysis["sensitivity_reasons"] = ["分析失败，采用安全优先策略"]
            return analysis

    def _save_encrypted(
        self, graph_data: nx.MultiDiGraph, filepath: Path, analysis: Dict[str, Any]
    ) -> bool:
        """保存加密图数据"""
        try:
            # 序列化图数据
            graph_bytes = pickle.dumps(graph_data, protocol=pickle.HIGHEST_PROTOCOL)

            # 加密数据
            encrypted_data = self.encryption_manager._fernet.encrypt(graph_bytes)

            # 保存到加密文件
            encrypted_file = filepath.with_suffix(".enc")
            with open(encrypted_file, "wb") as f:
                f.write(encrypted_data)

            # 保存元数据
            metadata = {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "encryption_enabled": True,
                "sensitivity_analysis": analysis,
                "file_size_bytes": len(encrypted_data),
                "original_size_bytes": len(graph_bytes),
            }

            metadata_file = filepath.with_suffix(".metadata.json")
            import json

            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            # 删除可能存在的明文文件
            if filepath.exists():
                filepath.unlink()

            logger.info(
                f"图数据已加密保存: {encrypted_file} ({len(encrypted_data)} bytes)"
            )
            logger.info(f"敏感度原因: {', '.join(analysis['sensitivity_reasons'])}")
            return True

        except Exception as e:
            logger.error(f"加密保存失败: {e}")
            return False

    def _save_plaintext(
        self, graph_data: nx.MultiDiGraph, filepath: Path, analysis: Dict[str, Any]
    ) -> bool:
        """保存明文图数据"""
        try:
            # 序列化并保存
            with open(filepath, "wb") as f:
                pickle.dump(graph_data, f, protocol=pickle.HIGHEST_PROTOCOL)

            # 保存元数据
            metadata = {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "encryption_enabled": False,
                "sensitivity_analysis": analysis,
                "file_size_bytes": filepath.stat().st_size,
                "storage_reason": "低敏感度数据，明文存储以优化性能和调试体验",
            }

            metadata_file = filepath.with_suffix(".metadata.json")
            import json

            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            # 删除可能存在的加密文件
            encrypted_file = filepath.with_suffix(".enc")
            if encrypted_file.exists():
                encrypted_file.unlink()

            logger.info(f"图数据已明文保存: {filepath} (性能优化模式)")
            return True

        except Exception as e:
            logger.error(f"明文保存失败: {e}")
            return False

    def _load_encrypted(self, encrypted_file: Path) -> Optional[nx.MultiDiGraph]:
        """加载加密图数据"""
        try:
            # 读取加密数据
            with open(encrypted_file, "rb") as f:
                encrypted_data = f.read()

            # 解密数据
            decrypted_bytes = self.encryption_manager._fernet.decrypt(encrypted_data)

            # 反序列化图数据
            graph_data = pickle.loads(decrypted_bytes)

            logger.info(f"加密图数据解密成功: {encrypted_file}")
            return graph_data

        except Exception as e:
            logger.error(f"解密加载失败: {e}")
            return None

    def _load_plaintext(self, filepath: Path) -> Optional[nx.MultiDiGraph]:
        """加载明文图数据"""
        try:
            with open(filepath, "rb") as f:
                graph_data = pickle.load(f)

            logger.info(f"明文图数据加载成功: {filepath}")
            return graph_data

        except Exception as e:
            logger.error(f"明文加载失败: {e}")
            return None

    def get_storage_info(self, filepath: Path) -> Dict[str, Any]:
        """获取存储信息"""
        try:
            metadata_file = filepath.with_suffix(".metadata.json")
            if metadata_file.exists():
                import json

                with open(metadata_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            else:
                return {"encryption_enabled": None, "error": "metadata file not found"}

        except Exception as e:
            logger.error(f"获取存储信息失败: {e}")
            return {"error": str(e)}

    def migrate_existing_data(self, old_filepath: Path, new_filepath: Path) -> bool:
        """迁移现有数据到新的选择性加密存储格式"""
        try:
            # 加载现有数据
            if not old_filepath.exists():
                logger.warning(f"源数据文件不存在: {old_filepath}")
                return False

            logger.info(f"开始迁移图数据: {old_filepath} -> {new_filepath}")

            # 加载现有图数据
            with open(old_filepath, "rb") as f:
                graph_data = pickle.load(f)

            # 使用新的选择性加密存储格式保存
            success = self.save_graph_data(graph_data, new_filepath)

            if success:
                logger.info(f"图数据迁移完成: {new_filepath}")
                # 备份原文件（可选）
                backup_file = old_filepath.with_suffix(".backup")
                old_filepath.rename(backup_file)
                logger.info(f"原文件已备份: {backup_file}")

            return success

        except Exception as e:
            logger.error(f"数据迁移失败: {e}")
            return False


# 全局选择性加密存储实例
_selective_storage: Optional[SelectiveEncryptedStorage] = None


def get_selective_encrypted_storage() -> SelectiveEncryptedStorage:
    """获取全局选择性加密存储实例"""
    global _selective_storage
    if _selective_storage is None:
        _selective_storage = SelectiveEncryptedStorage()
    return _selective_storage


def test_selective_encryption():
    """测试选择性加密存储功能"""
    try:
        storage = get_selective_encrypted_storage()

        # 创建测试图数据
        test_graph = nx.MultiDiGraph()

        # 添加低敏感度测试数据
        test_graph.add_node("user1", entity_type="user", name="测试用户1")
        test_graph.add_node("doc1", entity_type="document", name="测试文档1")
        test_graph.add_edge("user1", "doc1", relationship_type="created")

        print("=== 低敏感度图数据测试 ===")
        test_file = Path("/tmp/test_low_sensitivity.pkl")
        success = storage.save_graph_data(test_graph, test_file)
        print(f"保存结果: {success}")

        if success:
            loaded_graph = storage.load_graph_data(test_file)
            print(f"加载结果: {loaded_graph is not None}")
            print(f"节点数量: {loaded_graph.number_of_nodes() if loaded_graph else 0}")

        # 创建高敏感度测试数据
        sensitive_graph = nx.MultiDiGraph()

        # 添加敏感节点和边
        for i in range(150):  # 超过阈值的节点数
            sensitive_graph.add_node(
                f"person_{i}", entity_type="person", name=f"联系人{i}"
            )

        # 添加敏感关系
        for i in range(20):
            sensitive_graph.add_edge(
                f"person_{i}",
                f"person_{i+1}",
                relationship_type="personal_contact",
                strength=0.8,
            )

        print("\n=== 高敏感度图数据测试 ===")
        test_file2 = Path("/tmp/test_high_sensitivity.pkl")
        success2 = storage.save_graph_data(sensitive_graph, test_file2)
        print(f"保存结果: {success2}")

        if success2:
            loaded_graph2 = storage.load_graph_data(test_file2)
            print(f"加载结果: {loaded_graph2 is not None}")
            print(
                f"节点数量: {loaded_graph2.number_of_nodes() if loaded_graph2 else 0}"
            )

        # 清理测试文件
        for test_file in [test_file, test_file2]:
            for suffix in ["", ".enc", ".metadata.json"]:
                file_to_remove = test_file.with_suffix(test_file.suffix + suffix)
                if file_to_remove.exists():
                    file_to_remove.unlink()

        print("\n✅ 选择性加密存储测试完成")
        return True

    except Exception as e:
        print(f"❌ 选择性加密存储测试失败: {e}")
        return False


if __name__ == "__main__":
    # 运行测试
    test_selective_encryption()
