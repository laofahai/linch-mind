#!/bin/bash

# Go builder for connectors with go.mod
# Usage: ./go_builder.sh <connector_path> <output_dir>

set -e

CONNECTOR_PATH="$1"
OUTPUT_DIR="$2"
CONNECTOR_ID="$3"

echo "🐹 Building Go connector: $CONNECTOR_ID"

# Enter connector directory
cd "$CONNECTOR_PATH"

# Check for go.mod
if [ ! -f "go.mod" ]; then
    echo "❌ No go.mod found in $CONNECTOR_PATH"
    exit 1
fi

# Build with go
echo "🔨 Building with go..."
go build -ldflags="-s -w" -o "${CONNECTOR_ID}-connector" .

BUILT_BINARY="${CONNECTOR_ID}-connector"

if [ ! -f "$BUILT_BINARY" ]; then
    echo "❌ Go build failed"
    exit 1
fi

echo "✅ Found binary: $BUILT_BINARY"

# Get binary size
SIZE=$(ls -lh "$BUILT_BINARY" | awk '{print $5}')
echo "📊 Binary size: $SIZE"

echo "📦 Go build completed successfully"
echo "BUILT_BINARY=$BUILT_BINARY"