# Flutter迁移技术决策记录

**决策编号**: ADR-003  
**状态**: 已批准  
**创建时间**: 2025-08-02  
**决策者**: 项目团队核心

## 决策背景

### 当前技术栈问题
Linch Mind项目使用Kotlin Multiplatform (KMP) + Compose Multiplatform技术栈遇到以下挑战：

1. **开发复杂度过高**: KMP生态系统复杂，依赖管理困难
2. **跨平台支持不成熟**: Compose Multiplatform移动端支持仍在发展中
3. **团队技能匹配**: Flutter生态系统更加成熟和广泛使用
4. **开发效率**: Flutter单一语言栈简化开发流程
5. **生态系统成熟度**: Flutter插件生态系统更加丰富

### 业务需求驱动
- 需要更快的开发迭代速度
- 跨平台一致性体验要求
- 降低技术维护成本
- 提升团队开发效率

## 决策内容

### 核心决策: 完全迁移到Flutter

**技术栈选择**:
- **前端**: Flutter (Dart语言)
- **状态管理**: Riverpod
- **数据库**: SQLite (使用sqflite)
- **网络**: Dio HTTP客户端
- **本地AI**: 通过FFI调用C++库或HTTP API

### 架构迁移策略

#### 1. UI层迁移
```
Kotlin Multiplatform + Compose Desktop/Mobile
                ↓
Flutter (单一代码库，原生跨平台)
```

#### 2. 状态管理迁移
```
Kotlin StateFlow + ViewModel
                ↓
Riverpod Provider + StateNotifier
```

#### 3. 数据层迁移
```
SQLite + KMP-NativeSQL
                ↓
SQLite + sqflite (Flutter官方推荐)
```

## 实施计划

### Phase 1: 架构设计重构 (2周)
- [ ] Flutter项目架构设计
- [ ] Daemon服务重新设计
- [ ] 数据模型Dart重写
- [ ] API接口设计更新

### Phase 2: 核心功能迁移 (4-6周)
- [ ] 知识图谱存储迁移到sqflite
- [ ] AI服务集成重写
- [ ] 数据采集器Flutter插件重写
- [ ] 推荐引擎Dart实现

### Phase 3: UI完全重构 (3-4周)
- [ ] 主界面Flutter重写
- [ ] 图谱可视化组件
- [ ] 设置和配置界面
- [ ] 响应式设计适配

### Phase 4: 测试和优化 (2-3周)
- [ ] 功能测试覆盖
- [ ] 性能优化
- [ ] 跨平台兼容性测试
- [ ] 用户体验优化

## Daemon实现策略重新设计

### 选项A: Dart HTTP服务器 (推荐)
**实现方案**: 使用Dart的shelf框架实现HTTP daemon
```dart
// 示例架构
class LinchMindDaemon {
  final shelf.Handler handler;
  final KnowledgeService knowledgeService;
  final RecommendationEngine recommendationEngine;
  
  Future<void> start(int port) async {
    final server = await shelf_io.serve(handler, 'localhost', port);
  }
}
```

**优势**:
- 与Flutter应用完全统一的语言栈
- 简化开发和维护
- 优秀的HTTP服务器库支持
- 原生异步支持

**劣势**:
- Dart服务器生态相对较小
- 性能可能不如专门的服务器语言

### 选项B: Node.js Daemon
**实现方案**: 使用Node.js + Express实现daemon
```javascript
// 示例架构
class LinchMindDaemon {
  constructor() {
    this.app = express();
    this.knowledgeService = new KnowledgeService();
  }
  
  async start(port) {
    this.app.listen(port);
  }
}
```

**优势**:
- 成熟的服务器生态系统
- 优秀的性能和稳定性
- 丰富的中间件和库支持

**劣势**:
- 多语言栈增加复杂度
- 需要维护两套代码库

### 选项C: Rust + Tauri Daemon
**实现方案**: 使用Rust实现高性能daemon，Tauri提供Flutter接口
```rust
// 示例架构
#[tauri::command]
async fn get_recommendations() -> Result<Vec<Recommendation>, String> {
    let engine = RecommendationEngine::new();
    engine.get_recommendations().await
}
```

**优势**:
- 极高的性能和安全性
- 内存安全保证
- 优秀的并发处理能力

**劣势**:
- 学习曲线陡峭
- 开发周期较长
- 调试复杂度较高

## 推荐决策: 选项A - Dart HTTP服务器

### 决策理由
1. **技术栈统一**: 单一Dart语言，降低维护复杂度
2. **开发效率**: 共享代码、模型和逻辑
3. **生态系统**: shelf框架成熟，HTTP服务器功能完整
4. **团队效率**: 无需学习新语言，专注业务逻辑
5. **部署简化**: 单一运行时环境

### 技术风险缓解
1. **性能监控**: 建立完整的性能监控体系
2. **负载测试**: 早期进行压力测试验证
3. **架构优化**: 使用Isolate并发处理请求
4. **缓存策略**: 实现多层缓存优化响应速度

## 迁移风险评估

### 技术风险
| 风险 | 概率 | 影响 | 缓解策略 |
|------|------|------|----------|
| Flutter生态系统不足 | 低 | 中 | 使用成熟第三方库，必要时自开发 |
| 性能不如原KMP实现 | 中 | 中 | 性能测试驱动优化，使用原生插件 |
| Dart daemon性能问题 | 中 | 高 | 早期压力测试，必要时切换到Node.js |
| 数据迁移复杂 | 低 | 中 | 制定详细迁移脚本和回滚方案 |

### 业务风险
| 风险 | 概率 | 影响 | 缓解策略 |
|------|------|------|----------|
| 迁移周期过长 | 中 | 高 | 分阶段迁移，保持功能持续可用 |
| 用户体验下降 | 低 | 高 | UI/UX设计先行，用户测试验证 |
| 功能缺失 | 中 | 中 | 完整功能清单，优先级排序 |

## 成功指标

### 技术指标
- [ ] 应用启动时间 < 3秒
- [ ] UI响应时间 < 100ms
- [ ] Daemon API响应时间 < 200ms
- [ ] 内存使用 < 500MB (桌面版)
- [ ] 跨平台功能一致性 > 95%

### 业务指标
- [ ] 开发效率提升 > 30%
- [ ] Bug数量减少 > 40%
- [ ] 新功能交付速度提升 > 50%
- [ ] 用户满意度保持 > 85%

## 相关文档

- [Flutter架构设计文档](../01_technical_design/flutter_architecture_design.md)
- [Daemon架构重新设计](../01_technical_design/flutter_daemon_architecture.md)
- [迁移实施计划](../01_technical_design/migration_implementation_plan.md)
- [开发环境配置指南](../01_technical_design/flutter_development_setup.md)

---

**决策批准人**: 项目负责人  
**实施负责人**: 技术团队  
**审查周期**: 每2周审查进度，必要时调整方案  
**回滚计划**: 如迁移失败，6周内可回滚到KMP版本