#!/usr/bin/env python3
"""
循环依赖修复脚本
自动识别和修复项目中的循环依赖问题
"""

import sys
import re
import logging
from pathlib import Path
from typing import List, Tuple, Dict, Set

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)


class CircularDependencyFixer:
    """循环依赖修复器"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.violations: List[Tuple[Path, int, str, str]] = []
        self.fixes_applied: List[Tuple[Path, str]] = []

    def scan_project(self):
        """扫描项目中的循环依赖"""
        logger.info("扫描项目循环依赖...")

        for py_file in self.project_root.rglob("*.py"):
            if self._should_skip_file(py_file):
                continue

            self._analyze_file(py_file)

        logger.info(f"扫描完成，发现 {len(self.violations)} 个问题")

    def _should_skip_file(self, file_path: Path) -> bool:
        """判断是否应该跳过文件"""
        skip_patterns = [
            "__pycache__",
            ".backup",
            "build/",
            "dist/",
            ".git/",
            "test_",
            ".pyc"
        ]

        file_str = str(file_path)
        return any(pattern in file_str for pattern in skip_patterns)

    def _analyze_file(self, file_path: Path):
        """分析单个文件的循环依赖"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            lines = content.split('\n')
            
            # 检查方法内导入
            self._check_method_imports(file_path, lines)
            
            # 检查延迟导入模式
            self._check_lazy_imports(file_path, lines)

        except Exception as e:
            logger.debug(f"分析文件失败 {file_path}: {e}")

    def _check_method_imports(self, file_path: Path, lines: List[str]):
        """检查方法内导入"""
        in_method = False
        method_name = ""
        indent_level = 0

        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # 检测方法开始
            if stripped.startswith("def ") and not stripped.startswith("def __"):
                in_method = True
                method_name = stripped.split("(")[0].replace("def ", "")
                indent_level = len(line) - len(line.lstrip())
            
            # 检测方法结束（通过缩进判断）
            elif in_method and line and len(line) - len(line.lstrip()) <= indent_level:
                if not stripped.startswith((" ", "\t")) or stripped.startswith(("def ", "class ", "@")):
                    in_method = False
                    method_name = ""
            
            # 检测方法内导入
            elif in_method and (stripped.startswith("from ") or stripped.startswith("import ")):
                # 排除一些常见的合法导入
                if not self._is_legitimate_import(stripped):
                    self.violations.append((
                        file_path, 
                        i + 1, 
                        stripped, 
                        f"方法内导入 (方法: {method_name})"
                    ))

    def _check_lazy_imports(self, file_path: Path, lines: List[str]):
        """检查延迟导入模式"""
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # 检查常见的循环依赖模式
            if "get_environment_manager" in stripped and "from core.environment_manager import" in stripped:
                self.violations.append((
                    file_path,
                    i + 1,
                    stripped,
                    "环境管理器循环依赖"
                ))
            
            if "get_database_service" in stripped and "from " in stripped:
                self.violations.append((
                    file_path,
                    i + 1,
                    stripped,
                    "数据库服务循环依赖"
                ))

    def _is_legitimate_import(self, import_stmt: str) -> bool:
        """判断是否为合法的导入"""
        legitimate_patterns = [
            "from datetime import",
            "from typing import",
            "from dataclasses import",
            "from enum import",
            "from pathlib import",
            "import os",
            "import sys",
            "import json",
            "import logging",
            "import asyncio",
            "import copy",
            "import secrets",
        ]

        return any(pattern in import_stmt for pattern in legitimate_patterns)

    def generate_fixes(self) -> Dict[str, List[str]]:
        """生成修复方案"""
        fixes = {}

        for file_path, line_num, import_stmt, violation_type in self.violations:
            file_key = str(file_path.relative_to(self.project_root))
            
            if file_key not in fixes:
                fixes[file_key] = []

            fix_suggestion = self._generate_fix_suggestion(import_stmt, violation_type)
            fixes[file_key].append(f"Line {line_num}: {fix_suggestion}")

        return fixes

    def _generate_fix_suggestion(self, import_stmt: str, violation_type: str) -> str:
        """生成修复建议"""
        if "环境管理器" in violation_type:
            return f"替换: {import_stmt} -> Dependencies.environment_manager()"
        
        elif "数据库服务" in violation_type:
            return f"替换: {import_stmt} -> Dependencies.database_service()"
        
        elif "方法内导入" in violation_type:
            # 分析导入内容，给出具体建议
            if "core.service_facade import get_database_service" in import_stmt:
                return "移动到类构造函数或使用 Dependencies.database_service()"
            
            elif "core.environment_manager import get_environment_manager" in import_stmt:
                return "移动到类构造函数或使用 Dependencies.environment_manager()"
            
            else:
                return f"将导入移动到文件顶部或构造函数中: {import_stmt}"
        
        return f"需要重构: {import_stmt}"

    def apply_automatic_fixes(self) -> bool:
        """应用自动修复"""
        try:
            logger.info("开始应用自动修复...")

            for file_path, line_num, import_stmt, violation_type in self.violations:
                if self._can_auto_fix(violation_type):
                    success = self._apply_fix(file_path, import_stmt, violation_type)
                    if success:
                        self.fixes_applied.append((file_path, violation_type))

            logger.info(f"自动修复完成，修复了 {len(self.fixes_applied)} 个问题")
            return True

        except Exception as e:
            logger.error(f"自动修复失败: {e}")
            return False

    def _can_auto_fix(self, violation_type: str) -> bool:
        """判断是否可以自动修复"""
        # 目前只支持简单的自动修复
        return False  # 为了安全，暂时禁用自动修复

    def _apply_fix(self, file_path: Path, import_stmt: str, violation_type: str) -> bool:
        """应用具体修复"""
        # 这里可以实现具体的文件修改逻辑
        # 目前只是占位实现
        return False

    def generate_report(self) -> str:
        """生成分析报告"""
        report_lines = [
            "# 循环依赖分析报告",
            f"扫描时间: {self._get_current_time()}",
            f"项目根目录: {self.project_root}",
            f"发现问题: {len(self.violations)} 个",
            "",
            "## 问题分类统计",
        ]

        # 统计问题类型
        type_counts = {}
        for _, _, _, violation_type in self.violations:
            type_counts[violation_type] = type_counts.get(violation_type, 0) + 1

        for violation_type, count in sorted(type_counts.items()):
            report_lines.append(f"- {violation_type}: {count} 个")

        report_lines.extend(["", "## 详细问题列表"])

        # 按文件分组显示问题
        file_violations = {}
        for file_path, line_num, import_stmt, violation_type in self.violations:
            rel_path = file_path.relative_to(self.project_root)
            if rel_path not in file_violations:
                file_violations[rel_path] = []
            file_violations[rel_path].append((line_num, import_stmt, violation_type))

        for file_path, violations in sorted(file_violations.items()):
            report_lines.append(f"\n### {file_path}")
            for line_num, import_stmt, violation_type in violations:
                report_lines.append(f"- Line {line_num}: `{import_stmt}` ({violation_type})")

        report_lines.extend(["", "## 修复建议"])
        
        fixes = self.generate_fixes()
        for file_path, fix_list in fixes.items():
            report_lines.append(f"\n### {file_path}")
            for fix in fix_list:
                report_lines.append(f"- {fix}")

        report_lines.extend([
            "",
            "## 通用修复指南",
            "",
            "1. **消除方法内导入**",
            "   - 将导入语句移到文件顶部",
            "   - 或者移到类的`__init__`方法中",
            "   - 使用依赖注入模式",
            "",
            "2. **使用依赖解析器**",
            "   ```python",
            "   # 替代延迟导入",
            "   from core.dependency_resolver import Dependencies",
            "   ",
            "   # 在需要的地方使用",
            "   env_manager = Dependencies.environment_manager()",
            "   db_service = Dependencies.database_service()",
            "   ```",
            "",
            "3. **重构全局获取函数**",
            "   - 移除 `get_*_service()` 全局函数",
            "   - 使用统一的依赖解析器",
            "   - 通过构造函数注入依赖",
            "",
            "4. **配置访问统一化**",
            "   - 使用 `UnifiedConfigManager`",
            "   - 避免分散的配置导入",
        ])

        return "\n".join(report_lines)

    def _get_current_time(self) -> str:
        """获取当前时间字符串"""
        from datetime import datetime
        return datetime.utcnow().isoformat()


def main():
    """主函数"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    logger.info("开始循环依赖分析和修复...")

    try:
        # 创建修复器
        fixer = CircularDependencyFixer(project_root)

        # 扫描项目
        fixer.scan_project()

        # 生成报告
        report = fixer.generate_report()

        # 保存报告
        report_file = project_root / "CIRCULAR_DEPENDENCY_REPORT.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        logger.info(f"分析报告已保存: {report_file}")

        # 显示摘要
        print("\n=== 循环依赖分析摘要 ===")
        print(f"发现问题: {len(fixer.violations)} 个")
        
        if fixer.violations:
            print("\n前5个问题:")
            for i, (file_path, line_num, import_stmt, violation_type) in enumerate(fixer.violations[:5]):
                rel_path = file_path.relative_to(project_root)
                print(f"  {i+1}. {rel_path}:{line_num} - {violation_type}")
                print(f"     {import_stmt}")

            print(f"\n完整报告请查看: {report_file}")
        else:
            print("✅ 未发现循环依赖问题!")

        return len(fixer.violations) == 0

    except Exception as e:
        logger.error(f"循环依赖分析失败: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)