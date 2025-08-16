#!/usr/bin/env python3
"""
统一服务迁移脚本
自动识别和迁移重复的服务实现到统一服务架构
"""

import ast
import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DuplicateCodeAnalyzer:
    """重复代码分析器"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.duplicate_patterns = {
            'vector_search': [
                'VectorService',
                'vector_search',
                'faiss',
                'search_by_vector',
                'similarity_search'
            ],
            'graph_search': [
                'GraphService', 
                'networkx',
                'find_neighbors',
                'graph_traversal',
                'shortest_path'
            ],
            'cache_systems': [
                'cache',
                'Cache',
                'memory_cache',
                'disk_cache',
                'lru_cache'
            ],
            'thread_pools': [
                'ThreadPoolExecutor',
                'concurrent.futures',
                'executor',
                'submit',
                'thread_pool'
            ]
        }
        
        self.unified_services = {
            'vector_search': 'UnifiedSearchService',
            'graph_search': 'UnifiedSearchService', 
            'cache_systems': 'UnifiedCacheService',
            'thread_pools': 'SharedExecutorService'
        }
    
    def scan_project(self) -> Dict[str, List[str]]:
        """扫描项目中的重复实现"""
        results = {category: [] for category in self.duplicate_patterns}
        
        for py_file in self.project_root.rglob("*.py"):
            if any(skip in str(py_file) for skip in ['__pycache__', '.git', 'unified_', 'shared_']):
                continue
                
            try:
                content = py_file.read_text(encoding='utf-8')
                
                for category, patterns in self.duplicate_patterns.items():
                    for pattern in patterns:
                        if pattern in content:
                            results[category].append(str(py_file))
                            break
                            
            except Exception as e:
                logger.warning(f"无法分析文件 {py_file}: {e}")
        
        return results
    
    def generate_migration_plan(self) -> Dict[str, List[Dict]]:
        """生成迁移计划"""
        scan_results = self.scan_project()
        migration_plan = {}
        
        for category, files in scan_results.items():
            if not files:
                continue
                
            unified_service = self.unified_services[category]
            migration_plan[category] = {
                'unified_service': unified_service,
                'affected_files': files,
                'migration_steps': self._get_migration_steps(category),
                'risk_level': self._assess_risk_level(files)
            }
        
        return migration_plan
    
    def _get_migration_steps(self, category: str) -> List[str]:
        """获取迁移步骤"""
        steps = {
            'vector_search': [
                "替换VectorService导入为UnifiedSearchService",
                "更新vector_search调用为unified search API",
                "修改搜索参数为SearchQuery格式",
                "更新结果处理为SearchResult格式"
            ],
            'graph_search': [
                "替换GraphService导入为UnifiedSearchService", 
                "更新graph traversal调用为unified search API",
                "修改图搜索参数为SearchQuery格式",
                "更新结果处理为SearchResult格式"
            ],
            'cache_systems': [
                "替换各种cache导入为UnifiedCacheService",
                "统一缓存API调用格式",
                "迁移缓存配置到CacheType",
                "更新缓存键值格式"
            ],
            'thread_pools': [
                "替换ThreadPoolExecutor导入为SharedExecutorService",
                "更新submit调用为统一任务提交API",
                "分类任务类型(IO/CPU/ML等)",
                "迁移错误处理到统一格式"
            ]
        }
        return steps.get(category, [])
    
    def _assess_risk_level(self, files: List[str]) -> str:
        """评估迁移风险等级"""
        if len(files) >= 10:
            return "HIGH"
        elif len(files) >= 5:
            return "MEDIUM"
        else:
            return "LOW"


class AutoMigrator:
    """自动迁移器"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.backup_dir = project_root / "backup_before_migration"
        
    def create_backup(self, files: List[str]):
        """创建迁移前备份"""
        self.backup_dir.mkdir(exist_ok=True)
        
        for file_path in files:
            src_file = Path(file_path)
            if src_file.exists():
                backup_file = self.backup_dir / src_file.name
                backup_file.write_text(src_file.read_text())
                logger.info(f"备份文件: {src_file} -> {backup_file}")
    
    def migrate_vector_graph_services(self, files: List[str]) -> Dict[str, bool]:
        """迁移向量和图搜索服务"""
        results = {}
        
        migration_patterns = [
            # VectorService替换
            (
                r'from\s+services\.storage\.vector_service\s+import\s+VectorService',
                'from services.unified_search_service import UnifiedSearchService, SearchQuery, SearchType'
            ),
            (
                r'from\s+.*\s+import\s+.*VectorService.*',
                'from services.unified_search_service import UnifiedSearchService, SearchQuery, SearchType'
            ),
            # GraphService替换
            (
                r'from\s+services\.storage\.graph_service\s+import\s+GraphService',
                'from services.unified_search_service import UnifiedSearchService, SearchQuery, SearchType'
            ),
            # 服务获取方法替换
            (
                r'get_vector_service\(\)',
                'await get_unified_search_service()'
            ),
            (
                r'get_graph_service\(\)',
                'await get_unified_search_service()'
            ),
            # API调用替换示例 (需要根据具体用法调整)
            (
                r'vector_service\.search\(',
                'search_service.search(SearchQuery(query=..., search_type=SearchType.SEMANTIC, '
            ),
            (
                r'graph_service\.find_neighbors\(',
                'search_service.search(SearchQuery(query="", search_type=SearchType.GRAPH, start_entity_id=..., '
            )
        ]
        
        for file_path in files:
            try:
                file_obj = Path(file_path)
                if not file_obj.exists():
                    continue
                    
                content = file_obj.read_text()
                original_content = content
                
                # 应用迁移模式
                for pattern, replacement in migration_patterns:
                    content = re.sub(pattern, replacement, content)
                
                # 只有内容发生变化时才写入
                if content != original_content:
                    file_obj.write_text(content)
                    logger.info(f"✅ 已迁移搜索服务: {file_path}")
                    results[file_path] = True
                else:
                    results[file_path] = False
                    
            except Exception as e:
                logger.error(f"❌ 迁移失败 {file_path}: {e}")
                results[file_path] = False
        
        return results
    
    def migrate_cache_systems(self, files: List[str]) -> Dict[str, bool]:
        """迁移缓存系统"""
        results = {}
        
        cache_patterns = [
            # 替换各种缓存导入
            (
                r'from\s+functools\s+import\s+lru_cache',
                'from services.unified_cache_service import get_unified_cache_service, CacheType'
            ),
            (
                r'@lru_cache\(.*?\)',
                '# TODO: 迁移到UnifiedCacheService - 使用cache_service.get_or_set()'
            ),
            # 内存缓存替换
            (
                r'self\._cache\s*=\s*\{\}',
                '# 使用UnifiedCacheService替代内存缓存'
            ),
            (
                r'cache\.get\(',
                'await cache_service.get('
            ),
            (
                r'cache\.set\(',
                'await cache_service.set('
            )
        ]
        
        for file_path in files:
            try:
                file_obj = Path(file_path)
                if not file_obj.exists():
                    continue
                
                content = file_obj.read_text()
                original_content = content
                
                for pattern, replacement in cache_patterns:
                    content = re.sub(pattern, replacement, content)
                
                if content != original_content:
                    file_obj.write_text(content)
                    logger.info(f"✅ 已迁移缓存系统: {file_path}")
                    results[file_path] = True
                else:
                    results[file_path] = False
                    
            except Exception as e:
                logger.error(f"❌ 缓存迁移失败 {file_path}: {e}")
                results[file_path] = False
        
        return results
    
    def migrate_thread_pools(self, files: List[str]) -> Dict[str, bool]:
        """迁移线程池"""
        results = {}
        
        executor_patterns = [
            # ThreadPoolExecutor替换
            (
                r'from\s+concurrent\.futures\s+import\s+ThreadPoolExecutor',
                'from services.shared_executor_service import get_shared_executor_service, TaskType'
            ),
            (
                r'ThreadPoolExecutor\(max_workers=(\d+)\)',
                '# 使用SharedExecutorService替代ThreadPoolExecutor'
            ),
            (
                r'self\._executor\s*=\s*ThreadPoolExecutor\(.*?\)',
                'self._executor = get_shared_executor_service()'
            ),
            (
                r'executor\.submit\(',
                'await executor.submit('
            )
        ]
        
        for file_path in files:
            try:
                file_obj = Path(file_path)
                if not file_obj.exists():
                    continue
                
                content = file_obj.read_text()
                original_content = content
                
                for pattern, replacement in executor_patterns:
                    content = re.sub(pattern, replacement, content)
                
                if content != original_content:
                    file_obj.write_text(content)
                    logger.info(f"✅ 已迁移线程池: {file_path}")
                    results[file_path] = True
                else:
                    results[file_path] = False
                    
            except Exception as e:
                logger.error(f"❌ 线程池迁移失败 {file_path}: {e}")
                results[file_path] = False
        
        return results


def main():
    """主迁移流程"""
    project_root = Path(__file__).parent.parent
    
    logger.info("🚀 开始统一服务迁移分析")
    
    # 分析重复代码
    analyzer = DuplicateCodeAnalyzer(project_root)
    migration_plan = analyzer.generate_migration_plan()
    
    logger.info("📊 迁移计划分析结果:")
    for category, plan in migration_plan.items():
        logger.info(f"  {category}:")
        logger.info(f"    统一服务: {plan['unified_service']}")
        logger.info(f"    影响文件: {len(plan['affected_files'])} 个")
        logger.info(f"    风险等级: {plan['risk_level']}")
        for step in plan['migration_steps']:
            logger.info(f"      - {step}")
    
    # 执行迁移
    migrator = AutoMigrator(project_root)
    
    # 创建备份
    all_files = []
    for plan in migration_plan.values():
        all_files.extend(plan['affected_files'])
    
    if all_files:
        migrator.create_backup(all_files)
        logger.info(f"✅ 已备份 {len(all_files)} 个文件")
    
    # 执行分类迁移
    total_migrated = 0
    
    if 'vector_search' in migration_plan or 'graph_search' in migration_plan:
        search_files = set()
        if 'vector_search' in migration_plan:
            search_files.update(migration_plan['vector_search']['affected_files'])
        if 'graph_search' in migration_plan:
            search_files.update(migration_plan['graph_search']['affected_files'])
        
        results = migrator.migrate_vector_graph_services(list(search_files))
        migrated_count = sum(results.values())
        total_migrated += migrated_count
        logger.info(f"🔍 搜索服务迁移完成: {migrated_count}/{len(search_files)} 个文件")
    
    if 'cache_systems' in migration_plan:
        cache_files = migration_plan['cache_systems']['affected_files']
        results = migrator.migrate_cache_systems(cache_files)
        migrated_count = sum(results.values())
        total_migrated += migrated_count
        logger.info(f"💾 缓存系统迁移完成: {migrated_count}/{len(cache_files)} 个文件")
    
    if 'thread_pools' in migration_plan:
        executor_files = migration_plan['thread_pools']['affected_files']
        results = migrator.migrate_thread_pools(executor_files)
        migrated_count = sum(results.values())
        total_migrated += migrated_count
        logger.info(f"🚀 线程池迁移完成: {migrated_count}/{len(executor_files)} 个文件")
    
    logger.info(f"✅ 统一服务迁移完成！总计迁移 {total_migrated} 个文件")
    logger.info("📝 请运行测试验证迁移结果，必要时从backup目录恢复")


if __name__ == "__main__":
    main()