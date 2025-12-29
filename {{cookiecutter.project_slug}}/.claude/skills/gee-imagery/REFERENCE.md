# GEE Imagery Reference

## Satellite Collections

### Sentinel-2

**Surface Reflectance (Recommended)**
```python
collection_id = 'COPERNICUS/S2_SR_HARMONIZED'
```

| Band | Description | Resolution | Wavelength |
|------|-------------|------------|------------|
| B1 | Coastal aerosol | 60m | 443nm |
| B2 | Blue | 10m | 490nm |
| B3 | Green | 10m | 560nm |
| B4 | Red | 10m | 665nm |
| B5 | Red Edge 1 | 20m | 705nm |
| B6 | Red Edge 2 | 20m | 740nm |
| B7 | Red Edge 3 | 20m | 783nm |
| B8 | NIR | 10m | 842nm |
| B8A | Red Edge 4 | 20m | 865nm |
| B9 | Water Vapor | 60m | 945nm |
| B11 | SWIR 1 | 20m | 1610nm |
| B12 | SWIR 2 | 20m | 2190nm |
| SCL | Scene Classification | 20m | - |

**Cloud Filtering Property:** `CLOUDY_PIXEL_PERCENTAGE`

**Common Band Combinations:**
- True Color: `B4, B3, B2`
- False Color (vegetation): `B8, B4, B3`
- Agriculture: `B11, B8, B2`
- NDVI: `(B8 - B4) / (B8 + B4)`

---

### Landsat 8/9

**Collection 2 Level 2 (Surface Reflectance)**
```python
# Landsat 8
collection_id = 'LANDSAT/LC08/C02/T1_L2'
# Landsat 9
collection_id = 'LANDSAT/LC09/C02/T1_L2'
```

| Band | Description | Resolution |
|------|-------------|------------|
| SR_B1 | Coastal Aerosol | 30m |
| SR_B2 | Blue | 30m |
| SR_B3 | Green | 30m |
| SR_B4 | Red | 30m |
| SR_B5 | NIR | 30m |
| SR_B6 | SWIR 1 | 30m |
| SR_B7 | SWIR 2 | 30m |
| ST_B10 | Thermal | 100m |
| QA_PIXEL | Quality Assessment | 30m |

**Cloud Filtering Property:** `CLOUD_COVER`

**Scaling:** Multiply by 0.0000275 and add -0.2 for surface reflectance

```python
def apply_scale_factors(image):
    optical = image.select('SR_B.').multiply(0.0000275).add(-0.2)
    thermal = image.select('ST_B.*').multiply(0.00341802).add(149.0)
    return image.addBands(optical, None, True).addBands(thermal, None, True)
```

---

### Sentinel-1 SAR

```python
collection_id = 'COPERNICUS/S1_GRD'
```

| Band | Description | Polarization |
|------|-------------|--------------|
| VV | Vertical transmit, Vertical receive | Single/Dual |
| VH | Vertical transmit, Horizontal receive | Dual |
| HH | Horizontal transmit, Horizontal receive | Single/Dual |
| HV | Horizontal transmit, Vertical receive | Dual |

**Key Filters:**
```python
collection.filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'))
collection.filter(ee.Filter.eq('instrumentMode', 'IW'))
collection.filter(ee.Filter.eq('orbitProperties_pass', 'ASCENDING'))
```

---

### MODIS

**Vegetation Indices (16-day composite)**
```python
collection_id = 'MODIS/061/MOD13A1'  # 500m
collection_id = 'MODIS/061/MOD13Q1'  # 250m
```

| Band | Description | Scale Factor |
|------|-------------|--------------|
| NDVI | Normalized Difference Vegetation Index | 0.0001 |
| EVI | Enhanced Vegetation Index | 0.0001 |

**Land Surface Temperature**
```python
collection_id = 'MODIS/061/MOD11A1'  # Daily, 1km
```

---

### Digital Elevation Models

**SRTM (30m)**
```python
dem = ee.Image('USGS/SRTMGL1_003')
elevation = dem.select('elevation')
slope = ee.Terrain.slope(dem)
aspect = ee.Terrain.aspect(dem)
```

**Copernicus DEM (30m)**
```python
dem = ee.ImageCollection('COPERNICUS/DEM/GLO30').mosaic()
```

**ALOS World 3D (30m)**
```python
dem = ee.ImageCollection('JAXA/ALOS/AW3D30/V3_2').mosaic()
```

---

## Common Operations

### Cloud Masking

**Sentinel-2 (using SCL band)**
```python
def mask_s2_clouds(image):
    scl = image.select('SCL')
    mask = scl.neq(3).And(scl.neq(8)).And(scl.neq(9)).And(scl.neq(10))
    return image.updateMask(mask)

collection = collection.map(mask_s2_clouds)
```

**Landsat (using QA_PIXEL)**
```python
def mask_landsat_clouds(image):
    qa = image.select('QA_PIXEL')
    cloud_mask = qa.bitwiseAnd(1 << 3).eq(0)  # Cloud
    shadow_mask = qa.bitwiseAnd(1 << 4).eq(0)  # Cloud shadow
    return image.updateMask(cloud_mask.And(shadow_mask))
```

### Compositing

```python
# Median (good for removing clouds)
composite = collection.median()

# Greenest pixel (max NDVI)
def add_ndvi(image):
    ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
    return image.addBands(ndvi)

composite = collection.map(add_ndvi).qualityMosaic('NDVI')

# Percentile
composite = collection.reduce(ee.Reducer.percentile([25, 50, 75]))
```

### Spectral Indices

```python
# NDVI
ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')

# NDWI (water)
ndwi = image.normalizedDifference(['B3', 'B8']).rename('NDWI')

# NDBI (built-up)
ndbi = image.normalizedDifference(['B11', 'B8']).rename('NDBI')

# EVI
evi = image.expression(
    '2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))',
    {'NIR': image.select('B8'), 'RED': image.select('B4'), 'BLUE': image.select('B2')}
).rename('EVI')
```

---

## Export Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `scale` | Resolution in meters | Collection native |
| `maxPixels` | Maximum pixels to export | 1e8 |
| `region` | Export region geometry | Required |
| `crs` | Coordinate reference system | EPSG:4326 |
| `fileFormat` | Output format | GeoTIFF |
| `formatOptions` | Format-specific options | {} |

**Large Area Export (tiled)**
```python
# For very large areas, use fileDimensions to create tiles
task = ee.batch.Export.image.toDrive(
    image=composite,
    description='large_export',
    region=roi,
    scale=10,
    maxPixels=1e13,
    fileDimensions=[2048, 2048],  # Creates tiles
    fileFormat='GeoTIFF'
)
```

---

## Rate Limits and Quotas

| Limit | Value |
|-------|-------|
| Concurrent exports | 3000 |
| Max pixels per request | 1e8 (can increase with maxPixels) |
| getDownloadURL max size | ~32MB |
| Daily compute units | Varies by account type |

**Tips for Large Downloads:**
1. Use `toDrive` or `toCloudStorage` for large areas
2. Split into tiles using `fileDimensions`
3. Use lower resolution for initial exploration
4. Filter aggressively before exporting
