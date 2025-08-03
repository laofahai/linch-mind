import json
import socket
import random
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import os


class ServerConfig:
    def __init__(self, config_file: str = None):
        # 创建应用数据目录
        self.app_data_dir = Path.home() / ".linch-mind"
        self.app_data_dir.mkdir(exist_ok=True)
        
        # 配置文件路径
        if config_file is None:
            config_file = self.app_data_dir / "server_config.json"
        
        self.config_file = Path(config_file)
        self.config = self._load_config()
        
        # 创建其他必要目录
        self.data_dir = self.app_data_dir / "data"
        self.logs_dir = self.app_data_dir / "logs"
        self.db_dir = self.app_data_dir / "db"
        
        for dir_path in [self.data_dir, self.logs_dir, self.db_dir]:
            dir_path.mkdir(exist_ok=True)
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件，如果不存在则创建默认配置"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """创建默认配置"""
        return {
            "server": {
                "host": "0.0.0.0",
                "port": None,
                "port_range": [8000, 9000],
                "started_at": None
            },
            "api": {
                "version": "1.0.0",
                "title": "Linch Mind API",
                "description": "Personal AI Life Assistant API"
            },
            "connectors": {
                "filesystem": {
                    "enabled": True,
                    "watch_paths": []
                },
                "clipboard": {
                    "enabled": False
                }
            }
        }
    
    def _is_port_available(self, port: int) -> bool:
        """检查端口是否可用"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return True
        except OSError:
            return False
    
    def get_available_port(self) -> int:
        """获取可用端口"""
        current_port = self.config["server"]["port"]
        
        # 如果配置中有端口且可用，直接使用
        if current_port and self._is_port_available(current_port):
            print(f"使用配置中的端口: {current_port}")
            return current_port
        
        # 否则查找新的可用端口
        port_range = self.config["server"]["port_range"]
        start_port, end_port = port_range[0], port_range[1]
        
        # 首先尝试随机端口
        for _ in range(10):
            port = random.randint(start_port, end_port)
            if self._is_port_available(port):
                print(f"找到随机可用端口: {port}")
                self.update_port(port)
                return port
        
        # 如果随机没找到，顺序查找
        for port in range(start_port, end_port + 1):
            if self._is_port_available(port):
                print(f"找到顺序可用端口: {port}")
                self.update_port(port)
                return port
        
        raise RuntimeError(f"在范围 {start_port}-{end_port} 内没有找到可用端口")
    
    def update_port(self, port: int):
        """更新配置中的端口"""
        self.config["server"]["port"] = port
        self.config["server"]["started_at"] = datetime.now().isoformat()
        self.save_config()
    
    def save_config(self):
        """保存配置到文件"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
        print(f"配置已保存到: {self.config_file}")
    
    def get_server_info(self) -> Dict[str, Any]:
        """获取服务器信息"""
        return {
            "host": self.config["server"]["host"],
            "port": self.config["server"]["port"],
            "version": self.config["api"]["version"],
            "started_at": self.config["server"]["started_at"]
        }
    
    def get_paths(self) -> Dict[str, Path]:
        """获取应用相关路径"""
        return {
            "app_data": self.app_data_dir,
            "config": self.config_file,
            "data": self.data_dir,
            "logs": self.logs_dir,
            "database": self.db_dir
        }