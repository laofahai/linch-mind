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

# Read connector configuration
CONNECTOR_ID=$(python3 -c "import json; print(json.load(open('$CONNECTOR_PATH/connector.json'))['id'])")
echo "📦 Building connector: $CONNECTOR_ID from $CONNECTOR_PATH"

# Detect connector type and build
SCRIPT_DIR="$(dirname "$0")"
BUILT_BINARY=""
BUILDER_USED=""

if [ -f "$CONNECTOR_PATH/build.sh" ]; then
    echo "🔧 Detected native connector (build.sh)"
    BUILDER_USED="native"
    
elif [ -f "$CONNECTOR_PATH/Cargo.toml" ]; then
    echo "🦀 Detected Rust connector (Cargo.toml)"
    BUILDER_USED="rust"
    
elif [ -f "$CONNECTOR_PATH/go.mod" ]; then
    echo "🐹 Detected Go connector (go.mod)"
    BUILDER_USED="go"
    
elif [ -f "$CONNECTOR_PATH/main.py" ]; then
    echo "🐍 Detected Python connector (main.py)"
    BUILDER_USED="python"
    
else
    echo "❌ Unknown connector type in $CONNECTOR_PATH"
    echo "   Supported:"  
    echo "     - build.sh (native C++/C)"
    echo "     - Cargo.toml (Rust)"
    echo "     - go.mod (Go)"
    echo "     - main.py (Python)"
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

# Copy to output directory with standard name
FINAL_BINARY="$OUTPUT_DIR/${CONNECTOR_ID}-connector"
cp "$BUILT_BINARY" "$FINAL_BINARY"

# Get final binary size
SIZE=$(ls -lh "$FINAL_BINARY" | awk '{print $5}')
echo "📊 Final binary size: $SIZE"

# Create ZIP package
cd "$OUTPUT_DIR"
ZIP_NAME="${CONNECTOR_ID}-connector.zip"

echo "📦 Creating ZIP package: $ZIP_NAME"
zip "$ZIP_NAME" "${CONNECTOR_ID}-connector"

# Add connector.json
zip "$ZIP_NAME" -j "$CONNECTOR_PATH/connector.json"

# Add README if exists
if [ -f "$CONNECTOR_PATH/README.md" ]; then
    zip "$ZIP_NAME" -j "$CONNECTOR_PATH/README.md"
fi

# Show ZIP size
ZIP_SIZE=$(ls -lh "$ZIP_NAME" | awk '{print $5}')
echo "📋 ZIP package size: $ZIP_SIZE"

echo ""
echo "✅ Build completed successfully!"
echo "📁 Artifacts:"
echo "   Binary: $FINAL_BINARY"
echo "   Package: $OUTPUT_DIR/$ZIP_NAME"