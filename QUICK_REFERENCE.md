# Quick Reference Guide

## 🚀 Quick Start (5 Minutes)

```bash
# 1. Setup environment
cp .env.example .env
# Edit .env with your API keys

# 2. Install dependencies
pip install -r requirements.txt

# 3. Test Python script
export $(cat .env | xargs)
python traffic_agent.py

# 4. Deploy to Twilio (manual - see SETUP_GUIDE.md)

# 5. Push to GitHub
git add .
git commit -m "Traffic agent ready"
git push
```

---

## 📱 WhatsApp Test Flow

```
You:     .
Bot:     🤖 *JARVIS SENSORS INITIALIZED*...

You:     123 Main Street, City
Bot:     📍 *Origin Secured.*...

You:     456 Office Drive, City
Bot:     🚀 *Parameters Accepted.*...
         [Wait 15-30 seconds]
Bot:     🤖 *JARVIS FLIGHT PLAN SYSTEM*...
         [Traffic analysis report]
```

---

## 🔧 Common Commands

### Testing Python Locally
```bash
# Set environment variables
export TRIGGER_MESSAGE="from Home to Office in 0 mins"
export MAPS_API_KEY="your_key_here"
export TWILIO_ACCOUNT_SID="your_sid"
export TWILIO_AUTH_TOKEN="your_token"
export YOUR_CELL_NUMBER="whatsapp:+1234567890"
export HF_TOKEN="your_token"
export HOME_ADDRESS="Home"
export OFFICE_ADDRESS="Office"

# Run the script
python traffic_agent.py
```

### Testing with .env File
```bash
# Export all variables at once
export $(cat .env | xargs)

# Run the script
python traffic_agent.py

# Or with inline trigger
TRIGGER_MESSAGE="from Home to Office in 0 mins" python traffic_agent.py
```

### Testing API Endpoints

```bash
# Google Maps API
curl "https://maps.googleapis.com/maps/api/directions/json?origin=Home&destination=Office&key=YOUR_KEY"

# Weather API
curl "https://api.open-meteo.com/v1/forecast?latitude=17.3850&longitude=78.4867&current=temperature_2m,weather_code"

# AQI API
curl "https://air-quality-api.open-meteo.com/v1/air-quality?latitude=17.3850&longitude=78.4867&current=us_aqi"

# GitHub Token Verification
curl -H "Authorization: Bearer YOUR_GITHUB_TOKEN" https://api.github.com/user
```

---

## 📊 File Locations Reference

### Code Files
- JavaScript Handler: `twilio_handler.js`
- Python Backend: `traffic_agent.py`
- Workflow: `.github/workflows/traffic-analysis.yml`

### Configuration
- Environment Template: `.env.example`
- Dependencies: `requirements.txt`
- Git Ignore: `.gitignore`

### Documentation
- Main README: `README.md`
- Setup Guide: `SETUP_GUIDE.md`
- Issue Analysis: `ISSUE_ANALYSIS.md`
- This Guide: `QUICK_REFERENCE.md`

---

## 🔑 Environment Variables Checklist

```
Required:
✓ MAPS_API_KEY
✓ TWILIO_ACCOUNT_SID
✓ TWILIO_AUTH_TOKEN
✓ YOUR_CELL_NUMBER
✓ HF_TOKEN
✓ HOME_ADDRESS
✓ OFFICE_ADDRESS

Optional (for local testing):
✓ TRIGGER_MESSAGE
✓ GITHUB_TOKEN (for testing workflow dispatch)
✓ GITHUB_REPO
✓ WORKFLOW_FILE
```

---

## 🐛 Debugging Commands

### Check Python Syntax
```bash
python -m py_compile traffic_agent.py
```

### Check for Missing Modules
```bash
pip list
# Should show: requests, twilio, python-dotenv, numpy
```

### Test Twilio Connection
```bash
python -c "
from twilio.rest import Client
import os
client = Client(os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))
print('Twilio connected successfully!')
"
```

### View Logs
```bash
# Twilio Function Logs
# Go to: Twilio Console → Functions → Logs

# GitHub Actions Logs
# Go to: https://github.com/YOUR_USERNAME/traffic-agent/actions

# Python stderr
python -u traffic_agent.py  # Run unbuffered
```

---

## 🔄 Deployment Checklist

Before pushing to production:

```bash
# 1. Verify all files exist
ls -la twilio_handler.js traffic_agent.py .github/workflows/traffic-analysis.yml

# 2. Test Python script
python traffic_agent.py

# 3. Verify no hardcoded secrets
grep -r "sk-" . --exclude-dir=.git
grep -r "Bearer " . --exclude-dir=.git

# 4. Check git status
git status

# 5. Add files
git add .

# 6. Commit
git commit -m "Production-ready traffic agent"

# 7. Push
git push origin main

# 8. Verify on GitHub
open https://github.com/YOUR_USERNAME/traffic-agent
```

---

## 🚨 Emergency Troubleshooting

### System Completely Broken?

```bash
# 1. Check Python installation
python --version  # Should be 3.7+

# 2. Check dependencies
pip install -r requirements.txt --upgrade

# 3. Test individual imports
python -c "import requests; print('requests OK')"
python -c "import twilio; print('twilio OK')"

# 4. Check environment
env | grep MAPS_API_KEY  # Should show value

# 5. Test API connectivity
python -c "import requests; requests.get('https://google.com'); print('Internet OK')"
```

### Handler Not Responding?

```bash
# 1. Check Twilio logs
open https://www.twilio.com/console/functions/logs

# 2. Verify function URL
# In Twilio Console → Functions → Logs

# 3. Manually test function
curl -X POST https://your-service.twilio.io/handler \
  -d "From=whatsapp:+1234567890&Body=hi"

# 4. Check error response
# Look for error messages in response body
```

### GitHub Actions Not Running?

```bash
# 1. Check workflow syntax
python -m yamllint .github/workflows/traffic-analysis.yml

# 2. Check Actions are enabled
# Repo Settings → Actions → General → "Allow all actions"

# 3. Check secrets are set
# Settings → Secrets and variables → Actions

# 4. View run logs
open https://github.com/YOUR_USERNAME/traffic-agent/actions
```

---

## 💡 Pro Tips

### Testing Different Locations
```bash
# Test with coordinates
TRIGGER_MESSAGE="from 17.3850,78.4867 to 17.4209,78.4601 in 0 mins" python traffic_agent.py

# Test with addresses
TRIGGER_MESSAGE="from Home to Office in 0 mins" python traffic_agent.py

# Test with time offset
TRIGGER_MESSAGE="from Home to Office in 30 mins" python traffic_agent.py
```

### Performance Optimization
```bash
# Run with logging
python -u traffic_agent.py 2>&1 | tee traffic.log

# Profile execution
python -m cProfile -s cumulative traffic_agent.py

# Check API response times
# Add print(time.time()) before/after each API call
```

### Monitoring
```bash
# Watch GitHub Actions
watch -n 5 'curl -s https://api.github.com/repos/YOUR_USERNAME/traffic-agent/actions | jq'

# Monitor Twilio usage
# Twilio Console → Usage and Billing

# Monitor Google Maps usage
# Google Cloud Console → Billing
```

---

## 📞 Support Matrix

| Issue | Check | Solution |
|-------|-------|----------|
| Handler stuck | Twilio logs | Add `return callback()` |
| No workflow trigger | GitHub Actions | Verify GITHUB_TOKEN |
| Missing traffic data | API keys | Enable Direction API |
| AQI showing offline | Network | Check internet connection |
| Python crashes | Dependencies | `pip install -r requirements.txt` |
| State corruption | Code | Verify early returns |

---

## 🎯 Success Indicators

When system is working correctly:

- ✅ WhatsApp conversation flows smoothly
- ✅ Replies come within 30 seconds
- ✅ No error messages appear
- ✅ Traffic data is populated
- ✅ Google Maps links work
- ✅ GitHub Actions runs successfully
- ✅ All APIs responding

---

## 📈 Scaling Guide

As you scale to more users:

```bash
# Monitor API quotas
# Google Maps: Check daily usage
# Hugging Face: Monitor inference calls
# Twilio: Track message count

# Implement caching
# Cache route data for common paths
# Cache weather data for 10 minutes

# Add rate limiting
# Max 1 request per 10 seconds per user
# Max 100 requests per day per user

# Optimize code
# Use connection pooling
# Implement request batching
```

---

## 🔗 Useful Links

- [Twilio WhatsApp API](https://www.twilio.com/whatsapp)
- [Google Maps Directions API](https://developers.google.com/maps/documentation/directions)
- [GitHub Actions](https://docs.github.com/en/actions)
- [Open-Meteo Weather API](https://open-meteo.com/)
- [Hugging Face Models](https://huggingface.co/models)

---

## 📝 Notes

Add your custom notes here:

```
_________________________________
_________________________________
_________________________________
_________________________________
_________________________________
```

---

**Last Updated**: June 2026
**Version**: 1.0
**Status**: Production Ready ✅

