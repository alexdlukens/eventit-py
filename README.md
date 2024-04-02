<img src="https://github.com/alexdlukens/eventit-py/blob/master/docs/source/_static/logos/EventIT_Logo_Email_Signature.png" height="100">

[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Actions status](https://github.com/astral-sh/ruff/workflows/CI/badge.svg)](https://github.com/alexdlukens/eventit-py/actions)

# EventIT Library for Python

This repo is intended to be the core event tracking framework that will be built-upon in other applications

**Note:** As of now, this is just a personal project. Any advise or contributions towards the direction of this project would be greatly appreciated. Feel free to make a Github Issue/discussion about future work.

[Documentation link](https://alexdlukens.github.io/eventit-py/#)

## Overview
In this context, an event is a "log", as a dictionary with pre-defined fields. These fields are defined in Pydantic models, which validate the event during the logging process.

### Features
- Pydantic validation
- Custom user-defined metrics
- Support for various backend data-storage services (MongoDB as primary data backend)
- Support for different "types" of events, such as rate-based, authentication-based, etc. (TODO)
- Integration with cross-platform frameworks, such as OpenTelemetry, Flask, FastAPI, etc. (TODO)

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
