#!/usr/bin/env python3
"""
连接器注册表生成脚本
用于GitHub Actions和本地开发
"""

import json
import glob
import os
import sys
import argparse
from datetime import datetime, timezone
from pathlib import Path


def generate_registry(connectors_dir: str = ".", output_file: str = "registry.json") -> dict:
    """
    生成连接器注册表
    
    Args:
        connectors_dir: connectors目录路径
        output_file: 输出文件路径
    
    Returns:
        生成的注册表字典
    """
    # 切换到connectors目录
    original_dir = os.getcwd()
    os.chdir(connectors_dir)
    
    try:
        # 扫描所有连接器配置文件（official和community）
        config_files = glob.glob('official/*/connector.json') + glob.glob('community/*/connector.json')
        print(f"Found {len(config_files)} connector configs: {config_files}")
        
        registry = {
            'schema_version': '1.0',
            'last_updated': datetime.now(timezone.utc).isoformat(),
            'connectors': {},
            'metadata': {
                'repository': os.environ.get('GITHUB_REPOSITORY', 'unknown'),
                'commit': os.environ.get('GITHUB_SHA', 'unknown'),
                'total_count': 0
            }
        }
        
        for config_path in config_files:
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                connector_id = config['id']
                connector_type = config_path.split('/')[0]  # official or community
                
                registry['connectors'][connector_id] = {
                    'id': config['id'],
                    'name': config['name'],
                    'version': config['version'],
                    'description': config['description'],
                    'author': config['author'],
                    'category': config['category'],
                    'type': connector_type,
                    'platforms': config.get('platforms', {}),
                    'permissions': config.get('permissions', []),
                    'capabilities': config.get('capabilities', {}),
                    'config_path': config_path
                }
                print(f"✅ Added {connector_id} v{config['version']} ({connector_type})")
                
            except Exception as e:
                print(f"❌ Error processing {config_path}: {e}")
                continue
        
        registry['metadata']['total_count'] = len(registry['connectors'])
        
        # 保存注册表
        with open(output_file, 'w') as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)
        
        print(f'✅ Registry generated with {len(registry["connectors"])} connectors')
        print(f'📄 Registry saved to: {output_file}')
        
        return registry
        
    finally:
        os.chdir(original_dir)


def main():
    parser = argparse.ArgumentParser(description='连接器注册表生成工具')
    parser.add_argument('--dir', default='.', help='connectors目录路径')
    parser.add_argument('--output', default='registry.json', help='输出文件名')
    parser.add_argument('--format', action='store_true', help='格式化输出')
    
    args = parser.parse_args()
    
    if not Path(args.dir).exists():
        print(f"❌ 目录不存在: {args.dir}")
        sys.exit(1)
    
    registry = generate_registry(args.dir, args.output)
    
    if args.format:
        print("\n📋 Registry Summary:")
        print(f"   Total connectors: {registry['metadata']['total_count']}")
        for connector_id, info in registry['connectors'].items():
            print(f"   - {connector_id} v{info['version']} ({info['type']})")


if __name__ == "__main__":
    main()