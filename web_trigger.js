const axios = require('axios');

exports.handler = async function(context, event, callback) {
    // 1. Setup CORS Headers - Required for cross-origin browser requests
    const response = new Twilio.Response();
    response.appendHeader('Access-Control-Allow-Origin', '*');
    response.appendHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    response.appendHeader('Access-Control-Allow-Headers', 'Content-Type');

    // 2. Handle browser Preflight (OPTIONS) requests
    if (event.request.method === 'OPTIONS') {
        return callback(null, response);
    }

    // 3. Extract data from the POST body
    // Twilio Functions automatically parse JSON bodies into the 'event' object
    const source = event.source;
    const destination = event.destination;

    if (!source || !destination) {
        response.setStatusCode(400);
        response.setBody({ error: "Missing source or destination" });
        return callback(null, response);
    }

    // 4. Trigger the GitHub Action
    const url = `https://api.github.com/repos/${context.GITHUB_REPO}/actions/workflows/${context.WORKFLOW_FILE}/dispatches`;
    const githubHeaders = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': `Bearer ${context.GITHUB_TOKEN}`,
        'User-Agent': 'Twilio-Web-Function'
    };

    const data = {
        ref: 'main',
        inputs: {
            message: `from ${source} to ${destination} in 0 mins`
        }
    };

    try {
        await axios.post(url, data, { headers: githubHeaders });
        
        response.setStatusCode(200);
        response.setBody({ success: true, message: "🚀 Flight plan triggered! Check your WhatsApp." });
        return callback(null, response);
    } catch (error) {
        console.error("GitHub Action Error:", error.response ? error.response.data : error.message);
        response.setStatusCode(500);
        response.setBody({ error: "Failed to trigger the pipeline." });
        return callback(null, response);
    }
};