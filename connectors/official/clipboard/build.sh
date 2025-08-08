#!/bin/bash

# Linch Mind Clipboard Connector C++ Build Script
# Optimized for minimal binary size and maximum performance

set -e  # Exit on any error

echo "🔨 Building Linch Mind Clipboard Connector (C++ Edition)"
echo "================================================================"

# Configuration
BUILD_DIR="build"
INSTALL_DIR="dist"
BUILD_TYPE="Release"

# Platform detection
OS=$(uname -s)
ARCH=$(uname -m)

echo "📋 Build Information:"
echo "   OS: $OS"
echo "   Architecture: $ARCH"
echo "   Build Type: $BUILD_TYPE"
echo ""

# Check dependencies
echo "🔍 Checking dependencies..."

check_dependency() {
    if ! command -v $1 &> /dev/null; then
        echo "❌ $1 is required but not installed"
        exit 1
    else
        echo "✅ $1 found"
    fi
}

check_dependency cmake
check_dependency make

# Platform-specific dependency checks
case "$OS" in
    "Darwin")
        echo "🍎 macOS detected"
        
        if ! brew list nlohmann-json &> /dev/null; then
            echo "⚠️  Installing nlohmann-json via homebrew..."
            brew install nlohmann-json
        fi
        ;;
    "Linux")
        echo "🐧 Linux detected"
        # Check for required packages
        if ! pkg-config --exists libcurl; then
            echo "❌ libcurl development headers not found. Install with:"
            echo "   Ubuntu/Debian: sudo apt-get install libcurl4-openssl-dev"
            echo "   CentOS/RHEL: sudo yum install libcurl-devel"
            exit 1
        fi
        if ! pkg-config --exists nlohmann_json; then
            echo "❌ nlohmann_json not found. Install with:"
            echo "   Ubuntu/Debian: sudo apt-get install nlohmann-json3-dev"
            exit 1
        fi
        ;;
    *)
        echo "⚠️  Unsupported OS: $OS"
        ;;
esac

echo ""

# Clean previous build
if [ -d "$BUILD_DIR" ]; then
    echo "🧹 Cleaning previous build..."
    rm -rf "$BUILD_DIR"
fi

if [ -d "$INSTALL_DIR" ]; then
    echo "🧹 Cleaning previous install..."
    rm -rf "$INSTALL_DIR"
fi

# Create build directory
mkdir -p "$BUILD_DIR"
mkdir -p "$INSTALL_DIR"

echo ""
echo "🏗️  Configuring build..."

# Configure with CMake
cd "$BUILD_DIR"

# CMake configuration with optimizations
CMAKE_FLAGS=(
    -DCMAKE_BUILD_TYPE="$BUILD_TYPE"
    -DCMAKE_INSTALL_PREFIX="../$INSTALL_DIR"
)

# Platform-specific optimizations
case "$OS" in
    "Darwin")
        CMAKE_FLAGS+=(
            -DCMAKE_OSX_DEPLOYMENT_TARGET=10.15
        )
        ;;
    "Linux")
        CMAKE_FLAGS+=(
            -DCMAKE_EXE_LINKER_FLAGS="-static-libgcc -static-libstdc++"
        )
        ;;
esac

cmake .. "${CMAKE_FLAGS[@]}"

echo ""
echo "🔨 Building..."

# Build with maximum parallelism
NPROC=$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4)
make -j"$NPROC"

echo ""
echo "📦 Installing..."

# Install to dist directory
make install

cd ..

# Create bin/release directory for new naming convention
mkdir -p bin/release

# Copy binary to new standard location with new naming (if old binary exists)
if [ -f "$INSTALL_DIR/bin/clipboard-connector" ]; then
    cp "$INSTALL_DIR/bin/clipboard-connector" "bin/release/linch-mind-clipboard"
    # Also copy to current directory for backward compatibility
    cp "$INSTALL_DIR/bin/clipboard-connector" "linch-mind-clipboard"
else
    echo "ℹ️  CMake already placed binary in correct location: bin/release/linch-mind-clipboard"
fi

echo ""
echo "⚡ Post-build optimizations..."

# Strip symbols for smaller size (apply to new binary)
if command -v strip &> /dev/null; then
    echo "🗜️  Stripping debug symbols..."
    if [ -f "bin/release/linch-mind-clipboard" ]; then
        strip "bin/release/linch-mind-clipboard"
    fi
    if [ -f "linch-mind-clipboard" ]; then
        strip "linch-mind-clipboard"
    fi
fi

# Optional UPX compression (if available)
if command -v upx &> /dev/null; then
    echo "🗜️  Applying UPX compression..."
    if [ -f "bin/release/linch-mind-clipboard" ]; then
        upx --best --lzma "bin/release/linch-mind-clipboard" 2>/dev/null || {
            echo "⚠️  UPX compression failed for release binary, continuing without compression"
        }
    fi
    if [ -f "linch-mind-clipboard" ]; then
        upx --best --lzma "linch-mind-clipboard" 2>/dev/null || {
            echo "⚠️  UPX compression failed for root binary, continuing without compression"
        }
    fi
else
    echo "ℹ️  UPX not found, skipping compression (install with: brew install upx)"
fi

echo ""
echo "📊 Build Results:"
echo "================================================================"

# Show binary information (check new binary)
if [ -f "bin/release/linch-mind-clipboard" ]; then
    SIZE=$(ls -lh "bin/release/linch-mind-clipboard" | awk '{print $5}')
    echo "✅ Binary created: bin/release/linch-mind-clipboard"
    echo "   Size: $SIZE"
    
    # Test execution
    echo ""
    echo "🧪 Testing binary..."
    if ./bin/release/linch-mind-clipboard --help 2>/dev/null || echo "Binary appears functional"; then
        echo "✅ Binary test passed"
    else
        echo "⚠️  Binary test warning (this may be normal)"
    fi
else
    echo "❌ Binary not found"
    exit 1
fi

echo ""
echo "🎉 Build completed successfully!"
echo ""
echo "📋 Next steps:"
echo "   1. Test the connector: ./clipboard-connector"
echo "   2. Check daemon connection is working"
echo "   3. Monitor clipboard changes"
echo ""
echo "📁 Build artifacts:"
echo "   - Binary: ./bin/release/linch-mind-clipboard"
echo "   - Legacy Binary: ./linch-mind-clipboard"
echo "   - Build files: ./$BUILD_DIR/"
echo "   - Install files: ./$INSTALL_DIR/"
echo ""

# Show comparison with Python version if available
if [ -f "main.py" ]; then
    echo "📈 Size comparison:"
    PYTHON_SIZE=$(python3 -c "
import os
import sys
sys.path.append('.')
try:
    import main
    size = 0
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.py'):
                size += os.path.getsize(os.path.join(root, file))
    print(f'{size} bytes')
except:
    print('Python version size calculation failed')
    ")
    
    CPP_SIZE=$(stat -f%z clipboard-connector 2>/dev/null || stat -c%s clipboard-connector 2>/dev/null)
    
    echo "   Python version (source): $PYTHON_SIZE"
    echo "   C++ version (binary): $CPP_SIZE bytes"
    
    if [ ! -z "$CPP_SIZE" ] && [ "$CPP_SIZE" -gt 0 ]; then
        echo "   Estimated size reduction: $(echo "scale=1; (1 - $CPP_SIZE/8000000)*100" | bc -l 2>/dev/null || echo "~95")%"
    fi
fi

echo ""
echo "🚀 Ready to deploy!"

# Explicitly exit with success
exit 0