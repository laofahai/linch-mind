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
import hashlib
from datetime import datetime, timezone
from pathlib import Path


def generate_registry(connectors_dir: str = ".", output_file: str = "registry.json") -> dict:
    """
    生成连接器注册表，支持增量更新
    
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
        
        # 读取现有注册表（如果存在）
        existing_registry = {}
        if os.path.exists(output_file):
            try:
                with open(output_file, 'r') as f:
                    existing_registry = json.load(f)
                print(f"📖 Loaded existing registry with {len(existing_registry.get('connectors', {}))} connectors")
            except Exception as e:
                print(f"⚠️ Failed to load existing registry: {e}, creating new one")
        
        # 初始化新注册表结构
        registry = {
            'schema_version': '1.0',
            'last_updated': datetime.now(timezone.utc).isoformat(),
            'connectors': existing_registry.get('connectors', {}),
            'metadata': {
                'repository': os.environ.get('GITHUB_REPOSITORY', 'laofahai/linch-mind'),
                'commit': os.environ.get('GITHUB_SHA', 'unknown'),
                'total_count': 0
            }
        }
        
        # 处理每个连接器配置
        for config_path in config_files:
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                connector_id = config['id']
                connector_type = config_path.split('/')[0]  # official or community
                current_version = config['version']
                
                # 检查连接器是否已存在
                existing_connector = registry['connectors'].get(connector_id)
                
                if existing_connector:
                    existing_version = existing_connector.get('version', '0.0.0')
                    if existing_version != current_version:
                        print(f"🔄 Updating {connector_id}: {existing_version} -> {current_version}")
                        action = "updated"
                    else:
                        print(f"✅ Keeping {connector_id} v{current_version} (no changes)")
                        action = "kept"
                else:
                    print(f"🆕 Adding new connector: {connector_id} v{current_version}")
                    action = "added"
                
                # 构建连接器信息（新增或更新）
                connector_info = {
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
                    'config_path': config_path,
                    'last_updated': datetime.now(timezone.utc).isoformat(),
                    'action': action
                }
                
                # 保留现有的下载URL（如果存在）
                if existing_connector and 'download_url' in existing_connector:
                    connector_info['download_url'] = existing_connector['download_url']
                
                registry['connectors'][connector_id] = connector_info
                
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


def update_download_urls(registry_file: str, release_tag: str, base_url: str = None) -> bool:
    """
    更新注册表中的下载URL
    
    Args:
        registry_file: 注册表文件路径
        release_tag: GitHub Release标签
        base_url: 基础URL，默认从环境变量获取
    
    Returns:
        更新是否成功
    """
    if not os.path.exists(registry_file):
        print(f"❌ Registry file not found: {registry_file}")
        return False
    
    # 构建基础URL
    if not base_url:
        repo = os.environ.get('GITHUB_REPOSITORY', 'laofahai/linch-mind')
        base_url = f"https://github.com/{repo}/releases/download/{release_tag}"
    
    try:
        with open(registry_file, 'r') as f:
            registry = json.load(f)
        
        updated_count = 0
        for connector_id, connector_info in registry['connectors'].items():
            zip_filename = f"{connector_id}-connector.zip"
            download_url = f"{base_url}/{zip_filename}"
            
            # 更新或添加下载URL
            old_url = connector_info.get('download_url')
            connector_info['download_url'] = download_url
            
            if old_url != download_url:
                print(f"🔗 Updated download URL for {connector_id}")
                updated_count += 1
        
        # 更新注册表时间戳
        registry['last_updated'] = datetime.now(timezone.utc).isoformat()
        registry['metadata']['release_tag'] = release_tag
        
        # 保存更新的注册表
        with open(registry_file, 'w') as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Updated {updated_count} download URLs in registry")
        return True
        
    except Exception as e:
        print(f"❌ Error updating download URLs: {e}")
        return False


def calculate_checksum(file_path: str) -> str:
    """
    计算文件SHA256校验和
    """
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        print(f"⚠️ Failed to calculate checksum for {file_path}: {e}")
        return ""


def main():
    parser = argparse.ArgumentParser(description='连接器注册表生成工具')
    parser.add_argument('--dir', default='.', help='connectors目录路径')
    parser.add_argument('--output', default='registry.json', help='输出文件名')
    parser.add_argument('--format', action='store_true', help='格式化输出')
    parser.add_argument('--update-urls', help='更新下载URL，需要提供release标签')
    parser.add_argument('--base-url', help='自定义基础URL')
    
    args = parser.parse_args()
    
    # 更新下载URL模式
    if args.update_urls:
        if not Path(args.output).exists():
            print(f"❌ 注册表文件不存在: {args.output}")
            sys.exit(1)
        
        success = update_download_urls(args.output, args.update_urls, args.base_url)
        sys.exit(0 if success else 1)
    
    # 正常生成模式
    if not Path(args.dir).exists():
        print(f"❌ 目录不存在: {args.dir}")
        sys.exit(1)
    
    registry = generate_registry(args.dir, args.output)
    
    if args.format:
        print("\n📋 Registry Summary:")
        print(f"   Total connectors: {registry['metadata']['total_count']}")
        for connector_id, info in registry['connectors'].items():
            action_emoji = {"added": "🆕", "updated": "🔄", "kept": "✅"}.get(info.get('action', 'kept'), '🔧')
            download_status = "📥" if 'download_url' in info else "❓"
            print(f"   {action_emoji} {connector_id} v{info['version']} ({info['type']}) {download_status}")
            if 'download_url' in info:
                print(f"      📍 {info['download_url']}")


if __name__ == "__main__":
    main()