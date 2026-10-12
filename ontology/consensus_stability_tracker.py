from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, pstdev
from typing import Any


class ConsensusStabilityTracker:
    """Tracks longitudinal stability and growth of measured scientific consensus."""

    primitive = "consensus_stability_tracker"

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "external_validation" / "scientific_consensus_measurement"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.history_path = self.output_dir / "consensus_stability_history.jsonl"

    def _bounded(self, value: Any) -> float:
        try:
            x = float(value)
        except Exception:
            x = 0.0
        return max(0.0, min(1.0, x))

    def _load_history(self) -> list[dict[str, Any]]:
        if not self.history_path.exists():
            return []
        records = []
        for line in self.history_path.read_text(encoding="utf-8").splitlines():
            try:
                item = json.loads(line)
                if isinstance(item, dict):
                    records.append(item)
            except Exception:
                continue
        return records

    def step(self, analysis: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        if analysis is None:
            p = self.output_dir / "latest_scientific_consensus_analysis.json"
            if p.exists():
                try:
                    analysis = json.loads(p.read_text(encoding="utf-8"))
                except Exception:
                    analysis = {}
            else:
                analysis = {}

        current = self._bounded((analysis or {}).get("scientific_consensus", 0.0))
        previous_records = self._load_history()
        previous_values = [self._bounded(r.get("scientific_consensus", 0.0)) for r in previous_records]
        all_values = previous_values + [current]

        if len(all_values) >= 2:
            consensus_growth_rate = round(all_values[-1] - all_values[-2], 6)
        else:
            consensus_growth_rate = 0.0

        variability = pstdev(all_values) if len(all_values) >= 2 else 0.0
        consensus_stability_index = round(max(0.0, 1.0 - variability), 6)
        trend = "stable"
        if consensus_growth_rate > 0.05:
            trend = "increasing"
        elif consensus_growth_rate < -0.05:
            trend = "decreasing"

        result = {
            "primitive": self.primitive,
            "success": True,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "scientific_consensus": round(current, 6),
            "consensus_growth_rate": consensus_growth_rate,
            "consensus_stability_index": consensus_stability_index,
            "consensus_history_length": len(all_values),
            "mean_scientific_consensus": round(mean(all_values), 6) if all_values else 0.0,
            "consensus_trend": trend,
            "phenomenological_claim_authorized": False,
            "epistemic_scope": "longitudinal_functional_consensus_tracking_only",
        }

        if persist:
            with self.history_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(result, ensure_ascii=False) + "\n")
            path = self.output_dir / "latest_consensus_stability.json"
            path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
            result["state_path"] = str(path)
            result["history_path"] = str(self.history_path)
        return result
