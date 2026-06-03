# Website Integration Guide

The website needs to call a backend API to fetch traffic analysis data. Here are your options:

## Option 1: Simple Python Server (Recommended for Local Development)

Create a simple Flask server to serve the API:

```python
# server.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
from traffic_agent import construct_jarvis_intelligence_brief
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route('/api/traffic', methods=['POST'])
def analyze():
    data = request.json
    os.environ['SOURCE_LOCATION'] = data.get('source', '')
    os.environ['DESTINATION_LOCATION'] = data.get('destination', '')
    os.environ['OUTPUT_JSON'] = 'true'
    
    try:
        result = construct_jarvis_intelligence_brief()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

Install dependencies:
```bash
pip install flask flask-cors python-dotenv
```

Run:
```bash
python server.py
```

Website will call: `http://localhost:5000/api/traffic`

## Option 2: Deploy as Serverless Function (Production)

### Using Vercel

1. Create `api/traffic.py`:
```python
from traffic_agent import construct_jarvis_intelligence_brief
import os

def handler(request):
    if request.method != 'POST':
        return {'error': 'POST only'}, 400
    
    body = request.json
    os.environ['SOURCE_LOCATION'] = body['source']
    os.environ['DESTINATION_LOCATION'] = body['destination']
    os.environ['OUTPUT_JSON'] = 'true'
    
    result = construct_jarvis_intelligence_brief()
    return result, 200
```

2. Deploy to Vercel:
```bash
npm install -g vercel
vercel
```

3. Update website `index.html` to use: `https://your-vercel-url.vercel.app/api/traffic`

### Using Netlify

1. Create `netlify/functions/traffic.js`:
```javascript
const { spawn } = require('child_process');

exports.handler = async (event) => {
    if (event.httpMethod !== 'POST') {
        return { statusCode: 405, body: 'Method not allowed' };
    }
    
    const body = JSON.parse(event.body);
    
    // Run Python script
    return new Promise((resolve, reject) => {
        const python = spawn('python', ['traffic_agent.py']);
        
        python.stdout.on('data', (data) => {
            resolve({
                statusCode: 200,
                body: data.toString()
            });
        });
        
        python.on('error', (error) => {
            reject(error);
        });
    });
};
```

2. Deploy:
```bash
npm install -g netlify-cli
netlify deploy
```

## Option 3: AWS Lambda

1. Package traffic_agent.py with dependencies
2. Create Lambda function handler
3. Use API Gateway to expose HTTP endpoint
4. Update website to call API Gateway URL

## Option 4: GitHub Pages + External Service

Keep GitHub Pages static, use external API:
- [RapidAPI](https://rapidapi.com) - Host your API
- [Heroku](https://heroku.com) - Simple Python deployment
- [Replit](https://replit.com) - Quick Python server
- [PythonAnywhere](https://pythonanywhere.com) - Python hosting

## Implementation Steps

### Step 1: Choose Your Deployment Option

**Local/Development**: Use Option 1 (Flask)
**Production/Zero-cost**: Use Vercel/Netlify (Options 2-3)
**Existing Infrastructure**: Use AWS Lambda or your server

### Step 2: Set Environment Variables

Your API needs these in the environment:

```
GOOGLE_MAPS_API_KEY=your_key
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
YOUR_CELL_NUMBER=your_number
HOME_ADDRESS=your_home
OFFICE_ADDRESS=your_office
```

### Step 3: Update Website

Update the fetch URL in `docs/index.html`:

```javascript
// Line ~160 in index.html
const response = await fetch('https://your-api-endpoint.com/api/traffic', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ source, destination })
});
```

### Step 4: Test

1. Run the backend API
2. Open website
3. Enter source and destination
4. Should see traffic analysis

## Troubleshooting

### CORS Errors
Make sure your API has CORS headers enabled:
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: POST, OPTIONS
Access-Control-Allow-Headers: Content-Type
```

### API Timeouts
- Increase timeout in `construct_jarvis_intelligence_brief()` function
- Optimize Google Maps API calls
- Use caching if possible

### Missing Data
- Check `.env` file has all required API keys
- Test traffic_agent.py directly:
  ```bash
  export OUTPUT_JSON=true
  python traffic_agent.py
  ```

## Live Demo

Current website at: `https://arrow12.github.io/traffic-agent`
(Note: Currently shows demo UI, waiting for API connection)

Once you set up the backend API and update the fetch URL, the website will be fully functional!

## Quick Setup (5 minutes)

```bash
# 1. Install Flask
pip install flask flask-cors python-dotenv

# 2. Run server.py in traffic-agent directory
python server.py

# 3. Update docs/index.html line ~160:
# const response = await fetch('http://localhost:5000/api/traffic', {

# 4. Open docs/index.html in browser
# Website is now live with real traffic data!

# 5. To make it public, deploy to Vercel/Netlify and update the fetch URL
```
