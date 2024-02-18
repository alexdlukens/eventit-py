# AuthIT Library for Python

Integrating anonymous authentication with invoicing for web-apps

## Overview

This project is intended to provide "route event" tracking on a per-user basis. Each user will be provided with a distinct api-key that is sent with each request to identify the user. In a database, we will record the "events" performed by each user. A dashboard will be made to allow admins to see traffic per-route, and per-user

In the future, "invoicing" or "pricing" can be attributed to each API route. We can then help apps track usage via the events recorded, per-user.

This can be expanded upon with groups, automated email summaries about usage, etc.

Emphasis to be made on minimal "user" information recorded to get a user account up and started. Just request a new api key from an endpoint, and start using it. Can integrate with Flask-Login extension in the future.

## Developer details


I have setup pre-commit in this repository to execute pytest, ruff linting, and ruff formatting before commits. Poetry is used for dependency management. To setup this environment for development, first ensure [Poetry](https://python-poetry.org/) is installed.

To install all dependencies for authit-py, run the following commands from the base directory of this project.

```bash
poetry config virtualenvs.in-project true
poetry install
```


Next, install pre-commit on your machine, and install it into this project

```
pip install pre-commit
pre-commit install
```

For sanity, it is beneficial to run pre-commit on all files to ensure consistency
```
pre-commit run --all-files
```

From this point on, pre-commit will be run on every commit
