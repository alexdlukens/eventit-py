#!/bin/bash
set -e
poetry run coverage run --source=eventit_py -m pytest tests/
poetry run coverage report
