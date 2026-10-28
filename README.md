<div align="center">

<!-- Banner -->
<img src="https://capsule-render.vercel.app/api?type=waving&color=667EEA&height=300&section=header&text=Bathymetry%20Mapping%20Tool&fontSize=70&animation=fadeIn&fontAlignY=38&desc=Convert%20KML%20contour%20data%20to%20interactive%20bathymetry%20maps&descAlignY=55&descAlign=50" width="100%" />

<!-- Badges -->
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

</div>

# Overview / About The Project

**Nat** is a Python-based bathymetry mapping tool that converts survey point data (from KML contour lines, CSV, or Excel files) into interactive bathymetry maps. It uses cubic interpolation, Gaussian smoothing, and the viridis colormap to produce publication-quality depth maps with contour lines and a depth legend.

The project exists to simplify the process of transforming geographical contour data into visual bathymetry representations, suitable for marine research, mapping, and analysis.

# Key Features

- Reads multiple data formats: Excel (.xlsx, .xls), CSV, and TXT files
- Automatic column renaming (LONGITUDE/LATITUDE/DEPTH → X/Y/Z)
- Cubic interpolation onto regular grids using `scipy.interpolate.griddata`
- Gaussian smoothing control (0 = none, 2-5 = gentle smoothing)
- Viridis colormap with consistent color stops (yellow=shallow, purple=deep)
- Automatic contour line generation with labeled levels
- Latitude/longitude shape correction for degree-based coordinates
- High-resolution PNG output (200 DPI)
- Batch processing of multiple data files

# Tech Stack & Prerequisites

- **Language:** Python 3.10+
- **Dependencies:**
  - `numpy` — numerical operations
  - `pandas` — data manipulation
  - `matplotlib` — plotting
  - `scipy` — interpolation and Gaussian filtering
  - `openpyxl` — Excel file support (required for .xlsx files)

**Input data requirements:**
- Files must contain columns named X, Y, Z (or variants: Longitude, Latitude, Depth, Easting, Northing, Elevation)
- Z values represent depth (positive downward or invertible)

# Getting Started / Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd nat
   ```

2. **Install dependencies:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
   _Or manually:_ `pip install numpy pandas matplotlib scipy openpyxl`

3. **Ensure data files are present:**
   - Place Excel/CSV files with X/Y/Z columns in the project folder
   - Or run `python extract_kml.py` to convert KML contour data to `survey_data.csv`

4. **Run the app locally:**
   ```bash
   python main.py
   ```
   This generates `bathymetry_map.png` in the project root.

# Usage Guide & Examples

**Basic usage:**
```bash
python main.py
```

**With custom parameters:**
Edit `main.py` or pass parameters directly:
- `FOLDER` — path to data folder or single file
- `GRID_SIZE` — grid resolution (default: 300)
- `SMOOTHING` — smoothing strength (0-5, default: 3)
- `CONTOUR_INTERVAL` — contour spacing in meters (default: 1)
- `COLORMAP` — matplotlib colormap name (default: "viridis")
- `OUTPUT` — output filename (default: "bathymetry_map.png")

**From extracted KML data:**
```bash
python extract_kml.py   # generates survey_data.csv from doc.kml
python main.py          # creates the bathymetry map
```

**HTML contour map:**
The project also includes `fix_html_colors.py` to regenerate the interactive HTML contour map with consistent viridis colors matching the PNG legend.

# Project Structure

```
nat/
├── main.py                  # Main bathymetry mapping script
├── extract_kml.py           # Extract points from KML contour lines
├── fix_html_colors.py       # Regenerate HTML with consistent viridis colors
├── survey_data.csv          # Input data (X, Y, Z columns)
├── doc.kml                  # Source KML contour data
├── simulated_bathy_grid_zone42n.xlsx  # Sample Excel data
├── simulated_survey_data_contours.html  # HTML contour map
├── bathymetry_map.png       # Generated output
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

# Contributing & License

- **License:** MIT — see `LICENSE` for details
- **Contributions:** Pull requests are welcome. Please ensure code follows the project's style (keep it simple, readable, and well-commented)
- **Running tests:** Currently no formal test suite; manual verification via `python main.py` is the primary validation method