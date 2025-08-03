# 连接器内部管理标准 - Session V55版

**基于Session V54决策**: 连接器内部自管理复杂度，系统只做启停和配置分发

**版本**: 1.0  
**状态**: 标准制定完成  
**创建时间**: 2025-08-03  
**适用范围**: 所有Linch Mind连接器开发

---

## 🎯 Session V54核心理念

### 职责边界清晰分离
```
┌─────────────────────────────────────────┐
│              系统职责边界                │
│                                         │
│  🔧 安装/卸载连接器                      │
│  ⚡ 启用/禁用连接器                      │  
│  📝 配置分发和验证                       │
│  📊 状态查询和监控                       │
│                                         │
└─────────────────────────────────────────┘
                     ↕️
┌─────────────────────────────────────────┐
│             连接器内部职责                │
│                                         │
│  📋 解析和验证配置                       │
│  🔄 创建和管理内部任务                   │
│  📁 资源分配和清理                       │
│  📡 数据处理和发送                       │
│  📈 内部统计和监控                       │
│  🛠️ 错误处理和恢复                       │
│                                         │
└─────────────────────────────────────────┘
```

### 核心设计原则
1. **连接器最懂自己**: 业务逻辑复杂度内化到连接器内部
2. **配置更新=进程重启**: 避免复杂的热重载逻辑
3. **内部任务完全自管理**: 系统不了解内部任务结构
4. **状态透明化**: 向系统暴露必要的运行状态

---

## 🏗️ 连接器内部架构标准

### 标准目录结构
```
connector_name/
├── main.py                    # 连接器入口点
├── connector.json             # 连接器元数据
├── config_schema.json         # 配置模式定义
├── src/
│   ├── connector.py           # 核心连接器类
│   ├── task_manager.py        # 内部任务管理器
│   ├── config_handler.py      # 配置解析器
│   └── tasks/
│       ├── base_task.py       # 任务基类
│       ├── watcher_task.py    # 具体任务实现
│       └── monitor_task.py    # 监控任务
├── requirements.txt           # 依赖定义
└── tests/
    ├── test_connector.py      # 连接器测试
    └── test_tasks.py          # 任务测试
```

### 核心组件标准

#### 1. 连接器主类标准
```python
# src/connector.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import asyncio
import logging
from datetime import datetime

class BaseConnector(ABC):
    """
    连接器基类 - Session V54标准
    所有连接器必须继承此基类并实现核心方法
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.task_manager = TaskManager()
        self.is_running = False
        self.stats = ConnectorStats()
        self.logger = logging.getLogger(f"connector.{self.__class__.__name__}")
        
        # Session V54: 连接器完全自管理内部状态
        self._internal_tasks: List[BaseTask] = []
        self._health_monitor: Optional[HealthMonitor] = None
        self._config_hash = self._calculate_config_hash(config)
    
    @abstractmethod
    async def start(self) -> None:
        """
        启用连接器 - 连接器内部创建所有必要任务
        
        实现要求:
        1. 解析配置，创建内部任务
        2. 启动所有任务
        3. 设置内部监控
        4. 更新统计信息
        """
        pass
    
    @abstractmethod
    async def stop(self) -> None:
        """
        禁用连接器 - 连接器内部清理所有资源
        
        实现要求:
        1. 停止所有内部任务
        2. 清理资源和连接
        3. 更新统计信息
        4. 确保无资源泄漏
        """
        pass
    
    async def reload_config(self, new_config: Dict[str, Any]) -> None:
        """
        配置重载 - Session V54决策: 进程重启方式
        
        默认实现采用停止->更新->启动的简单方式
        连接器可以覆盖此方法实现特殊逻辑
        """
        self.logger.info(f"配置重载开始: {self.__class__.__name__}")
        
        was_running = self.is_running
        
        # 完全停止
        if was_running:
            await self.stop()
        
        # 更新配置
        old_hash = self._config_hash
        self.config = new_config
        self._config_hash = self._calculate_config_hash(new_config)
        
        self.logger.info(f"配置更新: {old_hash} -> {self._config_hash}")
        
        # 重新启动 (如果之前在运行)
        if was_running:
            await self.start()
        
        self.logger.info("配置重载完成")
    
    @abstractmethod
    async def process_data(self, data: Dict[str, Any]) -> None:
        """
        处理数据并发送给daemon
        
        实现要求:
        1. 验证数据格式
        2. 添加连接器元数据
        3. 发送给daemon
        4. 更新统计信息
        """
        pass
    
    async def get_internal_status(self) -> Dict[str, Any]:
        """
        获取连接器内部状态 - 系统监控用
        
        标准状态信息，所有连接器必须提供
        """
        task_statuses = await self.task_manager.get_all_task_statuses()
        
        return {
            "connector_class": self.__class__.__name__,
            "is_running": self.is_running,
            "config_hash": self._config_hash,
            "uptime_seconds": self.stats.get_uptime_seconds(),
            
            # 任务管理信息
            "total_tasks": len(self._internal_tasks),
            "active_tasks": len([t for t in self._internal_tasks if t.is_active()]),
            "task_details": task_statuses,
            
            # 资源使用信息
            "memory_usage_mb": await self._get_memory_usage(),
            "cpu_usage_percent": await self._get_cpu_usage(),
            
            # 业务统计信息
            "statistics": self.stats.to_dict(),
            
            # 健康状态
            "health_status": await self._get_health_status(),
            "last_error": self.stats.last_error,
            "error_count": self.stats.error_count
        }
    
    # 受保护的辅助方法
    def _calculate_config_hash(self, config: Dict[str, Any]) -> str:
        """计算配置哈希值"""
        import hashlib
        import json
        config_str = json.dumps(config, sort_keys=True)
        return hashlib.md5(config_str.encode()).hexdigest()[:8]
    
    async def _get_memory_usage(self) -> float:
        """获取内存使用量 (MB)"""
        import psutil
        import os
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024
    
    async def _get_cpu_usage(self) -> float:
        """获取CPU使用率"""
        import psutil
        import os
        process = psutil.Process(os.getpid())
        return process.cpu_percent()
    
    async def _get_health_status(self) -> str:
        """获取健康状态"""
        if not self.is_running:
            return "stopped"
        
        if self.stats.error_count > 10:  # 错误太多
            return "unhealthy"
        
        if len([t for t in self._internal_tasks if not t.is_active()]) > 0:
            return "degraded"  # 有任务不活跃
        
        return "healthy"
```

#### 2. 任务管理器标准
```python
# src/task_manager.py
class TaskManager:
    """
    连接器内部任务管理器
    负责管理连接器内部的所有异步任务
    """
    
    def __init__(self):
        self.tasks: Dict[str, BaseTask] = {}
        self.task_handles: Dict[str, asyncio.Task] = {}
        self.logger = logging.getLogger("task_manager")
    
    async def register_task(self, task_id: str, task: 'BaseTask') -> None:
        """注册任务到管理器"""
        if task_id in self.tasks:
            raise ValueError(f"任务 {task_id} 已存在")
        
        self.tasks[task_id] = task
        self.logger.debug(f"注册任务: {task_id} ({type(task).__name__})")
    
    async def start_task(self, task_id: str) -> None:
        """启动指定任务"""
        if task_id not in self.tasks:
            raise ValueError(f"任务 {task_id} 不存在")
        
        task = self.tasks[task_id]
        
        # 创建异步任务句柄
        handle = asyncio.create_task(task.run())
        self.task_handles[task_id] = handle
        
        self.logger.info(f"启动任务: {task_id}")
    
    async def stop_task(self, task_id: str) -> None:
        """停止指定任务"""
        if task_id in self.tasks:
            await self.tasks[task_id].stop()
        
        if task_id in self.task_handles:
            handle = self.task_handles[task_id]
            handle.cancel()
            try:
                await handle
            except asyncio.CancelledError:
                pass
            del self.task_handles[task_id]
        
        self.logger.info(f"停止任务: {task_id}")
    
    async def start_all_tasks(self) -> None:
        """启动所有任务"""
        for task_id in self.tasks:
            await self.start_task(task_id)
    
    async def stop_all_tasks(self) -> None:
        """停止所有任务"""
        for task_id in list(self.tasks.keys()):
            await self.stop_task(task_id)
        
        self.tasks.clear()
        self.task_handles.clear()
    
    async def get_all_task_statuses(self) -> Dict[str, Dict[str, Any]]:
        """获取所有任务状态"""
        statuses = {}
        
        for task_id, task in self.tasks.items():
            statuses[task_id] = {
                "type": type(task).__name__,
                "active": task.is_active(),
                "uptime_seconds": task.get_uptime_seconds(),
                "error_count": task.get_error_count(),
                "last_activity": task.get_last_activity(),
                "custom_status": await task.get_custom_status()
            }
        
        return statuses
```

#### 3. 任务基类标准
```python
# src/tasks/base_task.py
class BaseTask(ABC):
    """
    连接器内部任务基类
    所有内部任务必须继承此基类
    """
    
    def __init__(self, task_id: str, config: Dict[str, Any]):
        self.task_id = task_id
        self.config = config
        self.is_active_flag = False
        self.start_time: Optional[datetime] = None
        self.error_count = 0
        self.last_activity: Optional[datetime] = None
        self.last_error: Optional[str] = None
        self.logger = logging.getLogger(f"task.{task_id}")
    
    @abstractmethod
    async def run(self) -> None:
        """
        任务主循环
        必须实现具体的任务逻辑
        """
        pass
    
    async def stop(self) -> None:
        """
        停止任务
        子类可以覆盖实现特殊清理逻辑
        """
        self.is_active_flag = False
        self.logger.info(f"任务 {self.task_id} 已停止")
    
    def is_active(self) -> bool:
        """检查任务是否活跃"""
        return self.is_active_flag
    
    def get_uptime_seconds(self) -> int:
        """获取运行时间"""
        if not self.start_time:
            return 0
        return int((datetime.now() - self.start_time).total_seconds())
    
    def get_error_count(self) -> int:
        """获取错误计数"""
        return self.error_count
    
    def get_last_activity(self) -> Optional[str]:
        """获取最后活动时间"""
        return self.last_activity.isoformat() if self.last_activity else None
    
    @abstractmethod
    async def get_custom_status(self) -> Dict[str, Any]:
        """
        获取任务特定的状态信息
        子类必须实现
        """
        pass
    
    def _update_activity(self) -> None:
        """更新活动时间"""
        self.last_activity = datetime.now()
    
    def _record_error(self, error: str) -> None:
        """记录错误"""
        self.error_count += 1
        self.last_error = error
        self.logger.error(f"任务错误 {self.task_id}: {error}")
```

---

## 📁 文件系统连接器实现示例

### 完整实现示例
```python
# filesystem_connector/src/connector.py
class FilesystemConnector(BaseConnector):
    """
    文件系统连接器 - Session V54标准实现
    展示连接器内部自管理的最佳实践
    """
    
    async def start(self) -> None:
        """启用连接器 - 内部创建多个文件监控任务"""
        self.logger.info("🚀 启用文件系统连接器")
        
        # 解析配置
        watch_paths = self.config.get("paths", [])
        file_extensions = self.config.get("extensions", [".md", ".txt"])
        ignore_patterns = self.config.get("ignore_patterns", [".*"])
        
        if not watch_paths:
            raise ValueError("配置错误: 必须指定至少一个监控路径")
        
        # 为每个路径创建独立的监控任务
        for i, path in enumerate(watch_paths):
            task_id = f"watcher_{i}_{hash(path) % 1000}"
            
            watcher_task = FileWatcherTask(
                task_id=task_id,
                config={
                    "path": path,
                    "extensions": file_extensions,
                    "ignore_patterns": ignore_patterns,
                    "callback": self.process_data
                }
            )
            
            await self.task_manager.register_task(task_id, watcher_task)
            self._internal_tasks.append(watcher_task)
        
        # 创建健康监控任务
        health_task = HealthMonitorTask(
            task_id="health_monitor",
            config={"check_interval": 30}
        )
        
        await self.task_manager.register_task("health_monitor", health_task)
        self._internal_tasks.append(health_task)
        
        # 启动所有任务
        await self.task_manager.start_all_tasks()
        
        self.is_running = True
        self.stats.start_time = datetime.now()
        
        self.logger.info(f"✅ 文件系统连接器启用完成，管理 {len(self._internal_tasks)} 个任务")
    
    async def stop(self) -> None:
        """禁用连接器 - 内部清理所有任务"""
        self.logger.info("🛑 禁用文件系统连接器")
        
        # 停止所有任务
        await self.task_manager.stop_all_tasks()
        
        # 清理内部状态
        self._internal_tasks.clear()
        self.is_running = False
        
        self.logger.info("✅ 文件系统连接器禁用完成")
    
    async def process_data(self, data: Dict[str, Any]) -> None:
        """处理文件变化数据并发送给daemon"""
        try:
            # 添加连接器元数据
            enriched_data = {
                **data,
                "metadata": {
                    **data.get("metadata", {}),
                    "source": "filesystem",
                    "connector_version": "1.0.0",
                    "processed_at": datetime.now().isoformat()
                }
            }
            
            # 发送给daemon
            success = await self._send_to_daemon(enriched_data)
            
            if success:
                self.stats.data_sent_count += 1
                self.logger.debug(f"数据发送成功: {data.get('title', 'unknown')}")
            else:
                self.stats.error_count += 1
                self.logger.error(f"数据发送失败: {data.get('title', 'unknown')}")
                
        except Exception as e:
            self.stats.error_count += 1
            self.logger.error(f"处理数据失败: {e}")
    
    async def _send_to_daemon(self, data: Dict[str, Any]) -> bool:
        """发送数据到daemon"""
        # 实现与daemon的HTTP通信
        try:
            # 实际的HTTP请求实现
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "http://localhost:8000/api/entities",
                    json=data
                ) as response:
                    return response.status == 201
        except Exception as e:
            self.logger.error(f"发送数据到daemon失败: {e}")
            return False

class FileWatcherTask(BaseTask):
    """文件监控任务实现"""
    
    async def run(self) -> None:
        """文件监控主循环"""
        self.is_active_flag = True
        self.start_time = datetime.now()
        
        watch_path = self.config["path"]
        callback = self.config["callback"]
        
        self.logger.info(f"开始监控路径: {watch_path}")
        
        # 实现文件监控逻辑
        while self.is_active_flag:
            try:
                # 检查文件变化
                changes = await self._scan_for_changes()
                
                for change in changes:
                    await callback(change)
                    self._update_activity()
                
                await asyncio.sleep(5)  # 监控间隔
                
            except Exception as e:
                self._record_error(str(e))
                await asyncio.sleep(10)  # 错误后延长间隔
    
    async def get_custom_status(self) -> Dict[str, Any]:
        """获取文件监控特定状态"""
        return {
            "watch_path": self.config["path"],
            "files_monitored": await self._count_monitored_files(),
            "last_scan": self.get_last_activity()
        }
    
    async def _scan_for_changes(self) -> List[Dict[str, Any]]:
        """扫描文件变化"""
        # 实现具体的文件扫描逻辑
        pass
    
    async def _count_monitored_files(self) -> int:
        """统计监控的文件数量"""
        # 实现文件计数逻辑
        pass
```

---

## 📊 连接器统计信息标准

### 统计数据模型
```python
class ConnectorStats:
    """连接器统计信息"""
    
    def __init__(self):
        self.start_time: Optional[datetime] = None
        self.data_sent_count: int = 0
        self.data_received_count: int = 0
        self.error_count: int = 0
        self.last_error: Optional[str] = None
        self.last_activity: Optional[datetime] = None
        
        # 连接器特定统计 (子类扩展)
        self.custom_stats: Dict[str, Any] = {}
    
    def get_uptime_seconds(self) -> int:
        """获取运行时间"""
        if not self.start_time:
            return 0
        return int((datetime.now() - self.start_time).total_seconds())
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "uptime_seconds": self.get_uptime_seconds(),
            "data_sent_count": self.data_sent_count,
            "data_received_count": self.data_received_count,
            "error_count": self.error_count,
            "last_error": self.last_error,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            **self.custom_stats
        }
```

---

## 🔧 配置处理标准

### 配置验证器
```python
# src/config_handler.py
class ConfigHandler:
    """连接器配置处理器"""
    
    def __init__(self, schema_path: str):
        with open(schema_path, 'r') as f:
            self.schema = json.load(f)
    
    def validate_config(self, config: Dict[str, Any]) -> None:
        """验证配置格式"""
        import jsonschema
        
        try:
            jsonschema.validate(config, self.schema)
        except jsonschema.ValidationError as e:
            raise ValueError(f"配置验证失败: {e.message}")
    
    def get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        default_config = {}
        
        for key, schema in self.schema.get("properties", {}).items():
            if "default" in schema:
                default_config[key] = schema["default"]
        
        return default_config
    
    def merge_config(self, user_config: Dict[str, Any]) -> Dict[str, Any]:
        """合并用户配置和默认配置"""
        default_config = self.get_default_config()
        merged_config = {**default_config, **user_config}
        
        self.validate_config(merged_config)
        return merged_config
```

---

## 🚀 连接器开发最佳实践

### 1. 错误处理策略
```python
# 任务级错误处理
async def run(self) -> None:
    while self.is_active_flag:
        try:
            await self._do_work()
        except CriticalError as e:
            # 关键错误，停止任务
            self._record_error(f"关键错误: {e}")
            self.is_active_flag = False
            break
        except RetryableError as e:
            # 可重试错误，记录并继续
            self._record_error(f"可重试错误: {e}")
            await asyncio.sleep(10)
        except Exception as e:
            # 未知错误，记录并短暂暂停
            self._record_error(f"未知错误: {e}")
            await asyncio.sleep(5)
```

### 2. 资源管理策略
```python
# 确保资源正确清理
async def stop(self) -> None:
    try:
        # 停止所有任务
        await self.task_manager.stop_all_tasks()
        
        # 关闭文件句柄
        for handle in self._file_handles:
            handle.close()
        
        # 关闭网络连接
        if self._http_session:
            await self._http_session.close()
            
    except Exception as e:
        self.logger.error(f"清理资源时出错: {e}")
    finally:
        self.is_running = False
```

### 3. 性能优化策略
```python
# 批量处理数据
async def process_batch(self, items: List[Any]) -> None:
    batch_size = 50
    
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        
        try:
            await self._process_batch_internal(batch)
        except Exception as e:
            # 批量失败时，逐个处理
            for item in batch:
                try:
                    await self._process_single_item(item)
                except Exception as item_error:
                    self.logger.error(f"处理单项失败: {item_error}")
```

---

## 📋 开发检查清单

### 连接器开发必须满足
- [ ] 继承 `BaseConnector` 基类
- [ ] 实现所有抽象方法
- [ ] 使用 `TaskManager` 管理内部任务
- [ ] 提供详细的内部状态信息
- [ ] 正确处理配置重载 (进程重启方式)
- [ ] 实现完善的错误处理和资源清理
- [ ] 提供配置验证和默认配置
- [ ] 包含完整的单元测试

### 任务开发必须满足
- [ ] 继承 `BaseTask` 基类
- [ ] 实现任务主循环和停止逻辑
- [ ] 提供任务特定的状态信息
- [ ] 正确处理异常和错误
- [ ] 更新活动时间和统计信息
- [ ] 支持优雅停止

### 文档要求
- [ ] 完整的 `connector.json` 元数据
- [ ] 详细的 `config_schema.json` 配置模式
- [ ] 用户配置指南和示例
- [ ] 开发者集成文档
- [ ] 故障排除指南

---

## 🔍 Session V55标准总结

### ✅ 核心标准确立
1. **职责边界**: 系统负责生命周期，连接器负责业务逻辑
2. **内部自管理**: 连接器完全管理内部任务和资源
3. **配置重启**: 采用简单可靠的进程重启方式
4. **状态透明**: 向系统暴露必要的监控信息

### 🎯 开发效率提升
1. **标准化**: 统一的基类和开发模式
2. **可复用**: 任务管理器和配置处理器可复用
3. **可测试**: 清晰的接口便于单元测试
4. **可维护**: 职责清晰，错误隔离

### 🚀 质量保证
- 错误处理和恢复机制标准化
- 资源管理和清理策略统一
- 性能监控和统计信息标准化
- 配置验证和安全性保证

**Session V55连接器内部管理标准制定完成**: 为连接器开发提供清晰的技术规范和最佳实践指导!