import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import datetime as dt
import pandas as pd
import streamlit as st
from app.theme import header, disclaimer
from app.data import load_risk, weather, rain_next3

risk = load_risk()
header("Live Monitoring", "Latest weather at high-risk, high-population locations (Open-Meteo)")

# High-risk cells me se zyada population wale, ek-doosre se door 6 points
pts = risk[risk.risk_level == "High"].sort_values("pop_est", ascending=False).head(80)
sel = []
for _, r in pts.iterrows():
    if all(abs(r.lat - a) + abs(r.lon - b) > 0.12 for a, b in sel):
        sel.append((r.lat, r.lon))
    if len(sel) == 6:
        break

rows = []
for la, lo in sel:
    try:
        w = weather(la, lo)
        cur = w["current"]
        obs = dt.datetime.fromisoformat(cur["time"])
        age = int((dt.datetime.now() - obs).total_seconds() // 60)
        rows.append({
            "Location (lat, lon)": f"{la:.2f}, {lo:.2f}",
            "Temp (C)": cur["temperature_2m"],
            "Humidity (%)": cur["relative_humidity_2m"],
            "Wind (km/h)": cur["wind_speed_10m"],
            "Rain now (mm)": cur["precipitation"],
            "3-day forecast (mm)": rain_next3(w),
            "Observed at": cur["time"],
            "Freshness": "Fresh" if age < 60 else f"{age} min old",
        })
    except Exception as e:
        rows.append({"Location (lat, lon)": f"{la:.2f}, {lo:.2f}", "Freshness": f"Error: {str(e)[:50]}"})

df = pd.DataFrame(rows)

if df.empty:
    st.info("Koi data nahi mila.")
else:
    ok = df[df["Freshness"].astype(str).str.startswith(("Fresh", "min", "1", "2", "3", "4", "5", "6", "7", "8", "9"))]
    c1, c2, c3 = st.columns(3)
    c1.metric("Locations monitored", len(df))
    if "Humidity (%)" in df:
        c2.metric("Avg humidity (%)", round(df["Humidity (%)"].dropna().mean(), 1) if df["Humidity (%)"].notna().any() else "N/A")
    if "3-day forecast (mm)" in df:
        c3.metric("Max 3-day forecast (mm)", df["3-day forecast (mm)"].max())
    st.dataframe(df, use_container_width=True, hide_index=True)

st.caption("River water level: abhi available nahi (CWC ka live data chahiye). Roadmap page dekho.")
st.caption("Data source: Open-Meteo model data, ye official IMD observation nahi hai.")
disclaimer()