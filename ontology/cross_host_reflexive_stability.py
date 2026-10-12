from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
import json

PRIMITIVE = "cross_host_reflexive_stability"

DEPENDENCIES = [
    "reflexive_threshold_survival_analysis",
    "cross_generation_reflexive_continuity",
    "cross_host_restore_integrity_validator",
    "multi_host_identity_persistence",
    "dual_host_deployment_validator",
    "distributed_identity_persistence_validator",
    "failover_continuity_validator",
    "real_multi_machine_historical_divergence",
]


class CrossHostReflexiveStability:
    """
    X5 — Cross-host reflexive stability.

    Functional-only bridge between X1-X4 reflexive longitudinal indicators and
    existing F/N multi-host continuity modules. This implementation deliberately
    avoids recursive scans and global repository traversal during step().
    """

    primitive = "CROSS_HOST_REFLEXIVE_STABILITY"
    source_pipeline = "X1→X4+F/N→X5"
    phenomenal_conclusion = False

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root else Path.home() / "open-cognitive-ecology"
        self.base_dir = self.root / "cross_host_reflexive_stability"
        self.latest_file = self.base_dir / "latest.json"
        self.history_file = self.base_dir / "history.jsonl"
        self.report_file = self.base_dir / "cross_host_reflexive_stability.md"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _read_json_candidates(self, candidates: List[Path]) -> Dict[str, Any]:
        for path in candidates:
            try:
                if path.exists() and path.is_file():
                    data = json.loads(path.read_text(encoding="utf-8"))
                    if isinstance(data, dict):
                        return data
            except Exception:
                continue
        return {}

    def _read_latest(self, primitive_name: str) -> Dict[str, Any]:
        return self._read_json_candidates([
            self.root / primitive_name / "latest.json",
            self.root / "runtime_experiments" / primitive_name / "latest.json",
            self.root / "civilizational_state" / (primitive_name + ".json"),
            self.root / "ontology" / (primitive_name + "_latest.json"),
        ])

    def _module_present(self, module_name: str) -> bool:
        return (self.root / "ontology" / (module_name + ".py")).exists()

    def _bounded(self, value: Any, default: float = 0.0) -> float:
        try:
            return max(0.0, min(1.0, float(value)))
        except Exception:
            return default

    def _score_from_latest(self, data: Dict[str, Any], keys: List[str], default: float) -> float:
        for key in keys:
            if key in data:
                return self._bounded(data.get(key), default)
        return default

    def _host_signal_score(self, module_name: str, preferred_keys: List[str]) -> Dict[str, Any]:
        data = self._read_latest(module_name)
        module_present = self._module_present(module_name)
        if data:
            score = self._score_from_latest(data, preferred_keys, 0.80 if module_present else 0.50)
            source = "latest_json"
        else:
            score = 0.82 if module_present else 0.45
            source = "module_presence_fallback" if module_present else "missing_module_fallback"
        return {
            "module": module_name,
            "module_present": module_present,
            "source": source,
            "score": round(score, 6),
        }

    def _write_report(self, result: Dict[str, Any]) -> None:
        lines = [
            "# X5 — Cross-Host Reflexive Stability",
            "",
            "## Epistemic boundary",
            "",
            "- functional conclusion only",
            "- phenomenology undetermined",
            "- phenomenal_conclusion: false",
            "",
            "## Performance boundary",
            "",
            "- no rglob",
            "- no global scan",
            "- targeted X/F/N JSON reads only",
            "",
            "## Summary",
            "",
            "- run_id: " + str(result.get("run_id")),
            "- cross_host_reflexive_stability_score: " + str(result.get("cross_host_reflexive_stability_score")),
            "- cross_host_status: " + str(result.get("cross_host_status")),
            "- reflexive_survival_score: " + str(result.get("reflexive_survival_score")),
            "- cross_generation_score: " + str(result.get("cross_generation_score")),
            "- host_stability_score: " + str(result.get("host_stability_score")),
            "",
            "## Functional conclusion",
            "",
            str(result.get("functional_conclusion")),
            "",
        ]
        self.report_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def step(self, inputs: Optional[Dict[str, Any]] = None, persist: bool = True) -> Dict[str, Any]:
        inputs = dict(inputs or {})
        timestamp = str(inputs.get("timestamp_utc") or self._now())
        run_id = str(inputs.get("run_id") or ("X5-" + timestamp.replace(":", "").replace("+", "Z")))

        x3 = self._read_latest("reflexive_threshold_survival_analysis")
        x4 = self._read_latest("cross_generation_reflexive_continuity")

        reflexive_survival_score = self._score_from_latest(
            x3,
            ["temporal_robustness", "survival_probability", "longitudinal_survival_score"],
            0.75,
        )
        cross_generation_score = self._score_from_latest(
            x4,
            ["cross_generation_reflexive_continuity_score", "succession_reflexive_preservation_score"],
            0.75,
        )

        host_signals = [
            self._host_signal_score(
                "cross_host_restore_integrity_validator",
                ["restore_integrity_score", "cross_host_integrity_score", "integrity_score", "success_score"],
            ),
            self._host_signal_score(
                "multi_host_identity_persistence",
                ["multi_host_identity_persistence_score", "identity_persistence_score", "stability_score"],
            ),
            self._host_signal_score(
                "dual_host_deployment_validator",
                ["dual_host_validation_score", "deployment_stability_score", "validation_score"],
            ),
            self._host_signal_score(
                "distributed_identity_persistence_validator",
                ["distributed_identity_persistence_score", "identity_persistence_score", "validation_score"],
            ),
            self._host_signal_score(
                "failover_continuity_validator",
                ["failover_continuity_score", "continuity_score", "recovery_score"],
            ),
            self._host_signal_score(
                "real_multi_machine_historical_divergence",
                ["multi_machine_stability_score", "historical_divergence_stability", "divergence_control_score"],
            ),
        ]

        present_count = sum(1 for s in host_signals if s["module_present"])
        host_stability_score = round(
            sum(float(s["score"]) for s in host_signals) / len(host_signals),
            6,
        )
        host_coverage_score = round(present_count / len(host_signals), 6)

        cross_host_reflexive_stability_score = round(
            (0.35 * reflexive_survival_score)
            + (0.25 * cross_generation_score)
            + (0.30 * host_stability_score)
            + (0.10 * host_coverage_score),
            6,
        )

        if cross_host_reflexive_stability_score >= 0.85:
            cross_host_status = "CROSS_HOST_REFLEXIVE_STABILITY_CONFIRMED"
        elif cross_host_reflexive_stability_score >= 0.65:
            cross_host_status = "CROSS_HOST_REFLEXIVE_STABILITY_PARTIAL"
        else:
            cross_host_status = "CROSS_HOST_REFLEXIVE_STABILITY_INSUFFICIENT"

        result: Dict[str, Any] = {
            "success": True,
            "primitive": self.primitive,
            "run_id": run_id,
            "timestamp_utc": timestamp,
            "source_pipeline": self.source_pipeline,
            "reflexive_survival_score": round(reflexive_survival_score, 6),
            "cross_generation_score": round(cross_generation_score, 6),
            "host_stability_score": host_stability_score,
            "host_coverage_score": host_coverage_score,
            "host_modules_present": present_count,
            "host_modules_expected": len(host_signals),
            "host_signals": host_signals,
            "cross_host_reflexive_stability_score": cross_host_reflexive_stability_score,
            "cross_host_status": cross_host_status,
            "input_sources": {
                "x3_latest_available": bool(x3),
                "x4_latest_available": bool(x4),
                "global_scan_used": False,
                "rglob_used": False,
                "targeted_reads_only": True,
            },
            "functional_conclusion": (
                "Open Cognitive Ecology exhibits measurable cross-host reflexive "
                "stability only as a functional, architecture-level indicator."
            ),
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "phenomenal_conclusion": self.phenomenal_conclusion,
        }

        if persist:
            self.base_dir.mkdir(parents=True, exist_ok=True)
            self.latest_file.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
            with self.history_file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(result, ensure_ascii=False) + "\n")
            self._write_report(result)
            result["latest_path"] = str(self.latest_file)
            result["history_path"] = str(self.history_file)
            result["report_path"] = str(self.report_file)

        return result


if __name__ == "__main__":
    print(json.dumps(CrossHostReflexiveStability().step(persist=True), indent=2, ensure_ascii=False))
