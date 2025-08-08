#!/bin/bash
# Linch Mind 文档质量检查脚本
# 用途：验证文档与实际实现的一致性

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DOCS_DIR="$PROJECT_ROOT/docs"
DAEMON_DIR="$PROJECT_ROOT/daemon"
UI_DIR="$PROJECT_ROOT/ui"

echo -e "${BLUE}🔍 Linch Mind 文档质量检查开始...${NC}"
echo ""

# 检查计数器
CHECKS_PASSED=0
CHECKS_FAILED=0
WARNINGS=0

# 辅助函数
check_pass() {
    echo -e "${GREEN}✅ $1${NC}"
    ((CHECKS_PASSED++))
}

check_fail() {
    echo -e "${RED}❌ $1${NC}"
    ((CHECKS_FAILED++))
}

check_warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    ((WARNINGS++))
}

# 1. 检查启动命令准确性
echo -e "${BLUE}📋 检查启动命令准确性...${NC}"

if [ -f "$PROJECT_ROOT/linch-mind" ] && [ -x "$PROJECT_ROOT/linch-mind" ]; then
    check_pass "启动脚本存在且可执行"
else
    check_fail "启动脚本 ./linch-mind 不存在或不可执行"
fi

if [ -f "$DAEMON_DIR/ipc_main.py" ]; then
    check_pass "daemon入口点 ipc_main.py 存在"
else
    check_fail "daemon入口点 ipc_main.py 不存在"
fi

# 2. 检查技术栈一致性
echo -e "${BLUE}🔧 检查技术栈描述一致性...${NC}"

# 检查Python版本要求
if [ -f "$DAEMON_DIR/pyproject.toml" ]; then
    PYTHON_VERSION=$(grep 'python = ' "$DAEMON_DIR/pyproject.toml" | head -1)
    if [[ "$PYTHON_VERSION" == *"3.12"* ]]; then
        check_pass "Python版本要求一致 (3.12+)"
    else
        check_fail "Python版本要求不一致：$PYTHON_VERSION"
    fi
else
    check_fail "pyproject.toml 不存在"
fi

# 检查Flutter版本要求
if [ -f "$UI_DIR/pubspec.yaml" ]; then
    FLUTTER_VERSION=$(grep 'flutter:' "$UI_DIR/pubspec.yaml" -A 1 | grep '"' | head -1)
    if [[ "$FLUTTER_VERSION" == *"3."* ]]; then
        check_pass "Flutter版本要求存在"
    else
        check_warn "Flutter版本要求需要确认"
    fi
else
    check_fail "pubspec.yaml 不存在"
fi

# 3. 检查架构描述准确性
echo -e "${BLUE}🏗️  检查架构描述准确性...${NC}"

# 检查是否仍有HTTP相关描述
HTTP_REFS=$(find "$DOCS_DIR" -name "*.md" -exec grep -l "HTTP\|REST\|FastAPI" {} \; 2>/dev/null || true)
if [ -z "$HTTP_REFS" ]; then
    check_pass "文档中已清理HTTP相关描述"
else
    echo -e "${YELLOW}⚠️  以下文档仍包含HTTP描述：${NC}"
    echo "$HTTP_REFS"
    ((WARNINGS++))
fi

# 检查IPC架构描述
IPC_REFS=$(find "$DOCS_DIR" -name "*.md" -exec grep -l "IPC\|Unix Socket\|Named Pipe" {} \; 2>/dev/null || true)
if [ -n "$IPC_REFS" ]; then
    check_pass "文档中包含IPC架构描述"
else
    check_fail "文档中缺少IPC架构描述"
fi

# 4. 检查依赖描述准确性
echo -e "${BLUE}📦 检查依赖描述准确性...${NC}"

# 检查Poetry是否在文档中提及
if grep -r "Poetry" "$DOCS_DIR" >/dev/null 2>&1; then
    check_pass "文档中提及Poetry依赖管理"
else
    check_warn "文档中未提及Poetry依赖管理"
fi

# 检查实际依赖是否与文档一致
if [ -f "$DAEMON_DIR/pyproject.toml" ]; then
    # 检查关键依赖
    if grep -q "sqlalchemy" "$DAEMON_DIR/pyproject.toml"; then
        check_pass "SQLAlchemy依赖存在"
    else
        check_fail "SQLAlchemy依赖缺失"
    fi
    
    if grep -q "faiss-cpu" "$DAEMON_DIR/pyproject.toml"; then
        check_pass "FAISS依赖存在"
    else
        check_warn "FAISS依赖可能缺失"
    fi
    
    if grep -q "networkx" "$DAEMON_DIR/pyproject.toml"; then
        check_pass "NetworkX依赖存在"
    else
        check_warn "NetworkX依赖可能缺失"
    fi
fi

# 5. 检查端口和路径引用
echo -e "${BLUE}🔌 检查端口和路径引用...${NC}"

# 检查是否仍有错误的端口引用
WRONG_PORTS=$(find "$DOCS_DIR" -name "*.md" -exec grep -H "8000\|8080\|8088" {} \; 2>/dev/null || true)
if [ -z "$WRONG_PORTS" ]; then
    check_pass "文档中无错误端口引用"
else
    echo -e "${RED}❌ 发现错误端口引用：${NC}"
    echo "$WRONG_PORTS"
    ((CHECKS_FAILED++))
fi

# 6. 检查命令可执行性
echo -e "${BLUE}⚙️  检查命令可执行性...${NC}"

# 检查Python环境
if command -v poetry &> /dev/null; then
    check_pass "Poetry命令可用"
    
    # 检查虚拟环境
    cd "$DAEMON_DIR"
    if poetry env info >/dev/null 2>&1; then
        check_pass "Poetry虚拟环境已配置"
    else
        check_warn "Poetry虚拟环境未配置，请运行 'poetry install'"
    fi
    cd "$PROJECT_ROOT"
else
    check_fail "Poetry命令不可用，请安装Poetry"
fi

# 检查Flutter环境
if command -v flutter &> /dev/null; then
    check_pass "Flutter命令可用"
else
    check_warn "Flutter命令不可用"
fi

# 7. 检查文件存在性
echo -e "${BLUE}📁 检查关键文件存在性...${NC}"

KEY_FILES=(
    "README.md"
    "CLAUDE.md"
    "daemon/ipc_main.py"
    "daemon/pyproject.toml"
    "ui/pubspec.yaml"
    "ui/lib/main.dart"
    "connectors/official/filesystem/connector.json"
    "connectors/official/clipboard/connector.json"
)

for file in "${KEY_FILES[@]}"; do
    if [ -f "$PROJECT_ROOT/$file" ]; then
        check_pass "关键文件存在: $file"
    else
        check_fail "关键文件缺失: $file"
    fi
done

# 8. 生成报告
echo ""
echo -e "${BLUE}📊 检查报告总结${NC}"
echo "=========================="
echo -e "通过检查: ${GREEN}$CHECKS_PASSED${NC}"
echo -e "失败检查: ${RED}$CHECKS_FAILED${NC}" 
echo -e "警告数量: ${YELLOW}$WARNINGS${NC}"
echo ""

# 确定总体状态
TOTAL_ISSUES=$((CHECKS_FAILED + WARNINGS))

if [ $CHECKS_FAILED -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}🎉 文档质量检查全部通过！${NC}"
    exit 0
elif [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "${YELLOW}⚠️  文档质量检查通过，但有 $WARNINGS 个警告需要关注${NC}"
    exit 0
else
    echo -e "${RED}❌ 文档质量检查失败，发现 $CHECKS_FAILED 个错误和 $WARNINGS 个警告${NC}"
    echo ""
    echo -e "${BLUE}建议修复措施：${NC}"
    echo "1. 检查并修正上述错误项"
    echo "2. 确保文档与实际实现保持同步"
    echo "3. 运行相关测试验证功能正常"
    exit 1
fi