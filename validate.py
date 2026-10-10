"""CSV validation with useful errors and nonzero failure exit codes."""
import argparse
import csv
import os
import re
import sys

COLUMNS = ["record_id", "text", "label", "dataset_version"]
LABELS = {"positive", "negative", "neutral"}


def validate(path, expected_version):
    errors = []
    seen = set()
    count = 0
    with open(path, encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream, strict=True)
        if reader.fieldnames != COLUMNS:
            return [f"Header: expected {COLUMNS}; received {reader.fieldnames}"], 0
        for row in reader:
            count += 1
            line = reader.line_num
            if None in row or any(value is None for value in row.values()):
                errors.append(f"Line {line}: incorrect number of fields")
                continue
            raw_id = row["record_id"]
            if not re.fullmatch(r"[0-9]+", raw_id) or int(raw_id) <= 0:
                errors.append(f"Line {line}: record_id must be a positive integer")
            else:
                record_id = int(raw_id)
                if record_id in seen:
                    errors.append(f"Line {line}: duplicate record_id {record_id}")
                seen.add(record_id)
            if not row["text"].strip():
                errors.append(f"Line {line}: text is blank")
            if row["label"] not in LABELS:
                errors.append(f"Line {line}: invalid label {row['label']!r}")
            if row["dataset_version"] != expected_version:
                errors.append(f"Line {line}: dataset_version must equal {expected_version!r}")
    if count == 0:
        errors.append("Dataset has no data rows")
    return errors, count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default="data/dataset.csv")
    parser.add_argument("--expected-version", default=os.environ.get("DATASET_VERSION", "1.0.0"))
    args = parser.parse_args()
    if not args.expected_version.strip():
        print("ERROR: expected version cannot be blank", file=sys.stderr)
        return 1
    try:
        errors, count = validate(args.path, args.expected_version)
    except (OSError, UnicodeError, csv.Error, ValueError) as error:
        print(f"ERROR: cannot validate dataset: {error}", file=sys.stderr)
        return 1
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"PASS: Validated {count} rows.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
