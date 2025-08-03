#!/bin/bash

# Linch Mind 高级质量门禁系统
# 多层质量检查，包括静态分析、动态测试、架构合规性和性能回归检测

set -euo pipefail

# 读取输入数据
INPUT=$(cat)

# 解析工具和参数信息
TOOL_NAME=$(echo "$INPUT" | jq -r '.toolName // "unknown"')
FILE_PATH=$(echo "$INPUT" | jq -r '.parameters.file_path // ""')
CHANGE_TYPE=$(echo "$INPUT" | jq -r '.changeType // "unknown"')

# 配置参数
PROJECT_ROOT="/Users/laofahai/Documents/workspace/linch-mind"
LOG_FILE=".claude/logs/quality-gate.log"
METRICS_FILE=".claude/logs/quality-metrics.json"

# 日志函数
log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] QUALITY_GATE: $message" | tee -a "$LOG_FILE" >&2
}

# 错误处理函数
handle_error() {
    local exit_code=$1
    local error_msg="$2"
    local severity="${3:-ERROR}"
    
    log "$severity" "$error_msg (exit code: $exit_code)"
    
    # 记录质量指标
    record_quality_metric "error" "$error_msg" "$exit_code"
    
    if [[ "$severity" == "ERROR" ]]; then
        echo "{\"status\": \"failed\", \"error\": \"$error_msg\", \"exit_code\": $exit_code, \"severity\": \"$severity\"}"
        exit $exit_code
    else
        echo "{\"status\": \"warning\", \"warning\": \"$error_msg\", \"exit_code\": $exit_code, \"severity\": \"$severity\"}"
    fi
}

# 记录质量指标
record_quality_metric() {
    local metric_type="$1"
    local metric_value="$2"
    local additional_info="${3:-}"
    local timestamp=$(date -Iseconds)
    
    # 创建或追加质量指标JSON
    local metric_entry="{
        \"timestamp\": \"$timestamp\",
        \"file\": \"$FILE_PATH\",
        \"tool\": \"$TOOL_NAME\",
        \"metric_type\": \"$metric_type\",
        \"value\": \"$metric_value\",
        \"additional_info\": \"$additional_info\"
    }"
    
    echo "$metric_entry" >> "$METRICS_FILE"
}

# 获取文件变更统计
get_change_stats() {
    if [[ -f "$FILE_PATH" ]]; then
        local lines_added=$(git diff --cached "$FILE_PATH" 2>/dev/null | grep "^+" | wc -l || echo "0")
        local lines_removed=$(git diff --cached "$FILE_PATH" 2>/dev/null | grep "^-" | wc -l || echo "0")
        echo "$lines_added,$lines_removed"
    else
        echo "0,0"
    fi
}

# 静态代码分析
perform_static_analysis() {
    log "INFO" "开始静态代码分析..."
    
    # Kotlin文件的特定检查
    if [[ "$FILE_PATH" =~ \.kt$ ]]; then
        # 检查代码复杂度
        local complexity_score=0
        
        # 计算圈复杂度指标
        local if_count=$(grep -c "if\s*(" "$FILE_PATH" 2>/dev/null || echo "0")
        local when_count=$(grep -c "when\s*(" "$FILE_PATH" 2>/dev/null || echo "0")
        local for_count=$(grep -c "for\s*(" "$FILE_PATH" 2>/dev/null || echo "0")
        local while_count=$(grep -c "while\s*(" "$FILE_PATH" 2>/dev/null || echo "0")
        
        complexity_score=$((if_count + when_count + for_count + while_count))
        
        log "INFO" "代码复杂度评分: $complexity_score"
        record_quality_metric "complexity" "$complexity_score"
        
        # 复杂度过高警告
        if [[ $complexity_score -gt 15 ]]; then
            handle_error 1 "代码复杂度过高 ($complexity_score)，建议重构" "WARNING"
        fi
        
        # 检查长方法
        local method_lengths=$(awk '/fun / { start=NR } /^}$/ && start { print NR-start; start=0 }' "$FILE_PATH" 2>/dev/null || echo "")
        if [[ -n "$method_lengths" ]]; then
            local max_method_length=$(echo "$method_lengths" | sort -nr | head -n1)
            if [[ $max_method_length -gt 50 ]]; then
                handle_error 2 "发现过长方法 ($max_method_length 行)，建议拆分" "WARNING"
            fi
        fi
        
        # 检查命名规范
        local bad_naming=$(grep -n "^[[:space:]]*\(fun\|val\|var\|class\)" "$FILE_PATH" | grep -E "(^[A-Z]|_[a-z])" || true)
        if [[ -n "$bad_naming" ]]; then
            handle_error 3 "发现命名规范问题" "WARNING"
        fi
    fi
    
    log "INFO" "静态代码分析完成"
}

# 架构合规性检查
check_architecture_compliance() {
    log "INFO" "开始架构合规性检查..."
    
    local violations=0
    
    # 分层架构检查
    if [[ "$FILE_PATH" =~ src/.*/ui/ ]]; then
        # UI层不应直接访问存储层
        if grep -q "import.*\.storage\." "$FILE_PATH" 2>/dev/null; then
            log "WARNING" "UI层直接访问存储层违规: $FILE_PATH"
            violations=$((violations + 1))
        fi
        
        # UI层不应直接访问AI服务层
        if grep -q "import.*\.ai\..*Service" "$FILE_PATH" 2>/dev/null; then
            log "WARNING" "UI层直接访问AI服务层违规: $FILE_PATH"
            violations=$((violations + 1))
        fi
    fi
    
    if [[ "$FILE_PATH" =~ src/.*/ai/ ]]; then
        # AI层不应导入UI组件
        if grep -q "import.*\.ui\." "$FILE_PATH" 2>/dev/null; then
            log "WARNING" "AI层导入UI组件违规: $FILE_PATH"
            violations=$((violations + 1))
        fi
    fi
    
    # 依赖方向检查
    if [[ "$FILE_PATH" =~ src/.*/storage/ ]]; then
        # 存储层不应依赖业务逻辑层
        if grep -q "import.*\.intelligence\." "$FILE_PATH" 2>/dev/null; then
            log "WARNING" "存储层依赖业务逻辑层违规: $FILE_PATH"
            violations=$((violations + 1))
        fi
    fi
    
    record_quality_metric "architecture_violations" "$violations"
    
    if [[ $violations -gt 0 ]]; then
        handle_error 4 "发现 $violations 个架构违规" "WARNING"
    fi
    
    log "INFO" "架构合规性检查完成"
}

# 性能影响分析
analyze_performance_impact() {
    log "INFO" "开始性能影响分析..."
    
    # 检查关键性能路径上的文件
    local is_critical_path=false
    
    case "$FILE_PATH" in
        *PersonalAssistant.kt|*GraphRAGService.kt|*VectorEmbeddingService.kt|*KnowledgeGraphView.kt)
            is_critical_path=true
            ;;
    esac
    
    if [[ "$is_critical_path" == "true" ]]; then
        log "INFO" "检测到关键性能路径文件，执行深度性能分析"
        record_quality_metric "critical_path_change" "true"
        
        # 对关键路径文件进行额外检查
        if [[ "$FILE_PATH" =~ \.kt$ ]]; then
            # 检查是否引入了阻塞调用
            local blocking_calls=$(grep -n "Thread\.sleep\|\.get()\|runBlocking" "$FILE_PATH" 2>/dev/null || echo "")
            if [[ -n "$blocking_calls" ]]; then
                handle_error 5 "关键路径中发现阻塞调用，可能影响性能" "WARNING"
            fi
            
            # 检查是否有大量对象创建
            local object_creation=$(grep -c "= [A-Z][a-zA-Z]*(" "$FILE_PATH" 2>/dev/null || echo "0")
            if [[ $object_creation -gt 20 ]]; then
                handle_error 6 "大量对象创建可能影响GC性能 ($object_creation 个)" "WARNING"
            fi
        fi
    fi
    
    log "INFO" "性能影响分析完成"
}

# 安全性检查
perform_security_check() {
    log "INFO" "开始安全性检查..."
    
    local security_issues=0
    
    if [[ "$FILE_PATH" =~ \.kt$ ]]; then
        # 检查硬编码密钥
        local hardcoded_secrets=$(grep -in "password\|secret\|key\|token" "$FILE_PATH" | grep -v "//\|/\*" || echo "")
        if [[ -n "$hardcoded_secrets" ]]; then
            log "WARNING" "发现可能的硬编码敏感信息"
            security_issues=$((security_issues + 1))
        fi
        
        # 检查SQL注入风险
        local sql_concat=$(grep -n "\".*+.*\"" "$FILE_PATH" | grep -i "select\|insert\|update\|delete" || echo "")
        if [[ -n "$sql_concat" ]]; then
            log "WARNING" "发现潜在SQL注入风险"
            security_issues=$((security_issues + 1))
        fi
        
        # 检查不安全的随机数生成
        local insecure_random=$(grep -n "Random()" "$FILE_PATH" || echo "")
        if [[ -n "$insecure_random" ]]; then
            log "WARNING" "使用不安全的随机数生成器"
            security_issues=$((security_issues + 1))
        fi
    fi
    
    record_quality_metric "security_issues" "$security_issues"
    
    if [[ $security_issues -gt 0 ]]; then
        handle_error 7 "发现 $security_issues 个安全问题" "WARNING"
    fi
    
    log "INFO" "安全性检查完成"
}

# 测试覆盖率检查
check_test_coverage() {
    log "INFO" "开始测试覆盖率检查..."
    
    # 检查是否为新增的重要文件
    if [[ "$TOOL_NAME" == "Write" ]] && [[ "$FILE_PATH" =~ (Service|Manager|Engine|Repository)\.kt$ ]]; then
        local base_name=$(basename "$FILE_PATH" .kt)
        local test_file=$(find src -name "${base_name}Test.kt" 2>/dev/null || echo "")
        
        if [[ -z "$test_file" ]]; then
            handle_error 8 "重要类 $base_name 缺少单元测试" "WARNING"
        else
            log "INFO" "找到对应测试文件: $test_file"
        fi
    fi
    
    log "INFO" "测试覆盖率检查完成"
}

# 生成质量报告
generate_quality_report() {
    local overall_status="passed"
    local warnings=0
    local errors=0
    
    # 统计最近的质量指标
    if [[ -f "$METRICS_FILE" ]]; then
        warnings=$(tail -n 50 "$METRICS_FILE" | jq -s 'map(select(.metric_type == "warning")) | length' 2>/dev/null || echo "0")
        errors=$(tail -n 50 "$METRICS_FILE" | jq -s 'map(select(.metric_type == "error")) | length' 2>/dev/null || echo "0")
    fi
    
    if [[ $errors -gt 0 ]]; then
        overall_status="failed"
    elif [[ $warnings -gt 0 ]]; then
        overall_status="warning"
    fi
    
    local quality_report="{
        \"status\": \"$overall_status\",
        \"file\": \"$FILE_PATH\",
        \"tool\": \"$TOOL_NAME\",
        \"timestamp\": \"$(date -Iseconds)\",
        \"statistics\": {
            \"warnings\": $warnings,
            \"errors\": $errors,
            \"change_stats\": \"$(get_change_stats)\"
        },
        \"checks_performed\": [
            \"static_analysis\",
            \"architecture_compliance\",
            \"performance_impact\",
            \"security_check\",
            \"test_coverage\"
        ]
    }"
    
    echo "$quality_report"
}

# 主执行流程
main() {
    log "INFO" "开始高级质量门禁检查: $FILE_PATH (工具: $TOOL_NAME)"
    
    # 创建日志目录
    mkdir -p "$(dirname "$LOG_FILE")"
    mkdir -p "$(dirname "$METRICS_FILE")"
    
    # 记录开始时间
    local start_time=$(date +%s)
    
    # 执行各项检查
    perform_static_analysis
    check_architecture_compliance
    analyze_performance_impact
    perform_security_check
    check_test_coverage
    
    # 记录执行时间
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    record_quality_metric "execution_time" "$duration"
    
    log "INFO" "质量门禁检查完成，耗时 ${duration}s"
    
    # 生成最终报告
    generate_quality_report
}

# 执行主逻辑
main

log "INFO" "高级质量门禁系统执行完成"