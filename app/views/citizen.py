import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import folium
import streamlit as st
from streamlit_folium import st_folium
from app.theme import header, disclaimer
from app.data import load_risk, nearest, weather, rain_next3, shelters_near, route_to

risk = load_risk()
header("Citizen View", "Meri location: risk, nearest shelter aur evacuation route")

c1, c2, c3 = st.columns(3)
lat = c1.number_input("Latitude", 20.20, 20.90, 20.74, 0.01)
lon = c2.number_input("Longitude", 86.20, 87.00, 86.45, 0.01)
demo = c3.checkbox("Demo mode (150 mm rain simulate)")

cell = nearest(risk, lat, lon)
level = cell["risk_level"]
rain3 = 0.0
try:
    rain3 = rain_next3(weather(lat, lon))
except Exception as e:
    st.warning(f"Weather load nahi hua: {e}")
if demo:
    rain3 = 150.0
    level = "High" if level == "Low" else level
    st.warning("DEMO MODE: simulated rain, real forecast nahi.")

alert_on = level in ("High", "Medium") and rain3 >= 100
if alert_on:
    st.error("Aapka ilaaka flood-prone hai aur bhaari baarish ki forecast hai. Niche diye shelter ki taraf jaane ki taiyari rakho.")
elif level == "High":
    st.warning("Aapka ilaaka flood-prone hai. Abhi bhaari baarish forecast nahi hai, par alert rahein.")
else:
    st.success("Abhi koi flood alert nahi.")

m1, m2, m3 = st.columns(3)
m1.metric("Susceptibility", level)
m2.metric("3-day rain (mm)", rain3)
m3.metric("People in your 1 km cell (est.)", f"{int(cell['pop_est']):,}")

try:
    shel = shelters_near(lat, lon)
except Exception as e:
    shel = []
    st.warning(f"Shelters load nahi hue: {e}")

if not shel:
    st.info("Aas-paas shelter data nahi mila. Thodi der baad dobara try karo.")
else:
    names = [f"{s['name']} ({s['type']}, {s['dist_km']} km)" for s in shel]
    pick = st.selectbox("Shelter chuno", names, index=0)
    dest = shel[names.index(pick)]
    rt = route_to(lat, lon, dest["lat"], dest["lon"])

    m = folium.Map(location=[lat, lon], zoom_start=12, tiles="OpenStreetMap")
    folium.Marker([lat, lon], tooltip="Aap yahan", icon=folium.Icon(color="red")).add_to(m)
    folium.Marker([dest["lat"], dest["lon"]], tooltip=dest["name"],
                  icon=folium.Icon(color="green", icon="home")).add_to(m)
    if rt:
        coords, km, mins = rt
        folium.PolyLine(coords, color="#22d3ee", weight=5).add_to(m)
        st.success(f"Route: {km} km, lagbhag {mins} minute (gaadi se, normal sadak ki haalat maan ke).")
    else:
        folium.PolyLine([[lat, lon], [dest["lat"], dest["lon"]]], color="#f59e0b",
                        weight=3, dash_array="8").add_to(m)
        st.warning("Route service abhi available nahi. Seedhi line dikhayi gayi hai, ye asli sadak nahi hai.")
    st_folium(m, height=420, use_container_width=True, key="citizen_map",
              returned_objects=[])

st.caption("Route estimate hai. Baadh mein sadkein band ho sakti hain; local administration / OSDMA ke nirdesh maanein.")
disclaimer()