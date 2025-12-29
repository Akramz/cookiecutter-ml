---
name: gee-imagery
description: Downloads remote sensing imagery from Google Earth Engine. Use when the user wants to download satellite imagery, acquire Landsat/Sentinel/MODIS data, get imagery for a region of interest, export GEE collections, or prepare remote sensing data for ML training.
allowed-tools: Read, Write, Edit, Bash(python:*), Bash(earthengine:*), Glob, Grep
---

# Google Earth Engine Imagery Download

Download remote sensing imagery from Google Earth Engine (GEE) for a region of interest, time period, and dataset.

## Quick Start

### 1. Gather Required Information

Ask the user for:
- **Region of Interest (ROI)**: GeoJSON file path, bounding box coordinates `[west, south, east, north]`, or point coordinates `[lon, lat]` with buffer
- **Time Period**: Start date and end date in `YYYY-MM-DD` format
- **Dataset**: Which satellite collection (see [REFERENCE.md](REFERENCE.md) for options)
- **Output Path**: Where to save the imagery (e.g., `data/raw/imagery/`)

### 2. Check Prerequisites

```bash
# Check if earthengine-api is installed
python -c "import ee; print('earthengine-api installed')"

# Check authentication status
python .claude/skills/gee-imagery/scripts/authenticate.py --check
```

**If not authenticated**, choose one method:

```bash
# Option A: Interactive (opens browser) - for local development
python .claude/skills/gee-imagery/scripts/authenticate.py

# Option B: CLI equivalent
earthengine authenticate

# Option C: Service account (for servers/CI/automated pipelines)
python .claude/skills/gee-imagery/scripts/authenticate.py \
    --service-account path/to/service-account-key.json
```

**Authentication persists** in `~/.config/earthengine/credentials` - you only need to authenticate once per machine.

### 3. Download Imagery

Use the helper script:

```bash
# Download a composite (single image)
python .claude/skills/gee-imagery/scripts/download_imagery.py \
    --collection COPERNICUS/S2_SR_HARMONIZED \
    --start-date 2023-01-01 \
    --end-date 2023-12-31 \
    --roi path/to/roi.geojson \
    --output-dir data/raw/imagery/ \
    --composite median

# Download full time series (one file per image)
python .claude/skills/gee-imagery/scripts/download_imagery.py \
    --collection COPERNICUS/S1_GRD \
    --start-date 2023-01-01 \
    --end-date 2023-03-31 \
    --roi -122.5,37.5,-122.0,38.0 \
    --output-dir data/raw/imagery/
```

**Arguments:**
| Arg | Description |
|-----|-------------|
| `--collection` | GEE ImageCollection ID (required) |
| `--start-date` | Start date YYYY-MM-DD (required) |
| `--end-date` | End date YYYY-MM-DD (required) |
| `--roi` | GeoJSON file or bbox `west,south,east,north` (required) |
| `--output-dir` | Output directory (default: `data/raw/imagery/`) |
| `--composite` | `median`, `mean`, `min`, `max`, `mosaic` (omit for time series) |
| `--bands` | Comma-separated band names (default: all) |
| `--scale` | Resolution in meters (default: 10) |
| `--crs` | CRS (default: EPSG:4326) |
| `--dry-run` | Preview without downloading |

## Common Datasets

| Dataset | Collection ID | Resolution | Use Case |
|---------|--------------|------------|----------|
| Sentinel-2 SR | `COPERNICUS/S2_SR_HARMONIZED` | 10m | Land cover, agriculture |
| Landsat 8 | `LANDSAT/LC08/C02/T1_L2` | 30m | Long-term monitoring |
| Landsat 9 | `LANDSAT/LC09/C02/T1_L2` | 30m | Recent imagery |
| MODIS NDVI | `MODIS/061/MOD13A1` | 500m | Vegetation monitoring |
| Sentinel-1 SAR | `COPERNICUS/S1_GRD` | 10m | All-weather imaging |
| DEM (SRTM) | `USGS/SRTMGL1_003` | 30m | Elevation data |

For complete dataset reference, see [REFERENCE.md](REFERENCE.md).

## Workflow Steps

### Step 1: Define Region of Interest

```python
import ee
ee.Initialize()

# Option A: From GeoJSON file
import json
with open('roi.geojson') as f:
    geojson = json.load(f)
roi = ee.Geometry(geojson['features'][0]['geometry'])

# Option B: Bounding box [west, south, east, north]
roi = ee.Geometry.Rectangle([-122.5, 37.5, -122.0, 38.0])

# Option C: Point with buffer (in meters)
roi = ee.Geometry.Point([-122.3, 37.8]).buffer(5000)
```

### Step 2: Filter Collection

```python
collection = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterBounds(roi)
    .filterDate('2023-01-01', '2023-12-31')
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)))

print(f"Found {collection.size().getInfo()} images")
```

### Step 3: Process and Export

```python
# Create composite (median reduces clouds)
composite = collection.median().clip(roi)

# Select bands
composite = composite.select(['B4', 'B3', 'B2', 'B8'])

# Export to Google Drive
task = ee.batch.Export.image.toDrive(
    image=composite,
    description='sentinel2_composite',
    folder='gee_exports',
    region=roi,
    scale=10,
    maxPixels=1e13,
    fileFormat='GeoTIFF'
)
task.start()
print(f"Export started: {task.status()}")
```

### Step 4: Download from Drive (or use direct download for small areas)

For small areas, use direct download:
```python
import requests
url = composite.getDownloadURL({
    'scale': 10,
    'region': roi,
    'format': 'GEO_TIFF'
})
response = requests.get(url)
with open('output.tif', 'wb') as f:
    f.write(response.content)
```

## Output Structure

After downloading, organize imagery as:
```
data/raw/imagery/
├── sentinel2_2023_composite.tif
├── metadata.json
└── roi.geojson
```

## Requirements

Add to `requirements.txt`:
```
earthengine-api>=0.1.370
google-cloud-storage>=2.0.0
geojson>=3.0.0
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Not authenticated" | Run `python .claude/skills/gee-imagery/scripts/authenticate.py` |
| "Quota exceeded" | Use smaller ROI or reduce scale |
| "No images found" | Check collection ID, date range, and ROI |
| "Download failed" | ROI may be too large - try smaller area or use `--dry-run` first |

## Next Steps

After downloading imagery:
1. Add data path to experiment config in `configs/`
2. Create/update dataset class in `{{cookiecutter.project_slug}}/datasets.py`
3. Run preprocessing if needed
