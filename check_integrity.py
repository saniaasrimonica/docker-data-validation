"""Compare a file's SHA-256 digest with a previously trusted manifest."""
import argparse
import hashlib
import json
import re
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", default="data/dataset.csv")
    parser.add_argument("--manifest", default="dataset_manifest.json")
    args = parser.parse_args()
    try:
        with open(args.manifest, encoding="utf-8") as file:
            manifest = json.load(file)
        expected = manifest["sha256"]
        if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", expected):
            raise ValueError("Manifest sha256 must contain 64 hexadecimal characters")
        digest = hashlib.sha256()
        with open(args.data, "rb") as file:
            for block in iter(lambda: file.read(1024 * 1024), b""):
                digest.update(block)
        if digest.hexdigest() != expected.lower():
            raise ValueError("Dataset checksum mismatch: file bytes have changed")
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("PASS: Dataset SHA-256 matches the manifest.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
