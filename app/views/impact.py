import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import plotly.express as px
import streamlit as st
from app.theme import header, kpi, COLORS, disclaimer
from app.data import load_risk

risk = load_risk()
header("Flood Impact Analysis", "Aug 2022 Mahanadi flood: Sentinel-1 mapped extent + WorldPop population")

flooded = risk[risk.flood_frac >= 0.10]
people = int((risk.pop_est * risk.flood_frac).sum())

c = st.columns(4)
kpi(c[0], "Mapped flood area", "289 sq km", "Sentinel-1, 18-24 Aug 2022")
kpi(c[1], "People in mapped flood", f"{people:,}", "Approximate estimate", "#f59e0b")
kpi(c[2], "Cells >= 10% flooded", f"{len(flooded):,}", "Used as model label")
kpi(c[3], "Model blocked-CV AUC", "0.76", "Baseline 0.68", "#22c55e")

st.write("")
a, b = st.columns(2)
layout = dict(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
              plot_bgcolor="rgba(0,0,0,0)", showlegend=False, height=320)

with a:
    st.subheader("Population by risk level")
    p = (risk.groupby("risk_level", observed=True).pop_est.sum()
         .reindex(["Low", "Medium", "High"]).reset_index())
    fig = px.bar(p, x="risk_level", y="pop_est", color="risk_level", color_discrete_map=COLORS)
    fig.update_layout(**layout, yaxis_title="Estimated people")
    st.plotly_chart(fig, use_container_width=True)

with b:
    st.subheader("Actual flooded share by predicted risk")
    s = (risk.assign(f=(risk.flood_frac >= 0.10).astype(int))
         .groupby("risk_level", observed=True).f.mean() * 100)
    s = s.reindex(["Low", "Medium", "High"]).reset_index()
    s.columns = ["risk_level", "pct"]
    fig = px.bar(s, x="risk_level", y="pct", color="risk_level", color_discrete_map=COLORS)
    fig.update_layout(**layout, yaxis_title="% cells flooded")
    st.plotly_chart(fig, use_container_width=True)

st.info("Validation: NRSC/ISRO Sentinel-1A flood map (21 Aug 2022) se visual comparison kiya gaya. "
        "Quantitative IoU future work hai. Dhaan ke geele khet false positive ho sakte hain, "
        "isliye flood extent aur people numbers approximate hain.")
disclaimer()