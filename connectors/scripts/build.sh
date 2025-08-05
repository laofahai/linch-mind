#!/bin/bash
# Build connector script tools
set -e

SCRIPT_DIR="$(dirname "$0")"
cd "$SCRIPT_DIR"

echo "🔨 Building connector script tools..."

# Create build directory
mkdir -p build
cd build

# Configure and build with CMake
cmake .. -DCMAKE_BUILD_TYPE=Release
make -j$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4)

# Install binaries to parent directory
make install

echo "✅ Build completed. Tools available in connectors/scripts/"
ls -la ../version_manager