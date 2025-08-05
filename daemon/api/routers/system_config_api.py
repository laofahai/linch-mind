#!/usr/bin/env python3
"""
系统配置API - 包括Registry URL配置管理
为UI提供配置读取和更新接口
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, HttpUrl
from typing import Dict, Any, Optional, List
import logging

from config.core_config import get_core_config
from services.registry_discovery_service import get_registry_discovery_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/system/config", tags=["System Config"])

class RegistryConfigRequest(BaseModel):
    """注册表配置请求"""
    registry_url: Optional[str] = None
    cache_duration_hours: Optional[int] = None
    auto_refresh: Optional[bool] = None

class RegistryConfigResponse(BaseModel):
    """注册表配置响应"""
    registry_url: str
    cache_duration_hours: int
    auto_refresh: bool
    current_source: Optional[str]
    last_updated: Optional[str]
    total_connectors: Optional[int]
    status: str

class SystemConfigResponse(BaseModel):
    """系统配置响应"""
    registry: RegistryConfigResponse
    app_data_dir: str
    config_sources: List[Dict[str, Any]]

@router.get("/registry", response_model=RegistryConfigResponse)
async def get_registry_config():
    """获取注册表配置"""
    try:
        discovery_service = get_registry_discovery_service()
        core_config = get_core_config()
        
        # 获取当前配置
        config_data = core_config.get_raw_config()
        registry_config = config_data.get('connector_registry', {})
        
        # 获取发现服务状态
        status = discovery_service.get_discovery_status()
        
        # 获取注册表元数据
        registry_metadata = await discovery_service.discover_registry()
        metadata = None
        if registry_metadata[0]:
            metadata = registry_metadata[0].get('metadata', {})
        
        return RegistryConfigResponse(
            registry_url=registry_config.get('url', discovery_service.sources[0].url),
            cache_duration_hours=registry_config.get('cache_duration_hours', 6),
            auto_refresh=registry_config.get('auto_refresh', True),
            current_source=status['last_successful_source']['description'] if status['last_successful_source'] else None,
            last_updated=metadata.get('last_updated') if metadata else None,
            total_connectors=metadata.get('total_count') if metadata else None,
            status="available" if registry_metadata[0] else "unavailable"
        )
        
    except Exception as e:
        logger.error(f"获取注册表配置失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取注册表配置失败: {str(e)}")

@router.put("/registry", response_model=RegistryConfigResponse)
async def update_registry_config(config_request: RegistryConfigRequest):
    """更新注册表配置"""
    try:
        core_config = get_core_config()
        
        # 获取当前配置
        config_data = core_config.get_raw_config()
        if 'connector_registry' not in config_data:
            config_data['connector_registry'] = {}
        
        registry_config = config_data['connector_registry']
        
        # 更新配置
        if config_request.registry_url is not None:
            registry_config['url'] = config_request.registry_url
            
        if config_request.cache_duration_hours is not None:
            registry_config['cache_duration_hours'] = config_request.cache_duration_hours
            
        if config_request.auto_refresh is not None:
            registry_config['auto_refresh'] = config_request.auto_refresh
        
        # 保存配置
        success = core_config.update_config(config_data)
        if not success:
            raise HTTPException(status_code=500, detail="保存配置失败")
        
        # 刷新发现服务
        discovery_service = get_registry_discovery_service()
        discovery_service.__init__()  # 重新初始化以使用新配置
        
        # 测试新配置
        registry_data, source = await discovery_service.discover_registry(force_refresh=True)
        
        if not registry_data:
            logger.warning("新的注册表URL测试失败，但配置已保存")
        
        # 返回更新后的配置
        return await get_registry_config()
        
    except Exception as e:
        logger.error(f"更新注册表配置失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新注册表配置失败: {str(e)}")

@router.post("/registry/test")
async def test_registry_url(test_url: str):
    """测试注册表URL可用性"""
    try:
        discovery_service = get_registry_discovery_service()
        
        # 临时创建测试源
        from services.registry_discovery_service import RegistrySource, RegistrySourceType
        test_source = RegistrySource(
            type=RegistrySourceType.USER_CONFIGURED,
            url=test_url,
            priority=1,
            timeout=30,
            description="测试URL"
        )
        
        # 测试获取数据
        registry_data = await discovery_service._fetch_from_source(test_source)
        
        if registry_data and discovery_service._validate_registry_data(registry_data):
            connector_count = len(registry_data.get('connectors', {}))
            return {
                "status": "success",
                "message": f"URL可用，发现 {connector_count} 个连接器",
                "connector_count": connector_count,
                "last_updated": registry_data.get('last_updated')
            }
        else:
            return {
                "status": "error", 
                "message": "URL不可用或数据格式错误"
            }
            
    except Exception as e:
        logger.error(f"测试注册表URL失败: {e}")
        return {
            "status": "error",
            "message": f"测试失败: {str(e)}"
        }

@router.get("/", response_model=SystemConfigResponse)
async def get_system_config():
    """获取系统配置概览"""
    try:
        core_config = get_core_config()
        discovery_service = get_registry_discovery_service()
        
        # 获取注册表配置
        registry_config = await get_registry_config()
        
        # 获取配置源信息
        status = discovery_service.get_discovery_status()
        
        return SystemConfigResponse(
            registry=registry_config,
            app_data_dir=str(core_config.app_data_dir),
            config_sources=status['sources']
        )
        
    except Exception as e:
        logger.error(f"获取系统配置失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取系统配置失败: {str(e)}")

@router.post("/registry/refresh")
async def refresh_registry():
    """手动刷新注册表缓存"""
    try:
        discovery_service = get_registry_discovery_service()
        
        registry_data, source = await discovery_service.discover_registry(force_refresh=True)
        
        if registry_data:
            connector_count = len(registry_data.get('connectors', {}))
            return {
                "status": "success",
                "message": f"注册表已刷新，发现 {connector_count} 个连接器",
                "source": source.description if source else "unknown",
                "connector_count": connector_count
            }
        else:
            return {
                "status": "error",
                "message": "刷新注册表失败"
            }
            
    except Exception as e:
        logger.error(f"刷新注册表失败: {e}")
        return {
            "status": "error", 
            "message": f"刷新失败: {str(e)}"
        }

@router.get("/registry/sources")
async def get_registry_sources():
    """获取注册表源状态"""
    try:
        discovery_service = get_registry_discovery_service()
        status = discovery_service.get_discovery_status()
        
        return {
            "sources": status['sources'],
            "last_successful_source": status['last_successful_source'],
            "cache_info": status['cache_info']
        }
        
    except Exception as e:
        logger.error(f"获取注册表源状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取状态失败: {str(e)}")

@router.get("/registry/connectors")
async def get_registry_connectors(query: Optional[str] = None, category: Optional[str] = None):
    """获取注册表中的连接器列表"""
    try:
        # 导入注册表服务
        from services.connector_registry_service import get_connector_registry_service
        registry_service = get_connector_registry_service()
        
        # 搜索连接器
        connectors = await registry_service.search_connectors(
            query=query or "",
            category=category if category and category != 'all' else None
        )
        
        return connectors
        
    except Exception as e:
        logger.error(f"获取注册表连接器失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取连接器失败: {str(e)}")

@router.get("/registry/connectors/{connector_id}/download")
async def get_connector_download_info(connector_id: str, platform: str = "linux-x64"):
    """获取连接器下载信息"""
    try:
        from services.connector_registry_service import get_connector_registry_service
        registry_service = get_connector_registry_service()
        
        download_info = await registry_service.get_connector_download_info(connector_id, platform)
        
        if download_info:
            return download_info
        else:
            raise HTTPException(status_code=404, detail=f"连接器 {connector_id} 不存在或不支持平台 {platform}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取连接器下载信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取下载信息失败: {str(e)}")