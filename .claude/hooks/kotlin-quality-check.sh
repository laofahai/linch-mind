#!/bin/bash
# Kotlin文件质量检查hook

FILE="$1"
if [ -z "$FILE" ]; then
    echo "错误: 未提供文件路径"
    exit 1
fi

echo "=== Kotlin文件质量检查: $FILE ==="

# 检查文件大小（行数）
LINE_COUNT=$(wc -l < "$FILE")
if [ "$LINE_COUNT" -gt 500 ]; then
    echo "⚠️  警告: 文件过大 ($LINE_COUNT 行)，建议拆分"
fi

# 检查是否有TODO注释
TODO_COUNT=$(grep -c "TODO\|FIXME" "$FILE" 2>/dev/null || echo "0")
if [ "$TODO_COUNT" -gt 0 ]; then
    echo "📝 发现 $TODO_COUNT 个待办事项"
fi

# 检查基本的Kotlin代码风格
if grep -q "fun.*{$" "$FILE"; then
    echo "✅ 函数格式正确"
else
    echo "⚠️  建议检查函数格式"
fi

# 检查是否有适当的日志记录
if grep -q "Logger\|log\." "$FILE"; then
    echo "✅ 包含日志记录"
else
    echo "⚠️  建议添加日志记录"
fi

echo "=== 检查完成 ==="