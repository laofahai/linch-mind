#!/usr/bin/env python3
"""
统一配置文件加载器
支持JSON、TOML、YAML格式，自动格式检测和向后兼容
"""

import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, Union

import yaml

# Python 3.11+ 内置 tomllib，否则使用 tomli
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None

# TOML 写入支持
try:
    import tomli_w
except ImportError:
    tomli_w = None

logger = logging.getLogger(__name__)


class ConfigLoadError(Exception):
    """配置加载错误"""



class ConfigLoader:
    """统一配置文件加载器

    支持格式:
    - TOML (.toml) - 推荐格式
    - JSON (.json) - 向后兼容
    - YAML (.yaml/.yml) - 基础支持

    特性:
    - 自动格式检测
    - 向后兼容JSON配置
    - 优先选择TOML格式
    - 详细错误信息
    """

    @staticmethod
    def load_config(config_path: Union[str, Path]) -> Dict[str, Any]:
        """加载配置文件，自动检测格式

        Args:
            config_path: 配置文件路径

        Returns:
            配置数据字典

        Raises:
            ConfigLoadError: 配置文件加载失败
        """
        config_path = Path(config_path)

        if not config_path.exists():
            raise ConfigLoadError(f"配置文件不存在: {config_path}")

        try:
            # 根据文件扩展名选择解析器
            suffix = config_path.suffix.lower()

            if suffix == ".toml":
                return ConfigLoader._load_toml(config_path)
            elif suffix == ".json":
                return ConfigLoader._load_json(config_path)
            elif suffix in [".yaml", ".yml"]:
                return ConfigLoader._load_yaml(config_path)
            else:
                # 尝试自动检测格式
                return ConfigLoader._auto_detect_and_load(config_path)

        except Exception as e:
            raise ConfigLoadError(f"加载配置文件失败 {config_path}: {e}") from e

    @staticmethod
    def load_with_fallback(base_name: str, search_dirs: list[Path]) -> Dict[str, Any]:
        """按优先级加载配置文件

        优先级: .toml > .json > .yaml

        Args:
            base_name: 配置文件基础名称 (不包含扩展名)
            search_dirs: 搜索目录列表

        Returns:
            配置数据字典

        Raises:
            ConfigLoadError: 所有可能的配置文件都不存在
        """
        # 按优先级尝试不同格式
        extensions = [".toml", ".json", ".yaml", ".yml"]

        for search_dir in search_dirs:
            for ext in extensions:
                config_path = search_dir / f"{base_name}{ext}"
                if config_path.exists():
                    logger.info(f"找到配置文件: {config_path}")
                    return ConfigLoader.load_config(config_path)

        # 生成所有尝试过的路径用于错误信息
        attempted_paths = []
        for search_dir in search_dirs:
            for ext in extensions:
                attempted_paths.append(search_dir / f"{base_name}{ext}")

        raise ConfigLoadError(
            f"未找到配置文件 '{base_name}'，搜索路径: "
            f"{[str(p) for p in attempted_paths]}"
        )

    @staticmethod
    def _load_toml(config_path: Path) -> Dict[str, Any]:
        """加载TOML配置文件"""
        if tomllib is None:
            raise ConfigLoadError("TOML支持不可用，请安装 tomli 包")

        with open(config_path, "rb") as f:
            return tomllib.load(f)

    @staticmethod
    def _load_json(config_path: Path) -> Dict[str, Any]:
        """加载JSON配置文件"""
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def _load_yaml(config_path: Path) -> Dict[str, Any]:
        """加载YAML配置文件"""
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    @staticmethod
    def _auto_detect_and_load(config_path: Path) -> Dict[str, Any]:
        """自动检测配置文件格式并加载"""
        content = config_path.read_text(encoding="utf-8").strip()

        # 尝试JSON格式
        if content.startswith("{") or content.startswith("["):
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                pass

        # 尝试TOML格式
        if tomllib and ("=" in content or "[" in content):
            try:
                return tomllib.loads(content)
            except Exception:
                pass

        # 尝试YAML格式
        try:
            return yaml.safe_load(content)
        except yaml.YAMLError:
            pass

        raise ConfigLoadError(f"无法识别配置文件格式: {config_path}")


class ConfigWriter:
    """统一配置文件写入器"""

    @staticmethod
    def save_config(config_data: Dict[str, Any], config_path: Union[str, Path]) -> None:
        """保存配置文件，根据扩展名选择格式

        Args:
            config_data: 配置数据
            config_path: 配置文件路径
        """
        config_path = Path(config_path)
        suffix = config_path.suffix.lower()

        # 确保目录存在
        config_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            if suffix == ".toml":
                ConfigWriter._save_toml(config_data, config_path)
            elif suffix == ".json":
                ConfigWriter._save_json(config_data, config_path)
            elif suffix in [".yaml", ".yml"]:
                ConfigWriter._save_yaml(config_data, config_path)
            else:
                # 默认使用TOML格式
                ConfigWriter._save_toml(config_data, config_path.with_suffix(".toml"))

        except Exception as e:
            raise ConfigLoadError(f"保存配置文件失败 {config_path}: {e}") from e

    @staticmethod
    def _save_toml(config_data: Dict[str, Any], config_path: Path) -> None:
        """保存为TOML格式"""
        if tomli_w is None:
            raise ConfigLoadError("TOML写入支持不可用，请安装 tomli-w 包")

        with open(config_path, "wb") as f:
            tomli_w.dump(config_data, f)

    @staticmethod
    def _save_json(config_data: Dict[str, Any], config_path: Path) -> None:
        """保存为JSON格式"""
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)

    @staticmethod
    def _save_yaml(config_data: Dict[str, Any], config_path: Path) -> None:
        """保存为YAML格式"""
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(
                config_data, f, default_flow_style=False, allow_unicode=True, indent=2
            )


# 便捷函数
def load_config(config_path: Union[str, Path]) -> Dict[str, Any]:
    """便捷函数：加载配置文件"""
    return ConfigLoader.load_config(config_path)


def save_config(config_data: Dict[str, Any], config_path: Union[str, Path]) -> None:
    """便捷函数：保存配置文件"""
    return ConfigWriter.save_config(config_data, config_path)


def load_with_fallback(base_name: str, search_dirs: list[Path]) -> Dict[str, Any]:
    """便捷函数：按优先级加载配置文件"""
    return ConfigLoader.load_with_fallback(base_name, search_dirs)
