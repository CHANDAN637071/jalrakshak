import datetime as dt
import folium
import streamlit as st
from streamlit_folium import st_folium

COLORS = {"Low": "#22c55e", "Medium": "#f59e0b", "High": "#ef4444"}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: linear-gradient(180deg,#0b1730 0%,#09101f 100%); }
section[data-testid="stSidebar"] { background:#0d1b3a; border-right:1px solid #1e3358; }
.block-container { padding-top: 1.4rem; max-width: 1400px; }
.card { background: linear-gradient(145deg,#12244a,#0f1e3d); border:1px solid #1f3a66;
  border-radius:14px; padding:16px 18px; box-shadow:0 6px 18px rgba(0,0,0,.28);
  transition: transform .15s, border-color .15s; height:100%; }
.card:hover { transform: translateY(-2px); border-color:#22d3ee; }
.kpi-label { color:#8fa6c9; font-size:.74rem; text-transform:uppercase; letter-spacing:.07em; }
.kpi-value { color:#e6f0ff; font-size:1.75rem; font-weight:700; line-height:1.2; }
.kpi-sub { color:#22d3ee; font-size:.76rem; }
.badge { display:inline-block; padding:2px 10px; border-radius:999px; font-size:.72rem; font-weight:600; }
.page-title { font-size:1.6rem; font-weight:700; color:#e6f0ff; margin:0; }
.page-sub { color:#8fa6c9; font-size:.85rem; margin-bottom:.8rem; }
.logo { font-size:1.35rem; font-weight:700; color:#22d3ee; }
.logo small { display:block; color:#8fa6c9; font-weight:400; font-size:.72rem; }
div[data-testid="stMetric"] { background:#10224a; border:1px solid #1f3a66; border-radius:12px; padding:10px 14px; }
.stButton>button { border-radius:10px; border:1px solid #22d3ee; background:#0e7490; color:white; font-weight:600; }
.stButton>button:hover { background:#22d3ee; color:#0b1730; }
</style>
"""

def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)

def header(title, subtitle=""):
    now = dt.datetime.now().strftime("%d %b %Y, %H:%M")
    c1, c2 = st.columns([3, 1])
    c1.markdown(f'<p class="page-title">{title}</p><p class="page-sub">{subtitle}</p>', unsafe_allow_html=True)
    c2.markdown(f'<div style="text-align:right" class="page-sub">Last updated: {now}<br>'
                f'<span class="badge" style="background:#1e3a5f;color:#7dd3fc">RESEARCH PROTOTYPE</span></div>',
                unsafe_allow_html=True)

def kpi(col, label, value, sub="", color="#22d3ee"):
    col.markdown(f'<div class="card"><div class="kpi-label">{label}</div>'
                 f'<div class="kpi-value">{value}</div>'
                 f'<div class="kpi-sub" style="color:{color}">{sub}</div></div>', unsafe_allow_html=True)

def disclaimer():
    st.caption("Prototype hai, official warning nahi. Official alerts ke liye IMD / OSDMA follow karo.")

def risk_map(df, center, zoom=10, height=520, shelters=None, key="map"):
    m = folium.Map(location=center, zoom_start=zoom, tiles="OpenStreetMap")
    for _, r in df.iterrows():
        folium.CircleMarker([r.lat, r.lon], radius=4, color=COLORS[r.risk_level], fill=True,
            fill_opacity=0.65, weight=0,
            tooltip=f"{r.risk_level} | score {r.risk_score:.2f} | pop ~{int(r.pop_est):,}").add_to(m)
    for s in shelters or []:
        folium.Marker([s["lat"], s["lon"]], tooltip=f"{s['name']} ({s['type']}, {s['dist_km']} km)",
                      icon=folium.Icon(color="blue", icon="home")).add_to(m)
    folium.Marker(center, tooltip="Selected", icon=folium.Icon(color="red")).add_to(m)
    return st_folium(m, height=height, use_container_width=True, key=key,
                     returned_objects=["last_object_clicked"])