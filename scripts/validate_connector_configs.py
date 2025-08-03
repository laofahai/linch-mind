#!/usr/bin/env python3
"""
连接器配置验证脚本
验证迁移后的配置文件完整性和正确性
"""

import sys
import yaml
import json
from pathlib import Path
from typing import Dict, List, Any, Tuple
import logging

# 添加项目路径到sys.path
script_dir = Path(__file__).parent
project_root = script_dir.parent
sys.path.insert(0, str(project_root))

# 设置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ConnectorConfigValidator:
    """连接器配置验证器"""

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.connectors_dir = self.project_root / "connectors"

        # 配置文件路径
        self.master_config_path = self.connectors_dir / "connectors.yaml"
        self.instances_config_path = self.connectors_dir / "instances.yaml"

        # 验证结果
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []

        logger.info(f"连接器配置验证器初始化 - 项目根目录: {self.project_root}")

    def validate_all(self) -> bool:
        """验证所有配置"""
        logger.info("🔍 开始验证连接器配置")

        try:
            # 1. 基础文件检查
            if not self._check_basic_files():
                return False

            # 2. 加载配置文件
            master_config, instances_config = self._load_configs()
            if master_config is None or instances_config is None:
                return False

            # 3. 验证配置文件结构
            self._validate_config_structure(master_config, instances_config)

            # 4. 验证连接器类型
            self._validate_connector_types(master_config.get("connector_types", {}))

            # 5. 验证连接器实例
            self._validate_connector_instances(
                instances_config.get("instances", {}),
                master_config.get("connector_types", {}),
            )

            # 6. 验证文件系统一致性
            self._validate_filesystem_consistency(
                master_config.get("connector_types", {})
            )

            # 7. 验证配置完整性
            self._validate_config_completeness(master_config, instances_config)

            # 8. 输出验证结果
            self._print_validation_results()

            # 返回是否有错误
            return len(self.errors) == 0

        except Exception as e:
            logger.error(f"验证过程中发生错误: {e}")
            self.errors.append(f"验证过程异常: {str(e)}")
            return False

    def _check_basic_files(self) -> bool:
        """检查基础文件是否存在"""
        logger.info("📁 检查配置文件存在性...")

        if not self.connectors_dir.exists():
            self.errors.append(f"连接器目录不存在: {self.connectors_dir}")
            return False

        if not self.master_config_path.exists():
            self.errors.append(f"主配置文件不存在: {self.master_config_path}")
            return False

        if not self.instances_config_path.exists():
            self.warnings.append(f"实例配置文件不存在: {self.instances_config_path}")
            # 实例配置文件不存在不是致命错误

        self.info.append("✅ 基础文件检查通过")
        return True

    def _load_configs(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """加载配置文件"""
        logger.info("📖 加载配置文件...")

        try:
            # 加载主配置
            with open(self.master_config_path, "r", encoding="utf-8") as f:
                master_config = yaml.safe_load(f)

            if not isinstance(master_config, dict):
                self.errors.append("主配置文件格式错误：不是有效的YAML对象")
                return None, None

            # 加载实例配置
            instances_config = {}
            if self.instances_config_path.exists():
                with open(self.instances_config_path, "r", encoding="utf-8") as f:
                    instances_config = yaml.safe_load(f)

                if not isinstance(instances_config, dict):
                    self.errors.append("实例配置文件格式错误：不是有效的YAML对象")
                    return None, None

            self.info.append("✅ 配置文件加载成功")
            return master_config, instances_config

        except yaml.YAMLError as e:
            self.errors.append(f"YAML解析错误: {e}")
            return None, None
        except Exception as e:
            self.errors.append(f"配置文件加载失败: {e}")
            return None, None

    def _validate_config_structure(self, master_config: Dict, instances_config: Dict):
        """验证配置文件结构"""
        logger.info("🏗️ 验证配置文件结构...")

        # 验证主配置结构
        required_master_fields = ["config_version", "connector_types"]
        for field in required_master_fields:
            if field not in master_config:
                self.errors.append(f"主配置文件缺少必需字段: {field}")

        # 验证版本信息
        version = master_config.get("config_version")
        if version != "1.0":
            self.warnings.append(f"配置版本不匹配，期望1.0，实际: {version}")

        # 验证实例配置结构
        if instances_config:
            if "instances" not in instances_config:
                self.warnings.append("实例配置文件缺少instances字段")

        self.info.append("✅ 配置文件结构验证完成")

    def _validate_connector_types(self, connector_types: Dict[str, Dict]):
        """验证连接器类型配置"""
        logger.info("🔌 验证连接器类型配置...")

        if not connector_types:
            self.warnings.append("没有找到任何连接器类型配置")
            return

        for type_id, type_config in connector_types.items():
            self._validate_single_connector_type(type_id, type_config)

        self.info.append(f"✅ 连接器类型验证完成，共验证 {len(connector_types)} 个类型")

    def _validate_single_connector_type(self, type_id: str, type_config: Dict):
        """验证单个连接器类型"""
        # 必需字段检查
        required_fields = ["name", "description", "version", "category"]
        for field in required_fields:
            if field not in type_config or not type_config[field]:
                self.errors.append(f"连接器类型 {type_id} 缺少必需字段: {field}")

        # 版本格式检查
        version = type_config.get("version", "")
        if version and not self._is_valid_version(version):
            self.warnings.append(f"连接器类型 {type_id} 版本格式可能无效: {version}")

        # 能力配置检查
        supports_multiple = type_config.get("supports_multiple_instances", False)
        max_instances = type_config.get("max_instances_per_user", 1)

        if supports_multiple and max_instances <= 1:
            self.warnings.append(f"连接器类型 {type_id} 支持多实例但最大实例数 <= 1")

        if not supports_multiple and max_instances > 1:
            self.warnings.append(f"连接器类型 {type_id} 不支持多实例但最大实例数 > 1")

        # 配置模式验证
        config_schema = type_config.get("config_schema", {})
        if config_schema and not self._validate_json_schema(config_schema):
            self.warnings.append(f"连接器类型 {type_id} 配置模式可能无效")

        # 入口点检查
        entry_point = type_config.get("entry_point", "main.py")
        if not entry_point.endswith(".py"):
            self.warnings.append(
                f"连接器类型 {type_id} 入口点不是Python文件: {entry_point}"
            )

    def _is_valid_version(self, version: str) -> bool:
        """检查版本格式是否有效（简单的语义版本检查）"""
        import re

        pattern = r"^\d+\.\d+\.\d+([+-][a-zA-Z0-9.-]+)?$"
        return bool(re.match(pattern, version))

    def _validate_json_schema(self, schema: Dict) -> bool:
        """验证JSON Schema格式（简化版）"""
        if not isinstance(schema, dict):
            return False

        # 基本的JSON Schema字段检查
        if "type" in schema:
            valid_types = [
                "object",
                "array",
                "string",
                "number",
                "integer",
                "boolean",
                "null",
            ]
            if schema["type"] not in valid_types:
                return False

        return True

    def _validate_connector_instances(
        self, instances: Dict[str, Dict], connector_types: Dict[str, Dict]
    ):
        """验证连接器实例配置"""
        logger.info("🏃 验证连接器实例配置...")

        if not instances:
            self.info.append("没有配置任何连接器实例")
            return

        for instance_id, instance_config in instances.items():
            self._validate_single_instance(
                instance_id, instance_config, connector_types
            )

        # 检查实例数量限制
        self._check_instance_limits(instances, connector_types)

        self.info.append(f"✅ 连接器实例验证完成，共验证 {len(instances)} 个实例")

    def _validate_single_instance(
        self, instance_id: str, instance_config: Dict, connector_types: Dict
    ):
        """验证单个连接器实例"""
        # 必需字段检查
        required_fields = ["type_id", "display_name", "config"]
        for field in required_fields:
            if field not in instance_config:
                self.errors.append(f"连接器实例 {instance_id} 缺少必需字段: {field}")

        # 类型引用检查
        type_id = instance_config.get("type_id")
        if type_id and type_id not in connector_types:
            self.errors.append(
                f"连接器实例 {instance_id} 引用了不存在的类型: {type_id}"
            )
            return

        # 状态值检查
        state = instance_config.get("state", "configured")
        valid_states = [
            "available",
            "installed",
            "configured",
            "enabled",
            "running",
            "error",
            "stopping",
            "updating",
            "uninstalling",
        ]
        if state not in valid_states:
            self.warnings.append(f"连接器实例 {instance_id} 状态值无效: {state}")

        # 配置验证（如果有类型定义）
        if type_id and type_id in connector_types:
            connector_type = connector_types[type_id]
            config_schema = connector_type.get("config_schema", {})
            instance_config_data = instance_config.get("config", {})

            if config_schema and not self._validate_instance_config(
                instance_config_data, config_schema
            ):
                self.warnings.append(f"连接器实例 {instance_id} 配置可能不符合类型要求")

    def _validate_instance_config(
        self, instance_config: Dict, config_schema: Dict
    ) -> bool:
        """验证实例配置是否符合类型要求（简化版）"""
        if not isinstance(config_schema, dict) or "required" not in config_schema:
            return True  # 没有严格要求就认为通过

        required_fields = config_schema.get("required", [])
        for field in required_fields:
            if field not in instance_config:
                return False

        return True

    def _check_instance_limits(self, instances: Dict, connector_types: Dict):
        """检查实例数量限制"""
        type_instance_counts = {}

        # 统计每种类型的实例数量
        for instance_id, instance_config in instances.items():
            type_id = instance_config.get("type_id")
            if type_id:
                type_instance_counts[type_id] = type_instance_counts.get(type_id, 0) + 1

        # 检查是否超过限制
        for type_id, count in type_instance_counts.items():
            if type_id in connector_types:
                connector_type = connector_types[type_id]
                supports_multiple = connector_type.get(
                    "supports_multiple_instances", False
                )
                max_instances = connector_type.get("max_instances_per_user", 1)

                if not supports_multiple and count > 1:
                    self.errors.append(
                        f"连接器类型 {type_id} 不支持多实例，但配置了 {count} 个实例"
                    )

                if count > max_instances:
                    self.errors.append(
                        f"连接器类型 {type_id} 实例数量 ({count}) 超过最大限制 ({max_instances})"
                    )

    def _validate_filesystem_consistency(self, connector_types: Dict[str, Dict]):
        """验证文件系统一致性"""
        logger.info("📂 验证文件系统一致性...")

        official_dir = self.connectors_dir / "official"
        if not official_dir.exists():
            self.warnings.append(f"官方连接器目录不存在: {official_dir}")
            return

        # 检查配置中的连接器是否在文件系统中存在
        for type_id, type_config in connector_types.items():
            connector_dir = official_dir / type_id

            if not connector_dir.exists():
                self.warnings.append(
                    f"连接器类型 {type_id} 的目录不存在: {connector_dir}"
                )
                continue

            # 检查入口文件
            entry_point = type_config.get("entry_point", "main.py")
            entry_file = connector_dir / entry_point

            if not entry_file.exists():
                self.errors.append(
                    f"连接器类型 {type_id} 的入口文件不存在: {entry_file}"
                )

            # 检查连接器配置文件
            connector_json = connector_dir / "connector.json"
            if connector_json.exists():
                try:
                    with open(connector_json, "r", encoding="utf-8") as f:
                        local_config = json.load(f)

                    # 简单一致性检查
                    local_id = local_config.get("id")
                    if local_id and local_id != type_id:
                        self.warnings.append(
                            f"连接器 {type_id} 本地配置ID不匹配: {local_id}"
                        )

                except Exception as e:
                    self.warnings.append(f"读取连接器 {type_id} 本地配置失败: {e}")

        # 检查文件系统中是否有配置中缺少的连接器
        for connector_dir in official_dir.iterdir():
            if connector_dir.is_dir() and connector_dir.name not in connector_types:
                main_file = connector_dir / "main.py"
                if main_file.exists():
                    self.warnings.append(
                        f"文件系统中存在未配置的连接器: {connector_dir.name}"
                    )

        self.info.append("✅ 文件系统一致性验证完成")

    def _validate_config_completeness(
        self, master_config: Dict, instances_config: Dict
    ):
        """验证配置完整性"""
        logger.info("🔧 验证配置完整性...")

        connector_types = master_config.get("connector_types", {})
        instances = instances_config.get("instances", {})

        # 检查是否有连接器类型但没有实例
        types_without_instances = []
        for type_id in connector_types.keys():
            has_instance = any(
                inst.get("type_id") == type_id for inst in instances.values()
            )
            if not has_instance:
                types_without_instances.append(type_id)

        if types_without_instances:
            self.info.append(
                f"以下连接器类型没有配置实例: {', '.join(types_without_instances)}"
            )

        # 检查配置元数据
        master_metadata = master_config.get("metadata", {})
        if "migration_timestamp" in master_metadata:
            self.info.append("✅ 检测到迁移配置，配置由迁移工具生成")

        self.info.append("✅ 配置完整性验证完成")

    def _print_validation_results(self):
        """打印验证结果"""
        print("\n" + "=" * 60)
        print("📋 连接器配置验证报告")
        print("=" * 60)

        # 统计信息
        total_issues = len(self.errors) + len(self.warnings)
        print(
            f"总计问题: {total_issues} (错误: {len(self.errors)}, 警告: {len(self.warnings)})"
        )

        # 错误信息
        if self.errors:
            print(f"\n❌ 错误 ({len(self.errors)}):")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")

        # 警告信息
        if self.warnings:
            print(f"\n⚠️  警告 ({len(self.warnings)}):")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")

        # 信息
        if self.info:
            print(f"\n💡 信息 ({len(self.info)}):")
            for i, info in enumerate(self.info, 1):
                print(f"  {i}. {info}")

        # 总结
        print("\n" + "=" * 60)
        if len(self.errors) == 0:
            print("✅ 验证通过！配置文件没有发现严重错误。")
        else:
            print("❌ 验证失败！发现严重错误，需要修复后才能正常使用。")

        if len(self.warnings) > 0:
            print(f"⚠️  发现 {len(self.warnings)} 个警告，建议检查和修复。")

        print("=" * 60)

    def get_validation_summary(self) -> Dict[str, Any]:
        """获取验证摘要"""
        return {
            "total_errors": len(self.errors),
            "total_warnings": len(self.warnings),
            "errors": self.errors,
            "warnings": self.warnings,
            "info": self.info,
            "passed": len(self.errors) == 0,
        }


def main():
    """主函数"""
    print("🔍 连接器配置验证工具")
    print("验证统一配置系统的配置文件完整性和正确性")
    print()

    # 创建验证器并运行
    validator = ConnectorConfigValidator()
    success = validator.validate_all()

    if success:
        print("\n🎉 配置验证通过！")
        print("配置文件格式正确，可以正常使用。")
    else:
        print("\n❌ 配置验证失败！")
        print("请根据错误信息修复配置文件。")
        sys.exit(1)


if __name__ == "__main__":
    main()
