const axios = require('axios');

// In-memory state tracking map for temporary multi-step parameters
// Note: For long-term production persistence across container spin-downs,
// Twilio Sync map documents can easily replace this array layout.
global.userStates = global.userStates || {};

exports.handler = async function(context, event, callback) {
    const twiml = new Twilio.twiml.MessagingResponse();
    const userNumber = event.From;
    const incomingBody = (event.Body || '').trim();
    
    // Check if the payload contains native WhatsApp incoming GPS parameters
    const incomingLatitude = event.Latitude;
    const incomingLongitude = event.Longitude;

    // Load internal pipeline configuration credentials
    const githubToken = context.GITHUB_TOKEN;
    const repo = context.GITHUB_REPO;
    const workflow = context.WORKFLOW_FILE;

    // Initialize state profile if empty
    if (!global.userStates[userNumber]) {
        global.userStates[userNumber] = { stage: "IDLE", source: null };
    }

    let currentState = global.userStates[userNumber];

    // STEP 1: Catch session initiation triggers
    if (incomingBody.toLowerCase() === 'hi' || incomingBody === '.') {
        currentState.stage = "AWAITING_START";
        currentState.source = null;
        
        twiml.message(
            "🤖 *JARVIS SENSORS INITIALIZED*\n\n" +
            "Please provide your *starting point* / current location.\n\n" +
            "📌 *Tip:* Click the attachment icon (📎 or +) in WhatsApp and select *Location* to transmit your current coordinates instantly, or reply with a text address manually."
        );
        return callback(null, twiml);
    }

    // STEP 2: Process Starting Point input vector
    if (currentState.stage === "AWAITING_START") {
        if (incomingLatitude && incomingLongitude) {
            // User used native WhatsApp paperclip attachment to share live GPS coordinates
            currentState.source = `${incomingLatitude},${incomingLongitude}`;
        } else if (incomingBody.length > 2) {
            // User opted to type text coordinates or manual text location address string
            currentState.source = incomingBody;
        } else {
            twiml.message("⚠️ Entry invalid. Please reply with a text location or drop a map pin.");
            return callback(null, twiml);
        }

        currentState.stage = "AWAITING_DESTINATION";
        twiml.message("📍 *Origin Secured.* Now enter your *destination location* as plain text:");
        return callback(null, twiml);
    }

    // STEP 3: Process Destination input vector and boot core execution engine
    if (currentState.stage === "AWAITING_DESTINATION") {
        if (!incomingBody || incomingBody.length < 2) {
            twiml.message("⚠️ Please reply with a valid target destination location address name.");
            return callback(null, twiml);
        }

        const resolvedSource = currentState.source;
        const resolvedDestination = incomingBody;

        // Reset tracking flags back to default state
        currentState.stage = "IDLE";
        currentState.source = null;

        // Immediately flash acknowledgment receipt back to client frame
        twiml.message(`🚀 *Parameters Accepted.*\nFrom: ${resolvedSource}\nTo: ${resolvedDestination}\nFiring predictions now...`);

        // Trigger GitHub Actions Workflow via API
        const url = `https://api.github.com/repos/${repo}/actions/workflows/${workflow}/dispatches`;
        const headers = {
            'Accept': 'application/vnd.github.v3+json',
            'Authorization': `Bearer ${githubToken}`,
            'User-Agent': 'Twilio-Function'
        };

        // Pass source and destination as separate workflow inputs
        const data = {
            ref: 'main',
            inputs: {
                source: resolvedSource,
                destination: resolvedDestination
            }
        };

        try {
            await axios.post(url, data, { headers });
            return callback(null, twiml);
        } catch (error) {
            console.error(error.response ? error.response.data : error.message);
            // Fallback communication block
            const errorTwiml = new Twilio.twiml.MessagingResponse();
            errorTwiml.message("❌ Pipeline interface deployment connection failure on core endpoint.");
            return callback(null, errorTwiml);
        }
    }

    // Default catch-all for passive outside conversation input
    twiml.message("🤖 System is idle. Type *.* or *hi* to trigger a navigation flight plan sequence.");
    return callback(null, twiml);
};
