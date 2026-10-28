import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from scipy.ndimage import gaussian_filter

# ---------------- PARAMETERS ----------------
# Input data folder (Excel/CSV files)
FOLDER = "simulated_bathy_grid_zone42n.xlsx"
# If depths should be treated as positive numbers (downward positive)
DEPTH_POSITIVE_DOWN = True
# Grid resolution: more cells = finer map
GRID_SIZE = 300
# Smoothing strength: 0 = none, 2-5 = gentle smoothing
SMOOTHING = 3
# Contour line spacing in meters
CONTOUR_INTERVAL = 1
# Color scheme: viridis goes from yellow (shallow) to purple (deep)
COLORMAP = "viridis"
# Output filename
OUTPUT = "bathymetry_map.png"

# Standard viridis color stops for legend
VIRIDIS_STOPS = [
    (0.0, "#440154"),   # deep purple
    (0.25, "#414487"),  # purple-blue
    (0.5, "#2a788e"),   # teal
    (0.75, "#22a884"),  # green-teal
    (1.0, "#fde725"),   # yellow
]

# ---------------- 1. LOAD ALL DATA FILES ----------------
import os

# Find all data files in the folder
if os.path.isfile(FOLDER):
    files = [FOLDER]
else:
    files = []
    for ext in ("xlsx", "xls", "csv", "txt"):
        for f in glob.glob(FOLDER + "/**/*." + ext, recursive=True):
            files.append(f)

print("Files found:", len(files))

# Column name mapping: rename various column names to standard X, Y, Z
RENAME_MAP = {
    "LONGITUDE": "X", "LON": "X", "LONG": "X", "EASTING": "X",
    "EASTING_X_M": "X",
    "LATITUDE": "Y", "LAT": "Y", "NORTHING": "Y",
    "NORTHING_Y_M": "Y",
    "DEPTH": "Z", "ELEVATION_Z_MSL_M": "Z"
}

has_latlon = False
data_frames = []

for f in files:
    # Read file: Excel or CSV
    if f.endswith((".xlsx", ".xls")):
        df = pd.read_excel(f)
    else:
        df = pd.read_csv(f, sep=None, engine="python")

    # Normalize column names to uppercase
    df.columns = [str(c).strip().upper() for c in df.columns]

    # Check if this file has latitude/longitude columns
    has_latlon = has_latlon or ("LATITUDE" in df.columns or "LAT" in df.columns)

    # Rename columns to standard X, Y, Z names
    df = df.rename(columns=RENAME_MAP)

    # Keep only files that have X, Y, and Z columns
    if "X" in df.columns and "Y" in df.columns and "Z" in df.columns:
        data_frames.append(df[["X", "Y", "Z"]])
        print("Read:", f, " -", len(df), "points")
    else:
        print("Skipped (no X, Y, Z):", f, "| columns:", list(df.columns))

# Exit if no valid data found
if not data_frames:
    raise SystemExit("No data read. Check FOLDER path and ensure columns are X, Y, Z (or Longitude, Latitude, Depth).")

# Combine all data, convert to numbers, remove missing values
all_data = pd.concat(data_frames).apply(pd.to_numeric, errors="coerce").dropna()

# Extract coordinate and depth arrays
easting = all_data["X"].values
northing = all_data["Y"].values
depth = all_data["Z"].values if DEPTH_POSITIVE_DOWN else -all_data["Z"].values

# ---------------- 2. INTERPOLATE AND SMOOTH ----------------
# Create a regular grid covering the data area
grid_x, grid_y = np.meshgrid(
    np.linspace(easting.min(), easting.max(), GRID_SIZE),
    np.linspace(northing.min(), northing.max(), GRID_SIZE)
)

# Interpolate depth values onto the grid (cubic fills gaps between points)
interpolated_grid = griddata((easting, northing), depth, (grid_x, grid_y), method="cubic")

# Apply smoothing if requested
if SMOOTHING > 0:
    # Remember which grid cells are outside the data area
    outside_cells = np.isnan(interpolated_grid)
    # Replace NaN with mean for smoothing, then smooth
    grid_data = gaussian_filter(np.nan_to_num(interpolated_grid, nan=np.nanmean(interpolated_grid)), SMOOTHING)
    # Restore NaN for outside cells (keep them blank)
    grid_data[outside_cells] = np.nan
else:
    grid_data = interpolated_grid

# ---------------- 3. CREATE PLOT ----------------
# Contour levels from floor of min to max, spaced by interval
levels = np.arange(np.floor(np.nanmin(grid_data)), np.nanmax(grid_data) + CONTOUR_INTERVAL, CONTOUR_INTERVAL)

# Set up the figure
figure, axis = plt.subplots(figsize=(10, 8))

# Filled contour plot (100 levels) using viridis colormap
contour_fill = axis.contourf(grid_x, grid_y, grid_data, levels=100, cmap=COLORMAP)

# Contour lines in black
contour_lines = axis.contour(grid_x, grid_y, grid_data, levels=levels, colors="k", linewidths=0.5)
# Add labels on contour lines
axis.clabel(contour_lines, fmt="%g", fontsize=7)

# Colorbar with label
colorbar = figure.colorbar(contour_fill, label="Depth (m)")
# Flip colorbar so deep = bottom (purple at bottom)
colorbar.ax.invert_yaxis()

# Set aspect ratio and labels
if has_latlon:
    # Correct shape for degree coordinates
    axis.set_aspect(1 / np.cos(np.radians(northing.mean())))
    axis.set_xlabel("Longitude")
    axis.set_ylabel("Latitude")
else:
    # Equal aspect for metric coordinates
    axis.set_aspect("equal")
    axis.set_xlabel("Easting (m)")
    axis.set_ylabel("Northing (m)")

# Title showing color scheme
axis.set_title("Bathymetry Map (Viridis: shallow=yellow, deep=purple)")

# Save figure at high DPI
plt.savefig(OUTPUT, dpi=200, bbox_inches='tight')
# plt.show()  # Commented out for non-interactive use

print("Saved to:", OUTPUT)