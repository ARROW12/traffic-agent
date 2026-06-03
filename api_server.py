"""
Simple Flask API server for JARVIS Traffic Agent website.

Usage:
    pip install flask flask-cors
    python api_server.py

Then update docs/index.html fetch URL to: http://localhost:5000/api/traffic
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import json

# Add current directory to path so we can import traffic_agent
sys.path.insert(0, os.path.dirname(__file__))

try:
    from traffic_agent import construct_jarvis_intelligence_brief
    from dotenv import load_dotenv
    load_dotenv()
except ImportError as e:
    print(f"Error importing traffic_agent: {e}")
    print("Make sure traffic_agent.py is in the same directory")
    sys.exit(1)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/api/traffic', methods=['POST', 'OPTIONS'])
def analyze_traffic():
    """Main traffic analysis endpoint."""
    
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        return '', 204
    
    try:
        data = request.json
        
        if not data or 'source' not in data or 'destination' not in data:
            return jsonify({
                'error': 'Missing required fields: source and destination'
            }), 400
        
        source = data.get('source', '').strip()
        destination = data.get('destination', '').strip()
        
        if not source or not destination:
            return jsonify({
                'error': 'Source and destination cannot be empty'
            }), 400
        
        # Set environment variables for traffic_agent
        os.environ['SOURCE_LOCATION'] = source
        os.environ['DESTINATION_LOCATION'] = destination
        os.environ['OUTPUT_JSON'] = 'true'
        
        # Run traffic analysis
        result = construct_jarvis_intelligence_brief()
        
        # If result is already a dict (JSON output), return as-is
        if isinstance(result, dict):
            return jsonify(result), 200
        else:
            # If it's a string, return as text
            return jsonify({
                'text': result,
                'data': {}
            }), 200
    
    except Exception as e:
        print(f"Error in analyze_traffic: {str(e)}", file=sys.stderr)
        return jsonify({
            'error': f'Traffic analysis failed: {str(e)}'
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'service': 'JARVIS Traffic Agent API'
    }), 200

@app.route('/', methods=['GET'])
def root():
    """Root endpoint with API documentation."""
    return jsonify({
        'name': 'JARVIS Traffic Agent API',
        'version': '1.0',
        'endpoints': {
            'POST /api/traffic': {
                'description': 'Analyze traffic for a route',
                'request': {
                    'source': 'Starting location (string)',
                    'destination': 'Destination location (string)'
                },
                'example': {
                    'curl': 'curl -X POST http://localhost:5000/api/traffic -H "Content-Type: application/json" -d \'{"source":"Hitech City","destination":"Banjara Hills"}\'',
                    'python': 'requests.post("http://localhost:5000/api/traffic", json={"source":"Hitech City","destination":"Banjara Hills"})'
                }
            },
            'GET /health': {
                'description': 'Check if API is running'
            }
        }
    }), 200

if __name__ == '__main__':
    print("🤖 JARVIS Traffic Agent API Server")
    print("=" * 50)
    print("✅ Server starting on http://localhost:5000")
    print()
    print("📍 Endpoints:")
    print("  • http://localhost:5000 - API docs")
    print("  • http://localhost:5000/health - Health check")
    print("  • http://localhost:5000/api/traffic - Traffic analysis")
    print()
    print("🌐 Website setup:")
    print("  1. Update docs/index.html line ~160:")
    print("     const response = await fetch('http://localhost:5000/api/traffic', {")
    print()
    print("  2. Open docs/index.html in browser")
    print()
    print("  3. Try it out!")
    print()
    print("=" * 50)
    print()
    
    # Run the Flask app
    app.run(debug=True, port=5000, use_reloader=True)
