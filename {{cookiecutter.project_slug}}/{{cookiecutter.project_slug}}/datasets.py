"""
Dataset utilities for loading and preprocessing data.

This module provides base dataset classes and utility functions for:
- Loading image data from disk or remote sources
- Preprocessing and augmenting data
- Converting between different data formats

Customize these classes for your specific data structure and tasks.
"""

import os
from typing import Dict, List, Callable, Optional, Tuple, Union

import numpy as np
import torch
from torch.utils.data import Dataset
import torchvision.transforms as T
from PIL import Image
import pandas as pd


def stack_samples(samples):
    """Stack a list of samples into a batch.

    Args:
        samples: List of sample dictionaries

    Returns:
        Dictionary with stacked tensors
    """
    batch = {}
    for key in samples[0].keys():
        if isinstance(samples[0][key], torch.Tensor):
            batch[key] = torch.stack([s[key] for s in samples])
        else:
            batch[key] = [s[key] for s in samples]
    return batch


class BaseImageDataset(Dataset):
    """Base dataset for loading images and targets."""

    def __init__(
        self,
        image_paths: List[str],
        target_paths: Optional[List[str]] = None,
        transforms: Optional[Callable] = None,
        image_size: Tuple[int, int] = (224, 224),
    ):
        """Initialize dataset.

        Args:
            image_paths: List of paths to images
            target_paths: List of paths to targets (optional)
            transforms: Transforms to apply
            image_size: Size to resize images to
        """
        self.image_paths = image_paths
        self.target_paths = target_paths
        self.transforms = transforms
        self.image_size = image_size

        # Default transforms if none provided
        if self.transforms is None:
            self.transforms = T.Compose(
                [
                    T.Resize(image_size),
                    T.ToTensor(),
                    T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
                ]
            )

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        """Get dataset item.

        Args:
            idx: Index

        Returns:
            Dictionary with image and target
        """
        # Load image
        img_path = self.image_paths[idx]
        image = Image.open(img_path).convert("RGB")

        # Apply transforms
        image = self.transforms(image)

        # Create sample dictionary
        sample = {"image": image, "path": img_path}

        # Load target if available
        if self.target_paths is not None:
            target_path = self.target_paths[idx]
            target = Image.open(target_path).convert("L")
            target = T.Resize(self.image_size)(target)
            target = T.ToTensor()(target)
            sample["target"] = target

        return sample


def get_dataset(config, transform=None):
    """Get dataset based on configuration.

    Args:
        config: Configuration object
        transform: Optional transforms to apply

    Returns:
        Dataset instance
    """
    # Detect dataset type from input dirs
    input_dirs = config.input_dirs
    if isinstance(input_dirs, str):
        input_dirs = [input_dirs]

    if len(input_dirs) == 0:
        raise ValueError("No input directories specified")

    image_paths = []
    target_paths = []

    for directory in input_dirs:
        if not os.path.exists(directory):
            continue

        # Find all images with common extensions
        for ext in ["jpg", "jpeg", "png", "tif", "tiff"]:
            image_paths.extend(
                [
                    os.path.join(directory, f)
                    for f in os.listdir(directory)
                    if f.lower().endswith(f".{ext}")
                ]
            )

    return BaseImageDataset(
        image_paths=image_paths,
        target_paths=None,
        transforms=transform,
        image_size=getattr(config, "image_size", (224, 224)),
    )
