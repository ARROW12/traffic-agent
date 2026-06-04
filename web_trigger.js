const axios = require('axios');

exports.handler = async function(context, event, callback) {
    const response = new Twilio.Response();

    // CORS Headers
    response.appendHeader('Access-Control-Allow-Origin', '*');
    response.appendHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    response.appendHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
    response.appendHeader('Content-Type', 'application/json');

    // Preflight check for Browser Fetch
    if (event.request.method === 'OPTIONS') {
        response.setStatusCode(204);
        return callback(null, response);
    }

    try {
        // Sanitize environment variables to prevent 404 URL errors
        const repo = (context.GITHUB_REPO || '').trim();
        const workflow = (context.WORKFLOW_FILE || '').trim();
        const token = (context.GITHUB_TOKEN || '').trim();

        if (!repo || !workflow || !token) {
            throw new Error("Missing Twilio Environment Variables.");
        }

        const url = `https://api.github.com/repos/${repo}/actions/workflows/${workflow}/dispatches`;
        console.log("Triggering URL:", url);

        // Call GitHub
        await axios.post(url, {
            ref: 'main', // Make sure your workflow is on the 'main' branch
            inputs: { 
                source: event.source || 'Home', 
                destination: event.destination || 'Office' 
            }
        }, {
            headers: {
                'Accept': 'application/vnd.github.v3+json',
                'Authorization': `Bearer ${token}`,
                'User-Agent': 'Twilio-Web-Function'
            }
        });

        // SUCCESS: Explicitly send success payload back to HTML
        response.setStatusCode(200);
        response.setBody(JSON.stringify({ 
            success: true, 
            message: "🚀 Flight plan successfully launched!" 
        }));
        return callback(null, response);

    } catch (error) {
        const statusCode = error.response ? error.response.status : 500;
        console.error(`GITHUB ERROR (${statusCode}):`, error.response ? error.response.data : error.message);
        
        // Translate GitHub errors into human-readable messages for your UI
        let userMessage = "Pipeline trigger failed.";
        if (statusCode === 404) userMessage = "Workflow file not found. Check GITHUB_REPO and WORKFLOW_FILE variables.";
        if (statusCode === 401) userMessage = "Unauthorized. Check your GITHUB_TOKEN.";
        if (statusCode === 422) userMessage = "Invalid inputs. Ensure workflow YAML matches the data sent.";

        // We return a 200 HTTP status so the browser fetch doesn't crash, 
        // but we pass success: false so your JS knows it failed.
        response.setStatusCode(200);
        response.setBody(JSON.stringify({ 
            success: false, 
            error: userMessage 
        }));
        return callback(null, response);
    }
};
