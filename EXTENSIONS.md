# Data validation extensions

Copy these files into the root of the previous docker-data-validation project. Keep its existing validate.py, Dockerfile, data/, tests/, and workflow. No additional Python dependencies are needed.

## Files and commands

- schema.json: external, versioned CSV schema contract.
- validate_schema.py: validates header, field count, labels, and version against that contract. The original validate.py remains responsible for IDs and blank text.
- dataset_manifest.json: sample SHA-256 checksum and source description.
- check_integrity.py: streams the dataset and checks byte integrity against the manifest.
- build_validated.sh: stops on a failed validation, checksum check, test, build, or container run.

```bash
python3 validate_schema.py
python3 check_integrity.py
bash build_validated.sh
```

The Bash script requires Docker access. If your Ubuntu user requires sudo, run `sudo bash build_validated.sh` for this practice project. Review any script before running it with sudo.

## Manifest behavior

The supplied checksum matches the previous downloadable dataset.csv exactly, including LF line endings and its final newline. CRLF conversion or any edit changes the checksum. A mismatch is expected when bytes differ; it does not necessarily indicate incorrect row values. Do not automatically regenerate the expected hash inside CI, as that would make the integrity check ineffective. Update the manifest only after independently reviewing an intentional dataset change.

A checksum detects changes only when the expected manifest is trusted. It does not prove authenticity if both dataset and manifest can be changed together. Production workflows should protect or sign approved manifests and record source URI, transformations, and revisions.

## CI integration

Add these steps before the Build image step in the existing workflow:

```yaml
      - name: Validate external schema
        run: python validate_schema.py
      - name: Check dataset integrity
        run: python check_integrity.py
```

The existing Dockerfile still runs only validate.py inside its build. These additional checks run on the host or CI; they do not automatically become Docker build steps. To enforce them in Docker as well, explicitly COPY both scripts, schema.json, and dataset_manifest.json, then add RUN commands. Also add those files to the .dockerignore allowlist. Keep the schema version and dataset version aligned with Docker labels during reviewed updates.

## Practice demonstrations

1. Run both Python scripts on the unchanged sample: both should pass.
2. Edit any text: schema validation may pass, while integrity validation must fail.
3. Change a label to invalid: schema validation must fail.
4. Restore the exact original dataset before committing.

These are learning extensions, not a complete production governance or MLOps platform.
