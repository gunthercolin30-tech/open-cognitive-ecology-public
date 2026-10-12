from __future__ import annotations

import argparse
import json
from pathlib import Path

from oif.review.governed_redundancy_review import (
    CONFIRMATION_PHRASE,
    GovernedRedundancyReview,
)

ROOT = Path.home() / "open-cognitive-ecology"


def main() -> int:
    parser = argparse.ArgumentParser(description="OIF-0.B4 governed qualitative redundancy review")
    parser.add_argument("action", choices=("prepare", "apply", "status"))
    parser.add_argument("--workbook", type=Path)
    parser.add_argument("--confirmation", default="")
    parser.add_argument("--output-root", type=Path)
    args = parser.parse_args()
    engine = GovernedRedundancyReview(ROOT)
    if args.action == "prepare":
        path = engine.prepare(args.output_root)
        workbook = json.loads(path.read_text(encoding="utf-8"))
        print("OIF_GOVERNED_REDUNDANCY_REVIEW_PREPARED")
        print(f"campaign_id={workbook['campaign_id']}")
        print(f"candidate_count={workbook['candidate_count']}")
        print(f"workbook={path}")
        print("automatic_changes_made=false")
        return 0
    if args.action == "apply":
        if args.workbook is None:
            parser.error("--workbook is required for apply")
        result = engine.apply(args.workbook, args.confirmation)
        print("OIF_GOVERNED_REDUNDANCY_REVIEW_APPLIED")
        print(f"decision_count={result['decision_count']}")
        print(f"appended_count={result['appended_count']}")
        print(f"replayed_count={result['replayed_count']}")
        print(f"ledger={result['ledger_path']}")
        return 0
    base = ROOT / "oif_review/campaigns"
    matches = sorted(base.glob("*/review_manifest.json")) if base.is_dir() else []
    print(matches[-1].read_text(encoding="utf-8") if matches else json.dumps({"status": "NOT_PREPARED"}))
    print(f"confirmation_phrase={CONFIRMATION_PHRASE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
