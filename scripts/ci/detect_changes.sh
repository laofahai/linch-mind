#!/bin/bash

# Detect changed connectors and bump versions
# Usage: ./detect_changes.sh

set -e

echo "🔍 Detecting changed connectors..." >&2

# Detect changes in connectors
changed_files=$(git diff --name-only HEAD~1 HEAD | grep -E '^connectors/(official|community)/' || true)

if [ -z "$changed_files" ]; then
    echo "No connector changes detected" >&2
    if [ -n "$GITHUB_OUTPUT" ]; then
        echo "changed_connectors=" >> $GITHUB_OUTPUT
    fi
    exit 0
fi

echo "📝 Changed files:" >&2
echo "$changed_files" >&2

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

echo "🔗 Changed connectors: $changed_connectors" >&2

# Output for GitHub Actions
if [ -n "$GITHUB_OUTPUT" ]; then
    echo "changed_connectors=$changed_connectors" >> $GITHUB_OUTPUT
fi

# Output to stdout for script chaining (clean output, no decorations)
printf "%s" "$changed_connectors"

# Bump versions for changed connectors
if [ -n "$changed_connectors" ]; then
    echo "🔢 Bumping connector versions..." >&2
    for connector_path in $changed_connectors; do
        if [ -f "$connector_path/connector.json" ]; then
            echo "   Updating $connector_path" >&2
            python3 scripts/version_manager.py "$connector_path/connector.json" --bump patch
        else
            echo "   ⚠️ No connector.json found in $connector_path" >&2
        fi
    done
    echo "✅ Version bumping completed" >&2
fi

echo "Changed connectors: $changed_connectors" >&2