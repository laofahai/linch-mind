#!/bin/bash

# Linch Mind 智能降级和人工介入触发器
# 监控AI代理的执行状态，在必要时触发降级策略或要求人工介入

set -euo pipefail

# 读取输入数据
INPUT=$(cat)

# 解析输入信息
TOOL_NAME=$(echo "$INPUT" | jq -r '.toolName // "unknown"')
FILE_PATH=$(echo "$INPUT" | jq -r '.parameters.file_path // ""')
ERROR_COUNT=$(echo "$INPUT" | jq -r '.errorCount // 0')
EXECUTION_TIME=$(echo "$INPUT" | jq -r '.executionTime // 0')
AGENT_NAME=$(echo "$INPUT" | jq -r '.agentName // "unknown"')

# 配置参数
PROJECT_ROOT="/Users/laofahai/Documents/workspace/linch-mind"
FALLBACK_LOG=".claude/logs/fallback-decisions.log"
METRICS_FILE=".claude/logs/system-metrics.json"
HUMAN_INTERVENTION_FLAG=".claude/human-intervention-required"

# 阈值配置
MAX_COMPILATION_FAILURES=3
MAX_EXECUTION_TIME=300  # 5分钟
MAX_CONSECUTIVE_ERRORS=5
COMPLEXITY_THRESHOLD=8
CRITICAL_FILE_PATTERNS=("Main.kt" "AppScope.kt" ".*Service.kt" ".*Manager.kt")

# 日志函数
log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] FALLBACK: $message" | tee -a "$FALLBACK_LOG" >&2
}

# 记录系统指标
record_system_metric() {
    local metric_type="$1"
    local metric_value="$2"
    local context="${3:-}"
    local timestamp=$(date -Iseconds)
    
    local metric_entry="{
        \"timestamp\": \"$timestamp\",
        \"metric_type\": \"$metric_type\",
        \"value\": \"$metric_value\",
        \"context\": {
            \"file\": \"$FILE_PATH\",
            \"tool\": \"$TOOL_NAME\",
            \"agent\": \"$AGENT_NAME\",
            \"additional\": \"$context\"
        }
    }"
    
    echo "$metric_entry" >> "$METRICS_FILE"
}

# 检查是否为关键文件
is_critical_file() {
    local filepath="$1"
    for pattern in "${CRITICAL_FILE_PATTERNS[@]}"; do
        if [[ "$filepath" =~ $pattern ]]; then
            return 0
        fi
    done
    return 1
}

# 获取历史错误统计
get_error_history() {
    local timeframe="${1:-3600}"  # 默认1小时
    local since_time=$(date -d "$timeframe seconds ago" -Iseconds 2>/dev/null || date -v-${timeframe}S -Iseconds)
    
    if [[ -f "$METRICS_FILE" ]]; then
        grep "error" "$METRICS_FILE" | grep -c "$since_time" || echo "0"
    else
        echo "0"
    fi
}

# 评估任务复杂度
assess_task_complexity() {
    local complexity_score=0
    
    # 基于工具类型
    case "$TOOL_NAME" in
        "MultiEdit") complexity_score=$((complexity_score + 4)) ;;
        "Write") 
            if is_critical_file "$FILE_PATH"; then
                complexity_score=$((complexity_score + 3))
            else
                complexity_score=$((complexity_score + 2))
            fi
            ;;
        "Edit") complexity_score=$((complexity_score + 2)) ;;
        "Bash") complexity_score=$((complexity_score + 3)) ;;
    esac
    
    # 基于文件类型和位置
    if [[ "$FILE_PATH" =~ build\.gradle\.kts$ ]]; then
        complexity_score=$((complexity_score + 2))
    fi
    
    if [[ "$FILE_PATH" =~ src/.*/ai/|src/.*/intelligence/ ]]; then
        complexity_score=$((complexity_score + 2))
    fi
    
    echo $complexity_score
}

# 检查系统健康状态
check_system_health() {
    log "INFO" "检查系统健康状态..."
    
    local health_issues=0
    
    # 检查编译状态
    if ! ./gradlew compileKotlin --quiet 2>/dev/null; then
        log "WARNING" "编译失败检测"
        health_issues=$((health_issues + 1))
        record_system_metric "compilation_failure" "1" "compile_check"
    fi
    
    # 检查磁盘空间
    local disk_usage=$(df . | tail -1 | awk '{print $5}' | sed 's/%//')
    if [[ $disk_usage -gt 90 ]]; then
        log "WARNING" "磁盘空间不足: ${disk_usage}%"
        health_issues=$((health_issues + 1))
    fi
    
    # 检查内存使用（如果可用）
    if command -v free >/dev/null 2>&1; then
        local mem_usage=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
        if [[ $mem_usage -gt 85 ]]; then
            log "WARNING" "内存使用过高: ${mem_usage}%"
            health_issues=$((health_issues + 1))
        fi
    fi
    
    echo $health_issues
}

# 决策降级策略
decide_fallback_strategy() {
    local complexity=$(assess_task_complexity)
    local error_history=$(get_error_history)
    local health_issues=$(check_system_health)
    
    log "INFO" "评估状态 - 复杂度:$complexity, 历史错误:$error_history, 健康问题:$health_issues"
    
    # 决策矩阵
    local intervention_required=false
    local fallback_strategy="none"
    local reason=""
    
    # 关键文件 + 高复杂度 = 人工介入
    if is_critical_file "$FILE_PATH" && [[ $complexity -gt $COMPLEXITY_THRESHOLD ]]; then
        intervention_required=true
        fallback_strategy="human_review"
        reason="关键文件的高复杂度操作"
    fi
    
    # 连续错误过多 = 降级到基础模式
    if [[ $error_history -gt $MAX_CONSECUTIVE_ERRORS ]]; then
        if [[ $complexity -gt 6 ]]; then
            intervention_required=true
            fallback_strategy="human_intervention"
            reason="连续错误过多且任务复杂"
        else
            fallback_strategy="basic_mode"
            reason="连续错误过多，降级到基础模式"
        fi
    fi
    
    # 系统健康问题 = 延迟执行
    if [[ $health_issues -gt 2 ]]; then
        fallback_strategy="delay_execution"
        reason="系统健康状态不佳"
    fi
    
    # 执行时间过长 = 超时处理
    if [[ $EXECUTION_TIME -gt $MAX_EXECUTION_TIME ]]; then
        intervention_required=true
        fallback_strategy="timeout_intervention"
        reason="执行时间超过阈值"
    fi
    
    echo "$intervention_required,$fallback_strategy,$reason"
}

# 创建人工介入请求
create_human_intervention_request() {
    local reason="$1"
    local strategy="$2"
    local priority="${3:-medium}"
    
    local request="{
        \"timestamp\": \"$(date -Iseconds)\",
        \"file\": \"$FILE_PATH\",
        \"tool\": \"$TOOL_NAME\",
        \"agent\": \"$AGENT_NAME\",
        \"reason\": \"$reason\",
        \"strategy\": \"$strategy\",
        \"priority\": \"$priority\",
        \"context\": {
            \"error_count\": $ERROR_COUNT,
            \"execution_time\": $EXECUTION_TIME,
            \"complexity_score\": $(assess_task_complexity)
        }
    }"
    
    echo "$request" > "$HUMAN_INTERVENTION_FLAG"
    log "CRITICAL" "已创建人工介入请求: $reason"
    
    # 发送通知（如果有配置）
    if command -v osascript >/dev/null 2>&1; then
        osascript -e "display notification \"AI开发需要人工干预: $reason\" with title \"Linch Mind\" sound name \"Glass\""
    fi
}

# 执行降级策略
execute_fallback_strategy() {
    local strategy="$1"
    local reason="$2"
    
    log "INFO" "执行降级策略: $strategy (原因: $reason)"
    
    case "$strategy" in
        "human_review")
            create_human_intervention_request "$reason" "$strategy" "high"
            echo "{\"action\": \"require_human_review\", \"reason\": \"$reason\", \"priority\": \"high\"}"
            return 1
            ;;
        "human_intervention")
            create_human_intervention_request "$reason" "$strategy" "critical"
            echo "{\"action\": \"require_human_intervention\", \"reason\": \"$reason\", \"priority\": \"critical\"}"
            return 2
            ;;
        "basic_mode")
            log "INFO" "切换到基础模式执行"
            echo "{\"action\": \"switch_to_basic_mode\", \"reason\": \"$reason\"}"
            # 这里可以设置环境变量或配置，指示使用更简单的处理模式
            export CLAUDE_BASIC_MODE=true
            ;;
        "delay_execution")
            log "INFO" "延迟执行，等待系统恢复"
            sleep 30
            echo "{\"action\": \"delayed_execution\", \"reason\": \"$reason\"}"
            ;;
        "timeout_intervention")
            create_human_intervention_request "$reason" "$strategy" "critical"
            echo "{\"action\": \"timeout_abort\", \"reason\": \"$reason\"}"
            return 3
            ;;
        "none")
            log "INFO" "无需降级，继续正常执行"
            echo "{\"action\": \"continue\", \"reason\": \"系统状态正常\"}"
            ;;
    esac
    
    record_system_metric "fallback_strategy" "$strategy" "$reason"
}

# 清理过期的人工介入请求
cleanup_intervention_requests() {
    if [[ -f "$HUMAN_INTERVENTION_FLAG" ]]; then
        local request_age=$(stat -c %Y "$HUMAN_INTERVENTION_FLAG" 2>/dev/null || stat -f %m "$HUMAN_INTERVENTION_FLAG" 2>/dev/null || echo "0")
        local current_time=$(date +%s)
        local age_hours=$(( (current_time - request_age) / 3600 ))
        
        # 如果请求超过24小时，自动清理
        if [[ $age_hours -gt 24 ]]; then
            rm -f "$HUMAN_INTERVENTION_FLAG"
            log "INFO" "清理过期的人工介入请求 (${age_hours}小时前)"
        fi
    fi
}

# 主执行流程
main() {
    log "INFO" "开始智能降级评估: $FILE_PATH (代理: $AGENT_NAME)"
    
    # 创建必要的目录
    mkdir -p "$(dirname "$FALLBACK_LOG")"
    mkdir -p "$(dirname "$METRICS_FILE")"
    
    # 清理过期请求
    cleanup_intervention_requests
    
    # 检查是否已有人工介入请求
    if [[ -f "$HUMAN_INTERVENTION_FLAG" ]]; then
        log "WARNING" "存在待处理的人工介入请求"
        echo "{\"action\": \"pending_human_intervention\", \"reason\": \"存在未处理的人工介入请求\"}"
        return 1
    fi
    
    # 评估和决策
    local decision_result=$(decide_fallback_strategy)
    IFS=',' read -r intervention_required strategy reason <<< "$decision_result"
    
    # 记录决策过程
    record_system_metric "fallback_decision" "$strategy" "$reason"
    
    # 执行策略
    execute_fallback_strategy "$strategy" "$reason"
    
    log "INFO" "智能降级评估完成"
}

# 执行主逻辑
main

log "INFO" "智能降级系统执行完成"