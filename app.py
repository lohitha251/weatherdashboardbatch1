mport streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Weather App", page_icon="☀️")

WMO_codes = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partially cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snowfall",
    73: "Moderate snowfall",
    75: "Heavy snowfall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail"
}

def get_wmo(code):
    return WMO_codes.get(code, "Unknown weather condition")

def wind_direction(degree):
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    idx = int((degree / 45) % 8)
    return directions[idx]

# API calls
def geocode(city):
    r = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={
            "name": city,
            "count": 5,
            "language": "en",
            "format": "json"
        },
        timeout=8,
    )
    r.raise_for_status()
    return r.json().get("results", [])

def fetch_weather(lat, lon):
    r = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m,wind_direction_10m,precipitation,weather_code",
            "hourly": "temperature_2m,precipitation_probability",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
            "timezone": "auto",
            "forecast_days": 7,
        },
        timeout=8,
    )
    r.raise_for_status()
    return r.json()

# UI Components
st.title("☀️ Weather App Dashboard")
st.caption("Get current weather and 7-day forecast for any city in the world.")

city = st.text_input("Enter city name", placeholder="e.g. London, Paris, New York")
unit = st.radio("Select temperature unit", ("Celsius", "Fahrenheit"), horizontal=True)

if not city:
    st.info("Please enter a city name to get weather information.")
    st.stop()

# Get location data
with st.spinner("Fetching location data..."):
    try:
        locations = geocode(city)
    except Exception as e:
        st.error(f"Geocode Failed: {e}")
        st.stop()

if not locations:
    st.warning("No locations found. Please check city name.")
    st.stop()

# Create readable location options
options = [f"{r['name']}, {r.get('admin1', '')}, {r['country']}" for r in locations]

# Let user select location directly
selected_option = st.selectbox("Select correct location", options)

# Find selected location
selected_index = options.index(selected_option)
loc = locations[selected_index]

lat = loc["latitude"]
lon = loc["longitude"]
city_name = loc["name"]
country = loc.get("country", "Unknown")

# Fetch weather data
with st.spinner("Fetching weather data..."):
    try:
        data = fetch_weather(lat, lon)
    except Exception as e:
        st.error(f"Weather API Failed: {e}")
        st.stop()

current = data.get("current", {})
daily = data.get("daily", {})

temp = current.get("temperature_2m", 0)
feels_like = current.get("apparent_temperature", 0)
humidity = current.get("relative_humidity_2m", 0)
wind_speed = current.get("wind_speed_10m", 0)
wind_dir = current.get("wind_direction_10m", 0)
precipitation = current.get("precipitation", 0)
weather_code = current.get("weather_code", -1)

# Convert units if needed
if unit == "Fahrenheit":
    temp = (temp * 9/5) + 32
    feels_like = (feels_like * 9/5) + 32
    temp_unit = "°F"
else:
    temp_unit = "°C"

# Current weather display
st.subheader(f"Current Weather in {city_name}, {country}")

c1, c2, c3 = st.columns(3)

with c1:
    st.metric("Temperature", f"{temp:.1f}{temp_unit}")
    st.metric("Feels Like", f"{feels_like:.1f}{temp_unit}")

with c2:
    st.metric("Humidity", f"{humidity}%")
    st.metric("Precipitation", f"{precipitation} mm")

with c3:
    st.metric("Wind Speed", f"{wind_speed} km/h")
    st.metric("Wind Direction", wind_direction(wind_dir))

st.success(f"Condition: {get_wmo(weather_code)}")

# 7-Day Forecast
st.subheader("7-Day Forecast")

max_temps = daily.get("temperature_2m_max", [])
min_temps = daily.get("temperature_2m_min", [])

# Convert forecast temperatures if Fahrenheit selected
if unit == "Fahrenheit":
    max_temps = [(t * 9/5) + 32 for t in max_temps]
    min_temps = [(t * 9/5) + 32 for t in min_temps]

forecast_data = {
    "Day": [f"Day {i+1}" for i in range(len(max_temps))],
    "Max Temp": max_temps,
    "Min Temp": min_temps
}

st.line_chart(data=forecast_data, x="Day", y=["Max Temp", "Min Temp"])
