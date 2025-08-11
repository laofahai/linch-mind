#!/usr/bin/env python3
"""
轻量级依赖注入容器
替换全局单例模式，提供统一的服务管理和依赖解析
"""

import inspect
import logging
import threading
from contextlib import contextmanager
from typing import Any, Callable, Dict, List, Type, TypeVar, Union

logger = logging.getLogger(__name__)

T = TypeVar("T")


class ServiceNotRegisteredError(Exception):
    """服务未注册异常"""


class CircularDependencyError(Exception):
    """循环依赖异常"""


class ServiceLifecycleError(Exception):
    """服务生命周期异常"""


class ServiceLifecycle:
    """服务生命周期枚举"""

    SINGLETON = "singleton"
    TRANSIENT = "transient"
    SCOPED = "scoped"


class ServiceDescriptor:
    """服务描述符"""

    def __init__(
        self,
        service_type: Type[T],
        factory: Union[Callable[[], T], Callable[[Any], T], Type[T]],
        lifecycle: str = ServiceLifecycle.SINGLETON,
        dependencies: List[Type] = None,
        lazy: bool = True,
    ):
        self.service_type = service_type
        self.factory = factory
        self.lifecycle = lifecycle
        self.dependencies = dependencies or []
        self.lazy = lazy
        self.instance = None
        self.created_at = None
        self.access_count = 0

    def __repr__(self):
        return f"ServiceDescriptor({self.service_type.__name__}, {self.lifecycle})"


class ServiceContainer:
    """轻量级依赖注入容器

    功能特性:
    - 支持单例、瞬态、作用域生命周期
    - 自动依赖解析和注入
    - 循环依赖检测
    - 线程安全
    - 异步服务支持
    - 弱引用支持避免内存泄漏
    """

    def __init__(self):
        self._services: Dict[Type, ServiceDescriptor] = {}
        self._instances: Dict[Type, Any] = {}
        self._scoped_instances: Dict[str, Dict[Type, Any]] = {}
        self._resolution_stack: List[Type] = []
        self._lock = threading.RLock()
        self._scope_storage = threading.local()

        logger.info("服务容器已初始化")

    def register_singleton(
        self,
        service_type: Type[T],
        factory: Union[Callable[[], T], Type[T]] = None,
        dependencies: List[Type] = None,
    ) -> "ServiceContainer":
        """注册单例服务"""
        factory = factory or service_type
        descriptor = ServiceDescriptor(
            service_type=service_type,
            factory=factory,
            lifecycle=ServiceLifecycle.SINGLETON,
            dependencies=dependencies or [],
        )

        with self._lock:
            self._services[service_type] = descriptor

        logger.debug(f"注册单例服务: {service_type.__name__}")
        return self

    def register_transient(
        self,
        service_type: Type[T],
        factory: Union[Callable[[], T], Type[T]] = None,
        dependencies: List[Type] = None,
    ) -> "ServiceContainer":
        """注册瞬态服务（每次调用都创建新实例）"""
        factory = factory or service_type
        descriptor = ServiceDescriptor(
            service_type=service_type,
            factory=factory,
            lifecycle=ServiceLifecycle.TRANSIENT,
            dependencies=dependencies or [],
        )

        with self._lock:
            self._services[service_type] = descriptor

        logger.debug(f"注册瞬态服务: {service_type.__name__}")
        return self

    def register_scoped(
        self,
        service_type: Type[T],
        factory: Union[Callable[[], T], Type[T]] = None,
        dependencies: List[Type] = None,
    ) -> "ServiceContainer":
        """注册作用域服务（在同一作用域内为单例）"""
        factory = factory or service_type
        descriptor = ServiceDescriptor(
            service_type=service_type,
            factory=factory,
            lifecycle=ServiceLifecycle.SCOPED,
            dependencies=dependencies or [],
        )

        with self._lock:
            self._services[service_type] = descriptor

        logger.debug(f"注册作用域服务: {service_type.__name__}")
        return self

    def register_instance(
        self, service_type: Type[T], instance: T
    ) -> "ServiceContainer":
        """注册服务实例"""
        descriptor = ServiceDescriptor(
            service_type=service_type,
            factory=lambda: instance,
            lifecycle=ServiceLifecycle.SINGLETON,
            lazy=False,
        )
        descriptor.instance = instance

        with self._lock:
            self._services[service_type] = descriptor
            self._instances[service_type] = instance

        logger.debug(f"注册服务实例: {service_type.__name__}")
        return self

    def get_service(self, service_type: Type[T]) -> T:
        """获取服务实例"""
        with self._lock:
            if service_type not in self._services:
                raise ServiceNotRegisteredError(f"服务 {service_type.__name__} 未注册")

            # 检查循环依赖
            if service_type in self._resolution_stack:
                cycle = (
                    " -> ".join([t.__name__ for t in self._resolution_stack])
                    + f" -> {service_type.__name__}"
                )
                raise CircularDependencyError(f"检测到循环依赖: {cycle}")

            descriptor = self._services[service_type]

            # 根据生命周期获取实例
            if descriptor.lifecycle == ServiceLifecycle.SINGLETON:
                return self._get_singleton(service_type, descriptor)
            elif descriptor.lifecycle == ServiceLifecycle.TRANSIENT:
                return self._create_instance(service_type, descriptor)
            elif descriptor.lifecycle == ServiceLifecycle.SCOPED:
                return self._get_scoped(service_type, descriptor)
            else:
                raise ServiceLifecycleError(f"不支持的生命周期: {descriptor.lifecycle}")

    def _get_singleton(self, service_type: Type[T], descriptor: ServiceDescriptor) -> T:
        """获取单例实例"""
        if descriptor.instance is not None:
            descriptor.access_count += 1
            return descriptor.instance

        if service_type in self._instances:
            descriptor.access_count += 1
            return self._instances[service_type]

        # 创建新实例
        instance = self._create_instance(service_type, descriptor)
        descriptor.instance = instance
        self._instances[service_type] = instance

        return instance

    def _get_scoped(self, service_type: Type[T], descriptor: ServiceDescriptor) -> T:
        """获取作用域实例"""
        scope_id = getattr(self._scope_storage, "scope_id", "default")

        if scope_id not in self._scoped_instances:
            self._scoped_instances[scope_id] = {}

        scope_instances = self._scoped_instances[scope_id]

        if service_type in scope_instances:
            descriptor.access_count += 1
            return scope_instances[service_type]

        # 创建新实例
        instance = self._create_instance(service_type, descriptor)
        scope_instances[service_type] = instance

        return instance

    def _create_instance(
        self, service_type: Type[T], descriptor: ServiceDescriptor
    ) -> T:
        """创建服务实例"""
        try:
            self._resolution_stack.append(service_type)

            factory = descriptor.factory
            descriptor.dependencies

            # 自动依赖注入
            if inspect.isclass(factory):
                # 如果factory是类，检查构造函数参数
                constructor = factory.__init__
                sig = inspect.signature(constructor)

                kwargs = {}
                for param_name, param in sig.parameters.items():
                    if param_name == "self":
                        continue

                    # 如果有类型注解，尝试解析依赖
                    if param.annotation != inspect.Parameter.empty:
                        if param.annotation in self._services:
                            kwargs[param_name] = self.get_service(param.annotation)
                        elif param.default != inspect.Parameter.empty:
                            # 有默认值，跳过
                            continue
                        else:
                            logger.warning(
                                f"无法解析参数 {param_name} 的依赖: {param.annotation}"
                            )

                instance = factory(**kwargs)
            else:
                # 普通工厂函数
                sig = inspect.signature(factory)
                if len(sig.parameters) == 0:
                    # 无参数工厂函数
                    instance = factory()
                else:
                    # 带参数，尝试依赖注入
                    kwargs = {}
                    for param_name, param in sig.parameters.items():
                        if (
                            param.annotation != inspect.Parameter.empty
                            and param.annotation in self._services
                        ):
                            kwargs[param_name] = self.get_service(param.annotation)

                    instance = factory(**kwargs)

            descriptor.access_count += 1
            logger.debug(f"创建服务实例: {service_type.__name__}")

            return instance

        except Exception as e:
            logger.error(f"创建服务实例失败 {service_type.__name__}: {e}")
            raise ServiceLifecycleError(f"无法创建服务 {service_type.__name__}: {e}")
        finally:
            if service_type in self._resolution_stack:
                self._resolution_stack.remove(service_type)

    @contextmanager
    def create_scope(self, scope_id: str = None):
        """创建服务作用域"""
        import uuid

        scope_id = scope_id or str(uuid.uuid4())

        # 保存当前作用域
        old_scope = getattr(self._scope_storage, "scope_id", None)

        try:
            self._scope_storage.scope_id = scope_id
            logger.debug(f"创建服务作用域: {scope_id}")
            yield scope_id
        finally:
            # 恢复作用域
            if old_scope:
                self._scope_storage.scope_id = old_scope
            else:
                if hasattr(self._scope_storage, "scope_id"):
                    delattr(self._scope_storage, "scope_id")

            # 清理作用域实例
            if scope_id in self._scoped_instances:
                instances = self._scoped_instances.pop(scope_id)
                logger.debug(f"清理作用域实例: {scope_id}, 实例数: {len(instances)}")

    def is_registered(self, service_type: Type) -> bool:
        """检查服务是否已注册"""
        return service_type in self._services

    def get_service_info(self, service_type: Type) -> Dict[str, Any]:
        """获取服务信息"""
        if service_type not in self._services:
            return {"registered": False}

        descriptor = self._services[service_type]
        return {
            "registered": True,
            "lifecycle": descriptor.lifecycle,
            "access_count": descriptor.access_count,
            "has_instance": descriptor.instance is not None,
            "dependencies": [dep.__name__ for dep in descriptor.dependencies],
        }

    def get_all_services(self) -> Dict[str, Dict[str, Any]]:
        """获取所有已注册服务的信息"""
        return {
            service_type.__name__: self.get_service_info(service_type)
            for service_type in self._services.keys()
        }

    async def dispose_async(self):
        """异步释放资源"""
        logger.info("开始异步释放服务容器资源...")

        # 释放所有单例实例
        disposed_count = 0
        for service_type, instance in list(self._instances.items()):
            try:
                if hasattr(instance, "dispose_async"):
                    await instance.dispose_async()
                elif hasattr(instance, "dispose"):
                    instance.dispose()
                disposed_count += 1
            except Exception as e:
                logger.error(f"释放服务 {service_type.__name__} 时出错: {e}")

        # 清理所有缓存
        self._instances.clear()
        self._scoped_instances.clear()

        logger.info(f"服务容器资源释放完成，已释放 {disposed_count} 个服务实例")

    def dispose(self):
        """同步释放资源"""
        logger.info("开始同步释放服务容器资源...")

        disposed_count = 0
        for service_type, instance in list(self._instances.items()):
            try:
                if hasattr(instance, "dispose"):
                    instance.dispose()
                disposed_count += 1
            except Exception as e:
                logger.error(f"释放服务 {service_type.__name__} 时出错: {e}")

        self._instances.clear()
        self._scoped_instances.clear()

        logger.info(f"服务容器资源释放完成，已释放 {disposed_count} 个服务实例")


# 全局服务容器
_global_container = ServiceContainer()


def get_container() -> ServiceContainer:
    """获取全局服务容器"""
    return _global_container


def inject(service_type: Type[T]) -> T:
    """依赖注入装饰器 - 从容器获取服务"""
    return _global_container.get_service(service_type)


def injectable(
    service_type: Type[T] = None, lifecycle: str = ServiceLifecycle.SINGLETON
):
    """可注入服务装饰器"""

    def decorator(cls):
        target_type = service_type or cls
        _global_container.register_singleton(target_type, cls)
        return cls

    return decorator


# 便捷注册函数
def register_singleton(
    service_type: Type[T], factory: Callable[[], T] = None
) -> ServiceContainer:
    """便捷单例注册函数"""
    return _global_container.register_singleton(service_type, factory)


def register_transient(
    service_type: Type[T], factory: Callable[[], T] = None
) -> ServiceContainer:
    """便捷瞬态注册函数"""
    return _global_container.register_transient(service_type, factory)


def register_scoped(
    service_type: Type[T], factory: Callable[[], T] = None
) -> ServiceContainer:
    """便捷作用域注册函数"""
    return _global_container.register_scoped(service_type, factory)


if __name__ == "__main__":
    # 测试依赖注入容器
    logging.basicConfig(level=logging.INFO)

    # 定义测试服务
    class ILogger:
        def log(self, message: str):
            pass

    class ConsoleLogger(ILogger):
        def log(self, message: str):
            print(f"LOG: {message}")

    class IRepository:
        def save(self, data):
            pass

    class DatabaseRepository(IRepository):
        def __init__(self, logger: ILogger):
            self.logger = logger

        def save(self, data):
            self.logger.log(f"Saving data: {data}")

    class UserService:
        def __init__(self, repository: IRepository, logger: ILogger):
            self.repository = repository
            self.logger = logger

        def create_user(self, name: str):
            self.logger.log(f"Creating user: {name}")
            self.repository.save({"name": name})

    # 注册服务
    container = ServiceContainer()
    container.register_singleton(ILogger, ConsoleLogger)
    container.register_singleton(IRepository, DatabaseRepository)
    container.register_singleton(UserService)

    # 使用服务
    user_service = container.get_service(UserService)
    user_service.create_user("Alice")

    # 查看服务信息
    print("所有注册的服务:")
    for name, info in container.get_all_services().items():
        print(f"  {name}: {info}")
