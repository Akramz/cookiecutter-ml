"""
PyTorch Lightning module for model training, validation, and testing.

This module provides:
- Base training logic for various computer vision tasks
- Metrics tracking and logging
- Visualization capabilities
- Customizable loss functions

Customize this file to fit your specific task and metrics needs.

Resources:
- https://torchgeo.readthedocs.io/en/latest/api/trainers.html
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import lightning.pytorch as pl
from lightning.pytorch import loggers as pl_loggers
import matplotlib.pyplot as plt
import numpy as np
from torchmetrics import MetricCollection
from torchmetrics.classification import Precision, Recall, F1Score
from torchmetrics.regression import MeanSquaredError, MeanAbsoluteError


class Task(pl.LightningModule):
    """Abstract base class for all TorchGeo trainers.

    .. versionadded:: 0.5
    """

    #: Parameters to ignore when saving hyperparameters.
    ignore: Sequence[str] | str | None = "weights"

    #: Model to train.
    model: Any

    #: Performance metric to monitor in learning rate scheduler and callbacks.
    monitor = "val_loss"

    #: Whether the goal is to minimize or maximize the performance metric to monitor.
    mode = "min"

    def __init__(self) -> None:
        """Initialize a new BaseTask instance.

        Args:
            ignore: Arguments to skip when saving hyperparameters.
        """
        super().__init__()
        self.save_hyperparameters(ignore=self.ignore)
        self.configure_models()
        self.configure_losses()
        self.configure_metrics()

    @abstractmethod
    def configure_models(self) -> None:
        """Initialize the model."""

    def configure_losses(self) -> None:
        """Initialize the loss criterion."""
        if loss_name == "mse":
            self.loss_fn = nn.MSELoss()
        elif loss_name == "bce":
            self.loss_fn = nn.BCEWithLogitsLoss()
        elif loss_name == "ce":
            self.loss_fn = nn.CrossEntropyLoss()
        elif loss_name == "huber":
            self.loss_fn = nn.HuberLoss(delta=0.7)
        else:
            raise ValueError(f"Unsupported loss: {loss_name}")

    def configure_metrics(self) -> None:
        """Initialize the performance metrics."""

    def configure_optimizers(self):
        """Configure optimizers and learning rate schedulers."""

        if self.hparams.optimizer == "adam":
            optimizer = torch.optim.Adam(
                self.parameters(),
                lr=self.hparams.learning_rate,
                weight_decay=self.hparams.weight_decay,
            )
        elif self.hparams.optimizer == "adamw":
            optimizer = torch.optim.AdamW(
                self.parameters(),
                lr=self.hparams.learning_rate,
                weight_decay=self.hparams.weight_decay,
            )
        elif self.hparams.optimizer == "sgd":
            optimizer = torch.optim.SGD(
                self.parameters(),
                lr=self.hparams.learning_rate,
                weight_decay=self.hparams.weight_decay,
                momentum=0.9,
            )
        elif self.hparams.optimizer == "rmsprop":
            optimizer = torch.optim.RMSprop(
                self.parameters(),
                lr=self.hparams.learning_rate,
                weight_decay=self.hparams.weight_decay,
            )
        else:
            raise ValueError(f"Unsupported optimizer: {self.hparams.optimizer}")

        # Configure scheduler
        if self.hparams.scheduler == "cosine":
            scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
                optimizer, T_max=self.hparams.get("t_max", 10), eta_min=1e-6
            )
            return {
                "optimizer": optimizer,
                "lr_scheduler": scheduler,
                "monitor": "val_loss",
            }

        elif self.hparams.scheduler == "plateau":
            scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
                optimizer,
                patience=self.hparams.get("patience", 10),
                factor=self.hparams.get("factor", 0.1),
            )
            return {
                "optimizer": optimizer,
                "lr_scheduler": scheduler,
                "monitor": "val_loss",
            }

        elif self.hparams.scheduler == "step":
            scheduler = torch.optim.lr_scheduler.StepLR(
                optimizer,
                step_size=self.hparams.get("step_size", 30),
                gamma=self.hparams.get("gamma", 0.1),
            )
            return {"optimizer": optimizer, "lr_scheduler": scheduler}

        elif self.hparams.scheduler == "none" or self.hparams.scheduler is None:
            return {"optimizer": optimizer}

        else:
            raise ValueError(f"Unsupported scheduler: {self.hparams.scheduler}")

    def forward(self, *args: Any, **kwargs: Any) -> Any:
        """Forward pass of the model.

        Args:
            args: Arguments to pass to model.
            kwargs: Keyword arguments to pass to model.

        Returns:
            Output of the model.
        """
        return self.model(*args, **kwargs)

    def training_step(self, batch, batch_idx):

        # Calculate loss
        x, y = batch["image"], batch["target"]
        y_hat = self(x)
        loss = self.loss_fn(y_hat, y)

        # Update and log metrics
        self.train_metrics(y_hat, y)
        self.log("train_loss", loss)
        self.log_dict(self.train_metrics)

        # Visualize training examples occasionally
        if batch_idx % 100 == 0:
            self.visualize_batch(x, y, y_hat, "train", batch_idx)

        return loss

    def validation_step(self, batch, batch_idx):

        # Calculate validation loss
        x, y = batch["image"], batch["target"]
        y_hat = self(x)
        loss = self.loss_fn(y_hat, y)

        # Update and log metrics
        self.val_metrics(y_hat, y)
        self.log("val_loss", loss)
        self.log_dict(self.val_metrics)

        # Visualize validation examples occasionally
        if batch_idx == 0:
            self.visualize_batch(x, y, y_hat, "val", self.current_epoch)

    def test_step(self, batch, batch_idx):
        # Update and log metrics
        x, y = batch["image"], batch["target"]
        y_hat = self(x)
        self.test_metrics(y_hat, y)
        self.log_dict(self.test_metrics)

    def visualize_batch(self, x, y, y_hat, stage, idx):
        # Customize this method based on your task/data
        pass


def get_task(task_type, model, **kwargs):
    """Factory function to get task by type.

    Args:
        task_type: Type of task (segmentation, regression, classification)
        model: Model to use
        **kwargs: Additional arguments for the task

    Returns:
        LightningModule instance
    """
    return Task(model, **kwargs)
