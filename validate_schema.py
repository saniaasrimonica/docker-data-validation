"""Validate the practice CSV against an external schema contract."""
import argparse
import csv
import json
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default="data/dataset.csv")
    parser.add_argument("--schema", default="schema.json")
    args = parser.parse_args()
    try:
        with open(args.schema, encoding="utf-8") as file:
            schema = json.load(file)
        columns = schema["columns"]
        labels = schema["allowed_labels"]
        version = schema["dataset_version"]
        if not isinstance(columns, list) or columns != ["record_id", "text", "label", "dataset_version"]:
            raise ValueError("schema columns must match the four-column practice contract")
        if not isinstance(labels, list) or not labels or not all(isinstance(x, str) and x for x in labels):
            raise ValueError("allowed_labels must be a nonempty list of strings")
        if not isinstance(version, str) or not version.strip():
            raise ValueError("dataset_version must be a nonblank string")
        if not isinstance(schema.get("schema_version"), str) or not schema["schema_version"].strip():
            raise ValueError("schema_version must be a nonblank string")
        errors = []
        count = 0
        with open(args.data, encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file, strict=True)
            if reader.fieldnames != columns:
                raise ValueError(f"CSV header must equal {columns}")
            for row in reader:
                count += 1
                line = reader.line_num
                if None in row or any(value is None for value in row.values()):
                    errors.append(f"Line {line}: wrong number of fields")
                    continue
                if row["label"] not in labels:
                    errors.append(f"Line {line}: label violates schema")
                if row["dataset_version"] != version:
                    errors.append(f"Line {line}: version violates schema")
        if not count:
            errors.append("Dataset is empty")
        if errors:
            raise ValueError("; ".join(errors))
    except (OSError, UnicodeError, csv.Error, ValueError, KeyError, TypeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"PASS: Schema {schema['schema_version']} validated {count} rows.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
