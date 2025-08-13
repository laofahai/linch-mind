#!/usr/bin/env python3
"""
IPC安全配置 - 集中管理IPC通信的安全策略
"""

import os
from dataclasses import dataclass
from typing import Dict, Optional, Set


# 默认允许的进程名称配置 - 可通过环境变量或配置文件覆盖
DEFAULT_ALLOWED_PROCESSES = {
    "python", "python3", "python.exe",
    "flutter", "flutter.exe",
    "linch", "linch.exe"
}

# 连接器进程名称模式 - 支持动态连接器
CONNECTOR_PROCESS_PATTERNS = {
    "*-connector", "*-connector.exe",
    "linch-*", "linch-*.exe"
}

@dataclass
class IPCSecurityConfig:
    """IPC安全配置数据类"""

    # 身份验证设置
    require_authentication: bool = True
    allowed_process_names: Set[str] = None
    allowed_pids: Set[int] = None
    allowed_process_patterns: Set[str] = None

    # 频率限制设置
    rate_limit_enabled: bool = True
    max_requests_per_minute: int = 100
    max_burst_requests: int = 50

    # 路径访问控制
    blocked_paths: Set[str] = None
    sensitive_paths: Set[str] = None

    # Socket安全设置
    socket_file_permissions: int = 0o600  # 仅owner可读写
    socket_dir_permissions: int = 0o700  # 仅owner可访问

    # 日志和监控
    security_logging_enabled: bool = True
    log_security_events: bool = True
    log_failed_auth_attempts: bool = True

    # 调试和开发模式
    debug_mode: bool = False
    development_mode: bool = False

    def __post_init__(self):
        """初始化默认值"""
        if self.allowed_process_names is None:
            # 从环境变量或使用默认配置
            env_processes = os.getenv('LINCH_ALLOWED_PROCESSES')
            if env_processes:
                self.allowed_process_names = set(env_processes.split(','))
            else:
                self.allowed_process_names = DEFAULT_ALLOWED_PROCESSES.copy()
        
        if self.allowed_process_patterns is None:
            self.allowed_process_patterns = CONNECTOR_PROCESS_PATTERNS.copy()

        if self.allowed_pids is None:
            self.allowed_pids = set()

        if self.blocked_paths is None:
            self.blocked_paths = {"/internal/debug", "/admin/shutdown", "/system/kill"}

        if self.sensitive_paths is None:
            self.sensitive_paths = {
                "/system-config/security",
                "/system-config/database",
                "/connector-lifecycle/kill",
            }


class IPCSecurityManager:
    """IPC安全管理器"""

    def __init__(self, config: Optional[IPCSecurityConfig] = None):
        self.config = config or self._load_default_config()

    def _load_default_config(self) -> IPCSecurityConfig:
        """加载默认安全配置"""
        # 根据环境变量调整配置
        is_development = os.getenv("LINCH_DEVELOPMENT", "").lower() == "true"
        is_debug = os.getenv("LINCH_DEBUG", "").lower() == "true"

        config = IPCSecurityConfig()

        if is_development:
            # 开发模式：放宽一些安全限制
            config.development_mode = True
            config.require_authentication = False
            config.max_requests_per_minute = 300
            config.debug_mode = is_debug
        else:
            # 生产模式：严格安全设置
            config.development_mode = False
            config.require_authentication = True
            config.max_requests_per_minute = 100
            config.debug_mode = False

        return config

    def is_process_allowed(self, process_name: str, pid: int) -> bool:
        """检查进程是否被允许"""
        if not self.config.require_authentication:
            return True

        # 检查PID白名单
        if self.config.allowed_pids and pid in self.config.allowed_pids:
            return True

        process_name_lower = process_name.lower()
        
        # 检查进程名白名单
        if self.config.allowed_process_names:
            for allowed_name in self.config.allowed_process_names:
                if allowed_name.lower() in process_name_lower:
                    return True
        
        # 检查进程名模式匹配（支持通配符）
        if self.config.allowed_process_patterns:
            for pattern in self.config.allowed_process_patterns:
                if self._match_process_pattern(process_name_lower, pattern.lower()):
                    return True

        return False
    
    def _match_process_pattern(self, process_name: str, pattern: str) -> bool:
        """匹配进程名模式（简单通配符支持）"""
        if '*' not in pattern:
            return pattern in process_name
        
        # 简单通配符匹配
        import fnmatch
        return fnmatch.fnmatch(process_name, pattern)

    def is_path_allowed(self, path: str) -> bool:
        """检查路径是否被允许访问"""
        # 检查阻止列表
        if path in self.config.blocked_paths:
            return False

        # 对于敏感路径，需要额外验证
        if path in self.config.sensitive_paths:
            # 在生产模式下，敏感路径需要特殊处理
            if not self.config.development_mode:
                return False  # 暂时阻止，可以根据需要添加特殊验证逻辑

        return True

    def get_rate_limit_config(self) -> Dict[str, int]:
        """获取频率限制配置"""
        return {
            "max_requests_per_minute": self.config.max_requests_per_minute,
            "max_burst_requests": self.config.max_burst_requests,
            "enabled": self.config.rate_limit_enabled,
        }

    def get_socket_security_config(self) -> Dict[str, int]:
        """获取socket安全配置"""
        return {
            "file_permissions": self.config.socket_file_permissions,
            "dir_permissions": self.config.socket_dir_permissions,
        }

    def should_log_security_event(self, event_type: str) -> bool:
        """检查是否应该记录安全事件"""
        if not self.config.security_logging_enabled:
            return False

        if event_type == "auth_failed" and not self.config.log_failed_auth_attempts:
            return False

        return self.config.log_security_events

    def update_allowed_pid(self, pid: int, allow: bool = True):
        """动态更新允许的PID"""
        if allow:
            self.config.allowed_pids.add(pid)
        else:
            self.config.allowed_pids.discard(pid)
    
    def add_allowed_process(self, process_name: str):
        """动态添加允许的进程名"""
        self.config.allowed_process_names.add(process_name)
    
    def remove_allowed_process(self, process_name: str):
        """动态移除允许的进程名"""
        self.config.allowed_process_names.discard(process_name)
    
    def add_process_pattern(self, pattern: str):
        """动态添加进程名模式"""
        self.config.allowed_process_patterns.add(pattern)

    def block_path(self, path: str):
        """动态阻止路径"""
        self.config.blocked_paths.add(path)

    def unblock_path(self, path: str):
        """动态解除路径阻止"""
        self.config.blocked_paths.discard(path)


# 全局安全管理器实例
_security_manager = None


def get_ipc_security_manager() -> IPCSecurityManager:
    """获取全局IPC安全管理器"""
    global _security_manager
    if _security_manager is None:
        _security_manager = IPCSecurityManager()
    return _security_manager


def create_secure_middleware_config() -> Dict:
    """创建安全中间件配置"""
    security_manager = get_ipc_security_manager()
    rate_limit_config = security_manager.get_rate_limit_config()

    return {
        "authentication": {
            "require_auth": security_manager.config.require_authentication,
            "allowed_processes": security_manager.config.allowed_process_names,
        },
        "rate_limiting": rate_limit_config,
        "logging": {
            "enabled": security_manager.config.security_logging_enabled,
            "debug": security_manager.config.debug_mode,
        },
    }


# 预定义的安全策略
SECURITY_POLICIES = {
    "strict": IPCSecurityConfig(
        require_authentication=True,
        max_requests_per_minute=50,
        max_burst_requests=25,
        security_logging_enabled=True,
        debug_mode=False,
    ),
    "moderate": IPCSecurityConfig(
        require_authentication=True,
        max_requests_per_minute=100,
        max_burst_requests=50,
        security_logging_enabled=True,
        debug_mode=False,
    ),
    "development": IPCSecurityConfig(
        require_authentication=False,
        max_requests_per_minute=300,
        max_burst_requests=150,
        security_logging_enabled=True,
        debug_mode=True,
        development_mode=True,
    ),
    "testing": IPCSecurityConfig(
        require_authentication=False,
        max_requests_per_minute=1000,
        max_burst_requests=500,
        security_logging_enabled=False,
        debug_mode=True,
        development_mode=True,
    ),
}


def get_security_policy(policy_name: str) -> IPCSecurityConfig:
    """根据策略名称获取安全配置"""
    if policy_name in SECURITY_POLICIES:
        return SECURITY_POLICIES[policy_name]
    else:
        raise ValueError(f"Unknown security policy: {policy_name}")


if __name__ == "__main__":
    # 演示安全配置的使用
    manager = get_ipc_security_manager()

    print("=== IPC安全配置 ===")
    print(f"身份验证: {'启用' if manager.config.require_authentication else '禁用'}")
    print(f"频率限制: {manager.config.max_requests_per_minute} 请求/分钟")
    print(f"开发模式: {'是' if manager.config.development_mode else '否'}")
    print(f"允许的进程: {manager.config.allowed_process_names}")
    print(f"阻止的路径: {manager.config.blocked_paths}")
    print(f"敏感路径: {manager.config.sensitive_paths}")
