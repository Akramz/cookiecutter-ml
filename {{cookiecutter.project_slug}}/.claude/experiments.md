# Experiment Rules

> **Quick Start:** Use the `/new-experiment` slash command to create experiments interactively.

## Two Types of Experiments

### Type 1: Existing Hyperparameter (Config-Only)

No code changes needed. Fork from a parent experiment:

```yaml
# parent: configs/0_baselines/00_baseline_default.yaml
experiment_name: "01_lr_1e4"
learning_rate: 0.0001  # changed from 0.001
...
```

Steps:
1. Copy parent config to new file
2. Add `# parent: <path>` comment at top
3. Modify the hyperparameter(s) being tested
4. Run: `python scripts/train.py --config configs/<dir>/<name>.yaml`

### Type 2: New Hyperparameter (Code Change)

Requires adding support for the new param:

1. **config.py**: Add a field for the new hyperparameter where appropriate with type hint and default
2. **train.py**: Pass the new param where needed
3. **Other files**: Propagate the implementation to models.py, datasets.py, etc. as needed
4. Create config YAML using the new param
5. Run: `python scripts/train.py --config configs/<dir>/<name>.yaml`

## Config Organization

```
configs/
├── 0_baselines/        # Simple methods (random, median, heuristics)
├── 1_architectures/    # Model architecture variants
├── 2_augmentation/     # Data augmentation strategies
├── 3_regularization/   # Regularization techniques
└── ...                 # Add directions as research evolves
```

## Naming

Format: `{EXP_NUM}_{HP_NAME}_{HP_VALUE}.yaml`

- `EXP_NUM`: 2-digit experiment number (00, 01, 02, ...)
- `HP_NAME`: Hyperparameter name being tested
- `HP_VALUE`: Value or variant being tested

Examples:
- `00_baseline_default.yaml` (root baseline)
- `01_lr_1e4.yaml`
- `02_lr_1e3.yaml`
- `03_batch_64.yaml`
- `04_arch_resnet50.yaml`

## Rules

- Baselines have no parent (they are roots)
- All other experiments must declare their parent
- Change ONE variable at a time when comparing
- Checkpoints save to `model_runs/<experiment_name>/`
