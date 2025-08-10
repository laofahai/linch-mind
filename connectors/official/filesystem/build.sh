#!/bin/bash

# Filesystem Connector Build Script
# Delegates to the shared build script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SHARED_BUILD_SCRIPT="$SCRIPT_DIR/../../shared/scripts/build_connector.sh"

if [ ! -f "$SHARED_BUILD_SCRIPT" ]; then
    echo "❌ Shared build script not found at: $SHARED_BUILD_SCRIPT"
    echo "Falling back to simple build..."
    
    # Simple fallback build
    set -e
    mkdir -p build && cd build
    cmake -DCMAKE_BUILD_TYPE=Release ..
    make -j$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4)
    cd ..
    mkdir -p bin/release
    cp build/linch-mind-filesystem bin/release/
    echo "✅ Build completed: bin/release/linch-mind-filesystem"
else
    # Use shared build script
    exec "$SHARED_BUILD_SCRIPT" filesystem "$@"
fi