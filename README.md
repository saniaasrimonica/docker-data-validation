# Docker Data Validation

A learning and portfolio project: validate a synthetic CSV dataset before a Docker image can be built. Uses Python's standard library; no pip dependencies are required.

## Validation contract

The ordered header must be `record_id,text,label,dataset_version`. At least one data row is required. IDs must contain decimal digits, be positive, and be unique (01 and 1 count as the same ID). Text must not be blank. Labels must be positive, negative, or neutral. Every dataset version must match the configured expected version. Extra or missing fields fail validation.

## Run locally

```bash
python3 validate.py
python3 -m unittest discover -s tests -v
python3 validate.py data/dataset.csv --expected-version 1.0.0
```

Exit code 0 means success; 1 means invalid data or a read failure. Command-line version overrides DATASET_VERSION, which defaults to 1.0.0.

## Build and run

```bash
sudo docker build --build-arg DATASET_VERSION=1.0.0 -t data-validator:1.0.0 .
sudo docker run --rm data-validator:1.0.0
sudo docker image inspect data-validator:1.0.0 --format '{{ index .Config.Labels "dataset.version" }}'
```

ARG configures the expected version during the build. ENV supplies it to the validator, and LABEL records it in image metadata. Labels alone do not validate data. RUN invokes the validator and a nonzero exit stops the build. Runtime validation executes as a non-root numeric user.

## Failure demonstration

```bash
sudo docker build --build-arg DATASET_VERSION=2.0.0 -t data-validator:invalid .
```

This must fail because the sample rows contain version 1.0.0. It does not change the CSV. Tests also cover duplicate IDs, invalid labels, whitespace text, bad field counts, invalid IDs, missing files, bad headers, and empty data.

## CI

.github/workflows/validate.yml runs tests, local validation, image build, and container validation on pushes and pull requests. It also checks that a mismatched version build fails. No registry publishing or deployment is configured. For protected merges, configure the validate job as a required status check in repository rules.

## Traceability and limitations

The dataset.source label identifies synthetic practice data; it is not complete lineage. Production extensions could record a dataset SHA-256 checksum, source URI, transformation history, Git revision, and schema artifact. Pin the base image by digest and workflow actions by full commit SHA for stronger reproducibility. This example currently uses moving image and action tags, and requires network access to fetch them. Docker build caching may reuse validation when its inputs are unchanged.

## Manual GitHub upload

Extract the ZIP first; uploading the ZIP alone will not activate CI. Upload the project contents into the repository root, preserving data/ and tests/. Hidden files may not appear in your file picker. Create .github/workflows/validate.yml with GitHub's Add file > Create new file if needed, then paste the supplied workflow. Likewise create .dockerignore and .gitignore if the uploader skips them. Review the resulting paths before committing.
