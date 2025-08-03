#\!/bin/bash

# Linch Mind 项目健康检查脚本
# 全面评估项目的技术健康状态

set -euo pipefail

echo "🏥 Linch Mind 项目健康检查报告"
echo "================================="
echo "检查时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 状态函数
print_status() {
    local status=$1
    local message=$2
    case $status in
        "OK") echo -e "${GREEN}✅ $message${NC}" ;;
        "WARNING") echo -e "${YELLOW}⚠️  $message${NC}" ;;
        "ERROR") echo -e "${RED}❌ $message${NC}" ;;
        "INFO") echo -e "${BLUE}ℹ️  $message${NC}" ;;
    esac
}

# 1. 编译状态检查
echo "📋 1. 编译状态检查"
echo "-------------------"
if ./gradlew compileKotlin --quiet; then
    print_status "OK" "Kotlin编译通过"
else
    print_status "ERROR" "Kotlin编译失败"
fi

if ./gradlew compileDesktopKotlin --quiet; then
    print_status "OK" "Desktop模块编译通过"
else
    print_status "ERROR" "Desktop模块编译失败"
fi
echo ""

# 2. 代码质量指标
echo "📊 2. 代码质量指标"
echo "-------------------"
KOTLIN_FILES=$(find src -name "*.kt" | wc -l)
print_status "INFO" "Kotlin文件总数: $KOTLIN_FILES"

# 检查代码风格
if ./gradlew tasks --quiet | grep -q "ktlint"; then
    if ./gradlew ktlintCheck --quiet; then
        print_status "OK" "代码风格检查通过"
    else
        print_status "WARNING" "代码风格需要修复"
    fi
else
    print_status "INFO" "未配置代码风格检查"
fi

# 检查TODO和FIXME
TODO_COUNT=$(grep -r "TODO\|FIXME" src --include="*.kt" | wc -l || echo "0")
if [ "$TODO_COUNT" -gt 0 ]; then
    print_status "INFO" "发现 $TODO_COUNT 个TODO/FIXME标记"
else
    print_status "OK" "无待处理的TODO/FIXME"
fi
echo ""

# 3. 测试状态
echo "🧪 3. 测试状态"
echo "---------------"
TEST_FILES=$(find src -name "*Test.kt" | wc -l)
print_status "INFO" "测试文件数量: $TEST_FILES"

if ./gradlew test --quiet; then
    print_status "OK" "单元测试通过"
else
    print_status "WARNING" "部分单元测试失败"
fi
echo ""

# 4. 依赖健康度
echo "📦 4. 依赖健康度"
echo "-----------------"
if [ -f "build.gradle.kts" ]; then
    print_status "OK" "构建文件存在"
    
    # 检查依赖版本
    DEPS_COUNT=$(grep -c "implementation\|api" build.gradle.kts || echo "0")
    print_status "INFO" "项目依赖数量: $DEPS_COUNT"
else
    print_status "ERROR" "构建文件缺失"
fi
echo ""

# 5. Git状态
echo "📝 5. Git状态"
echo "-------------"
if git status --porcelain | head -n 5; then
    CHANGED_FILES=$(git status --porcelain | wc -l)
    if [ "$CHANGED_FILES" -gt 0 ]; then
        print_status "INFO" "有 $CHANGED_FILES 个文件待提交"
    else
        print_status "OK" "工作目录干净"
    fi
else
    print_status "ERROR" "Git状态检查失败"
fi

# 检查最近提交
RECENT_COMMITS=$(git log --oneline -5)
print_status "INFO" "最近5次提交:"
echo "$RECENT_COMMITS"
echo ""

# 6. 性能指标
echo "⚡ 6. 性能指标"
echo "-------------"
# 检查数据库大小
if [ -f "knowledge.db" ]; then
    DB_SIZE=$(du -h knowledge.db | cut -f1)
    print_status "INFO" "知识库大小: $DB_SIZE"
else
    print_status "WARNING" "知识库文件不存在"
fi

# 检查向量索引
if [ -d "vector_index" ]; then
    INDEX_SIZE=$(du -sh vector_index | cut -f1)
    print_status "INFO" "向量索引大小: $INDEX_SIZE"
else
    print_status "WARNING" "向量索引目录不存在"
fi
echo ""

# 7. AI Agent系统状态
echo "🤖 7. AI Agent系统状态"
echo "----------------------"
AGENT_COUNT=$(find .claude/agents -name "*.md" 2>/dev/null | wc -l || echo "0")
print_status "INFO" "Sub-agent数量: $AGENT_COUNT"

HOOKS_COUNT=$(find .claude/hooks -name "*.sh" 2>/dev/null | wc -l || echo "0")
print_status "INFO" "Hooks脚本数量: $HOOKS_COUNT"

COMMANDS_COUNT=$(find .claude/commands -name "*.md" 2>/dev/null | wc -l || echo "0")
print_status "INFO" "自定义命令数量: $COMMANDS_COUNT"

if [ -f ".claude/settings.json" ]; then
    print_status "OK" "Claude Code配置文件存在"
else
    print_status "WARNING" "Claude Code配置文件缺失"
fi
echo ""

# 8. 总体健康评分
echo "🎯 8. 总体健康评分"
echo "------------------"
# 简单的健康评分逻辑
SCORE=100

# 编译失败 -30分
if \! ./gradlew compileKotlin --quiet; then
    SCORE=$((SCORE - 30))
fi

# 测试失败 -20分
if \! ./gradlew test --quiet; then
    SCORE=$((SCORE - 20))
fi

# 代码风格问题 -10分
if ./gradlew tasks --quiet | grep -q "ktlint" && \! ./gradlew ktlintCheck --quiet; then
    SCORE=$((SCORE - 10))
fi

# 大量未处理TODO -5分
if [ "$TODO_COUNT" -gt 20 ]; then
    SCORE=$((SCORE - 5))
fi

if [ $SCORE -ge 90 ]; then
    print_status "OK" "项目健康评分: $SCORE/100 (优秀)"
elif [ $SCORE -ge 70 ]; then
    print_status "WARNING" "项目健康评分: $SCORE/100 (良好)"
else
    print_status "ERROR" "项目健康评分: $SCORE/100 (需要改进)"
fi

echo ""
echo "🎉 健康检查完成！"
echo "建议: 定期运行此脚本以监控项目健康状态"
echo "================================="
EOF < /dev/null