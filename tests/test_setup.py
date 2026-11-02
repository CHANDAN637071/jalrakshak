import ee
from src.config import GEE_PROJECT, AOI_BOX

# 1. Library check
import geopandas, rasterio, folium, streamlit, xgboost, sklearn, pandas, numpy
print("All libraries imported OK")

# 2. Earth Engine check
ee.Initialize(project=GEE_PROJECT)
aoi = ee.Geometry.Rectangle(AOI_BOX)
count = (ee.ImageCollection("COPERNICUS/S1_GRD")
         .filterBounds(aoi)
         .filterDate("2022-06-01", "2022-06-30")
         .size().getInfo())
print(f"Earth Engine OK. Sentinel-1 images found for June 2022: {count}")