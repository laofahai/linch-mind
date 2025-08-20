#!/usr/bin/env python3
"""
Linch Mind Daemon - 简化启动入口
架构优化后的精简版main.py，仅保留启动逻辑
"""

import sys
import asyncio
import logging

# 使用新的应用启动器
from core.application_bootstrap import ApplicationBootstrap

logger = logging.getLogger(__name__)


def main():
    """主函数 - 架构优化后的精简版
    
    从原来的600+行精简到<30行
    所有复杂逻辑已模块化:
    - 配置管理 → config.config_manager
    - 服务注册 → core.service_registry  
    - 启动流程 → core.application_bootstrap
    """
    
    try:
        # 创建应用启动器并运行
        bootstrap = ApplicationBootstrap()
        asyncio.run(bootstrap.run())
        
    except KeyboardInterrupt:
        logger.info("收到中断信号，应用已退出")
    except Exception as e:
        logger.error(f"应用启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()