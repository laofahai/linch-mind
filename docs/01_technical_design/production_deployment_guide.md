# Linch Mind 生产环境部署指南

## 🎯 部署架构概览

Linch Mind 生产环境采用**分布式插件生态架构**，包含以下核心组件：

```bash
🌐 Linch Mind 生产环境架构
├── 📱 客户端应用 (Flutter Desktop/Mobile)
├── 🚀 Daemon 服务 (Python FastAPI)
├── 🔌 插件注册表 (GitHub/CDN)
├── 📦 插件分发系统 (CI/CD Pipeline)
└── 🛡️ 安全验证服务 (数字签名/恶意代码扫描)
```

---

## 🏗️ 基础设施要求

### 💻 服务器规格
```yaml
# 生产环境推荐配置
Daemon 服务器:
  CPU: 4核 (推荐 8核)
  内存: 8GB (推荐 16GB)
  存储: 100GB SSD (推荐 500GB)
  网络: 100Mbps (推荐 1Gbps)
  操作系统: Ubuntu 22.04 LTS / CentOS 8 / Amazon Linux 2

插件注册表服务:
  CPU: 2核
  内存: 4GB
  存储: 50GB SSD
  网络: CDN分发 (CloudFlare/AWS CloudFront)
  
CI/CD构建集群:
  GitHub Actions (推荐)
  或 Jenkins + Docker Swarm
  或 GitLab CI/CD
```

### 🌐 网络和域名
```bash
# 推荐域名结构
主应用: https://app.linch-mind.com
API服务: https://api.linch-mind.com
插件注册表: https://registry.linch-mind.com
插件分发: https://cdn.linch-mind.com
开发者文档: https://dev.linch-mind.com
```

---

## 🚀 Daemon 服务部署

### 🐳 Docker 容器化部署
```dockerfile
# Dockerfile.daemon
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY daemon/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY daemon/ .

# 创建非root用户
RUN useradd -m -u 1000 linch && chown -R linch:linch /app
USER linch

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8088/health || exit 1

# 启动命令
CMD ["python", "-m", "api.main", "--host", "0.0.0.0", "--port", "8088"]
```

### 🔧 Docker Compose 配置
```yaml
# docker-compose.production.yml
version: '3.8'

services:
  linch-daemon:
    build:
      context: .
      dockerfile: Dockerfile.daemon
    ports:
      - "8088:8088"
    environment:
      - LINCH_MIND_ENV=production
      - LINCH_MIND_DATABASE_URL=sqlite:///data/linch_mind.db
      - LINCH_MIND_LOG_LEVEL=INFO
      - LINCH_MIND_PLUGIN_REGISTRY_URL=https://registry.linch-mind.com
    volumes:
      - linch_data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8088/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
      - ./logs/nginx:/var/log/nginx
    depends_on:
      - linch-daemon
    restart: unless-stopped

volumes:
  linch_data:
    driver: local
```

### ⚙️ Nginx 反向代理配置
```nginx
# nginx/nginx.conf
upstream linch_daemon {
    server linch-daemon:8088;
}

server {
    listen 80;
    server_name api.linch-mind.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.linch-mind.com;
    
    ssl_certificate /etc/nginx/ssl/linch-mind.crt;
    ssl_certificate_key /etc/nginx/ssl/linch-mind.key;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_stapling on;
    ssl_stapling_verify on;
    
    # 安全headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    
    # API代理
    location / {
        proxy_pass http://linch_daemon;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # 静态文件
    location /static/ {
        alias /app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # 健康检查
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

---

## 📦 插件注册表系统

### 🏗️ 注册表服务架构
```python
# registry_service.py - 插件注册表微服务
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import asyncio
import json
from pathlib import Path

app = FastAPI(title="Linch Mind Plugin Registry", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.linch-mind.com", "https://dev.linch-mind.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class PluginRegistryService:
    """插件注册表服务"""
    
    def __init__(self):
        self.registry_data = {}
        self.cache_ttl = 300  # 5分钟缓存
        asyncio.create_task(self.load_registry_data())
    
    async def load_registry_data(self):
        """从GitHub/CDN加载注册表数据"""
        while True:
            try:
                # 从多个源加载插件数据
                official_plugins = await self.load_from_github("linch-mind/official-connectors")
                community_plugins = await self.load_from_github("linch-mind/community-connectors")
                
                self.registry_data = {
                    "official": official_plugins,
                    "community": community_plugins,
                    "last_updated": datetime.now().isoformat()
                }
                
                logger.info(f"注册表数据更新完成: {len(official_plugins + community_plugins)} 个插件")
                
            except Exception as e:
                logger.error(f"注册表数据加载失败: {e}")
            
            await asyncio.sleep(self.cache_ttl)
    
    async def load_from_github(self, repo: str) -> List[dict]:
        """从GitHub仓库加载插件信息"""
        # 实现GitHub API调用逻辑
        pass


registry_service = PluginRegistryService()


@app.get("/discovery")
async def discover_plugins(
    category: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50
):
    """发现插件"""
    plugins = []
    
    # 合并官方和社区插件
    all_plugins = (
        registry_service.registry_data.get("official", []) +
        registry_service.registry_data.get("community", [])
    )
    
    # 过滤
    if category:
        all_plugins = [p for p in all_plugins if p.get("category") == category]
    
    if search:
        search_lower = search.lower()
        all_plugins = [p for p in all_plugins 
                      if search_lower in p.get("name", "").lower() 
                      or search_lower in p.get("description", "").lower()]
    
    return {
        "plugins": all_plugins[:limit],
        "total_count": len(all_plugins),
        "last_updated": registry_service.registry_data.get("last_updated")
    }


@app.get("/plugin/{plugin_id}")
async def get_plugin_details(plugin_id: str):
    """获取插件详细信息"""
    # 实现插件详情查询
    pass


@app.get("/plugin/{plugin_id}/download/{version}")
async def download_plugin(plugin_id: str, version: str, platform: str):
    """下载插件包"""
    # 实现插件下载逻辑
    pass
```

### 🔄 CI/CD 插件构建流水线
```yaml
# .github/workflows/plugin-release-pipeline.yml
name: Plugin Release Pipeline

on:
  push:
    tags: ['connectors/*/v*']
  workflow_dispatch:
    inputs:
      connector_name:
        description: 'Connector name to build'
        required: true
      version:
        description: 'Version to release'
        required: true

env:
  REGISTRY_URL: https://registry.linch-mind.com
  CDN_URL: https://cdn.linch-mind.com

jobs:
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      matrix: ${{ steps.set-matrix.outputs.matrix }}
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 2
      
      - name: Detect changed connectors
        id: set-matrix
        run: |
          # 检测哪些连接器发生了变化
          if [[ $GITHUB_REF =~ refs/tags/connectors/([^/]+)/v(.+) ]]; then
            connector="${BASH_REMATCH[1]}"
            version="${BASH_REMATCH[2]}"
            echo "matrix={\"include\":[{\"connector\":\"$connector\",\"version\":\"$version\"}]}" >> $GITHUB_OUTPUT
          else
            # 检测所有变化的连接器
            changed_connectors=$(git diff --name-only HEAD~1 HEAD | grep "^connectors/" | cut -d'/' -f2 | sort -u)
            matrix_json=$(echo "$changed_connectors" | jq -R -s -c 'split("\n")[:-1] | map({connector: ., version: "auto"})')
            echo "matrix={\"include\":$matrix_json}" >> $GITHUB_OUTPUT
          fi

  build-and-test:
    needs: detect-changes
    if: needs.detect-changes.outputs.matrix != ''
    strategy:
      matrix: ${{ fromJson(needs.detect-changes.outputs.matrix) }}
      fail-fast: false
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r connectors/requirements.txt
          pip install pytest pytest-asyncio pyinstaller
      
      - name: Validate connector
        run: |
          python scripts/validate_connector.py connectors/official/${{ matrix.connector }}
      
      - name: Run tests
        run: |
          cd connectors/official/${{ matrix.connector }}
          if [ -f "tests/test_*.py" ]; then
            pytest tests/
          fi
      
      - name: Security scan
        run: |
          python scripts/security_scan.py connectors/official/${{ matrix.connector }}

  build-multiplatform:
    needs: [detect-changes, build-and-test]
    strategy:
      matrix:
        connector: ${{ fromJson(needs.detect-changes.outputs.matrix).include[*].connector }}
        platform: [ubuntu-latest, windows-latest, macos-latest]
    runs-on: ${{ matrix.platform }}
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Build binary
        run: |
          cd connectors/official/${{ matrix.connector }}
          pip install -r requirements.txt
          pip install pyinstaller
          python build_executable.py
      
      - name: Code signing (Windows)
        if: matrix.platform == 'windows-latest'
        run: |
          # Windows代码签名
          signtool sign /f ${{ secrets.WIN_CERTIFICATE }} /p ${{ secrets.WIN_CERT_PASSWORD }} dist/*.exe
      
      - name: Code signing (macOS)
        if: matrix.platform == 'macos-latest'
        run: |
          # macOS代码签名
          codesign --force --options runtime --sign "${{ secrets.MACOS_CERTIFICATE }}" dist/*
      
      - name: Generate package metadata
        run: |
          python scripts/generate_package_metadata.py \
            --connector ${{ matrix.connector }} \
            --platform ${{ runner.os }} \
            --binary-path dist/
      
      - name: Upload to artifact
        uses: actions/upload-artifact@v3
        with:
          name: ${{ matrix.connector }}-${{ runner.os }}
          path: |
            dist/
            metadata/

  publish-to-registry:
    needs: [detect-changes, build-multiplatform]
    runs-on: ubuntu-latest
    if: startsWith(github.ref, 'refs/tags/')
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Download all artifacts
        uses: actions/download-artifact@v3
        with:
          path: artifacts/
      
      - name: Prepare release package
        run: |
          python scripts/prepare_release_package.py \
            --artifacts-dir artifacts/ \
            --output-dir release/
      
      - name: Upload to CDN
        run: |
          python scripts/upload_to_cdn.py \
            --release-dir release/ \
            --cdn-url ${{ env.CDN_URL }} \
            --api-key ${{ secrets.CDN_API_KEY }}
      
      - name: Update registry
        run: |
          python scripts/update_registry.py \
            --registry-url ${{ env.REGISTRY_URL }} \
            --release-info release/metadata.json \
            --api-key ${{ secrets.REGISTRY_API_KEY }}
      
      - name: Create GitHub release
        uses: softprops/action-gh-release@v1
        with:
          files: release/*
          generate_release_notes: true
          tag_name: ${{ github.ref_name }}
```

---

## 🛡️ 安全和监控

### 🔐 安全配置
```python
# security_config.py
SECURITY_CONFIG = {
    "api_rate_limits": {
        "discovery": "100/minute",
        "download": "50/minute", 
        "upload": "10/minute"
    },
    
    "plugin_validation": {
        "require_digital_signature": True,
        "malware_scan_enabled": True,
        "max_package_size_mb": 100,
        "allowed_file_types": [".py", ".json", ".txt", ".md"]
    },
    
    "user_permissions": {
        "allow_unsigned_plugins": False,
        "require_user_confirmation": True,
        "sandbox_execution": True
    }
}
```

### 📊 监控和日志
```yaml
# monitoring/docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./grafana/datasources:/etc/grafana/provisioning/datasources

  loki:
    image: grafana/loki:latest
    ports:
      - "3100:3100"
    volumes:
      - ./loki/loki-config.yml:/etc/loki/local-config.yaml
    command: -config.file=/etc/loki/local-config.yaml

  promtail:
    image: grafana/promtail:latest
    volumes:
      - /var/log:/var/log:ro
      - ./logs:/app/logs:ro
      - ./promtail/promtail-config.yml:/etc/promtail/config.yml
    command: -config.file=/etc/promtail/config.yml

volumes:
  prometheus_data:
  grafana_data:
```

---

## 🚀 部署脚本和自动化

### 📦 一键部署脚本
```bash
#!/bin/bash
# deploy.sh - Linch Mind生产环境一键部署脚本

set -e

# 配置
DEPLOY_ENV=${1:-production}
DOMAIN=${2:-api.linch-mind.com}
EMAIL=${3:-admin@linch-mind.com}

echo "🚀 开始部署 Linch Mind 到 $DEPLOY_ENV 环境..."

# 1. 系统更新和依赖安装
echo "📦 安装系统依赖..."
sudo apt-get update
sudo apt-get install -y docker.io docker-compose-plugin nginx certbot python3-certbot-nginx

# 2. 克隆代码
echo "📥 获取最新代码..."
if [ ! -d "/opt/linch-mind" ]; then
    sudo git clone https://github.com/linch-mind/linch-mind.git /opt/linch-mind
else
    cd /opt/linch-mind && sudo git pull
fi

cd /opt/linch-mind

# 3. 环境配置
echo "⚙️ 配置环境..."
sudo cp deployment/production.env .env
sudo cp deployment/docker-compose.production.yml docker-compose.yml

# 4. SSL证书
echo "🔒 配置SSL证书..."
if [ ! -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    sudo certbot certonly --nginx -d $DOMAIN --email $EMAIL --agree-tos --non-interactive
fi

# 5. 启动服务
echo "🎯 启动服务..."
sudo docker compose down || true
sudo docker compose build
sudo docker compose up -d

# 6. 验证部署
echo "✅ 验证部署状态..."
sleep 30

if curl -f http://localhost:8088/health > /dev/null 2>&1; then
    echo "✅ Daemon服务启动成功"
else
    echo "❌ Daemon服务启动失败"
    exit 1
fi

if curl -f https://$DOMAIN/health > /dev/null 2>&1; then
    echo "✅ HTTPS访问正常"
else
    echo "❌ HTTPS访问失败"
    exit 1
fi

echo "🎉 部署完成！"
echo "📊 监控面板: https://$DOMAIN:3000"
echo "📊 API文档: https://$DOMAIN/docs"
echo "📋 健康检查: https://$DOMAIN/health"
```

### 🔄 更新脚本
```bash
#!/bin/bash
# update.sh - 零停机更新脚本

echo "🔄 开始零停机更新..."

# 1. 拉取最新代码
git pull

# 2. 构建新镜像
docker compose build

# 3. 滚动更新
docker compose up -d --no-deps --build linch-daemon

# 4. 验证新版本
sleep 15
if curl -f http://localhost:8088/health; then
    echo "✅ 更新成功"
    # 清理旧镜像
    docker image prune -f
else
    echo "❌ 更新失败，回滚..."
    docker compose rollback
fi
```

---

## 📈 性能优化

### ⚡ 性能配置
```python
# performance_config.py
PERFORMANCE_CONFIG = {
    "daemon": {
        "worker_processes": 4,
        "max_connections": 1000,
        "keepalive_timeout": 65,
        "client_max_body_size": "100M"
    },
    
    "database": {
        "pool_size": 20,
        "max_overflow": 30,
        "pool_pre_ping": True,
        "pool_recycle": 3600
    },
    
    "caching": {
        "plugin_registry_ttl": 300,
        "api_response_ttl": 60,
        "enable_compression": True
    }
}
```

### 🗄️ 数据库优化
```sql
-- 生产环境数据库优化
-- 创建索引
CREATE INDEX idx_plugins_category ON plugins(category);
CREATE INDEX idx_plugins_updated_at ON plugins(updated_at);
CREATE INDEX idx_download_stats_plugin_id ON download_stats(plugin_id);

-- 分区表（可选）
CREATE TABLE plugin_downloads_2025 PARTITION OF plugin_downloads
FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
```

---

## 🚨 故障排除和维护

### 🔍 常见问题诊断
```bash
# 健康检查脚本
#!/bin/bash
# health_check.sh

echo "🏥 Linch Mind 健康检查报告"
echo "=================================="

# 1. 服务状态
echo "📊 服务状态:"
docker compose ps

# 2. 磁盘使用
echo "💾 磁盘使用:"
df -h

# 3. 内存使用
echo "🧠 内存使用:"
free -h

# 4. 网络连通性
echo "🌐 网络检查:"
curl -s -o /dev/null -w "Daemon API: %{http_code}\n" http://localhost:8088/health
curl -s -o /dev/null -w "Registry API: %{http_code}\n" https://registry.linch-mind.com/health

# 5. 最近日志
echo "📝 最近错误日志:"
docker compose logs --tail=20 linch-daemon | grep ERROR || echo "无错误日志"

echo "=================================="
echo "✅ 健康检查完成"
```

### 🛠️ 维护任务
```bash
# maintenance.sh - 定期维护脚本
#!/bin/bash

# 日志轮转
docker compose exec linch-daemon logrotate /etc/logrotate.conf

# 数据库清理
docker compose exec linch-daemon python scripts/cleanup_old_data.py --days=90

# 清理Docker资源
docker system prune -f

# 备份重要数据
docker compose exec linch-daemon python scripts/backup_data.py --destination s3://backups/
```

---

## 📋 运维检查清单

### 🎯 部署前检查
- [ ] 服务器资源充足
- [ ] 域名和DNS配置正确
- [ ] SSL证书有效
- [ ] 防火墙规则配置
- [ ] 备份策略就绪
- [ ] 监控系统部署

### 🔄 部署后验证
- [ ] 所有服务启动正常
- [ ] API接口响应正常
- [ ] 插件发现功能工作
- [ ] 监控指标正常
- [ ] 日志输出正常
- [ ] 性能指标达标

### 📊 定期维护
- [ ] 每日：健康检查和日志审查
- [ ] 每周：性能报告和容量规划
- [ ] 每月：安全更新和依赖升级
- [ ] 每季度：备份恢复测试和灾难演练

通过这个完整的生产环境部署指南，Linch Mind可以在生产环境中稳定、安全、高效地运行，为用户提供可靠的插件生态系统服务。