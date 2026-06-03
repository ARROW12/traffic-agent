#!/bin/bash

# JARVIS Traffic Agent - Run with GitHub Secrets
# This script fetches environment secrets from GitHub and starts the API server

set -e  # Exit on error

echo "🤖 JARVIS Traffic Agent - Loading secrets from GitHub..."
echo "=================================================="
echo ""

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) not found!"
    echo "Install it from: https://cli.github.com/"
    exit 1
fi

# Fetch secrets from GitHub
echo "📦 Fetching secrets from GitHub..."

export MAPS_API_KEY=$(gh secret view MAPS_API_KEY -R ARROW12/traffic-agent 2>/dev/null || echo "")
export TWILIO_ACCOUNT_SID=$(gh secret view TWILIO_ACCOUNT_SID -R ARROW12/traffic-agent 2>/dev/null || echo "")
export TWILIO_AUTH_TOKEN=$(gh secret view TWILIO_AUTH_TOKEN -R ARROW12/traffic-agent 2>/dev/null || echo "")
export YOUR_CELL_NUMBER=$(gh secret view YOUR_CELL_NUMBER -R ARROW12/traffic-agent 2>/dev/null || echo "")
export HOME_ADDRESS=$(gh secret view HOME_ADDRESS -R ARROW12/traffic-agent 2>/dev/null || echo "")
export OFFICE_ADDRESS=$(gh secret view OFFICE_ADDRESS -R ARROW12/traffic-agent 2>/dev/null || echo "")
export GITHUB_TOKEN=$(gh secret view GITHUB_TOKEN -R ARROW12/traffic-agent 2>/dev/null || echo "")
export GITHUB_REPO=$(gh secret view GITHUB_REPO -R ARROW12/traffic-agent 2>/dev/null || echo "ARROW12/traffic-agent")
export WORKFLOW_FILE=$(gh secret view WORKFLOW_FILE -R ARROW12/traffic-agent 2>/dev/null || echo "traffic-analysis.yml")

# Set OUTPUT_JSON for web interface
export OUTPUT_JSON=true

# Verify critical secrets are set
if [ -z "$MAPS_API_KEY" ]; then
    echo "❌ MAPS_API_KEY not found in GitHub secrets!"
    exit 1
fi

if [ -z "$TWILIO_ACCOUNT_SID" ]; then
    echo "❌ TWILIO_ACCOUNT_SID not found in GitHub secrets!"
    exit 1
fi

echo "✅ Secrets loaded successfully!"
echo ""
echo "Configuration:"
echo "  📍 MAPS_API_KEY: ${MAPS_API_KEY:0:10}..."
echo "  📱 TWILIO_ACCOUNT_SID: ${TWILIO_ACCOUNT_SID:0:10}..."
echo "  📍 HOME_ADDRESS: $HOME_ADDRESS"
echo "  📍 OFFICE_ADDRESS: $OFFICE_ADDRESS"
echo ""

# Start the API server
echo "🚀 Starting JARVIS Traffic Agent API Server..."
echo "=================================================="
echo ""

python3 api_server.py
