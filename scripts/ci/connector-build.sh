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
cd ..
./scripts/build/build_all.sh "$CHANGED_CONNECTORS"

# Step 3: Generate registry
echo ""
echo "Step 3: Generating registry..."
cd connectors && python3 scripts/registry_generator.py --output release/registry.json --format

echo ""
echo "🎉 Connector build pipeline completed successfully!"
echo "📦 Artifacts available in: connectors/release/dist/"