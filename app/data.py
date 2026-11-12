import io, math, struct, wave, datetime as dt
from pathlib import Path
import pandas as pd
import requests
import streamlit as st
from src.shelters import find_shelters

ROOT = Path(__file__).resolve().parent.parent
LOG = ROOT / "data" / "processed" / "alert_log.csv"

@st.cache_data
def load_risk():
    df = pd.read_csv(ROOT / "data" / "processed" / "risk_map_2022.csv")
    if "pop_est" not in df.columns: df["pop_est"] = 0
    if "flood_frac" not in df.columns: df["flood_frac"] = 0.0
    df["pop_est"] = df.pop_est.fillna(0)
    return df

def nearest(df, lat, lon):
    return df.loc[((df.lat - lat) ** 2 + (df.lon - lon) ** 2).idxmin()]

@st.cache_data(ttl=600)
def weather(lat, lon):
    r = requests.get("https://api.open-meteo.com/v1/forecast", params={
        "latitude": lat, "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation",
        "daily": "precipitation_sum", "past_days": 7, "forecast_days": 7,
        "timezone": "Asia/Kolkata"}, timeout=20)
    r.raise_for_status()
    return r.json()

def rain_next3(w):
    vals = [x or 0 for x in w["daily"]["precipitation_sum"]]
    return round(sum(vals[7:10]), 1)   # index 7 = aaj

@st.cache_data(ttl=3600)
def shelters_near(lat, lon):
    return find_shelters(round(lat, 3), round(lon, 3))

@st.cache_data
def siren_wav():
    rate, buf = 22050, io.BytesIO()
    with wave.open(buf, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(rate)
        for i in range(rate * 3):
            fr = 600 + 400 * abs(math.sin(math.pi * i / rate))
            f.writeframes(struct.pack("<h", int(12000 * math.sin(2 * math.pi * fr * i / rate))))
    return buf.getvalue()

def log_alert(level, lat, lon, rain3, status):
    row = pd.DataFrame([{"time": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                         "level": level, "lat": lat, "lon": lon, "rain_3d_mm": rain3, "status": status}])
    row.to_csv(LOG, mode="a", header=not LOG.exists(), index=False)

def read_log():
    return pd.read_csv(LOG) if LOG.exists() else pd.DataFrame(
        columns=["time", "level", "lat", "lon", "rain_3d_mm", "status"])