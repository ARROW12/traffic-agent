# JARVIS Traffic Agent - Web Interface

This website is hosted on GitHub Pages and provides a beautiful UI for traffic analysis.

## Features

✨ **Real-Time Traffic Analysis**
- Search any source and destination
- Get car and bike routing options
- See weather and AQI data
- Direct Google Maps navigation links

📊 **Place Ratings & Reviews**
- Destination ratings and reviews
- Opening hours
- Place details

🌐 **Fully Responsive**
- Works on desktop, tablet, and mobile
- Optimized interface

## Setup

### Option 1: Enable GitHub Pages (Automatic)

1. Go to GitHub repo → Settings → Pages
2. Source: Deploy from a branch
3. Branch: main
4. Folder: /docs
5. Click Save
6. Your site will be live at: `https://ARROW12.github.io/traffic-agent`

### Option 2: Connect to Traffic Agent API

If you want live data from your traffic agent:

1. Set up an API endpoint that returns JSON
2. Update `index.html` to point to your API
3. The website will call your API automatically

## How It Works

1. Enter starting location and destination
2. Website displays traffic analysis with:
   - Current ETA for cars and bikes
   - Fuel cost estimates
   - Weather conditions
   - Air quality index
   - Direct Google Maps links
   - Route recommendations

## Integration

### Connect with Backend

If you have a backend API returning traffic data:

```javascript
// Replace the fetch URL in index.html
const response = await fetch('https://your-api.com/traffic', {
    method: 'POST',
    body: JSON.stringify({ source, destination })
});
```

### Mock Data (for Demo)

The website includes demo data that loads on first visit:
- Source: "Hitech City, Hyderabad"
- Destination: "Banjara Hills"

This lets you see the UI without needing an API.

## Deployment

The website is automatically deployed when you push to `main` branch (files in `/docs` folder).

No additional setup needed - just visit:
**https://ARROW12.github.io/traffic-agent**

## Files

- `index.html` - Main website (all-in-one HTML file)
- `README.md` - This file

## Architecture

```
User visits website
    ↓
Enters source & destination
    ↓
Calls traffic_agent.py API
    ↓
Gets JSON response
    ↓
Renders beautiful dashboard
```

## Future Enhancements

- [ ] Add route comparison (save/compare multiple routes)
- [ ] Add favorite locations (Home, Office, etc.)
- [ ] Add historical traffic patterns
- [ ] Add incident alerts (accidents, delays)
- [ ] Add EV charging station locator
- [ ] Add public transit options
