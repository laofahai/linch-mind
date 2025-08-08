#!/bin/bash

# Universal Connector Builder
# Automatically detects connector type and uses appropriate builder
# Usage: ./build_connector.sh <connector_path> <output_dir>

set -e

CONNECTOR_PATH="$1"
OUTPUT_DIR="$2"

if [ -z "$CONNECTOR_PATH" ] || [ -z "$OUTPUT_DIR" ]; then
    echo "Usage: $0 <connector_path> <output_dir>"
    echo "Example: $0 connectors/official/clipboard /tmp/build"
    exit 1
fi

if [ ! -f "$CONNECTOR_PATH/connector.json" ]; then
    echo "❌ Missing connector.json in $CONNECTOR_PATH"
    exit 1
fi

# Convert to absolute paths
CONNECTOR_PATH="$(cd "$CONNECTOR_PATH" && pwd)"
OUTPUT_DIR="$(mkdir -p "$OUTPUT_DIR" && cd "$OUTPUT_DIR" && pwd)"

# Read connector configuration using jq instead of python
CONNECTOR_ID=$(jq -r '.id' "$CONNECTOR_PATH/connector.json")
echo "📦 Building connector: $CONNECTOR_ID from $CONNECTOR_PATH"

# Detect connector type and build
SCRIPT_DIR="$(dirname "$0")"
BUILT_BINARY=""
BUILDER_USED=""

if [ -f "$CONNECTOR_PATH/build.sh" ]; then
    echo "🔧 Detected native connector (build.sh)"
    BUILDER_USED="native"
    
elif [ -f "$CONNECTOR_PATH/CMakeLists.txt" ]; then
    echo "🏗️ Detected CMake C++ connector (CMakeLists.txt)"
    BUILDER_USED="native"
    
elif [ -f "$CONNECTOR_PATH/Cargo.toml" ]; then
    echo "🦀 Detected Rust connector (Cargo.toml)"
    BUILDER_USED="rust"
    
elif [ -f "$CONNECTOR_PATH/go.mod" ]; then
    echo "🐹 Detected Go connector (go.mod)"
    BUILDER_USED="go"
    
else
    echo "❌ Unknown connector type in $CONNECTOR_PATH"
    echo "   Supported:"  
    echo "     - build.sh (native C++/C)"
    echo "     - CMakeLists.txt (C++ with CMake)"
    echo "     - Cargo.toml (Rust)"
    echo "     - go.mod (Go)"
    exit 1
fi

# Run appropriate builder
BUILD_OUTPUT=$("$SCRIPT_DIR/builders/${BUILDER_USED}_builder.sh" "$CONNECTOR_PATH" "$OUTPUT_DIR" "$CONNECTOR_ID")
echo "$BUILD_OUTPUT"

# Extract binary path from output
BUILT_BINARY=$(echo "$BUILD_OUTPUT" | grep "BUILT_BINARY=" | cut -d'=' -f2)
BUILT_BINARY="$CONNECTOR_PATH/$BUILT_BINARY"

# Verify binary exists
if [ ! -f "$BUILT_BINARY" ]; then
    echo "❌ Binary not found: $BUILT_BINARY"
    exit 1
fi

echo "✅ Binary verified: $BUILT_BINARY"

# Copy to output directory with new linch-mind naming standard
FINAL_BINARY="$OUTPUT_DIR/linch-mind-${CONNECTOR_ID}"
cp "$BUILT_BINARY" "$FINAL_BINARY"

# Get final binary size
SIZE=$(ls -lh "$FINAL_BINARY" | awk '{print $5}')
echo "📊 Final binary size: $SIZE"

# Create ZIP package
cd "$OUTPUT_DIR"
ZIP_NAME="linch-mind-${CONNECTOR_ID}.zip"

echo "📦 Creating ZIP package: $ZIP_NAME"
zip "$ZIP_NAME" "linch-mind-${CONNECTOR_ID}" || { echo "Warning: Failed to add binary to ZIP"; }

# Add connector.json
zip "$ZIP_NAME" -j "$CONNECTOR_PATH/connector.json" || { echo "Warning: Failed to add connector.json to ZIP"; }

# Add README if exists
if [ -f "$CONNECTOR_PATH/README.md" ]; then
    zip "$ZIP_NAME" -j "$CONNECTOR_PATH/README.md" || { echo "Warning: Failed to add README to ZIP"; }
fi

# Show ZIP size
ZIP_SIZE=$(ls -lh "$ZIP_NAME" | awk '{print $5}')
echo "📋 ZIP package size: $ZIP_SIZE"

echo ""
echo "✅ Build completed successfully!"
echo "📁 Artifacts:"
echo "   Binary: $FINAL_BINARY"
echo "   Package: $OUTPUT_DIR/$ZIP_NAME"

# Explicitly exit with success
exit 0