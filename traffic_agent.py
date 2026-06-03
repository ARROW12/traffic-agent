import os
import re
import json
import requests
import numpy as np
from datetime import datetime, timedelta
from twilio.rest import Client

# Configuration Boundaries
GOOGLE_MAPS_API_KEY = os.getenv("MAPS_API_KEY") or os.getenv("GOOGLE_MAPS_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
YOUR_CELL_NUMBER = os.getenv("YOUR_CELL_NUMBER")
TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886"

# Hugging Face Free Inference Config
HF_TOKEN = os.getenv("HF_TOKEN")
HF_API_URL = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct"

DEFAULT_HOME = os.getenv("HOME_ADDRESS")
DEFAULT_OFFICE = os.getenv("OFFICE_ADDRESS")
TRIGGER_MESSAGE = os.getenv("TRIGGER_MESSAGE", "")

def get_live_petrol_price():
    """Fetches the live daily petrol price for Telangana/Hyderabad from an open API endpoint."""
    fallback_price = 115.73 # Standard historical baseline if API fails
    try:
        url = "https://www.trinadhthatakula.com/fuelCheck/india/"
        response = requests.get(url, timeout=10)
        
        # The API returns a list of dictionaries. We need to find Telangana.
        if response.status_code == 200:
            data = response.json()
            for state_data in data:
                if state_data.get('state', '').lower() == 'telangana':
                    # Extract the petrol price and convert to float
                    price_str = state_data.get('petrol', str(fallback_price))
                    # Clean up the string just in case it has currency symbols
                    clean_price = re.sub(r'[^\d.]', '', price_str)
                    return float(clean_price)
    except Exception as e:
        print(f"Failed to fetch live petrol price: {e}. Using fallback.")
        
    return fallback_price

# Fetch dynamic localized price baseline for Hyderabad, Telangana
PETROL_PRICE_HYD = get_live_petrol_price()

def parse_trigger_message_with_llm(msg):
    """Uses a free serverless LLM to extract source, destination, and timing offsets into a clean dictionary."""
    if not msg or len(msg.strip()) < 10:
        return DEFAULT_HOME, DEFAULT_OFFICE, 0

    system_prompt = (
        "You are a precise data extraction assistant. Your task is to extract navigation routing details "
        "from a user's text message. You must output exactly a JSON dictionary with these keys: "
        "'source' (string or null), 'destination' (string or null), and 'offset_minutes' (integer or 0).\n"
        "Rules:\n"
        "1. Extract the starting point into 'source' and the destination building/area into 'destination'.\n"
        "2. Extract relative time frames (like 'in 30 mins' or 'after 15 minutes') into 'offset_minutes' as a pure integer.\n"
        "3. Do NOT include conversational words like 'can you share', 'please', or 'in 30 mins' inside the source or destination names.\n"
        "4. Return ONLY valid raw JSON. No markdown wrappers, no explanations."
    )

    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {
        "inputs": f"<|system|>\n{system_prompt}\n<|user|>\nInput text: \"{msg}\"\n<|assistant|>\n",
        "parameters": {"max_new_tokens": 150, "temperature": 0.1}
    }

    try:
        response = requests.post(HF_API_URL, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            raw_output = response.json()[0]['generated_text']
            
            json_match = re.search(r'\{.*?\}', raw_output, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                
                source = data.get("source") or DEFAULT_HOME
                destination = data.get("destination") or DEFAULT_OFFICE
                offset = int(data.get("offset_minutes", 0))
                
                return source, destination, offset
    except Exception as e:
        print(f"LLM parsing failed or timed out: {e}. Falling back to default secrets.")
        
    return DEFAULT_HOME, DEFAULT_OFFICE, 0

def get_ist_time():
    """Converts server runtime clock to Indian Standard Time (IST)."""
    return (datetime.utcnow() + timedelta(hours=5, minutes=30)).strftime("%I:%M:%S %p")

def get_aqi_metrics(lat, lon):
    """Fetches localized real-time US-AQI index ratings."""
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

def generate_maps_navigation_url(coords, mode):
    """Generates standard universal deep links using precise coordinates to guarantee mobile resolution."""
    start_lat = coords.get('start_lat')
    start_lon = coords.get('start_lon')
    end_lat = coords.get('end_lat')
    end_lon = coords.get('end_lon')
    
    gmaps_mode = "driving" if mode == "driving" else "two-wheeler"
    return f"https://www.google.com/maps/dir/?api=1&origin={start_lat},{start_lon}&destination={end_lat},{end_lon}&travelmode={gmaps_mode}"

def profile_predictive_engine(source, destination, base_offset, mode):
    """Samples forward vectors and computes real-time regression curves."""
    base_url = "https://maps.googleapis.com/maps/api/directions/json"
    intervals = [base_offset, base_offset + 10, base_offset + 30]
    sampled_durations = []
    
    primary_via = "Standard Route"
    distance_km = 0.0
    distance_str = "N/A"
    resolved_source = source
    resolved_destination = destination
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
                    resolved_source = leg.get("start_address", source)
                    resolved_destination = leg.get("end_address", destination)
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

    # Calculate precise fuel consumption expenses using the LIVE petrol price
    mileage = 12.0 if mode == "driving" else 25.0
    fuel_cost = (distance_km / mileage) * PETROL_PRICE_HYD
    
    # Delta optimization matrix
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
        "resolved_source": resolved_source,
        "resolved_destination": resolved_destination,
        "current_eta": f"{int(sampled_durations[0])} mins",
        "trend": immediate_trend,
        "recommendation": recommendation,
        "fuel_cost": f"₹{fuel_cost:.2f}",
        "coords": coords,
        "nav_link": generate_maps_navigation_url(coords, mode)
    }

def construct_jarvis_intelligence_brief():
    """Assembles all data sub-systems into a clean character-optimized brief."""
    source, destination, base_offset = parse_trigger_message_with_llm(TRIGGER_MESSAGE)
    
    car_profile = profile_predictive_engine(source, destination, base_offset, "driving")
    bike_profile = profile_predictive_engine(source, destination, base_offset, "two_wheeler")
    
    source_aqi, dest_aqi = "N/A", "N/A"
    active_profile = car_profile or bike_profile
    
    display_source = active_profile["resolved_source"] if active_profile else source
    display_dest = active_profile["resolved_destination"] if active_profile else destination
    
    if active_profile and 'coords' in active_profile:
        c = active_profile['coords']
        source_aqi = get_aqi_metrics(c['start_lat'], c['start_lon'])
        dest_aqi = get_aqi_metrics(c['end_lat'], c['end_lon'])

    timestamp = get_ist_time()
    brief = [
        f"🤖 *JARVIS FLIGHT PLAN SYSTEM — SYNC_{timestamp}*",
        f"🗺️ *Vector:* {display_source} ➔ {display_dest}",
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
