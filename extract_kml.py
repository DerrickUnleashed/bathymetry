#!/usr/bin/env python3
"""Extract survey points from KML contour lines and save as CSV for main.py"""
import xml.etree.ElementTree as ET
import pandas as pd

# Parse the KML
tree = ET.parse("doc.kml")
root = tree.getroot()

# KML namespace
ns = {"kml": "http://www.opengis.net/kml/2.2"}

# Extract all Placemarks with LineString coordinates
data = []
for placemark in root.findall(".//kml:Placemark", ns):
    name_elem = placemark.find("kml:name", ns)
    desc_elem = placemark.find("kml:description", ns)
    coords_elem = placemark.find(".//kml:coordinates", ns)
    
    if coords_elem is not None and coords_elem.text:
        # Parse depth from name or description (e.g., "1 m", "Depth: 1 m")
        depth = None
        if name_elem is not None and name_elem.text:
            import re
            match = re.search(r"(\d+(?:\.\d+)?)\s*m", name_elem.text)
            if match:
                depth = float(match.group(1))
        if depth is None and desc_elem is not None and desc_elem.text:
            import re
            match = re.search(r"(\d+(?:\.\d+)?)\s*m", desc_elem.text)
            if match:
                depth = float(match.group(1))
        
        if depth is None:
            continue
            
        # Parse coordinates: "lon,lat,0.0 lon,lat,0.0 ..."
        coords_text = coords_elem.text.strip()
        for coord in coords_text.split():
            parts = coord.split(",")
            if len(parts) >= 2:
                lon = float(parts[0])
                lat = float(parts[1])
                data.append({"X": lon, "Y": lat, "Z": depth})

df = pd.DataFrame(data)
print(f"Extracted {len(df)} points")
print(f"Depth range: {df['Z'].min()} - {df['Z'].max()} m")
print(df.head())

# Save as CSV for main.py
df.to_csv("survey_data.csv", index=False)
print("Saved to survey_data.csv")