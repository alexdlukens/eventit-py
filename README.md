# EventIT Library for Python

This repo is intended to be the core event tracking framework that will be built-upon in other applications (e.g. Authentication event tracking, logs, etc.)

## Overview

Pass for now

## Developer details


I have setup pre-commit in this repository to execute pytest, ruff linting, and ruff formatting before commits. Poetry is used for dependency management. To setup this environment for development, first ensure [Poetry](https://python-poetry.org/) is installed.

To install all dependencies for eventit-py, run the following commands from the base directory of this project.

```bash
poetry config virtualenvs.in-project true
poetry install --with=dev
```


Next, install pre-commit on your machine, and install it into this project

```bash
pip install pre-commit
pre-commit install
```

For sanity, it is beneficial to run pre-commit on all files to ensure consistency

```bash
pre-commit run --all-files
```

From this point on, pre-commit will be run on every commit
