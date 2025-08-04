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




class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None


class ServerInfo(BaseModel):
    version: str
    port: int
    started_at: datetime
    status: str = "running"


