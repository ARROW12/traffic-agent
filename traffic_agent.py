import os
import requests
from twilio.rest import Client

# Fetch API Keys & Numbers from GitHub Environment Variables
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
YOUR_CELL_NUMBER = os.getenv("YOUR_CELL_NUMBER")
TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886"  # Standard Twilio Sandbox Number

# Fetch Core Addresses from GitHub Environment Variables
HOME_ADDRESS = os.getenv("HOME_ADDRESS")
OFFICE_ADDRESS = os.getenv("OFFICE_ADDRESS")

# Define alternative routes using intermediate waypoints to force separate paths
# Note: Replace spaces with '+' signs when defining waypoints below
ROUTES = {
    "Route Alpha (Main Highway)": "Waypoint+Address+One+City",
    "Route Beta (Expressway/Toll)": "Waypoint+Address+Two+City",
    "Route Gamma (Backroads)": "Waypoint+Address+Three+City"
}

def get_best_route():
    route_results = {}
    
    for route_name, waypoint in ROUTES.items():
        # 'departure_time=now' forces Google to evaluate real-time gridlock conditions
        url = (
            f"https://maps.googleapis.com/maps/api/distancematrix/json?"
            f"origins={HOME_ADDRESS}&destinations={OFFICE_ADDRESS}&waypoints={waypoint}"
            f"&departure_time=now&traffic_model=best_guess&key={GOOGLE_MAPS_API_KEY}"
        )
        try:
            response = requests.get(url).json()
            element = response['rows'][0]['elements'][0]
            
            # Extract real-time human-readable time and absolute value in seconds
            duration_in_traffic = element['duration_in_traffic']['text']
            duration_seconds = element['duration_in_traffic']['value']
            
            route_results[route_name] = {
                "text": duration_in_traffic,
                "seconds": duration_seconds
            }
        except Exception as e:
            print(f"Error processing route data for {route_name}: {e}")
            
    if not route_results:
        return "⚠️ *Traffic Agent Error:* Unable to retrieve real-time data from the mapping API."
        
    # Find the path with the absolute lowest duration in seconds
    fastest_route = min(route_results, key=lambda x: route_results[x]['seconds'])
    
    # Format the WhatsApp message body
    message_body = "🚗 *On-Demand Traffic Report* 🚗\n\n"
    message_body += f"🏆 *Optimal Path:* {fastest_route} ({route_results[fastest_route]['text']})\n\n"
    message_body += "All Tracked Options:\n"
    for name, data in route_results.items():
         message_body += f"• {name}: {data['text']}\n"
        
    return message_body

def send_whatsapp_message(text):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    message = client.messages.create(
        from_=TWILIO_WHATSAPP_NUMBER,
        body=text,
        to=YOUR_CELL_NUMBER
    )
    print(f"Workflow successfully completed. Notification Sent SID: {message.sid}")

if __name__ == "__main__":
    traffic_report = get_best_route()
    send_whatsapp_message(traffic_report)