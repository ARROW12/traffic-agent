#!/bin/bash

# JARVIS Traffic Agent - Easy Setup Wizard
# This script helps you set up the API server with your GitHub secrets

echo "🤖 JARVIS Traffic Agent - Setup Wizard"
echo "======================================"
echo ""
echo "This script will help you configure the API server."
echo "You have two options:"
echo ""
echo "Option 1: Use GitHub CLI (recommended)"
echo "  - Install: brew install gh"
echo "  - Run: ./run-with-secrets.sh"
echo ""
echo "Option 2: Enter secrets manually (this script)"
echo "  - Continue below"
echo ""

# Check if .env already exists
if [ -f ".env" ]; then
    echo "✅ .env file already exists!"
    echo ""
    read -p "Do you want to update it? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Using existing .env file..."
        exec python3 api_server.py
        exit 0
    fi
fi

echo ""
echo "Enter your configuration values:"
echo "(Leave blank to use defaults)"
echo ""

read -p "📍 Google Maps API Key: " MAPS_API_KEY
read -p "📱 Twilio Account SID: " TWILIO_ACCOUNT_SID
read -p "🔑 Twilio Auth Token: " TWILIO_AUTH_TOKEN
read -p "📱 Your WhatsApp Number (e.g., +91999999999): " YOUR_CELL_NUMBER
read -p "🏠 Home Address (default: Hitech City, Hyderabad): " HOME_ADDRESS
HOME_ADDRESS=${HOME_ADDRESS:-Hitech City, Hyderabad}
read -p "🏢 Office Address (default: Banjara Hills): " OFFICE_ADDRESS
OFFICE_ADDRESS=${OFFICE_ADDRESS:-Banjara Hills}
read -p "🔑 GitHub Token: " GITHUB_TOKEN
read -p "📦 GitHub Repo (default: ARROW12/traffic-agent): " GITHUB_REPO
GITHUB_REPO=${GITHUB_REPO:-ARROW12/traffic-agent}
read -p "⚙️ Workflow File (default: traffic-analysis.yml): " WORKFLOW_FILE
WORKFLOW_FILE=${WORKFLOW_FILE:-traffic-analysis.yml}

# Create .env file
cat > .env << EOF
# Google Maps
MAPS_API_KEY=$MAPS_API_KEY

# Twilio WhatsApp
TWILIO_ACCOUNT_SID=$TWILIO_ACCOUNT_SID
TWILIO_AUTH_TOKEN=$TWILIO_AUTH_TOKEN
YOUR_CELL_NUMBER=$YOUR_CELL_NUMBER

# Default Locations
HOME_ADDRESS=$HOME_ADDRESS
OFFICE_ADDRESS=$OFFICE_ADDRESS

# GitHub (for workflow triggers)
GITHUB_TOKEN=$GITHUB_TOKEN
GITHUB_REPO=$GITHUB_REPO
WORKFLOW_FILE=$WORKFLOW_FILE

# Web interface
OUTPUT_JSON=true
EOF

echo ""
echo "✅ Configuration saved to .env"
echo ""
echo "🚀 Starting JARVIS Traffic Agent API Server..."
echo "================================================"
echo ""
echo "✨ Server will start on http://localhost:5000"
echo ""

python3 api_server.py
