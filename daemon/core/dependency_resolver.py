#!/usr/bin/env python3
"""
依赖解析器
解决循环依赖问题，提供清晰的依赖注入模式
替代分散在代码中的延迟导入
"""

import logging
from typing import Any, Callable, Dict, Optional, Type, TypeVar
from functools import wraps
import inspect

logger = logging.getLogger(__name__)

T = TypeVar("T")


class DependencyResolver:
    """依赖解析器
    
    功能:
    - 解决循环依赖问题
    - 提供懒加载依赖注入
    - 统一依赖获取接口
    - 避免在方法内部导入
    """

    def __init__(self):
        self._factories: Dict[str, Callable] = {}
        self._singletons: Dict[str, Any] = {}
        self._dependency_graph: Dict[str, set] = {}

    def register_factory(self, name: str, factory: Callable[[], Any]):
        """注册依赖工厂"""
        self._factories[name] = factory
        logger.debug(f"注册依赖工厂: {name}")

    def register_singleton(self, name: str, factory: Callable[[], Any]):
        """注册单例依赖"""
        self._factories[name] = factory
        # 单例会在首次获取时创建
        logger.debug(f"注册单例依赖: {name}")

    def get_dependency(self, name: str) -> Any:
        """获取依赖实例"""
        try:
            # 检查单例缓存
            if name in self._singletons:
                return self._singletons[name]

            # 检查工厂
            if name not in self._factories:
                raise ValueError(f"未注册的依赖: {name}")

            # 创建实例
            factory = self._factories[name]
            instance = factory()

            # 如果是单例，缓存实例
            if self._is_singleton_factory(name):
                self._singletons[name] = instance

            return instance

        except Exception as e:
            logger.error(f"获取依赖失败 [{name}]: {e}")
            raise

    def _is_singleton_factory(self, name: str) -> bool:
        """检查是否为单例工厂"""
        # 简单实现：通过命名约定判断
        # 实际项目中可以用装饰器或注册时标记
        return name.endswith("_service") or name.endswith("_manager")

    def resolve_circular_dependencies(self):
        """解决循环依赖"""
        # 这里可以实现循环依赖检测算法
        # 目前是简化实现
        pass

    def clear_cache(self):
        """清理缓存"""
        self._singletons.clear()
        logger.debug("依赖缓存已清理")


# 全局依赖解析器实例
_dependency_resolver = DependencyResolver()


def get_dependency_resolver() -> DependencyResolver:
    """获取依赖解析器"""
    return _dependency_resolver


def lazy_dependency(name: str):
    """懒加载依赖装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 注入依赖到函数参数
            resolver = get_dependency_resolver()
            dependency = resolver.get_dependency(name)
            return func(dependency, *args, **kwargs)
        return wrapper
    return decorator


class LazyDependency:
    """懒加载依赖包装器"""
    
    def __init__(self, dependency_name: str):
        self._dependency_name = dependency_name
        self._cached_instance = None

    def __call__(self):
        """获取依赖实例"""
        if self._cached_instance is None:
            resolver = get_dependency_resolver()
            self._cached_instance = resolver.get_dependency(self._dependency_name)
        return self._cached_instance

    def clear_cache(self):
        """清理缓存"""
        self._cached_instance = None


# 常用依赖的懒加载包装器
class Dependencies:
    """常用依赖的懒加载访问器"""
    
    database_service = LazyDependency("database_service")
    config_manager = LazyDependency("config_manager")
    environment_manager = LazyDependency("environment_manager")
    connector_manager = LazyDependency("connector_manager")


def setup_core_dependencies():
    """设置核心依赖"""
    resolver = get_dependency_resolver()

    # 数据库服务
    def create_database_service():
        from services.unified_database_service import UnifiedDatabaseService
        return UnifiedDatabaseService()

    resolver.register_singleton("database_service", create_database_service)

    # 配置管理器
    def create_config_manager():
        from services.unified_config_manager import UnifiedConfigManager
        return UnifiedConfigManager()

    resolver.register_singleton("config_manager", create_config_manager)

    # 环境管理器
    def create_environment_manager():
        from core.environment_manager import EnvironmentManager
        return EnvironmentManager()

    resolver.register_singleton("environment_manager", create_environment_manager)

    # 连接器管理器
    def create_connector_manager():
        from services.connectors.connector_manager import ConnectorManager
        return ConnectorManager()

    resolver.register_singleton("connector_manager", create_connector_manager)

    logger.info("核心依赖设置完成")


def resolve_import_cycles():
    """解决导入循环问题的重构指南
    
    这个函数包含了重构建议，帮助消除项目中的循环依赖
    """
    
    refactoring_guide = """
    循环依赖重构指南:
    
    1. 识别循环依赖模式:
    ❌ 错误模式:
    ```python
    def some_method(self):
        # 在方法内部导入
        from core.environment_manager import get_environment_manager
        env_manager = get_environment_manager()
    ```
    
    ✅ 正确模式:
    ```python
    def some_method(self):
        # 使用依赖解析器
        env_manager = Dependencies.environment_manager()
    ```
    
    2. 服务初始化重构:
    ❌ 错误模式:
    ```python
    class SomeService:
        def __init__(self):
            from another.service import get_another_service
            self.another_service = get_another_service()
    ```
    
    ✅ 正确模式:
    ```python
    class SomeService:
        def __init__(self, another_service=None):
            self.another_service = another_service or Dependencies.another_service()
    ```
    
    3. 全局获取函数重构:
    ❌ 删除这些模式:
    ```python
    def get_database_service():
        global _db_service
        if _db_service is None:
            _db_service = DatabaseService()
        return _db_service
    ```
    
    ✅ 使用依赖解析器:
    ```python
    # 通过依赖解析器获取
    db_service = Dependencies.database_service()
    ```
    
    4. 配置访问重构:
    ❌ 分散的配置访问:
    ```python
    from config.core_config import get_database_config
    from config.ipc_security_config import get_security_config
    ```
    
    ✅ 统一配置访问:
    ```python
    config_manager = Dependencies.config_manager()
    db_config = config_manager.get_config('database.url')
    security_config = config_manager.get_config('ipc.security.enabled')
    ```
    """
    
    print(refactoring_guide)
    return refactoring_guide


def analyze_dependency_violations():
    """分析依赖违规"""
    violations = []

    # 检查常见的循环依赖模式
    import ast
    import os
    from pathlib import Path

    project_root = Path(__file__).parent.parent
    
    for py_file in project_root.rglob("*.py"):
        if py_file.name.startswith("__"):
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查方法内导入
            if "from " in content and "def " in content:
                lines = content.split('\n')
                in_method = False
                method_imports = []
                
                for i, line in enumerate(lines):
                    stripped = line.strip()
                    if stripped.startswith("def ") and not stripped.startswith("def __"):
                        in_method = True
                    elif stripped.startswith("class "):
                        in_method = False
                    elif in_method and stripped.startswith("from "):
                        method_imports.append((py_file, i+1, stripped))
                
                if method_imports:
                    violations.extend(method_imports)
                    
        except Exception as e:
            logger.debug(f"分析文件失败 {py_file}: {e}")

    return violations


if __name__ == "__main__":
    # 运行依赖分析
    violations = analyze_dependency_violations()
    
    print("=== 循环依赖违规分析 ===")
    print(f"发现 {len(violations)} 个潜在的循环依赖问题:")
    
    for file_path, line_num, import_stmt in violations[:10]:  # 显示前10个
        rel_path = file_path.relative_to(Path(__file__).parent.parent)
        print(f"  {rel_path}:{line_num} - {import_stmt}")
    
    if len(violations) > 10:
        print(f"  ... 还有 {len(violations) - 10} 个问题")
    
    print("\n=== 重构建议 ===")
    resolve_import_cycles()