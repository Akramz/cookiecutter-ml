{% set is_open_source = cookiecutter.open_source_license != 'Not open source' -%}
# {{ cookiecutter.project_name }}

{% if is_open_source %}
[![PyPI](https://img.shields.io/pypi/v/{{ cookiecutter.project_slug }}.svg)](https://pypi.python.org/pypi/{{ cookiecutter.project_slug }})

[![Travis CI](https://img.shields.io/travis/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}.svg)](https://travis-ci.com/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }})

[![Documentation Status](https://readthedocs.org/projects/{{ cookiecutter.project_slug | replace("_", "-") }}/badge/?version=latest)](https://{{ cookiecutter.project_slug | replace("_", "-") }}.readthedocs.io/en/latest/?version=latest)
{%- endif %}

{% if cookiecutter.add_pyup_badge == 'y' %}
[![Updates](https://pyup.io/repos/github/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}/shield.svg)](https://pyup.io/repos/github/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}/)
{% endif %}

{{ cookiecutter.project_short_description }}

{% if is_open_source %}
* Free software: {{ cookiecutter.open_source_license }}
* Documentation: https://{{ cookiecutter.project_slug | replace("_", "-") }}.readthedocs.io.
{% endif %}

## Guidelines

What follows is a structured approach for developing your {{ cookiecutter.project_name }} project by organizing experiments, iterating quickly, and maintaining effective feedback loops.

## Step-by-Step Process

### 1. Set Up Experiment Tracking

* Create a [Google Sheet](https://docs.google.com/spreadsheets) with columns: Experiment ID, Description/Hypothesis, Key Parameters, Results/Metrics, Observations, Next Steps
* This sheet will be your central record for all experiments

### 2. Establish Baselines

* Implement simple baseline methods (random predictions, mode, median, mean, persistence)
* Document baseline results in your tracking sheet
* This gives you a reference point for improvement

### 3. Prepare Your Environment

* Create a Python environment:

```console
$ mamba create -n your_project_name python=3.10
```

* Activate it:

```console
$ conda activate your_project_name
```

* Install requirements:

```console
$ pip install -r requirements.txt
```

* Install package locally:

```console
$ pip install -e .
```

### 4. Organize Your Data

* Prepare dataset files or URLs using one of these approaches:
  
  - CSV file with pointers to input/output data
  - Local file paths organized in directories
  - Remote data URLs with access tokens

### 5. Run Your First Experiment

* Train a baseline model:

```console
$ python scripts/train.py --config configs/0_baselines/0_simple_baseline.yaml
```

* Evaluate the model:

```console
$ python scripts/evaluate.py --model-path model_runs/experiment_name/best.ckpt --test-data path/to/test
```

* Analyze errors:

```console
$ python scripts/analyze.py --model-path model_runs/experiment_name/best.ckpt --test-data path/to/test
```

* Document results in your tracking sheet

### 6. Iterative Improvement Loop

* Identify a specific change to implement based on error analysis
* Create a new configuration file in the appropriate `configs/` subdirectory
* Train the updated model using the new config
* Evaluate and analyze errors
* Document results in tracking sheet
* If performing better, consider producing a release
* Brainstorm ideas to reduce mistakes, prioritize and repeat

### 7. Hyperparameter Tuning

* Categorize hyperparameters:
  
  - Scientific: measure effect on performance
  - Nuisance: must be tuned for fair comparisons
  - Fixed: keep constant for now

* Run hyperparameter search:

```console
$ python scripts/train.py --config configs/0_baselines/0_simple_baseline.yaml --search_mode --n_trials 20
```

### 8. Speeding Up Experimentation

* For training: subsample data, increase batch size, maxout on GPU usage
* For inference: subsample test set
* For evaluation: parallelize and distribute training & evaluation jobs
* For analysis: focus on model collapses for faster error analysis

## Project Structure

The repository is organized as follows:

```text
{{cookiecutter.project_slug}}/ - Core implementation modules
|-- configs/            - YAML configuration files by research direction
|-- scripts/            - Training and evaluation scripts
|-- notebooks/          - Jupyter notebooks for analysis
|-- docs/               - Documentation and guides
```

## Customization

### 1. Define your data

* Update `datasets.py` with your data loading logic
* Configure input and output formats

### 2. Choose/implement models

* Select from standard models or add custom architectures in `models.py`
* Configure via YAML files

### 3. Set evaluation metrics

* Customize metrics in `trainers.py` for your specific task
* Add task-specific visualizations

### 4. Document your process

* Use your tracking sheet to record iterations
* Keep error analysis for each significant improvement

## Credits

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the [audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage) project template.