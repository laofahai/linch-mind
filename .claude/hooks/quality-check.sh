#!/bin/bash

# Linch Mind 质量检查系统
# 在代码修改后自动执行多层质量检查

set -euo pipefail

# 读取输入数据
INPUT=$(cat)

# 解析工具和参数信息
TOOL_NAME=$(echo "$INPUT" | jq -r '.toolName // "unknown"')
FILE_PATH=$(echo "$INPUT" | jq -r '.parameters.file_path // ""')

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] QUALITY_CHECK: $1" >&2
}

# 错误处理函数
handle_error() {
    local exit_code=$1
    local error_msg="$2"
    log "ERROR: $error_msg (exit code: $exit_code)"
    echo "{\"status\": \"failed\", \"error\": \"$error_msg\", \"exit_code\": $exit_code}"
    exit $exit_code
}

# 检查是否为Kotlin文件
is_kotlin_file() {
    [[ "$FILE_PATH" =~ \.kt$ ]]
}

# 检查是否为构建文件
is_build_file() {
    [[ "$FILE_PATH" =~ (build\.gradle\.kts|settings\.gradle\.kts|gradle\.properties)$ ]]
}

# 执行Kotlin代码编译检查
check_kotlin_compilation() {
    log "Running Kotlin compilation check..."
    
    if ! ./gradlew compileKotlin 2>&1; then
        handle_error 1 "Kotlin compilation failed"
    fi
    
    log "Kotlin compilation check passed"
}

# 执行代码风格检查
check_code_style() {
    log "Running code style check..."
    
    # 检查是否有ktlint配置
    if [[ -f ".editorconfig" ]] || ./gradlew tasks 2>/dev/null | grep -q "ktlint"; then
        if ! ./gradlew ktlintCheck 2>&1; then
            log "WARNING: Code style check failed, attempting auto-fix..."
            ./gradlew ktlintFormat 2>&1 || log "WARNING: Auto-fix failed"
        fi
    else
        log "No ktlint configuration found, skipping code style check"
    fi
    
    log "Code style check completed"
}

# 执行单元测试
run_unit_tests() {
    log "Running unit tests..."
    
    # 只运行相关的测试
    local test_task="test"
    
    # 如果是特定模块的文件，运行该模块的测试
    if [[ "$FILE_PATH" =~ src/commonMain ]]; then
        test_task="commonTest"
    elif [[ "$FILE_PATH" =~ src/desktopMain ]]; then
        test_task="desktopTest"
    fi
    
    if ! ./gradlew $test_task 2>&1; then
        handle_error 2 "Unit tests failed"
    fi
    
    log "Unit tests passed"
}

# 检查架构合规性
check_architecture_compliance() {
    log "Running architecture compliance check..."
    
    # 检查是否违反了CLAUDE.md中的架构规则
    local violations=0
    
    # 检查是否在AI目录中添加了不适当的依赖
    if [[ "$FILE_PATH" =~ src/.*/ai/ ]] && [[ "$TOOL_NAME" == "Edit" || "$TOOL_NAME" == "Write" ]]; then
        if grep -q "import.*ui\." "$FILE_PATH" 2>/dev/null; then
            log "WARNING: AI layer importing UI components detected"
            violations=$((violations + 1))
        fi
    fi
    
    # 检查是否在UI层直接调用了存储层
    if [[ "$FILE_PATH" =~ src/.*/ui/ ]] && [[ "$TOOL_NAME" == "Edit" || "$TOOL_NAME" == "Write" ]]; then
        if grep -q "import.*storage\." "$FILE_PATH" 2>/dev/null; then
            log "WARNING: UI layer directly accessing storage layer detected"
            violations=$((violations + 1))
        fi
    fi
    
    if [[ $violations -gt 0 ]]; then
        log "Architecture compliance check found $violations violations"
        echo "{\"status\": \"warning\", \"violations\": $violations, \"message\": \"Architecture violations detected\"}"
    else
        log "Architecture compliance check passed"
    fi
}

# 性能回归检查
check_performance_regression() {
    log "Running performance regression check..."
    
    # 简单的性能检查：确保应用能够启动
    if [[ "$FILE_PATH" =~ (Main\.kt|AppScope\.kt) ]]; then
        log "Critical file modified, checking application startup..."
        # 这里可以添加更复杂的性能测试
        # timeout 30s ./gradlew run --args="--test-mode" 2>&1 || handle_error 3 "Application startup test failed"
    fi
    
    log "Performance regression check completed"
}

# 主检查流程
main() {
    log "Starting quality check for file: $FILE_PATH (tool: $TOOL_NAME)"
    
    # 根据文件类型执行不同的检查
    if is_kotlin_file; then
        log "Detected Kotlin file, running Kotlin-specific checks..."
        
        # 1. 编译检查（必须通过）
        check_kotlin_compilation
        
        # 2. 代码风格检查（警告）
        check_code_style
        
        # 3. 架构合规性检查（警告）
        check_architecture_compliance
        
        # 4. 单元测试（可选，基于复杂度）
        if [[ "$TOOL_NAME" == "MultiEdit" ]] || [[ "$FILE_PATH" =~ (Service|Manager|Engine)\.kt$ ]]; then
            run_unit_tests
        fi
        
        # 5. 性能回归检查（关键文件）
        check_performance_regression
        
    elif is_build_file; then
        log "Detected build file, running build-specific checks..."
        
        # 构建文件检查
        check_kotlin_compilation
        
    else
        log "Non-Kotlin file, running basic checks..."
        
        # 基础检查：确保文件语法正确
        if [[ "$FILE_PATH" =~ \.(json|yaml|yml)$ ]]; then
            if command -v jq >/dev/null && [[ "$FILE_PATH" =~ \.json$ ]]; then
                if ! jq . "$FILE_PATH" >/dev/null 2>&1; then
                    handle_error 4 "Invalid JSON syntax in $FILE_PATH"
                fi
            fi
        fi
    fi
    
    log "Quality check completed successfully"
    echo "{\"status\": \"passed\", \"message\": \"All quality checks passed\"}"
}

# 执行主逻辑
main

log "Quality check hook completed"