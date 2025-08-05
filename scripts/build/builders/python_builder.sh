#!/bin/bash

# Python builder for connectors with main.py
# Usage: ./python_builder.sh <connector_path> <output_dir>

set -e

CONNECTOR_PATH="$1"
OUTPUT_DIR="$2" 
CONNECTOR_ID="$3"

echo "🐍 Building Python connector: $CONNECTOR_ID"

# Check for requirements.txt
if [ -f "$CONNECTOR_PATH/requirements.txt" ]; then
    echo "📦 Installing Python dependencies..."
    pip install -r "$CONNECTOR_PATH/requirements.txt"
fi

# Use PyInstaller to build
echo "🔨 Building with PyInstaller..."
cd "$CONNECTOR_PATH"

pyinstaller \
    --onefile \
    --name "${CONNECTOR_ID}-connector" \
    --distpath "dist" \
    --clean \
    --noconfirm \
    --strip \
    --optimize=2 \
    main.py

BUILT_BINARY="dist/${CONNECTOR_ID}-connector"

if [ ! -f "$BUILT_BINARY" ]; then
    echo "❌ PyInstaller build failed"
    exit 1
fi

echo "✅ Found binary: $BUILT_BINARY"

# Get binary size
SIZE=$(ls -lh "$BUILT_BINARY" | awk '{print $5}')
echo "📊 Binary size: $SIZE"

echo "📦 Python build completed successfully"
echo "BUILT_BINARY=$BUILT_BINARY"