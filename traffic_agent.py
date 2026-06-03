import os
import requests
from twilio.rest import Client

# Fetch API Keys & Numbers from GitHub Environment Variables
GOOGLE_MAPS_API_KEY = os.getenv("MAPS_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
YOUR_CELL_NUMBER = os.getenv("YOUR_CELL_NUMBER")
TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886"  # Standard Twilio Sandbox Number

# Fetch Core Addresses from GitHub Environment Variables
HOME_ADDRESS = os.getenv("HOME_ADDRESS")
OFFICE_ADDRESS = os.getenv("OFFICE_ADDRESS")

# Define alternative routes using intermediate waypoints to force separate paths
ROUTES = {
    "Route Alpha (Main Highway)": "Waypoint+Address+One+City",
    "Route Beta (Expressway/Toll)": "Waypoint+Address+Two+City",
    "Route Gamma (Backroads)": "Waypoint+Address+Three+City"
}

def get_best_route():
    route_results = {}
    error_logs = []
    
    for route_name, waypoint in ROUTES.items():
        # Switched to Directions API which natively supports the 'via:' waypoint routing modifier
        url = (
            f"https://maps.googleapis.com/maps/api/directions/json?"
            f"origin={HOME_ADDRESS}&destination={OFFICE_ADDRESS}&waypoints=via:{waypoint}"
            f"&departure_time=now&traffic_model=best_guess&key={GOOGLE_MAPS_API_KEY}"
        )
        try:
            res = requests.get(url).json()
            
            # If Google explicitly flags an error code, log it
            if res.get("status") != "OK":
                error_detail = res.get("error_message", res.get("status"))
                error_logs.append(f"• {route_name}: {error_detail}")
                continue
                
            leg = res['routes'][0]['legs'][0]
            
            # Extract traffic duration or fall back gracefully to base timeline
            if 'duration_in_traffic' in leg:
                duration_text = leg['duration_in_traffic']['text']
                duration_seconds = leg['duration_in_traffic']['value']
            else:
                duration_text = leg['duration']['text'] + " (No Traffic Info)"
                duration_seconds = leg['duration']['value']
                
            route_results[route_name] = {
                "text": duration_text,
                "seconds": duration_seconds
            }
        except Exception as e:
            error_logs.append(f"• {route_name} Code Exception: {str(e)}")
            
    if not route_results:
        error_summary = "\n".join(error_logs)
        return f"⚠️ *Google Maps Configuration Error:*\n\n{error_summary}\n\n_Please check your Google Cloud Console settings._"
        
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
    print(f"Workflow completed. Notification Sent: {message.sid}")

if __name__ == "__main__":
    traffic_report = get_best_route()
    send_whatsapp_message(traffic_report)
