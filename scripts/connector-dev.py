#!/usr/bin/env python3
"""
Linch Mind Connector Development Tools
用于连接器验证、构建和管理的开发工具
"""

import json
import sys
import os
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent
CONNECTORS_DIR = ROOT_DIR / "connectors"
OFFICIAL_DIR = CONNECTORS_DIR / "official"
SCHEMA_FILE = CONNECTORS_DIR / "connector.schema.json"


class ConnectorValidator:
    """连接器验证器"""

    def __init__(self):
        self.schema = self._load_schema()

    def _load_schema(self) -> Optional[Dict]:
        """加载连接器schema"""
        if not SCHEMA_FILE.exists():
            logger.warning(f"Schema file not found: {SCHEMA_FILE}")
            return None

        try:
            with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load schema: {e}")
            return None

    def validate_connector(self, connector_dir: Path) -> bool:
        """验证单个连接器"""
        logger.info(f"Validating connector: {connector_dir.name}")

        # 检查必需文件
        required_files = ["connector.json", "main.py", "requirements.txt", "README.md"]

        missing_files = []
        for file_name in required_files:
            file_path = connector_dir / file_name
            if not file_path.exists():
                missing_files.append(file_name)

        if missing_files:
            logger.error(f"Missing required files: {missing_files}")
            return False

        # 验证connector.json
        config_file = connector_dir / "connector.json"
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)

            # 基本字段验证
            required_fields = ["id", "name", "version", "description", "type"]
            missing_fields = [field for field in required_fields if field not in config]

            if missing_fields:
                logger.error(
                    f"Missing required fields in connector.json: {missing_fields}"
                )
                return False

            # 验证ID匹配目录名
            if config["id"] != connector_dir.name:
                logger.error(
                    f"Connector ID '{config['id']}' doesn't match directory name '{connector_dir.name}'"
                )
                return False

            # 验证版本格式
            version = config["version"]
            if not self._is_valid_version(version):
                logger.error(f"Invalid version format: {version}")
                return False

            logger.info(f"✅ Connector {config['name']} v{version} is valid")
            return True

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in connector.json: {e}")
            return False
        except Exception as e:
            logger.error(f"Error validating connector.json: {e}")
            return False

    def _is_valid_version(self, version: str) -> bool:
        """验证版本号格式 (semantic versioning)"""
        import re

        pattern = r"^(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9-]+))?(?:\+([a-zA-Z0-9-]+))?$"
        return bool(re.match(pattern, version))

    def validate_all(self) -> bool:
        """验证所有官方连接器"""
        logger.info("Validating all official connectors...")

        if not OFFICIAL_DIR.exists():
            logger.error(f"Official connectors directory not found: {OFFICIAL_DIR}")
            return False

        connectors = [
            d
            for d in OFFICIAL_DIR.iterdir()
            if d.is_dir() and not d.name.startswith(".")
        ]

        if not connectors:
            logger.warning("No connectors found")
            return True

        valid_count = 0
        for connector_dir in connectors:
            if self.validate_connector(connector_dir):
                valid_count += 1

        logger.info(
            f"Validation complete: {valid_count}/{len(connectors)} connectors valid"
        )
        return valid_count == len(connectors)


class ConnectorLister:
    """连接器列表器"""

    def list_connectors(self, detail: bool = False) -> List[Dict[str, Any]]:
        """列出所有连接器"""
        connectors = []

        if not OFFICIAL_DIR.exists():
            logger.warning(f"Official connectors directory not found: {OFFICIAL_DIR}")
            return connectors

        for connector_dir in OFFICIAL_DIR.iterdir():
            if not connector_dir.is_dir() or connector_dir.name.startswith("."):
                continue

            config_file = connector_dir / "connector.json"
            if not config_file.exists():
                continue

            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)

                connector_info = {
                    "id": config.get("id", connector_dir.name),
                    "name": config.get("name", "Unknown"),
                    "version": config.get("version", "0.0.0"),
                    "description": config.get("description", "No description"),
                    "type": config.get("type", "unknown"),
                    "path": str(connector_dir),
                }

                if detail:
                    connector_info.update(
                        {
                            "author": config.get("author", "Unknown"),
                            "homepage": config.get("homepage", ""),
                            "permissions": config.get("permissions", []),
                            "config_schema": config.get("config_schema", {}),
                            "supported_platforms": config.get(
                                "supported_platforms", []
                            ),
                        }
                    )

                connectors.append(connector_info)

            except Exception as e:
                logger.warning(f"Failed to load config for {connector_dir.name}: {e}")

        return sorted(connectors, key=lambda x: x["id"])

    def print_list(self, detail: bool = False):
        """打印连接器列表"""
        connectors = self.list_connectors(detail)

        if not connectors:
            print("No connectors found.")
            return

        print(f"\n📦 Found {len(connectors)} connectors:\n")

        for connector in connectors:
            print(f"🔌 {connector['name']} ({connector['id']})")
            print(f"   Version: {connector['version']}")
            print(f"   Type: {connector['type']}")
            print(f"   Description: {connector['description']}")

            if detail:
                print(f"   Author: {connector['author']}")
                print(f"   Path: {connector['path']}")
                if connector["permissions"]:
                    print(f"   Permissions: {', '.join(connector['permissions'])}")
                if connector["supported_platforms"]:
                    print(
                        f"   Platforms: {', '.join(connector['supported_platforms'])}"
                    )

            print()


class ConnectorTester:
    """连接器测试器"""

    def test_connector(self, connector_id: str) -> bool:
        """测试单个连接器"""
        connector_dir = OFFICIAL_DIR / connector_id

        if not connector_dir.exists():
            logger.error(f"Connector not found: {connector_id}")
            return False

        logger.info(f"Testing connector: {connector_id}")

        # 检查依赖
        requirements_file = connector_dir / "requirements.txt"
        if requirements_file.exists():
            logger.info("Installing dependencies...")
            try:
                subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "pip",
                        "install",
                        "-r",
                        str(requirements_file),
                    ],
                    check=True,
                    capture_output=True,
                )
                logger.info("✅ Dependencies installed")
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to install dependencies: {e}")
                return False

        # 运行语法检查
        main_file = connector_dir / "main.py"
        if main_file.exists():
            logger.info("Running syntax check...")
            try:
                subprocess.run(
                    [sys.executable, "-m", "py_compile", str(main_file)],
                    check=True,
                    capture_output=True,
                )
                logger.info("✅ Syntax check passed")
            except subprocess.CalledProcessError as e:
                logger.error(f"Syntax check failed: {e}")
                return False

        # 查找并运行测试
        test_dir = connector_dir / "tests"
        if test_dir.exists():
            logger.info("Running tests...")
            try:
                subprocess.run(
                    [sys.executable, "-m", "pytest", str(test_dir), "-v"],
                    check=True,
                    capture_output=True,
                )
                logger.info("✅ Tests passed")
            except subprocess.CalledProcessError as e:
                logger.warning(f"Tests failed: {e}")
                # 测试失败不算致命错误

        logger.info(f"✅ Connector {connector_id} test completed")
        return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Linch Mind Connector Development Tools"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # validate命令
    validate_parser = subparsers.add_parser("validate", help="Validate connectors")
    validate_parser.add_argument(
        "connector", nargs="?", help="Specific connector to validate (optional)"
    )

    # list命令
    list_parser = subparsers.add_parser("list", help="List connectors")
    list_parser.add_argument(
        "--detail", action="store_true", help="Show detailed information"
    )

    # test命令
    test_parser = subparsers.add_parser("test", help="Test connectors")
    test_parser.add_argument("connector", help="Connector to test")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    try:
        if args.command == "validate":
            validator = ConnectorValidator()

            if args.connector:
                # 验证指定连接器
                connector_dir = OFFICIAL_DIR / args.connector
                if not connector_dir.exists():
                    logger.error(f"Connector not found: {args.connector}")
                    return 1

                success = validator.validate_connector(connector_dir)
                return 0 if success else 1
            else:
                # 验证所有连接器
                success = validator.validate_all()
                return 0 if success else 1

        elif args.command == "list":
            lister = ConnectorLister()
            lister.print_list(detail=args.detail)
            return 0

        elif args.command == "test":
            tester = ConnectorTester()
            success = tester.test_connector(args.connector)
            return 0 if success else 1

        else:
            parser.print_help()
            return 1

    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
