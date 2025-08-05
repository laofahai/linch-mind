#!/bin/bash

# Filesystem Connector Build Script
# Based on clipboard connector build process

set -e

echo "🔨 Building Linch Mind Filesystem Connector..."

# Create build directory
mkdir -p build
cd build

# Configure with CMake
echo "📋 Configuring with CMake..."
cmake -DCMAKE_BUILD_TYPE=Release ..

# Build the project
echo "🔧 Building project..."
make -j$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4)

# Create distribution directory
echo "📦 Creating distribution..."
mkdir -p ../dist/bin

# Copy executable to dist
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    cp filesystem-connector.exe ../dist/bin/
    echo "✅ Windows executable created: dist/bin/filesystem-connector.exe"
else
    cp filesystem-connector ../dist/bin/
    echo "✅ Executable created: dist/bin/filesystem-connector"
fi

# Install (optional)
if [[ "$1" == "--install" ]]; then
    echo "📥 Installing filesystem-connector..."
    make install
fi

echo "🎉 Build completed successfully!"
echo "📁 Executable location: $(pwd)/../dist/bin/"

# Show binary info
if command -v file >/dev/null 2>&1; then
    echo "📊 Binary info:"
    file ../dist/bin/filesystem-connector* | head -1
fi

if command -v ls >/dev/null 2>&1; then
    echo "📊 Binary size:"
    ls -lh ../dist/bin/filesystem-connector* | awk '{print $5, $9}'
fi