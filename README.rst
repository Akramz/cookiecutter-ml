======================
Cookiecutter Machine Learning
======================

.. image:: https://pyup.io/repos/github/audreyfeldroy/cookiecutter-pypackage/shield.svg
    :target: https://pyup.io/repos/github/audreyfeldroy/cookiecutter-pypackage/
    :alt: Updates

.. image:: https://travis-ci.org/audreyfeldroy/cookiecutter-pypackage.svg?branch=master
    :target: https://travis-ci.org/github/audreyfeldroy/cookiecutter-pypackage
    :alt: Build Status

.. image:: https://readthedocs.org/projects/cookiecutter-pypackage/badge/?version=latest
    :target: https://cookiecutter-pypackage.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

Cookiecutter_ template for productive machine learning.

* Current GitHub repo: https://github.com/Akramz/cookiecutter-ml
* Original GitHub repo: https://github.com/audreyfeldroy/cookiecutter-pypackage/
* Free software: BSD license

Features
--------

* Testing setup with ``unittest`` and ``python setup.py test`` or ``pytest``
* Travis-CI_: Ready for Travis Continuous Integration testing
* Tox_ testing: Setup to easily test for Python 3.6, 3.7, 3.8
* Sphinx_ docs: Documentation ready for generation with, for example, `Read the Docs`_
* bump2version_: Pre-configured version bumping with a single command
* Auto-release to PyPI_ when you push a new tag to master (optional)
* Command line interface using Click (optional)

.. _Cookiecutter: https://github.com/cookiecutter/cookiecutter

Quickstart
----------

Install the latest Cookiecutter if you haven't installed it yet (this requires
Cookiecutter 1.4.0 or higher)::

    pip install -U cookiecutter

Generate a Python package project::

    cookiecutter https://github.com/Akramz/cookiecutter-ml.git

Create a new Conda environment and install `pip`::

    conda install -c conda-forge mamba
    cd [PROJECT_NAME]/
    mamba env create -n [ENV_NAME] -f environment.yml
    conda activate [ENV_NAME]
    jupyter contrib nbextension install --user

Then:

* Create a GitHub repo and put it there.
* Add the repo to your Travis-CI_ account.
* Install the developer requirements into a conda environment (``pip install -r requirements_dev.txt``).
* Register_ your project with PyPI.
* Run the Travis CLI command ``travis encrypt --add deploy.password`` to encrypt your PyPI password in Travis config
  and activate automated deployment on PyPI when you push a new tag to master branch.
* Add the repo to your `Read the Docs`_ account + turn on the Read the Docs service hook.
* Release your package by pushing a new tag to master.
* Add a ``requirements.txt`` file that specifies the packages you will need for
  your project and their versions. For more info see the `pip docs for requirements files`_.
* Install the current package: ``pip install -e .``
* Activate your project on `pyup.io`_.

.. _`pip docs for requirements files`: https://pip.pypa.io/en/stable/user_guide/#requirements-files
.. _Register: https://packaging.python.org/tutorials/packaging-projects/#uploading-the-distribution-archives
.. _Travis-CI: http://travis-ci.org/
.. _Tox: http://testrun.org/tox/
.. _Sphinx: http://sphinx-doc.org/
.. _Read the Docs: https://readthedocs.io/
.. _`pyup.io`: https://pyup.io/
.. _bump2version: https://github.com/c4urself/bump2version
.. _Punch: https://github.com/lgiordani/punch
.. _Poetry: https://python-poetry.org/
.. _PyPi: https://pypi.python.org/pypi
.. _Mkdocs: https://pypi.org/project/mkdocs/
.. _Pre-commit: https://pre-commit.com/
.. _Black: https://black.readthedocs.io/en/stable/
.. _Mypy: https://mypy.readthedocs.io/en/stable/
.. _`Nekroze/cookiecutter-pypackage`: https://github.com/Nekroze/cookiecutter-pypackage
.. _`tony/cookiecutter-pypackage-pythonic`: https://github.com/tony/cookiecutter-pypackage-pythonic
.. _`ardydedase/cookiecutter-pypackage`: https://github.com/ardydedase/cookiecutter-pypackage
.. _`lgiordani/cookiecutter-pypackage`: https://github.com/lgiordani/cookiecutter-pypackage
.. _`briggySmalls/cookiecutter-pypackage`: https://github.com/briggySmalls/cookiecutter-pypackage
.. _`veit/cookiecutter-namespace-template`: https://github.com/veit/cookiecutter-namespace-template
.. _`zillionare/cookiecutter-pypackage`: https://zillionare.github.io/cookiecutter-pypackage/
.. _`waynerv/cookiecutter-pypackage`: https://waynerv.github.io/cookiecutter-pypackage/
.. _github comparison view: https://github.com/tony/cookiecutter-pypackage-pythonic/compare/audreyr:master...master
.. _`network`: https://github.com/audreyr/cookiecutter-pypackage/network
.. _`family tree`: https://github.com/audreyr/cookiecutter-pypackage/network/members
