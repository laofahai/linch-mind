# 连接器架构大简化设计 - Session V55重构版

**基于Session V54决策的彻底重构**: 完全去除"实例"概念，连接器内部自管理复杂度

## 🎯 Session V54决策回顾

### ❌ 废弃: 复杂化的"实例"模型
```bash
# 被彻底否决的复杂架构
连接器类型 → 创建多个实例 → 每个实例独立配置 → 复杂的实例生命周期管理

filesystem连接器:
├── 文档实例 (监控 ~/Documents)     # ❌ 删除实例概念
├── 项目实例 (监控 ~/Projects)      # ❌ 删除实例概念
├── 下载实例 (监控 ~/Downloads)     # ❌ 删除实例概念
└── 实例间复杂的启停控制和状态管理   # ❌ 删除复杂管理

API复杂度: 8+ 端点，管理实例CRUD，配置同步等
维护成本: 极高
用户困惑度: 很高 ("什么是实例？")
```

### ✅ 采用: 极简连接器模型
```bash
# Session V54确定的简化架构
连接器 → 安装 → 启用/禁用 → 连接器内部自管理 → 配置更新=进程重启

filesystem连接器:
├── 用户视图: 简单的启用/禁用开关
├── 配置界面: 管理多个监控路径
├── 内部实现: 连接器自己创建多个文件监控任务
└── 配置更新: 停止进程 → 更新配置 → 重启进程

API简化: 4个核心端点，减少60%+
维护成本: 大幅降低
用户体验: 直观简单
```

---

## 🏗️ 极简API架构 (从8个减少到4个核心端点)

### 📋 Session V55重新设计的API端点
```python
# 彻底简化的API设计 - 只保留4个核心端点
/connectors/                     # 连接器管理中心
├── GET /list                    # 列出所有连接器 (已安装+可安装)
├── POST /{connector_id}/toggle  # 启用/禁用连接器 (统一端点)
├── GET /{connector_id}/config   # 获取连接器配置和状态
└── PUT /{connector_id}/config   # 更新连接器配置 (包含安装/卸载逻辑)

# 删除的冗余端点 (简化收益)
❌ /discovery    → 合并到 /list
❌ /installed    → 合并到 /list  
❌ /install      → 合并到 /config (PUT时自动安装)
❌ /uninstall    → 合并到 /config (DELETE时自动卸载)
❌ /enable       → 合并到 /toggle
❌ /disable      → 合并到 /toggle
❌ /status       → 合并到 /config
❌ /events       → 暂时不需要 (YAGNI原则)
```

### 🔧 极简数据模型 (基于Session V54决策)
```python
# Session V55重构的连接器模型
class Connector:
    """极简连接器模型 - 只保留核心属性"""
    id: str                    # 连接器ID (如 "filesystem")
    name: str                  # 显示名称 (如 "文件系统连接器")
    version: str               # 版本号
    status: ConnectorStatus    # 生命周期状态
    enabled: bool              # 启用/禁用开关
    config: dict               # 连接器配置 (连接器内部解析和管理)
    process_id: Optional[int]  # 运行进程ID (仅当enabled=True时)
    install_source: str        # 安装来源: "local_dev", "registry", "manual"
    # 删除的复杂属性
    # ❌ instances: List[Instance]  # 实例概念完全删除
    # ❌ instance_configs: dict     # 实例配置删除
    # ❌ heartbeat_config: dict     # 简化心跳机制

class ConnectorStatus(Enum):
    """简化的连接器状态枚举"""
    NOT_INSTALLED = "not_installed"  # 未安装 (可从registry安装)
    INSTALLED = "installed"          # 已安装，等待启用
    RUNNING = "running"              # 运行中 (enabled=True)
    STOPPED = "stopped"              # 已停止 (enabled=False)
    ERROR = "error"                  # 运行错误
    # 删除的复杂状态
    # ❌ STARTING = "starting"      # 删除中间状态，简化状态机
    # ❌ STOPPING = "stopping"      # 删除中间状态
    # ❌ MAINTENANCE = "maintenance" # 删除维护状态
```

---

## 🔄 极简API实现 (Session V55重构版)

### 📡 4个核心API端点实现
```python
# ultra_simplified_connector_api.py - Session V55架构
from fastapi import APIRouter, HTTPException, Body
from typing import List, Optional, Union
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/connectors", tags=["connectors"])


@router.get("/list")
async def list_all_connectors():
    """
    统一端点: 列出所有连接器 (已安装+可安装)
    替代原来的 /discovery 和 /installed 端点
    """
    try:
        connector_manager = get_connector_manager()
        
        # 获取已安装连接器
        installed = await connector_manager.list_installed()
        
        # 从registry获取可用连接器 (如果可用)
        try:
            registry_client = get_registry_client()
            available = await registry_client.discover_connectors()
        except Exception:
            available = []  # registry不可用时降级处理
        
        # 合并数据，标记安装状态
        all_connectors = []
        installed_ids = {c.id for c in installed}
        
        # 添加已安装的连接器
        for connector in installed:
            all_connectors.append({
                "id": connector.id,
                "name": connector.name,
                "version": connector.version,
                "status": connector.status,
                "enabled": connector.enabled,
                "installed": True,
                "install_source": connector.install_source
            })
        
        # 添加可安装但未安装的连接器
        for connector in available:
            if connector["id"] not in installed_ids:
                all_connectors.append({
                    "id": connector["id"],
                    "name": connector["name"],
                    "version": connector["version"],
                    "status": "not_installed",
                    "enabled": False,
                    "installed": False,
                    "install_source": "registry"
                })
        
        return {
            "success": True,
            "connectors": all_connectors,
            "total_count": len(all_connectors),
            "installed_count": len(installed),
            "available_count": len(available)
        }
        
    except Exception as e:
        logger.error(f"列出连接器失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{connector_id}/toggle")
async def toggle_connector(connector_id: str, action: dict = Body(...)):
    """
    统一端点: 启用/禁用连接器切换
    替代原来的 /enable 和 /disable 端点
    """
    try:
        connector_manager = get_connector_manager()
        target_enabled = action.get("enabled", True)  # 默认启用
        
        # 检查连接器是否存在
        if not await connector_manager.is_installed(connector_id):
            raise HTTPException(status_code=404, detail=f"连接器 {connector_id} 未安装")
        
        current_connector = await connector_manager.get_connector(connector_id)
        
        if target_enabled and not current_connector.enabled:
            # 启用连接器
            success = await connector_manager.enable(connector_id)
            action_desc = "启用"
        elif not target_enabled and current_connector.enabled:
            # 禁用连接器
            success = await connector_manager.disable(connector_id)
            action_desc = "禁用"
        else:
            # 状态没有变化
            return {
                "success": True,
                "message": f"连接器 {connector_id} 状态未变化",
                "connector_id": connector_id,
                "enabled": current_connector.enabled,
                "status": current_connector.status
            }
        
        if success:
            return {
                "success": True,
                "message": f"连接器 {connector_id} {action_desc}成功",
                "connector_id": connector_id,
                "enabled": target_enabled,
                "status": "running" if target_enabled else "stopped"
            }
        else:
            raise HTTPException(status_code=500, detail=f"{action_desc}失败")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"切换连接器状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{connector_id}/config")
async def get_connector_config_and_status(connector_id: str):
    """
    统一端点: 获取连接器配置和状态
    替代原来的 /config 和 /status 端点
    """
    try:
        connector_manager = get_connector_manager()
        
        # 检查连接器是否存在
        if not await connector_manager.is_installed(connector_id):
            # 如果未安装，从registry获取默认配置
            try:
                registry_client = get_registry_client()
                connector_info = await registry_client.get_connector_info(connector_id)
                return {
                    "success": True,
                    "connector_id": connector_id,
                    "status": "not_installed",
                    "enabled": False,
                    "config": {},
                    "config_schema": connector_info.get("config_schema", {}),
                    "default_config": connector_info.get("default_config", {}),
                    "can_install": True
                }
            except Exception:
                raise HTTPException(status_code=404, detail=f"连接器 {connector_id} 不存在")
        
        # 获取已安装连接器的完整信息
        connector = await connector_manager.get_connector(connector_id)
        config = await connector_manager.get_config(connector_id)
        config_schema = await connector_manager.get_config_schema(connector_id)
        detailed_status = await connector_manager.get_detailed_status(connector_id)
        
        return {
            "success": True,
            "connector_id": connector_id,
            "status": connector.status,
            "enabled": connector.enabled,
            "config": config,
            "config_schema": config_schema,
            "version": connector.version,
            "install_source": connector.install_source,
            "process_id": connector.process_id,
            "detailed_status": detailed_status,
            "can_install": False  # 已安装
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取连接器配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{connector_id}/config")
async def update_connector_config_and_lifecycle(
    connector_id: str, 
    update_data: dict = Body(...)
):
    """
    统一端点: 更新配置+生命周期管理 (安装/卸载/配置更新)
    替代原来的 /install, /uninstall, /config 端点
    """
    try:
        connector_manager = get_connector_manager()
        action = update_data.get("action", "update_config")  # update_config, install, uninstall
        
        if action == "install":
            # 安装连接器
            if await connector_manager.is_installed(connector_id):
                raise HTTPException(status_code=400, detail="连接器已安装")
            
            version = update_data.get("version", "latest")
            initial_config = update_data.get("config", {})
            
            success = await connector_manager.install(connector_id, version, initial_config)
            
            if success:
                return {
                    "success": True,
                    "message": f"连接器 {connector_id} 安装成功",
                    "connector_id": connector_id,
                    "action": "installed",
                    "version": version
                }
            else:
                raise HTTPException(status_code=500, detail="安装失败")
        
        elif action == "uninstall":
            # 卸载连接器
            if not await connector_manager.is_installed(connector_id):
                raise HTTPException(status_code=404, detail="连接器未安装")
            
            # 如果正在运行，先停止
            connector = await connector_manager.get_connector(connector_id)
            if connector.enabled:
                await connector_manager.disable(connector_id)
            
            success = await connector_manager.uninstall(connector_id)
            
            if success:
                return {
                    "success": True,
                    "message": f"连接器 {connector_id} 卸载成功",
                    "connector_id": connector_id,
                    "action": "uninstalled"
                }
            else:
                raise HTTPException(status_code=500, detail="卸载失败")
        
        else:  # action == "update_config" (默认)
            # 更新配置
            if not await connector_manager.is_installed(connector_id):
                raise HTTPException(status_code=404, detail="连接器未安装")
            
            new_config = update_data.get("config", {})
            
            # 验证配置
            await connector_manager.validate_config(connector_id, new_config)
            
            # 更新配置 (Session V54决策: 配置更新 = 进程重启)
            connector = await connector_manager.get_connector(connector_id)
            was_running = connector.enabled
            
            # 如果正在运行，先停止
            if was_running:
                await connector_manager.disable(connector_id)
            
            # 更新配置
            success = await connector_manager.update_config(connector_id, new_config)
            
            # 如果之前在运行，重新启动
            restart_success = True
            if was_running:
                restart_success = await connector_manager.enable(connector_id)
            
            if success:
                return {
                    "success": True,
                    "message": "配置更新成功" + (" (已重启)" if was_running else ""),
                    "connector_id": connector_id,
                    "action": "config_updated",
                    "restarted": was_running,
                    "restart_success": restart_success
                }
            else:
                raise HTTPException(status_code=500, detail="配置更新失败")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新连接器配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 🎯 连接器内部自管理架构 (Session V54核心理念)

### 📁 Filesystem连接器重新设计 - 完全自管理版
```python
# filesystem_connector_v55.py - Session V55重构版
class FilesystemConnector:
    """
    Session V54决策实现: 连接器内部自管理复杂度
    用户只需要管理启用/禁用，连接器内部处理所有多任务管理
    """
    
    def __init__(self, config: dict):
        self.config = config
        self.watchers = []  # 内部管理的多个文件监控任务
        self.task_manager = TaskManager()  # 内部任务管理器
        self.is_running = False
        self.stats = {
            "files_monitored": 0,
            "changes_detected": 0,
            "tasks_running": 0,
            "last_activity": None
        }
    
    async def start(self):
        """
        启用连接器 - 内部完全自管理
        核心原则: 连接器最懂自己的业务逻辑
        """
        logger.info("🚀 启用文件系统连接器 - 开始内部自管理")
        
        # 解析配置，创建内部任务
        watch_paths = self.config.get("paths", [])
        file_extensions = self.config.get("extensions", [".md", ".txt", ".pdf"])
        ignore_patterns = self.config.get("ignore_patterns", [".*", "node_modules", ".git"])
        max_file_size = self.config.get("max_file_size", 10 * 1024 * 1024)  # 10MB
        scan_interval = self.config.get("scan_interval", 5)  # 5秒
        
        # 内部自管理: 为每个路径创建独立的监控任务
        for i, path in enumerate(watch_paths):
            task_id = f"watcher_{i}_{hash(path) % 1000}"
            
            logger.info(f"📁 创建内部监控任务: {task_id} -> {path}")
            
            watcher = FileWatcher(
                task_id=task_id,
                path=path,
                extensions=file_extensions,
                ignore_patterns=ignore_patterns,
                max_file_size=max_file_size,
                scan_interval=scan_interval,
                callback=self.on_file_change
            )
            
            # 注册到内部任务管理器
            await self.task_manager.register_task(task_id, watcher)
            await watcher.start()
            self.watchers.append(watcher)
        
        # 启动内部状态监控任务
        health_monitor = HealthMonitor(self.watchers, self.update_stats)
        await self.task_manager.register_task("health_monitor", health_monitor)
        await health_monitor.start()
        
        self.is_running = True
        self.stats["tasks_running"] = len(self.watchers) + 1  # +1 for health monitor
        
        logger.info(f"✅ 文件系统连接器启用完成，内部管理 {len(self.watchers)} 个监控任务")
    
    async def stop(self):
        """
        禁用连接器 - 内部完全清理
        保证没有任何残留的任务或资源
        """
        logger.info("🛑 禁用文件系统连接器 - 开始内部清理")
        
        # 停止所有内部任务
        await self.task_manager.stop_all_tasks()
        
        # 清理监控器
        for watcher in self.watchers:
            await watcher.stop()
        
        self.watchers.clear()
        self.is_running = False
        self.stats["tasks_running"] = 0
        
        logger.info("✅ 文件系统连接器禁用完成，所有内部任务已清理")
    
    async def reload_config(self, new_config: dict):
        """
        配置重载 - Session V54决策: 进程重启方式
        简化逻辑，避免复杂的热重载
        """
        logger.info("🔄 文件系统连接器配置重载 (进程重启方式)")
        
        was_running = self.is_running
        
        # 完全停止
        if was_running:
            await self.stop()
        
        # 更新配置
        self.config = new_config
        
        # 重新启动 (如果之前在运行)
        if was_running:
            await self.start()
        
        logger.info("✅ 配置重载完成")
    
    async def on_file_change(self, file_path: str, event_type: str, task_id: str):
        """
        文件变化回调 - 连接器内部处理并发送到daemon
        包含内部统计和错误处理
        """
        logger.debug(f"📄 检测到文件变化: {file_path} ({event_type}) [任务: {task_id}]")
        
        self.stats["changes_detected"] += 1
        self.stats["last_activity"] = datetime.now().isoformat()
        
        # 读取文件内容并发送给daemon
        if event_type in ["created", "modified"]:
            try:
                content = await self.read_file_content(file_path)
                
                # 内部数据处理和验证
                if not content or len(content.strip()) == 0:
                    logger.debug(f"跳过空文件: {file_path}")
                    return
                
                # 发送结构化数据到daemon
                entity_data = {
                    "entity_type": "document",
                    "title": Path(file_path).name,
                    "content": content,
                    "metadata": {
                        "source": "filesystem",
                        "connector_task_id": task_id,
                        "file_path": file_path,
                        "event_type": event_type,
                        "timestamp": datetime.now().isoformat(),
                        "file_size": len(content),
                        "connector_version": "1.0.0"
                    }
                }
                
                success = await self.send_to_daemon(entity_data)
                if success:
                    logger.debug(f"✅ 文件数据已发送: {file_path}")
                else:
                    logger.error(f"❌ 文件数据发送失败: {file_path}")
                    
            except Exception as e:
                logger.error(f"❌ 处理文件变化失败 {file_path}: {e}")
                # 内部错误计数
                self.stats.setdefault("errors", 0)
                self.stats["errors"] += 1
        
        elif event_type == "deleted":
            # 通知daemon删除实体
            await self.send_to_daemon({
                "action": "delete_entity",
                "metadata": {
                    "source": "filesystem",
                    "file_path": file_path,
                    "connector_task_id": task_id
                }
            })
    
    async def get_internal_status(self) -> dict:
        """
        获取连接器内部状态 - 用于监控和调试
        暴露内部任务的运行状况
        """
        task_statuses = await self.task_manager.get_all_task_statuses()
        
        return {
            "is_running": self.is_running,
            "total_tasks": len(self.watchers) + 1,  # +1 for health monitor
            "active_watchers": len([w for w in self.watchers if w.is_active()]),
            "monitored_paths": [w.path for w in self.watchers],
            "statistics": self.stats,
            "task_details": task_statuses,
            "config_hash": hash(str(self.config)),
            "memory_usage": await self.get_memory_usage()
        }

class TaskManager:
    """连接器内部任务管理器"""
    def __init__(self):
        self.tasks = {}
        
    async def register_task(self, task_id: str, task):
        self.tasks[task_id] = task
        
    async def stop_all_tasks(self):
        for task_id, task in self.tasks.items():
            try:
                await task.stop()
                logger.debug(f"停止内部任务: {task_id}")
            except Exception as e:
                logger.error(f"停止任务失败 {task_id}: {e}")
        self.tasks.clear()
        
    async def get_all_task_statuses(self):
        statuses = {}
        for task_id, task in self.tasks.items():
            statuses[task_id] = {
                "active": getattr(task, 'is_active', lambda: False)(),
                "type": type(task).__name__
            }
        return statuses

class HealthMonitor:
    """连接器内部健康监控任务"""
    def __init__(self, watchers, stats_callback):
        self.watchers = watchers
        self.stats_callback = stats_callback
        self.running = False
        
    async def start(self):
        self.running = True
        asyncio.create_task(self._monitor_loop())
        
    async def stop(self):
        self.running = False
        
    async def _monitor_loop(self):
        while self.running:
            try:
                # 更新文件监控统计
                total_files = sum(w.get_file_count() for w in self.watchers if hasattr(w, 'get_file_count'))
                await self.stats_callback({"files_monitored": total_files})
                
                await asyncio.sleep(30)  # 30秒检查一次
            except Exception as e:
                logger.error(f"健康监控错误: {e}")
                await asyncio.sleep(60)  # 错误时延长间隔
```

---

## 🎨 极简UI设计 (Session V55重构版)

### 📱 基于4个API端点的Flutter界面
```dart
// ultra_simplified_connector_screen.dart - Session V55重构版
class ConnectorManagementScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('连接器管理'),
        // 移除多余的商店按钮，集成到主界面
      ),
      body: Consumer<ConnectorProvider>(
        builder: (context, provider, child) {
          return RefreshIndicator(
            onRefresh: () => provider.refreshConnectors(), // 使用新的统一刷新方法
            child: CustomScrollView(
              slivers: [
                // 已安装连接器区域
                SliverToBoxAdapter(
                  child: _buildSectionHeader('已安装连接器', provider.installedCount),
                ),
                _buildInstalledConnectors(provider),
                
                // 可安装连接器区域 (如果有)
                if (provider.availableConnectors.isNotEmpty) ...[
                  SliverToBoxAdapter(
                    child: _buildSectionHeader('可安装连接器', provider.availableCount),
                  ),
                  _buildAvailableConnectors(provider),
                ],
                
                // 空状态处理
                if (provider.allConnectors.isEmpty)
                  SliverFillRemaining(
                    child: _buildEmptyState(),
                  ),
              ],
            ),
          );
        },
      ),
    );
  }
  
  Widget _buildSectionHeader(String title, int count) {
    return Padding(
      padding: EdgeInsets.all(16),
      child: Row(
        children: [
          Text(
            title,
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          SizedBox(width: 8),
          Chip(
            label: Text('$count'),
            materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
          ),
        ],
      ),
    );
  }
  
  Widget _buildInstalledConnectors(ConnectorProvider provider) {
    return SliverList(
      delegate: SliverChildBuilderDelegate(
        (context, index) {
          final connector = provider.installedConnectors[index];
          return ConnectorTile(
            connector: connector,
            isInstalled: true,
          );
        },
        childCount: provider.installedConnectors.length,
      ),
    );
  }
  
  Widget _buildAvailableConnectors(ConnectorProvider provider) {
    return SliverList(
      delegate: SliverChildBuilderDelegate(
        (context, index) {
          final connector = provider.availableConnectors[index];
          return ConnectorTile(
            connector: connector,
            isInstalled: false,
          );
        },
        childCount: provider.availableConnectors.length,
      ),
    );
  }
  
  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.extension_off, size: 64, color: Colors.grey),
          SizedBox(height: 16),
          Text('没有找到任何连接器'),
          SizedBox(height: 8),
          Text('请检查网络连接或联系管理员', style: TextStyle(color: Colors.grey)),
        ],
      ),
    );
  }
}

// 极简连接器卡片 - 支持已安装和可安装两种状态
class ConnectorTile extends StatelessWidget {
  final ConnectorInfo connector;
  final bool isInstalled;
  
  const ConnectorTile({
    Key? key, 
    required this.connector, 
    required this.isInstalled
  }) : super(key: key);
  
  @override
  Widget build(BuildContext context) {
    return Card(
      margin: EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      child: ListTile(
        leading: CircleAvatar(
          child: Icon(_getConnectorIcon(connector.id)),
          backgroundColor: _getConnectorColor(connector.status, isInstalled),
        ),
        title: Text(connector.name),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(connector.description ?? ''),
            SizedBox(height: 4),
            _buildStatusInfo(),
          ],
        ),
        trailing: _buildActions(context),
      ),
    );
  }
  
  Widget _buildStatusInfo() {
    if (!isInstalled) {
      return Chip(
        label: Text('可安装', style: TextStyle(color: Colors.white, fontSize: 12)),
        backgroundColor: Colors.blue,
        materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
      );
    }
    
    Color color;
    String text;
    
    switch (connector.status) {
      case 'running':
        color = Colors.green;
        text = '运行中';
        break;
      case 'stopped':
        color = Colors.grey;
        text = '已停止';
        break;
      case 'error':
        color = Colors.red;
        text = '错误';
        break;
      default:
        color = Colors.blue;
        text = '已安装';
    }
    
    return Chip(
      label: Text(text, style: TextStyle(color: Colors.white, fontSize: 12)),
      backgroundColor: color,
      materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
    );
  }
  
  Widget _buildActions(BuildContext context) {
    if (!isInstalled) {
      // 未安装连接器: 只有安装按钮
      return ElevatedButton.icon(
        icon: Icon(Icons.download, size: 16),
        label: Text('安装'),
        onPressed: () => _installConnector(context),
        style: ElevatedButton.styleFrom(
          padding: EdgeInsets.symmetric(horizontal: 12, vertical: 4),
        ),
      );
    }
    
    // 已安装连接器: 启用/禁用开关 + 配置按钮 + 更多菜单
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        // 启用/禁用开关 (使用新的toggle API)
        Switch(
          value: connector.enabled,
          onChanged: connector.status == 'error' 
            ? null 
            : (enabled) => _toggleConnector(context, enabled),
        ),
        // 配置按钮
        IconButton(
          icon: Icon(Icons.settings, size: 20),
          onPressed: () => _showConfigDialog(context),
          padding: EdgeInsets.all(4),
          constraints: BoxConstraints(),
        ),
        // 更多操作菜单
        PopupMenuButton<String>(
          padding: EdgeInsets.zero,
          icon: Icon(Icons.more_vert, size: 20),
          onSelected: (action) => _handleMenuAction(context, action),
          itemBuilder: (context) => [
            PopupMenuItem(
              value: 'details',
              child: Row(
                children: [
                  Icon(Icons.info_outline, size: 16),
                  SizedBox(width: 8),
                  Text('详情'),
                ],
              ),
            ),
            PopupMenuItem(
              value: 'uninstall',
              child: Row(
                children: [
                  Icon(Icons.delete_outline, color: Colors.red, size: 16),
                  SizedBox(width: 8),
                  Text('卸载', style: TextStyle(color: Colors.red)),
                ],
              ),
            ),
          ],
        ),
      ],
    );
  }
  
  // Session V55的API调用方法
  Future<void> _installConnector(BuildContext context) async {
    try {
      final provider = context.read<ConnectorProvider>();
      
      // 显示加载状态
      showDialog(
        context: context,
        barrierDismissible: false,
        builder: (context) => AlertDialog(
          content: Row(
            children: [
              CircularProgressIndicator(),
              SizedBox(width: 16),
              Text('正在安装 ${connector.name}...'),
            ],
          ),
        ),
      );
      
      // 调用新的统一安装API: PUT /{connector_id}/config
      await provider.installConnector(
        connector.id, 
        version: connector.version,
        initialConfig: {}
      );
      
      Navigator.of(context).pop(); // 关闭加载对话框
      
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('${connector.name} 安装成功')),
      );
      
    } catch (e) {
      Navigator.of(context).pop(); // 关闭加载对话框
      
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('安装失败: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }
  
  Future<void> _toggleConnector(BuildContext context, bool enabled) async {
    try {
      final provider = context.read<ConnectorProvider>();
      
      // 调用新的统一切换API: POST /{connector_id}/toggle
      await provider.toggleConnector(connector.id, enabled);
      
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('${connector.name} ${enabled ? "已启用" : "已禁用"}'),
        ),
      );
      
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('操作失败: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }
  
  Future<void> _showConfigDialog(BuildContext context) async {
    try {
      final provider = context.read<ConnectorProvider>();
      
      // 调用新的统一配置API: GET /{connector_id}/config
      final configData = await provider.getConnectorConfig(connector.id);
      
      showDialog(
        context: context,
        builder: (context) => ConnectorConfigDialog(
          connector: connector,
          configData: configData,
        ),
      );
      
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('获取配置失败: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }
  
  Future<void> _handleMenuAction(BuildContext context, String action) async {
    switch (action) {
      case 'details':
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) => ConnectorDetailsScreen(connector: connector),
          ),
        );
        break;
        
      case 'uninstall':
        final confirmed = await showDialog<bool>(
          context: context,
          builder: (context) => AlertDialog(
            title: Text('确认卸载'),
            content: Text('确定要卸载 ${connector.name} 吗？这将删除所有相关数据。'),
            actions: [
              TextButton(
                onPressed: () => Navigator.of(context).pop(false),
                child: Text('取消'),
              ),
              TextButton(
                onPressed: () => Navigator.of(context).pop(true),
                child: Text('卸载', style: TextStyle(color: Colors.red)),
              ),
            ],
          ),
        );
        
        if (confirmed == true) {
          await _uninstallConnector(context);
        }
        break;
    }
  }
  
  Future<void> _uninstallConnector(BuildContext context) async {
    try {
      final provider = context.read<ConnectorProvider>();
      
      // 调用新的统一卸载API: PUT /{connector_id}/config with action=uninstall
      await provider.uninstallConnector(connector.id);
      
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('${connector.name} 卸载成功')),
      );
      
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('卸载失败: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }
  
  IconData _getConnectorIcon(String connectorId) {
    switch (connectorId) {
      case 'filesystem':
        return Icons.folder;
      case 'clipboard':
        return Icons.content_paste;
      case 'browser':
        return Icons.web;
      case 'email':
        return Icons.email;
      default:
        return Icons.extension;
    }
  }
  
  Color _getConnectorColor(String status, bool isInstalled) {
    if (!isInstalled) return Colors.blue;
    
    switch (status) {
      case 'running':
        return Colors.green;
      case 'stopped':
        return Colors.grey;
      case 'error':
        return Colors.red;
      default:
        return Colors.blue;
    }
  }
}

// 连接器信息数据模型 (对应新的API响应)
class ConnectorInfo {
  final String id;
  final String name;
  final String version;
  final String status;
  final bool enabled;
  final bool installed;
  final String? description;
  final String installSource;
  
  ConnectorInfo({
    required this.id,
    required this.name,
    required this.version,
    required this.status,
    required this.enabled,
    required this.installed,
    this.description,
    required this.installSource,
  });
  
  factory ConnectorInfo.fromJson(Map<String, dynamic> json) {
    return ConnectorInfo(
      id: json['id'],
      name: json['name'],
      version: json['version'],
      status: json['status'],
      enabled: json['enabled'] ?? false,
      installed: json['installed'] ?? false,
      description: json['description'],
      installSource: json['install_source'] ?? 'unknown',
    );
  }
}
```

---

## 🚀 Session V55实施计划 (基于架构重构)

### 🔴 Phase 1: 核心架构重构 (当前session - 立即行动)
1. **✅ 文档重构完成**: 
   - ✅ 更新连接器架构设计文档
   - ✅ API端点从8个简化到4个核心端点
   - ✅ 数据模型简化，移除实例概念
   - ✅ 连接器内部自管理标准制定

2. **🔴 代码重构规划**:
   - 重构Daemon连接器管理模块
   - 实现4个核心API端点
   - 更新连接器基类架构
   - 重构filesystem连接器作为示例

### 🟡 Phase 2: 代码实施 (后续sessions)
1. **API层重构** (Session V56):
   - 实现新的4个核心API端点
   - 删除旧的复杂API端点
   - 更新数据模型和验证逻辑

2. **连接器重构** (Session V57):
   - 重构filesystem连接器实现内部自管理
   - 更新clipboard连接器
   - 建立连接器开发标准

3. **UI层重构** (Session V58):
   - 实现基于新API的Flutter界面
   - 统一连接器管理体验
   - 删除旧的复杂UI组件

### 🟢 Phase 3: 验证和优化 (Session V59-V60)
1. **集成测试**:
   - 端到端连接器生命周期测试
   - 配置更新和重启逻辑验证
   - 错误处理和恢复机制测试

2. **性能优化**:
   - 连接器启动速度优化
   - 内存使用和资源清理
   - API响应时间优化

3. **用户体验验证**:
   - 连接器安装/卸载流程
   - 配置界面易用性
   - 错误信息和帮助文档

### 📊 成功指标

#### 🎯 架构简化指标
- **API复杂度降低**: 从8个端点减少到4个 (50%减少)
- **代码行数减少**: Daemon连接器管理代码减少60%+
- **概念简化**: 完全移除"实例"概念，用户理解成本降低

#### 🚀 开发效率指标
- **新连接器开发时间**: 从3天减少到1天
- **bug修复时间**: 连接器相关bug修复时间减少50%
- **维护成本**: 月度维护时间减少70%

#### 👤 用户体验指标
- **操作简化**: 连接器管理操作步骤减少60%
- **理解难度**: 用户对连接器概念的理解时间从30分钟减少到5分钟
- **错误率**: 连接器配置错误率减少80%

---

## 💡 Session V54决策核心原则

### 🎯 **极简至上** (基于Session V54深度协商)
```
❌ 废弃思维: 系统需要管理连接器的复杂内部逻辑
✅ 采用思维: 连接器最懂自己，系统只做启停和配置分发
```

### 🔧 **连接器自治** (Session V54核心洞察)
```
系统职责: 安装 → 启用/禁用 → 配置分发 → 卸载
连接器职责: 解析配置 → 创建内部任务 → 管理资源 → 数据处理

边界清晰，职责分离，维护简单
```

### 📱 **配置更新=进程重启** (Session V54关键简化)
```
❌ 复杂热重载: 配置更新 → 内部状态同步 → 增量任务管理
✅ 简化重启: 配置更新 → 停止进程 → 更新配置 → 重启进程

虽然有短暂中断，但逻辑简单可靠，维护成本极低
```

### 🎨 **用户视角优先**
```
用户看到的连接器管理界面:
- filesystem连接器 [🟢启用] [⚙️配置] [🗑️卸载]
- 配置界面: 监控路径 + 文件类型 + 忽略规则
- 状态显示: 正在监控142个文件，今日处理23个变化

用户不需要知道内部有多少个watcher任务在运行
```

---

## 🔍 Session V55架构重构总结

### ✅ 重大简化成果
1. **API端点**: 从8个减少到4个，减少50%复杂度
2. **数据模型**: 移除实例概念，简化60%+
3. **用户界面**: 统一连接器管理，删除混淆概念
4. **连接器开发**: 标准化内部自管理模式

### 🎯 关键架构决策
1. **GET /connectors/list**: 统一列出已安装和可安装连接器
2. **POST /connectors/{id}/toggle**: 统一启用/禁用操作
3. **GET /connectors/{id}/config**: 统一配置和状态查询
4. **PUT /connectors/{id}/config**: 统一配置更新/安装/卸载

### 🚀 实施准备就绪
- 详细的API设计和实现代码
- 连接器内部自管理架构标准
- Flutter UI重构完整方案
- 分阶段实施计划和成功指标

**Session V55目标达成**: 架构文档重构完成，为后续代码实施提供清晰指导!