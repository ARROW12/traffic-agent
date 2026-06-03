# JARVIS Traffic Agent - Interactive Console Website

This is an **interactive chat-like console** for real-time traffic analysis, hosted on GitHub Pages.

## Features

✨ **Interactive Console Experience**
- Chat-like interface similar to WhatsApp
- Step-by-step conversation (source → destination → analysis)
- Real-time traffic analysis
- Animated typing indicators
- Beautiful gradient UI

📊 **Real-Time Data**
- Current ETA estimates
- Traffic trend predictions (+10min, +30min)
- Fuel cost calculations
- Weather conditions
- Air quality index
- Place ratings & reviews

🚗 **Multi-Modal Support**
- Car routing
- 2-wheeler routing
- Direct Google Maps links

## How It Works

### User Flow

```
1. User opens website
2. Bot: "Welcome! Where are you traveling from?"
3. User: "Hitech City, Hyderabad"
4. Bot: "✅ Source set. Where do you want to go?"
5. User: "Banjara Hills"
6. Bot: "🔍 Analyzing... [shows results]"
   - Route information
   - Weather & AQI
   - Car route options
   - Bike route options
7. Bot: "Want to search another route?"
8. Loop back to step 2
```

## Setup

### Option 1: Local Testing

```bash
# 1. Navigate to project
cd traffic-agent

# 2. Start API server (in Terminal 1)
python api_server.py

# 3. Edit docs/index.html
# Find line: const API_URL = 'http://localhost:5000/api/traffic';
# Keep as-is for local testing

# 4. Open in browser
open docs/index.html
```

### Option 2: GitHub Pages (Production)

```bash
# 1. Enable GitHub Pages
# Go to: Settings → Pages
# Source: Deploy from branch → main
# Folder: / (root)

# 2. Deploy API backend (choose one):
# - Vercel: npm install -g vercel && vercel
# - Netlify: netlify deploy
# - Heroku: git push heroku main

# 3. Update API URL in docs/index.html
# Line: const API_URL = 'https://your-api-url.com/api/traffic';

# 4. Commit and push
git add docs/index.html
git commit -m "Update API endpoint"
git push origin main

# 5. Website automatically deploys!
```

## API Integration

The website calls your backend API with:

```javascript
POST /api/traffic
Content-Type: application/json

{
  "source": "Hitech City, Hyderabad",
  "destination": "Banjara Hills"
}
```

Expected response:

```json
{
  "text": "Traffic analysis report",
  "data": {
    "source": "Hitech City, Hyderabad",
    "destination": "Banjara Hills",
    "timestamp": "02:30:15 PM",
    "weather": "28°C, Partly Cloudy ⛅",
    "aqi": {
      "source": "67 (Moderate 🟡)",
      "destination": "62 (Moderate 🟡)"
    },
    "source_details": {
      "rating": 4.5,
      "reviews": 1240
    },
    "dest_details": {
      "rating": 4.3,
      "reviews": 890
    },
    "car_profile": {
      "via": "NH44",
      "distance": "12.3 km",
      "current_eta": "18 mins",
      "trend": "Clearing 📉",
      "recommendation": "Hold position...",
      "fuel_cost": "₹23.45",
      "nav_link": "https://maps.google.com/..."
    },
    "bike_profile": {
      "via": "NH44",
      "distance": "12.3 km",
      "current_eta": "25 mins",
      "trend": "Stable ➡️",
      "recommendation": "Traffic is consistent...",
      "fuel_cost": "₹6.45",
      "nav_link": "https://maps.google.com/..."
    }
  }
}
```

## Customization

### Change API URL

Edit `docs/index.html` line 179:

```javascript
// For local testing
const API_URL = 'http://localhost:5000/api/traffic';

// For production
const API_URL = 'https://your-deployed-api.com/api/traffic';
```

### Change Colors

Edit `docs/index.html` CSS section:

```css
/* Current colors (purple gradient) */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Change to your preferred gradient */
```

### Change Welcome Message

Edit JavaScript section (search for "Welcome"):

```javascript
addMessage("👋 Welcome! Start by telling me your source location.");
```

## Deployment URLs

| Service | URL |
|---------|-----|
| GitHub Pages | `https://USERNAME.github.io/traffic-agent` |
| Vercel API | `https://traffic-agent.vercel.app/api/traffic` |
| Netlify API | `https://traffic-agent.netlify.app/api/traffic` |

## Troubleshooting

### Website shows blank page
- Check browser console (F12 → Console)
- Verify API server is running
- Check API URL in index.html is correct

### "Cannot connect to API"
- Ensure api_server.py is running: `python api_server.py`
- Check API URL in code matches server URL
- For production, deploy API and update URL

### "No route found"
- Try with full addresses: "Hitech City, Hyderabad"
- Not just "Hitech City"
- Use real place names

### Messages not appearing
- Check browser JavaScript errors (F12 → Console)
- Ensure input field is focused
- Try pressing Enter key

## Performance Tips

- API responses usually take 2-5 seconds
- Animated typing indicators provide feedback
- Console auto-scrolls to latest message
- Works on mobile devices

## Browser Support

✅ Chrome 90+
✅ Firefox 88+
✅ Safari 14+
✅ Edge 90+
✅ Mobile browsers (iOS Safari, Chrome Android)

---

**Start exploring!** Open `index.html` or visit your GitHub Pages URL.

