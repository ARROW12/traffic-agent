import os
import requests
from twilio.rest import Client

# Fetch Environment Variables
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
YOUR_CELL_NUMBER = os.getenv("YOUR_CELL_NUMBER")
TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886"

HOME_ADDRESS = os.getenv("HOME_ADDRESS")
OFFICE_ADDRESS = os.getenv("OFFICE_ADDRESS")

ROUTES = {
    "Route Alpha (Main Highway)": "Waypoint+Address+One+City",
}

def get_best_route():
    route_results = {}
    error_logs = []
    
    # --- SAFE DIAGNOSTICS CONTROL ---
    key_str = GOOGLE_MAPS_API_KEY if GOOGLE_MAPS_API_KEY else ""
    key_length = len(key_str)
    key_prefix = key_str[:6] if key_length >= 6 else key_str
    # --------------------------------
    
    for route_name, waypoint in ROUTES.items():
        url = (
            f"https://maps.googleapis.com/maps/api/directions/json?"
            f"origin={HOME_ADDRESS}&destination={OFFICE_ADDRESS}&key={key_str}"
        )
        try:
            res = requests.get(url).json()
            if res.get("status") != "OK":
                error_detail = res.get("error_message", res.get("status"))
                error_logs.append(f"• {route_name}: {error_detail}")
                continue
                
            leg = res['routes'][0]['legs'][0]
            duration_text = leg['duration_in_traffic']['text'] if 'duration_in_traffic' in leg else leg['duration']['text']
            route_results[route_name] = duration_text
        except Exception as e:
            error_logs.append(f"• {route_name} Exception: {str(e)}")
            
    if not route_results:
        error_summary = "\n".join(error_logs)
        # Appending safe debugging meta-data directly to your WhatsApp alert
        diagnostic_report = (
            f"⚠️ *Google Maps Configuration Error:*\n\n{error_summary}\n\n"
            f"🔍 *Pipeline Diagnostic Data*:\n"
            f"• Key String Length: `{key_length}` characters\n"
            f"• Key Starts With: `{key_prefix}`"
        )
        return diagnostic_report
        
    return f"🏆 Optimal Path: {list(route_results.values())[0]}"

def send_whatsapp_message(text):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    client.messages.create(from_=TWILIO_WHATSAPP_NUMBER, body=text, to=YOUR_CELL_NUMBER)

if __name__ == "__main__":
    traffic_report = get_best_route()
    send_whatsapp_message(traffic_report)
