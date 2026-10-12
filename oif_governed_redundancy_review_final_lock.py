from __future__ import annotations

import json
import tempfile
from pathlib import Path

from oif.review.governed_redundancy_review import build_workbook, prepare

ROOT = Path.home() / "open-cognitive-ecology"


def main() -> int:
    first = build_workbook(ROOT)
    second = build_workbook(ROOT)
    if first != second:
        raise SystemExit("OIF_B4_DETERMINISM_FAILURE")
    counts = {}
    for entry in first["entries"]:
        name = entry["proposed_classification"]
        counts[name] = counts.get(name, 0) + 1
        if entry["automatic_change_authorized"] is not False:
            raise SystemExit("OIF_B4_AUTOMATIC_CHANGE_AUTHORIZATION_FAILURE")
        if entry["entry_hash"] == "" or entry["source_pair_hash"] == "":
            raise SystemExit("OIF_B4_HASH_BINDING_FAILURE")
    if first["candidate_count"] != 104:
        raise SystemExit(f"OIF_B4_EXPECTED_104_PRIORITY_CASES_GOT_{first['candidate_count']}")
    expected = {"ADAPTER": 1, "COMPLEMENTARY": 1, "HUMAN_REVIEW_REQUIRED": 100, "PARTIAL_OVERLAP": 1, "VIEW": 1}
    if counts != expected:
        raise SystemExit(f"OIF_B4_CLASSIFICATION_DISTRIBUTION_FAILURE_{counts}")
    with tempfile.TemporaryDirectory() as tmp:
        path = prepare(ROOT, Path(tmp))
        persisted = json.loads(path.read_text(encoding="utf-8"))
        if persisted != first:
            raise SystemExit("OIF_B4_PERSISTENCE_DETERMINISM_FAILURE")
    if not first.get("functional_conclusion_only") or not first.get("phenomenology_undetermined"):
        raise SystemExit("OIF_B4_EPISTEMIC_GUARD_FAILURE")
    print("OIF_GOVERNED_REDUNDANCY_REVIEW_104_CASES_READY")
    print(f"classification_counts={counts}")
    print("automatic_changes_made=false")
    print("OIF_GOVERNED_REDUNDANCY_REVIEW_FINAL_LOCK_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
