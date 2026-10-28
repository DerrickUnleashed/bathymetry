import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from scipy.ndimage import gaussian_filter

# ---------------- PARAMETERS ----------------
FOLDER = "simulated_bathy_grid_zone42n.xlsx"   # folder with all data files (Excel / CSV)
DEPTH_POSITIVE_DOWN = True               # True = depths are positive numbers
GRID_SIZE = 300                          # grid cells (higher = finer)
SMOOTHING = 3                            # 0 = no smoothing, 2-5 = smooth
CONTOUR_INTERVAL = 1                     # contour line every ... m
COLORMAP = "viridis"                     # colours: shallow (yellow) -> deep (purple)
OUTPUT = "bathymetry_map.png"

# Viridis color stops for consistent legend (matches HTML)
# These are the standard viridis colormap stops
VIRIDIS_STOPS = [
    (0.0, "#440154"),   # deep purple
    (0.25, "#414487"),  # purple-blue
    (0.5, "#2a788e"),   # teal
    (0.75, "#22a884"),  # green-teal
    (1.0, "#fde725"),   # yellow
]

# ---------------- 1. READ ALL FILES ----------------
import os
if os.path.isfile(FOLDER):                           # a single file also works
    files = [FOLDER]
else:
    files = [f for ext in ("xlsx", "xls", "csv", "txt")
             for f in glob.glob(FOLDER + "/**/*." + ext, recursive=True)]
print("Files found:", len(files))

RENAME = {"LONGITUDE": "X", "LON": "X", "LONG": "X", "EASTING": "X",
          "EASTING_X_M": "X", "LATITUDE": "Y", "LAT": "Y", "NORTHING": "Y",
          "NORTHING_Y_M": "Y", "DEPTH": "Z", "ELEVATION_Z_MSL_M": "Z"}
IS_LATLON = False
data = []
for f in files:
    df = pd.read_excel(f) if f.endswith((".xlsx", ".xls")) else pd.read_csv(f, sep=None, engine="python")
    df.columns = [str(c).strip().upper() for c in df.columns]
    IS_LATLON = IS_LATLON or "LATITUDE" in df.columns or "LAT" in df.columns
    df = df.rename(columns=RENAME)                  # latitude/longitude/depth -> Y/X/Z
    if {"X", "Y", "Z"} <= set(df.columns):          # use only files with X, Y, Z
        data.append(df[["X", "Y", "Z"]])
        print("Read:", f, len(df), "points")
    else:
        print("Skipped (no X, Y, Z columns):", f, "| columns are:", list(df.columns))

if not data:
    raise SystemExit("No data read. Check FOLDER path and that columns are X, Y, Z (or Longitude, Latitude, Depth).")
data = pd.concat(data).apply(pd.to_numeric, errors="coerce").dropna()

x = data["X"].values                                 # easting (m)
y = data["Y"].values                                 # northing (m)
depth = data["Z"].values if DEPTH_POSITIVE_DOWN else -data["Z"].values

# ---------------- 2. SMOOTH SURFACE ----------------
gx, gy = np.meshgrid(np.linspace(x.min(), x.max(), GRID_SIZE),
                     np.linspace(y.min(), y.max(), GRID_SIZE))
grid = griddata((x, y), depth, (gx, gy), method="cubic")   # fill gaps between points
if SMOOTHING > 0:
    outside = np.isnan(grid)                               # remember blank area
    grid = gaussian_filter(np.nan_to_num(grid, nan=np.nanmean(grid)), SMOOTHING)
    grid[outside] = np.nan                                 # keep outside area blank

# ---------------- 3. PLOT ----------------
levels = np.arange(np.floor(np.nanmin(grid)), np.nanmax(grid) + CONTOUR_INTERVAL, CONTOUR_INTERVAL)
fig, ax = plt.subplots(figsize=(10, 8))

# Use viridis (shallow=yellow, deep=purple) with proper colorbar orientation
fill = ax.contourf(gx, gy, grid, levels=100, cmap=COLORMAP)
lines = ax.contour(gx, gy, grid, levels=levels, colors="k", linewidths=0.5)
ax.clabel(lines, fmt="%g", fontsize=7)

# Colorbar: deep (purple) at bottom, shallow (yellow) at top for bathymetry
cbar = fig.colorbar(fill, label="Depth (m)")
cbar.ax.invert_yaxis()  # deep = bottom

if IS_LATLON:
    ax.set_aspect(1 / np.cos(np.radians(y.mean())))   # correct shape for degrees
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
else:
    ax.set_aspect("equal")
    ax.set_xlabel("Easting (m)")
    ax.set_ylabel("Northing (m)")
ax.set_title("Bathymetry Map (Viridis: shallow=yellow, deep=purple)")
plt.savefig(OUTPUT, dpi=200, bbox_inches='tight')
# plt.show()  # Commented out for non-interactive use
print(f"Saved to {OUTPUT}")