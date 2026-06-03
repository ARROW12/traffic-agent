import os, re, requests
from datetime import datetime, timedelta
from twilio.rest import Client

# Configuration
MAPS_KEY = os.getenv("MAPS_API_KEY")
TWILIO_CLIENT = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
TRIGGER = os.getenv("TRIGGER_MESSAGE", "")

def get_fuel_price():
    try:
        res = requests.get("https://www.trinadhthatakula.com/fuelCheck/india/", timeout=5).json()
        for s in res:
            if s.get('state', '').lower() == 'telangana':
                return float(re.sub(r'[^\d.]', '', s.get('petrol', '115.73')))
    except: return 115.73

PETROL_PRICE = get_fuel_price()

def get_route_data(source, dest, mode, timestamp):
    """Fetches Google Maps data. Returns duration, distance, and coordinates."""
    params = {"origin": source, "destination": dest, "mode": mode, "departure_time": timestamp, "key": MAPS_KEY}
    res = requests.get("https://maps.googleapis.com/maps/api/directions/json", params=params).json()
    
    if res.get("status") == "OK":
        leg = res["routes"][0]["legs"][0]
        return {
            "dur": leg.get("duration_in_traffic", leg["duration"])["value"] / 60,
            "dist_val": leg["distance"]["value"] / 1000,
            "dist_txt": leg["distance"]["text"],
            "lat": leg["start_location"]["lat"], "lon": leg["start_location"]["lng"]
        }
    return None

def get_meteo(lat, lon):
    try:
        w = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code", timeout=5).json()["current"]
        a = requests.get(f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=us_aqi", timeout=5).json()["current"]
        alerts = []
        if w["weather_code"] in [51, 61, 80]: alerts.append("⚠️ Rain predicted.")
        if w["temperature_2m"] > 38: alerts.append("🔥 Heat advisory.")
        return f"{w['temperature_2m']}°C", f"{a['us_aqi']}", alerts
    except: return "N/A", "N/A", ["Weather data offline."]

def construct_brief():
    # Parse input from Twilio: "from [Source] to [Dest] in 0 mins"
    match = re.search(r'from\s+(.+?)\s+to\s+(.+?)\s+in', TRIGGER, re.IGNORECASE)
    s, d = (match.group(1).strip(), match.group(2).strip()) if match else ("Current Location", "Destination")
    
    now = int(datetime.utcnow().timestamp())
    future = int((datetime.utcnow() + timedelta(minutes=10)).timestamp())
    
    # CALCULATE PROFILES
    car_now = get_route_data(s, d, "driving", now)
    car_future = get_route_data(s, d, "driving", future)
    bike = get_route_data(s, d, "two-wheeler", now)
    
    temp, aqi, alerts = get_meteo(car_now['lat'], car_now['lon']) if car_now else ("N/A", "N/A", [])
    
    # PREDICTIVE TREND ANALYSIS
    trend = "Stable"
    if car_now and car_future:
        delta = car_future['dur'] - car_now['dur']
        trend = "📈 Building" if delta > 1 else ("📉 Clearing" if delta < -1 else "➡️ Stable")

    brief = [f"🤖 *JARVIS FLIGHT PLAN — {datetime.now().strftime('%I:%M %p')}*", f"🗺️ *Vector:* {s} ➔ {d}", f"🌡️ {temp} | 😷 AQI: {aqi}", "---"]
    
    # CAR PROFILE
    if car_now:
        fuel = (car_now['dist_val'] / 12) * PETROL_PRICE
        brief.append(f"🚗 *CAR:* {int(car_now['dur'])}m ({car_now['dist_txt']}) | Trend: {trend}")
        brief.append(f"⛽ *Est. Cost:* ₹{fuel:.2f}")
    
    # BIKE PROFILE
    if bike:
        fuel_bike = (bike['dist_val'] / 25) * PETROL_PRICE
        brief.append(f"🏍️ *BIKE:* {int(bike['dur'])}m ({bike['dist_txt']})")
        brief.append(f"⛽ *Est. Cost:* ₹{fuel_bike:.2f}")

    brief.extend(["---", "*ALERTS:* " + (", ".join(alerts) if alerts else "None")])
    return "\n".join(brief)

if __name__ == "__main__":
    TWILIO_CLIENT.messages.create(from_="whatsapp:+14155238886", body="\n".join(construct_brief()), to=os.getenv("YOUR_CELL_NUMBER"))
