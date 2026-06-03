# 🤖 JARVIS Traffic Agent - Complete Setup Guide

**All-in-one guide combining setup, features, troubleshooting, and GitHub Pages deployment.**

---

## Table of Contents

1. [Quick Start (5 minutes)](#quick-start)
2. [Full Setup Guide](#full-setup-guide)
3. [GitHub Pages Deployment (Step-by-Step)](#github-pages-deployment)
4. [API Backend Setup](#api-backend-setup)
5. [Features & Architecture](#features--architecture)
6. [Troubleshooting](#troubleshooting)
7. [Reference](#reference)

---

## Quick Start

### Prerequisites
- Python 3.10+
- Git
- Google Maps API key
- Twilio account with WhatsApp
- GitHub account

### In 5 Minutes:

```bash
# 1. Clone and navigate
cd traffic-agent
git clone https://github.com/ARROW12/traffic-agent.git
cd traffic-agent

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your credentials

# 4. Test the system
export SOURCE_LOCATION="Hitech City, Hyderabad"
export DESTINATION_LOCATION="Banjara Hills"
python traffic_agent.py
```

You should see the traffic analysis output on your terminal.

---

## Full Setup Guide

### Step 1: Prerequisites Setup

#### 1.1 Get Google Maps API Key
```
1. Go to: https://console.cloud.google.com
2. Create new project
3. Enable APIs:
   - Directions API
   - Places API
   - Distance Matrix API
   - Roads API
   - Time Zone API
4. Create API Key (Credentials → Create Credentials → API Key)
5. Save the key
```

#### 1.2 Get Twilio WhatsApp Credentials
```
1. Go to: https://www.twilio.com
2. Sign up or login
3. Get Account SID and Auth Token from Dashboard
4. Go to Phone Numbers → Manage → Get WhatsApp number
5. Save credentials
```

#### 1.3 Get GitHub Token
```
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes: repo, workflow, admin:repo_hook
4. Save the token (won't show again!)
```

### Step 2: Clone Repository

```bash
git clone https://github.com/ARROW12/traffic-agent.git
cd traffic-agent
```

### Step 3: Create Environment File

```bash
# Copy template
cp .env.example .env

# Edit .env with your values
nano .env
```

**Required values:**

```env
# Google Maps
MAPS_API_KEY=your_google_maps_key

# Twilio WhatsApp
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
YOUR_CELL_NUMBER=+91xxxxxxxxxx

# Default Locations (for testing)
HOME_ADDRESS=Hitech City, Hyderabad
OFFICE_ADDRESS=Banjara Hills

# GitHub (for Twilio handler)
GITHUB_TOKEN=your_github_token
GITHUB_REPO=ARROW12/traffic-agent
WORKFLOW_FILE=traffic-analysis.yml
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `requests` - HTTP client for APIs
- `twilio` - WhatsApp messaging
- `python-dotenv` - Environment configuration
- `flask` - API server
- `flask-cors` - Cross-origin requests

### Step 5: Test WhatsApp Interface

```bash
export SOURCE_LOCATION="Hitech City, Hyderabad"
export DESTINATION_LOCATION="Banjara Hills"
python traffic_agent.py
```

**Expected output:**
```
🤖 JARVIS FLIGHT PLAN SYSTEM — SYNC_02:30:15 PM
🗺️ Vector: Hitech City, Hyderabad ➔ Banjara Hills
⭐ Origin: 4.5 (1240 reviews)
...
```

### Step 6: Test API Server

```bash
# Terminal 1: Start API server
python api_server.py

# Terminal 2: Test the API
curl -X POST http://localhost:5000/api/traffic \
  -H "Content-Type: application/json" \
  -d '{"source":"Hitech City","destination":"Banjara Hills"}'
```

### Step 7: Test Website Locally

```bash
# 1. Edit docs/index.html
# Find line ~160: const response = await fetch('...'
# Change to: const response = await fetch('http://localhost:5000/api/traffic', {

# 2. Open in browser
# Mac: open docs/index.html
# Linux: xdg-open docs/index.html
# Windows: start docs/index.html

# 3. Enter locations and click "Analyze Traffic"
```

---

## GitHub Pages Deployment

### Step-by-Step Instructions

#### Step 1: Enable GitHub Pages

```
1. Go to your GitHub repo: github.com/ARROW12/traffic-agent
2. Click "Settings" (top right)
3. Left sidebar → Click "Pages"
4. Under "Build and deployment":
   - Source: Select "Deploy from a branch"
   - Branch: Select "main"
   - Folder: Select "/ (root)" (NOT /docs)
5. Click "Save"
```

⏳ **Wait 1-2 minutes** for GitHub to build and deploy

#### Step 2: Verify Deployment

```
1. Still in Settings → Pages
2. Look for: "Your site is live at https://USERNAME.github.io/traffic-agent"
3. Click the link to verify the website is live
```

✅ **Your website is now publicly available!**

#### Step 3: Connect to API Backend

Your website needs an API to fetch real traffic data. Choose one:

**Option A: Local Testing (for development)**
```bash
# Start Flask server
python api_server.py

# Edit docs/index.html line ~160
# Change: const response = await fetch('http://localhost:5000/api/traffic', {
```

**Option B: Deploy to Vercel (Recommended for production)**

```bash
# 1. Install Vercel CLI
npm install -g vercel

# 2. Login to Vercel
vercel login

# 3. Deploy
vercel

# 4. Get your API URL (example: https://traffic-agent.vercel.app/api/traffic)

# 5. Edit docs/index.html line ~160
# Change: const response = await fetch('https://traffic-agent.vercel.app/api/traffic', {

# 6. Commit and push changes
git add docs/index.html
git commit -m "Update API endpoint to Vercel"
git push origin main

# 7. GitHub Pages will auto-deploy within 1-2 minutes
```

**Option C: Deploy to Netlify**

```bash
# 1. Connect your GitHub repo to Netlify
# Visit: https://app.netlify.com

# 2. Create new site from Git
# Select: GitHub → Select traffic-agent repo

# 3. Set build command: python api_server.py
# Set publish directory: docs

# 4. Deploy

# 5. Get your API URL
# 6. Update docs/index.html with your Netlify URL
# 7. Commit and push
```

#### Step 4: Verify Website Works End-to-End

```
1. Open: https://USERNAME.github.io/traffic-agent
2. Enter test locations:
   - Source: "Hitech City, Hyderabad"
   - Destination: "Banjara Hills"
3. Click "Analyze Traffic"
4. Should see dashboard with:
   - ✅ Route information
   - ✅ Place ratings & reviews
   - ✅ Weather conditions
   - ✅ Air quality index
   - ✅ Car and bike route options
   - ✅ Direct Google Maps links
```

---

## API Backend Setup

### Option 1: Local Flask Server (Development)

```bash
# Start server
python api_server.py

# Server runs on: http://localhost:5000
# API endpoint: POST http://localhost:5000/api/traffic
# Payload: {"source": "...", "destination": "..."}
```

### Option 2: Vercel (Production - Recommended)

#### 2.1 Setup Vercel

```bash
npm install -g vercel
vercel login
cd traffic-agent
vercel
```

#### 2.2 Create `vercel.json`

```json
{
  "buildCommand": "pip install -r requirements.txt",
  "devCommand": "python api_server.py",
  "env": {
    "MAPS_API_KEY": "@maps_api_key",
    "TWILIO_ACCOUNT_SID": "@twilio_account_sid",
    "TWILIO_AUTH_TOKEN": "@twilio_auth_token",
    "YOUR_CELL_NUMBER": "@your_cell_number"
  }
}
```

#### 2.3 Deploy

```bash
vercel deploy --prod
```

Your API is now live and can be used in the website!

### Option 3: Netlify Functions

```bash
npm install -g netlify-cli
netlify login
netlify link  # Link to your GitHub repo
netlify deploy --prod
```

### Option 4: AWS Lambda

```
1. Package traffic_agent.py with dependencies
2. Create Lambda function
3. Use API Gateway to expose HTTP endpoint
4. Point website to API Gateway URL
```

---

## Features & Architecture

### What You Get

#### WhatsApp Interface
- ✅ 3-step conversation (source → destination → analysis)
- ✅ Real-time traffic updates
- ✅ Fuel cost estimates
- ✅ Multi-modal routing (car & bike)
- ✅ Weather and air quality
- ✅ Smart recommendations

#### Website Interface
- ✅ Beautiful responsive dashboard
- ✅ Real-time traffic search
- ✅ Place ratings & reviews
- ✅ Weather & AQI display
- ✅ Multi-modal routing
- ✅ Direct Google Maps navigation
- ✅ Mobile-optimized design

#### Data Points
For each route, you get:

```
📍 Location Data
- Place ratings and reviews
- Opening hours
- Formatted addresses

🌡️ Environmental Data
- Real-time temperature
- Weather conditions
- Air Quality Index (both locations)
- Timezone information

🚗 Route Information
- Distance in km
- Current ETA
- Traffic trends (+10min, +30min)
- Fuel cost estimates
- Smart recommendations

📊 Multi-Modal Support
- Car routing
- 2-wheeler routing
- Direct Google Maps links
```

### Architecture

```
User's Browser
    ↓
Website (docs/index.html)
    ↓
API Server (api_server.py)
    ↓
Google Maps APIs
  + Weather API
  + AQI API
    ↓
Traffic Analysis Engine (traffic_agent.py)
    ↓
Response → Website Dashboard
```

### APIs Used

| API | Purpose | Data |
|-----|---------|------|
| Directions API | Route planning | ETA, distance, traffic |
| Places API | Location details | Ratings, reviews, hours |
| Distance Matrix API | Multi-route comparison | Distance, duration |
| Roads API | Road metadata | Speed limits, lanes |
| Time Zone API | Location timezone | Timezone info |
| Open-Meteo | Weather data | Temperature, conditions |
| Air Quality API | AQI data | Air quality index |

---

## Troubleshooting

### "ModuleNotFoundError" when running Python

```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

### "API key error" or "Invalid credentials"

```bash
# Check your .env file exists
cat .env

# Verify credentials in .env match your accounts:
# - MAPS_API_KEY from Google Cloud Console
# - TWILIO_* from Twilio Dashboard
# - GITHUB_TOKEN from GitHub Settings

# Reload environment
source .env
```

### Website shows blank page

```bash
# 1. Check browser console (F12 → Console)
# 2. Verify API server is running:
python api_server.py

# 3. Test API directly:
curl -X POST http://localhost:5000/api/traffic \
  -H "Content-Type: application/json" \
  -d '{"source":"Hitech City","destination":"Banjara Hills"}'

# 4. Check docs/index.html line ~160 has correct API URL
```

### "No route found" error

```bash
# Try with more specific locations:
# ✅ "Hitech City, Hyderabad"
# ✅ "Times Square, New York"
# ✅ "Eiffel Tower, Paris"

# Not just: "Hitech City" or "Times Square"
```

### GitHub Pages not updating

```bash
# 1. Verify files are in /docs folder
ls -la docs/

# 2. Check GitHub Pages is enabled
# Settings → Pages → Should show "Your site is live at..."

# 3. Force rebuild:
git add .
git commit --allow-empty -m "Rebuild pages"
git push origin main

# 4. Wait 1-2 minutes and refresh
```

### WhatsApp message not received

```bash
# Reason 1: Account in trial mode (50 messages/day limit)
# Solution: Upgrade account → Add payment method

# Reason 2: Number not configured
# Solution: Verify YOUR_CELL_NUMBER in .env

# Reason 3: Rate limited
# Solution: Wait until next day or upgrade account
```

### CORS errors on website

```bash
# This means the API server isn't running with CORS
# Solution:

# 1. Verify api_server.py is running:
python api_server.py

# 2. Check it imports CORS:
grep -n "CORS" api_server.py

# 3. Test API with curl (no CORS needed):
curl -X POST http://localhost:5000/api/traffic \
  -H "Content-Type: application/json" \
  -d '{"source":"Test","destination":"Test"}'
```

---

## Reference

### Environment Variables

```env
# Required: Google Maps
MAPS_API_KEY=sk-xxxxxxxxxxxx

# Required: Twilio
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxx
YOUR_CELL_NUMBER=+91xxxxxxxxxx

# Optional: Default locations
HOME_ADDRESS=Hitech City, Hyderabad
OFFICE_ADDRESS=Banjara Hills

# Optional: GitHub (for workflow triggers)
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxx
GITHUB_REPO=ARROW12/traffic-agent
WORKFLOW_FILE=traffic-analysis.yml

# Optional: Output format
OUTPUT_JSON=false  # Set true for API server
```

### Command Reference

```bash
# Test traffic analysis
export SOURCE_LOCATION="Hitech City, Hyderabad"
export DESTINATION_LOCATION="Banjara Hills"
python traffic_agent.py

# Test JSON output
export OUTPUT_JSON=true
python traffic_agent.py

# Start API server
python api_server.py

# Test API endpoint
curl -X POST http://localhost:5000/api/traffic \
  -H "Content-Type: application/json" \
  -d '{"source":"Hitech City","destination":"Banjara Hills"}'

# Check Python syntax
python -m py_compile traffic_agent.py api_server.py

# View logs
tail -f traffic_agent.py

# Git commands
git status
git add .
git commit -m "Your message"
git push origin main
```

### File Structure

```
traffic-agent/
├── traffic_agent.py              # Core analysis engine
├── twilio_handler.js             # WhatsApp handler
├── api_server.py                 # Flask API server
├── requirements.txt              # Python dependencies
├── .env                          # Configuration (create from .env.example)
├── .env.example                  # Template
├── .github/
│   └── workflows/
│       └── traffic-analysis.yml  # GitHub Actions workflow
└── docs/
    ├── index.html               # Website (GitHub Pages)
    └── README.md                # Website setup
```

### URLs After Setup

```
GitHub Pages Website:
https://USERNAME.github.io/traffic-agent

Local API Server:
http://localhost:5000

API Endpoint (local):
POST http://localhost:5000/api/traffic
Request: {"source": "...", "destination": "..."}

API Health Check:
GET http://localhost:5000/health
```

---

## Verification Checklist

- [ ] Prerequisites installed (Python 3.10+, Git)
- [ ] API keys obtained (Google Maps, Twilio, GitHub)
- [ ] Repository cloned
- [ ] `.env` file created and configured
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Traffic analysis works locally (`python traffic_agent.py`)
- [ ] API server starts (`python api_server.py`)
- [ ] GitHub Pages enabled in Settings
- [ ] Website accessible at GitHub Pages URL
- [ ] API backend deployed (Flask/Vercel/Netlify)
- [ ] Website connected to API
- [ ] End-to-end test completed

---

## What's Next?

### Immediate
1. ✅ Complete setup from this guide
2. ✅ Test locally (both WhatsApp and website)
3. ✅ Deploy to GitHub Pages

### Short-term
- Monitor usage and error logs
- Optimize API calls if needed
- Upgrade Twilio account for production

### Long-term Enhancements
- Add route history tracking
- Implement saved favorite routes
- Add incident alerts
- Include public transit options
- Add EV charging station locator
- Create mobile app

---

## Support & Resources

**GitHub Issues**: https://github.com/ARROW12/traffic-agent/issues

**Documentation**:
- See individual files for detailed information
- Each function in the code is documented

**Tutorials**:
- Google Maps API: https://developers.google.com/maps
- Twilio WhatsApp: https://www.twilio.com/docs/whatsapp
- GitHub Pages: https://docs.github.com/en/pages

---

## License & Credits

**Project**: JARVIS Traffic Agent
**Author**: Tejas
**Last Updated**: June 2026

Built with ❤️ using Python, Flask, Google APIs, and GitHub Pages.

---

**Ready to deploy? Start at "Step 1: Prerequisites Setup" above! 🚀**
