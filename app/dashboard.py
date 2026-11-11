import sys, io, wave, math, struct
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # project root

import pandas as pd
import requests
import streamlit as st
import folium
from streamlit_folium import st_folium
from src.shelters import find_shelters
from src.alerts import build_message, send_telegram

st.set_page_config(page_title="JalRakshak", layout="wide")
st.title("JalRakshak: Flood Susceptibility, Live Weather and Alerts")
st.caption("Research prototype. Official warnings ke liye IMD / OSDMA follow karo.")

@st.cache_data
def load_risk():
    return pd.read_csv("data/processed/risk_map_2022.csv")

@st.cache_data(ttl=600)
def weather(lat, lon):
    r = requests.get("https://api.open-meteo.com/v1/forecast", params={
        "latitude": lat, "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation",
        "daily": "precipitation_sum", "forecast_days": 3, "timezone": "Asia/Kolkata"}, timeout=15)
    r.raise_for_status()
    return r.json()

@st.cache_data(ttl=3600)
def shelters_near(lat, lon):
    return find_shelters(round(lat, 3), round(lon, 3))

@st.cache_data
def siren_wav():
    rate, buf = 22050, io.BytesIO()
    with wave.open(buf, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(rate)
        for i in range(rate * 3):
            freq = 600 + 400 * abs(math.sin(math.pi * i / rate))   # upar-neeche siren
            f.writeframes(struct.pack("<h", int(12000 * math.sin(2 * math.pi * freq * i / rate))))
    return buf.getvalue()

risk = load_risk()
COLORS = {"Low": "#2ecc71", "Medium": "#f39c12", "High": "#e74c3c"}

st.sidebar.header("Location")
lat = st.sidebar.number_input("Latitude", 20.20, 20.90, 20.50, 0.01)
lon = st.sidebar.number_input("Longitude", 86.20, 87.00, 86.60, 0.01)
test_rain = st.sidebar.checkbox("Demo mode: heavy rain simulate karo")

cell = risk.loc(((risk.lat - lat) ** 2 + (risk.lon - lon) ** 2).idxmin()) if False else \
       risk.loc[((risk.lat - lat) ** 2 + (risk.lon - lon) ** 2).idxmin()]
level = cell["risk_level"]

rain3 = 0.0
col1, col2 = st.columns([2, 1])

with col2:
    st.subheader("Live weather")
    try:
        w = weather(lat, lon); cur = w["current"]
        st.metric("Temperature (C)", cur["temperature_2m"])
        st.metric("Humidity (%)", cur["relative_humidity_2m"])
        st.metric("Wind (km/h)", cur["wind_speed_10m"])
        rain3 = round(sum(x or 0 for x in w["daily"]["precipitation_sum"]), 1)
    except Exception as e:
        st.warning(f"Weather load nahi hua: {e}")
    if test_rain:
        rain3 = 150.0
    st.metric("Forecast rain, 3 days (mm)", rain3)

    st.subheader("Risk")
    st.markdown(f"**Susceptibility:** {level}")
    alert_on = level in ("High", "Medium") and rain3 >= 100
    if alert_on:
        st.error(f"{level}-risk area + heavy rain forecast. Safe jagah jaane ki taiyari rakho.")
        st.audio(siren_wav(), format="audio/wav")
    elif level == "High":
        st.warning("Flood-prone area. Abhi heavy rain forecast nahi hai.")
    else:
        st.success("Abhi koi alert nahi.")

    try:
        shelters = shelters_near(lat, lon)
    except Exception as e:
        shelters = []
        st.warning(f"Shelter data load nahi hua: {e}")

    st.subheader("Nearest shelters (OSM data)")
    for s in shelters:
        st.write(f"{s['name']} | {s['type']} | {s['dist_km']} km")

    if st.button("Telegram alert bhejo"):
        try:
            send_telegram(build_message(level, rain3, shelters))
            st.success("Alert bhej diya.")
        except Exception as e:
            st.error(f"Alert fail: {e}")

with col1:
    m = folium.Map(location=[lat, lon], zoom_start=10)
    for _, r in risk[risk.risk_level != "Low"].iterrows():
        folium.CircleMarker([r.lat, r.lon], radius=3, color=COLORS[r.risk_level],
                            fill=True, fill_opacity=0.6, weight=0).add_to(m)
    for s in shelters:
        folium.Marker([s["lat"], s["lon"]], tooltip=f"{s['name']} ({s['type']})",
                      icon=folium.Icon(color="blue", icon="home")).add_to(m)
    folium.Marker([lat, lon], tooltip="Aap yahan", icon=folium.Icon(color="red")).add_to(m)
    st_folium(m, height=550, use_container_width=True)