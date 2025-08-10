#!/usr/bin/env python3
"""
SQLCipher数据库加密迁移脚本
将现有明文数据库迁移到SQLCipher加密数据库
"""

import os
import sys
from pathlib import Path

# 添加daemon目录到Python路径
daemon_dir = Path(__file__).parent.parent
sys.path.insert(0, str(daemon_dir))

import logging
import sqlite3
from services.encrypted_database_service import EncryptedDatabaseService, SQLCipherKeyManager
from config.core_config import get_core_config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def find_existing_database():
    """查找现有的明文数据库"""
    try:
        config = get_core_config()
        
        if config.config.database.sqlite_url.startswith("sqlite:///"):
            db_path = Path(config.config.database.sqlite_url[10:])  # 移除 "sqlite:///"
            
            if db_path.exists():
                logger.info(f"发现现有数据库: {db_path}")
                return db_path
            else:
                logger.info("未发现现有数据库文件")
                return None
        else:
            logger.info("配置使用内存数据库，无需迁移")
            return None
            
    except Exception as e:
        logger.error(f"查找数据库失败: {e}")
        return None


def get_database_info(db_path: Path):
    """获取数据库信息"""
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # 获取所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        total_records = 0
        table_info = {}
        
        for (table_name,) in tables:
            if table_name.startswith('sqlite_'):
                continue
            
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            table_info[table_name] = count
            total_records += count
        
        conn.close()
        
        return {
            'tables': table_info,
            'total_records': total_records,
            'file_size_mb': db_path.stat().st_size / (1024 * 1024)
        }
        
    except Exception as e:
        logger.error(f"获取数据库信息失败: {e}")
        return None


def migrate_database_data(source_db_path: Path, encrypted_db: EncryptedDatabaseService):
    """迁移数据库数据到加密数据库"""
    try:
        logger.info("开始数据迁移...")
        
        # 连接源数据库
        source_conn = sqlite3.connect(str(source_db_path))
        source_cursor = source_conn.cursor()
        
        # 获取所有表名
        source_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [table[0] for table in source_cursor.fetchall() 
                 if not table[0].startswith('sqlite_')]
        
        logger.info(f"发现 {len(tables)} 个表需要迁移: {', '.join(tables)}")
        
        total_migrated = 0
        
        with encrypted_db.get_session() as session:
            from sqlalchemy import text
            
            for table_name in tables:
                logger.info(f"迁移表: {table_name}")
                
                # 获取源表结构
                source_cursor.execute(f"PRAGMA table_info({table_name});")
                columns_info = source_cursor.fetchall()
                columns = [col[1] for col in columns_info]  # col[1] 是列名
                
                # 获取源表数据
                source_cursor.execute(f"SELECT * FROM {table_name};")
                rows = source_cursor.fetchall()
                
                if rows:
                    # 构建插入SQL
                    placeholders = ','.join(['?' for _ in columns])
                    insert_sql = f"INSERT OR REPLACE INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})"
                    
                    # 批量插入到加密数据库
                    for row in rows:
                        session.execute(text(insert_sql), row)
                    
                    session.commit()
                    logger.info(f"  -> 迁移了 {len(rows)} 条记录")
                    total_migrated += len(rows)
                else:
                    logger.info(f"  -> 表为空，跳过")
        
        source_conn.close()
        logger.info(f"数据迁移完成，总计迁移 {total_migrated} 条记录")
        
        return True
        
    except Exception as e:
        logger.error(f"数据迁移失败: {e}")
        return False


def backup_original_database(db_path: Path):
    """备份原始数据库"""
    try:
        backup_path = db_path.with_suffix('.db.backup')
        
        import shutil
        shutil.copy2(db_path, backup_path)
        
        logger.info(f"原始数据库已备份到: {backup_path}")
        return backup_path
        
    except Exception as e:
        logger.error(f"备份数据库失败: {e}")
        return None


def main():
    """主迁移流程"""
    print("=== Linch Mind SQLCipher加密数据库迁移 ===")
    print()
    
    try:
        # 1. 查找现有数据库
        print("[1/6] 检查现有数据库...")
        existing_db_path = find_existing_database()
        
        if existing_db_path:
            # 显示数据库信息
            db_info = get_database_info(existing_db_path)
            if db_info:
                print(f"📊 数据库信息:")
                print(f"   文件大小: {db_info['file_size_mb']:.2f} MB")
                print(f"   总记录数: {db_info['total_records']}")
                print(f"   数据表: {', '.join(db_info['tables'].keys())}")
                
                for table, count in db_info['tables'].items():
                    print(f"     - {table}: {count} 条记录")
            
            # 确认是否继续
            confirm = input(f"\n是否要将此数据库迁移到SQLCipher加密？ (y/n): ")
            if confirm.lower().strip() != 'y':
                print("取消迁移")
                return False
        else:
            print("未发现现有数据库，将创建新的加密数据库")
        
        # 2. 备份原始数据库
        backup_path = None
        if existing_db_path:
            print(f"\n[2/6] 备份原始数据库...")
            backup_path = backup_original_database(existing_db_path)
            if not backup_path:
                print("备份失败，停止迁移")
                return False
        
        # 3. 初始化SQLCipher密钥
        print(f"\n[3/6] 初始化SQLCipher密钥...")
        try:
            encryption_key = SQLCipherKeyManager.get_or_create_key()
            print("✅ SQLCipher密钥准备完成")
        except Exception as e:
            print(f"❌ 密钥初始化失败: {e}")
            return False
        
        # 4. 创建加密数据库
        print(f"\n[4/6] 创建SQLCipher加密数据库...")
        try:
            encrypted_db = EncryptedDatabaseService()
            print("✅ SQLCipher加密数据库创建成功")
        except Exception as e:
            print(f"❌ 加密数据库创建失败: {e}")
            return False
        
        # 5. 迁移数据
        if existing_db_path:
            print(f"\n[5/6] 迁移数据到加密数据库...")
            if migrate_database_data(existing_db_path, encrypted_db):
                print("✅ 数据迁移完成")
            else:
                print("❌ 数据迁移失败")
                encrypted_db.cleanup()
                return False
        else:
            print(f"\n[5/6] 跳过数据迁移（无现有数据）")
        
        # 6. 完成并清理
        print(f"\n[6/6] 完成迁移...")
        
        # 验证加密数据库
        try:
            with encrypted_db.get_session() as session:
                from sqlalchemy import text
                result = session.execute(text("SELECT name FROM sqlite_master WHERE type='table';")).fetchall()
                print(f"🔍 加密数据库验证：发现 {len(result)} 个表")
        except Exception as e:
            print(f"⚠️  数据库验证警告: {e}")
        
        encrypted_db.cleanup()
        
        # 删除原始明文数据库
        if existing_db_path and backup_path:
            try:
                existing_db_path.unlink()
                print(f"🗑️  原始明文数据库已删除")
                print(f"💾 备份保存在: {backup_path}")
            except Exception as e:
                print(f"⚠️  删除原始数据库失败: {e}")
        
        print(f"\n🎉 === 迁移成功完成 ===")
        print("✅ 数据库现已使用SQLCipher AES-256加密保护")
        print("🔐 加密密钥安全存储在系统keyring中")
        print("🚀 应用将自动使用加密数据库")
        print()
        
        return True
        
    except KeyboardInterrupt:
        print("\n⚠️  迁移被用户中断")
        return False
    except Exception as e:
        logger.error(f"迁移过程发生错误: {e}")
        print(f"\n❌ 迁移失败: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)