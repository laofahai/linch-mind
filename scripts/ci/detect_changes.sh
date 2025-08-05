#!/bin/bash

# Detect changed connectors and bump versions
# Usage: ./detect_changes.sh

set -e

echo "🔍 Detecting changed connectors..."

# Detect changes in connectors
changed_files=$(git diff --name-only HEAD~1 HEAD | grep -E '^connectors/(official|community)/' || true)

if [ -z "$changed_files" ]; then
    echo "No connector changes detected"
    if [ -n "$GITHUB_OUTPUT" ]; then
        echo "changed_connectors=" >> $GITHUB_OUTPUT
    fi
    exit 0
fi

echo "📝 Changed files:"
echo "$changed_files"

# Extract unique connector paths
changed_connectors=""
for file in $changed_files; do
    if [[ $file =~ ^connectors/(official|community)/([^/]+)/ ]]; then
        connector_type="${BASH_REMATCH[1]}"
        connector_name="${BASH_REMATCH[2]}"
        connector_path="$connector_type/$connector_name"
        changed_connectors="$changed_connectors $connector_path"
    fi
done

# Remove duplicates and sort
changed_connectors=$(echo "$changed_connectors" | tr ' ' '\n' | sort -u | tr '\n' ' ' | xargs)

echo "🔗 Changed connectors: $changed_connectors"

# Output for GitHub Actions
if [ -n "$GITHUB_OUTPUT" ]; then
    echo "changed_connectors=$changed_connectors" >> $GITHUB_OUTPUT
fi

# Also output to stdout for script chaining
echo "$changed_connectors"

# Bump versions for changed connectors
if [ -n "$changed_connectors" ]; then
    echo "🔢 Bumping connector versions..."
    for connector_path in $changed_connectors; do
        if [ -f "$connector_path/connector.json" ]; then
            echo "   Updating $connector_path"
            python3 scripts/version_manager.py "$connector_path/connector.json" --bump patch
        else
            echo "   ⚠️ No connector.json found in $connector_path"
        fi
    done
    echo "✅ Version bumping completed"
fi

echo "Changed connectors: $changed_connectors"