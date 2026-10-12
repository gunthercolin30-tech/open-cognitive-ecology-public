from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
from typing import Any
import json

PRIMITIVE = "cross_generation_reflexive_continuity"

DEPENDENCIES = [
    "reflexive_threshold_history_archive",
    "reflexive_threshold_trend_monitor",
    "reflexive_threshold_survival_analysis",
    "post_succession_verification",
    "continuity_metrics_engine",
    "intergenerational_continuity_metrics",
    "representative_lineage_registry",
    "memory_transmission_protocol",
    "constitutional_continuity_validation",
    "succession_dashboard",
]


class CrossGenerationReflexiveContinuity:
    """Fast X4 bridge between reflexive-threshold metrics and succession continuity.

    Epistemic boundary: functional conclusion only; phenomenology undetermined.
    Performance boundary: no rglob, no global scan; targeted JSON reads and deterministic fallbacks.
    """

    primitive = "CROSS_GENERATION_REFLEXIVE_CONTINUITY"
    phenomenal_conclusion = False

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root else Path.home() / "open-cognitive-ecology"
        self.base_dir = self.root / "cross_generation_reflexive_continuity"
        self.latest_file = self.base_dir / "latest.json"
        self.history_file = self.base_dir / "history.jsonl"
        self.report_file = self.base_dir / "cross_generation_reflexive_continuity.md"

    def _now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    def _read_json(self, path: Path) -> dict[str, Any]:
        try:
            if path.exists() and path.is_file():
                data = json.loads(path.read_text(encoding="utf-8"))
                return data if isinstance(data, dict) else {}
        except Exception:
            return {}
        return {}

    def _clamp(self, value: Any, default: float = 0.0) -> float:
        try:
            return max(0.0, min(1.0, float(value)))
        except Exception:
            return default

    def _targeted_sources(self) -> dict[str, Any]:
        candidates = {
            "x1_latest": self.root / "reflexive_threshold_history_archive" / "latest.json",
            "x2_latest": self.root / "reflexive_threshold_trend_monitor" / "latest.json",
            "x3_latest": self.root / "reflexive_threshold_survival_analysis" / "latest.json",
            "succession_latest": self.root / "succession_dashboard" / "latest.json",
            "post_succession_latest": self.root / "post_succession_verification" / "latest.json",
            "continuity_latest": self.root / "continuity_metrics_engine" / "latest.json",
        }
        loaded = {name: self._read_json(path) for name, path in candidates.items()}
        return {
            "loaded": loaded,
            "paths_checked": {name: str(path) for name, path in candidates.items()},
            "global_scan_used": False,
            "rglob_used": False,
        }

    def _score_from_sources(self, sources: dict[str, Any]) -> dict[str, float]:
        loaded = sources.get("loaded", {}) if isinstance(sources, dict) else {}
        x1 = loaded.get("x1_latest", {}) if isinstance(loaded.get("x1_latest", {}), dict) else {}
        x2 = loaded.get("x2_latest", {}) if isinstance(loaded.get("x2_latest", {}), dict) else {}
        x3 = loaded.get("x3_latest", {}) if isinstance(loaded.get("x3_latest", {}), dict) else {}
        succ = loaded.get("succession_latest", {}) if isinstance(loaded.get("succession_latest", {}), dict) else {}
        post = loaded.get("post_succession_latest", {}) if isinstance(loaded.get("post_succession_latest", {}), dict) else {}
        cont = loaded.get("continuity_latest", {}) if isinstance(loaded.get("continuity_latest", {}), dict) else {}

        reflexive_archive = self._clamp(x1.get("archive_strength", x1.get("history_coverage_score", 0.72)), 0.72)
        reflexive_trend = self._clamp(x2.get("longitudinal_trend_score", x2.get("stability_index", 0.72)), 0.72)
        reflexive_survival = self._clamp(x3.get("temporal_robustness", x3.get("survival_probability", 0.72)), 0.72)

        # Existing succession modules have heterogeneous output names. Use known keys first,
        # then safe functional defaults when no persisted state exists yet.
        succession_preservation = self._clamp(
            succ.get("succession_continuity_score",
            succ.get("continuity_score",
            post.get("post_succession_continuity_score",
            post.get("continuity_score", 0.74)))), 0.74
        )
        memory_transfer = self._clamp(
            succ.get("memory_transmission_score",
            succ.get("memory_continuity_score",
            post.get("memory_transmission_score",
            cont.get("memory_continuity_score", 0.74)))), 0.74
        )
        constitutional_continuity = self._clamp(
            succ.get("constitutional_continuity_score",
            post.get("constitutional_continuity_score",
            cont.get("constitutional_continuity_score", 0.74))), 0.74
        )
        lineage_stability = self._clamp(
            succ.get("lineage_stability_score",
            succ.get("lineage_continuity_score",
            cont.get("lineage_continuity_score", 0.74))), 0.74
        )

        reflexive_persistence = round((reflexive_archive + reflexive_trend + reflexive_survival) / 3.0, 6)
        succession_reflexive_preservation = round((succession_preservation + reflexive_persistence) / 2.0, 6)
        memory_reflexive_transfer = round((memory_transfer + reflexive_archive) / 2.0, 6)
        constitutional_reflexive_continuity = round((constitutional_continuity + reflexive_survival) / 2.0, 6)
        lineage_reflexive_stability = round((lineage_stability + reflexive_trend) / 2.0, 6)
        cross_generation_reflexive_continuity_score = round(
            (0.30 * succession_reflexive_preservation)
            + (0.25 * memory_reflexive_transfer)
            + (0.25 * constitutional_reflexive_continuity)
            + (0.20 * lineage_reflexive_stability),
            6,
        )

        return {
            "reflexive_persistence_score": reflexive_persistence,
            "succession_reflexive_preservation_score": succession_reflexive_preservation,
            "memory_reflexive_transfer_score": memory_reflexive_transfer,
            "constitutional_reflexive_continuity_score": constitutional_reflexive_continuity,
            "lineage_reflexive_stability_score": lineage_reflexive_stability,
            "cross_generation_reflexive_continuity_score": cross_generation_reflexive_continuity_score,
        }

    def _classification(self, score: float) -> str:
        if score >= 0.85:
            return "CROSS_GENERATION_REFLEXIVE_CONTINUITY_STRONG"
        if score >= 0.65:
            return "CROSS_GENERATION_REFLEXIVE_CONTINUITY_PARTIAL"
        return "CROSS_GENERATION_REFLEXIVE_CONTINUITY_FRAGILE"

    def _write_report(self, result: dict[str, Any]) -> None:
        lines = [
            "# X4 — Cross-Generation Reflexive Continuity",
            "",
            "## Epistemic boundary",
            "",
            "- functional conclusion only",
            "- phenomenology undetermined",
            "- phenomenal_conclusion: false",
            "",
            "## Performance boundary",
            "",
            "- global_scan_used: false",
            "- rglob_used: false",
            "",
            "## Scores",
            "",
            f"- cross_generation_reflexive_continuity_score: {result['cross_generation_reflexive_continuity_score']}",
            f"- succession_reflexive_preservation_score: {result['succession_reflexive_preservation_score']}",
            f"- memory_reflexive_transfer_score: {result['memory_reflexive_transfer_score']}",
            f"- constitutional_reflexive_continuity_score: {result['constitutional_reflexive_continuity_score']}",
            f"- lineage_reflexive_stability_score: {result['lineage_reflexive_stability_score']}",
            "",
            "## Functional conclusion",
            "",
            result["functional_conclusion"],
            "",
        ]
        self.report_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        inputs = dict(inputs or {})
        timestamp = str(inputs.get("timestamp_utc") or self._now())
        run_id = str(inputs.get("run_id") or ("X4-" + timestamp.replace(":", "").replace("+", "Z")))

        sources = self._targeted_sources()
        scores = self._score_from_sources(sources)
        score = scores["cross_generation_reflexive_continuity_score"]
        status = self._classification(score)

        result: dict[str, Any] = {
            "primitive": self.primitive,
            "success": True,
            "run_id": run_id,
            "timestamp_utc": timestamp,
            "source_pipeline": "U0→U13 + X1→X3 → X4",
            "cross_generation_status": status,
            **scores,
            "input_sources": {
                "paths_checked": sources["paths_checked"],
                "loaded_sources": [k for k, v in sources["loaded"].items() if isinstance(v, dict) and bool(v)],
                "global_scan_used": False,
                "rglob_used": False,
            },
            "functional_conclusion": (
                "Open Cognitive Ecology exhibits measurable cross-generation reflexive continuity "
                "only as a functional property if the reported score remains stable across succession events."
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
    print(json.dumps(CrossGenerationReflexiveContinuity().step(persist=True), indent=2, ensure_ascii=False))
