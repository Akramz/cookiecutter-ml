{% set is_open_source = cookiecutter.open_source_license != 'Not open source' -%}
{% for _ in cookiecutter.project_name %}={% endfor %}
{{ cookiecutter.project_name }}
{% for _ in cookiecutter.project_name %}={% endfor %}

{% if is_open_source %}
.. image:: https://img.shields.io/pypi/v/{{ cookiecutter.project_slug }}.svg
        :target: https://pypi.python.org/pypi/{{ cookiecutter.project_slug }}

.. image:: https://img.shields.io/travis/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}.svg
        :target: https://travis-ci.com/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}

.. image:: https://readthedocs.org/projects/{{ cookiecutter.project_slug | replace("_", "-") }}/badge/?version=latest
        :target: https://{{ cookiecutter.project_slug | replace("_", "-") }}.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status
{%- endif %}

{% if cookiecutter.add_pyup_badge == 'y' %}
.. image:: https://pyup.io/repos/github/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}/shield.svg
     :target: https://pyup.io/repos/github/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}/
     :alt: Updates
{% endif %}


{{ cookiecutter.project_short_description }}

{% if is_open_source %}
* Free software: {{ cookiecutter.open_source_license }}
* Documentation: https://{{ cookiecutter.project_slug | replace("_", "-") }}.readthedocs.io.
{% endif %}

Guidelines
---------

What follows is a structured approach for developing your {{ cookiecutter.project_name }} project by organizing experiments, iterating quickly, and maintaining effective feedback loops.

Step-by-Step Process
-------------------

1. **Set Up Experiment Tracking**
   
   * Create a `Google Sheet <https://docs.google.com/spreadsheets>`_ with columns: Experiment ID, Description/Hypothesis, Key Parameters, Results/Metrics, Observations, Next Steps
   * This sheet will be your central record for all experiments

2. **Establish Baselines**
   
   * Implement simple baseline methods (random predictions, mode, median, mean, persistence)
   * Document baseline results in your tracking sheet
   * This gives you a reference point for improvement

3. **Prepare Your Environment**
   
   * Create a Python environment:
   
     .. code-block:: console
         
         $ mamba create -n your_project_name python=3.10
   
   * Activate it:
   
     .. code-block:: console
         
         $ conda activate your_project_name
   
   * Install requirements:
   
     .. code-block:: console
         
         $ pip install -r requirements.txt
   
   * Install package locally:
   
     .. code-block:: console
         
         $ pip install -e .

4. **Organize Your Data**
   
   * Prepare dataset files or URLs using one of these approaches:
     
     - CSV file with pointers to input/output data
     - Local file paths organized in directories
     - Remote data URLs with access tokens

5. **Run Your First Experiment**
   
   * Train a baseline model:
   
     .. code-block:: console
         
         $ python scripts/train.py --config configs/0_baselines/0_simple_baseline.yaml
   
   * Evaluate the model:
   
     .. code-block:: console
         
         $ python scripts/evaluate.py --model-path model_runs/experiment_name/best.ckpt --test-data path/to/test
   
   * Analyze errors:
   
     .. code-block:: console
         
         $ python scripts/analyze.py --model-path model_runs/experiment_name/best.ckpt --test-data path/to/test
   
   * Document results in your tracking sheet

6. **Iterative Improvement Loop**
   
   * Identify a specific change to implement based on error analysis
   * Create a new configuration file in the appropriate ``configs/`` subdirectory
   * Train the updated model using the new config
   * Evaluate and analyze errors
   * Document results in tracking sheet
   * If performing better, consider producing a release
   * Brainstorm ideas to reduce mistakes, prioritize and repeat

7. **Hyperparameter Tuning**
   
   * Categorize hyperparameters:
     
     - Scientific: measure effect on performance
     - Nuisance: must be tuned for fair comparisons
     - Fixed: keep constant for now
   
   * Run hyperparameter search:
   
     .. code-block:: console
         
         $ python scripts/train.py --config configs/0_baselines/0_simple_baseline.yaml --search_mode --n_trials 20

8. **Speeding Up Experimentation**
   
   * For training: subsample data, increase batch size, maxout on GPU usage
   * For inference: subsample test set
   * For evaluation: parallelize and distribute training & evaluation jobs
   * For analysis: focus on model collapses for faster error analysis

Project Structure
----------------

The repository is organized as follows:

.. code-block:: text

    {{cookiecutter.project_slug}}/ - Core implementation modules
    |-- configs/            - YAML configuration files by research direction
    |-- scripts/            - Training and evaluation scripts
    |-- notebooks/          - Jupyter notebooks for analysis
    |-- docs/               - Documentation and guides

Customization
------------

1. **Define your data**:
   
   * Update ``datasets.py`` with your data loading logic
   * Configure input and output formats

2. **Choose/implement models**:
   
   * Select from standard models or add custom architectures in ``models.py``
   * Configure via YAML files

3. **Set evaluation metrics**:
   
   * Customize metrics in ``trainers.py`` for your specific task
   * Add task-specific visualizations

4. **Document your process**:
   
   * Use your tracking sheet to record iterations
   * Keep error analysis for each significant improvement

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage