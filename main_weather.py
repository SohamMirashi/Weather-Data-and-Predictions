from fastapi import FastAPI, Query, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import requests
from pymongo import MongoClient
from datetime import datetime
import os

# Optional: reuse MySQL models to validate user_id
from sqlalchemy.orm import Session
try:
    from database import SessionLocal  # from local project
    from models import User
except Exception:  # if not available, skip validation
    SessionLocal = None
    User = None

app = FastAPI()

# Allow frontend (HTML/JS) to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

APIkey = "c1a5392fbefd2b709742dd352902cb58"  

# ---- MongoDB connection ----
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "weather_app_backend")
mongo_client = MongoClient(MONGODB_URI)
mongo_db = mongo_client[MONGO_DB_NAME]
coordinates_collection = mongo_db["location"]
weather_data_collection = mongo_db["weather_data"]


def get_db():
    if SessionLocal is None:
        return None
    db = SessionLocal()
    try: 
        yield db
    finally:
        db.close()

# ---- Nominatim API ----
@app.get("/geocode/")
def get_coordinates(
    address: str = Query(..., description="Address to search"),
    user_id: int | None = Query(None, description="Optional user id to link with MySQL user"),
    minimal: bool | None = Query(False, description="If true, return only the display_name"),
    db: Session | None = Depends(get_db),
):
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={address}"
    response = requests.get(url, headers={"User-Agent": "weather-app"})
    data = response.json()
    if len(data) == 0:
        return {"error": "No results found"}
    result = {
        "lat": data[0]["lat"],
        "lon": data[0]["lon"],
        "display_name": data[0]["display_name"],
    }

    # Optional MySQL user validation
    if user_id is not None and db is not None and User is not None:
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=400, detail="Invalid user_id")

    # Persist to MongoDB (coordinates collection)
    try:
        coordinates_collection.insert_one({
            "user_id": user_id,
            "address": address,
            "display_name": result["display_name"], 
            "coordinates": {"lat": result["lat"], "lon": result["lon"]},
            "provider": "nominatim",
            "created_at": datetime.utcnow(),
        })
    except Exception:
        # Non-fatal if MongoDB is unreachable
        pass

    if minimal:
        return {"display_name": result["display_name"]}
    return result

# ---- OpenWeather API ----
@app.get("/weather/")
def get_weather( 
    lat: float,
    lon: float,
    address: str | None = Query(None, description="Optional address context"),
    user_id: int | None = Query(None, description="Optional user id to link with MySQL user"),
    db: Session | None = Depends(get_db),
):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={APIkey}&units=metric"
    response = requests.get(url)
    data = response.json()
    
    if "error" in data or data.get("cod") != 200:
        return {"error": "Failed to fetch weather data"}
    
    # Process the weather data to match frontend expectations
    weather_description = data["weather"][0]["description"].title()
    weather_main = data["weather"][0]["main"].lower() 
    temperature = round(data["main"]["temp"])
    feels_like = round(data["main"]["feels_like"])
    humidity = data["main"]["humidity"]
    cloudiness = data["clouds"]["all"]
    wind_speed = data["wind"]["speed"]

    visibility = data.get("visibility")
    if visibility:
        visibility = visibility / 1000  
    else:
        visibility = 10  
    
    # Determine weather condition type (prioritize precipitation/storm conditions)
    weather_type = "Unknown"
    desc_lower = weather_description.lower()
    
    if "thunderstorm" in desc_lower or weather_main == "thunderstorm":
        weather_type = "⛈️ Thunderstorm"
    elif "snow" in desc_lower or weather_main == "snow":
        weather_type = "❄️ Snowy"
    elif "rain" in desc_lower or weather_main == "rain":
        weather_type = "🌧️ Rainy"
    elif "drizzle" in desc_lower:
        weather_type = "🌦️ Drizzle"
    elif "mist" in desc_lower or "fog" in desc_lower or weather_main in ["mist", "fog"]:
        weather_type = "🌫️ Foggy/Misty"
    elif weather_main in ["clear"] and cloudiness < 25:
        weather_type = "☀️ Sunny"
    elif cloudiness < 25:
        weather_type = "☀️ Mostly Sunny"
    elif cloudiness < 50:
        weather_type = "⛅ Partly Cloudy"
    elif cloudiness < 75:
        weather_type = "☁️ Cloudy"
    else:
        weather_type = "☁️ Overcast"
    
    # Add wind conditions
    if wind_speed > 15:
        weather_type += " & 💨 Windy"
    elif wind_speed > 8:
        weather_type += " & 🌬️ Breezy"
    
    advice = []
    
    travel_score = 0
    travel_recommendation = ""
    
    if 18 <= temperature <= 25:
        travel_score += 3
        advice.append(f"✅ Perfect temperature for travel ({temperature}°C) - ideal weather conditions!")
    elif 15 <= temperature <= 28:
        travel_score += 2
        advice.append(f"✅ Good temperature for travel ({temperature}°C) - comfortable weather.")
    elif 10 <= temperature < 15 or 28 < temperature <= 32:
        travel_score += 1
        advice.append(f"⚠️ Moderate temperature ({temperature}°C) - still travel-friendly but dress accordingly.")
    elif temperature < 10:
        travel_score -= 1
        advice.append(f"❄️ Cold weather ({temperature}°C) - pack warm clothes if traveling.")
    else:  
        travel_score -= 1
        advice.append(f"🔥 Hot weather ({temperature}°C) - stay hydrated and avoid peak sun hours.")
    
    # Weather condition scoring
    if weather_main in ["clear"] and cloudiness < 25:
        travel_score += 3
        advice.append("☀️ Clear sunny skies - perfect for outdoor activities and sightseeing!")
    elif weather_main == "rain" or "rain" in weather_description.lower():
        travel_score -= 2
        advice.append("🌧️ Rainy conditions - consider indoor activities or bring an umbrella.")
    elif weather_main == "snow" or "snow" in weather_description.lower():
        travel_score -= 2
        advice.append("❄️ Snowy weather - roads may be slippery, travel carefully.")
    elif weather_main == "thunderstorm":
        travel_score -= 3
        advice.append("⛈️ Thunderstorm warning - avoid outdoor activities and travel if possible.")
    elif cloudiness < 50:
        travel_score += 1
        advice.append("⛅ Partly cloudy - good weather for travel with some clouds.")
    else:
        travel_score += 0
        advice.append("☁️ Cloudy conditions - still suitable for travel but less sunny.")
    
    # Wind conditions
    if wind_speed > 15:
        travel_score -= 1
        advice.append("💨 Strong winds detected - be cautious if driving or engaging in outdoor activities.")
    elif wind_speed > 8:
        advice.append("🌬️ Breezy conditions - pleasant for most activities.")
    elif wind_speed < 5:
        travel_score += 1
        advice.append("🍃 Calm winds - very pleasant weather conditions.")
    
    # Humidity conditions
    if humidity > 80:
        travel_score -= 1
        advice.append("💧 High humidity - it may feel more uncomfortable, stay hydrated.")
    elif humidity < 30:
        advice.append("🌵 Low humidity - dry air, good for travel but drink plenty of water.")
    elif 40 <= humidity <= 60:
        travel_score += 1
        advice.append("✅ Comfortable humidity levels - ideal for travel.")
    
    # Visibility conditions
    if visibility < 1:
        travel_score -= 2
        advice.append("⚠️ Poor visibility - exercise extreme caution if driving or traveling.")
    elif visibility < 5:
        travel_score -= 1
        advice.append("🌫️ Reduced visibility - drive carefully.")
    
    # Overall travel recommendation
    if travel_score >= 5:
        travel_recommendation = "✅ Excellent weather for travel! Perfect conditions to visit this location."
    elif travel_score >= 3:
        travel_recommendation = "✅ Good weather for travel. Conditions are favorable."
    elif travel_score >= 1:
        travel_recommendation = "⚠️ Moderate weather - travel is possible but be prepared for conditions."
    elif travel_score >= -1:
        travel_recommendation = "⚠️ Challenging weather conditions - consider postponing travel if possible."
    else:
        travel_recommendation = "❌ Poor weather conditions - not recommended for travel at this time."
    
    advice.insert(0, travel_recommendation)
    advice.insert(1, f"🌤️ Current Weather: {weather_type}")
    
    result = {
        "weather_description": weather_description,
        "weather_type": weather_type,  # Added for better display
        "temperature": temperature,
        "feels_like": feels_like,
        "humidity": humidity,
        "cloudiness": cloudiness,
        "wind_speed": wind_speed,
        "travel_recommendation": travel_recommendation,  # Added travel recommendation
        "advice": advice
    }

    # Optional MySQL user validation
    if user_id is not None and db is not None and User is not None:
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=400, detail="Invalid user_id")

    # Persist to MongoDB (weather_data collection)
    try:
        weather_data_collection.insert_one({
            "user_id": user_id,
            "address": address,
            "coordinates": {"lat": lat, "lon": lon},
            "provider": "openweathermap",
            "summary": result,  # convenient structured summary for UI/reporting
            "raw": data,        # full JSON from OpenWeatherMap as requested
            "created_at": datetime.utcnow(),
        })
    except Exception:
        pass

    return result

