"""
连接器路径解析器 - 从ConnectorManager中提取的专用类
简化路径查找逻辑，去除硬编码
"""

import logging
import platform
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ConnectorPathResolver:
    """专用的连接器路径解析器"""

    def __init__(self):
        # 确定当前平台
        system = platform.system().lower()
        platform_map = {"darwin": "macos", "linux": "linux", "windows": "windows"}
        self.current_platform = platform_map.get(system, system)
        
        # 可能的基础目录（按优先级排序）
        self.base_dirs = self._find_connector_base_directories()
        
        # 可能的可执行文件名模式
        # 支持下划线转连字符的变体，以适配实际的二进制文件命名
        self.exe_patterns = [
            "linch-mind-{connector_id}",
            "linch-mind-{connector_id}.exe",
            "linch-mind-{connector_id_dash}",  # 下划线转连字符版本
            "linch-mind-{connector_id_dash}.exe",
            "{connector_id}",
            "{connector_id}.exe",
            "{connector_id_dash}",  # 下划线转连字符版本
            "{connector_id_dash}.exe",
        ]
        
        # 搜索目录（按优先级排序）
        self.search_subdirs = [
            "bin/release",
            "bin/debug", 
            "bin",
            ".",
        ]

    def resolve_executable_path(self, connector_id: str, connector_config: Dict[str, Any]) -> Optional[str]:
        """
        解析连接器的可执行文件路径
        
        Args:
            connector_id: 连接器ID
            connector_config: 连接器配置
            
        Returns:
            可执行文件的绝对路径，失败返回None
        """
        try:
            # 1. 首先尝试从配置中的production路径
            production_path = self._try_production_path(connector_id, connector_config)
            if production_path:
                return production_path
            
            # 2. 搜索标准位置
            return self._search_standard_locations(connector_id)
            
        except Exception as e:
            logger.error(f"解析连接器路径失败 {connector_id}: {e}")
            return None

    def _try_production_path(self, connector_id: str, connector_config: Dict[str, Any]) -> Optional[str]:
        """尝试从配置文件的production部分获取路径"""
        try:
            entry_config = connector_config.get("entry", {})
            production_config = entry_config.get("production", {})
            
            if self.current_platform in production_config:
                rel_path = production_config[self.current_platform]
                
                # 在每个基础目录中尝试相对路径
                for base_dir in self.base_dirs:
                    connector_dir = base_dir / connector_id
                    if connector_dir.exists():
                        executable_path = connector_dir / rel_path
                        if executable_path.exists():
                            logger.debug(f"使用production路径: {executable_path}")
                            return str(executable_path.resolve())
                            
        except Exception as e:
            logger.debug(f"尝试production路径失败: {e}")
        
        return None

    def _search_standard_locations(self, connector_id: str) -> Optional[str]:
        """在标准位置搜索可执行文件"""
        for base_dir in self.base_dirs:
            # 尝试 official/connector_id 和 connector_id 两种结构
            possible_dirs = [
                base_dir / "official" / connector_id,
                base_dir / connector_id
            ]
            
            for connector_dir in possible_dirs:
                if not connector_dir.exists():
                    continue
                    
                # 在每个搜索子目录中查找
                for subdir in self.search_subdirs:
                    search_dir = connector_dir / subdir
                    if not search_dir.exists():
                        continue
                    
                    # 尝试每种文件名模式
                    for pattern in self.exe_patterns:
                        # 支持下划线转连字符的变体
                        connector_id_dash = connector_id.replace('_', '-')
                        exe_name = pattern.format(
                            connector_id=connector_id,
                            connector_id_dash=connector_id_dash
                        )
                        exe_path = search_dir / exe_name
                        
                        if exe_path.exists() and exe_path.is_file():
                            logger.debug(f"找到可执行文件: {exe_path}")
                            return str(exe_path.resolve())
        
        logger.warning(f"未找到连接器 {connector_id} 的可执行文件")
        self._log_search_details(connector_id)
        return None

    def _find_connector_base_directories(self) -> List[Path]:
        """查找连接器的基础目录
        
        注：仅用于已注册连接器的可执行文件查找
        不再用于自动发现新连接器
        """
        from core.environment_manager import get_environment_manager
        
        found_dirs = []
        
        # 1. 用户数据目录（下载的连接器）
        try:
            env_manager = get_environment_manager()
            user_connectors_dir = Path(env_manager.get_data_dir()) / "connectors"
            if user_connectors_dir.exists():
                found_dirs.append(user_connectors_dir)
        except Exception as e:
            logger.debug(f"获取用户连接器目录失败: {e}")
        
        # 2. 开发模式fallback（仅用于开发测试）
        if not found_dirs:
            # 开发模式下查找项目目录
            dev_connectors = Path(__file__).parent.parent.parent.parent / "connectors"
            if dev_connectors.exists():
                found_dirs.append(dev_connectors)
                logger.debug(f"使用开发模式连接器目录: {dev_connectors}")
                
        if not found_dirs:
            logger.warning("未找到任何连接器目录")
            
        return found_dirs

    def _log_search_details(self, connector_id: str):
        """记录搜索细节以便调试"""
        logger.debug(f"搜索连接器 {connector_id} 的详细信息:")
        logger.debug(f"  基础目录: {[str(d) for d in self.base_dirs]}")
        logger.debug(f"  文件名模式: {self.exe_patterns}")
        logger.debug(f"  搜索子目录: {self.search_subdirs}")
        logger.debug(f"  当前平台: {self.current_platform}")


# 全局实例
_path_resolver = None


def get_path_resolver() -> ConnectorPathResolver:
    """获取全局路径解析器实例"""
    global _path_resolver
    if _path_resolver is None:
        _path_resolver = ConnectorPathResolver()
    return _path_resolver