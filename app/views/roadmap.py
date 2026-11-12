import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
from app.theme import header

header("Roadmap", "Planned features that need data we do not have yet")
items = [
    ("River water level inputs", "Needs live CWC gauge data."),
    ("Village-level risk and management", "Needs village boundary shapefile and a database."),
    ("Rainfall-aware prediction", "Needs 2-3 more flood events (2018, 2019, 2020) for training."),
    ("Official shelter list", "Replace OSM shelters with OSDMA data."),
    ("SMS / WhatsApp delivery", "Needs a gateway and DLT registration."),
    ("Quantitative validation", "IoU against the NRSC flood layer."),
]
cols = st.columns(3)
for i, (t, d) in enumerate(items):
    cols[i % 3].markdown(f'<div class="card"><b>{t}</b><br><span class="page-sub">{d}</span></div>',
                         unsafe_allow_html=True)