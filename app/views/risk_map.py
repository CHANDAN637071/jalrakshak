import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
from app.theme import header, risk_map, disclaimer
from app.data import load_risk, nearest, shelters_near

risk = load_risk()
header("Odisha Risk Map", "Marker pe click karo: cell ki details aur nearest shelters dikhenge")

f1, f2 = st.columns([2, 1])
levels = f1.multiselect("Risk level", ["High", "Medium", "Low"], default=["High", "Medium"])
min_pop = f2.slider("Min population in cell", 0, int(risk.pop_est.max()), 0, 500)
view = risk[risk.risk_level.isin(levels) & (risk.pop_est >= min_pop)]

if "sel" not in st.session_state:
    st.session_state.sel = (20.80, 86.40)
lat, lon = st.session_state.sel
cell = nearest(risk, lat, lon)

try:
    shel = shelters_near(lat, lon)
except Exception as e:
    shel = []
    st.warning(f"Shelters load nahi hue: {e}")

mc, pc = st.columns([3, 1])
with mc:
    out = risk_map(view, [lat, lon], zoom=10, height=600, shelters=shel, key="rm")
    clk = (out or {}).get("last_object_clicked")
    if clk and (round(clk["lat"], 4), round(clk["lng"], 4)) != (round(lat, 4), round(lon, 4)):
        st.session_state.sel = (clk["lat"], clk["lng"])
        st.rerun()
with pc:
    st.markdown("**Legend**  \n🟢 Low  🟠 Medium  🔴 High")
    st.subheader("Selected cell")
    st.metric("Risk level", cell["risk_level"])
    st.metric("Model score", f"{cell['risk_score']:.2f}")
    st.metric("Population (est.)", f"{int(cell['pop_est']):,}")
    st.metric("Aug 2022 flooded share", f"{cell['flood_frac']*100:.0f}%")
    st.caption(f"{lat:.3f}, {lon:.3f}")
    st.subheader("Nearest shelters (OSM)")
    for s in shel:
        st.write(f"**{s['name']}** · {s['type']} · {s['dist_km']} km")
disclaimer()