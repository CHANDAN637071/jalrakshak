import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pandas as pd
import plotly.express as px
import streamlit as st
from app.theme import header, kpi, COLORS, risk_map, disclaimer
from app.data import load_risk, weather, rain_next3, read_log

risk = load_risk()
header("Overview", "Flood susceptibility, rainfall and population at risk (Kendrapara-Cuttack-Jagatsinghpur region)")

lat, lon = 20.50, 86.42
try:
    w = weather(lat, lon)
    r3 = f"{rain_next3(w)} mm"
except Exception:
    w, r3 = None, "N/A"

hi = risk[risk.risk_level == "High"]
c = st.columns(5)
kpi(c[0], "Grid cells (1 km)", f"{len(risk):,}", "Study area")
kpi(c[1], "High-risk cells", f"{len(hi):,}", "Top 10% by model score", "#ef4444")
kpi(c[2], "Population in High risk", f"{int(hi.pop_est.sum()):,}", "WorldPop estimate", "#f59e0b")
kpi(c[3], "Aug 2022 flood mapped", "289 sq km", "Sentinel-1", "#22d3ee")
kpi(c[4], "3-day rain forecast", r3, "Open-Meteo")

st.write("")
left, right = st.columns([3, 2])
with left:
    st.subheader("Risk map")
    risk_map(risk[risk.risk_level != "Low"], [lat, lon], zoom=9, height=420, key="ov_map")
with right:
    st.subheader("Cells by risk level")
    cnt = risk.risk_level.value_counts().reindex(["Low", "Medium", "High"]).reset_index()
    cnt.columns = ["level", "cells"]
    fig = px.bar(cnt, x="level", y="cells", color="level", color_discrete_map=COLORS)
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      showlegend=False, height=200, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Rainfall (past 7 + next 7 days)")
    if w:
        d = pd.DataFrame({"date": w["daily"]["time"], "rain_mm": w["daily"]["precipitation_sum"]})
        fig2 = px.area(d, x="date", y="rain_mm", color_discrete_sequence=["#22d3ee"])
        fig2.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           height=210, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Weather data load nahi hua (internet check karo).")

st.subheader("Recent alerts sent")
log = read_log()
if log.empty:
    st.info("Abhi tak koi alert nahi bheja gaya. Alert Centre se bhejo.")
else:
    st.dataframe(log.tail(8).iloc[::-1], use_container_width=True, hide_index=True)
disclaimer()