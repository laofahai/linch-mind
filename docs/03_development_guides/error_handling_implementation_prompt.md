# 错误处理架构实现通用Prompt

## 使用方法

将以下prompt提供给开发者，确保完整实现错误处理架构。

---

## 核心Prompt

```
请为Linch Mind项目实现增强错误处理架构。在开始之前，请先阅读以下文档以理解设计理念和要求：

## 📖 必读文档（按顺序阅读）
1. `docs/03_development_guides/error_handling_best_practices.md` - 了解完整的架构设计和最佳实践
2. 当前项目的错误处理现状：
   - `ui/lib/services/ipc_api_adapter.dart`
   - `ui/lib/services/ipc_client.dart` 
   - `ui/lib/utils/app_logger.dart`
   - `daemon/core/error_handling.py`
   - `daemon/services/ipc_protocol.py`

## 🎯 实现目标
彻底解决"UI显示错误但控制台、调试模式、错误堆栈等完全看不到"的问题，同时确保生产环境安全。

## 🔍 问题分析
当前问题：用户在UI看到错误提示，但开发者无法在控制台、IDE调试器中看到具体错误信息和堆栈，导致调试困难。

## 📋 完整实现清单

### Phase 1: 后端安全增强 (Python)
1. **扩展 `daemon/core/error_handling.py`**：
   - 实现 `ProcessedError` 类，包含 errorId、安全消息分离
   - 实现 `EnhancedErrorHandler` 类，包含：
     - 错误签名生成（用于去重）
     - 用户友好消息映射
     - 可恢复性判断逻辑
     - 重试延迟计算
     - 详细日志记录（仅后端保留）
   - 实现 `ErrorRateLimiter` 类，防止错误风暴

2. **修改 `daemon/services/ipc_protocol.py`**：
   - 扩展 `IPCResponse.from_error()` 方法
   - 确保只传输安全字段：errorId, message, canRetry, isRecoverable
   - 移除敏感字段：stackTrace, debugInfo, context

3. **更新所有IPC路由处理器**：
   - 使用新的 `EnhancedErrorHandler.process_error()`
   - 确保异常都经过安全过滤

### Phase 2: UI端智能处理 (Flutter)
1. **创建 `ui/lib/utils/enhanced_error_handler.dart`**：
   - 实现单例 `EnhancedErrorHandler` 类
   - 集成RxDart的去重和限流机制
   - 实现错误签名去重（5秒窗口）
   - 实现1秒限流保护
   - 实现 `RecoveryManager` 自动恢复机制

2. **创建 `ui/lib/models/ui_error.dart`**：
   - 定义 `UIError` 模型
   - 实现从IPC错误数据的转换
   - 包含错误分类逻辑（网络/认证/严重错误）

3. **创建 `ui/lib/widgets/smart_error_display.dart`**：
   - 实现智能错误显示组件
   - 支持多种错误类型的视觉区分
   - 提供重试按钮和错误ID复制功能
   - 调试模式显示详细信息，生产模式友好提示

4. **更新所有API调用点**：
   - 使用 `EnhancedErrorHandler.safeAsync()` 包装
   - 传入正确的操作上下文
   - 移除原有的简单try-catch

### Phase 3: 系统集成
1. **修改 `ui/lib/main.dart`**：
   - 设置全局错误处理器
   - 包装应用根Widget为 `SmartErrorDisplay`
   - 处理Flutter框架错误

2. **添加依赖**：
   - Flutter: rxdart (去重限流)
   - Python: 确保现有依赖充足

3. **配置调试输出**：
   - 开发环境：完整错误信息输出到控制台
   - 生产环境：仅用户友好提示
   - 使用 `kDebugMode` 严格区分

## 🔒 安全要求 (严格执行)

### 绝对禁止项
- ❌ 生产环境传输堆栈跟踪到UI
- ❌ 暴露文件路径、函数名等技术细节
- ❌ 在IPC响应中包含原始异常信息

### 必须执行项
- ✅ 错误ID用于后端日志关联
- ✅ 用户消息必须友好且可操作
- ✅ 敏感信息仅记录在后端日志
- ✅ 调试信息仅在kDebugMode显示

## 🎯 功能要求

### 去重机制
```dart
// 5秒窗口内相同错误签名仅处理一次
final signature = '${error.code}:${operation}';
if (_recentErrors[signature]?.after(5.seconds.ago) == true) return;
```

### 限流保护
```dart
// 使用RxDart的throttleTime，1秒内最多触发一次UI更新
errorStream.throttleTime(Duration(seconds: 1))
```

### 自动恢复
```dart
// 对可恢复错误实施指数退避重连
if (error.isRecoverable) {
  _recoveryManager.attemptRecovery(
    error, 
    maxAttempts: 3,
    backoffStrategy: ExponentialBackoff()
  );
}
```

### 内存管理
- 错误缓存最多保留20个条目
- Stream订阅必须在dispose时取消
- 定时器必须在销毁时清理

## 🔍 调试增强要求

### 开发环境输出格式
```
╔════════════════════════════════════════════════════════════
║ 🔴 ERROR: ConnectorLifecycle.getConnectors()
║ ID: uuid-12345
║ Code: DATABASE_ERROR  
║ Message: Database connection failed
║ Time: 2025-01-10T15:30:00Z
║ Retry: Available (after 2s)
║ Request Trace: req_abc123 -> ipc_xyz789
║ Stack Trace: [仅开发环境显示]
╚════════════════════════════════════════════════════════════
```

### 生产环境输出
- 仅显示用户友好消息
- 错误ID供技术支持使用
- 自动重试提示

## 📋 实现检查清单

### 后端检查项
- [ ] ProcessedError类包含所有必需字段
- [ ] 错误签名算法正确实现
- [ ] 用户消息映射覆盖所有错误类型
- [ ] 限流器防止同类错误过多
- [ ] IPC响应仅包含安全字段
- [ ] 详细日志正确记录

### UI端检查项  
- [ ] 错误去重5秒窗口正常工作
- [ ] 限流保护1秒间隔生效
- [ ] 自动恢复机制正确触发
- [ ] 错误显示组件视觉清晰
- [ ] 重试按钮功能完整
- [ ] 内存管理无泄漏

### 集成检查项
- [ ] 全局错误处理正确设置
- [ ] 所有API调用已更新
- [ ] 调试输出格式正确
- [ ] 生产环境安全合规

## 🚀 验证步骤

### 功能验证
1. 触发相同错误多次，验证去重生效
2. 快速产生多个错误，验证限流保护
3. 断开IPC连接，验证自动重连
4. 检查错误ID能否在后端日志中找到

### 安全验证
1. 生产环境模式下不能看到堆栈跟踪
2. 网络抓包确认敏感信息未传输
3. 错误消息对普通用户友好

### 性能验证
1. 错误处理不影响正常操作性能
2. 内存使用稳定，无泄漏
3. UI响应流畅，无卡顿

## 📁 期望文件结构

```
daemon/
├── core/
│   └── error_handling.py (增强)
├── services/
│   └── ipc_protocol.py (修改)
└── services/ipc_routes/ (所有路由更新)

ui/lib/
├── utils/
│   └── enhanced_error_handler.dart (新建)
├── models/
│   └── ui_error.dart (新建)
├── widgets/
│   └── smart_error_display.dart (新建)
├── services/ (所有API客户端更新)
└── main.dart (修改)

docs/03_development_guides/
├── error_handling_best_practices.md (已存在)
└── error_handling_implementation_prompt.md (当前文件)
```

## ⚡ 一键验证命令

实现完成后，运行以下验证：

```bash
# 后端测试
cd daemon && python -m pytest tests/test_error_handling.py -v

# UI测试  
cd ui && flutter test test/error_handling_test.dart

# 集成测试
./scripts/test_error_handling_integration.sh
```

## 📊 成功标准

完成后必须满足：
- ✅ 开发环境：控制台显示完整错误信息，IDE能断点调试
- ✅ 生产环境：用户看到友好提示，技术细节完全隐藏
- ✅ 相同错误5秒内仅显示一次
- ✅ 错误风暴时UI依然响应流畅
- ✅ IPC断线自动重连成功
- ✅ 每个错误都有唯一ID可追踪
- ✅ 零内存泄漏，零安全隐患

这个实现将彻底解决调试困难问题，同时提供工业级的用户体验。

## ⚠️ 重要提醒
1. **先阅读文档**：开始实现前必须完整阅读上述必读文档
2. **理解原理**：理解为什么要这样设计（安全性、用户体验、可维护性）
3. **分阶段实施**：按照Phase 1-3的顺序实现，不要跳跃
4. **严格测试**：每个阶段完成后都要经过功能、安全、性能验证

## 📞 实施支持
如有疑问，请参考：
- `error_handling_best_practices.md` 了解设计原理
- 项目现有代码了解当前实现
- 测试用例验证实现正确性
```

---

## 📋 Prompt使用清单

使用此prompt时，开发者应该：

### ✅ 准备工作
- [ ] 确保能访问所有必读文档
- [ ] 理解当前项目的错误处理现状
- [ ] 设置好开发环境

### ✅ 实施检查
- [ ] 按顺序阅读了所有必读文档
- [ ] 理解了设计原理和安全要求
- [ ] 分阶段实施，不跳跃步骤
- [ ] 每阶段完成后进行验证

### ✅ 交付标准
- [ ] 所有检查清单项目都已完成
- [ ] 通过了功能、安全、性能验证
- [ ] 满足了明确的成功标准

## 🎯 Prompt优势

这个优化后的prompt具备：

1. **文档导向**：要求先读懂设计理念
2. **问题明确**：清晰描述要解决的具体问题  
3. **分步实施**：避免开发者迷失方向
4. **严格验证**：确保实现质量
5. **安全优先**：避免生产环境风险

通过这种方式，确保开发者能够完整、正确地实现整套错误处理架构。