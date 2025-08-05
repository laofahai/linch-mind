from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel


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
