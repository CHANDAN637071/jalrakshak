# JalRakshak: Flood Risk Early-Warning Prototype for Coastal Odisha

Live demo: https://jalrakshak-r5ltfuf3wbdvxsstypja8l.streamlit.app/

## What it does
- Maps the August 2022 Mahanadi flood from Sentinel-1 SAR (~289 sq km)
- Ranks 1 km cells by flood susceptibility (XGBoost, blocked CV AUC 0.76)
- Shows live weather and 3-day rain forecast (Open-Meteo)
- Estimates population at risk (WorldPop)
- Finds nearest shelters (OpenStreetMap) with evacuation route (OSRM)
- Sends Odia + English Telegram alerts with a siren in the dashboard

## Tech
Python, Google Earth Engine, Sentinel-1, XGBoost, Streamlit, Folium, Plotly,
Open-Meteo, OSRM, Overpass API, Telegram Bot API

## Limitations
Single flood event, flood label not ground-truth validated (paddy fields may
add false positives), OSM shelters (not official OSDMA list), static
susceptibility model. This is a research prototype, not an official warning system.

## Future work
Soil moisture, rainfall-aware prediction with more events, IoT sensors,
Firebase push, village-level boundaries, official CWC/OSDMA data.