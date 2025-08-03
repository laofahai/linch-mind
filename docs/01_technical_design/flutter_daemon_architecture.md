# Flutter Daemon架构设计

**版本**: 1.0  
**状态**: 设计中  
**创建时间**: 2025-08-02  
**基于**: Flutter迁移后的Daemon重新设计

## 1. 概述

Flutter迁移为我们提供了重新设计Daemon架构的绝佳机会。新的Dart HTTP Daemon不仅简化了技术栈，还解决了连接器插件的语言限制问题，实现了真正的多语言插件生态系统。

### 1.1 核心设计优势

**语言无关的插件系统**:
- Daemon作为统一的插件执行环境
- 支持任何语言编写的连接器插件
- UI端专注于管理和配置，不直接执行插件逻辑
- 插件通过标准接口（HTTP/进程/文件）与Daemon通信

**架构分离的清晰边界**:
- **UI端**: 插件管理、配置界面、状态展示
- **Daemon端**: 插件执行、数据处理、业务逻辑
- **插件**: 独立进程、任意语言、标准接口

## 2. Daemon核心架构

### 2.1 整体架构图
```
┌─────────────────────────────────────────────────────────┐
│                  Flutter UI Application                │
│  ┌─────────────────────────────────────────────────────┐ │
│  │           Connector Management UI                   │ │
│  │  ├── ConnectorListScreen                           │ │
│  │  ├── ConnectorConfigScreen                         │ │
│  │  ├── ConnectorStatusCard                           │ │
│  │  └── ConnectorLogsViewer                           │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                              ↕ HTTP REST API
┌─────────────────────────────────────────────────────────┐
│              Dart HTTP Daemon (Core Engine)            │
│  ┌─────────────────────────────────────────────────────┐ │
│  │                REST API Layer                       │ │
│  │  ├── GET  /api/v1/connectors                       │ │
│  │  ├── POST /api/v1/connectors/{id}/start            │ │
│  │  ├── POST /api/v1/connectors/{id}/stop             │ │
│  │  ├── PUT  /api/v1/connectors/{id}/config           │ │
│  │  └── GET  /api/v1/connectors/{id}/status           │ │
│  └─────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────┐ │
│  │             Plugin Execution Engine                 │ │
│  │  ├── PluginProcessManager                          │ │
│  │  ├── PluginLifecycleManager                        │ │
│  │  ├── PluginCommunicationBridge                     │ │
│  │  └── PluginHealthMonitor                           │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                    ↕ Multi-Protocol Communication
┌─────────────────────────────────────────────────────────┐
│              Multi-Language Plugin Ecosystem           │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐  │
│  │ Python Plugin│ │ Node.js Plugin│ │ Rust Plugin      │  │
│  │ ──────────── │ │ ──────────────│ │ ──────────────── │  │
│  │ Obsidian     │ │ Slack         │ │ SystemMonitor    │  │
│  │ Connector    │ │ Connector     │ │ Connector        │  │
│  └──────────────┘ └──────────────┘ └──────────────────┘  │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐  │
│  │ Go Plugin    │ │ Bash Script   │ │ Java Plugin      │  │
│  │ ──────────── │ │ ──────────────│ │ ──────────────── │  │
│  │ Git          │ │ FileSystem    │ │ JetBrains        │  │
│  │ Connector    │ │ Watcher       │ │ IDE Connector    │  │
│  └──────────────┘ └──────────────┘ └──────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 2.2 插件执行引擎
```dart
class PluginExecutionEngine {
  final Map<String, PluginProcess> runningPlugins = {};
  final PluginRegistry registry;
  final PluginCommunicationBridge communicationBridge;
  
  PluginExecutionEngine({
    required this.registry,
    required this.communicationBridge,
  });
  
  /// 启动插件
  Future<void> startPlugin(String pluginId) async {
    final plugin = registry.getPlugin(pluginId);
    if (plugin == null) {
      throw PluginNotFoundException(pluginId);
    }
    
    // 根据插件类型选择启动方式
    final process = await _createPluginProcess(plugin);
    await process.start();
    
    // 建立通信桥梁
    await communicationBridge.establishConnection(pluginId, process);
    
    runningPlugins[pluginId] = process;
    
    logger.info('Plugin started: $pluginId (${plugin.language})');
  }
  
  /// 停止插件
  Future<void> stopPlugin(String pluginId) async {
    final process = runningPlugins[pluginId];
    if (process == null) return;
    
    try {
      // 优雅关闭
      await process.sendCommand(PluginCommand.shutdown());
      await process.waitForExit(timeout: Duration(seconds: 10));
    } catch (e) {
      // 强制终止
      await process.kill();
    } finally {
      runningPlugins.remove(pluginId);
      await communicationBridge.closeConnection(pluginId);
    }
    
    logger.info('Plugin stopped: $pluginId');
  }
  
  /// 根据插件类型创建对应的进程
  Future<PluginProcess> _createPluginProcess(PluginDefinition plugin) async {
    switch (plugin.runtime) {
      case PluginRuntime.python:
        return PythonPluginProcess(plugin);
      case PluginRuntime.nodejs:
        return NodeJSPluginProcess(plugin);
      case PluginRuntime.executable:
        return ExecutablePluginProcess(plugin);
      case PluginRuntime.script:
        return ScriptPluginProcess(plugin);
      default:
        throw UnsupportedPluginRuntimeException(plugin.runtime);
    }
  }
}
```

## 3. 多语言插件系统

### 3.1 插件接口标准化
所有插件都必须实现统一的接口，无论使用什么语言编写：

```json
// Plugin Manifest (plugin.json)
{
  "id": "obsidian-connector",
  "name": "Obsidian Vault Connector",
  "version": "1.0.0",
  "description": "Connects to Obsidian vault and monitors changes",
  "author": "Linch Mind Team",
  "runtime": "python",
  "entry_point": "main.py",
  "dependencies": {
    "python": ">=3.8",
    "packages": ["watchdog", "requests", "pyyaml"]
  },
  "communication": {
    "protocol": "http",
    "port": "auto",
    "heartbeat_interval": 30
  },
  "permissions": [
    "file_system_read",
    "file_system_watch",
    "network_outbound"
  ],
  "configuration_schema": {
    "type": "object",
    "properties": {
      "vault_path": {
        "type": "string",
        "description": "Path to Obsidian vault"
      },
      "watch_extensions": {
        "type": "array",
        "items": {"type": "string"},
        "default": [".md"]
      }
    },
    "required": ["vault_path"]
  }
}
```

### 3.2 通信协议设计
```dart
// 统一的插件通信接口
abstract class PluginCommunicationProtocol {
  Future<void> sendCommand(String pluginId, PluginCommand command);
  Future<PluginResponse> sendQuery(String pluginId, PluginQuery query);
  Stream<PluginEvent> listenToEvents(String pluginId);
}

// HTTP通信实现
class HTTPPluginCommunication implements PluginCommunicationProtocol {
  final Map<String, String> pluginBaseUrls = {};
  final Dio httpClient = Dio();
  
  @override
  Future<void> sendCommand(String pluginId, PluginCommand command) async {
    final baseUrl = pluginBaseUrls[pluginId];
    if (baseUrl == null) throw PluginNotConnectedException(pluginId);
    
    await httpClient.post(
      '$baseUrl/command',
      data: command.toJson(),
    );
  }
  
  @override
  Future<PluginResponse> sendQuery(String pluginId, PluginQuery query) async {
    final baseUrl = pluginBaseUrls[pluginId];
    if (baseUrl == null) throw PluginNotConnectedException(pluginId);
    
    final response = await httpClient.post(
      '$baseUrl/query',
      data: query.toJson(),
    );
    
    return PluginResponse.fromJson(response.data);
  }
}

// 进程间通信实现
class IPCPluginCommunication implements PluginCommunicationProtocol {
  final Map<String, Process> pluginProcesses = {};
  
  @override
  Future<void> sendCommand(String pluginId, PluginCommand command) async {
    final process = pluginProcesses[pluginId];
    if (process == null) throw PluginNotConnectedException(pluginId);
    
    // 通过stdin发送JSON消息
    process.stdin.writeln(jsonEncode(command.toJson()));
  }
}
```

### 3.3 多语言插件实现示例

#### Python插件示例
```python
#!/usr/bin/env python3
# obsidian_connector/main.py

import json
import time
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from flask import Flask, request, jsonify
import threading

class ObsidianConnector:
    def __init__(self, config):
        self.config = config
        self.vault_path = Path(config['vault_path'])
        self.app = Flask(__name__)
        self.setup_routes()
        self.observer = None
        
    def setup_routes(self):
        @self.app.route('/command', methods=['POST'])
        def handle_command():
            command = request.json
            return self.process_command(command)
            
        @self.app.route('/query', methods=['POST'])
        def handle_query():
            query = request.json
            return self.process_query(query)
            
        @self.app.route('/health', methods=['GET'])
        def health_check():
            return jsonify({'status': 'healthy', 'timestamp': time.time()})
    
    def process_command(self, command):
        cmd_type = command.get('type')
        
        if cmd_type == 'start_monitoring':
            self.start_file_monitoring()
            return jsonify({'success': True})
        elif cmd_type == 'stop_monitoring':
            self.stop_file_monitoring()
            return jsonify({'success': True})
        elif cmd_type == 'shutdown':
            self.shutdown()
            return jsonify({'success': True})
        else:
            return jsonify({'error': f'Unknown command: {cmd_type}'}), 400
    
    def process_query(self, query):
        query_type = query.get('type')
        
        if query_type == 'scan_vault':
            files = self.scan_vault_files()
            return jsonify({'files': files})
        elif query_type == 'get_file_content':
            file_path = query.get('file_path')
            content = self.get_file_content(file_path)
            return jsonify({'content': content})
        else:
            return jsonify({'error': f'Unknown query: {query_type}'}), 400
    
    def start_file_monitoring(self):
        if self.observer is None:
            event_handler = VaultFileHandler(self)
            self.observer = Observer()
            self.observer.schedule(event_handler, str(self.vault_path), recursive=True)
            self.observer.start()
            logging.info(f"Started monitoring {self.vault_path}")
    
    def scan_vault_files(self):
        files = []
        for md_file in self.vault_path.rglob('*.md'):
            files.append({
                'path': str(md_file),
                'name': md_file.name,
                'modified': md_file.stat().st_mtime,
                'size': md_file.stat().st_size
            })
        return files

class VaultFileHandler(FileSystemEventHandler):
    def __init__(self, connector):
        self.connector = connector
    
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('.md'):
            # 通知Daemon有文件变更
            self.notify_daemon('file_modified', {
                'path': event.src_path,
                'timestamp': time.time()
            })
    
    def notify_daemon(self, event_type, data):
        # 发送事件到Daemon
        # 可以通过webhook、消息队列或其他方式
        pass

if __name__ == '__main__':
    # 读取配置
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    # 启动连接器
    connector = ObsidianConnector(config)
    connector.app.run(host='localhost', port=config.get('port', 0))
```

#### Node.js插件示例
```javascript
// slack_connector/index.js

const express = require('express');
const { WebClient } = require('@slack/web-api');
const fs = require('fs').promises;

class SlackConnector {
    constructor(config) {
        this.config = config;
        this.app = express();
        this.slack = new WebClient(config.bot_token);
        this.setupRoutes();
    }
    
    setupRoutes() {
        this.app.use(express.json());
        
        this.app.post('/command', (req, res) => {
            this.handleCommand(req.body)
                .then(result => res.json(result))
                .catch(error => res.status(500).json({error: error.message}));
        });
        
        this.app.post('/query', (req, res) => {
            this.handleQuery(req.body)
                .then(result => res.json(result))
                .catch(error => res.status(500).json({error: error.message}));
        });
        
        this.app.get('/health', (req, res) => {
            res.json({status: 'healthy', timestamp: Date.now()});
        });
    }
    
    async handleCommand(command) {
        switch (command.type) {
            case 'start_monitoring':
                await this.startMessageMonitoring();
                return {success: true};
            case 'send_message':
                await this.sendMessage(command.channel, command.text);
                return {success: true};
            case 'shutdown':
                this.shutdown();
                return {success: true};
            default:
                throw new Error(`Unknown command: ${command.type}`);
        }
    }
    
    async handleQuery(query) {
        switch (query.type) {
            case 'get_channels':
                const channels = await this.getChannels();
                return {channels};
            case 'get_messages':
                const messages = await this.getMessages(query.channel, query.limit);
                return {messages};
            default:
                throw new Error(`Unknown query: ${query.type}`);
        }
    }
    
    async getChannels() {
        const result = await this.slack.conversations.list();
        return result.channels.map(channel => ({
            id: channel.id,
            name: channel.name,
            is_private: channel.is_private
        }));
    }
    
    async getMessages(channelId, limit = 50) {
        const result = await this.slack.conversations.history({
            channel: channelId,
            limit: limit
        });
        
        return result.messages.map(message => ({
            user: message.user,
            text: message.text,
            timestamp: message.ts
        }));
    }
    
    async startMessageMonitoring() {
        // 使用Slack RTM API或Socket Mode监听实时消息
        // 这里简化实现
        console.log('Started Slack message monitoring');
    }
    
    start(port) {
        this.server = this.app.listen(port, () => {
            console.log(`Slack Connector running on port ${port}`);
        });
    }
    
    shutdown() {
        if (this.server) {
            this.server.close();
        }
        process.exit(0);
    }
}

// 启动连接器
async function main() {
    const config = JSON.parse(await fs.readFile('config.json', 'utf8'));
    const connector = new SlackConnector(config);
    connector.start(config.port || 0);
}

main().catch(console.error);
```

#### Rust插件示例
```rust
// system_monitor/src/main.rs

use serde::{Deserialize, Serialize};
use tokio::net::TcpListener;
use warp::Filter;
use sysinfo::{System, SystemExt, CpuExt, DiskExt};
use std::collections::HashMap;

#[derive(Debug, Deserialize)]
struct PluginCommand {
    #[serde(rename = "type")]
    command_type: String,
    data: Option<serde_json::Value>,
}

#[derive(Debug, Serialize)]
struct PluginResponse {
    success: bool,
    data: Option<serde_json::Value>,
    error: Option<String>,
}

#[derive(Debug, Deserialize)]
struct PluginQuery {
    #[serde(rename = "type")]
    query_type: String,
    params: Option<HashMap<String, serde_json::Value>>,
}

struct SystemMonitorConnector {
    system: System,
}

impl SystemMonitorConnector {
    fn new() -> Self {
        Self {
            system: System::new_all(),
        }
    }
    
    fn handle_command(&mut self, command: PluginCommand) -> PluginResponse {
        match command.command_type.as_str() {
            "start_monitoring" => {
                // 启动系统监控
                PluginResponse {
                    success: true,
                    data: None,
                    error: None,
                }
            }
            "stop_monitoring" => {
                // 停止系统监控
                PluginResponse {
                    success: true,
                    data: None,
                    error: None,
                }
            }
            _ => PluginResponse {
                success: false,
                data: None,
                error: Some(format!("Unknown command: {}", command.command_type)),
            }
        }
    }
    
    fn handle_query(&mut self, query: PluginQuery) -> PluginResponse {
        self.system.refresh_all();
        
        match query.query_type.as_str() {
            "get_system_info" => {
                let info = serde_json::json!({
                    "os": System::name(),
                    "kernel_version": System::kernel_version(),
                    "total_memory": self.system.total_memory(),
                    "used_memory": self.system.used_memory(),
                    "cpu_count": self.system.cpus().len(),
                    "cpu_usage": self.system.global_cpu_info().cpu_usage(),
                });
                
                PluginResponse {
                    success: true,
                    data: Some(info),
                    error: None,
                }
            }
            "get_disk_usage" => {
                let disks: Vec<_> = self.system.disks().iter().map(|disk| {
                    serde_json::json!({
                        "name": disk.name().to_string_lossy(),
                        "mount_point": disk.mount_point().to_string_lossy(),
                        "total_space": disk.total_space(),
                        "available_space": disk.available_space(),
                        "file_system": String::from_utf8_lossy(disk.file_system()),
                    })
                }).collect();
                
                PluginResponse {
                    success: true,
                    data: Some(serde_json::json!({"disks": disks})),
                    error: None,
                }
            }
            _ => PluginResponse {
                success: false,
                data: None,
                error: Some(format!("Unknown query: {}", query.query_type)),
            }
        }
    }
}

#[tokio::main]
async fn main() {
    let mut connector = SystemMonitorConnector::new();
    
    let command_route = warp::path("command")
        .and(warp::post())
        .and(warp::body::json())
        .map(move |command: PluginCommand| {
            let response = connector.handle_command(command);
            warp::reply::json(&response)
        });
    
    let query_route = warp::path("query")
        .and(warp::post())
        .and(warp::body::json())
        .map(move |query: PluginQuery| {
            let response = connector.handle_query(query);
            warp::reply::json(&response)
        });
    
    let health_route = warp::path("health")
        .and(warp::get())
        .map(|| {
            warp::reply::json(&serde_json::json!({
                "status": "healthy",
                "timestamp": chrono::Utc::now().timestamp()
            }))
        });
    
    let routes = command_route.or(query_route).or(health_route);
    
    println!("System Monitor Connector starting on port 3030");
    warp::serve(routes).run(([127, 0, 0, 1], 3030)).await;
}
```

## 4. UI端插件管理

### 4.1 Flutter插件管理界面
```dart
// lib/screens/connector_management_screen.dart

class ConnectorManagementScreen extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final connectors = ref.watch(connectorsProvider);
    
    return Scaffold(
      appBar: AppBar(
        title: Text('连接器管理'),
        actions: [
          IconButton(
            icon: Icon(Icons.add),
            onPressed: () => _showAddConnectorDialog(context),
          ),
        ],
      ),
      body: connectors.when(
        data: (connectorList) => ListView.builder(
          itemCount: connectorList.length,
          itemBuilder: (context, index) {
            final connector = connectorList[index];
            return ConnectorCard(connector: connector);
          },
        ),
        loading: () => Center(child: CircularProgressIndicator()),
        error: (error, stack) => Center(
          child: Text('加载连接器失败: $error'),
        ),
      ),
    );
  }
}

class ConnectorCard extends ConsumerWidget {
  final ConnectorInfo connector;
  
  const ConnectorCard({required this.connector});
  
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Card(
      margin: EdgeInsets.all(8),
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        connector.name,
                        style: Theme.of(context).textTheme.titleLarge,
                      ),
                      Text(
                        connector.description,
                        style: Theme.of(context).textTheme.bodyMedium,
                      ),
                      SizedBox(height: 8),
                      Row(
                        children: [
                          _buildStatusIndicator(connector.status),
                          SizedBox(width: 8),
                          Text('${connector.runtime} • v${connector.version}'),
                        ],
                      ),
                    ],
                  ),
                ),
                Column(
                  children: [
                    Switch(
                      value: connector.isEnabled,
                      onChanged: (value) {
                        ref.read(connectorsProvider.notifier)
                           .toggleConnector(connector.id, value);
                      },
                    ),
                    PopupMenuButton<String>(
                      onSelected: (action) => _handleConnectorAction(
                        context, ref, connector, action
                      ),
                      itemBuilder: (context) => [
                        PopupMenuItem(
                          value: 'configure',
                          child: Text('配置'),
                        ),
                        PopupMenuItem(
                          value: 'logs',
                          child: Text('查看日志'),
                        ),
                        PopupMenuItem(
                          value: 'restart',
                          child: Text('重启'),
                        ),
                        PopupMenuItem(
                          value: 'uninstall',
                          child: Text('卸载'),
                        ),
                      ],
                    ),
                  ],
                ),
              ],
            ),
            if (connector.isRunning) ...[
              SizedBox(height: 16),
              _buildConnectorStats(connector),
            ],
          ],
        ),
      ),
    );
  }
  
  Widget _buildStatusIndicator(ConnectorStatus status) {
    Color color;
    IconData icon;
    String text;
    
    switch (status) {
      case ConnectorStatus.running:
        color = Colors.green;
        icon = Icons.play_circle;
        text = '运行中';
        break;
      case ConnectorStatus.stopped:
        color = Colors.grey;
        icon = Icons.stop_circle;
        text = '已停止';
        break;
      case ConnectorStatus.error:
        color = Colors.red;
        icon = Icons.error;
        text = '错误';
        break;
      case ConnectorStatus.starting:
        color = Colors.orange;
        icon = Icons.refresh;
        text = '启动中';
        break;
    }
    
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, color: color, size: 16),
        SizedBox(width: 4),
        Text(text, style: TextStyle(color: color)),
      ],
    );
  }
  
  Widget _buildConnectorStats(ConnectorInfo connector) {
    return Container(
      padding: EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.grey[50],
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          _buildStatItem('数据收集', '${connector.stats.itemsCollected}'),
          _buildStatItem('运行时间', _formatUptime(connector.stats.uptime)),
          _buildStatItem('最后活动', _formatLastActivity(connector.stats.lastActivity)),
        ],
      ),
    );
  }
}
```

### 4.2 插件配置界面
```dart
// lib/screens/connector_config_screen.dart

class ConnectorConfigScreen extends ConsumerStatefulWidget {
  final String connectorId;
  
  const ConnectorConfigScreen({required this.connectorId});
  
  @override
  ConsumerState<ConnectorConfigScreen> createState() => _ConnectorConfigScreenState();
}

class _ConnectorConfigScreenState extends ConsumerState<ConnectorConfigScreen> {
  late Map<String, dynamic> _config;
  late Map<String, dynamic> _schema;
  bool _loading = true;
  
  @override
  void initState() {
    super.initState();
    _loadConnectorConfig();
  }
  
  Future<void> _loadConnectorConfig() async {
    try {
      final connector = await ref.read(daemonClientProvider)
          .getConnectorDetails(widget.connectorId);
      
      setState(() {
        _config = Map<String, dynamic>.from(connector.config);
        _schema = connector.configSchema;
        _loading = false;
      });
    } catch (e) {
      // 处理错误
      setState(() => _loading = false);
    }
  }
  
  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return Scaffold(
        appBar: AppBar(title: Text('配置连接器')),
        body: Center(child: CircularProgressIndicator()),
      );
    }
    
    return Scaffold(
      appBar: AppBar(
        title: Text('配置连接器'),
        actions: [
          TextButton(
            onPressed: _saveConfig,
            child: Text('保存'),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: EdgeInsets.all(16),
        child: _buildConfigForm(),
      ),
    );
  }
  
  Widget _buildConfigForm() {
    return ConfigFormBuilder(
      schema: _schema,
      config: _config,
      onConfigChanged: (newConfig) {
        setState(() {
          _config = newConfig;
        });
      },
    );
  }
  
  Future<void> _saveConfig() async {
    try {
      await ref.read(daemonClientProvider)
          .updateConnectorConfig(widget.connectorId, _config);
      
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('配置已保存')),
      );
      
      Navigator.of(context).pop();
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('保存失败: $e')),
      );
    }
  }
}

// 通用配置表单构建器
class ConfigFormBuilder extends StatelessWidget {
  final Map<String, dynamic> schema;
  final Map<String, dynamic> config;
  final Function(Map<String, dynamic>) onConfigChanged;
  
  const ConfigFormBuilder({
    required this.schema,
    required this.config,
    required this.onConfigChanged,
  });
  
  @override
  Widget build(BuildContext context) {
    final properties = schema['properties'] as Map<String, dynamic>? ?? {};
    
    return Column(
      children: properties.entries.map((entry) {
        return _buildFieldWidget(entry.key, entry.value);
      }).toList(),
    );
  }
  
  Widget _buildFieldWidget(String fieldName, Map<String, dynamic> fieldSchema) {
    final fieldType = fieldSchema['type'] as String;
    final fieldDescription = fieldSchema['description'] as String?;
    final currentValue = config[fieldName];
    
    switch (fieldType) {
      case 'string':
        return Padding(
          padding: EdgeInsets.only(bottom: 16),
          child: TextFormField(
            initialValue: currentValue?.toString() ?? '',
            decoration: InputDecoration(
              labelText: fieldName,
              helperText: fieldDescription,
              border: OutlineInputBorder(),
            ),
            onChanged: (value) {
              final newConfig = Map<String, dynamic>.from(config);
              newConfig[fieldName] = value;
              onConfigChanged(newConfig);
            },
          ),
        );
      
      case 'boolean':
        return Padding(
          padding: EdgeInsets.only(bottom: 16),
          child: SwitchListTile(
            title: Text(fieldName),
            subtitle: fieldDescription != null ? Text(fieldDescription) : null,
            value: currentValue == true,
            onChanged: (value) {
              final newConfig = Map<String, dynamic>.from(config);
              newConfig[fieldName] = value;
              onConfigChanged(newConfig);
            },
          ),
        );
      
      case 'array':
        return _buildArrayField(fieldName, fieldSchema, currentValue);
      
      default:
        return Text('Unsupported field type: $fieldType');
    }
  }
  
  Widget _buildArrayField(String fieldName, Map<String, dynamic> fieldSchema, dynamic currentValue) {
    final items = (currentValue as List<dynamic>?) ?? [];
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(fieldName, style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            IconButton(
              icon: Icon(Icons.add),
              onPressed: () {
                final newConfig = Map<String, dynamic>.from(config);
                final newItems = List<dynamic>.from(items)..add('');
                newConfig[fieldName] = newItems;
                onConfigChanged(newConfig);
              },
            ),
          ],
        ),
        ...items.asMap().entries.map((entry) {
          final index = entry.key;
          final value = entry.value;
          
          return Padding(
            padding: EdgeInsets.only(bottom: 8),
            child: Row(
              children: [
                Expanded(
                  child: TextFormField(
                    initialValue: value.toString(),
                    onChanged: (newValue) {
                      final newConfig = Map<String, dynamic>.from(config);
                      final newItems = List<dynamic>.from(items);
                      newItems[index] = newValue;
                      newConfig[fieldName] = newItems;
                      onConfigChanged(newConfig);
                    },
                  ),
                ),
                IconButton(
                  icon: Icon(Icons.remove),
                  onPressed: () {
                    final newConfig = Map<String, dynamic>.from(config);
                    final newItems = List<dynamic>.from(items)..removeAt(index);
                    newConfig[fieldName] = newItems;
                    onConfigChanged(newConfig);
                  },
                ),
              ],
            ),
          );
        }).toList(),
        SizedBox(height: 16),
      ],
    );
  }
}
```

## 5. 优势总结

### 5.1 技术优势
1. **语言自由**: 插件可用任何语言编写，选择最适合的技术栈
2. **隔离性**: 每个插件独立进程，故障隔离，不影响核心系统
3. **标准化**: 统一的插件接口和通信协议
4. **可扩展**: 轻松添加新的插件类型和通信方式
5. **维护性**: UI和逻辑完全分离，各自独立维护

### 5.2 开发优势
1. **专业化**: 每个插件可以使用最适合的语言和库
2. **团队协作**: 不同团队可以并行开发不同插件
3. **测试独立**: 插件可以独立测试，不依赖主应用
4. **部署灵活**: 插件可以独立更新和部署

### 5.3 用户体验优势
1. **丰富生态**: 支持更多种类的数据源和服务
2. **配置简单**: UI提供直观的插件管理和配置界面
3. **状态透明**: 实时显示插件运行状态和统计信息
4. **故障恢复**: 插件故障不影响主应用，自动重启机制

这种架构设计真正实现了"UI端专注管理，Daemon端负责执行"的清晰分工，同时为插件生态系统提供了最大的灵活性和扩展性。

---

*文档版本: 1.0*  
*创建时间: 2025-08-02*  
*维护团队: Flutter架构设计组*