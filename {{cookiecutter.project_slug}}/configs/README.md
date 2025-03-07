# Configuration Files

This directory contains YAML configuration files for model training. Each file defines a unique experiment setup, files may include model architecture, hyperparameters, and training parameters (depending on the training setup).

## Directory Structure

Configuration files are organized by research direction, with each sub-directory representing a specific branch of investigation:

```
configs/
├── 0_baselines/         # Initial baseline experiments
├── 1_architectures/     # Testing different model architecturess
├── 2_data_augmentation/ # Exploring augmentation strategies
└── ...                  # Additional research directions
```

## Creating New Experiments

After deciding on a research direction:

1. **Create a new branch and checkout to it**.
2. **Start from an existing configuration**: Copy a relevant config file as your starting point
3. **Change only what's needed**: Modify only the parameters you want to test
4. **Implement new configurations**: to enable a switch (i.e., on/off) to test your new ideas.
5. **Run training** to compare with the best previous setup.

## Experiment Naming Convention

Within each research direction, use a clear naming convention for experiment configs:

```
0_baselines/
├── 0_persistance.yaml
├── 1_climatology.yaml
└── 2_median.yaml

1_architectures/
├── 0_resnet18.yaml
├── 1_resnet50.yaml
└── 2_efficientnet.yaml
```

## Scientific vs. Nuisance Hyperparameters

When designing experiments, distinguish between:

- **Scientific hyperparameters**: Those you want to scientifically measure the effect of (e.g., model architecture, loss function)
- **Nuisance hyperparameters**: Those that must be tuned for fair comparison but aren't the focus (e.g., learning rate, batch size)
- **Fixed hyparameteres**: shouldn't change from one experiment to the next.

Group your hyperparameters by the above categories in the YAML files.

To find optimal values for nuisance hyperparameters, use the hyperparameter search mode:

```bash
python scripts/train.py --config configs/0_baselines/0_simple_baseline.yaml --search_mode --n_trials 20 --lr_range 1e-5,1e-2
```
