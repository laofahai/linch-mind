#!/bin/bash

# Linch Mind AI Agent 智能路由系统
# 基于文件路径、工具类型和任务复杂度自动选择合适的sub-agent

set -euo pipefail

# 读取输入数据
INPUT=$(cat)

# 解析工具和参数信息
TOOL_NAME=$(echo "$INPUT" | jq -r '.toolName // "unknown"')
FILE_PATH=$(echo "$INPUT" | jq -r '.parameters.file_path // .parameters.pattern // ""')
TASK_DESCRIPTION=$(echo "$INPUT" | jq -r '.taskDescription // ""')

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] SMART_ROUTING: $1" >&2
}

# 检测任务复杂度
detect_complexity() {
    local complexity=0
    
    # 基于工具类型评估复杂度
    case "$TOOL_NAME" in
        "MultiEdit") complexity=$((complexity + 3)) ;;
        "Edit"|"Write") complexity=$((complexity + 2)) ;;
        "Read"|"Grep"|"Glob") complexity=$((complexity + 1)) ;;
        "Bash") complexity=$((complexity + 1)) ;;
    esac
    
    # 基于文件路径评估复杂度
    if [[ "$FILE_PATH" =~ \.(kt|java)$ ]]; then
        complexity=$((complexity + 1))
    fi
    
    # 基于任务描述关键词评估复杂度
    if [[ "$TASK_DESCRIPTION" =~ (refactor|architect|design|complex|system) ]]; then
        complexity=$((complexity + 2))
    fi
    
    echo $complexity
}

# 基于文件路径选择专业agent
select_agent_by_path() {
    local path="$1"
    
    # AI/ML 相关文件
    if [[ "$path" =~ (ai/|vector/|intelligence/|rag/) ]]; then
        echo "ai-ml-specialist"
        return 0
    fi
    
    # UI/UX 相关文件
    if [[ "$path" =~ (ui/|compose/|theme/|screens/|components/) ]]; then
        echo "ui-ux-specialist"
        return 0
    fi
    
    # 数据架构相关文件
    if [[ "$path" =~ (storage/|graph/|persistence/|migration/) ]]; then
        echo "data-architecture-specialist"
        return 0
    fi
    
    # 性能相关文件
    if [[ "$path" =~ (performance/|monitoring/|benchmark/) ]] || [[ "$TASK_DESCRIPTION" =~ (performance|optimize|memory|cpu) ]]; then
        echo "performance-optimizer"
        return 0
    fi
    
    # 安全隐私相关文件
    if [[ "$path" =~ (security/|permission/|crypto/) ]] || [[ "$TASK_DESCRIPTION" =~ (security|privacy|encrypt|permission) ]]; then
        echo "security-privacy-specialist"
        return 0
    fi
    
    # 默认返回核心开发架构师
    echo "core-development-architect"
}

# 主路由逻辑
main() {
    log "Processing tool: $TOOL_NAME, file: $FILE_PATH"
    
    # 检测任务复杂度
    COMPLEXITY=$(detect_complexity)
    log "Task complexity score: $COMPLEXITY"
    
    # 如果复杂度过高，要求人工介入
    if [[ $COMPLEXITY -gt 7 ]]; then
        log "Task complexity too high ($COMPLEXITY), requiring human review"
        echo '{"action": "require_human_review", "reason": "Task complexity exceeds threshold", "complexity": '$COMPLEXITY'}'
        exit 1
    fi
    
    # 选择合适的agent
    SELECTED_AGENT=$(select_agent_by_path "$FILE_PATH")
    log "Selected agent: $SELECTED_AGENT"
    
    # 特殊情况：多文件编辑或重大重构，使用核心架构师
    if [[ "$TOOL_NAME" == "MultiEdit" ]] || [[ $COMPLEXITY -gt 5 ]]; then
        SELECTED_AGENT="core-development-architect"
        log "Upgraded to core-development-architect due to complexity"
    fi
    
    # 输出路由决策
    echo "{
        \"action\": \"route_to_agent\",
        \"agent\": \"$SELECTED_AGENT\",
        \"complexity\": $COMPLEXITY,
        \"reasoning\": \"File path: $FILE_PATH, Tool: $TOOL_NAME, Complexity: $COMPLEXITY\"
    }"
}

# 执行主逻辑
main

log "Smart routing completed successfully"