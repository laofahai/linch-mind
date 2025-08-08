#!/bin/bash

# 多平台连接器构建脚本
# 为特定平台构建连接器并处理平台特定的命名

set -e

echo "🚀 Starting Multi-Platform Connector Build"
echo "============================================="

# 环境变量检查
PLATFORM="${PLATFORM:-linux}"
ARCH="${ARCH:-x64}"
ARTIFACT_SUFFIX="${ARTIFACT_SUFFIX:-linux-x64}"
CHANGED_CONNECTORS="${CHANGED_CONNECTORS}"

echo "📋 Build Configuration:"
echo "   Platform: $PLATFORM"
echo "   Architecture: $ARCH" 
echo "   Artifact Suffix: $ARTIFACT_SUFFIX"
echo "   Changed Connectors: $CHANGED_CONNECTORS"
echo ""

if [ -z "$CHANGED_CONNECTORS" ]; then
    echo "✅ No connector changes detected, exiting"
    exit 0
fi

# 切换到项目根目录
cd "$(dirname "$0")/../.."

# 创建平台特定的输出目录
OUTPUT_DIR="connectors/release/dist-${ARTIFACT_SUFFIX}"
mkdir -p "$OUTPUT_DIR"

echo "📦 Will build connectors: $CHANGED_CONNECTORS"
echo "📁 Output directory: $OUTPUT_DIR"
echo ""

# 构建每个连接器
success_count=0
fail_count=0
failed_connectors=""

for connector_path in $CHANGED_CONNECTORS; do
    echo ""
    echo "=" "Building $connector_path for $PLATFORM-$ARCH" "="
    
    cd connectors
    
    # 使用现有的构建器，但指定平台特定的输出目录
    if ../scripts/build-tools/build_connector.sh "$connector_path" "../$OUTPUT_DIR"; then
        # 重命名二进制文件添加平台后缀
        connector_id=$(jq -r '.id' "$connector_path/connector.json")
        
        # 平台特定的文件扩展名
        case "$PLATFORM" in
            "windows")
                binary_ext=".exe"
                ;;
            *)
                binary_ext=""
                ;;
        esac
        
        # 查找实际的二进制文件（支持新旧命名格式）
        original_binary=""
        for binary_candidate in "../$OUTPUT_DIR/linch-mind-${connector_id}" "../$OUTPUT_DIR/${connector_id}-connector" "../$OUTPUT_DIR/${connector_id}"; do
            if [ -f "${binary_candidate}${binary_ext}" ]; then
                original_binary="${binary_candidate}${binary_ext}"
                break
            fi
        done
        
        original_zip="../$OUTPUT_DIR/${connector_id}-connector.zip"
        
        # 平台特定的文件名（使用新的命名格式）
        platform_binary="../$OUTPUT_DIR/linch-mind-${connector_id}-${ARTIFACT_SUFFIX}${binary_ext}"
        platform_zip="../$OUTPUT_DIR/linch-mind-${connector_id}-${ARTIFACT_SUFFIX}.zip"
        
        # 重命名二进制文件
        if [ -f "$original_binary" ]; then
            mv "$original_binary" "$platform_binary"
            echo "📝 Renamed binary: $(basename "$platform_binary")"
        fi
        
        # 重命名ZIP包
        if [ -f "$original_zip" ]; then
            mv "$original_zip" "$platform_zip"
            echo "📦 Renamed package: $(basename "$platform_zip")"
        fi
        
        echo "✅ Successfully built $connector_path for $PLATFORM-$ARCH"
        success_count=$((success_count + 1))
    else
        echo "❌ Failed to build $connector_path for $PLATFORM-$ARCH"
        fail_count=$((fail_count + 1))
        failed_connectors="$failed_connectors $connector_path"
    fi
    
    cd ..
done

echo ""
echo "📊 Build Summary for $PLATFORM-$ARCH:"
echo "   ✅ Successful: $success_count"
echo "   ❌ Failed: $fail_count"

if [ $fail_count -gt 0 ]; then
    echo "   Failed connectors: $failed_connectors"
fi

# 列出构建的制品
echo ""
echo "📦 Built artifacts for $PLATFORM-$ARCH:"
if [ -d "$OUTPUT_DIR" ] && [ "$(ls -A "$OUTPUT_DIR" 2>/dev/null)" ]; then
    ls -lh "$OUTPUT_DIR"/
else
    echo "No artifacts found"
fi

# 生成平台特定的registry.json
echo ""
echo "🗃️ Generating platform-specific registry..."
cd connectors
scripts/registry_generator --output "release/registry-${ARTIFACT_SUFFIX}.json" --format --platform "$PLATFORM" --arch "$ARCH"

# 创建平台信息文件
cat > "release/platform-info-${ARTIFACT_SUFFIX}.json" << EOF
{
    "platform": "$PLATFORM",
    "arch": "$ARCH", 
    "artifact_suffix": "$ARTIFACT_SUFFIX",
    "build_time": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "built_connectors": [$(echo "$CHANGED_CONNECTORS" | sed 's/ /", "/g' | sed 's/^/"/;s/$/"/')],
    "successful_builds": $success_count,
    "failed_builds": $fail_count
}
EOF

echo "✅ Platform info saved: release/platform-info-${ARTIFACT_SUFFIX}.json"

# 失败时退出
if [ $fail_count -gt 0 ]; then
    exit 1
fi

echo ""
echo "🎉 Multi-platform build completed successfully for $PLATFORM-$ARCH!"

exit 0