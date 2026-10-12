#!/usr/bin/env python3

import json
from pathlib import Path

path = Path("scientific_validation_report.json")
data = json.loads(path.read_text(encoding="utf-8"))

print("TOP_LEVEL_KEYS")
for key in sorted(data):
    print("-", key)

print()
print("POSSIBLE_STATUS_FIELDS")
for key in (
    "overall_success",
    "success",
    "status",
    "validation_success",
    "error_count",
    "failed_calls",
    "timeouts",
    "failed_modules",
    "diagnostics",
    "summary",
):
    if key in data:
        print(f"{key} = {data[key]!r}")
