# Traffic Agent 🚗 - WhatsApp Navigation Intelligence System

A complete WhatsApp-based traffic analysis and navigation recommendation system using Twilio, Google Maps, and real-time weather/AQI data.

## System Architecture

```
WhatsApp User
    ↓ (Twilio Webhook)
JavaScript Handler (twilio_handler.js)
    ↓ (Triggers GitHub Actions)
GitHub Actions Workflow (traffic-analysis.yml)
    ↓ (Runs Python backend)
Traffic Agent (traffic_agent.py)
    ↓ (Fetches real-time data)
Google Maps API + Weather API + AQI API
    ↓ (Sends report)
WhatsApp User (Intelligent Briefing)
```

## Features

✨ **Multi-Step WhatsApp Conversation**
- Initialize with `.` or `hi`
- Provide starting location (text or GPS)
- Provide destination location
- Receive comprehensive traffic analysis

🚗 **Dual Vehicle Profiles**
- Car routing with real-time traffic
- Motorcycle routing with faster estimates
- Fuel cost calculations

🌡️ **Real-Time Environmental Data**
- Current weather conditions
- Air Quality Index (AQI) analysis
- Temperature-based alerts

🔮 **Predictive Traffic Trends**
- 10-minute forward traffic projections
- Traffic building/clearing analysis
- Strategic departure recommendations

📊 **Intelligent Brief**
- IST timestamp formatting
- Character-optimized WhatsApp messages
- Direct Google Maps navigation links
- Actionable driving recommendations

## Setup Instructions

### 1. Prerequisites
- Twilio WhatsApp Account
- Google Maps API Key
- Hugging Face API Token (free tier)
- GitHub repository with Actions enabled
- Python 3.10+

### 2. Environment Variables

Create a `.env` file or set GitHub Secrets:

```
# Twilio Configuration
TWILIO_ACCOUNT_SID=<your_twilio_sid>
TWILIO_AUTH_TOKEN=<your_twilio_auth_token>
YOUR_CELL_NUMBER=whatsapp:+<your_number>

# Google Maps API
MAPS_API_KEY=<your_google_maps_api_key>
GOOGLE_MAPS_API_KEY=<same_as_above>

# Hugging Face LLM
HF_TOKEN=<your_hugging_face_token>

# Default Locations
HOME_ADDRESS=<your_home_address>
OFFICE_ADDRESS=<your_office_address>

# GitHub Actions (set in repo settings)
GITHUB_TOKEN=<your_github_personal_access_token>
GITHUB_REPO=<owner/repo>
WORKFLOW_FILE=traffic-analysis.yml
```

### 3. Twilio Configuration

1. Go to Twilio Console → Messaging → Try it out → Send an SMS
2. Set up a WhatsApp Business Account
3. Configure Webhook URL pointing to your Twilio Function:
   - **Webhook URL**: `https://your-twilio-domain/twilio_handler`
   - **Method**: POST
   - **When a message comes in**: Use the webhook

### 4. Deploy Twilio Function

1. Create a new Twilio Function
2. Copy contents of `twilio_handler.js`
3. Add External Accounts:
   - Twilio
   - Environment variables for GITHUB_TOKEN, GITHUB_REPO, WORKFLOW_FILE
4. Deploy

### 5. GitHub Secrets Setup

In your GitHub repository settings, add these secrets:
- `MAPS_API_KEY`
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `YOUR_CELL_NUMBER`
- `HF_TOKEN`
- `HOME_ADDRESS`
- `OFFICE_ADDRESS`

### 6. Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export TRIGGER_MESSAGE="from Home to Office in 0 mins"
export MAPS_API_KEY="<your_key>"
# ... set other vars

# Run traffic agent
python traffic_agent.py
```

## Usage

### WhatsApp Flow

1. **User**: Send `.` or `hi`
2. **System**: "🤖 *JARVIS SENSORS INITIALIZED*..."
3. **User**: Send location or text address (e.g., "Home" or drop a pin)
4. **System**: "📍 *Origin Secured.*..."
5. **User**: Send destination (e.g., "Office")
6. **System**: Receives comprehensive traffic analysis with:
   - Current ETA for both car and bike
   - Fuel cost estimates
   - Traffic trend predictions
   - Weather and AQI metrics
   - Direct navigation links

## File Structure

```
traffic-agent/
├── twilio_handler.js              # Twilio WhatsApp webhook
├── traffic_agent.py               # Python backend processing
├── .github/
│   └── workflows/
│       └── traffic-analysis.yml    # GitHub Actions workflow
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
└── README.md                       # This file
```

## API Dependencies

| Service | Purpose | Cost |
|---------|---------|------|
| Google Maps Directions API | Route planning & traffic | ~$5/1000 requests |
| Open-Meteo | Weather data | FREE |
| Air Quality API | AQI metrics | FREE |
| Hugging Face | LLM extraction | FREE (serverless) |
| Twilio | WhatsApp messaging | ~$0.005 per message |
| GitHub Actions | Workflow execution | FREE (2000 min/month) |

## Troubleshooting

### JavaScript handler gets stuck after source input
**Fix**: Ensure all state transitions have `return callback(null, twiml);` statements.

### GitHub Actions workflow not triggered
**Check**:
- GITHUB_TOKEN is valid and has repo access
- GITHUB_REPO format is `owner/repo`
- WORKFLOW_FILE matches exact filename in `.github/workflows/`

### Traffic data returns N/A
**Check**:
- Google Maps API key is valid and has Directions API enabled
- Source/destination are valid location strings
- API quotas haven't been exceeded

### AQI/Weather showing "Offline"
- These are non-critical; system still functions
- Check internet connectivity
- Open-Meteo API may be experiencing temporary issues

## Key Functions

| Function | Purpose |
|----------|---------|
| `parse_trigger_message_with_llm()` | Extracts source/dest from text |
| `profile_predictive_engine()` | Calculates traffic profiles |
| `get_weather_metrics()` | Fetches weather conditions |
| `get_aqi_metrics()` | Retrieves air quality index |
| `construct_jarvis_intelligence_brief()` | Assembles final report |
| `dispatch_brief()` | Sends WhatsApp message |

## Performance Metrics

- **Response time**: ~15-30 seconds (includes API calls)
- **Message length**: Optimized for <1550 characters
- **API calls per request**: 4-6 concurrent calls
- **Monthly cost estimate**: $10-20 (excluding phone costs)

## Security Notes

⚠️ **Never commit secrets to git**
- Use GitHub Secrets for all API keys
- Use `.gitignore` for local `.env` files
- Rotate GITHUB_TOKEN regularly
- Use Twilio's secure environment variables

## Future Enhancements

- [ ] Multi-language support
- [ ] Historical traffic pattern analysis
- [ ] Public transit routing
- [ ] Carbon footprint calculations
- [ ] Real-time traffic incident alerts
- [ ] User preferences/favorite routes
- [ ] Batch route optimization

## Support

For issues or questions:
1. Check logs in GitHub Actions tab
2. Review Twilio debug console
3. Test with local Python execution
4. Verify all environment variables are set

---

**Made with ❤️ for smarter commutes**
