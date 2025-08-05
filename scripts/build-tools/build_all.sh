#!/bin/bash

# Build all changed connectors
# Usage: ./build_all.sh <connector_list>

set -e

CONNECTOR_LIST="$1"
OUTPUT_DIR="release/dist"

if [ -z "$CONNECTOR_LIST" ]; then
    echo "Usage: $0 '<connector1> <connector2> ...'"
    echo "Example: $0 'official/clipboard official/filesystem'"
    exit 1
fi

echo "🚀 Building connectors: $CONNECTOR_LIST"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Build each connector
success_count=0
fail_count=0
failed_connectors=""

for connector_path in $CONNECTOR_LIST; do
    echo ""
    echo "=" "Building $connector_path" "="
    
    if ../scripts/build-tools/build_connector.sh "$connector_path" "$OUTPUT_DIR"; then
        echo "✅ Successfully built $connector_path"
        success_count=$((success_count + 1))
    else
        echo "❌ Failed to build $connector_path"
        fail_count=$((fail_count + 1))
        failed_connectors="$failed_connectors $connector_path"
    fi
done

echo ""
echo "📊 Build Summary:"
echo "   ✅ Successful: $success_count"
echo "   ❌ Failed: $fail_count"

if [ $fail_count -gt 0 ]; then
    echo "   Failed connectors: $failed_connectors"
fi

# List built artifacts
echo ""
echo "📦 Built artifacts:"
if [ -d "$OUTPUT_DIR" ] && [ "$(ls -A "$OUTPUT_DIR" 2>/dev/null)" ]; then
    ls -lh "$OUTPUT_DIR"/
else
    echo "No artifacts found"
fi

# Exit with error if any builds failed
if [ $fail_count -gt 0 ]; then
    exit 1
fi

echo ""
echo "🎉 All builds completed successfully!"

echo "DEBUG: About to exit with 0"
exit 0