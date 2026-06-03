import os
import re
import requests
from twilio.rest import Client
from datetime import datetime, timedelta

# Environment configurations
GOOGLE_MAPS_API_KEY = os.getenv("MAPS_API_KEY") or os.getenv("GOOGLE_MAPS_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
YOUR_CELL_NUMBER = os.getenv("YOUR_CELL_NUMBER")
TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886"

HOME_ADDRESS = os.getenv("HOME_ADDRESS")
OFFICE_ADDRESS = os.getenv("OFFICE_ADDRESS")

def clean_html(raw_html):
    """Strips HTML tags from Google Maps navigation instructions."""
    clean_re = re.compile('<.*?>')
    return re.sub(clean_re, '', raw_html)

def get_weather_summary():
    """Fetches real-time weather and air safety updates."""
    # Using a reliable free open-data endpoint for weather integration
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude=26.7606&longitude=83.3731&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m"
        res = requests.get(url).json()
        current = res.get("current", {})
        temp = current.get("temperature_2m", "N/A")
        precip = current.get("precipitation", 0)
        
        condition = "Clear ☀️" if precip == 0 else "Rain Warning 🌧️ (Expect slippery roads)"
        return f"{temp}°C, {condition}"
    except Exception:
        return "Weather service momentarily unreachable."

def analyze_route_variant(mode):
    """Fetches navigation, turn insights, and computes traffic trends for a specific mode."""
    # Current Real-Time Fetch
    base_url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": HOME_ADDRESS,
        "destination": OFFICE_ADDRESS,
        "mode": mode,
        "departure_time": "now",
        "key": GOOGLE_MAPS_API_KEY
    }
    
    try:
        response = requests.get(base_url, params=params).json()
        if response.get("status") != "OK":
            return None
            
        route = response["routes"][0]
        leg = route["legs"][0]
        
        # Primary Route Name Identification
        summary_via = route.get("summary", "Primary Route")
        distance = leg["distance"]["text"]
        duration_normal = leg["duration"]["value"] # in seconds
        duration_traffic = leg.get("duration_in_traffic", leg["duration"])["value"]
        duration_traffic_text = leg.get("duration_in_traffic", leg["duration"])["text"]
        
        # Turn-by-Turn Processing (Extracting first 3 vital maneuvers)
        maneuvers = []
        for step in leg["steps"][:3]:
            instruction = clean_html(step.get("html_instructions", ""))
            maneuvers.append(f"• {instruction}")
        navigation_brief = "\n".join(maneuvers)
        
        # Algorithmic Traffic Density Calculation
        # TDI > 1.3 indicates severe congestion relative to free-flow capacity
        tdi = round(duration_traffic / duration_normal, 2)
        if tdi <= 1.05:
            density_status = "Fluid/Green 🟩"
        elif tdi <= 1.25:
            density_status = "Moderate Volumne 🟨"
        else:
            density_status = "Heavy Congestion / Bottleneck 🟥"
            
        # Predictive Trend Modeling (Looking forward 30 minutes to capture the slope)
        future_time = int((datetime.utcnow() + timedelta(minutes=30)).timestamp())
        params["departure_time"] = str(future_time)
        future_response = requests.get(base_url, params=params).json()
        
        trend_msg = "Stable ➡️"
        if future_response.get("status") == "OK":
            f_leg = future_response["routes"][0]["legs"][0]
            f_duration = f_leg.get("duration_in_traffic", f_leg["duration"])["value"]
            delta = f_duration - duration_traffic
            if delta < -120: # Saves more than 2 mins by waiting
                trend_msg = "Clearing Up Soon 📉 (Highly advise waiting 15-20 mins)"
            elif delta > 120:
                trend_msg = "Intensifying 📈 (Leave immediately to beat congestion)"

        return {
            "via": summary_via,
            "distance": distance,
            "time": duration_traffic_text,
            "density": density_status,
            "trend": trend_msg,
            "steps": navigation_brief
        }
    except Exception as e:
        return None

def generate_ai_commute_report():
    weather = get_weather_summary()
    car_data = analyze_route_variant("driving")
    bike_data = analyze_route_variant("two_wheeler")
    
    timestamp = datetime.now().strftime("%I:%M %p")
    
    report = [
        f"🤖 *TRAFFIC AGENT INTEL — {timestamp}*",
        f"🌍 *Environmental Matrix:* {weather}",
        "═" * 25
    ]
    
    if car_data:
        report.extend([
            f"🚗 *CAR COMMUTE PROFILE (Via {car_data['via']}):*",
            f"• ⏱️ ETA: `{car_data['time']}` ({car_data['distance']})",
            f"• 📊 Congestion Level: {car_data['density']}",
            f"• 🔮 Forecast Trajectory: {car_data['trend']}",
            f"📍 *Initial Navigation Vectors:* \n{car_data['steps']}",
            "─" * 20
        ])
        
    if bike_data:
        report.extend([
            f"🏍️ *BIKE COMMUTE PROFILE (Via {bike_data['via']}):*",
            f"• ⏱️ ETA: `{bike_data['time']}` ({bike_data['distance']})",
            f"• 📊 Congestion Level: {bike_data['density']}",
            f"• 🔮 Forecast Trajectory: {bike_data['trend']}",
            f"📍 *Initial Navigation Vectors:* \n{bike_data['steps']}"
        ])
        
    if not car_data and not bike_data:
        return "⚠️ Unable to isolate mapping data vectors. Verify endpoint restrictions."
        
    return "\n".join(report)

def send_whatsapp_message(text):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    client.messages.create(from_=TWILIO_WHATSAPP_NUMBER, body=text, to=YOUR_CELL_NUMBER)

if __name__ == "__main__":
    report = generate_ai_commute_report()
    send_whatsapp_message(report)
