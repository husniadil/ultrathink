#!/bin/bash

# SessionStart hook for UltraThink
# This script sets up the environment for Claude Code on the web
# It only runs in remote (web) environments, not locally

# Exit early if not running in remote environment
if [ "$CLAUDE_CODE_REMOTE" != "true" ]; then
  echo "Skipping remote-only setup (running locally)"
  exit 0
fi

echo "Running SessionStart hook for remote environment..."

# Install dependencies using uv
echo "Installing dependencies with uv sync..."
if uv sync; then
  echo "Dependencies installed successfully"
else
  echo "Error: Failed to install dependencies"
  exit 1
fi

echo "Environment setup complete!"
exit 0
