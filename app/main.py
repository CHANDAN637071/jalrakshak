import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import streamlit as st
st.set_page_config(page_title="JalRakshak", page_icon="🌊", layout="wide")

from app.theme import inject_css
inject_css()

st.sidebar.markdown('<div class="logo">🌊 JalRakshak<small>Flood Risk Command Centre</small></div>',
                    unsafe_allow_html=True)
st.sidebar.divider()

pages = [
    st.Page("views/overview.py", title="Overview", icon="📊", default=True),
    st.Page("views/risk_map.py", title="Odisha Risk Map", icon="🗺️"),
    st.Page("views/live.py", title="Live Monitoring", icon="📡"),
    st.Page("views/impact.py", title="Flood Impact Analysis", icon="🏘️"),
    st.Page("views/alerts.py", title="Alert Centre", icon="🚨"),
    st.Page("views/roadmap.py", title="Roadmap", icon="🧭"),
]
st.navigation(pages).run()