# 连接器管理架构重构 - 迁移实施计划

## 概述

本文档描述了从当前分散的连接器管理架构迁移到统一的生命周期管理架构的详细计划。

## 当前架构问题分析

### 1. 状态混乱问题
- **问题**: 没有明确的已安装/已启用概念，源码即安装
- **影响**: 用户无法理解连接器的实际状态
- **解决方案**: 引入清晰的状态模型 (Available → Installed → Configured → Enabled → Running)

### 2. 配置分散问题
- **问题**: 存在三套配置系统
  - `registry.json` - 连接器市场配置
  - 连接器内部 `connector.json` - 单个连接器配置
  - daemon配置 - 运行时配置
- **影响**: 配置不一致，维护困难
- **解决方案**: 统一配置管理 (`connectors.yaml` + `instances.yaml`)

### 3. 文件冗余问题
- **问题**: 存在大量未使用的构建脚本和配置文件
- **影响**: 项目复杂度高，开发者困惑
- **解决方案**: 清理冗余文件，简化项目结构

### 4. 生命周期管理缺失
- **问题**: 无法区分开发中/已安装/已启用/运行中状态
- **影响**: 进程管理混乱，状态不可控
- **解决方案**: 实现完整的生命周期管理器

## 新架构设计

### 1. 核心组件

```
连接器管理架构 v2.0
├── UnifiedConfigManager        # 统一配置管理
│   ├── connectors.yaml        # 连接器类型配置
│   └── instances.yaml         # 连接器实例配置
├── ConnectorLifecycleManager  # 生命周期管理
│   ├── 状态转换控制
│   ├── 进程管理
│   └── 健康监控
└── ConnectorLifecycleAPI      # RESTful API
    ├── 实例创建/删除
    ├── 启动/停止控制
    └── 状态查询/事件流
```

### 2. 状态模型

```
状态转换图:
Available → Installed → Configured → Enabled → Running
    ↓           ↓           ↓           ↓         ↓
Uninstalling ← ← ← ← ← ← ← ← ← ← ← ← ← ← Error
```

### 3. 配置架构

#### 主配置文件 (connectors.yaml)
```yaml
config_version: "1.0"
last_updated: "2025-08-03T10:00:00"
metadata:
  description: "Linch Mind 连接器配置 - 统一配置源"
  created_by: "UnifiedConfigManager"
  schema_version: "1.0"

connector_types:
  filesystem:
    name: "文件系统连接器"
    display_name: "文件系统监控"
    description: "实时监控文件系统变化，智能索引文件内容"
    category: "local_files"
    version: "2.0.0"
    author: "Linch Mind Team"
    license: "MIT"
    
    # 能力声明
    supports_multiple_instances: true
    max_instances_per_user: 10
    auto_discovery: false
    hot_config_reload: true
    health_check: true
    
    # 技术信息
    entry_point: "main.py"
    python_version: ">=3.8"
    dependencies: ["watchdog>=2.0.0", "httpx>=0.24.0"]
    permissions: ["file_system_read"]
    
    # 配置模式
    config_schema:
      type: "object"
      properties:
        global_config:
          type: "object"
          properties:
            default_extensions:
              type: "array"
              items: {type: "string"}
              default: [".txt", ".md", ".py"]
        directory_configs:
          type: "array"
          items:
            type: "object"
            properties:
              path: {type: "string"}
              display_name: {type: "string"}
              priority: {type: "string", enum: ["low", "normal", "high"]}
    
    # 实例模板
    instance_templates:
      - id: "documents"
        name: "文档监控"
        description: "监控文档目录，适合笔记和写作"
        config:
          global_config:
            default_extensions: [".md", ".txt", ".doc", ".docx", ".pdf"]
          directory_configs:
            - path: "~/Documents"
              display_name: "文档目录"
              priority: "high"
```

#### 实例配置文件 (instances.yaml)
```yaml
config_version: "1.0"
last_updated: "2025-08-03T10:00:00"
metadata:
  description: "连接器实例配置"
  created_by: "UnifiedConfigManager"

instances:
  filesystem_abc12345:
    type_id: "filesystem"
    display_name: "我的文档监控"
    config:
      global_config:
        default_extensions: [".md", ".txt"]
      directory_configs:
        - path: "/Users/user/Documents"
          display_name: "文档目录"
          priority: "high"
    
    # 状态信息
    state: "configured"
    auto_start: true
    enabled: true
    
    # 运行时信息 (可选，由系统维护)
    process_id: null
    last_heartbeat: null
    error_message: null
    data_count: 0
    
    # 元数据
    created_at: "2025-08-03T10:00:00"
    updated_at: "2025-08-03T10:00:00"
```

## 迁移实施步骤

### Phase 1: 基础设施准备 (已完成)
- [x] 创建 `UnifiedConfigManager` - 统一配置管理
- [x] 创建 `ConnectorLifecycleManager` - 生命周期管理
- [x] 创建 `ConnectorLifecycleAPI` - 新的API路由
- [x] 定义清晰的状态模型和转换规则

### Phase 2: 配置迁移 (下一步)
1. **自动迁移现有配置**
   ```bash
   # 运行迁移脚本
   python scripts/migrate_connector_configs.py
   ```
   - 从 `registry.json` 迁移连接器类型定义
   - 从数据库迁移实例配置
   - 生成新的 `connectors.yaml` 和 `instances.yaml`

2. **验证迁移结果**
   ```bash
   # 验证配置完整性
   python scripts/validate_connector_configs.py
   ```

3. **备份旧配置**
   - 将 `registry.json` 重命名为 `registry_backup_YYYYMMDD.json`
   - 保留数据库表作为备份

### Phase 3: API集成 (第3步)
1. **更新daemon主路由**
   - 在 `daemon/api/main.py` 中注册新的API路由
   - 保持旧API兼容性（标记为废弃）

2. **集成生命周期管理器**
   - 替换现有的 `ConnectorManager` 使用
   - 更新所有相关的服务调用

### Phase 4: Flutter UI更新 (第4步)
1. **更新API客户端**
   - 添加新的API调用方法
   - 支持实时状态同步 (Server-Sent Events)

2. **更新UI界面**
   - 清晰显示连接器状态
   - 支持实例创建和配置
   - 实时状态更新

### Phase 5: 清理和优化 (第5步)
1. **清理冗余文件**
   - 删除未使用的构建脚本
   - 移除旧的API路由
   - 简化目录结构

2. **性能优化**
   - 配置缓存优化
   - 状态同步优化
   - 内存使用优化

## 文件变更清单

### 需要创建的文件
- [x] `daemon/services/connectors/unified_config.py` - 统一配置管理
- [x] `daemon/services/connectors/lifecycle_manager.py` - 生命周期管理
- [x] `daemon/api/routers/connector_lifecycle.py` - 新API路由
- [ ] `connectors/connectors.yaml` - 主配置文件 (迁移时生成)
- [ ] `connectors/instances.yaml` - 实例配置文件 (迁移时生成)
- [ ] `scripts/migrate_connector_configs.py` - 迁移脚本
- [ ] `scripts/validate_connector_configs.py` - 验证脚本

### 需要修改的文件
- [ ] `daemon/api/main.py` - 注册新API路由
- [ ] `daemon/services/connector_manager.py` - 标记为废弃，逐步替换
- [ ] `ui/lib/services/api_client.dart` - 添加新API方法
- [ ] `ui/lib/screens/connectors_screen.dart` - UI更新
- [ ] `ui/lib/models/api_models.dart` - 数据模型更新

### 需要删除的文件 (Phase 5)
- [ ] `connectors/build_all.py` - 构建脚本 (开发模式不需要)
- [ ] `connectors/official/*/build_executable.py` - 单个构建脚本
- [ ] `daemon/api/routers/connector_management.py` - 旧API路由 (保留兼容期)
- [ ] `connectors/registry.json` - 重命名为备份文件

## 风险评估和缓解策略

### 1. 配置迁移风险
- **风险**: 迁移过程中丢失配置数据
- **缓解**: 完整备份 + 迁移验证 + 回滚机制

### 2. API兼容性风险
- **风险**: Flutter UI在迁移期间无法工作
- **缓解**: 保持旧API兼容性，渐进式迁移

### 3. 状态同步风险
- **风险**: 新旧系统状态不一致
- **缓解**: 使用统一的状态源，避免双写

### 4. 性能回归风险
- **风险**: 新架构可能比旧架构慢
- **缓解**: 性能基准测试 + 优化点识别

## 成功指标

### 功能指标
- [ ] 配置迁移成功率 100%
- [ ] 新API功能完整性 100%
- [ ] UI状态显示准确性 100%
- [ ] 连接器启动成功率 ≥ 95%

### 性能指标
- [ ] 配置加载时间 ≤ 1秒
- [ ] 状态查询响应时间 ≤ 100ms
- [ ] 实时状态同步延迟 ≤ 500ms
- [ ] 内存使用增长 ≤ 20%

### 可维护性指标
- [ ] 配置文件可读性提升 (YAML vs JSON)
- [ ] 代码复杂度降低 (消除重复)
- [ ] 开发者上手时间缩短 50%

## 实施时间表

```
Week 1: Phase 1 完成 (基础设施) ✅
Week 2: Phase 2 完成 (配置迁移)
Week 3: Phase 3 完成 (API集成)
Week 4: Phase 4 完成 (UI更新)
Week 5: Phase 5 完成 (清理优化)
Week 6: 测试和文档完善
```

## 回滚计划

如果迁移过程中遇到严重问题，可以通过以下步骤回滚：

1. **停止新系统**
   ```bash
   # 停止使用新的生命周期管理器
   # 切换回旧的ConnectorManager
   ```

2. **恢复旧配置**
   ```bash
   # 恢复registry.json
   mv registry_backup_YYYYMMDD.json registry.json
   # 恢复数据库状态
   python scripts/restore_database_backup.py
   ```

3. **切换API路由**
   ```python
   # 在daemon/api/main.py中
   # 禁用新路由，启用旧路由
   ```

4. **验证系统功能**
   - 确认连接器可以正常启动
   - 确认UI可以正常显示状态
   - 确认所有原有功能正常

## 后续优化方向

迁移完成后，可以考虑以下优化：

1. **配置验证增强**
   - JSON Schema验证
   - 配置模板系统
   - 配置版本管理

2. **监控和诊断**
   - 详细的健康检查
   - 性能指标收集
   - 异常告警机制

3. **用户体验提升**
   - 连接器市场界面
   - 可视化配置编辑器
   - 一键部署模板

4. **企业功能**
   - 权限管理
   - 审计日志
   - 集中配置管理

---

*文档版本: v1.0*  
*创建时间: 2025-08-03*  
*最后更新: 2025-08-03*