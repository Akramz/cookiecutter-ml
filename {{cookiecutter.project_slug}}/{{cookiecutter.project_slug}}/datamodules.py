"""
PyTorch Lightning DataModules for handling training, validation, and test datasets.

This module provides:
- DataModule classes for organizing datasets
- Train/val/test split functionality
- DataLoader configuration
- Data preprocessing and augmentation

Customize these components for your specific data requirements.
"""

from typing import Dict, List, Optional, Union, Callable, Any, Tuple

import lightning.pytorch as pl
import torch
from torch.utils.data import DataLoader, Dataset, random_split
import torchvision.transforms as T

from {{cookiecutter.project_slug}}.datasets import get_dataset, stack_samples


class BaseDataModule(pl.LightningDataModule):
    """Base DataModule for handling datasets and loaders."""
    
    def __init__(
        self,
        config,
        train_transforms=None,
        val_transforms=None,
        test_transforms=None,
        **kwargs
    ):
        """Initialize DataModule.
        
        Args:
            config: Configuration object
            train_transforms: Transforms for training data
            val_transforms: Transforms for validation data
            test_transforms: Transforms for test data
            **kwargs: Additional arguments
        """
        super().__init__()
        self.config = config
        self.batch_size = getattr(config, "batch_size", 32)
        self.num_workers = getattr(config, "num_workers", 4)
        self.val_ratio = getattr(config, "val_ratio", 0.2)
        self.test_ratio = getattr(config, "test_ratio", None)
        self.image_size = getattr(config, "image_size", (224, 224))
        self.seed = getattr(config, "seed", 42)
        
        # Set up transforms
        self.train_transforms = train_transforms or self._default_train_transforms()
        self.val_transforms = val_transforms or self._default_val_transforms()
        self.test_transforms = test_transforms or self._default_test_transforms()
        
        # Placeholders for datasets
        self.train_dataset = None
        self.val_dataset = None
        self.test_dataset = None
    
    def _default_train_transforms(self):
        """Default transforms for training data."""
        return T.Compose([
            T.RandomResizedCrop(self.image_size, scale=(0.8, 1.0)),
            T.RandomHorizontalFlip(),
            T.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.1),
            T.ToTensor(),
            T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
    
    def _default_val_transforms(self):
        """Default transforms for validation data."""
        return T.Compose([
            T.Resize(self.image_size),
            T.ToTensor(),
            T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
    
    def _default_test_transforms(self):
        """Default transforms for test data."""
        return T.Compose([
            T.Resize(self.image_size),
            T.ToTensor(),
            T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
    
    def prepare_data(self):
        """Prepare data - called once on an entire node's GPU."""
        # Data download/preparation could be done here if needed
        pass
    
    def setup(self, stage=None):
        """Set up datasets - called on every GPU.
        
        Args:
            stage: Current stage (fit, validate, test, predict)
        """
        if stage == "fit" or stage is None:

            # Create a single dataset for training and use random_split
            full_dataset = get_dataset(self.config, transform=self.train_transforms)
            
            # Determine splits
            dataset_size = len(full_dataset)
            val_size = int(dataset_size * self.val_ratio)
            train_size = dataset_size - val_size
            
            # Split dataset
            generator = torch.Generator().manual_seed(self.seed)
            self.train_dataset, self.val_dataset = random_split(
                full_dataset, [train_size, val_size], generator=generator
            )
            
            # Apply validation transforms
            # Note: this is a simplified approach - for complex cases, you may need
            # to create separate datasets with different transforms
            self.val_dataset.dataset = get_dataset(self.config, transform=self.val_transforms)
        
        if stage == "test" or stage is None:
            # For test data, you can either:
            # 1. Use a predetermined test split
            # 2. Use a separate test dataset
            # 3. Use the validation dataset as test
            
            # Option 3 (simplest) shown here:
            if self.test_dataset is None:
                if self.val_dataset is None:
                    full_dataset = get_dataset(self.config, transform=self.test_transforms)
                    dataset_size = len(full_dataset)
                    test_size = int(dataset_size * self.val_split)
                    _, self.test_dataset = random_split(
                        full_dataset, [dataset_size - test_size, test_size],
                        generator=torch.Generator().manual_seed(self.seed)
                    )
                else:
                    # Reuse validation dataset with test transforms
                    self.test_dataset = self.val_dataset
    
    def train_dataloader(self):
        """Create the training dataloader."""
        return DataLoader(
            self.train_dataset,
            batch_size=self.batch_size,
            shuffle=True,
            num_workers=self.num_workers,
            pin_memory=True,
            collate_fn=stack_samples
        )
    
    def val_dataloader(self):
        """Create the validation dataloader."""
        return DataLoader(
            self.val_dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=self.num_workers,
            pin_memory=True,
            collate_fn=stack_samples
        )
    
    def test_dataloader(self):
        """Create the test dataloader."""
        return DataLoader(
            self.test_dataset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=self.num_workers,
            pin_memory=True,
            collate_fn=stack_samples
        )


def get_datamodule(config, **kwargs):
    """Factory function to get DataModule by task type.
    
    Args:
        config: Configuration object
        **kwargs: Additional arguments for the DataModule
        
    Returns:
        DataModule instance
    """
    return BaseDataModule(config, **kwargs)