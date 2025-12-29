# New Experiment Slash Command

Create a new ML experiment following the project's config-driven workflow.

## Instructions

You are helping the user create a new experiment. Follow these steps:

### Step 1: Gather Information

First, ask the user the following questions using the AskUserQuestion tool:

**Question 1:** Does this experiment require a NEW hyperparameter that doesn't exist in `config.py` yet?

- **Yes, new hyperparameter** - Requires code changes (Type 2 experiment)
- **No, existing hyperparameter** - Config-only change (Type 1 experiment)

**Question 2:** Based on their answer:

- If **new hyperparameter**: Ask for:
  - The hyperparameter name (e.g., `dropout_rate`, `attention_heads`)
  - A description of how it should be implemented (which files it affects, default value, type)

- If **existing hyperparameter**: Ask for:
  - The hyperparameter name (must exist in `config.py`)
  - The value to use for this experiment

**Question 3:** Ask which research direction this experiment belongs to:
- `0_baselines` - Baseline methods
- `1_architectures` - Model architecture variants
- `2_augmentation` - Data augmentation strategies
- `3_regularization` - Regularization techniques
- Other (let them specify)

**Question 4:** Ask for the parent config path (e.g., `configs/0_baselines/00_baseline_default.yaml`)

### Step 2: Determine Experiment Number

Read the target research direction folder to find the next available experiment number:
```bash
ls configs/<research_direction>/
```
The new experiment should use the next sequential number (e.g., if `02_*` exists, use `03`).

### Step 3: Execute Based on Experiment Type

#### Type 1: Config-Only (Existing Hyperparameter)

1. **Create config stub** at `configs/<research_direction>/<exp_num>_<hp_name>_<hp_value>.yaml`:
   ```yaml
   # parent: <parent_config_path>
   experiment_name: "<exp_num>_<hp_name>_<hp_value>"
   <hp_name>: <hp_value>
   output_dir: "outputs/<exp_num>_<hp_name>_<hp_value>/"
   ```

2. **Validate** the config loads correctly by checking the parent config exists and the hyperparameter is valid.

3. **Add smoke command** - Print the command to run:
   ```bash
   python scripts/train.py --config configs/<research_direction>/<exp_name>.yaml
   ```

#### Type 2: New Hyperparameter (Code Changes Required)

1. **Update config.py** - Add the new field to `ExperimentConfig` (or `TrainerConfig` if it exists):
   ```python
   <hp_name>: Optional[<type>] = <default_value>
   ```

2. **Wire to runner** - Update `scripts/train.py`:
   - Add CLI argument if needed: `parser.add_argument("--<hp_name>", ...)`
   - Ensure the param is passed through the config override logic
   - Pass to model/task/datamodule as needed based on implementation description

3. **Propagate implementation** - Based on the user's description, update:
   - `models.py` - If it affects model architecture
   - `trainers.py` - If it affects training logic
   - `datamodules.py` - If it affects data loading
   - `datasets.py` - If it affects dataset processing

4. **Add logging keys** - If the hyperparameter should be logged:
   - Add to TensorBoard hyperparameter logging in `train.py`
   - Add to the training print summary

5. **Create config stub** at `configs/<research_direction>/<exp_num>_<hp_name>_<hp_value>.yaml`:
   ```yaml
   # parent: <parent_config_path>
   experiment_name: "<exp_num>_<hp_name>_<hp_value>"
   <hp_name>: <hp_value>
   output_dir: "outputs/<exp_num>_<hp_name>_<hp_value>/"
   ```

6. **Add smoke command** - Print the command to run:
   ```bash
   python scripts/train.py --config configs/<research_direction>/<exp_name>.yaml
   ```

### Step 4: Update Documentation

1. **Update `.claude/experiments.md`** if adding a new research direction
2. **Update `configs/README.md`** if the new hyperparameter is notable

### Step 5: Summary

After completing all steps, provide a summary:
- What was created/modified
- The experiment config path
- The command to run the experiment
- Any next steps or recommendations

## Example Outputs

### Type 1 Example (Config-Only)
```
Created experiment: configs/0_baselines/03_lr_0001.yaml
Parent: configs/0_baselines/00_baseline_default.yaml
Hyperparameter: learning_rate = 0.0001

Run with:
  python scripts/train.py --config configs/0_baselines/03_lr_0001.yaml
```

### Type 2 Example (New Hyperparameter)
```
Added new hyperparameter: dropout_rate (float, default=0.1)

Modified files:
  - {{cookiecutter.project_slug}}/config.py (added field)
  - scripts/train.py (added CLI arg, passed to task)
  - {{cookiecutter.project_slug}}/trainers.py (applied dropout)

Created experiment: configs/1_architectures/05_dropout_03.yaml
Parent: configs/0_baselines/00_baseline_default.yaml

Run with:
  python scripts/train.py --config configs/1_architectures/05_dropout_03.yaml
```