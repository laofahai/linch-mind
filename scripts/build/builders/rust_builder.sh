#!/bin/bash

# Rust builder for connectors with Cargo.toml
# Usage: ./rust_builder.sh <connector_path> <output_dir>

set -e

CONNECTOR_PATH="$1"
OUTPUT_DIR="$2"
CONNECTOR_ID="$3"

echo "🦀 Building Rust connector: $CONNECTOR_ID"

# Enter connector directory
cd "$CONNECTOR_PATH"

# Check for Cargo.toml
if [ ! -f "Cargo.toml" ]; then
    echo "❌ No Cargo.toml found in $CONNECTOR_PATH"
    exit 1
fi

# Build with cargo
echo "🔨 Building with cargo..."
cargo build --release

# Find built binary
BUILT_BINARY="target/release/${CONNECTOR_ID}-connector"

# Try alternative names if not found
if [ ! -f "$BUILT_BINARY" ]; then
    BUILT_BINARY="target/release/${CONNECTOR_ID}"
fi

if [ ! -f "$BUILT_BINARY" ]; then
    # Try to find any binary in release directory
    BUILT_BINARY=$(find target/release -maxdepth 1 -type f -executable | head -1)
fi

if [ ! -f "$BUILT_BINARY" ]; then
    echo "❌ No binary found in target/release/"
    exit 1
fi

echo "✅ Found binary: $BUILT_BINARY"

# Get binary size
SIZE=$(ls -lh "$BUILT_BINARY" | awk '{print $5}')
echo "📊 Binary size: $SIZE"

echo "📦 Rust build completed successfully"
echo "BUILT_BINARY=$BUILT_BINARY"