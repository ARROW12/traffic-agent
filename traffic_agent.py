import os
import re
import requests
from datetime import datetime, timedelta
from twilio.rest import Client

# Configuration Boundaries
GOOGLE_MAPS_API_KEY = os.getenv("MAPS_API_KEY") or os.getenv("GOOGLE_MAPS_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
YOUR_CELL_NUMBER = os.getenv("YOUR_CELL_NUMBER")
TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886"

# Direct location inputs from Twilio (no LLM needed)
SOURCE_LOCATION = os.getenv("SOURCE_LOCATION", os.getenv("HOME_ADDRESS"))
DESTINATION_LOCATION = os.getenv("DESTINATION_LOCATION", os.getenv("OFFICE_ADDRESS"))

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

def get_ist_time():
    """Converts server runtime clock to Indian Standard Time (IST)."""
    return (datetime.utcnow() + timedelta(hours=5, minutes=30)).strftime("%I:%M:%S %p")

def get_weather_metrics(lat, lon):
    """Fetches real-time temperature and weather conditions based on coordinates."""
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code"
        res = requests.get(url, timeout=5).json()
        temp = res["current"]["temperature_2m"]
        code = res["current"]["weather_code"]
        
        # Map WMO weather codes to visual descriptors
        if code == 0: desc = "Clear ☀️"
        elif code in [1, 2, 3]: desc = "Partly Cloudy ⛅"
        elif code in [45, 48]: desc = "Foggy 🌫️"
        elif code in [51, 53, 55, 56, 57]: desc = "Drizzle 🌧️"
        elif code in [61, 63, 65, 66, 67]: desc = "Rain ☔"
        elif code in [71, 73, 75, 77]: desc = "Snow ❄️"
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

def generate_maps_navigation_url(coords, mode):
    """Generates a Google Maps navigation link for the given coordinates and mode."""
    start_lat, start_lon = coords.get('start_lat'), coords.get('start_lon')
    end_lat, end_lon = coords.get('end_lat'), coords.get('end_lon')
    gmaps_mode = "driving" if mode == "driving" else "two-wheeler"
    return f"https://www.google.com/maps/dir/?api=1&origin={start_lat},{start_lon}&destination={end_lat},{end_lon}&travelmode={gmaps_mode}"

def profile_predictive_engine(source, destination, mode):
    """Samples forward vectors and computes real-time regression curves."""
    base_url = "https://maps.googleapis.com/maps/api/directions/json"
    intervals = [0, 10, 30]  # Now, +10min, +30min
    sampled_durations = []
    
    primary_via = "Standard Route"
    distance_km = 0.0
    distance_str = "N/A"
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

    mileage = 12.0 if mode == "driving" else 25.0
    fuel_cost = (distance_km / mileage) * PETROL_PRICE_HYD
    
    delta_10 = sampled_durations[1] - sampled_durations[0]
    if delta_10 > 0.5:
        immediate_trend = f"Building 📈 (+{int(delta_10)}m if you wait 10m)"
        recommendation = "Depart immediately to outrun peak gridlock build-up."
    elif delta_10 < -0.5:
        immediate_trend = f"Clearing 📉 (-{int(abs(delta_10))}m if you wait 10m)"
        recommendation = "Hold position. Bottleneck patterns are currently dissolving."
    else:
        immediate_trend = "Stable ➡️"
        recommendation = "Traffic is consistent. Proceed at your discretion."

    return {
        "via": primary_via,
        "distance": distance_str,
        "current_eta": f"{int(sampled_durations[0])} mins",
        "trend": immediate_trend,
        "recommendation": recommendation,
        "fuel_cost": f"₹{fuel_cost:.2f}",
        "coords": coords,
        "nav_link": generate_maps_navigation_url(coords, mode)
    }

def construct_jarvis_intelligence_brief():
    """Assembles all data sub-systems into a clean character-optimized brief."""
    # Use direct location inputs from Twilio (no parsing needed)
    source = SOURCE_LOCATION
    destination = DESTINATION_LOCATION
    
    car_profile = profile_predictive_engine(source, destination, "driving")
    bike_profile = profile_predictive_engine(source, destination, "two-wheeler")
    
    source_aqi, dest_aqi, vector_weather = "N/A", "N/A", "N/A"
    active_profile = car_profile or bike_profile
    
    if active_profile and 'coords' in active_profile:
        c = active_profile['coords']
        source_aqi = get_aqi_metrics(c['start_lat'], c['start_lon'])
        dest_aqi = get_aqi_metrics(c['end_lat'], c['end_lon'])
        vector_weather = get_weather_metrics(c['start_lat'], c['start_lon'])

    # Format the source/dest cleanly (e.g. Title Case)
    display_source = str(source).title()
    display_dest = str(destination).title()
    timestamp = get_ist_time()
    
    brief = [
        f"🤖 *JARVIS FLIGHT PLAN SYSTEM — SYNC_{timestamp}*",
        f"🗺️ *Vector:* {display_source} ➔ {display_dest}",
        f"🌡️ *Weather:* {vector_weather}",
        f"😷 *AQI:* Source: {source_aqi} | Dest: {dest_aqi}",
        "============================="
    ]
    
    if car_profile:
        brief.extend([
            f"🚗 *CAR SYSTEM PROFILE [{car_profile['via']}]*",
            f"• ⏱️ ETA: `{car_profile['current_eta']}` | Range: {car_profile['distance']}",
            f"• ⛽ Fuel Cost: *{car_profile['fuel_cost']}* (Live Price: ₹{PETROL_PRICE_HYD:.2f}/L)",
            f"• 🔮 10-Min Trend: {car_profile['trend']}",
            f"• 💡 Vector Strategy: {car_profile['recommendation']}",
            f"🔗 *Launch Navigation:* {car_profile['nav_link']}",
            "-----------------------------"
        ])
        
    if bike_profile:
        brief.extend([
            f"🏍️ *BIKE SYSTEM PROFILE [{bike_profile['via']}]*",
            f"• ⏱️ ETA: `{bike_profile['current_eta']}` | Range: {bike_profile['distance']}",
            f"• ⛽ Fuel Cost: *{bike_profile['fuel_cost']}* (Live Price: ₹{PETROL_PRICE_HYD:.2f}/L)",
            f"• 🔮 10-Min Trend: {bike_profile['trend']}",
            f"• 💡 Vector Strategy: {bike_profile['recommendation']}",
            f"🔗 *Launch Navigation:* {bike_profile['nav_link']}"
        ])
        
    if not car_profile and not bike_profile:
        return f"⚠️ Core Interface Failure: Target routing strings could not be resolved."
        
    return "\n".join(brief)

def dispatch_brief(text):
    """Transmits structural intelligence report to user endpoint."""
    if len(text) > 1550:
        text = text[:1500] + "\n\n⚠️ Payload truncated to meet text character safety buffers."
        
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    client.messages.create(from_=TWILIO_WHATSAPP_NUMBER, body=text, to=YOUR_CELL_NUMBER)

if __name__ == "__main__":
    briefing_payload = construct_jarvis_intelligence_brief()
    dispatch_brief(briefing_payload)
