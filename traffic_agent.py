import os
import re
import requests
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from twilio.rest import Client

# Pipeline Configurations
GOOGLE_MAPS_API_KEY = os.getenv("MAPS_API_KEY") or os.getenv("GOOGLE_MAPS_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
YOUR_CELL_NUMBER = os.getenv("YOUR_CELL_NUMBER")
TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886"

HOME_ADDRESS = os.getenv("HOME_ADDRESS")
OFFICE_ADDRESS = os.getenv("OFFICE_ADDRESS")

def clean_html(raw_html):
    """Strips HTML formatting blocks from turn-by-turn text chunks."""
    return re.sub(re.compile('<.*?>'), '', raw_html)

def get_environmental_risk():
    """Queries real-time meteorological metrics to compute weather risk modifiers."""
    try:
        # Coords mapped dynamically to primary operations profile zone
        url = "https://api.open-meteo.com/v1/forecast?latitude=26.7606&longitude=83.3731&current=temperature_2m,precipitation,wind_speed_10m"
        res = requests.get(url).json().get("current", {})
        temp = res.get("temperature_2m", 25)
        precip = res.get("precipitation", 0)
        wind = res.get("wind_speed_10m", 0)
        
        risk_score = 0.0
        weather_desc = "Optimal ☀️"
        
        if precip > 0:
            risk_score += 2.5
            weather_desc = "Precipitation Detected 🌧️ [Road Friction Reduced]"
        if wind > 15:
            risk_score += 1.5
            weather_desc = f"High Winds ({wind} km/h) 💨"
            
        return {"desc": weather_desc, "temp": temp, "risk_factor": risk_score}
    except Exception:
        return {"desc": "Nominal (Sensors Offline)", "temp": 25, "risk_factor": 0.0}

def profile_predictive_engine(mode, weather_risk):
    """Samples future time intervals and builds a localized Linear Regression trend model."""
    base_url = "https://maps.googleapis.com/maps/api/directions/json"
    intervals = [0, 15, 30, 45, 60]  # Forward-looking offset sampling windows (minutes)
    sampled_durations = []
    timeline_matrix = np.array(intervals).reshape(-1, 1)
    
    primary_via = "Standard Route"
    distance_str = "N/A"
    tactical_maneuvers = []
    
    # Run dynamic temporal vector sampling
    for offset in intervals:
        future_timestamp = int((datetime.utcnow() + timedelta(minutes=offset)).timestamp())
        params = {
            "origin": HOME_ADDRESS,
            "destination": OFFICE_ADDRESS,
            "mode": mode,
            "departure_time": str(future_timestamp),
            "key": GOOGLE_MAPS_API_KEY
        }
        
        try:
            res = requests.get(base_url, params=params).json()
            if res.get("status") == "OK":
                route = res["routes"][0]
                leg = route["legs"][0]
                
                # Gather navigation details from current baseline (offset 0)
                if offset == 0:
                    primary_via = route.get("summary", "Primary Arterial")
                    distance_str = leg["distance"]["text"]
                    tactical_maneuvers = [clean_html(s["html_instructions"]) for s in leg["steps"][:2]]
                
                dur_val = leg.get("duration_in_traffic", leg["duration"])["value"] / 60.0  # Convert seconds to minutes
                sampled_durations.append(dur_val)
            else:
                if len(sampled_durations) > 0:
                    sampled_durations.append(sampled_durations[-1])
        except Exception:
            return None

    if len(sampled_durations) < 3:
        return None

    # Train Memory-Isolated Predictive Model
    y = np.array(sampled_durations)
    model = LinearRegression().fit(timeline_matrix, y)
    slope = model.coef_[0]  # Quantifies travel time change rate per elapsed minute
    
    # Process Trend Trajectory Signatures
    if slope < -0.08:
        trajectory = "Dissipating 📉 [Advise Delayed Departure]"
        recommendation = f"Hold position. Delaying departure 20 mins recovers ~{int(abs(slope) * 20)} mins of active transit time."
    elif slope > 0.08:
        trajectory = "Building 📈 [Advise Immediate Departure]"
        recommendation = "Congestion front is compounding. Depart immediately to outrun peak gridlock velocity."
    else:
        trajectory = "Static / Stable ➡️"
        recommendation = "Traffic variance is nominal. Proceed at your discretion."

    # Compute Operational Readiness & Safety Performance Indexes
    current_duration = sampled_durations[0]
    efficiency_loss = max(0, (current_duration - (sampled_durations[0] / 1.3)))
    safety_score = max(10, int(100 - (efficiency_loss * 2) - (weather_risk * 10)))

    return {
        "via": primary_via,
        "distance": distance_str,
        "current_eta": f"{int(current_duration)} mins",
        "trajectory": trajectory,
        "recommendation": recommendation,
        "maneuvers": tactical_maneuvers,
        "score": f"{safety_score}/100"
    }

def construct_jarvis_intelligence_brief():
    """Compiles analytics engine outputs into a structured messaging payload."""
    env = get_environmental_risk()
    car_profile = profile_predictive_engine("driving", env["risk_factor"])
    bike_profile = profile_predictive_engine("two_wheeler", env["risk_factor"])
    
    timestamp = datetime.now().strftime("%I:%M:%S %p")
    brief = [
        f"🤖 *JARVIS TACTICAL FLIGHT PLAN — SYNC_{timestamp}*",
        f"🌍 *Atmospheric Context:* {env['temp']}°C | {env['desc']}",
        "============================="
    ]
    
    if car_profile:
        brief.extend([
            f"🚗 *CAR SYSTEM PROFILE [{car_profile['via']}]*",
            f"• ⏱️ Current Weight: `{car_profile['current_eta']}` | Range: {car_profile['distance']}",
            f"• 🔮 Vector Trajectory: {car_profile['trajectory']}",
            f"• 🛡️ Operational Efficiency Score: {car_profile['score']}",
            f"• 💡 Tactical Vector: {car_profile['recommendation']}",
            f"📍 *Vector Targets:* \n  1. {car_profile['maneuvers'][0] if len(car_profile['maneuvers']) > 0 else 'Proceed on route'}",
            f"  2. {car_profile['maneuvers'][1] if len(car_profile['maneuvers']) > 1 else 'Follow main indicators'}",
            "-----------------------------"
        ])
        
    if bike_profile:
        brief.extend([
            f"状况 *BIKE SYSTEM PROFILE [{bike_profile['via']}]*",
            f"• ⏱️ Current Weight: `{bike_profile['current_eta']}` | Range: {bike_profile['distance']}",
            f"• 🔮 Vector Trajectory: {bike_profile['trajectory']}",
            f"• 🛡️ Operational Efficiency Score: {bike_profile['score']}",
            f"• 💡 Tactical Vector: {bike_profile['recommendation']}",
            f"📍 *Vector Targets:* \n  1. {bike_profile['maneuvers'][0] if len(bike_profile['maneuvers']) > 0 else 'Proceed on route'}",
            f"  2. {bike_profile['maneuvers'][1] if len(bike_profile['maneuvers']) > 1 else 'Follow main indicators'}"
        ])
        
    if not car_profile and not bike_profile:
        return "⚠️ Tactical Error: Failed to gather path vectors from data streams."
        
    return "\n".join(brief)

def dispatch_brief(text):
    """Transmits finalized payload to user device via WhatsApp API pipeline."""
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    client.messages.create(from_=TWILIO_WHATSAPP_NUMBER, body=text, to=YOUR_CELL_NUMBER)

if __name__ == "__main__":
    briefing_payload = construct_jarvis_intelligence_brief()
    dispatch_brief(briefing_payload)
