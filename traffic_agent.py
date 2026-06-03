import os
import re
import requests
import urllib.parse
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from twilio.rest import Client

# Configuration Boundaries
GOOGLE_MAPS_API_KEY = os.getenv("MAPS_API_KEY") or os.getenv("GOOGLE_MAPS_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
YOUR_CELL_NUMBER = os.getenv("YOUR_CELL_NUMBER")
TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886"

DEFAULT_HOME = os.getenv("HOME_ADDRESS")
DEFAULT_OFFICE = os.getenv("OFFICE_ADDRESS")
TRIGGER_MESSAGE = os.getenv("TRIGGER_MESSAGE", "")

# Current localized price baseline for Hyderabad, Telangana
PETROL_PRICE_HYD = 115.73  

def parse_trigger_message(msg):
    """
    Parses text inputs using robust regex separation rules to identify overrides.
    Example text target: 'I want to travel from Point A to Point B in 30 mins'
    """
    if not msg or "from" not in msg.lower() or "to" not in msg.lower():
        return DEFAULT_HOME, DEFAULT_OFFICE, 0
        
    source, destination, offset = None, None, 0
    try:
        from_match = re.search(r'\bfrom\s+(.*?)\s+to\b', msg, re.IGNORECASE)
        if from_match:
            source = from_match.group(1).strip()
            
        to_match = re.search(r'\bto\s+(.*?)(?:\s+in\s+|\s+now\b|\s+can\s+you|$)', msg, re.IGNORECASE)
        if to_match:
            destination = to_match.group(1).strip()
            destination = re.sub(r'(,?\s+in\s+\d+.*|,?\s+now.*)', '', destination, flags=re.IGNORECASE).strip()
            
        time_match = re.search(r'\bin\s+(\d+)\s*mins?', msg, re.IGNORECASE)
        if time_match:
            offset = int(time_match.group(1))
    except Exception:
        return DEFAULT_HOME, DEFAULT_OFFICE, 0
        
    return (source or DEFAULT_HOME), (destination or DEFAULT_OFFICE), offset

def get_ist_time():
    return (datetime.utcnow() + timedelta(hours=5, minutes=30)).strftime("%I:%M:%S %p")

def get_aqi_metrics(lat, lon):
    try:
        url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=us_aqi"
        res = requests.get(url).json()
        aqi = res.get("current", {}).get("us_aqi", None)
        if aqi is None: return "N/A"
        if aqi <= 50: return f"{aqi} (Good 🟢)"
        elif aqi <= 100: return f"{aqi} (Moderate 🟡)"
        elif aqi <= 150: return f"{aqi} (Sensitive 🟠)"
        return f"{aqi} (Unhealthy 🔴)"
    except Exception:
        return "Offline"

def generate_maps_navigation_url(origin, destination, mode):
    encoded_origin = urllib.parse.quote(origin)
    encoded_dest = urllib.parse.quote(destination)
    gmaps_mode = "driving" if mode == "driving" else "two_wheeler"
    return f"https://www.google.com/maps/dir/?api=1&origin={encoded_origin}&destination={encoded_dest}&travelmode={gmaps_mode}"

def profile_predictive_engine(source, destination, base_offset, mode):
    base_url = "https://maps.googleapis.com/maps/api/directions/json"
    intervals = [base_offset, base_offset + 10, base_offset + 30]
    sampled_durations = []
    timeline_matrix = np.array(intervals).reshape(-1, 1)
    
    primary_via = "Standard Route"
    distance_km = 0.0
    distance_str = "N/A"
    tactical_maneuvers = []
    coords = {}
    
    for idx, offset in enumerate(intervals):
        future_timestamp = int((datetime.utcnow() + timedelta(minutes=offset)).timestamp())
        params = {
            "origin": source,
            "destination": destination,
            "mode": mode,
            "departure_time": str(future_timestamp),
            "key": GOOGLE_MAPS_API_KEY
        }
        
        try:
            res = requests.get(base_url, params=params).json()
            if res.get("status") == "OK":
                route = res["routes"][0]
                leg = route["legs"][0]
                
                if idx == 0:
                    primary_via = route.get("summary", "Primary Route")
                    distance_km = leg["distance"]["value"] / 1000.0
                    distance_str = leg["distance"]["text"]
                    tactical_maneuvers = [re.sub(re.compile('<.*?>'), '', s.get("html_instructions", "")) for s in leg["steps"][:2]]
                    coords = {
                        'start_lat': leg["start_location"]["lat"], 'start_lon': leg["start_location"]["lng"],
                        'end_lat': leg["end_location"]["lat"], 'end_lon': leg["end_location"]["lng"]
                    }
                
                dur_val = leg.get("duration_in_traffic", leg["duration"])["value"] / 60.0
                sampled_durations.append(dur_val)
            else:
                if len(sampled_durations) > 0:
                    sampled_durations.append(sampled_durations[-1])
        except Exception:
            return None

    if len(sampled_durations) < 2:
        return None

    # Calculate specific fuel expenses
    mileage = 12.0 if mode == "driving" else 25.0
    fuel_needed = distance_km / mileage
    fuel_cost = fuel_needed * PETROL_PRICE_HYD
    
    # Delta forecasting optimization calculation
    delta_10 = sampled_durations[1] - sampled_durations[0]
    if delta_10 > 0.5:
        immediate_trend = f"Building 📈 (+ {int(delta_10)} mins if you wait 10 mins)"
        recommendation = "Depart immediately. Postponing departure builds congestion overhead."
    elif delta_10 < -0.5:
        immediate_trend = f"Clearing 📉 (- {int(abs(delta_10))} mins if you wait 10 mins)"
        recommendation = "Hold position. Waiting 10-15 minutes bypasses localized bottlenecks."
    else:
        immediate_trend = "Stable ➡️ [No variation inside 10 mins]"
        recommendation = "Parameters nominal. Depart at your convenience."

    return {
        "via": primary_via,
        "distance": distance_str,
        "current_eta": f"{int(sampled_durations[0])} mins",
        "trend": immediate_trend,
        "recommendation": recommendation,
        "maneuvers": tactical_maneuvers,
        "fuel_cost": f"₹{fuel_cost:.2f}",
        "coords": coords,
        "nav_link": generate_maps_navigation_url(source, destination, mode)
    }

def construct_jarvis_intelligence_brief():
    source, destination, base_offset = parse_trigger_message(TRIGGER_MESSAGE)
    
    car_profile = profile_predictive_engine(source, destination, base_offset, "driving")
    bike_profile = profile_predictive_engine(source, destination, base_offset, "two_wheeler")
    
    source_aqi, dest_aqi = "N/A", "N/A"
    active_profile = car_profile or bike_profile
    if active_profile and 'coords' in active_profile:
        c = active_profile['coords']
        source_aqi = get_aqi_metrics(c['start_lat'], c['start_lon'])
        dest_aqi = get_aqi_metrics(c['end_lat'], c['end_lon'])

    timestamp = get_ist_time()
    brief = [
        f"🤖 *JARVIS FLIGHT PLAN SYSTEM — SYNC_{timestamp}*",
        f"🗺️ *Route Vector:* {source} ➔ {destination}",
        f"😷 *Air Quality Index:* Source: {source_aqi} | Dest: {dest_aqi}",
        "============================="
    ]
    
    if car_profile:
        brief.extend([
            f"🚗 *CAR MODULE PROFILE [{car_profile['via']}]*",
            f"• ⏱️ ETA at Destination: `{car_profile['current_eta']}` | Range: {car_profile['distance']}",
            f"• ⛽ Estimated Fuel Cost: *{car_profile['fuel_cost']}*",
            f"• 🔮 10-Min Window Forecast: {car_profile['trend']}",
            f"• 💡 Tactical Guidance: {car_profile['recommendation']}",
            f"📍 *Initial Turns:* \n  1. {car_profile['maneuvers'][0] if len(car_profile['maneuvers']) > 0 else 'Proceed'}\n  2. {car_profile['maneuvers'][1] if len(car_profile['maneuvers']) > 1 else 'Proceed'}",
            f"🔗 *Launch Shortest Path Navigation:* {car_profile['nav_link']}",
            "-----------------------------"
        ])
        
    if bike_profile:
        brief.extend([
            f"🏍️ *BIKE MODULE PROFILE [{bike_profile['via']}]*",
            f"• ⏱️ ETA at Destination: `{bike_profile['current_eta']}` | Range: {bike_profile['distance']}",
            f"• ⛽ Estimated Fuel Cost: *{bike_profile['fuel_cost']}*",
            f"• 🔮 10-Min Window Forecast: {bike_profile['trend']}",
            f"• 💡 Tactical Guidance: {bike_profile['recommendation']}",
            f"📍 *Initial Turns:* \n  1. {bike_profile['maneuvers'][0] if len(bike_profile['maneuvers']) > 0 else 'Proceed'}\n  2. {bike_profile['maneuvers'][1] if len(bike_profile['maneuvers']) > 1 else 'Proceed'}",
            f"🔗 *Launch Shortest Path Navigation:* {bike_profile['nav_link']}"
        ])
        
    if not car_profile and not bike_profile:
        return f"⚠️ Tactical Error: Unable to extract navigation coordinates for standard route parameters."
        
    return "\n".join(brief)

def dispatch_brief(text):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    client.messages.create(from_=TWILIO_WHATSAPP_NUMBER, body=text, to=YOUR_CELL_NUMBER)

if __name__ == "__main__":
    briefing_payload = construct_jarvis_intelligence_brief()
    dispatch_brief(briefing_payload)
