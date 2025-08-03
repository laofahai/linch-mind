# 📚 Linch Mind 项目文档导航

> **Linch Mind** - 个人AI生活助手，基于连接器插件生态系统的智能数据分析平台

---

## 📖 文档结构概览

### 🎯 [愿景与策略](./00_vision_and_strategy/)
项目的核心理念、产品定位和发展规划

- **[产品愿景和策略](./00_vision_and_strategy/product_vision_and_strategy.md)** - 产品核心定位、目标用户、价值主张

### 🏗️ [技术设计](./01_technical_design/)
系统架构设计、技术选型和实现方案

#### 🔌 连接器插件系统 (核心)
- **[连接器插件生态系统架构](./01_technical_design/connector_plugin_ecosystem_architecture.md)** 
  - 双模式架构设计 (开发/生产)
  - CI/CD构建和发布流水线  
  - 在线注册表和插件发现机制
  - 安全验证和权限管理系统

- **[插件开发者指南](./01_technical_design/plugin_developer_guide.md)**
  - 5分钟快速开始开发插件
  - 项目结构和核心文件说明
  - 测试、调试和最佳实践
  - 生产环境构建和发布流程

- **[生产环境部署指南](./01_technical_design/production_deployment_guide.md)**
  - Docker容器化部署方案
  - 插件注册表服务架构
  - CI/CD自动化部署流水线
  - 监控、安全和运维指南

#### 🛠️ 系统架构设计
- **[Daemon架构设计](./01_technical_design/daemon_architecture.md)** - Python FastAPI后端服务架构
- **[Flutter架构设计](./01_technical_design/flutter_architecture_design.md)** - 跨平台UI应用架构
- **[API契约设计](./01_technical_design/api_contract_design.md)** - RESTful API接口规范

#### 📊 专业领域设计
- **[日志系统](./01_technical_design/logging_system/)** - 结构化日志和监控体系
- **[NER系统](./01_technical_design/ner_system/)** - 智能实体识别和分析
- **[性能优化路线图](./01_technical_design/performance_optimization_roadmap.md)** - 系统性能优化策略

### 📋 [架构决策记录](./02_decisions/)
重要的技术决策和架构选择的记录

- **[Flutter迁移决策记录](./02_decisions/flutter_migration_decision_record.md)** - 从Kotlin Multiplatform迁移到Flutter的决策分析
- **[硬件扩展决策记录](./02_decisions/hardware_extension_decision_record.md)** - 硬件设备扩展的技术评估和决策

---

## 🚀 快速导航

### 👩‍💻 开发者快速入门
1. **新手开发者**: 从 [插件开发者指南](./01_technical_design/plugin_developer_guide.md) 开始
2. **架构了解**: 阅读 [连接器插件生态系统架构](./01_technical_design/connector_plugin_ecosystem_architecture.md)
3. **环境搭建**: 参考 [Flutter开发环境设置](./01_technical_design/flutter_development_setup.md)

### 🏢 运维和部署
1. **生产部署**: [生产环境部署指南](./01_technical_design/production_deployment_guide.md)
2. **监控运维**: [日志系统架构](./01_technical_design/logging_system/architecture.md)
3. **性能优化**: [性能优化路线图](./01_technical_design/performance_optimization_roadmap.md)

### 🎯 产品和策略
1. **产品理解**: [产品愿景和策略](./00_vision_and_strategy/product_vision_and_strategy.md)
2. **架构决策**: [架构决策记录](./02_decisions/) 目录

---

## 📊 文档状态

### ✅ 已完成的核心文档
- 🔌 **连接器插件生态系统架构** - 完整的双模式插件架构设计
- 👨‍💻 **插件开发者指南** - 从入门到生产的完整开发流程
- 🚀 **生产环境部署指南** - 企业级部署和运维方案
- 🏗️ **Daemon架构设计** - 后端服务的详细技术设计
- 📱 **Flutter架构设计** - 跨平台UI应用的架构方案

### 🔄 正在更新的文档
- 📊 **NER系统** - 智能实体识别系统设计 (90%完成)
- 🔍 **API契约设计** - RESTful API完整规范 (80%完成)
- ⚡ **性能优化路线图** - 系统性能提升策略 (85%完成)

### 📅 计划中的文档
- 🤖 **AI服务集成指南** - 多AI提供者集成方案
- 🔐 **安全架构设计** - 端到端安全保障体系
- 📈 **数据分析架构** - 智能推荐和用户画像系统

---

## 🎯 文档使用指南

### 📚 阅读建议
1. **产品新人**: 先读产品愿景 → 插件开发指南 → 架构设计
2. **技术人员**: 直接从相关技术设计文档开始
3. **运维人员**: 重点关注部署指南和日志系统文档

### 🔄 文档更新
- 所有重要架构变更都会更新相应文档
- 文档版本跟随项目版本发布
- 过时内容会移动到 `_archive/` 目录

### 🤝 贡献指南
1. 技术文档修改请提交 PR
2. 架构决策需要在 `02_decisions/` 中记录
3. 新增重要功能需要同步更新文档

---

## 🌟 关键设计理念

### 🎯 **双模式架构** 
- **开发模式**: 源码直接执行，支持热重载和调试
- **生产模式**: 二进制分发，支持在线发现和安装

### 🔌 **插件生态系统**
- **非侵入式**: 数据保持在用户原有应用中
- **AI能力聚合**: 支持多AI提供者统一接入
- **主动价值创造**: 智能推荐而非被动查询

### 🛡️ **安全优先**
- **多层验证**: 数字签名、权限审查、恶意代码扫描
- **渐进授权**: 用户可逐步授予插件权限
- **透明度**: 所有权限声明对用户可见

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