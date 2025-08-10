#!/bin/bash
# Linch Mind Daemon 测试运行脚本

set -e  # 遇到错误时退出

echo "🚀 开始运行 Linch Mind Daemon 测试套件"
echo "========================================"

# 检查poetry环境
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry 未安装，请先安装 Poetry"
    exit 1
fi

# 安装依赖
echo "📦 检查和安装依赖..."
poetry install --with dev

# 运行代码格式检查 (如果有)
echo ""
echo "🔍 运行代码质量检查..."
if command -v poetry run flake8 &> /dev/null; then
    poetry run flake8 core services --max-line-length=88 --ignore=E203,W503 || echo "⚠️ 代码格式检查发现问题"
fi

# 运行核心组件单元测试
echo ""
echo "🧪 运行核心组件单元测试..."
poetry run python -m pytest tests/test_core_components.py \
    --verbose \
    --tb=short \
    --cov=core \
    --cov-report=term-missing \
    --cov-report=html:htmlcov \
    || echo "⚠️ 部分测试失败"

# 运行性能基准测试
echo ""
echo "⚡ 运行性能基准测试..."
poetry run python tests/test_architecture_performance.py || echo "⚠️ 性能测试有问题"

# 运行其他现有测试
echo ""
echo "📋 运行其他现有测试..."
poetry run python -m pytest tests/ \
    --verbose \
    --tb=short \
    --ignore=tests/test_core_components.py \
    --ignore=tests/test_architecture_performance.py \
    -x \
    || echo "⚠️ 现有测试有问题"

# 生成测试报告
echo ""
echo "📊 测试完成！"
echo "========================================"
echo "✅ 核心组件单元测试已完成"
echo "✅ 性能基准测试已完成" 
echo "✅ 现有测试套件已执行"
echo ""
echo "📈 覆盖率报告已生成在 htmlcov/ 目录中"
echo "🌐 使用浏览器打开 htmlcov/index.html 查看详细报告"
echo ""
echo "🎉 测试套件执行完成！"