from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Optional, Any
from enum import Enum


class ConnectorStatus(Enum):
    INSTALLED = "installed"
    RUNNING = "running"
    ERROR = "error"


class ConnectorInfo(BaseModel):
    id: str
    name: str
    description: str
    status: ConnectorStatus
    data_count: int
    last_update: Optional[datetime] = None
    config: Dict[str, Any] = {}
    error_message: Optional[str] = None


class DataItem(BaseModel):
    id: str
    content: str
    source_connector: str
    timestamp: datetime
    file_path: Optional[str] = None
    metadata: Dict[str, Any] = {}
    # 智能存储策略相关字段
    storage_strategy: Optional[str] = None
    storage_reason: Optional[str] = None
    original_content_size: Optional[int] = None
    processed: Optional[bool] = None


class AIRecommendation(BaseModel):
    id: str
    title: str
    description: str
    confidence: float
    related_items: List[str] = []
    created_at: datetime


class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None


class ServerInfo(BaseModel):
    version: str
    port: int
    started_at: datetime
    status: str = "running"


# Data ingestion request models
class DataIngestionRequest(BaseModel):
    id: str
    content: str
    source_connector: str
    timestamp: datetime
    file_path: Optional[str] = None
    metadata: Dict[str, Any] = {}


class EntityRequest(BaseModel):
    id: str
    type: str
    label: str
    properties: Dict[str, Any] = {}
    source_data_id: Optional[str] = None


class RelationshipRequest(BaseModel):
    id: str
    source_entity_id: str
    target_entity_id: str
    relationship_type: str
    weight: float = 1.0
    properties: Dict[str, Any] = {}