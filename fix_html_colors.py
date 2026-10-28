#!/usr/bin/env python3
"""
Regenerate the HTML contour map with consistent viridis colors.
Reads the existing HTML, extracts the GeoJSON data, and rewrites with
viridis colors matching the legend.
"""
import json
import re

# Viridis colormap stops (from the legend in the HTML)
VIRIDIS_STOPS = [
    (0.0, "#440154"),   # deep purple (11.97m)
    (0.167, "#414487"), # purple-blue (9.68m)
    (0.333, "#2a788e"), # teal (7.38m)
    (0.5, "#22a884"),   # green-teal (5.09m)
    (0.667, "#7ad151"), # green (2.79m)
    (1.0, "#fde725"),   # yellow (0.5m)
]

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb):
    """Convert RGB tuple to hex color."""
    return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))

def interpolate_color(t, stops):
    """
    Interpolate color at position t (0.0 to 1.0) using viridis stops.
    t=0.0 = deep (purple), t=1.0 = shallow (yellow)
    """
    # Find the two stops to interpolate between
    for i in range(len(stops) - 1):
        t1, c1 = stops[i]
        t2, c2 = stops[i + 1]
        if t1 <= t <= t2:
            # Linear interpolation
            if t2 == t1:
                return c1
            factor = (t - t1) / (t2 - t1)
            r1, g1, b1 = hex_to_rgb(c1)
            r2, g2, b2 = hex_to_rgb(c2)
            r = r1 + factor * (r2 - r1)
            g = g1 + factor * (g2 - g1)
            b = b1 + factor * (b2 - b1)
            return rgb_to_hex((r, g, b))
    # If t is exactly 1.0
    return stops[-1][1]

def depth_to_viridis(depth, min_depth, max_depth):
    """
    Map depth to viridis color.
    Shallow (min_depth) -> yellow (t=1.0)
    Deep (max_depth) -> purple (t=0.0)
    """
    if max_depth == min_depth:
        return VIRIDIS_STOPS[-1][1]  # yellow
    # Normalize: 0 = deep, 1 = shallow
    t = 1.0 - (depth - min_depth) / (max_depth - min_depth)
    return interpolate_color(t, VIRIDIS_STOPS)

# Read the existing HTML
with open('simulated_survey_data_contours.html', 'r') as f:
    html = f.read()

# Extract the D object
match = re.search(r'const D = ({.*?});', html, re.DOTALL)
if not match:
    print("Could not find D object")
    exit(1)

d_str = match.group(1)
D = json.loads(d_str)

# Find all depth levels in minor and major features
levels = set()
for feature in D['minor']['features']:
    levels.add(feature['properties']['level'])
for feature in D['major']['features']:
    levels.add(feature['properties']['level'])

min_level = min(levels)
max_level = max(levels)
print(f"Depth range: {min_level} - {max_level} m")
print(f"Levels found: {sorted(levels)}")

# Create color map for each level
level_colors = {}
for level in sorted(levels):
    level_colors[level] = depth_to_viridis(level, min_level, max_level)
    print(f"  Level {level}m -> {level_colors[level]}")

# Update colors in minor features
for feature in D['minor']['features']:
    level = feature['properties']['level']
    feature['properties']['color'] = level_colors[level]

# Update colors in major features
for feature in D['major']['features']:
    level = feature['properties']['level']
    feature['properties']['color'] = level_colors[level]

# Update the legend to use consistent viridis stops
# The legend currently has 6 stops - we'll keep those but ensure they match
D['legend'] = [
    ["#fde725", f"{min_level:.1f}"],  # shallowest
    ["#7ad151", f"{min_level + (max_level-min_level)*0.167:.1f}"],
    ["#22a884", f"{min_level + (max_level-min_level)*0.333:.1f}"],
    ["#2a788e", f"{min_level + (max_level-min_level)*0.5:.1f}"],
    ["#414487", f"{min_level + (max_level-min_level)*0.667:.1f}"],
    ["#440154", f"{max_level:.1f}"],  # deepest
]

# Reconstruct the HTML
new_d_str = json.dumps(D, separators=(',', ':'))
new_html = html[:match.start(1)] + new_d_str + html[match.end(1):]

# Write the updated HTML
with open('simulated_survey_data_contours.html', 'w') as f:
    f.write(new_html)

print("\nHTML updated with consistent viridis colors!")
print("Legend updated to match depth range.")