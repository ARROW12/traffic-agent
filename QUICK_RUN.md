# 🚀 Quick Start - Run API Server

Two easy ways to start the JARVIS Traffic Agent API server:

## Option 1: Interactive Setup (Easiest) ✨

```bash
cd traffic-agent
./setup.sh
```

**What it does:**
1. Checks if `.env` exists
2. If not, asks you to enter your credentials interactively
3. Creates `.env` file automatically
4. Starts the API server

**Interactive prompts:**
```
📍 Google Maps API Key: [paste your key]
📱 Twilio Account SID: [paste your SID]
🔑 Twilio Auth Token: [paste your token]
📱 Your WhatsApp Number: +91999999999
🏠 Home Address: Hitech City, Hyderabad
🏢 Office Address: Banjara Hills
🔑 GitHub Token: [optional]
📦 GitHub Repo: ARROW12/traffic-agent
⚙️ Workflow File: traffic-analysis.yml
```

✅ Server starts automatically!

---

## Option 2: GitHub CLI (Most Secure) 🔐

If you want to use GitHub secrets directly:

### Step 1: Install GitHub CLI

**Mac:**
```bash
brew install gh
```

**Linux/Windows:** 
Visit https://cli.github.com/

### Step 2: Login to GitHub

```bash
gh auth login
```

### Step 3: Run the Secret Script

```bash
cd traffic-agent
./run-with-secrets.sh
```

**What it does:**
1. Fetches all secrets from GitHub automatically
2. Sets environment variables
3. Starts the API server

✅ No need to paste secrets manually!

---

## Option 3: Manual Setup (Fastest if you already have .env)

If you already have a `.env` file:

```bash
cd traffic-agent
python3 api_server.py
```

✅ Server starts with existing `.env` configuration!

---

## 📱 Test the Website

Once the server is running:

1. **Open website:**
   ```bash
   open docs/index.html
   ```

2. **Or visit:**
   - Local: `http://localhost:5000`
   - GitHub Pages: `https://ARROW12.github.io/traffic-agent`

3. **Interact:**
   - Type: `Mantri Celestia` → Enter
   - Type: `RMZ Spire, Hyderabad` → Enter
   - See traffic analysis! 🎉

---

## 🐛 Troubleshooting

### "Command not found"
```bash
chmod +x setup.sh run-with-secrets.sh
./setup.sh
```

### "API Key invalid"
- Get Google Maps key: https://console.cloud.google.com
- Get Twilio credentials: https://www.twilio.com/console

### "Cannot fetch from API"
- Make sure API server is running in another terminal
- Check it says: "✅ Server starting on http://localhost:5000"

### "Website shows error"
- Press F12 → Console tab
- Check exact error message
- Make sure API endpoint is correct

---

## 📊 What Each Script Does

| Script | Method | Requires | Difficulty |
|--------|--------|----------|-----------|
| `setup.sh` | Interactive form | Nothing | ⭐ Easy |
| `run-with-secrets.sh` | GitHub CLI | `gh` CLI tool | ⭐⭐ Medium |
| Manual | Copy .env | Manual setup | ⭐⭐⭐ Hard |

---

## ⚙️ Environment Variables Explained

| Variable | Where to get | Example |
|----------|-----------|---------|
| `MAPS_API_KEY` | Google Cloud Console | `AIzaSyDxxx...` |
| `TWILIO_ACCOUNT_SID` | Twilio Dashboard | `ACxxx...` |
| `TWILIO_AUTH_TOKEN` | Twilio Dashboard | `auth_xxx...` |
| `YOUR_CELL_NUMBER` | Your phone number | `+919876543210` |
| `HOME_ADDRESS` | Any location | `Hitech City, Hyderabad` |
| `OFFICE_ADDRESS` | Any location | `Banjara Hills` |
| `GITHUB_TOKEN` | GitHub Settings | `ghp_xxx...` |

---

## 🎯 Recommended Setup Path

**First Time:**
```bash
./setup.sh          # Quick interactive setup
# Paste your credentials when prompted
# Server starts automatically ✅
```

**Next Time:**
```bash
./setup.sh          # Uses existing .env
# Or just: python3 api_server.py
```

**With GitHub CLI (Advanced):**
```bash
brew install gh
./run-with-secrets.sh
```

---

## 💡 Pro Tips

1. **Keep scripts handy:** Save these scripts to run anytime
2. **Use GitHub CLI:** More secure (no local .env with secrets)
3. **Test locally first:** Before deploying to production
4. **Check logs:** If something fails, error messages help debug

---

**Ready? Start with:** `./setup.sh` 🚀
