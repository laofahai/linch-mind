#!/bin/bash

# 智能连接器启动脚本
# 自动检测平台并启动对应的连接器版本

set -e

SCRIPT_DIR="$(dirname "$0")"
CONNECTOR_NAME="${1:-}"

# 显示使用说明
show_usage() {
    echo "Linch Mind Connector Smart Launcher"
    echo "===================================="
    echo ""
    echo "Usage: $0 <connector-name> [args...]"
    echo ""
    echo "Examples:"
    echo "  $0 clipboard                    # 启动剪贴板连接器"
    echo "  $0 filesystem --help           # 显示文件系统连接器帮助"
    echo "  $0 clipboard --daemon-url http://localhost:8080"
    echo ""
    echo "Available connectors:"
    
    # 查找可用的连接器
    if [ -d "$SCRIPT_DIR/../connectors" ]; then
        find "$SCRIPT_DIR/../connectors" -name "*-connector-*" -executable 2>/dev/null | \
        sed 's/.*\///g' | sed 's/-connector-.*//' | sort -u | sed 's/^/  - /'
    else
        echo "  (No connectors found in expected location)"
    fi
}

# 检测当前平台
detect_platform() {
    local os=$(uname -s)
    local arch=$(uname -m)
    
    case "$os" in
        "Linux")
            case "$arch" in
                "x86_64"|"amd64")
                    echo "linux-x64"
                    ;;
                "aarch64"|"arm64")
                    echo "linux-arm64"
                    ;;
                *)
                    echo "linux-x64"  # 默认
                    ;;
            esac
            ;;
        "Darwin")
            case "$arch" in
                "x86_64"|"amd64")
                    echo "macos-x64"
                    ;;
                "arm64")
                    echo "macos-arm64"
                    ;;
                *)
                    echo "macos-x64"  # 默认
                    ;;
            esac
            ;;
        "CYGWIN"*|"MINGW"*|"MSYS"*)
            case "$arch" in
                "x86_64"|"amd64")
                    echo "windows-x64"
                    ;;
                *)
                    echo "windows-x64"  # 默认
                    ;;
            esac
            ;;
        *)
            echo "linux-x64"  # 默认假设Linux
            ;;
    esac
}

# 查找连接器可执行文件
find_connector() {
    local connector_name="$1"
    local platform="$2"
    
    # 可能的搜索路径
    local search_paths=(
        "$SCRIPT_DIR/../connectors/release/dist"
        "$SCRIPT_DIR/../../connectors/release/dist" 
        "$SCRIPT_DIR/../release/dist"
        "./connectors/release/dist"
        "./release/dist"
        "."
    )
    
    # 可能的文件名模式
    local file_patterns=(
        "${connector_name}-connector-${platform}"
        "${connector_name}-connector-${platform}.exe"
        "${connector_name}-connector"
        "${connector_name}-connector.exe"
    )
    
    for search_path in "${search_paths[@]}"; do
        if [ -d "$search_path" ]; then
            for pattern in "${file_patterns[@]}"; do
                local full_path="$search_path/$pattern"
                if [ -f "$full_path" ] && [ -x "$full_path" ]; then
                    echo "$full_path"
                    return 0
                fi
            done
        fi
    done
    
    return 1
}

# 主逻辑
main() {
    # 检查参数
    if [ -z "$CONNECTOR_NAME" ] || [ "$CONNECTOR_NAME" = "--help" ] || [ "$CONNECTOR_NAME" = "-h" ]; then
        show_usage
        exit 0
    fi
    
    echo "🚀 Linch Mind Connector Smart Launcher"
    echo "======================================"
    echo ""
    
    # 检测平台
    local platform=$(detect_platform)
    echo "🔍 Detected platform: $platform"
    
    # 查找连接器
    echo "📦 Looking for connector: $CONNECTOR_NAME"
    
    local connector_path
    if connector_path=$(find_connector "$CONNECTOR_NAME" "$platform"); then
        echo "✅ Found connector: $connector_path"
        
        # 获取连接器信息
        local connector_size=$(ls -lh "$connector_path" | awk '{print $5}')
        echo "📊 Binary size: $connector_size" 
        
        echo ""
        echo "🎯 Launching connector with arguments: ${@:2}"
        echo "───────────────────────────────────────────────"
        
        # 启动连接器，传递所有剩余参数
        exec "$connector_path" "${@:2}"
        
    else
        echo "❌ Connector not found: $CONNECTOR_NAME"
        echo ""
        echo "🔍 Searched for the following files:"
        echo "   - ${CONNECTOR_NAME}-connector-${platform}"
        echo "   - ${CONNECTOR_NAME}-connector-${platform}.exe"
        echo "   - ${CONNECTOR_NAME}-connector"
        echo "   - ${CONNECTOR_NAME}-connector.exe"
        echo ""
        echo "💡 Tips:"
        echo "   1. Make sure the connector is properly installed"
        echo "   2. Check that the connector name is correct"
        echo "   3. Verify the binary has execute permissions"
        echo "   4. Try running from the project root directory"
        echo ""
        
        show_usage
        exit 1
    fi
}

main "$@"