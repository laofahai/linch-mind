#!/bin/bash

# Native builder for connectors with build.sh
# Usage: ./native_builder.sh <connector_path> <output_dir>

set -e

CONNECTOR_PATH="$1"
OUTPUT_DIR="$2"
CONNECTOR_ID="$3"

echo "🔧 Building native connector: $CONNECTOR_ID"

# Enter connector directory
cd "$CONNECTOR_PATH"

# Make build script executable
chmod +x build.sh

# Run build
echo "🚀 Running build script..."
./build.sh

# Find built binary (common patterns)
BINARY_CANDIDATES=(
    # New linch-mind naming convention
    "linch-mind-${CONNECTOR_ID}"
    "bin/release/linch-mind-${CONNECTOR_ID}"
    "bin/debug/linch-mind-${CONNECTOR_ID}"
    "dist/bin/linch-mind-${CONNECTOR_ID}"
    
    # Legacy naming patterns for backward compatibility
    "${CONNECTOR_ID}-connector"
    "clipboard-connector"
    "filesystem-connector" 
    "connector"
    "${CONNECTOR_ID}"
)

BUILT_BINARY=""
for candidate in "${BINARY_CANDIDATES[@]}"; do
    if [ -f "$candidate" ]; then
        BUILT_BINARY="$candidate"
        break
    fi
done

if [ -z "$BUILT_BINARY" ]; then
    echo "❌ No binary found. Searched for: ${BINARY_CANDIDATES[*]}"
    exit 1
fi

echo "✅ Found binary: $BUILT_BINARY"

# Get binary size
SIZE=$(ls -lh "$BUILT_BINARY" | awk '{print $5}')
echo "📊 Binary size: $SIZE"

echo "📦 Native build completed successfully"
echo "BUILT_BINARY=$BUILT_BINARY"