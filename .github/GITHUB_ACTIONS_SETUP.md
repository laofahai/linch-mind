# 🔧 GitHub Actions CI/CD Setup Guide

这个文档描述如何配置Linch Mind项目的完整CI/CD流水线。

## 📋 工作流概述

我们的CI/CD系统包含以下工作流：

| 工作流 | 触发条件 | 功能 |
|--------|---------|------|
| `connector-build.yml` | 连接器代码变更 | 构建和发布连接器 |
| `flutter-build.yml` | UI代码变更 | 构建Flutter多平台应用 |
| `daemon-build.yml` | 后端代码变更 | 构建和部署Python daemon |
| `integration-tests.yml` | 主要分支或定时 | 运行集成和E2E测试 |
| `release.yml` | 版本标签 | 完整的发布流程 |
| `build-component.yml` | 被其他工作流调用 | 可重用的组件构建 |

## 🔐 必需的Secrets配置

### Repository Secrets

在GitHub仓库设置中添加以下secrets：

```bash
# 基础认证
GITHUB_TOKEN                 # 自动提供，用于GitHub API访问

# Docker Registry (GitHub Container Registry)
GHCR_TOKEN                   # GitHub Personal Access Token (用于推送镜像)

# 应用签名 (生产发布)
ANDROID_KEYSTORE_BASE64      # Android签名密钥 (base64编码)
ANDROID_KEYSTORE_PASSWORD    # Android密钥库密码
ANDROID_KEY_ALIAS            # Android密钥别名
ANDROID_KEY_PASSWORD         # Android密钥密码

IOS_CERTIFICATE_BASE64       # iOS签名证书 (base64编码)
IOS_CERTIFICATE_PASSWORD     # iOS证书密码
IOS_PROVISIONING_PROFILE     # iOS配置文件 (base64编码)

# 部署配置
PRODUCTION_SSH_KEY           # 生产服务器SSH私钥
PRODUCTION_HOST              # 生产服务器地址
PRODUCTION_USER              # 生产服务器用户名

STAGING_SSH_KEY              # 测试服务器SSH私钥
STAGING_HOST                 # 测试服务器地址
STAGING_USER                 # 测试服务器用户名

# 第三方服务
CODECOV_TOKEN               # Codecov代码覆盖率上传
SENTRY_DSN                  # Sentry错误监控
SLACK_WEBHOOK_URL           # Slack通知webhook

# 应用商店
GOOGLE_PLAY_SERVICE_ACCOUNT # Google Play上传服务账号JSON
APPLE_CONNECT_KEY_ID        # App Store Connect API密钥ID
APPLE_CONNECT_ISSUER_ID     # App Store Connect发行者ID
APPLE_CONNECT_PRIVATE_KEY   # App Store Connect私钥
```

### Environment Variables

在GitHub仓库设置中添加以下变量：

```bash
# 服务端点
REGISTRY_URL=https://registry.linch-mind.com/v1
DAEMON_URL=https://api.linch-mind.com

# 构建配置
FLUTTER_VERSION=3.24.3
PYTHON_VERSION=3.11
NODE_VERSION=20

# Docker配置
REGISTRY=ghcr.io
IMAGE_NAME=linch-mind/daemon

# 测试配置
TEST_DATABASE_URL=postgresql://test:test123@localhost:5432/linch_mind_test
TEST_REDIS_URL=redis://localhost:6379

# 部署配置
PRODUCTION_URL=https://linch-mind.com
STAGING_URL=https://staging.linch-mind.com
```

## 🏗️ Environments配置

### staging环境

在GitHub仓库设置中创建`staging`环境：

- **保护规则**: 需要审查者批准
- **部署分支**: `main`, `develop`
- **URL**: `https://staging.linch-mind.com`

### production环境

在GitHub仓库设置中创建`production`环境：

- **保护规则**: 需要审查者批准，等待定时器（5分钟）
- **部署分支**: 仅标签 (`v*`)
- **URL**: `https://linch-mind.com`

## 📱 移动应用签名配置

### Android签名设置

1. **生成密钥库**:
   ```bash
   keytool -genkey -v -keystore linch-mind.keystore -alias linch-mind -keyalg RSA -keysize 2048 -validity 10000
   ```

2. **转换为base64**:
   ```bash
   base64 -i linch-mind.keystore | pbcopy
   ```

3. **添加到secrets**:
   - `ANDROID_KEYSTORE_BASE64`: 上述base64字符串
   - `ANDROID_KEYSTORE_PASSWORD`: 密钥库密码
   - `ANDROID_KEY_ALIAS`: linch-mind
   - `ANDROID_KEY_PASSWORD`: 密钥密码

### iOS签名设置

1. **导出开发者证书**:
   - 从Keychain Access导出.p12文件
   - 转换为base64: `base64 -i certificate.p12 | pbcopy`

2. **导出配置文件**:
   - 从Apple Developer Portal下载.mobileprovision文件
   - 转换为base64: `base64 -i profile.mobileprovision | pbcopy`

3. **添加到secrets**:
   - `IOS_CERTIFICATE_BASE64`: 证书base64字符串
   - `IOS_CERTIFICATE_PASSWORD`: 证书密码
   - `IOS_PROVISIONING_PROFILE`: 配置文件base64字符串

## 🚀 部署配置

### 生产服务器设置

1. **创建部署用户**:
   ```bash
   sudo useradd -m -s /bin/bash deploy
   sudo usermod -aG docker deploy
   ```

2. **生成SSH密钥**:
   ```bash
   ssh-keygen -t rsa -b 4096 -C "github-actions@linch-mind.com"
   ```

3. **配置authorized_keys**:
   ```bash
   mkdir -p /home/deploy/.ssh
   cat deploy_key.pub >> /home/deploy/.ssh/authorized_keys
   chmod 700 /home/deploy/.ssh
   chmod 600 /home/deploy/.ssh/authorized_keys
   chown -R deploy:deploy /home/deploy/.ssh
   ```

4. **添加私钥到secrets**:
   - `PRODUCTION_SSH_KEY`: SSH私钥内容
   - `PRODUCTION_HOST`: 服务器IP或域名
   - `PRODUCTION_USER`: deploy

### Docker Registry权限

1. **创建GitHub Personal Access Token**:
   - 权限: `write:packages`, `read:packages`
   - 添加到`GHCR_TOKEN` secret

2. **配置包访问权限**:
   - 在GitHub Package settings中设置为public或配置团队访问权限

## 🔍 监控和通知

### Codecov集成

1. **注册Codecov账号**: 连接GitHub仓库
2. **获取token**: 从Codecov仓库设置页面
3. **添加到secrets**: `CODECOV_TOKEN`

### Slack通知

1. **创建Slack App**: 在workspace中创建应用
2. **配置Incoming Webhooks**: 获取webhook URL
3. **添加到secrets**: `SLACK_WEBHOOK_URL`

### Sentry错误监控

1. **创建Sentry项目**: 为Linch Mind创建项目
2. **获取DSN**: 从项目设置页面
3. **添加到secrets**: `SENTRY_DSN`

## 🧪 测试数据库配置

### PostgreSQL测试数据库

CI/CD使用Docker服务运行PostgreSQL：

```yaml
services:
  postgres:
    image: postgres:15
    env:
      POSTGRES_PASSWORD: test
      POSTGRES_DB: linch_mind_test
    options: >-
      --health-cmd pg_isready
      --health-interval 10s
      --health-timeout 5s
      --health-retries 5
```

### Redis缓存服务

```yaml
services:
  redis:
    image: redis:7-alpine
    options: >-
      --health-cmd "redis-cli ping"
      --health-interval 10s
      --health-timeout 5s
      --health-retries 3
```

## 📦 应用商店配置

### Google Play Store

1. **创建服务账号**:
   - 在Google Cloud Console创建服务账号
   - 下载JSON密钥文件
   - 在Google Play Console中授予发布权限

2. **添加到secrets**:
   - `GOOGLE_PLAY_SERVICE_ACCOUNT`: JSON密钥文件内容

### Apple App Store

1. **创建App Store Connect API密钥**:
   - 在App Store Connect中创建API密钥
   - 下载.p8私钥文件

2. **添加到secrets**:
   - `APPLE_CONNECT_KEY_ID`: 密钥ID
   - `APPLE_CONNECT_ISSUER_ID`: 发行者ID
   - `APPLE_CONNECT_PRIVATE_KEY`: .p8文件内容

## 🔄 工作流触发器

### 自动触发

- **Push到main/develop**: 触发构建和测试
- **Pull Request**: 触发质量检查和测试
- **Tag推送** (`v*`): 触发完整发布流程
- **定时任务**: 每日凌晨2点运行完整测试套件

### 手动触发

所有工作流都支持`workflow_dispatch`手动触发：

1. **GitHub网页**: Actions → 选择工作流 → Run workflow
2. **GitHub CLI**: 
   ```bash
   gh workflow run "Flutter Build" -f platforms=linux,windows,macos
   ```
3. **API调用**:
   ```bash
   curl -X POST \
     -H "Authorization: token $GITHUB_TOKEN" \
     -H "Accept: application/vnd.github.v3+json" \
     https://api.github.com/repos/OWNER/REPO/actions/workflows/WORKFLOW_ID/dispatches \
     -d '{"ref":"main","inputs":{"environment":"staging"}}'
   ```

## 🐛 故障排除

### 常见问题

1. **构建失败**: 检查依赖版本兼容性
2. **签名失败**: 验证证书和密钥配置
3. **部署失败**: 检查SSH连接和权限
4. **测试失败**: 查看具体测试日志

### 调试技巧

1. **启用debug日志**:
   ```yaml
   env:
     ACTIONS_STEP_DEBUG: true
     ACTIONS_RUNNER_DEBUG: true
   ```

2. **SSH到runner**:
   ```yaml
   - name: Setup tmate session
     uses: mxschmitt/action-tmate@v3
   ```

3. **保存artifacts**:
   ```yaml
   - name: Upload debug logs
     uses: actions/upload-artifact@v4
     if: failure()
     with:
       name: debug-logs
       path: |
         **/*.log
         **/crash-reports/
   ```

## 📞 支持

遇到CI/CD相关问题时：

1. **查看工作流日志**: Actions tab中的详细日志
2. **检查artifacts**: 下载构建产物和测试报告
3. **提交issue**: 在GitHub仓库中创建issue
4. **社区讨论**: 在Discussions中寻求帮助

---

**注意**: 所有敏感信息都应该通过GitHub Secrets管理，永远不要在代码中硬编码密钥或密码。