# Project Rules

## Project Structure

```
configs/           # YAML experiment configs (organized by research direction)
scripts/           # Production scripts: `train.py`, `evaluate.py`, `infer.py`
notebooks/         # Exploration only (gitignored, never production)
{{cookiecutter.project_slug}}/  # Reusable modules: models, datasets, trainers, config
```

## Workflow

### 1. Experiments are Config-Driven

Every experiment lives in `configs/` as a YAML file validated by Pydantic (`config.py`).

```bash
# Run an experiment
python scripts/train.py --config configs/0_baselines/hello_world.yaml

# Override params from CLI
python scripts/train.py --config configs/0_baselines/exp.yaml --learning_rate 1e-4

# Hyperparameter search
python scripts/train.py --config configs/0_baselines/exp.yaml --search_mode --n_trials 20
```

**When creating experiments:** duplicate an existing config, modify, and run. Never edit shared module code just to try a new hyperparameter.

### 2. Notebooks vs Scripts

| Notebooks | Scripts |
|-----------|---------|
| Exploration, EDA, prototyping | Production, reproducibility |
| Quick iteration, visualization | CLI-driven, config-validated |
| Disposable, local-only | Version-controlled, tested |

**Rule:** If code will be reused or needs reproducibility, move it to `scripts/` or the package.

### 3. Research Flow

```
Scope Project --> Collect Data --> Preprocess --> Baseline --> Evaluate --> Error Analysis --> Brainstorm --> Iterate Over Experiments
```

### 4. Error Analysis

After every evaluation:
1. Identify worst-performing slices/examples
2. Hypothesize failure modes
3. Create new config targeting that failure
4. Run experiment, repeat

### 5. Hyperparameter Discipline

- **Scientific params:** Measured for effect (architecture, loss)
- **Nuisance params:** Tuned for fair comparison (lr, batch_size)
- **Fixed params:** Constant across experiments (seed, epochs for comparison)

## Commands

```bash
make lint          # Check code style
make test          # Run tests
make clean         # Remove artifacts
python scripts/train.py --config <path>      # Train
python scripts/evaluate.py --model_path <path> --test_data <path>  # Evaluate
python scripts/infer.py --model_path <path> --input <path>         # Inference
```

## Code Style

- Type hints on all function signatures in `{{cookiecutter.project_slug}}/`
- Pydantic models for all configs
- PyTorch Lightning for training logic
- Factory functions for models/datasets (see `models.py`, `datasets.py`)

## Claude Code Slash Commands

Custom commands available for common data science workflows:

| Command | Description |
|---------|-------------|
| `/new-experiment` | Create a new experiment (config-only or with new hyperparameter) |

Usage: Type the command in Claude Code to trigger the workflow.

## Claude Code Skills

Skills are automatically invoked by Claude when relevant to your task:

| Skill | Description |
|-------|-------------|
| `gee-imagery` | Download remote sensing imagery from Google Earth Engine |

**GEE Imagery Skill** - Automatically activates when you mention:
- "Download satellite imagery"
- "Get Sentinel/Landsat/MODIS data"
- "Acquire imagery for region"
- "Export from Earth Engine"

Example: "Download Sentinel-2 imagery for my study area from 2023"

## Rules
- Delete unused or obsolete files when your changes make them irrelevant (refactors, feature removals, etc.), and revert files only when the change is yours or explicitly requested. If a git operation leaves you unsure about other agents' in-flight work, stop and coordinate instead of deleting.
- **Before attempting to delete a file to resolve a local type/lint failure, stop and ask the user.** Other agents are often editing adjacent files; deleting their work to silence an error is never acceptable without explicit approval.
- NEVER edit `.env` or any environment variable files—only the user may change them.
- Coordinate with other agents before removing their in-progress edits—don't revert or delete work you didn't author unless everyone agrees.
- Moving/renaming and restoring files is allowed.
- ABSOLUTELY NEVER run destructive git operations (e.g., `git reset --hard`, `rm`, `git checkout`/`git restore` to an older commit) unless the user gives an explicit, written instruction in this conversation. Treat these commands as catastrophic; if you are even slightly unsure, stop and ask before touching them. *(When working within Cursor or Codex Web, these git limitations do not apply; use the tooling's capabilities as needed.)*
- Never use `git restore` (or similar commands) to revert files you didn't author—coordinate with other agents instead so their in-progress work stays intact.
- Always double-check git status before any commit
- Keep commits atomic: commit only the files you touched and list each path explicitly. For tracked files run `git commit -m "<scoped message>" -- path/to/file1 path/to/file2`. For brand-new files, use the one-liner `git restore --staged :/ && git add "path/to/file1" "path/to/file2" && git commit -m "<scoped message>" -- path/to/file1 path/to/file2`.
- Quote any git paths containing brackets or parentheses (e.g., `src/app/[candidate]/**`) when staging or committing so the shell does not treat them as globs or subshells.
- When running `git rebase`, avoid opening editors—export `GIT_EDITOR=:` and `GIT_SEQUENCE_EDITOR=:` (or pass `--no-edit`) so the default messages are used automatically.
- Never amend commits unless you have explicit written approval in the task thread.
