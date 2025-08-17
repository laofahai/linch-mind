"""
事件验证器 - 深度防护机制

此模块提供多层验证机制，确保系统对无效事件的健壮性。
遵循"防御性编程"原则，即使连接器有bug也不会影响系统稳定性。
"""

import re
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum


class ValidationSeverity(Enum):
    """验证严重性级别"""
    WARNING = "warning"  # 警告，记录但继续处理
    ERROR = "error"      # 错误，拒绝处理
    CRITICAL = "critical"  # 严重错误，需要立即关注


@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool
    severity: ValidationSeverity
    error_code: str
    message: str
    suggestions: List[str]


class EventValidator:
    """
    事件验证器 - 深度防护机制
    
    设计原则：
    1. 多层验证：基础 -> 语义 -> 业务逻辑
    2. 容错性：对轻微问题给出警告但继续处理
    3. 防御性：对严重问题坚决拒绝
    4. 可观测性：详细记录验证失败原因
    """
    
    # 预定义的有效连接器ID
    VALID_CONNECTOR_IDS = {
        "filesystem", "clipboard", "browser", "email", 
        "calendar", "contacts", "notes", "media"
    }
    
    # 预定义的事件类型模式
    EVENT_TYPE_PATTERNS = {
        r"^file_(created|modified|deleted|renamed|moved)$",
        r"^content_(changed|copied|pasted)$", 
        r"^url_(visited|bookmarked|shared)$",
        r"^email_(received|sent|deleted)$",
        r"^calendar_(event_created|reminder)$",
        r"^contact_(added|updated|deleted)$",
        r"^note_(created|updated|deleted)$",
        r"^media_(played|paused|stopped)$"
    }
    
    def __init__(self):
        self.compiled_patterns = [re.compile(pattern) for pattern in self.EVENT_TYPE_PATTERNS]
    
    def validate_event(
        self, 
        connector_id: str, 
        event_type: str, 
        event_data: Dict[str, Any], 
        timestamp: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        执行完整的事件验证
        
        Args:
            connector_id: 连接器ID
            event_type: 事件类型
            event_data: 事件数据
            timestamp: 时间戳
            metadata: 元数据
            
        Returns:
            ValidationResult: 验证结果
        """
        
        # 第一层：基础验证
        basic_result = self._validate_basic_fields(connector_id, event_type, event_data, timestamp)
        if not basic_result.is_valid:
            return basic_result
        
        # 第二层：语义验证  
        semantic_result = self._validate_semantic_correctness(connector_id, event_type, event_data)
        if not semantic_result.is_valid:
            return semantic_result
            
        # 第三层：业务逻辑验证
        business_result = self._validate_business_logic(connector_id, event_type, event_data, metadata)
        if not business_result.is_valid:
            return business_result
        
        return ValidationResult(
            is_valid=True,
            severity=ValidationSeverity.WARNING,
            error_code="VALIDATION_PASSED",
            message="Event validation passed",
            suggestions=[]
        )
    
    def _validate_basic_fields(
        self, 
        connector_id: str, 
        event_type: str, 
        event_data: Dict[str, Any], 
        timestamp: str
    ) -> ValidationResult:
        """基础字段验证"""
        
        # 检查空值和空字符串
        if not connector_id or not connector_id.strip():
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                error_code="EMPTY_CONNECTOR_ID",
                message="connector_id cannot be empty or whitespace-only",
                suggestions=["Provide a valid connector_id"]
            )
        
        if not event_type or not event_type.strip():
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                error_code="EMPTY_EVENT_TYPE", 
                message="event_type cannot be empty or whitespace-only",
                suggestions=["Provide a descriptive event_type like 'file_created'"]
            )
        
        if event_data is None:
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                error_code="NULL_EVENT_DATA",
                message="event_data cannot be null",
                suggestions=["Provide at least an empty dictionary {}"]
            )
        
        if not isinstance(event_data, dict):
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                error_code="INVALID_EVENT_DATA_TYPE",
                message="event_data must be a dictionary",
                suggestions=["Convert event_data to a dictionary format"]
            )
        
        # 检查时间戳格式
        if not self._is_valid_timestamp(timestamp):
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.ERROR,
                error_code="INVALID_TIMESTAMP",
                message="timestamp format is invalid",
                suggestions=["Use ISO 8601 format like '2025-08-17T09:00:00Z'"]
            )
        
        return ValidationResult(
            is_valid=True,
            severity=ValidationSeverity.WARNING,
            error_code="BASIC_VALIDATION_PASSED",
            message="Basic validation passed",
            suggestions=[]
        )
    
    def _validate_semantic_correctness(
        self, 
        connector_id: str, 
        event_type: str, 
        event_data: Dict[str, Any]
    ) -> ValidationResult:
        """语义正确性验证"""
        
        # 检查连接器ID是否在已知列表中
        if connector_id.lower() not in self.VALID_CONNECTOR_IDS:
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.WARNING,  # 只是警告，允许新连接器
                error_code="UNKNOWN_CONNECTOR_ID",
                message=f"Unknown connector_id: {connector_id}",
                suggestions=[f"Known connectors: {', '.join(self.VALID_CONNECTOR_IDS)}"]
            )
        
        # 检查事件类型是否符合预期模式
        if not self._matches_event_type_pattern(event_type):
            return ValidationResult(
                is_valid=False,
                severity=ValidationSeverity.WARNING,  # 只是警告，允许自定义事件类型
                error_code="UNUSUAL_EVENT_TYPE",
                message=f"Event type doesn't match common patterns: {event_type}",
                suggestions=["Consider using standard patterns like 'resource_action'"]
            )
        
        return ValidationResult(
            is_valid=True,
            severity=ValidationSeverity.WARNING,
            error_code="SEMANTIC_VALIDATION_PASSED",
            message="Semantic validation passed",
            suggestions=[]
        )
    
    def _validate_business_logic(
        self, 
        connector_id: str, 
        event_type: str, 
        event_data: Dict[str, Any], 
        metadata: Optional[Dict[str, Any]]
    ) -> ValidationResult:
        """业务逻辑验证"""
        
        # 文件系统连接器特定验证
        if connector_id == "filesystem":
            if "path" not in event_data:
                return ValidationResult(
                    is_valid=False,
                    severity=ValidationSeverity.ERROR,
                    error_code="MISSING_FILE_PATH",
                    message="Filesystem events must include 'path' field",
                    suggestions=["Add 'path' field to event_data"]
                )
        
        # 剪贴板连接器特定验证
        if connector_id == "clipboard":
            if "content" not in event_data and "data" not in event_data:
                return ValidationResult(
                    is_valid=False,
                    severity=ValidationSeverity.ERROR,
                    error_code="MISSING_CLIPBOARD_CONTENT",
                    message="Clipboard events must include 'content' or 'data' field",
                    suggestions=["Add 'content' or 'data' field to event_data"]
                )
        
        return ValidationResult(
            is_valid=True,
            severity=ValidationSeverity.WARNING,
            error_code="BUSINESS_VALIDATION_PASSED",
            message="Business logic validation passed",
            suggestions=[]
        )
    
    def _is_valid_timestamp(self, timestamp: str) -> bool:
        """检查时间戳格式是否有效"""
        import re
        from datetime import datetime
        
        # ISO 8601 格式检查
        iso_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{3})?Z?$'
        if not re.match(iso_pattern, timestamp):
            return False
        
        try:
            # 尝试解析时间戳
            if timestamp.endswith('Z'):
                datetime.fromisoformat(timestamp[:-1])
            else:
                datetime.fromisoformat(timestamp)
            return True
        except ValueError:
            return False
    
    def _matches_event_type_pattern(self, event_type: str) -> bool:
        """检查事件类型是否符合常见模式"""
        return any(pattern.match(event_type) for pattern in self.compiled_patterns)


# 单例验证器
_validator = None


def get_event_validator() -> EventValidator:
    """获取事件验证器单例"""
    global _validator
    if _validator is None:
        _validator = EventValidator()
    return _validator