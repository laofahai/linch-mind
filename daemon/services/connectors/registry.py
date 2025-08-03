import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime

logger = logging.getLogger(__name__)


class ConnectorRegistry:
    """连接器注册表 - 单一职责：发现和注册连接器"""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent.parent
        self.connectors_dir = self.project_root / "connectors"
        self.registry_path = self.connectors_dir / "registry.json"
        self.schema_path = self.connectors_dir / "connector.schema.json"
        
        # 连接器配置缓存
        self.connector_configs: Dict[str, dict] = {}
        self.last_scan_time: Optional[datetime] = None
        
        # 可配置的扫描路径（消除硬编码）
        self.scan_paths = [
            self.connectors_dir / "official",
            self.connectors_dir / "community",
            self.connectors_dir / "third-party"
        ]
        
        logger.info(f"ConnectorRegistry初始化 - 扫描路径: {[str(p) for p in self.scan_paths]}")
        self._load_all_connectors()
    
    def _load_all_connectors(self):
        """加载所有连接器配置"""
        self.connector_configs = {}
        
        for scan_path in self.scan_paths:
            if scan_path.exists():
                self._scan_directory(scan_path)
        
        self.last_scan_time = datetime.now()
        logger.info(f"已加载 {len(self.connector_configs)} 个连接器")
    
    def _scan_directory(self, base_dir: Path):
        """扫描指定目录中的连接器"""
        for connector_dir in base_dir.iterdir():
            if not connector_dir.is_dir():
                continue
            
            connector_json_path = connector_dir / "connector.json"
            if not connector_json_path.exists():
                continue
            
            try:
                config = self._load_connector_config(connector_json_path, connector_dir, base_dir)
                if config:
                    self.connector_configs[config["id"]] = config
                    logger.debug(f"已注册连接器: {config['id']} v{config['version']}")
                    
            except Exception as e:
                logger.error(f"加载连接器配置失败 {connector_dir.name}: {e}")
    
    def _load_connector_config(self, config_path: Path, connector_dir: Path, base_dir: Path) -> Optional[dict]:
        """加载单个连接器配置"""
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        
        if not self._validate_config(config):
            return None
        
        # 添加运行时元数据
        config["_runtime"] = {
            "base_dir": str(base_dir),
            "connector_dir": str(connector_dir),
            "config_path": str(config_path),
            "registered_at": datetime.now().isoformat()
        }
        
        return config
    
    def _validate_config(self, config: dict) -> bool:
        """验证连接器配置"""
        required_fields = ["id", "name", "version", "author", "description", "entry", "permissions"]
        
        for field in required_fields:
            if field not in config:
                logger.error(f"连接器配置缺少必需字段: {field}")
                return False
        
        # 验证entry结构
        entry = config.get("entry", {})
        if "development" not in entry or "production" not in entry:
            logger.error("连接器配置缺少entry.development或entry.production")
            return False
        
        return True
    
    def get_connector_config(self, connector_id: str) -> Optional[dict]:
        """获取连接器配置"""
        return self.connector_configs.get(connector_id)
    
    def list_all_connectors(self) -> List[dict]:
        """列出所有可用连接器"""
        connectors = []
        for connector_id, config in self.connector_configs.items():
            connector_info = {
                "id": connector_id,
                "name": config["name"],
                "version": config["version"],
                "description": config["description"],
                "author": config["author"],
                "category": config.get("category", "unknown"),
                "capabilities": config.get("capabilities", {}),
                "permissions": config.get("permissions", []),
                "registered_at": config["_runtime"]["registered_at"]
            }
            connectors.append(connector_info)
        return connectors
    
    def search_connectors(self, query: str) -> List[dict]:
        """搜索连接器"""
        query_lower = query.lower()
        results = []
        
        for connector in self.list_all_connectors():
            # 在名称、描述、ID中搜索
            searchable_text = f"{connector['name']} {connector['description']} {connector['id']}".lower()
            if query_lower in searchable_text:
                results.append(connector)
        
        return results
    
    def validate_connector_permissions(self, connector_id: str) -> bool:
        """验证连接器权限声明"""
        config = self.get_connector_config(connector_id)
        if not config:
            return False
        
        permissions = config.get("permissions", [])
        valid_categories = ["filesystem", "network", "system", "process"]
        
        for permission in permissions:
            if ":" not in permission:
                logger.error(f"权限格式错误: {permission}")
                return False
            
            category, action = permission.split(":", 1)
            if category not in valid_categories:
                logger.error(f"未知权限类别: {category}")
                return False
        
        return True
    
    def reload_connectors(self):
        """重新加载连接器配置"""
        logger.info("重新加载连接器配置")
        old_count = len(self.connector_configs)
        self._load_all_connectors()
        new_count = len(self.connector_configs)
        logger.info(f"连接器配置重新加载完成: {old_count} -> {new_count}")
    
    def add_scan_path(self, path: Path):
        """添加新的扫描路径"""
        if path not in self.scan_paths:
            self.scan_paths.append(path)
            logger.info(f"添加新的扫描路径: {path}")
    
    def get_connector_count(self) -> int:
        """获取连接器总数"""
        return len(self.connector_configs)
    
    def is_connector_available(self, connector_id: str) -> bool:
        """检查连接器是否可用"""
        return connector_id in self.connector_configs