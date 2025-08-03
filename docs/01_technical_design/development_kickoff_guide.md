# Linch Mind 开发启动指南

**版本**: 1.0  
**状态**: 立即可用  
**创建时间**: 2025-08-02  
**适用于**: Flutter + Python Daemon 10天MVP

## 1. 项目概述

### 1.1 目标
10天内交付一个可演示的Linch Mind MVP，采用Flutter + Python Daemon架构，展示：
- 文件系统连接器实时监控
- 剪贴板数据采集和管理
- AI驱动的智能推荐系统
- 跨平台Flutter UI界面

### 1.2 技术架构
```
Flutter Frontend (Dart) ←→ Python Daemon (FastAPI) ←→ Multi-language Connectors
```

### 1.3 开发策略
- **契约优先**: API设计先行，Pydantic数据模型
- **垂直切片**: 每2天完成一个端到端功能
- **并行开发**: Mock服务支持前后端同步开发
- **持续集成**: 每日构建验证，实时反馈

## 2. Day-by-Day 开发计划

### Day 1: API契约设计和项目初始化

#### 上午任务 (9:00-12:00)
**API契约设计师** (1人):
```bash
# 创建项目结构
mkdir linch-mind-mvp
cd linch-mind-mvp
mkdir -p {daemon,flutter_app,docs,scripts}

# 设计Pydantic数据模型
# daemon/models.py
```

**具体任务**:
- [ ] 定义Entity, Recommendation, ConnectorConfig数据模型
- [ ] 设计RESTful API接口规范 (OpenAPI 3.0)
- [ ] 创建API版本管理策略
- [ ] 编写API文档和示例

**交付物**:
- `daemon/models.py` - 完整Pydantic模型
- `daemon/api_spec.yaml` - OpenAPI规范文档
- `docs/api_reference.md` - API使用指南

#### 下午任务 (13:00-18:00)
**FastAPI开发者** (1人):
```bash
# 创建FastAPI Mock服务
cd daemon
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
pip install fastapi uvicorn pydantic
```

**具体任务**:
- [ ] 实现FastAPI Mock服务器
- [ ] 添加CORS中间件配置
- [ ] 创建假数据生成器
- [ ] 实现所有API端点的Mock响应
- [ ] 添加请求响应日志

**交付物**:
- `daemon/mock_server.py` - 可运行的Mock服务
- `daemon/requirements.txt` - 依赖清单
- `scripts/start_mock.sh` - Mock服务启动脚本

**验收标准**:
- [ ] Mock服务能在 http://localhost:8000 启动
- [ ] 所有API端点返回合理的假数据
- [ ] API响应时间 < 100ms
- [ ] 支持CORS跨域请求

### Day 2: Flutter项目初始化和基础UI

#### 上午任务 (9:00-12:00)
**Flutter开发者** (1人):
```bash
# 创建Flutter项目
cd flutter_app
flutter create . --org com.linchmind --project-name linch_mind
```

**具体任务**:
- [ ] 配置pubspec.yaml依赖 (flutter_riverpod, dio, go_router)
- [ ] 设置项目结构 (lib/{models,services,screens,widgets})
- [ ] 创建Dart数据模型 (对应Python Pydantic模型)
- [ ] 实现HTTP客户端服务

**交付物**:
- `lib/models/` - Dart数据模型
- `lib/services/daemon_client.dart` - HTTP客户端
- `lib/main.dart` - 应用入口
- `pubspec.yaml` - 项目配置

#### 下午任务 (13:00-18:00)
**Flutter开发者** 继续:

**具体任务**:
- [ ] 实现基础UI框架 (Material Design 3)
- [ ] 设置Riverpod状态管理
- [ ] 创建主界面布局
- [ ] 实现路由导航系统
- [ ] 集成HTTP客户端调用Mock API

**交付物**:
- `lib/screens/main_screen.dart` - 主界面
- `lib/providers/` - Riverpod状态提供者
- `lib/widgets/` - 可复用UI组件

**验收标准**:
- [ ] Flutter应用能成功启动
- [ ] 能够调用Mock API并显示数据
- [ ] UI响应流畅，导航正常
- [ ] 状态管理工作正常

### Day 3: 文件系统连接器后端实现

#### 上午任务 (9:00-12:00)
**Python后端开发者** (1人):
```bash
# 安装文件监控依赖
pip install watchdog sqlalchemy aiofiles
```

**具体任务**:
- [ ] 实现FileSystemConnector类
- [ ] 集成watchdog库进行文件监控
- [ ] 创建SQLite数据库连接
- [ ] 实现文件内容解析器
- [ ] 添加文件变更事件处理

**核心代码结构**:
```python
# daemon/connectors/filesystem.py
class FileSystemConnector:
    def __init__(self, config: dict):
        self.watch_paths = config['watch_paths']
        self.observer = Observer()
    
    async def start(self):
        # 启动文件监控
        pass
    
    async def collect_data(self) -> List[DataItem]:
        # 收集文件数据
        pass
```

#### 下午任务 (13:00-18:00)
**Python后端开发者** 继续:

**具体任务**:
- [ ] 实现实时API端点 (替换Mock)
- [ ] 添加SQLite数据持久化
- [ ] 实现增量数据同步
- [ ] 添加文件类型过滤
- [ ] 创建性能监控

**交付物**:
- `daemon/connectors/filesystem.py` - 文件系统连接器
- `daemon/database.py` - 数据库操作
- `daemon/main.py` - 真实API服务器
- `daemon/config.yaml` - 配置文件

**验收标准**:
- [ ] 能监控指定目录的文件变化
- [ ] 文件变更能实时写入数据库
- [ ] API能返回真实的文件数据
- [ ] 服务启动时间 < 5秒

### Day 4: 文件系统连接器前端UI

#### 上午任务 (9:00-12:00)
**Flutter开发者**:

**具体任务**:
- [ ] 创建ConnectorManagementScreen
- [ ] 实现文件列表展示组件
- [ ] 添加连接器配置界面
- [ ] 实现实时状态更新

**UI组件**:
```dart
// lib/screens/connector_management_screen.dart
class ConnectorManagementScreen extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final connectors = ref.watch(connectorsProvider);
    // UI实现
  }
}
```

#### 下午任务 (13:00-18:00)
**Flutter开发者** 继续:

**具体任务**:
- [ ] 集成真实API调用
- [ ] 实现文件内容预览
- [ ] 添加搜索和过滤功能
- [ ] 优化UI响应性能
- [ ] 添加错误处理

**交付物**:
- `lib/screens/connector_management_screen.dart`
- `lib/widgets/file_list_widget.dart`
- `lib/widgets/connector_config_dialog.dart`

**验收标准**:
- [ ] 能显示实时的文件监控状态
- [ ] 文件列表更新流畅
- [ ] 配置更改能生效
- [ ] UI美观且响应迅速

### Day 5: 剪贴板连接器后端实现

#### 全天任务 (9:00-18:00)
**Python后端开发者**:

**具体任务**:
- [ ] 实现ClipboardConnector类
- [ ] 集成剪贴板监控库 (pyperclip, pyclip)
- [ ] 添加数据去重机制
- [ ] 实现历史记录管理
- [ ] 创建搜索和过滤API

**核心功能**:
```python
# daemon/connectors/clipboard.py
class ClipboardConnector:
    def __init__(self):
        self.history = []
        self.running = False
    
    async def start_monitoring(self):
        # 开始剪贴板监控
        pass
    
    async def get_history(self, limit: int = 100):
        # 获取历史记录
        pass
```

**交付物**:
- `daemon/connectors/clipboard.py` - 剪贴板连接器
- API端点: `/api/v1/clipboard/history`
- API端点: `/api/v1/clipboard/search`

**验收标准**:
- [ ] 能实时监控剪贴板变化
- [ ] 历史记录正确存储
- [ ] 支持文本搜索
- [ ] 内存使用合理 (< 50MB)

### Day 6: 剪贴板连接器前端UI

#### 全天任务 (9:00-18:00)
**Flutter开发者**:

**具体任务**:
- [ ] 创建ClipboardHistoryScreen
- [ ] 实现历史记录列表
- [ ] 添加搜索功能
- [ ] 实现数据预览和编辑
- [ ] 添加数据导出功能

**UI特性**:
- 支持长文本截断显示
- 富文本内容预览
- 快速搜索和过滤
- 一键复制功能

**交付物**:
- `lib/screens/clipboard_history_screen.dart`
- `lib/widgets/clipboard_item_widget.dart`
- `lib/services/clipboard_service.dart`

**验收标准**:
- [ ] 历史记录显示正确
- [ ] 搜索功能工作正常
- [ ] 界面流畅不卡顿
- [ ] 数据操作响应及时

### Day 7: AI推荐系统后端实现

#### 全天任务 (9:00-18:00)
**Python AI开发者** (1人):

**环境准备**:
```bash
pip install transformers torch ollama-python openai sentence-transformers
```

**具体任务**:
- [ ] 实现RecommendationService类
- [ ] 集成本地AI模型 (使用Ollama)
- [ ] 实现基于行为的推荐算法
- [ ] 创建推荐结果排序和过滤
- [ ] 添加AI解释生成

**核心算法**:
```python
# daemon/services/recommendation_service.py
class RecommendationService:
    def __init__(self):
        self.ai_client = OllamaClient()
        self.knowledge_service = KnowledgeService()
    
    async def generate_recommendations(self, user_id: str) -> List[Recommendation]:
        # 1. 分析用户行为
        behaviors = await self.get_user_behaviors(user_id)
        
        # 2. 找到相关实体
        entities = await self.find_related_entities(behaviors)
        
        # 3. AI增强推荐
        recommendations = await self.enhance_with_ai(entities)
        
        return recommendations
```

**交付物**:
- `daemon/services/recommendation_service.py`
- `daemon/ai/ollama_client.py` - AI客户端
- API端点: `/api/v1/recommendations`

**验收标准**:
- [ ] 推荐算法能基于用户数据工作
- [ ] AI解释文本生成正常
- [ ] 推荐响应时间 < 2秒
- [ ] 推荐结果相关性合理

### Day 8: AI推荐系统前端UI

#### 全天任务 (9:00-18:00)
**Flutter开发者**:

**具体任务**:
- [ ] 创建RecommendationDashboard
- [ ] 实现推荐卡片组件
- [ ] 添加AI解释展示
- [ ] 实现用户反馈收集
- [ ] 优化推荐内容布局

**UI设计要点**:
- 推荐卡片突出显示
- AI解释以友好方式呈现
- 支持用户点赞/忽略反馈
- 实时更新推荐内容

**交付物**:
- `lib/screens/recommendation_dashboard.dart`
- `lib/widgets/recommendation_card.dart`
- `lib/services/recommendation_service.dart`

**验收标准**:
- [ ] 推荐内容显示美观
- [ ] AI解释易于理解
- [ ] 用户反馈能正常提交
- [ ] 界面响应流畅

### Day 9: 系统集成和测试

#### 上午任务 (9:00-12:00)
**全体开发者**:

**集成任务**:
- [ ] 端到端功能测试
- [ ] API接口兼容性验证
- [ ] 数据流完整性检查
- [ ] 性能基准测试
- [ ] 错误处理验证

**测试场景**:
1. 启动系统 → 文件监控 → 数据入库 → UI显示
2. 剪贴板操作 → 历史记录 → 搜索功能 → 数据操作
3. 用户交互 → 行为分析 → AI推荐 → 反馈收集

#### 下午任务 (13:00-18:00)
**问题修复和优化**:

- [ ] 修复集成测试发现的问题
- [ ] 优化API响应性能
- [ ] 改进UI交互体验
- [ ] 完善错误处理机制
- [ ] 添加日志和监控

**验收标准**:
- [ ] 所有核心功能正常工作
- [ ] API响应时间达标
- [ ] UI操作流畅无卡顿
- [ ] 错误处理完善

### Day 10: 演示准备和文档完善

#### 上午任务 (9:00-12:00)
**演示数据准备**:

- [ ] 创建演示用的测试数据
- [ ] 准备演示脚本和场景
- [ ] 优化界面展示效果
- [ ] 测试演示流程
- [ ] 准备问题应对方案

**演示场景设计**:
```
1. 系统启动展示 (30秒)
2. 文件监控演示 (2分钟)
   - 创建文件 → 实时检测 → 数据展示
3. 剪贴板功能演示 (2分钟)
   - 复制内容 → 历史记录 → 搜索功能
4. AI推荐演示 (3分钟)
   - 数据积累 → AI分析 → 推荐生成 → 解释展示
5. 系统稳定性展示 (2分钟)
   - 重启应用 → 数据持久化 → 快速恢复
```

#### 下午任务 (13:00-18:00)
**文档和部署**:

- [ ] 完善API文档
- [ ] 编写用户使用指南
- [ ] 创建部署脚本
- [ ] 准备演示环境
- [ ] 最终测试验证

**交付物**:
- `docs/demo_guide.md` - 演示指南
- `docs/user_manual.md` - 用户手册
- `scripts/deploy.sh` - 部署脚本
- `scripts/demo_setup.sh` - 演示环境配置

**最终验收标准**:
- [ ] 演示环境稳定运行
- [ ] 所有演示场景测试通过
- [ ] 文档完整可读
- [ ] 部署脚本可用

## 3. 开发环境配置

### 3.1 必需工具
```bash
# Python环境
Python 3.9+
pip
venv

# Flutter开发
Flutter SDK 3.13+
Dart SDK
Android Studio / VS Code

# 数据库
SQLite3

# AI模型 (可选)
Ollama
```

### 3.2 快速启动脚本
```bash
#!/bin/bash
# scripts/quick_start.sh

echo "Setting up Linch Mind MVP development environment..."

# 后端环境
cd daemon
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
echo "Backend environment ready!"

# 前端环境
cd ../flutter_app
flutter pub get
echo "Frontend environment ready!"

# 启动服务
echo "Starting development servers..."
cd ../daemon
python main.py &
DAEMON_PID=$!

cd ../flutter_app
flutter run -d linux &
FLUTTER_PID=$!

echo "Daemon PID: $DAEMON_PID"
echo "Flutter PID: $FLUTTER_PID"

# 等待停止信号
trap "kill $DAEMON_PID $FLUTTER_PID" EXIT
wait
```

### 3.3 开发规范
- **代码提交**: 每个功能完成后立即提交
- **分支管理**: feature/day-X-description
- **代码审查**: 每日代码review，确保质量
- **文档更新**: 重要变更同步更新文档
- **测试覆盖**: 关键功能必须有测试用例

## 4. 风险管理

### 4.1 高风险项
| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| Python AI集成复杂 | 中 | 高 | 预备简化方案，Mock AI响应 |
| Flutter跨平台兼容性 | 低 | 中 | 优先Linux/Windows，Mac后续 |
| 10天时间不足 | 中 | 高 | 严格控制功能范围，删除非核心特性 |
| API契约变更频繁 | 中 | 中 | 版本控制，向后兼容保证 |

### 4.2 应急预案
- **时间延期**: 削减非核心功能，专注演示效果
- **技术障碍**: 准备降级方案，保证基础功能
- **集成问题**: 加强Mock服务，独立模块测试
- **性能问题**: 优化关键路径，接受合理延迟

## 5. 成功定义

### 5.1 MVP验收标准
- [ ] **功能完整性**: 文件监控、剪贴板、AI推荐三大功能正常
- [ ] **性能达标**: 启动 < 5秒，API响应 < 200ms，UI流畅
- [ ] **稳定性**: 连续运行2小时无崩溃
- [ ] **可演示性**: 完整演示流程 < 10分钟
- [ ] **代码质量**: 关键模块有测试，文档完整

### 5.2 技术指标
- **后端**: Python Daemon稳定运行，API响应正常
- **前端**: Flutter应用跨平台兼容，UI美观流畅
- **集成**: 端到端数据流正确，实时更新有效
- **AI**: 推荐算法基本可用，AI解释生成正常

---

**立即开始**: 这个指南可以立即投入使用。建议今天就开始Day 1的任务！

**文档版本**: 1.0  
**创建时间**: 2025-08-02  
**维护团队**: MVP开发组  
**预计完成**: 2025-08-12