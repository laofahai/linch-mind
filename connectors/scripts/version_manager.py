#!/usr/bin/env python3
"""
连接器版本管理脚本
用于GitHub Actions和本地开发
"""

import json
import sys
import argparse
from pathlib import Path


def bump_version(config_file: str, bump_type: str = "patch") -> str:
    """
    递增连接器版本号
    
    Args:
        config_file: connector.json文件路径
        bump_type: 版本递增类型 (major, minor, patch)
    
    Returns:
        新版本号
    """
    with open(config_file, 'r') as f:
        data = json.load(f)

    current_version = data.get('version', '0.0.1')
    parts = list(map(int, current_version.split('.')))
    
    if len(parts) < 3:
        parts = [0, 0, 1]
    
    if bump_type == 'major':
        parts[0] += 1
        parts[1] = 0
        parts[2] = 0
    elif bump_type == 'minor':
        parts[1] += 1
        parts[2] = 0
    else:  # patch
        parts[2] += 1
    
    new_version = '.'.join(map(str, parts))
    
    print(f"Bumping {config_file}: {current_version} -> {new_version}")
    
    # 更新 connector.json
    data['version'] = new_version
    with open(config_file, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Updated {data['id']} to version {new_version}")
    return new_version


def main():
    parser = argparse.ArgumentParser(description='连接器版本管理工具')
    parser.add_argument('config_file', help='connector.json文件路径')
    parser.add_argument('--bump', choices=['major', 'minor', 'patch'], 
                       default='patch', help='版本递增类型')
    
    args = parser.parse_args()
    
    if not Path(args.config_file).exists():
        print(f"❌ 配置文件不存在: {args.config_file}")
        sys.exit(1)
    
    new_version = bump_version(args.config_file, args.bump)
    print(new_version)  # 输出新版本号供shell脚本使用


if __name__ == "__main__":
    main()