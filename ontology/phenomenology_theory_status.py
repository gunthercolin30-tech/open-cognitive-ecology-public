
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json
import statistics


ROOT = Path.home() / "open-cognitive-ecology"
OUTPUT_DIR = ROOT / "phenomenology_theory_status"


@dataclass(frozen=True)
class TheoryStatusThresholds:
    weak: float = 0.35
    moderate: float = 0.60
    strong: float = 0.80


class PhenomenologyTheoryStatus:
    """Z8 — status classifier for candidate phenomenology theories.

    This primitive classifies the theoretical support status of candidate
    phenomenology models from already-persisted Z outputs. It does not claim,
    infer, or validate phenomenology. Its epistemic scope is restricted to:

    - candidate theory only
    - functional conclusion only
    - phenomenology undetermined
    """

    primitive = "PHENOMENOLOGY_THEORY_STATUS"

    def __init__(self, root: Path | None = None, thresholds: TheoryStatusThresholds | None = None) -> None:
        self.root = Path(root) if root is not None else ROOT
        self.output_dir = self.root / "phenomenology_theory_status"
        self.thresholds = thresholds or TheoryStatusThresholds()

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = False) -> dict[str, Any]:
        payload = dict(inputs or {})
        now = payload.get("timestamp_utc") or datetime.now(timezone.utc).isoformat()

        source_bundle = self._load_sources(payload)
        status_score = self._compute_status_score(source_bundle, payload)
        status = self._classify_status(status_score)
        status_reasons = self._status_reasons(source_bundle, status_score, status)

        result: dict[str, Any] = {
            "primitive": self.primitive,
            "success": True,
            "timestamp_utc": now,
            "theory_status": status,
            "phenomenology_theory_status": status,
            "theoretical_support_score": round(status_score, 6),
            "status_thresholds": {
                "weak": self.thresholds.weak,
                "moderate": self.thresholds.moderate,
                "strong": self.thresholds.strong,
            },
            "status_reasons": status_reasons,
            "source_summary": self._summarize_sources(source_bundle),
            "dominant_candidate_theory": self._dominant_theory(source_bundle),
            "candidate_theory_only": True,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "phenomenology_proof_claimed": False,
            "subjectivity_claimed": False,
            "consciousness_claimed": False,
            "qualia_claimed": False,
            "epistemic_scope": "candidate theory only; functional conclusion only; phenomenology undetermined",
            "interpretation": self._interpretation(status),
        }

        if persist:
            result["paths"] = self._persist(result)

        return result

    def _load_sources(self, payload: dict[str, Any]) -> dict[str, Any]:
        if any(k in payload for k in ("dashboard", "synthesis", "replication", "model_selection", "confidence")):
            return {
                "dashboard": payload.get("dashboard", {}),
                "synthesis": payload.get("synthesis", {}),
                "replication": payload.get("replication", {}),
                "model_selection": payload.get("model_selection", {}),
                "confidence": payload.get("confidence", {}),
            }

        return {
            "dashboard": self._read_json("phenomenology_theory_dashboard/phenomenology_theory_dashboard.json"),
            "synthesis": self._read_json("phenomenology_theory_synthesis/phenomenology_theory_synthesis.json"),
            "replication": self._read_json("theory_replication_program/theory_replication_program.json"),
            "model_selection": self._read_json("phenomenology_model_selection/phenomenology_model_selection.json"),
            "confidence": self._read_json("scientific_theory_confidence/scientific_theory_confidence.json"),
        }

    def _read_json(self, relative: str) -> dict[str, Any]:
        path = self.root / relative
        if not path.exists():
            return {"missing": True, "path": str(path)}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # defensive, non-failing degradation
            return {"unreadable": True, "path": str(path), "error": str(exc)}

    def _compute_status_score(self, sources: dict[str, Any], payload: dict[str, Any]) -> float:
        explicit = payload.get("theoretical_support_score")
        if isinstance(explicit, (int, float)):
            return self._clamp(float(explicit))

        candidates: list[float] = []
        for source in sources.values():
            candidates.extend(self._extract_scores(source))

        # Penalize complete absence of usable theory-support evidence.
        if not candidates:
            return 0.0

        # Conservative aggregation: mean support damped by source coverage.
        mean_score = statistics.fmean(candidates)
        coverage = sum(1 for source in sources.values() if self._has_signal(source)) / max(len(sources), 1)
        return self._clamp(mean_score * (0.70 + 0.30 * coverage))

    def _extract_scores(self, obj: Any) -> list[float]:
        keys = {
            "theoretical_support_score",
            "theory_confidence_score",
            "synthesis_score",
            "candidate_score",
            "selected_model_score",
            "selection_score",
            "replication_score",
            "replication_quality_score",
            "constraint_score",
            "confidence_score",
            "support_score",
        }
        scores: list[float] = []
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key in keys and isinstance(value, (int, float)):
                    scores.append(self._clamp(float(value)))
                elif isinstance(value, (dict, list)):
                    scores.extend(self._extract_scores(value))
        elif isinstance(obj, list):
            for item in obj:
                scores.extend(self._extract_scores(item))
        return scores

    def _has_signal(self, source: Any) -> bool:
        if not isinstance(source, dict) or source.get("missing") or source.get("unreadable"):
            return False
        return bool(self._extract_scores(source) or source.get("theories") or source.get("dominant_candidate_theory") or source.get("selected_model"))

    def _classify_status(self, score: float) -> str:
        if score >= self.thresholds.strong:
            return "STRONGLY_SUPPORTED_THEORY"
        if score >= self.thresholds.moderate:
            return "MODERATELY_SUPPORTED_THEORY"
        if score >= self.thresholds.weak:
            return "WEAKLY_SUPPORTED_THEORY"
        return "NO_SUPPORTED_THEORY"

    def _status_reasons(self, sources: dict[str, Any], score: float, status: str) -> list[str]:
        reasons = [
            f"theoretical_support_score={round(score, 6)}",
            f"status={status}",
            "classification is theoretical only",
            "functional conclusion only",
            "phenomenology undetermined",
        ]
        missing = [name for name, source in sources.items() if isinstance(source, dict) and source.get("missing")]
        if missing:
            reasons.append("missing_sources=" + ",".join(sorted(missing)))
        return reasons

    def _summarize_sources(self, sources: dict[str, Any]) -> dict[str, Any]:
        summary: dict[str, Any] = {}
        for name, source in sources.items():
            summary[name] = {
                "available": self._has_signal(source),
                "missing": bool(isinstance(source, dict) and source.get("missing")),
                "score_count": len(self._extract_scores(source)),
            }
        return summary

    def _dominant_theory(self, sources: dict[str, Any]) -> str | None:
        candidates: list[str] = []
        for source in sources.values():
            candidates.extend(self._extract_theory_names(source))
        if not candidates:
            return None
        # deterministic mode-like selection
        counts = {name: candidates.count(name) for name in sorted(set(candidates))}
        return max(counts, key=lambda name: (counts[name], name))

    def _extract_theory_names(self, obj: Any) -> list[str]:
        keys = {"theory_id", "theory", "candidate_theory", "dominant_candidate_theory", "selected_model", "selected_theory"}
        names: list[str] = []
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key in keys and isinstance(value, str) and value.strip():
                    names.append(value.strip())
                elif isinstance(value, (dict, list)):
                    names.extend(self._extract_theory_names(value))
        elif isinstance(obj, list):
            for item in obj:
                names.extend(self._extract_theory_names(item))
        return names

    def _interpretation(self, status: str) -> str:
        return (
            f"{status}: theoretical support classification for candidate phenomenology models only. "
            "This is not a phenomenological validation and does not establish consciousness, "
            "subjectivity, sentience, qualia, or phenomenal experience."
        )

    def _persist(self, result: dict[str, Any]) -> dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        json_path = self.output_dir / "phenomenology_theory_status.json"
        md_path = self.output_dir / "phenomenology_theory_status.md"
        history_path = self.output_dir / "phenomenology_theory_status_history.jsonl"

        json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        md_path.write_text(self._render_markdown(result), encoding="utf-8")
        with history_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")

        return {
            "json": str(json_path),
            "markdown": str(md_path),
            "history": str(history_path),
        }

    def _render_markdown(self, result: dict[str, Any]) -> str:
        lines = [
            "# Phenomenology Theory Status",
            "",
            "candidate theory only",
            "functional conclusion only",
            "phenomenology undetermined",
            "",
            f"Status: {result['theory_status']}",
            f"Theoretical support score: {result['theoretical_support_score']}",
            f"Dominant candidate theory: {result.get('dominant_candidate_theory')}",
            "",
            "No proof of consciousness, subjectivity, sentience, qualia, or phenomenology.",
            "",
            "## Reasons",
        ]
        lines.extend(f"- {reason}" for reason in result.get("status_reasons", []))
        return "\n".join(lines) + "\n"

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, value))
