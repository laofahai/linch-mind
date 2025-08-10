#!/bin/bash

# Universal C++ Connector Build Script for Linch Mind
# Usage: ./build_connector.sh [connector_name] [options]
# Example: ./build_connector.sh clipboard --release

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_color() {
    color=$1
    shift
    echo -e "${color}$@${NC}"
}

# Get connector name from argument or current directory
if [ -n "$1" ] && [ "$1" != "--release" ] && [ "$1" != "--debug" ]; then
    CONNECTOR_NAME="$1"
    shift
else
    # Try to determine from current directory
    CURRENT_DIR=$(basename $(pwd))
    if [ -f "connector.json" ]; then
        CONNECTOR_NAME=$CURRENT_DIR
    else
        print_color $RED "❌ Error: No connector name provided and couldn't determine from current directory"
        print_color $YELLOW "Usage: $0 [connector_name] [--release|--debug]"
        exit 1
    fi
fi

# Build type (default: Release)
BUILD_TYPE="Release"
if [ "$1" == "--debug" ]; then
    BUILD_TYPE="Debug"
fi

print_color $BLUE "🔨 Building Linch Mind Connector: $CONNECTOR_NAME"
print_color $BLUE "================================================================"

# Platform detection
OS=$(uname -s)
ARCH=$(uname -m)

print_color $GREEN "📋 Build Information:"
echo "   Connector: $CONNECTOR_NAME"
echo "   OS: $OS"
echo "   Architecture: $ARCH"
echo "   Build Type: $BUILD_TYPE"
echo ""

# Check dependencies
print_color $GREEN "🔍 Checking dependencies..."

check_dependency() {
    if ! command -v $1 &> /dev/null; then
        print_color $RED "❌ $1 is required but not installed"
        exit 1
    else
        print_color $GREEN "✅ $1 found"
    fi
}

check_dependency cmake
check_dependency make

# Platform-specific dependency checks
case "$OS" in
    "Darwin")
        print_color $YELLOW "🍎 macOS detected"
        
        # Check for nlohmann-json
        if ! brew list nlohmann-json &> /dev/null 2>&1; then
            print_color $YELLOW "⚠️  Installing nlohmann-json via homebrew..."
            brew install nlohmann-json
        fi
        ;;
    "Linux")
        print_color $YELLOW "🐧 Linux detected"
        
        # Check for nlohmann-json
        if ! pkg-config --exists nlohmann_json 2>/dev/null; then
            print_color $YELLOW "⚠️  nlohmann_json may not be installed"
            print_color $YELLOW "   Install with: sudo apt-get install nlohmann-json3-dev"
        fi
        ;;
    "MINGW"*|"MSYS"*)
        print_color $YELLOW "🪟 Windows detected"
        ;;
    *)
        print_color $YELLOW "⚠️  Unknown OS: $OS"
        ;;
esac

echo ""

# Build directory
BUILD_DIR="build"

# Clean previous build if requested
if [ "$2" == "--clean" ] || [ "$3" == "--clean" ]; then
    print_color $YELLOW "🧹 Cleaning previous build..."
    rm -rf "$BUILD_DIR"
fi

# Create build directory
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

print_color $GREEN "🏗️  Configuring build with CMake..."

# CMake configuration
CMAKE_FLAGS=(
    -DCMAKE_BUILD_TYPE="$BUILD_TYPE"
)

# Platform-specific optimizations
case "$OS" in
    "Darwin")
        CMAKE_FLAGS+=(
            -DCMAKE_OSX_DEPLOYMENT_TARGET=10.15
        )
        ;;
    "Linux")
        # Static linking for better portability
        CMAKE_FLAGS+=(
            -DCMAKE_EXE_LINKER_FLAGS="-static-libgcc -static-libstdc++"
        )
        ;;
esac

cmake .. "${CMAKE_FLAGS[@]}"

echo ""
print_color $GREEN "🔧 Building..."

# Build with maximum parallelism
NPROC=$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4)
make -j"$NPROC"

# Determine output binary name
BINARY_NAME="linch-mind-${CONNECTOR_NAME}"
if [[ "$OS" == "MINGW"* ]] || [[ "$OS" == "MSYS"* ]]; then
    BINARY_NAME="${BINARY_NAME}.exe"
fi

# Create output directories
print_color $GREEN "📦 Creating output directories..."
cd ..
mkdir -p "bin/release"
mkdir -p "bin/debug"

# Copy binary to appropriate directory
if [ "$BUILD_TYPE" == "Release" ]; then
    OUTPUT_DIR="bin/release"
else
    OUTPUT_DIR="bin/debug"
fi

# Copy the binary
if [ -f "$BUILD_DIR/$BINARY_NAME" ]; then
    cp "$BUILD_DIR/$BINARY_NAME" "$OUTPUT_DIR/"
    print_color $GREEN "✅ Binary created: $OUTPUT_DIR/$BINARY_NAME"
else
    # Try alternative naming patterns
    if [ -f "$BUILD_DIR/linch-mind-${CONNECTOR_NAME}" ]; then
        cp "$BUILD_DIR/linch-mind-${CONNECTOR_NAME}" "$OUTPUT_DIR/$BINARY_NAME"
        print_color $GREEN "✅ Binary created: $OUTPUT_DIR/$BINARY_NAME"
    else
        print_color $RED "❌ Binary not found after build"
        exit 1
    fi
fi

# Optional: Strip symbols for release builds
if [ "$BUILD_TYPE" == "Release" ] && command -v strip &> /dev/null; then
    print_color $YELLOW "🗜️  Stripping debug symbols..."
    strip "$OUTPUT_DIR/$BINARY_NAME"
fi

# Optional: UPX compression if available
if [ "$BUILD_TYPE" == "Release" ] && command -v upx &> /dev/null; then
    print_color $YELLOW "🗜️  Attempting UPX compression..."
    upx --best --lzma "$OUTPUT_DIR/$BINARY_NAME" 2>/dev/null || {
        print_color $YELLOW "⚠️  UPX compression failed, continuing without compression"
    }
fi

echo ""
print_color $GREEN "📊 Build Results:"
print_color $GREEN "================================================================"

# Show binary information
if [ -f "$OUTPUT_DIR/$BINARY_NAME" ]; then
    SIZE=$(ls -lh "$OUTPUT_DIR/$BINARY_NAME" | awk '{print $5}')
    print_color $GREEN "✅ Binary: $OUTPUT_DIR/$BINARY_NAME"
    print_color $GREEN "   Size: $SIZE"
    
    # Show file type info if available
    if command -v file >/dev/null 2>&1; then
        FILE_INFO=$(file "$OUTPUT_DIR/$BINARY_NAME" | cut -d: -f2)
        print_color $GREEN "   Type:$FILE_INFO"
    fi
fi

echo ""
print_color $GREEN "🎉 Build completed successfully!"
echo ""
print_color $BLUE "📋 Next steps:"
echo "   1. Test the connector: ./$OUTPUT_DIR/$BINARY_NAME"
echo "   2. Verify daemon connection"
echo "   3. Check connector.json configuration"
echo ""

exit 0