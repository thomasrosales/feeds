#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

poetry run coverage run -m pytest
poetry run coverage report
