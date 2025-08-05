# 📚 Linch Mind 项目文档导航

> **Linch Mind** - 个人AI生活助手，基于连接器插件生态系统的智能数据分析平台

---

## 📖 文档结构概览

### 🎯 [愿景与策略](./00_vision_and_strategy/)
项目的核心理念、产品定位和发展规划

- **[产品愿景和策略](./00_vision_and_strategy/product_vision_and_strategy.md)** - 产品核心定位、目标用户、价值主张

### 🏗️ [技术设计](./01_technical_design/)
系统架构设计、技术选型和实现方案

#### 🔌 连接器系统 (核心)
- **[连接器开发标准](./01_technical_design/connector_internal_management_standards.md)** 
  - 简化的连接器架构设计
  - Python生态和Poetry管理
  - API驱动的数据推送机制

#### 🛠️ 系统架构设计
- **[Daemon架构设计](./01_technical_design/daemon_architecture.md)** - Python FastAPI后端服务架构
- **[Flutter架构设计](./01_technical_design/flutter_architecture_design.md)** - 跨平台UI架构和状态管理
- **[API契约设计](./01_technical_design/api_contract_design.md)** - RESTful API接口规范

#### 📊 专业领域设计
- **[连接器UI设计](./01_technical_design/connector_ui_redesign.md)** - 连接器管理界面设计
- **[安全架构设计](./01_technical_design/security_architecture_design.md)** - 数据安全和隐私保护架构

### 📋 [架构决策记录](./02_decisions/)
重要的技术决策和架构选择的记录

- **[Python + Flutter最终架构决策](./02_decisions/python_flutter_architecture_final_decision.md)** - 最终技术架构选择的完整决策过程
- **[硬件扩展决策记录](./02_decisions/hardware_extension_decision_record.md)** - 硬件设备扩展的技术评估和决策

---

## 🚀 快速导航

### 👩‍💻 开发者快速入门
1. **新手开发者**: 从项目根目录 README.md 开始
2. **架构了解**: 阅读 [连接器开发标准](./01_technical_design/connector_internal_management_standards.md)
3. **环境搭建**: 使用项目根目录的 `./dev.sh` 脚本

### 🏢 系统运维
1. **架构理解**: [Daemon架构设计](./01_technical_design/daemon_architecture.md)
2. **安全配置**: [安全架构设计](./01_technical_design/security_architecture_design.md)

### 🎯 产品和策略
1. **产品理解**: [产品愿景和策略](./00_vision_and_strategy/product_vision_and_strategy.md)
2. **架构决策**: [架构决策记录](./02_decisions/) 目录

---

## 📊 文档状态

### ✅ 已完成的核心文档
- 🏗️ **Daemon架构设计** - Python FastAPI后端服务的详细技术设计
- 🔌 **连接器开发标准** - 简化的连接器架构和开发指南
- 🎯 **产品愿景和策略** - 项目核心理念和发展路线
- 📱 **Flutter架构设计** - 跨平台UI架构和状态管理

### ✅ 已完成的文档
- 🔍 **API契约设计** - RESTful API完整规范
- 📋 **重要架构决策** - Python+Flutter最终架构等关键决策记录
- 🎨 **连接器UI设计** - 连接器管理界面深度设计分析
- 🔐 **安全架构设计** - 数据安全和隐私保护完整方案

### 📅 后续规划文档
- 🤖 **AI服务集成指南** - 多AI提供者集成方案（架构就绪）
- 📈 **数据分析架构** - 智能推荐和用户画像系统优化
- 🔧 **部署运维指南** - 生产环境部署和监控指南

---

## 🎯 文档使用指南

### 📚 阅读建议
1. **产品新人**: 先读产品愿景 → 连接器开发指南 → 架构设计
2. **技术人员**: 直接从相关技术设计文档开始
3. **运维人员**: 重点关注Daemon架构和安全架构文档

### 🔄 文档更新
- 所有重要架构变更都会更新相应文档
- 文档版本跟随项目版本发布
- 过时内容会及时清理和更新

### 🤝 贡献指南
1. 技术文档修改请提交 PR
2. 架构决策需要在 `02_decisions/` 中记录
3. 新增重要功能需要同步更新文档

---

## 🌟 关键设计理念

### 🎯 **简化架构设计** 
- **开发优先**: Poetry环境，源码直接运行
- **配置驱动**: 通过YAML配置管理连接器
- **API集成**: RESTful API统一数据流

### 🔌 **连接器生态系统**
- **非侵入式**: 数据保持在用户原有应用中
- **Python生态**: 充分利用丰富的第三方库
- **简化设计**: Poetry统一管理，API驱动推送

### 🛡️ **隐私优先**
- **本地处理**: 所有数据在本地处理，不上传云端
- **用户控制**: 用户完全控制数据访问和处理
- **透明运行**: 开源代码，运行逻辑完全透明

---

## 📞 联系和支持

- **项目地址**: https://github.com/linch-mind/linch-mind
- **文档问题**: 请在 GitHub Issues 中提出
- **技术讨论**: 使用 GitHub Discussions
- **社区支持**: community@linch-mind.com

---

**最后更新**: 2025-08-03  
**文档版本**: v1.0  
**适用版本**: Linch Mind v0.1.0+