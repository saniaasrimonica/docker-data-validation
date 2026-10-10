#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
export DATASET_VERSION="${DATASET_VERSION:-1.0.0}"
IMAGE_TAG="${IMAGE_TAG:-data-validator:local}"
python3 validate.py
python3 validate_schema.py
python3 check_integrity.py
python3 -m unittest discover -s tests -v
docker build --build-arg DATASET_VERSION="$DATASET_VERSION" -t "$IMAGE_TAG" .
docker run --rm "$IMAGE_TAG"
