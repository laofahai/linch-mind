#!/bin/bash

# Create GitHub Release with artifacts
# Usage: ./create-github-release.sh <changed_connectors>

set -e

CHANGED_CONNECTORS="$1"
RELEASE_TAG="connectors-v${GITHUB_RUN_NUMBER:-$(date +%Y%m%d-%H%M%S)}"
RELEASE_TITLE="🔗 Connectors Release ${GITHUB_RUN_NUMBER:-$(date +%Y%m%d-%H%M%S)}"

if [ -z "$CHANGED_CONNECTORS" ]; then
    echo "Usage: $0 '<connector1> <connector2> ...'"
    exit 1
fi

echo "🏷️  Creating GitHub Release: $RELEASE_TAG"

# Create release notes
cat > /tmp/release_notes.md << EOF
📦 **连接器自动发布**

**更新的连接器**: $CHANGED_CONNECTORS

**提交信息**: ${GITHUB_EVENT_HEAD_COMMIT_MESSAGE:-"Manual release"}

---

### 📥 下载说明
- 下载对应连接器的ZIP文件
- ZIP包含可执行文件和配置文件
- 解压后按照README说明使用

### 🔧 构建信息
- **分支**: ${GITHUB_REF_NAME:-"main"}
- **提交**: ${GITHUB_SHA:-"$(git rev-parse HEAD)"}
- **构建号**: ${GITHUB_RUN_NUMBER:-"local"}
- **构建时间**: $(date -u '+%Y-%m-%d %H:%M:%S UTC')

### 📊 性能优化
- C++连接器体积: 50-200KB
- 启动速度: <0.1秒
- 内存占用: ~5MB
EOF

# Create release
echo "📝 Creating release with notes..."
gh release create "$RELEASE_TAG" \
    --title "$RELEASE_TITLE" \
    --notes-file /tmp/release_notes.md \
    --latest

# Upload ZIP packages
echo "📤 Uploading ZIP packages..."
cd connectors/release/dist

for zip_file in *.zip; do
    if [ -f "$zip_file" ]; then
        echo "   Uploading $zip_file..."
        gh release upload "$RELEASE_TAG" "$zip_file" --clobber
    fi
done

# Upload registry
if [ -f "../registry.json" ]; then
    echo "📋 Uploading registry.json..."
    gh release upload "$RELEASE_TAG" "../registry.json" --clobber
fi

echo "✅ GitHub Release created successfully: $RELEASE_TAG"