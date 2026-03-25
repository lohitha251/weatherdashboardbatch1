import streamlit as st
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
'''
geocode api : to get the latitude and longitude of the city
open meteo api : to get the weather data of the city
'''

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
with st.spinner("Fetching location data....."):
    try:
        locations=geocode(city)
    except Exception as e:
        st.error(f"Geocode Failed: {e}")
        st.stop()
if not locations:
    st.warning("No locations found Please check city name ")
    st.stop()
options=[f"{r['name']},{r.get('admin1','')},{r['country']}" for r in locations]
chosen_ind=st.selectbox("Select correct location",range(len(options)),format_func=lambda x:options[x])
loc=locations[chosen_ind]