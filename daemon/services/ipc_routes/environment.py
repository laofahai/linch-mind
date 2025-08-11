#!/usr/bin/env python3
"""
Environment Management IPC Routes - 环境管理IPC路由
提供环境切换、信息查询、初始化等功能的IPC接口
"""

import logging

from core.error_handling import ErrorCategory, ErrorSeverity, handle_errors
from core.service_facade import get_config_manager, get_environment_manager
from services.ipc_protocol import IPCErrorCode, IPCRequest, IPCResponse

logger = logging.getLogger(__name__)


class EnvironmentRoutes:
    """环境管理IPC路由处理器"""

    def __init__(self):
        self.env_manager = None
        self.config_manager = None

    def _ensure_services(self):
        """确保服务已初始化"""
        if self.env_manager is None:
            self.env_manager = get_environment_manager()
        if self.config_manager is None:
            self.config_manager = get_config_manager()

    @handle_errors(
        severity=ErrorSeverity.MEDIUM,
        category=ErrorCategory.IPC_COMMUNICATION,
        user_message="获取环境信息失败",
    )
    async def get_current_environment(self, request: IPCRequest) -> IPCResponse:
        """获取当前环境信息"""
        self._ensure_services()

        try:
            env_info = self.env_manager.get_environment_summary()

            return IPCResponse(success=True, data=env_info, message="环境信息获取成功")

        except Exception as e:
            logger.error(f"获取环境信息失败: {e}")
            return IPCResponse.error_response(
                error_code=IPCErrorCode.INTERNAL_ERROR,
                message=f"获取环境信息失败: {e}",
                details={"error_type": type(e).__name__},
            )

    @handle_errors(
        severity=ErrorSeverity.LOW,
        category=ErrorCategory.IPC_COMMUNICATION,
        user_message="列出环境失败",
    )
    async def list_environments(self, request: IPCRequest) -> IPCResponse:
        """列出所有可用环境"""
        self._ensure_services()

        try:
            environments = self.env_manager.list_environments()
            current_env = self.env_manager.current_environment.value

            # 添加当前环境标识
            for env in environments:
                env["is_current"] = env["name"] == current_env

            return IPCResponse(
                success=True,
                data={
                    "environments": environments,
                    "current_environment": current_env,
                    "total_count": len(environments),
                },
                message="环境列表获取成功",
            )

        except Exception as e:
            logger.error(f"列出环境失败: {e}")
            return IPCResponse.error_response(
                error_code="ENV_LIST_FAILED",
                message=f"列出环境失败: {e}",
                details={"error_type": type(e).__name__},
            )

    @handle_errors(
        severity=ErrorSeverity.HIGH,
        category=ErrorCategory.CONFIGURATION,
        user_message="环境切换失败",
    )
    async def switch_environment(self, request: IPCRequest) -> IPCResponse:
        """切换到指定环境"""
        self._ensure_services()

        try:
            data = request.data or {}
            target_env = data.get("environment")

            if not target_env:
                return IPCResponse.error_response(
                    error_code="ENV_SWITCH_INVALID_PARAMS",
                    message="缺少环境参数",
                    details={"required_params": ["environment"]},
                )

            # 执行环境切换
            success = self.config_manager.switch_environment(target_env)

            if success:
                return IPCResponse(
                    success=True,
                    data={
                        "old_environment": self.env_manager.current_environment.value,
                        "new_environment": target_env,
                        "restart_required": True,
                    },
                    message=f"环境已切换到 {target_env}，需要重启服务生效",
                )
            else:
                return IPCResponse.error_response(
                    error_code="ENV_SWITCH_FAILED",
                    message=f"环境切换失败: {target_env}",
                    details={"target_environment": target_env},
                )

        except Exception as e:
            logger.error(f"环境切换失败: {e}")
            return IPCResponse.error_response(
                error_code="ENV_SWITCH_ERROR",
                message=f"环境切换异常: {e}",
                details={"error_type": type(e).__name__},
            )

    @handle_errors(
        severity=ErrorSeverity.MEDIUM,
        category=ErrorCategory.CONFIGURATION,
        user_message="获取环境路径失败",
    )
    async def get_environment_paths(self, request: IPCRequest) -> IPCResponse:
        """获取环境路径信息"""
        self._ensure_services()

        try:
            paths = self.config_manager.get_environment_paths()

            return IPCResponse(
                success=True,
                data={
                    "environment": self.env_manager.current_environment.value,
                    "paths": paths,
                },
                message="环境路径信息获取成功",
            )

        except Exception as e:
            logger.error(f"获取环境路径失败: {e}")
            return IPCResponse.error_response(
                error_code="ENV_PATHS_FAILED",
                message=f"获取环境路径失败: {e}",
                details={"error_type": type(e).__name__},
            )

    @handle_errors(
        severity=ErrorSeverity.HIGH,
        category=ErrorCategory.SYSTEM_OPERATION,
        user_message="环境初始化失败",
    )
    async def initialize_environment(self, request: IPCRequest) -> IPCResponse:
        """初始化当前环境"""
        self._ensure_services()

        try:
            data = request.data or {}
            force_reinit = data.get("force_reinit", False)
            skip_models = data.get("skip_models", False)
            skip_connectors = data.get("skip_connectors", False)

            # 导入初始化器
            from scripts.initialize_environment import EnvironmentInitializer

            initializer = EnvironmentInitializer()
            success = await initializer.initialize_current_environment(
                force_reinit=force_reinit,
                skip_models=skip_models,
                skip_connectors=skip_connectors,
            )

            if success:
                return IPCResponse(
                    success=True,
                    data={
                        "environment": self.env_manager.current_environment.value,
                        "initialization_completed": True,
                        "steps": initializer.initialization_steps,
                    },
                    message="环境初始化成功完成",
                )
            else:
                return IPCResponse.error_response(
                    error_code="ENV_INIT_FAILED",
                    message="环境初始化失败",
                    details={
                        "environment": self.env_manager.current_environment.value,
                        "steps": initializer.initialization_steps,
                    },
                )

        except Exception as e:
            logger.error(f"环境初始化失败: {e}")
            return IPCResponse.error_response(
                error_code="ENV_INIT_ERROR",
                message=f"环境初始化异常: {e}",
                details={"error_type": type(e).__name__},
            )

    @handle_errors(
        severity=ErrorSeverity.HIGH,
        category=ErrorCategory.SYSTEM_OPERATION,
        user_message="环境清理失败",
    )
    async def cleanup_environment(self, request: IPCRequest) -> IPCResponse:
        """清理指定环境的数据"""
        self._ensure_services()

        try:
            data = request.data or {}
            target_env = data.get("environment")
            confirm = data.get("confirm", False)

            if not target_env:
                return IPCResponse.error_response(
                    error_code="ENV_CLEANUP_INVALID_PARAMS",
                    message="缺少环境参数",
                    details={"required_params": ["environment"]},
                )

            if not confirm:
                return IPCResponse.error_response(
                    error_code="ENV_CLEANUP_NOT_CONFIRMED",
                    message="环境清理需要确认",
                    details={"required_params": ["confirm=true"]},
                )

            # 防止清理当前环境
            current_env = self.env_manager.current_environment.value
            if target_env == current_env:
                return IPCResponse.error_response(
                    error_code="ENV_CLEANUP_CURRENT_ENV",
                    message="不能清理当前活跃环境",
                    details={"current_environment": current_env},
                )

            # 执行环境清理
            from core.environment_manager import Environment

            target_environment = Environment.from_string(target_env)
            success = self.env_manager.cleanup_environment(
                target_environment, confirm=True
            )

            if success:
                return IPCResponse(
                    success=True,
                    data={
                        "cleaned_environment": target_env,
                        "current_environment": current_env,
                    },
                    message=f"环境 {target_env} 清理完成",
                )
            else:
                return IPCResponse.error_response(
                    error_code="ENV_CLEANUP_FAILED",
                    message=f"环境清理失败: {target_env}",
                    details={"target_environment": target_env},
                )

        except Exception as e:
            logger.error(f"环境清理失败: {e}")
            return IPCResponse.error_response(
                error_code="ENV_CLEANUP_ERROR",
                message=f"环境清理异常: {e}",
                details={"error_type": type(e).__name__},
            )


# 路由注册
_environment_routes = EnvironmentRoutes()


# 导出的路由处理函数
async def handle_get_current_environment(request: IPCRequest) -> IPCResponse:
    """处理获取当前环境信息请求"""
    return await _environment_routes.get_current_environment(request)


async def handle_list_environments(request: IPCRequest) -> IPCResponse:
    """处理列出环境请求"""
    return await _environment_routes.list_environments(request)


async def handle_switch_environment(request: IPCRequest) -> IPCResponse:
    """处理环境切换请求"""
    return await _environment_routes.switch_environment(request)


async def handle_get_environment_paths(request: IPCRequest) -> IPCResponse:
    """处理获取环境路径请求"""
    return await _environment_routes.get_environment_paths(request)


async def handle_initialize_environment(request: IPCRequest) -> IPCResponse:
    """处理环境初始化请求"""
    return await _environment_routes.initialize_environment(request)


async def handle_cleanup_environment(request: IPCRequest) -> IPCResponse:
    """处理环境清理请求"""
    return await _environment_routes.cleanup_environment(request)


def create_environment_router():
    """创建环境管理路由器"""
    from services.ipc_router import IPCRouter

    router = IPCRouter(prefix="/environment")

    # 注册环境管理路由
    router.get("/current", handle_get_current_environment)
    router.get("/list", handle_list_environments)
    router.post("/switch", handle_switch_environment)
    router.get("/paths", handle_get_environment_paths)
    router.post("/initialize", handle_initialize_environment)
    router.delete("/cleanup", handle_cleanup_environment)

    logger.info("Environment router created with 6 endpoints")
    return router
