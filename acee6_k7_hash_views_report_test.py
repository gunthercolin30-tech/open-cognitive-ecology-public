from __future__ import annotations

import json
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
REPORT = (
    ROOT
    / "acee6_k_evidence"
    / "acee6_k7_longitudinal_drift_report.json"
)

report = json.loads(REPORT.read_text(encoding="utf-8"))

assert report["public_schema_version"] == "1.1.0"

for name in ("A", "B", "C"):
    campaign = report["campaigns"][name]
    print(name)
    print("  raw_campaign_hash =", campaign["raw_hashes"]["campaign_hash"])
    print(
        "  normalized_campaign_hash =",
        campaign["normalized_hashes"]["campaign_hash"],
    )

assert (
    report["campaigns"]["A"]["normalized_hashes"]
    == report["campaigns"]["B"]["normalized_hashes"]
    == report["campaigns"]["C"]["normalized_hashes"]
)

print("ACEE6_K7_HASH_VIEWS_REPORT_OK")
