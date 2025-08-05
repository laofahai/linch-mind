#!/bin/bash

# Main CI script for connector building
# This is the entry point called by GitHub Actions

set -e

echo "🚀 Starting Linch Mind Connector Build Pipeline"
echo "================================================"

# Change to project root
cd "$(dirname "$0")/../.."

# Step 1: Detect changes and bump versions
echo "Step 1: Detecting changes..."
cd connectors
CHANGED_CONNECTORS=$(../scripts/ci/detect_changes.sh)

# Also set GitHub Actions output if running in CI
if [ -n "$GITHUB_OUTPUT" ] && [ -n "$CHANGED_CONNECTORS" ]; then
    echo "changed_connectors=$CHANGED_CONNECTORS" >> $GITHUB_OUTPUT
fi

if [ -z "$CHANGED_CONNECTORS" ]; then
    echo "✅ No connector changes detected, exiting"
    exit 0
fi

echo "📦 Will build connectors: $CHANGED_CONNECTORS"

# Step 2: Build connectors
echo ""
echo "Step 2: Building connectors..."
echo "🔍 DEBUG: About to build connectors: $CHANGED_CONNECTORS"
echo "🔍 DEBUG: Current directory: $(pwd)"
echo "🔍 DEBUG: Checking build script..."
ls -la ../scripts/build/build_all.sh
# Stay in connectors directory for build_all.sh
../scripts/build/build_all.sh "$CHANGED_CONNECTORS"
BUILD_EXIT_CODE=$?
echo "🔍 DEBUG: Build script exit code: $BUILD_EXIT_CODE"

# Check if build succeeded before continuing
if [ $BUILD_EXIT_CODE -ne 0 ]; then
    echo "❌ Build failed with exit code: $BUILD_EXIT_CODE"
    exit $BUILD_EXIT_CODE
fi

# Step 3: Generate registry
echo ""
echo "Step 3: Generating registry..."
echo "🔍 DEBUG: About to generate registry..."
# Already in connectors directory
python3 scripts/registry_generator.py --output release/registry.json --format
REGISTRY_EXIT_CODE=$?
echo "🔍 DEBUG: Registry generation exit code: $REGISTRY_EXIT_CODE"

if [ $REGISTRY_EXIT_CODE -ne 0 ]; then
    echo "❌ Registry generation failed with exit code: $REGISTRY_EXIT_CODE"
    exit $REGISTRY_EXIT_CODE
fi

echo ""
echo "🎉 Connector build pipeline completed successfully!"
echo "📦 Artifacts available in: connectors/release/dist/"