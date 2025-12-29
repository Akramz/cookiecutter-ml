#!/usr/bin/env python3
"""
Download imagery from any Google Earth Engine ImageCollection.

Usage:
    # Download a composite
    python download_imagery.py \
        --collection COPERNICUS/S2_SR_HARMONIZED \
        --start-date 2023-01-01 \
        --end-date 2023-12-31 \
        --roi path/to/roi.geojson \
        --output-dir data/raw/imagery/ \
        --composite median

    # Download full time series (one file per image)
    python download_imagery.py \
        --collection COPERNICUS/S1_GRD \
        --start-date 2023-01-01 \
        --end-date 2023-03-31 \
        --roi -122.5,37.5,-122.0,38.0 \
        --output-dir data/raw/imagery/
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

try:
    import ee
except ImportError:
    print("Error: earthengine-api not installed. Run: pip install earthengine-api")
    sys.exit(1)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Download imagery from Google Earth Engine"
    )
    parser.add_argument(
        "--collection",
        type=str,
        required=True,
        help="GEE ImageCollection ID (e.g., COPERNICUS/S2_SR_HARMONIZED)",
    )
    parser.add_argument(
        "--start-date",
        type=str,
        required=True,
        help="Start date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--end-date",
        type=str,
        required=True,
        help="End date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--roi",
        type=str,
        required=True,
        help="Region of interest: GeoJSON file path or bbox 'west,south,east,north'",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/raw/imagery/",
        help="Output directory for downloaded imagery",
    )
    parser.add_argument(
        "--bands",
        type=str,
        default=None,
        help="Comma-separated list of bands to download (default: all)",
    )
    parser.add_argument(
        "--scale",
        type=int,
        default=10,
        help="Output resolution in meters (default: 10)",
    )
    parser.add_argument(
        "--composite",
        type=str,
        default=None,
        choices=["median", "mean", "min", "max", "mosaic"],
        help="Composite method. If not set, downloads full time series.",
    )
    parser.add_argument(
        "--name",
        type=str,
        default=None,
        help="Output filename prefix (default: derived from collection)",
    )
    parser.add_argument(
        "--crs",
        type=str,
        default="EPSG:4326",
        help="Coordinate reference system (default: EPSG:4326)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print info without downloading",
    )
    return parser.parse_args()


def load_roi(roi_arg: str) -> ee.Geometry:
    """Load region of interest from file or coordinates."""
    if os.path.exists(roi_arg):
        with open(roi_arg) as f:
            geojson = json.load(f)
        if geojson["type"] == "FeatureCollection":
            geometry = geojson["features"][0]["geometry"]
        elif geojson["type"] == "Feature":
            geometry = geojson["geometry"]
        else:
            geometry = geojson
        return ee.Geometry(geometry)

    # Parse as bbox (west,south,east,north) or point (lon,lat)
    try:
        coords = [float(x) for x in roi_arg.split(",")]
        if len(coords) == 4:
            return ee.Geometry.Rectangle(coords)
        elif len(coords) == 2:
            return ee.Geometry.Point(coords).buffer(5000)
        else:
            raise ValueError(f"Invalid coordinates: {roi_arg}")
    except ValueError as e:
        print(f"Error parsing ROI: {e}")
        sys.exit(1)


def create_composite(collection: ee.ImageCollection, method: str) -> ee.Image:
    """Create composite from collection."""
    if method == "median":
        return collection.median()
    elif method == "mean":
        return collection.mean()
    elif method == "min":
        return collection.min()
    elif method == "max":
        return collection.max()
    elif method == "mosaic":
        return collection.mosaic()
    else:
        raise ValueError(f"Unknown composite method: {method}")


def download_image(image: ee.Image, roi: ee.Geometry, output_path: Path,
                   scale: int, crs: str, bands: list = None) -> bool:
    """Download a single image via direct URL."""
    import requests

    if bands:
        image = image.select(bands)

    try:
        url = image.getDownloadURL({
            "scale": scale,
            "region": roi,
            "format": "GEO_TIFF",
            "crs": crs,
        })
        response = requests.get(url, timeout=600)
        response.raise_for_status()

        with open(output_path, "wb") as f:
            f.write(response.content)
        return True

    except Exception as e:
        print(f"  Error downloading: {e}")
        return False


def main():
    args = parse_args()

    # Initialize Earth Engine
    print("Initializing Google Earth Engine...")
    try:
        ee.Initialize()
    except Exception as e:
        print(f"Error: {e}")
        print("Run: python .claude/skills/gee-imagery/scripts/authenticate.py")
        sys.exit(1)

    # Load ROI
    print(f"Loading ROI: {args.roi}")
    roi = load_roi(args.roi)

    # Load and filter collection
    print(f"Loading collection: {args.collection}")
    collection = (ee.ImageCollection(args.collection)
        .filterBounds(roi)
        .filterDate(args.start_date, args.end_date))

    count = collection.size().getInfo()
    print(f"Found {count} images")

    if count == 0:
        print("No images found. Check collection ID, date range, and ROI.")
        sys.exit(1)

    # Parse bands
    bands = [b.strip() for b in args.bands.split(",")] if args.bands else None

    # Generate output name prefix
    if args.name:
        name_prefix = args.name
    else:
        name_prefix = args.collection.replace("/", "_").lower()

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.dry_run:
        print("\n--- Dry Run ---")
        print(f"Collection: {args.collection}")
        print(f"Date range: {args.start_date} to {args.end_date}")
        print(f"Image count: {count}")
        print(f"Composite: {args.composite or 'None (time series)'}")
        print(f"Scale: {args.scale}m")
        print(f"Bands: {bands or 'all'}")
        print(f"Output: {output_dir}")
        return

    if args.composite:
        # Download single composite
        print(f"Creating {args.composite} composite...")
        image = create_composite(collection, args.composite).clip(roi)

        output_path = output_dir / f"{name_prefix}_{args.start_date}_{args.end_date}_{args.composite}.tif"
        print(f"Downloading: {output_path}")

        if download_image(image, roi, output_path, args.scale, args.crs, bands):
            print(f"Saved: {output_path}")
        else:
            print("Download failed")
            sys.exit(1)

    else:
        # Download full time series
        print("Downloading time series...")
        image_list = collection.toList(count)

        downloaded = 0
        failed = 0

        for i in range(count):
            image = ee.Image(image_list.get(i))

            # Get image date for filename
            try:
                date = ee.Date(image.get("system:time_start")).format("YYYY-MM-dd").getInfo()
                image_id = image.get("system:index").getInfo()
            except Exception:
                date = f"image_{i:04d}"
                image_id = str(i)

            output_path = output_dir / f"{name_prefix}_{date}_{i:04d}.tif"
            print(f"  [{i+1}/{count}] {output_path.name}")

            if download_image(image.clip(roi), roi, output_path, args.scale, args.crs, bands):
                downloaded += 1
            else:
                failed += 1

        print(f"\nComplete: {downloaded} downloaded, {failed} failed")

    # Save metadata
    metadata = {
        "collection": args.collection,
        "start_date": args.start_date,
        "end_date": args.end_date,
        "image_count": count,
        "composite": args.composite,
        "scale": args.scale,
        "bands": bands,
        "crs": args.crs,
        "created_at": datetime.now().isoformat(),
    }

    metadata_path = output_dir / f"{name_prefix}_metadata.json"
    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"Metadata: {metadata_path}")


if __name__ == "__main__":
    main()
