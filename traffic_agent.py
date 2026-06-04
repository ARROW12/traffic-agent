import os
import re
import requests
import json
from datetime import datetime, timedelta
from twilio.rest import Client

# ==========================================
# 1. CONFIGURATION & CREDENTIALS
# ==========================================
GOOGLE_MAPS_API_KEY = os.getenv("MAPS_API_KEY") or os.getenv("GOOGLE_MAPS_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
YOUR_CELL_NUMBER = os.getenv("YOUR_CELL_NUMBER")
TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886"
OUTPUT_JSON = os.getenv("OUTPUT_JSON", "false").lower() == "true"

# Direct location inputs from Twilio
SOURCE_LOCATION = os.getenv("SOURCE_LOCATION", os.getenv("HOME_ADDRESS"))
DESTINATION_LOCATION = os.getenv("DESTINATION_LOCATION", os.getenv("OFFICE_ADDRESS"))

# ==========================================
# 2. DATA ACQUISITION SUBSYSTEMS
# ==========================================
def get_live_petrol_price():
    """Fetches the live daily petrol price for Telangana/Hyderabad from an open API endpoint."""
    fallback_price = 115.73 
    try:
        url = "https://www.trinadhthatakula.com/fuelCheck/india/"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            for state_data in data:
                if state_data.get('state', '').lower() == 'telangana':
                    price_str = state_data.get('petrol', str(fallback_price))
                    clean_price = re.sub(r'[^\d.]', '', price_str)
                    return float(clean_price)
    except Exception:
        pass
    return fallback_price

PETROL_PRICE_HYD = get_live_petrol_price()

def get_place_details(location_name):
    """Fetches place details like ratings and reviews."""
    try:
        url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
        params = {
            "input": location_name,
            "inputtype": "textquery",
            "key": GOOGLE_MAPS_API_KEY,
            "fields": "place_id,formatted_address,rating,user_ratings_total"
        }
        res = requests.get(url, params=params, timeout=5).json()
        if res.get("candidates"):
            place = res["candidates"][0]
            return {
                "name": place.get("formatted_address", location_name),
                "rating": place.get("rating", "N/A"),
                "reviews": place.get("user_ratings_total", 0)
            }
    except Exception:
        pass
    return {"name": location_name, "rating": "N/A", "reviews": 0}

def get_weather_metrics(lat, lon):
    """Fetches real-time temperature and weather conditions."""
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code"
        res = requests.get(url, timeout=5).json()
        temp = res["current"]["temperature_2m"]
        code = res["current"]["weather_code"]
        
        if code == 0: desc = "Clear ☀️"
        elif code in [1, 2, 3]: desc = "Partly Cloudy ⛅"
        elif code in [45, 48]: desc = "Foggy 🌫️"
        elif code in [51, 53, 55]: desc = "Drizzle 🌧️"
        elif code in [61, 63, 65]: desc = "Rain ☔"
        elif code in [80, 81, 82]: desc = "Showers 🌦️"
        elif code in [95, 96, 99]: desc = "Thunderstorm ⛈️"
        else: desc = "Unknown 🌤️"
        return f"{temp}°C, {desc}"
    except Exception:
        return "Offline"

def get_aqi_metrics(lat, lon):
    """Fetches localized real-time US-AQI index ratings."""
    try:
        url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=us_aqi"
        res = requests.get(url, timeout=5).json()
        aqi = res.get("current", {}).get("us_aqi", None)
        if aqi is None: return "N/A"
        if aqi <= 50: return f"{aqi} (Good 🟢)"
        elif aqi <= 100: return f"{aqi} (Moderate 🟡)"
        elif aqi <= 150: return f"{aqi} (Sensitive 🟠)"
        return f"{aqi} (Unhealthy 🔴)"
    except Exception:
        return "Offline"

# ==========================================
# 3. ROUTE PROCESSING & INCIDENT ENGINE
# ==========================================
def clean_html(raw_html):
    """Removes HTML brackets left behind by navigation metadata."""
    clean_text = re.sub(r'<[^<]+?>', ' ', raw_html)
    return re.sub(r'\s+', ' ', clean_text).strip()

def inspect_incidents(route_data):
    """Audits warnings and navigation lines for accidents, closures, and disruptions."""
    alerts = []
    for warning in route_data.get("warnings", []):
        alerts.append(f"⚠️ {warning}")
        
    for leg in route_data.get("legs", []):
        for step in leg.get("steps", []):
            instruction = clean_html(step.get("html_instructions", ""))
            if any(k in instruction.lower() for k in ["accident", "road closed", "blocked", "heavy traffic", "congestion", "gridlock"]):
                if len(instruction) > 65:
                    instruction = instruction[:62] + "..."
                alerts.append(f"🚨 {instruction}")
                
    return list(dict.fromkeys(alerts))[:3]

def detect_tolls(route_data):
    """Scans the route matrix to detect if a toll booth is present."""
    for warning in route_data.get("warnings", []):
        if "toll" in warning.lower():
            return True
            
    for leg in route_data.get("legs", []):
        for step in leg.get("steps", []):
            if "toll" in step.get("html_instructions", "").lower():
                return True
    return False

def generate_maps_navigation_url(coords, mode):
    """Generates official Google Maps mobile navigation intents."""
    if not coords: return "N/A"
    gmaps_mode = "driving" if mode == "driving" else "two-wheeler"
    return f"https://www.google.com/maps/dir/?api=1&origin={coords['start_lat']},{coords['start_lon']}&destination={coords['end_lat']},{coords['end_lon']}&travelmode={gmaps_mode}"

def process_route_object(route, mode):
    """Extracts measurements, flags incidents, detects tolls, and calculates fuel bounds."""
    leg = route["legs"][0]
    distance_km = leg["distance"]["value"] / 1000.0
    duration_str = leg.get("duration_in_traffic", leg["duration"])["text"]
    
    incidents = inspect_incidents(route)
    has_tolls = detect_tolls(route)
    
    # Custom Fuel Calculation Profiles
    mileage = 12.0 if mode == "driving" else 25.0
    cost = (distance_km / mileage) * PETROL_PRICE_HYD
    
    coords = {
        'start_lat': leg["start_location"]["lat"], 'start_lon': leg["start_location"]["lng"],
        'end_lat': leg["end_location"]["lat"], 'end_lon': leg["end_location"]["lng"]
    }
    
    return {
        "via": route.get("summary", "Standard Vector"),
        "distance": leg["distance"]["text"],
        "duration": duration_str,
        "fuel_cost": f"₹{cost:.2f}",
        "tolls": "Yes 💳" if has_tolls else "No 🆓",
        "alerts": incidents,
        "coords": coords,
        "nav_link": generate_maps_navigation_url(coords, mode)
    }

def profile_predictive_engine(source, destination, mode):
    """Samples data patterns across the area map, identifying alternative variants."""
    base_url = "https://maps.googleapis.com/maps/api/directions/json"
    now_timestamp = int(datetime.utcnow().timestamp())
    
    # We use "driving" for both map API requests to ensure highways route correctly, 
    # but the internal `mode` passed in applies bike math and URLs on our end.
    params = {
        "origin": source,
        "destination": destination,
        "mode": "driving", 
        "departure_time": str(now_timestamp),
        "alternatives": "true",
        "key": GOOGLE_MAPS_API_KEY
    }
    
    try:
        res = requests.get(base_url, params=params, timeout=8).json()
        if res.get("status") != "OK": return None
        
        routes_found = res["routes"]
        processed_routes = []
        
        for r in routes_found[:3]: 
            processed_routes.append(process_route_object(r, mode))
            
        if not processed_routes: return None
        
        # Trend mapping for the primary route
        future_timestamp = int((datetime.utcnow() + timedelta(minutes=10)).timestamp())
        params["alternatives"] = "false"
        params["departure_time"] = str(future_timestamp)
        
        trend_text = "Stable ➡️"
        strategy = "Traffic is consistent. Proceed at your discretion."
        
        future_res = requests.get(base_url, params=params, timeout=5).json()
        if future_res.get("status") == "OK":
            current_mins = res["routes"][0]["legs"][0].get("duration_in_traffic", res["routes"][0]["legs"][0]["duration"])["value"] / 60.0
            future_mins = future_res["routes"][0]["legs"][0].get("duration_in_traffic", future_res["routes"][0]["legs"][0]["duration"])["value"] / 60.0
            delta = future_mins - current_mins
            
            if delta > 1.0:
                trend_text = f"Building 📈 (+{int(delta)}m if you wait 10m)"
                strategy = "Depart immediately to outrun peak gridlock."
            elif delta < -1.0:
                trend_text = f"Clearing 📉 (-{int(abs(delta))}m if you wait 10m)"
                strategy = "Hold position. Bottlenecks are dissolving."

        processed_routes[0]["trend"] = trend_text
        processed_routes[0]["recommendation"] = strategy
        return processed_routes

    except Exception:
        return None

# ==========================================
# 4. REPORT COMPILATION & DISPATCH
# ==========================================
def get_ist_time():
    return (datetime.utcnow() + timedelta(hours=5, minutes=30)).strftime("%I:%M:%S %p")

def construct_jarvis_intelligence_brief():
    source = SOURCE_LOCATION
    destination = DESTINATION_LOCATION
    
    car_routes = profile_predictive_engine(source, destination, "driving")
    bike_routes = profile_predictive_engine(source, destination, "two-wheeler")
    
    source_aqi, dest_aqi, vector_weather = "N/A", "N/A", "N/A"
    active_profile = car_routes or bike_routes
    
    if active_profile and 'coords' in active_profile[0]:
        c = active_profile[0]['coords']
        source_aqi = get_aqi_metrics(c['start_lat'], c['start_lon'])
        dest_aqi = get_aqi_metrics(c['end_lat'], c['end_lon'])
        vector_weather = get_weather_metrics(c['start_lat'], c['start_lon'])

    display_source = str(source).title()
    display_dest = str(destination).title()
    timestamp = get_ist_time()
    
    brief = [
        f"🤖 *JARVIS FLIGHT PLAN — SYNC_{timestamp}*",
        f"🗺️ *Vector:* {display_source} ➔ {display_dest}",
        f"🌡️ *Weather:* {vector_weather} | 😷 *AQI:* S: {source_aqi} | D: {dest_aqi}",
        "============================="
    ]
    
    if car_routes:
        brief.append("🚗 *CAR SYSTEM OPTIONS:*")
        for i, r in enumerate(car_routes):
            prefix = "🏆 *Primary*" if i == 0 else f"⌥ *Alt Route {i}*"
            brief.append(f"{prefix} [Via {r['via']}]")
            brief.append(f" • ⏱️ Time: `{r['duration']}` | 📏 Dist: {r['distance']}")
            brief.append(f" • ⛽ Fuel: *{r['fuel_cost']}* (Live Price: ₹{PETROL_PRICE_HYD:.2f}/L) | 🛣️ Tolls: {r['tolls']}")
            if r['alerts']:
                brief.append(f" • {r['alerts'][0]}") 
            if i == 0:
                brief.append(f" • 🔮 Forecast: {r['trend']}")
                brief.append(f" • 💡 Strategy: {r['recommendation']}")
            brief.append(f" 🔗 *Nav:* {r['nav_link']}")
        brief.append("-----------------------------")
        
    if bike_routes:
        brief.append("🏍️ *BIKE SYSTEM OPTIONS:*")
        for i, r in enumerate(bike_routes):
            prefix = "🏆 *Primary*" if i == 0 else f"⌥ *Alt Route {i}*"
            brief.append(f"{prefix} [Via {r['via']}]")
            brief.append(f" • ⏱️ Time: `{r['duration']}` | 📏 Dist: {r['distance']}")
            brief.append(f" • ⛽ Fuel: *{r['fuel_cost']}* (Live Price: ₹{PETROL_PRICE_HYD:.2f}/L) | 🛣️ Tolls: {r['tolls']}")
            if r['alerts']:
                brief.append(f" • {r['alerts'][0]}")
            brief.append(f" 🔗 *Nav:* {r['nav_link']}")
        
    if not car_routes and not bike_routes:
        return f"⚠️ Core Interface Failure: Target routing strings could not be resolved."
    
    return "\n".join(brief)

def dispatch_brief(text):
    if len(text) > 1550:
        text = text[:1500] + "\n\n⚠️ Payload truncated to meet text safety buffers."
    
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        client.messages.create(from_=TWILIO_WHATSAPP_NUMBER, body=text, to=YOUR_CELL_NUMBER)
    except Exception as e:
        print(f"WhatsApp send failed: {str(e)}")

if __name__ == "__main__":
    briefing_payload = construct_jarvis_intelligence_brief()
    dispatch_brief(briefing_payload)
