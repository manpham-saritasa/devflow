#!/bin/bash
# Sync .ai/rules/core.md to your AI tool's root file
# Usage: ./sync.sh zed | cursor | copilot | claude | gemini | windsurf | codeium | aider | jetbrains | all
set -e

TOOL="${1:-all}"
SOURCE=".ai/rules/core.md"

declare -A TOOLS
TOOLS[zed]=".rules:symlink"
TOOLS[claude]="CLAUDE.md:symlink"
TOOLS[gemini]="GEMINI.md:symlink"
TOOLS[windsurf]=".windsurfrules:symlink"
TOOLS[codeium]=".codeiumrules:symlink"
TOOLS[aider]="CONVENTIONS.md:symlink"
TOOLS[cursor]=".cursor/rules/main.mdc:copy"
TOOLS[copilot]=".github/copilot-instructions.md:copy"
TOOLS[jetbrains]=".rules:symlink"

sync_one() {
    local name="$1"
    local cfg="$2"
    local path="${cfg%:*}"
    local type="${cfg#*:}"
    local dir
    dir=$(dirname "$path")
    if [ -n "$dir" ] && [ "$dir" != "." ]; then
        mkdir -p "$dir"
    fi
    if [ "$type" = "symlink" ]; then
        rm -f "$path"
        ln -s "$SOURCE" "$path"
        echo "  $name -> $path (symlink)"
    else
        cp "$SOURCE" "$path"
        echo "  $name -> $path (copy)"
    fi
}

if [ "$TOOL" = "all" ]; then
    echo "Syncing all tools..."
    for name in "${!TOOLS[@]}"; do
        sync_one "$name" "${TOOLS[$name]}"
    done
elif [ -n "${TOOLS[$TOOL]}" ]; then
    echo "Syncing $TOOL..."
    sync_one "$TOOL" "${TOOLS[$TOOL]}"
else
    echo "Unknown tool: $TOOL"
    echo "Usage: sync.sh [zed|cursor|copilot|claude|gemini|windsurf|codeium|aider|jetbrains|all]"
    exit 1
fi

echo "Done."
