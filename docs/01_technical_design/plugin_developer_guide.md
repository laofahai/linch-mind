# Linch Mind 连接器插件开发者指南

## 🎯 开发者快速入门

### 📋 前置要求
- Python 3.8+
- Git
- Linch Mind Daemon (开发环境)
- IDE (推荐 VS Code with Python 扩展)

### ⚡ 5分钟创建你的第一个插件

```bash
# 1. 创建插件目录
mkdir my-awesome-connector
cd my-awesome-connector

# 2. 使用 CLI 工具生成模板 (即将提供)
linch-mind create-connector --name my-awesome --category productivity

# 3. 编辑配置文件
vim connector.json

# 4. 实现插件逻辑  
vim main.py

# 5. 本地测试
linch-mind test-connector --local

# 6. 注册到开发环境
linch-mind register-connector --dev
```

---

## 📁 插件项目结构

### 🗂️ 标准目录布局
```bash
my-awesome-connector/
├── connector.json          # 插件元数据和配置
├── main.py                 # 插件入口点
├── requirements.txt        # Python 依赖
├── README.md              # 插件说明文档
├── tests/                 # 测试文件
│   ├── __init__.py
│   ├── test_connector.py
│   └── test_config.py
├── examples/              # 配置示例
│   ├── basic_config.json
│   └── advanced_config.json
└── build_executable.py    # 生产环境构建脚本
```

### 📄 核心文件详解

#### `connector.json` - 插件清单文件
```json
{
  "$schema": "../../connector.schema.json",
  "id": "my-awesome",
  "name": "我的超棒连接器",
  "version": "1.0.0",
  "author": "Your Name <your.email@example.com>",
  "description": "这个连接器做了一些超棒的事情",
  "license": "MIT",
  "homepage": "https://github.com/your-org/my-awesome-connector",
  "category": "productivity",
  "icon": "rocket",
  
  "entry": {
    "development": {
      "command": "python3",
      "args": ["main.py"],
      "working_dir": "."
    },
    "production": {
      "windows": "my-awesome-connector.exe",
      "macos": "my-awesome-connector",
      "linux": "my-awesome-connector"
    }
  },
  
  "permissions": [
    "network:external",
    "filesystem:read"
  ],
  
  "platforms": {
    "windows": { "min_version": "10" },
    "macos": { "min_version": "10.15" },
    "linux": { "min_version": "ubuntu-20.04" }
  },
  
  "capabilities": {
    "supports_multiple_instances": true,
    "max_instances": 5,
    "hot_reload": true
  },
  
  "build": {
    "pre_build": "pip install -r requirements.txt",
    "build_command": "pyinstaller --onefile --name my-awesome-connector main.py",
    "post_build": "echo 'Build completed'"
  },
  
  "config_schema": {
    "type": "object",
    "required": ["api_key"],
    "properties": {
      "api_key": {
        "type": "string",
        "description": "API密钥",
        "minLength": 10
      },
      "sync_interval": {
        "type": "integer",
        "description": "同步间隔（秒）",
        "default": 300,
        "minimum": 60,
        "maximum": 3600
      },
      "enable_notifications": {
        "type": "boolean",
        "description": "启用通知",
        "default": true
      }
    }
  }
}
```

#### `main.py` - 插件核心逻辑
```python
#!/usr/bin/env python3
"""
我的超棒连接器 - 主要逻辑实现
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

# 导入 Linch Mind 连接器基础类
from shared.base import BaseConnector
from shared.config import ConnectorConfig

logger = logging.getLogger(__name__)


class MyAwesomeConnector(BaseConnector):
    """我的超棒连接器实现"""
    
    def __init__(self, config: ConnectorConfig):
        super().__init__(config)
        self.api_key = config.get_required("api_key")
        self.sync_interval = config.get("sync_interval", 300)
        self.enable_notifications = config.get("enable_notifications", True)
        
        # 初始化连接器特有的状态
        self.last_sync_time: Optional[datetime] = None
        self.is_running = False
    
    async def initialize(self) -> bool:
        """初始化连接器"""
        try:
            logger.info(f"初始化 {self.connector_id} 连接器...")
            
            # 验证 API 密钥
            if not await self._validate_api_key():
                logger.error("API密钥验证失败")
                return False
            
            # 建立外部服务连接
            await self._connect_to_service()
            
            logger.info("连接器初始化成功")
            return True
            
        except Exception as e:
            logger.error(f"连接器初始化失败: {e}")
            return False
    
    async def start(self) -> bool:
        """启动连接器"""
        try:
            logger.info(f"启动 {self.connector_id} 连接器...")
            
            if not await self.initialize():
                return False
            
            self.is_running = True
            
            # 启动主要的工作循环
            asyncio.create_task(self._main_loop())
            
            # 注册健康检查
            await self.register_health_check(self._health_check)
            
            logger.info("连接器启动成功")
            return True
            
        except Exception as e:
            logger.error(f"连接器启动失败: {e}")
            return False
    
    async def stop(self) -> bool:
        """停止连接器"""
        try:
            logger.info(f"停止 {self.connector_id} 连接器...")
            
            self.is_running = False
            
            # 清理资源
            await self._cleanup_resources()
            
            logger.info("连接器停止成功")
            return True
            
        except Exception as e:
            logger.error(f"连接器停止失败: {e}")
            return False
    
    async def _main_loop(self):
        """主要工作循环"""
        while self.is_running:
            try:
                # 执行数据同步
                await self._sync_data()
                
                # 发送心跳
                await self.send_heartbeat()
                
                # 等待下次同步
                await asyncio.sleep(self.sync_interval)
                
            except Exception as e:
                logger.error(f"主循环执行错误: {e}")
                await asyncio.sleep(60)  # 错误时等待1分钟再重试
    
    async def _sync_data(self):
        """同步数据的核心逻辑"""
        try:
            logger.debug("开始数据同步...")
            
            # 1. 从外部服务获取数据
            data = await self._fetch_external_data()
            
            # 2. 处理和清洗数据
            processed_data = await self._process_data(data)
            
            # 3. 发送给 Daemon
            for item in processed_data:
                await self.send_data(item)
            
            # 4. 更新同步时间
            self.last_sync_time = datetime.now()
            
            logger.debug(f"数据同步完成，处理了 {len(processed_data)} 条记录")
            
        except Exception as e:
            logger.error(f"数据同步失败: {e}")
            raise
    
    async def _fetch_external_data(self) -> list:
        """从外部服务获取数据"""
        # 实现具体的数据获取逻辑
        # 这里是示例代码
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            async with session.get("https://api.example.com/data", headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"API请求失败: {response.status}")
    
    async def _process_data(self, raw_data: list) -> list:
        """处理和清洗数据"""
        processed = []
        
        for item in raw_data:
            # 转换为 Linch Mind 标准数据格式
            processed_item = {
                "entity_type": "document",
                "title": item.get("title", ""),
                "content": item.get("content", ""),
                "metadata": {
                    "source": "my-awesome-connector",
                    "external_id": item.get("id"),
                    "created_at": item.get("created_at"),
                    "tags": item.get("tags", [])
                }
            }
            processed.append(processed_item)
        
        return processed
    
    async def _validate_api_key(self) -> bool:
        """验证 API 密钥"""
        # 实现 API 密钥验证逻辑
        return len(self.api_key) >= 10
    
    async def _connect_to_service(self):
        """建立外部服务连接"""
        # 实现服务连接逻辑
        pass
    
    async def _cleanup_resources(self):
        """清理资源"""
        # 实现资源清理逻辑
        pass
    
    async def _health_check(self) -> Dict[str, Any]:
        """健康检查"""
        return {
            "status": "healthy" if self.is_running else "stopped",
            "last_sync_time": self.last_sync_time.isoformat() if self.last_sync_time else None,
            "api_key_valid": await self._validate_api_key(),
            "sync_interval": self.sync_interval
        }
    
    async def reload_config(self, new_config: ConnectorConfig) -> bool:
        """热重载配置"""
        try:
            logger.info("重新加载配置...")
            
            # 更新配置
            old_sync_interval = self.sync_interval
            self.sync_interval = new_config.get("sync_interval", 300)
            self.enable_notifications = new_config.get("enable_notifications", True)
            
            # 如果同步间隔改变，记录日志
            if old_sync_interval != self.sync_interval:
                logger.info(f"同步间隔从 {old_sync_interval} 秒改为 {self.sync_interval} 秒")
            
            return True
            
        except Exception as e:
            logger.error(f"配置重载失败: {e}")
            return False


async def main():
    """连接器入口点"""
    try:
        # 加载配置
        config = ConnectorConfig.from_env()
        
        # 创建连接器实例
        connector = MyAwesomeConnector(config)
        
        # 启动连接器
        if await connector.start():
            # 保持运行
            await connector.run_forever()
        else:
            logger.error("连接器启动失败")
            exit(1)
            
    except KeyboardInterrupt:
        logger.info("收到停止信号，正在关闭连接器...")
    except Exception as e:
        logger.error(f"连接器运行失败: {e}")
        exit(1)


if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 运行连接器
    asyncio.run(main())
```

---

## 🧪 测试和调试

### 🔍 本地开发测试
```python
# tests/test_connector.py
import pytest
import asyncio
from unittest.mock import AsyncMock, patch

from main import MyAwesomeConnector
from shared.config import ConnectorConfig


@pytest.fixture
def mock_config():
    return ConnectorConfig({
        "api_key": "test_api_key_12345",
        "sync_interval": 60,
        "enable_notifications": True
    })


@pytest.mark.asyncio
async def test_connector_initialization(mock_config):
    """测试连接器初始化"""
    connector = MyAwesomeConnector(mock_config)
    
    with patch.object(connector, '_validate_api_key', return_value=True):
        with patch.object(connector, '_connect_to_service'):
            result = await connector.initialize()
            assert result is True


@pytest.mark.asyncio
async def test_data_sync(mock_config):
    """测试数据同步"""
    connector = MyAwesomeConnector(mock_config)
    
    # Mock 外部 API 响应
    mock_data = [
        {"id": "1", "title": "Test Document", "content": "Test content"}
    ]
    
    with patch.object(connector, '_fetch_external_data', return_value=mock_data):
        with patch.object(connector, 'send_data') as mock_send:
            await connector._sync_data()
            
            # 验证数据被正确发送
            mock_send.assert_called_once()
            sent_data = mock_send.call_args[0][0]
            assert sent_data["title"] == "Test Document"


@pytest.mark.asyncio 
async def test_config_reload(mock_config):
    """测试配置热重载"""
    connector = MyAwesomeConnector(mock_config)
    
    new_config = ConnectorConfig({
        "api_key": "test_api_key_12345",
        "sync_interval": 120,  # 改变同步间隔
        "enable_notifications": False
    })
    
    result = await connector.reload_config(new_config)
    assert result is True
    assert connector.sync_interval == 120
    assert connector.enable_notifications is False
```

### 🎮 调试技巧
```bash
# 启用详细日志
export LINCH_MIND_LOG_LEVEL=DEBUG

# 单步调试模式
export LINCH_MIND_DEBUG_MODE=true

# 使用 pdb 调试
python -m pdb main.py

# 使用 VS Code 调试配置
# .vscode/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug Connector",
            "type": "python",
            "request": "launch",
            "program": "main.py",
            "env": {
                "LINCH_MIND_DEV_MODE": "true",
                "LINCH_MIND_LOG_LEVEL": "DEBUG"
            }
        }
    ]
}
```

---

## 📦 生产环境构建

### 🏗️ 构建脚本
```python
# build_executable.py
#!/usr/bin/env python3
"""
生产环境构建脚本
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def build_executable():
    """构建可执行文件"""
    current_platform = platform.system().lower()
    
    # 安装依赖
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    
    # 构建命令
    build_cmd = [
        "pyinstaller",
        "--onefile",
        "--name", f"my-awesome-connector",
        "--add-data", "connector.json:.",
        "main.py"
    ]
    
    # 平台特定配置
    if current_platform == "windows":
        build_cmd.append("--console")
    elif current_platform == "darwin":
        build_cmd.extend(["--osx-bundle-identifier", "com.linch-mind.connector.my-awesome"])
    
    # 执行构建
    subprocess.run(build_cmd, check=True)
    
    print(f"构建完成: dist/my-awesome-connector{'exe' if current_platform == 'windows' else ''}")


if __name__ == "__main__":
    build_executable()
```

### 🚀 CI/CD 集成
```yaml
# .github/workflows/build-connector.yml
name: Build My Awesome Connector

on:
  push:
    tags: ['v*']
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio
      
      - name: Run tests
        run: pytest tests/
  
  build:
    needs: test
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
    runs-on: ${{ matrix.os }}
    
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pyinstaller
      
      - name: Build executable
        run: python build_executable.py
      
      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: my-awesome-connector-${{ matrix.os }}
          path: dist/
```

---

## 📚 最佳实践

### ✨ 代码质量
```python
# 1. 使用类型提示
from typing import Dict, List, Optional, Any

async def process_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """处理数据时提供明确的类型信息"""

# 2. 丰富的日志记录
logger.info("开始处理数据", extra={"data_count": len(data)})
logger.debug("API响应", extra={"response": response_data})
logger.error("处理失败", extra={"error": str(e)}, exc_info=True)

# 3. 优雅的错误处理
try:
    result = await risky_operation()
except SpecificException as e:
    logger.warning(f"预期的错误: {e}")
    # 优雅降级
    result = default_value
except Exception as e:
    logger.error(f"未预期的错误: {e}")
    raise
```

### 🔐 安全考虑
```python
# 1. 敏感信息处理
def __init__(self, config: ConnectorConfig):
    self.api_key = config.get_required("api_key")
    # 不要在日志中输出敏感信息
    logger.info(f"初始化连接器，API密钥长度: {len(self.api_key)}")

# 2. 输入验证
def validate_input(self, data: Any) -> bool:
    """验证输入数据的安全性"""
    if not isinstance(data, dict):
        return False
    
    # 检查必需字段
    required_fields = ["title", "content"]
    if not all(field in data for field in required_fields):
        return False
    
    # 长度限制
    if len(data.get("content", "")) > 1000000:  # 1MB限制
        return False
    
    return True

# 3. 权限最小化原则
# 在 connector.json 中只声明必需的权限
"permissions": [
    "network:external",  # 仅访问外部网络
    "filesystem:read"    # 仅读取文件系统
]
```

### 🚀 性能优化
```python
# 1. 异步操作
async def process_multiple_items(self, items: List[Any]):
    """并发处理多个项目"""
    tasks = [self.process_single_item(item) for item in items]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 处理结果和异常
    success_count = sum(1 for r in results if not isinstance(r, Exception))
    logger.info(f"处理完成: {success_count}/{len(items)} 成功")

# 2. 缓存机制
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_computation(self, input_data: str) -> str:
    """缓存昂贵的计算结果"""
    # 复杂计算逻辑
    return result

# 3. 批量操作
async def send_data_batch(self, items: List[Dict[str, Any]]):
    """批量发送数据，提高效率"""
    batch_size = 100
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        await self.daemon_client.send_batch(batch)
```

---

## 🛠️ 开发工具和 CLI

### 🎯 Linch Mind CLI (计划中)
```bash
# 创建新连接器
linch-mind create-connector my-awesome-connector --template basic

# 验证连接器配置
linch-mind validate-connector ./my-awesome-connector

# 本地测试连接器
linch-mind test-connector ./my-awesome-connector --config test-config.json

# 构建生产版本
linch-mind build-connector ./my-awesome-connector --platform all

# 发布到注册表
linch-mind publish-connector ./my-awesome-connector --registry official
```

### 🔧 开发环境设置
```bash
# 设置开发环境
export LINCH_MIND_DEV_MODE=true
export LINCH_MIND_DAEMON_URL=http://localhost:8088
export LINCH_MIND_LOG_LEVEL=DEBUG

# 启动 Daemon (开发模式)
cd linch-mind/daemon
python -m api.main --dev

# 在另一个终端启动连接器
cd my-awesome-connector  
python main.py
```

---

## 📖 社区和支持

### 🤝 社区资源
- **官方文档**: https://docs.linch-mind.com/connectors
- **GitHub 仓库**: https://github.com/linch-mind/connectors
- **社区论坛**: https://community.linch-mind.com
- **Discord 群组**: https://discord.gg/linch-mind

### 💬 获取帮助
- **Bug 报告**: GitHub Issues
- **功能请求**: GitHub Discussions
- **技术支持**: community@linch-mind.com
- **开发者文档**: https://dev.linch-mind.com

### 🎉 贡献指南
1. **Fork** 官方连接器仓库
2. **创建** 功能分支 (`git checkout -b feature/awesome-connector`)
3. **提交** 更改 (`git commit -m 'Add awesome connector'`)
4. **推送** 到分支 (`git push origin feature/awesome-connector`)
5. **创建** Pull Request

---

## 🏆 成功案例

### 📊 官方连接器参考
- **文件系统连接器**: `connectors/official/filesystem/`
- **剪贴板连接器**: `connectors/official/clipboard/`
- **Notion 连接器**: `connectors/official/notion/` (计划中)
- **Slack 连接器**: `connectors/official/slack/` (计划中)

### 🌟 社区连接器展示
- **Chrome 书签同步**: 同步浏览器书签到知识图谱
- **Todoist 集成**: 导入任务和项目管理数据
- **Gmail 智能分析**: 提取邮件中的关键信息和联系人

通过遵循这个开发者指南，你可以快速创建高质量、安全可靠的 Linch Mind 连接器插件，为用户提供丰富的数据连接能力。