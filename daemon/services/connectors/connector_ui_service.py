#!/usr/bin/env python3
"""
连接器UI服务
管理连接器自定义UI组件和交互
"""

import logging
import json
import asyncio
from typing import Dict, Any, List, Optional
from pathlib import Path
import importlib.util
import tempfile
import os

from services.database_service import get_database_service
from models.database_models import Connector

logger = logging.getLogger(__name__)

class ConnectorUIService:
    """连接器UI服务"""
    
    def __init__(self):
        self.db_service = get_database_service()
        self._registered_widgets = {}  # 注册的自定义组件
        self._iframe_handlers = {}     # iframe处理器
        self._widget_actions = {}      # 组件动作处理器
        
    async def register_custom_widget(
        self, 
        connector_id: str, 
        widget_name: str, 
        widget_config: Dict[str, Any]
    ) -> bool:
        """注册自定义UI组件"""
        try:
            widget_key = f"{connector_id}:{widget_name}"
            
            # 验证组件配置
            if not self._validate_widget_config(widget_config):
                logger.error(f"无效的组件配置: {widget_key}")
                return False
            
            # 注册组件
            self._registered_widgets[widget_key] = {
                "connector_id": connector_id,
                "widget_name": widget_name,
                "config": widget_config,
                "registered_at": asyncio.get_event_loop().time()
            }
            
            # 如果是iframe组件，注册处理器
            if widget_config.get("type") == "iframe":
                await self._register_iframe_handler(connector_id, widget_name, widget_config)
            
            # 注册组件动作
            if "actions" in widget_config:
                await self._register_widget_actions(connector_id, widget_name, widget_config["actions"])
            
            logger.info(f"自定义组件注册成功: {widget_key}")
            return True
            
        except Exception as e:
            logger.error(f"注册自定义组件失败 {connector_id}:{widget_name}: {e}")
            return False
    
    async def get_custom_widget_config(
        self, 
        connector_id: str, 
        widget_name: str
    ) -> Optional[Dict[str, Any]]:
        """获取自定义组件配置"""
        try:
            widget_key = f"{connector_id}:{widget_name}"
            widget_info = self._registered_widgets.get(widget_key)
            
            if not widget_info:
                # 尝试从连接器代码动态加载
                widget_config = await self._load_widget_from_connector(connector_id, widget_name)
                if widget_config:
                    await self.register_custom_widget(connector_id, widget_name, widget_config)
                    return widget_config
                return None
            
            return widget_info["config"]
            
        except Exception as e:
            logger.error(f"获取自定义组件配置失败 {connector_id}:{widget_name}: {e}")
            return None
    
    async def get_iframe_content(
        self, 
        connector_id: str, 
        component_name: str, 
        request_params: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """获取iframe组件的HTML内容"""
        try:
            handler_key = f"{connector_id}:{component_name}"
            
            if handler_key in self._iframe_handlers:
                handler = self._iframe_handlers[handler_key]
                return await handler(request_params)
            
            # 尝试从连接器目录加载静态HTML文件
            static_content = await self._load_static_iframe_content(connector_id, component_name)
            if static_content:
                return static_content
            
            # 生成默认iframe内容
            return await self._generate_default_iframe_content(connector_id, component_name, request_params)
            
        except Exception as e:
            logger.error(f"获取iframe内容失败 {connector_id}:{component_name}: {e}")
            return None
    
    async def get_static_file(
        self, 
        connector_id: str, 
        file_path: str
    ) -> Optional[Dict[str, Any]]:
        """获取连接器静态文件信息"""
        try:
            # 查找连接器目录
            connector_path = self._find_connector_path(connector_id)
            if not connector_path:
                return {"exists": False}
            
            # 构建静态文件路径
            static_dir = connector_path / "static"
            full_path = static_dir / file_path
            
            # 安全检查：确保文件在static目录内
            if not str(full_path.resolve()).startswith(str(static_dir.resolve())):
                logger.warning(f"拒绝访问目录外文件: {file_path}")
                return {"exists": False}
            
            if not full_path.exists() or not full_path.is_file():
                return {"exists": False}
            
            return {
                "exists": True,
                "full_path": str(full_path),
                "size": full_path.stat().st_size
            }
            
        except Exception as e:
            logger.error(f"获取静态文件失败 {connector_id}:{file_path}: {e}")
            return {"exists": False}
    
    async def validate_custom_config(
        self, 
        connector_id: str, 
        widget_name: str, 
        config_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """验证自定义组件配置"""
        try:
            widget_config = await self.get_custom_widget_config(connector_id, widget_name)
            if not widget_config:
                return {
                    "valid": False,
                    "errors": [f"未找到组件 {widget_name} 的配置"]
                }
            
            # 获取验证规则
            validation_rules = widget_config.get("validation", {})
            errors = []
            warnings = []
            
            # 执行基础验证
            if "required_fields" in validation_rules:
                for field in validation_rules["required_fields"]:
                    if field not in config_data:
                        errors.append(f"缺少必需字段: {field}")
            
            # 执行自定义验证
            if "custom_validator" in validation_rules:
                custom_result = await self._execute_custom_validation(
                    connector_id, widget_name, config_data, validation_rules["custom_validator"]
                )
                errors.extend(custom_result.get("errors", []))
                warnings.extend(custom_result.get("warnings", []))
            
            return {
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings
            }
            
        except Exception as e:
            logger.error(f"验证自定义配置失败 {connector_id}:{widget_name}: {e}")
            return {
                "valid": False,
                "errors": [f"验证过程中发生错误: {str(e)}"]
            }
    
    async def get_available_widgets(self, connector_id: str) -> List[Dict[str, Any]]:
        """获取连接器可用的自定义组件"""
        try:
            widgets = []
            
            # 获取已注册的组件
            for widget_key, widget_info in self._registered_widgets.items():
                if widget_info["connector_id"] == connector_id:
                    widgets.append({
                        "widget_name": widget_info["widget_name"],
                        "type": widget_info["config"].get("type", "custom"),
                        "description": widget_info["config"].get("description", ""),
                        "version": widget_info["config"].get("version", "1.0.0"),
                        "registered": True
                    })
            
            # 扫描连接器目录中的组件定义
            discovered_widgets = await self._discover_widgets_from_connector(connector_id)
            for widget in discovered_widgets:
                if not any(w["widget_name"] == widget["widget_name"] for w in widgets):
                    widget["registered"] = False
                    widgets.append(widget)
            
            return widgets
            
        except Exception as e:
            logger.error(f"获取可用组件失败 {connector_id}: {e}")
            return []
    
    async def execute_widget_action(
        self, 
        connector_id: str, 
        widget_name: str, 
        action_name: str, 
        action_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行自定义组件动作"""
        try:
            action_key = f"{connector_id}:{widget_name}:{action_name}"
            
            if action_key in self._widget_actions:
                handler = self._widget_actions[action_key]
                return await handler(action_params)
            
            # 尝试从连接器代码执行动作
            result = await self._execute_connector_widget_action(
                connector_id, widget_name, action_name, action_params
            )
            
            if result:
                return result
            
            return {
                "success": False,
                "message": f"未找到动作处理器: {action_name}"
            }
            
        except Exception as e:
            logger.error(f"执行组件动作失败 {connector_id}:{widget_name}:{action_name}: {e}")
            return {
                "success": False,
                "message": f"执行失败: {str(e)}"
            }
    
    def _validate_widget_config(self, config: Dict[str, Any]) -> bool:
        """验证组件配置格式"""
        required_fields = ["type", "version"]
        return all(field in config for field in required_fields)
    
    async def _register_iframe_handler(
        self, 
        connector_id: str, 
        widget_name: str, 
        config: Dict[str, Any]
    ):
        """注册iframe处理器"""
        handler_key = f"{connector_id}:{widget_name}"
        
        if "template_path" in config:
            # 基于模板的iframe处理器
            async def template_handler(params):
                return await self._render_template_iframe(connector_id, config["template_path"], params)
            self._iframe_handlers[handler_key] = template_handler
        
        elif "static_file" in config:
            # 静态文件iframe处理器
            async def static_handler(params):
                return await self._load_static_iframe_content(connector_id, config["static_file"])
            self._iframe_handlers[handler_key] = static_handler
    
    async def _register_widget_actions(
        self, 
        connector_id: str, 
        widget_name: str, 
        actions: Dict[str, Any]
    ):
        """注册组件动作处理器"""
        for action_name, action_config in actions.items():
            action_key = f"{connector_id}:{widget_name}:{action_name}"
            
            # 创建动作处理器
            async def action_handler(params, config=action_config):
                return await self._execute_action_config(connector_id, config, params)
            
            self._widget_actions[action_key] = action_handler
    
    async def _load_widget_from_connector(
        self, 
        connector_id: str, 
        widget_name: str
    ) -> Optional[Dict[str, Any]]:
        """从连接器代码动态加载组件定义"""
        try:
            connector_path = self._find_connector_path(connector_id)
            if not connector_path:
                return None
            
            # 查找组件定义文件
            widget_file = connector_path / "ui" / f"{widget_name}.json"
            if widget_file.exists():
                with open(widget_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            # 从Python代码获取组件定义
            return await self._load_widget_from_python_code(connector_path, widget_name)
            
        except Exception as e:
            logger.error(f"从连接器加载组件失败 {connector_id}:{widget_name}: {e}")
            return None
    
    async def _load_static_iframe_content(
        self, 
        connector_id: str, 
        file_name: str
    ) -> Optional[Dict[str, Any]]:
        """加载静态iframe内容"""
        try:
            connector_path = self._find_connector_path(connector_id)
            if not connector_path:
                return None
            
            html_file = connector_path / "ui" / "templates" / f"{file_name}.html"
            if not html_file.exists():
                return None
            
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                "content": content,
                "content_type": "text/html"
            }
            
        except Exception as e:
            logger.error(f"加载静态iframe内容失败 {connector_id}:{file_name}: {e}")
            return None
    
    async def _generate_default_iframe_content(
        self, 
        connector_id: str, 
        component_name: str, 
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成默认iframe内容"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{connector_id} - {component_name}</title>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; }}
                .params {{ background: #f5f5f5; padding: 15px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>连接器自定义组件</h2>
                <p><strong>连接器ID:</strong> {connector_id}</p>
                <p><strong>组件名称:</strong> {component_name}</p>
                
                <h3>请求参数</h3>
                <div class="params">
                    <pre>{json.dumps(params, indent=2, ensure_ascii=False)}</pre>
                </div>
                
                <p><em>这是默认的iframe内容。连接器可以通过实现自定义处理器来替换此内容。</em></p>
            </div>
        </body>
        </html>
        """
        
        return {
            "content": html_content,
            "content_type": "text/html"
        }
    
    def _find_connector_path(self, connector_id: str) -> Optional[Path]:
        """查找连接器路径"""
        # 查找官方连接器
        official_path = Path(__file__).parent.parent.parent.parent / "connectors" / "official" / connector_id
        if official_path.exists():
            return official_path
        
        # 查找社区连接器
        community_path = Path(__file__).parent.parent.parent.parent / "connectors" / "community" / connector_id
        if community_path.exists():
            return community_path
        
        return None
    
    async def _discover_widgets_from_connector(self, connector_id: str) -> List[Dict[str, Any]]:
        """从连接器目录发现组件"""
        widgets = []
        
        try:
            connector_path = self._find_connector_path(connector_id)
            if not connector_path:
                return widgets
            
            ui_dir = connector_path / "ui"
            if not ui_dir.exists():
                return widgets
            
            # 扫描UI定义文件
            for ui_file in ui_dir.glob("*.json"):
                try:
                    with open(ui_file, 'r', encoding='utf-8') as f:
                        widget_config = json.load(f)
                    
                    widgets.append({
                        "widget_name": ui_file.stem,
                        "type": widget_config.get("type", "custom"),
                        "description": widget_config.get("description", ""),
                        "version": widget_config.get("version", "1.0.0")
                    })
                except Exception as e:
                    logger.warning(f"解析UI配置文件失败 {ui_file}: {e}")
            
        except Exception as e:
            logger.error(f"发现连接器组件失败 {connector_id}: {e}")
        
        return widgets
    
    async def _execute_custom_validation(
        self, 
        connector_id: str, 
        widget_name: str, 
        config_data: Dict[str, Any], 
        validator_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行自定义验证"""
        # 简化实现，实际可以执行Python脚本或调用连接器方法
        return {"errors": [], "warnings": []}
    
    async def _execute_action_config(
        self, 
        connector_id: str, 
        action_config: Dict[str, Any], 
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行动作配置"""
        # 简化实现，可以根据action_config执行不同类型的动作
        action_type = action_config.get("type", "http")
        
        if action_type == "http":
            # HTTP请求动作
            return await self._execute_http_action(action_config, params)
        elif action_type == "script":
            # 脚本执行动作
            return await self._execute_script_action(connector_id, action_config, params)
        else:
            return {"success": False, "message": f"不支持的动作类型: {action_type}"}
    
    async def _execute_http_action(self, config: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
        """执行HTTP动作"""
        # 简化实现
        return {"success": True, "message": "HTTP动作执行成功", "data": params}
    
    async def _execute_script_action(
        self, 
        connector_id: str, 
        config: Dict[str, Any], 
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """执行脚本动作"""
        # 简化实现
        return {"success": True, "message": "脚本动作执行成功", "data": params}
    
    async def _load_widget_from_python_code(
        self, 
        connector_path: Path, 
        widget_name: str
    ) -> Optional[Dict[str, Any]]:
        """从Python代码加载组件定义"""
        # 实际实现可以动态导入模块并调用获取组件定义的方法
        return None
    
    async def _render_template_iframe(
        self, 
        connector_id: str, 
        template_path: str, 
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """渲染模板iframe"""
        # 实际实现可以使用Jinja2等模板引擎
        return await self._generate_default_iframe_content(connector_id, template_path, params)
    
    async def _execute_connector_widget_action(
        self, 
        connector_id: str, 
        widget_name: str, 
        action_name: str, 
        params: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """从连接器代码执行组件动作"""
        # 实际实现可以动态导入连接器模块并调用相应方法
        return None

# 全局单例
_ui_service = None

def get_connector_ui_service() -> ConnectorUIService:
    """获取连接器UI服务单例"""
    global _ui_service
    if _ui_service is None:
        _ui_service = ConnectorUIService()
    return _ui_service