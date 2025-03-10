"""
Models module for implementing models.

This file serves as a placeholder where you can:
1. Define a custom model.
2. Import and adapt models from popular libraries.
3. Create model factory functions.

Examples of libraries you might want to use:
- TorchGeo: https://torchgeo.readthedocs.io/en/stable/api/models.html
- Segmentation Models PyTorch: https://github.com/qubvel/segmentation_models.pytorch
- Torchvision: https://pytorch.org/vision/stable/models.html
- Timm: https://github.com/huggingface/pytorch-image-models
"""

import torch
import torch.nn as nn


class CustomModel(nn.Module):
    """Example custom model. Replace with your implementation."""

    def __init__(self, config):
        """Initialize your model.

        Args:
            config: Configuration object containing model parameters
        """
        super().__init__()
        # TODO: Initialize your model architecture
        self.example_conv = nn.Conv2d(
            in_channels=config.in_channels, out_channels=64, kernel_size=3, padding=1
        )
        # Add more layers as needed

    def forward(self, x):
        """Forward pass.

        Args:
            x: Input tensor

        Returns:
            Model output
        """
        # TODO: Implement forward pass
        x = self.example_conv(x)
        # Process through other layers
        return x


def get_model(config):
    """Factory function to create a model instance from config.

    Args:
        config: Configuration object with model parameters

    Returns:
        A model instance
    """
    # TODO: Implement a factory function that returns the appropriate model
    # based on config.model_name and other parameters

    if config.model_name == "custom":
        return CustomModel(config)
    else:
        raise ValueError(
            f"Model '{config.model_name}' not implemented. Add it to the get_model function."
        )
