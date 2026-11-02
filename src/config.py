GEE_PROJECT = "flash-gasket-425916-s9"


# Study area: [min_lon, min_lat, max_lon, max_lat] (approx. Kendrapara region)
AOI_BOX = [86.2, 20.2, 87.0, 20.9]

# Flood events we will study (we will confirm exact dates later)
EVENTS = {
    "2018": {"before": ("2018-06-01", "2018-06-30"), "after": ("2018-08-01", "2018-08-31")},
    "2022": {"before": ("2022-06-01", "2022-06-30"), "after": ("2022-09-01", "2022-09-20")},
}