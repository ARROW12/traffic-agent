# 🚀 Quick Start Guide - 5 Minute Setup

This is the fastest way to get the JARVIS Traffic Agent running with both WhatsApp and website interfaces.

## Prerequisites

- ✅ Python 3.10+
- ✅ GitHub account with repo access
- ✅ Google Maps API key
- ✅ Twilio account with WhatsApp
- ✅ GitHub token (for Twilio handler)

## Step 1: Install Dependencies (1 minute)

```bash
cd traffic-agent
pip install -r requirements.txt
```

## Step 2: Configure Environment (2 minutes)

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
# Edit .env with your API keys
```

Required values:
- `MAPS_API_KEY` - From Google Cloud Console
- `TWILIO_ACCOUNT_SID` - From Twilio Dashboard
- `TWILIO_AUTH_TOKEN` - From Twilio Dashboard
- `YOUR_CELL_NUMBER` - Your WhatsApp number (e.g., +91999999999)
- `GITHUB_TOKEN` - From GitHub Settings
- `HOME_ADDRESS` - Default starting location
- `OFFICE_ADDRESS` - Default destination

## Step 3: Test WhatsApp Interface (1 minute)

```bash
# Set test locations
export SOURCE_LOCATION="Hitech City, Hyderabad"
export DESTINATION_LOCATION="Banjara Hills"
export OUTPUT_JSON=false

# Run traffic analysis
python traffic_agent.py

# Check output - should show formatted traffic brief
```

## Step 4: Run API Server (1 minute)

```bash
# In a new terminal, start the Flask API
python api_server.py

# You should see:
# 🤖 JARVIS Traffic Agent API Server
# ✅ Server starting on http://localhost:5000
```

## Step 5: Test Website (Optional)

1. Open `docs/index.html` in a text editor
2. Find line ~160: `const response = await fetch(...`
3. Update to: `const response = await fetch('http://localhost:5000/api/traffic', {`
4. Save the file
5. Open `docs/index.html` in your browser
6. You should see the interactive dashboard!

---

## What You Can Do Now

### From WhatsApp
```
Send: .
Reply: Hitech City, Hyderabad
Reply: Banjara Hills
→ Get real-time traffic analysis on WhatsApp
```

### From Website
```
1. Visit http://localhost:5000 (if running locally)
   OR https://ARROW12.github.io/traffic-agent (live)
2. Enter source and destination
3. Click "Analyze Traffic"
4. See beautiful dashboard with ratings, weather, and routes
```

---

## Deployment Options

### Option A: WhatsApp Only (Already Works!)
- Just send "." to WhatsApp
- System works with Twilio in trial mode (50 msgs/day)
- Upgrade account to increase limit

### Option B: Website + Local API
- Run `python api_server.py`
- Update website fetch URL to `http://localhost:5000/api/traffic`
- Open `docs/index.html` in browser
- Great for development!

### Option C: Website + Production API
1. Choose platform: Vercel, Netlify, AWS Lambda, or Heroku
2. Follow [WEBSITE_API_SETUP.md](WEBSITE_API_SETUP.md) for your platform
3. Deploy the API
4. Update website fetch URL to your API endpoint
5. Website is now live at GitHub Pages!

---

## Troubleshooting

### "API key error"
- Check your `.env` file
- Verify keys in Google Cloud Console / Twilio Dashboard

### "No route found"
- Try with famous landmarks: "Times Square, New York"
- Check if location names are correct

### "WhatsApp message not received"
- Account in trial mode (50 msgs/day limit)?
- Upgrade: Settings → Billing
- Or wait until next day

### "Website shows errors"
- Check browser console (F12)
- Verify API server is running
- Check fetch URL in index.html

---

## Commands Reference

```bash
# Test traffic analysis (WhatsApp format)
export SOURCE_LOCATION="Hitech City"
export DESTINATION_LOCATION="Banjara Hills"
python traffic_agent.py

# Test traffic analysis (JSON format for web)
export OUTPUT_JSON=true
python traffic_agent.py

# Start API server
python api_server.py

# Check syntax errors
python -m py_compile traffic_agent.py api_server.py

# View help
python api_server.py --help
```

---

## GitHub Pages Deployment

To make the website publicly available:

1. Go to GitHub Repo → Settings → Pages
2. Source: Deploy from branch → main
3. Folder: /docs
4. Click Save
5. Wait 1-2 minutes
6. Your website is live at: `https://ARROW12.github.io/traffic-agent`

---

## What's Next?

✅ **Done**: Core system working
✅ **Done**: Website created
✅ **Done**: API server ready

**Next**: Choose your deployment option and go live!

See [ENHANCEMENT_SUMMARY.md](ENHANCEMENT_SUMMARY.md) for complete feature list.

---

**Happy traffic analyzing! 🚗🚏🎉**
