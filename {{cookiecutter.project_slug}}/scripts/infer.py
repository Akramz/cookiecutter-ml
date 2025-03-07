"""
Inference script for semantic segmentation of satellite imagery.

This script:
1. Loads a trained model checkpoint
2. Processes input GeoTIFF files 
3. Generates and saves prediction masks as GeoTIFF files
4. Preserves geospatial metadata during processing

Usage:
    python infer.py --checkpoint path/to/model.ckpt --input_list path/to/files.txt --output_dir path/to/output
"""
import argparse
import os
import warnings
from pathlib import Path
import time
import json
import collections
from typing import Dict, List, Optional, Union, Any

import numpy as np
import rasterio
import torch
from torch import Tensor
from torch.utils.data import DataLoader, Dataset
from tqdm import tqdm

from {{cookiecutter.project_slug}}.trainers import get_task

# Set environment variables for better rasterio performance
rasterio_best_practices = {
    "GDAL_DISABLE_READDIR_ON_OPEN": "EMPTY_DIR",
    "GDAL_MAX_RAW_BLOCK_CACHE_SIZE": "200000000",
    "GDAL_SWATH_SIZE": "200000000",
    "VSI_CURL_CACHE_SIZE": "200000000",
}
os.environ.update(rasterio_best_practices)

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)


def _list_dict_to_dict_list(samples: List[Dict]) -> Dict[str, List]:
    """Convert a list of dictionaries to a dictionary of lists.
    
    Args:
        samples: List of sample dictionaries
        
    Returns:
        Dictionary of lists
    """
    collated = collections.defaultdict(list)
    for sample in samples:
        if sample is not None:
            for key, value in sample.items():
                collated[key].append(value)
    return collated


def stack_samples(samples: List[Dict]) -> Optional[Dict[str, Any]]:
    """Stack samples for batch processing.
    
    Args:
        samples: List of sample dictionaries
        
    Returns:
        Stacked samples or None if all samples are None
    """
    # If all samples are None, return None
    if all(sample is None for sample in samples):
        return None

    collated = _list_dict_to_dict_list(samples)
    # If no valid samples after filtering None values
    if not collated:
        return None

    # Stack tensor samples
    for key, value in collated.items():
        if isinstance(value[0], Tensor):
            collated[key] = torch.stack(value)
    return collated


class GeoTIFFDataset(Dataset):
    """Dataset for loading GeoTIFF files for inference."""
    
    def __init__(self, file_list: List[str], transforms=None):
        """Initialize dataset.
        
        Args:
            file_list: List of file paths to process
            transforms: Optional transforms to apply to samples
        """
        self.file_list = file_list
        self.transforms = transforms

    def __len__(self) -> int:
        """Get dataset length."""
        return len(self.file_list)

    def __getitem__(self, idx: int) -> Optional[Dict[str, Any]]:
        """Get a sample from the dataset.
        
        Args:
            idx: Sample index
            
        Returns:
            Sample dictionary or None if loading fails
        """
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Get file path
                file_path = self.file_list[idx]
                
                # Load image with rasterio
                with rasterio.open(file_path) as src:
                    # Get metadata
                    bounds = tuple(src.bounds)
                    transform = src.transform
                    crs = src.crs
                    
                    # Read image data
                    # For RGB images, we read bands 1, 2, 3
                    if src.count >= 3:
                        image = src.read([1, 2, 3]).astype(np.float32)
                    else:
                        image = src.read().astype(np.float32)
                
                # Create sample dictionary
                sample = {
                    "image": torch.from_numpy(image),
                    "file_path": file_path,
                    "bounds": bounds,
                    "transform": transform,
                    "crs": crs,
                    "height": image.shape[1],
                    "width": image.shape[2]
                }
                
                # Apply transforms if available
                if self.transforms is not None:
                    sample = self.transforms(sample)
                
                return sample
                
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"Retry {attempt+1}/{max_retries} for {file_path}: {e}")
                    time.sleep(1)  # Small delay before retrying
                else:
                    print(f"Failed to read {file_path} after {max_retries} attempts: {e}")
                    return None


def save_prediction(prediction: np.ndarray, metadata: Dict, output_path: str) -> None:
    """Save prediction as a GeoTIFF file.
    
    Args:
        prediction: Prediction array [C, H, W]
        metadata: Metadata dictionary with CRS, transform, etc.
        output_path: Output file path
    """
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Create profile for the output file
    profile = {
        "driver": "GTiff",
        "height": prediction.shape[1],
        "width": prediction.shape[2],
        "count": prediction.shape[0],
        "dtype": prediction.dtype,
        "crs": metadata["crs"],
        "transform": metadata["transform"],
        "compress": "lzw",
        "predictor": 3,  # Floating point predictor for better compression
        "tiled": True,
        "blockxsize": 256,
        "blockysize": 256,
    }
    
    # Write output
    with rasterio.open(output_path, 'w', **profile) as dst:
        for i in range(prediction.shape[0]):
            dst.write(prediction[i], i + 1)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run inference on GeoTIFF images")
    
    # Required arguments
    parser.add_argument(
        "--checkpoint",
        required=True,
        type=str,
        help="Path to model checkpoint (.ckpt format)"
    )
    parser.add_argument(
        "--input_list",
        required=True,
        type=str,
        help="Path to text file containing list of input file paths (one per line)"
    )
    parser.add_argument(
        "--output_dir",
        required=True,
        type=str,
        help="Directory to save prediction outputs"
    )
    
    # Optional arguments
    parser.add_argument(
        "--batch_size",
        type=int,
        default=1,
        help="Batch size for inference"
    )
    parser.add_argument(
        "--num_workers",
        type=int,
        default=4,
        help="Number of workers for data loading"
    )
    parser.add_argument(
        "--gpu",
        type=int,
        default=None,
        help="GPU ID to use for inference (default: None = CPU)"
    )
    parser.add_argument(
        "--file_suffix",
        type=str,
        default="_prediction.tif",
        help="Suffix to add to output filenames"
    )
    
    return parser.parse_args()


def main():
    """Run inference script."""
    # Parse arguments
    args = parse_args()
    
    # Set device
    device = torch.device(f"cuda:{args.gpu}" if args.gpu is not None and torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Load input file list
    with open(args.input_list, "r") as f:
        file_list = [line.strip() for line in f.readlines() if line.strip()]
    
    print(f"Loaded {len(file_list)} files for inference")
    
    # Load checkpoint
    print(f"Loading model from {args.checkpoint}")
    task = get_task("segmentation", None)  # The model will be loaded from checkpoint
    task = task.load_from_checkpoint(args.checkpoint, map_location=device)
    task.freeze()
    model = task.model.eval()
    
    # Create dataset and dataloader
    dataset = GeoTIFFDataset(file_list)
    dataloader = DataLoader(
        dataset,
        batch_size=args.batch_size,
        num_workers=args.num_workers,
        pin_memory=True,
        collate_fn=stack_samples
    )
    
    # Process images
    processed = 0
    failed = []
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Run inference
    print("Starting inference...")
    with torch.no_grad():
        for batch in tqdm(dataloader, desc="Processing"):
            if batch is None:
                continue
            
            # Move data to device
            images = batch["image"].to(device)
            file_paths = batch["file_path"]
            
            try:
                # Run inference
                predictions = model(images).cpu().numpy()
                
                # Process each prediction in the batch
                for i in range(len(images)):
                    # Get metadata
                    metadata = {
                        "crs": batch["crs"][i],
                        "transform": batch["transform"][i],
                        "height": batch["height"][i],
                        "width": batch["width"][i]
                    }
                    
                    # Create output path
                    input_path = Path(file_paths[i])
                    output_name = f"{input_path.stem}{args.file_suffix}"
                    output_path = os.path.join(args.output_dir, output_name)
                    
                    # Get single prediction from batch
                    prediction = predictions[i]
                    
                    # Save prediction
                    save_prediction(prediction, metadata, output_path)
                    processed += 1
                    
            except Exception as e:
                print(f"Error processing batch: {e}")
                for path in file_paths:
                    failed.append((path, str(e)))
    
    # Print summary
    print(f"\nInference complete:")
    print(f"Successfully processed: {processed}")
    print(f"Failed: {len(failed)}")
    
    # Save failed files list
    if failed:
        failed_path = os.path.join(args.output_dir, "failed_files.json")
        with open(failed_path, "w") as f:
            json.dump(failed, f, indent=2)
        print(f"List of failed files saved to: {failed_path}")


if __name__ == "__main__":
    main()
