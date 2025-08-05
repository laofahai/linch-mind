#!/bin/bash

# 合并多平台构建结果并创建统一的发布包
# 用于GitHub Actions的release阶段

set -e

echo "🔄 Merging Multi-Platform Connector Builds"
echo "==========================================="

# 环境变量检查
CHANGED_CONNECTORS="${CHANGED_CONNECTORS}"

if [ -z "$CHANGED_CONNECTORS" ]; then
    echo "✅ No connector changes to merge, exiting"
    exit 0
fi

echo "📋 Changed connectors: $CHANGED_CONNECTORS"
echo ""

# 切换到项目根目录
cd "$(dirname "$0")/../.."

# 创建最终的输出目录
FINAL_OUTPUT_DIR="connectors/release/dist"
mkdir -p "$FINAL_OUTPUT_DIR"

echo "📁 Final output directory: $FINAL_OUTPUT_DIR"
echo ""

# 平台列表
PLATFORMS=("linux-x64" "macos-x64" "windows-x64")

echo "🔍 Available artifacts:"
ls -la artifacts/ || echo "No artifacts directory found"
echo ""

# 合并所有平台的构建结果
for platform in "${PLATFORMS[@]}"; do
    platform_dir="artifacts/connectors-${platform}-v${GITHUB_RUN_NUMBER}"
    
    echo "📦 Processing platform: $platform"
    echo "   Looking for: $platform_dir"
    
    if [ -d "$platform_dir" ]; then
        echo "   ✅ Found artifacts for $platform"
        
        # 复制所有ZIP文件到最终目录
        if [ -d "$platform_dir/connectors/release/dist-${platform}" ]; then
            echo "   📋 Copying ZIP files..."
            cp "$platform_dir/connectors/release/dist-${platform}"/*.zip "$FINAL_OUTPUT_DIR/" 2>/dev/null || {
                echo "   ⚠️  No ZIP files found for $platform"
            }
            
            # 列出复制的文件
            ls -la "$platform_dir/connectors/release/dist-${platform}"/ | grep "\.zip" || echo "   No ZIP files"
        else
            echo "   ❌ Missing dist directory for $platform"
        fi
        
        # 复制平台信息文件
        if [ -f "$platform_dir/connectors/release/platform-info-${platform}.json" ]; then
            cp "$platform_dir/connectors/release/platform-info-${platform}.json" "$FINAL_OUTPUT_DIR/"
            echo "   ✅ Copied platform info"
        fi
    else
        echo "   ❌ Missing artifacts for $platform"
    fi
    echo ""
done

echo "📊 Final artifacts summary:"
if [ -d "$FINAL_OUTPUT_DIR" ] && [ "$(ls -A "$FINAL_OUTPUT_DIR" 2>/dev/null)" ]; then
    ls -lh "$FINAL_OUTPUT_DIR"/
    echo ""
    
    # 统计每个连接器的平台覆盖情况
    echo "🎯 Platform coverage by connector:"
    for connector_path in $CHANGED_CONNECTORS; do
        connector_id=$(jq -r '.id' "connectors/$connector_path/connector.json")
        echo "   📦 $connector_id:"
        
        platform_count=0
        for platform in "${PLATFORMS[@]}"; do
            zip_file="$FINAL_OUTPUT_DIR/${connector_id}-connector-${platform}.zip"
            if [ -f "$zip_file" ]; then
                size=$(ls -lh "$zip_file" | awk '{print $5}')
                echo "      ✅ $platform ($size)"
                platform_count=$((platform_count + 1))
            else
                echo "      ❌ $platform (missing)"
            fi
        done
        
        echo "      📊 Coverage: $platform_count/${#PLATFORMS[@]} platforms"
        echo ""
    done
else
    echo "❌ No final artifacts found"
fi

# 生成统一的注册表
echo "🗃️ Generating unified registry..."
cd connectors

# 首先生成基础注册表
scripts/registry_generator --output "release/registry.json" --format

# 如果有GitHub环境变量，更新下载URL
if [ -n "$GITHUB_RUN_NUMBER" ] && [ -n "$GITHUB_REF_NAME" ]; then
    RELEASE_TAG="v${GITHUB_RUN_NUMBER}-${GITHUB_REF_NAME}"
    echo "🔗 Updating download URLs with release tag: $RELEASE_TAG"
    
    scripts/registry_generator --update-urls "$RELEASE_TAG" --output "release/registry.json"
else
    echo "⚠️  GitHub environment not detected, skipping URL updates"
fi

# 复制注册表到最终目录
cp "release/registry.json" "$FINAL_OUTPUT_DIR/"

echo ""
echo "📋 Registry preview:"
head -20 "$FINAL_OUTPUT_DIR/registry.json" || echo "Registry file not found"

echo ""
echo "✅ Multi-platform build merge completed!"
echo ""
echo "📁 Final release artifacts:"
echo "   Directory: $FINAL_OUTPUT_DIR"
echo "   Contents:"
ls -la "$FINAL_OUTPUT_DIR"/ | grep -E "\.(zip|json)$" || echo "   No release files found"

# 创建发布摘要
cat > "$FINAL_OUTPUT_DIR/RELEASE_SUMMARY.md" << EOF
# Linch Mind Connectors Release

## Changed Connectors
$(echo "$CHANGED_CONNECTORS" | sed 's/ /\n/g' | sed 's/^/- /')

## Platform Support
$(for platform in "${PLATFORMS[@]}"; do
    count=$(ls "$FINAL_OUTPUT_DIR"/*-${platform}.zip 2>/dev/null | wc -l | tr -d ' ')
    echo "- $platform: $count connectors"
done)

## Build Information
- Build Number: ${GITHUB_RUN_NUMBER:-"local"}
- Commit: ${GITHUB_SHA:-"unknown"}
- Branch: ${GITHUB_REF_NAME:-"unknown"}
- Timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")

## Download Instructions
Each connector is available for multiple platforms:
\`\`\`
{connector-name}-connector-linux-x64.zip    # For Linux x64
{connector-name}-connector-macos-x64.zip    # For macOS x64  
{connector-name}-connector-windows-x64.zip  # For Windows x64
\`\`\`

Choose the appropriate package for your platform.
EOF

echo ""
echo "📄 Release summary created: $FINAL_OUTPUT_DIR/RELEASE_SUMMARY.md"

echo ""
echo "🚀 Ready for GitHub Release!"

exit 0