import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
from app.theme import header, disclaimer
from app.data import (load_risk, nearest, weather, rain_next3, shelters_near,
                      siren_wav, log_alert, read_log)
from src.alerts import build_message, send_telegram

risk = load_risk()
header("Alert Centre", "Preview, send and log flood alerts (Odia + English)")

c1, c2, c3 = st.columns(3)
lat = c1.number_input("Latitude", 20.20, 20.90, 20.80, 0.01)
lon = c2.number_input("Longitude", 86.20, 87.00, 86.40, 0.01)
demo = c3.checkbox("Demo mode (150 mm rain simulate)")

cell = nearest(risk, lat, lon)
level = cell["risk_level"]
if demo:
    level = "High"

rain3 = 0.0
try:
    rain3 = rain_next3(weather(lat, lon))
except Exception as e:
    st.warning(f"Weather load nahi hua: {e}")

if demo:
    rain3 = 150.0
    st.warning("DEMO MODE: rain simulated hai, ye real forecast nahi hai.")

try:
    shel = shelters_near(lat, lon)
except Exception as e:
    shel = []
    st.warning(f"Shelters load nahi hue: {e}")

alert_on = level in ("High", "Medium") and rain3 >= 100

left, right = st.columns(2)
with left:
    st.metric("Susceptibility", level)
    st.metric("3-day rain (mm)", rain3)
    st.metric("Population in this cell (est.)", f"{int(cell['pop_est']):,}")
    if alert_on:
        st.error(f"{level}-risk area + heavy rain. Safe jagah jaane ki taiyari rakho.")
        st.audio(siren_wav(), format="audio/wav", autoplay=True)
    else:
        st.success("Abhi alert trigger nahi hota.")

    if st.button("Telegram alert bhejo", type="primary"):
        try:
            send_telegram(build_message(level, rain3, shel))
            log_alert(level, lat, lon, rain3, "sent")
            st.toast("Alert bhej diya", icon="✅")
            st.success("Alert bhej diya.")
        except Exception as e:
            log_alert(level, lat, lon, rain3, "failed")
            st.error(f"Alert fail: {e}")

with right:
    st.subheader("Message preview")
    st.code(build_message(level, rain3, shel), language=None)
    st.subheader("Nearest shelters (OSM)")
    for s in shel:
        st.write(f"**{s['name']}** · {s['type']} · {s['dist_km']} km")

st.subheader("Alert history")
log = read_log()
if log.empty:
    st.info("Koi alert nahi bheja gaya.")
else:
    st.dataframe(log.iloc[::-1], use_container_width=True, hide_index=True)
    st.download_button("Export CSV", log.to_csv(index=False), "alert_history.csv")
disclaimer()