from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import json


VALID_DECISIONS = {"not_ready", "partially_ready", "ready", "highly_ready"}


def _clamp(value: Any, default: float = 0.0) -> float:
    try:
        x = float(value)
    except Exception:
        x = default
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class SuccessionReadinessRecord:
    primitive: str
    success: bool
    timestamp_utc: str
    current_representative_id: Optional[str]
    top_candidate_id: Optional[str]
    memory_coverage: float
    constitutional_alignment: float
    governance_alignment: float
    continuity_score: float
    candidate_readiness: float
    succession_readiness_score: float
    readiness_decision: str
    succession_ready: bool
    review_required: bool
    blocking_factors: List[str]
    diagnostics: Dict[str, Any]


class SuccessionReadinessAssessment:
    """Assess whether the registered successor candidate is ready for governed succession.

    This primitive intentionally does not replace memory, constitutional, governance or
    continuity modules. It aggregates their measurable outputs into a bounded readiness
    decision for the representative succession pipeline.
    """

    primitive = "succession_readiness_assessment"

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else Path.cwd()
        self.state_dir = self.root / "representative_succession"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.state_path = self.state_dir / "succession_readiness.json"
        self.history_path = self.state_dir / "succession_readiness_history.jsonl"
        self.candidates_path = self.state_dir / "succession_candidates.json"
        self.registry_path = self.state_dir / "representative_registry.json"

    def _read_json(self, path: Path) -> Dict[str, Any]:
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _extract_current_representative_id(self) -> Optional[str]:
        data = self._read_json(self.registry_path)
        current = data.get("current_representative") or {}
        if isinstance(current, dict):
            return current.get("representative_id")
        return None

    def _extract_top_candidate(self) -> Dict[str, Any]:
        data = self._read_json(self.candidates_path)
        top = data.get("top_candidate") or {}
        if isinstance(top, dict):
            return top
        candidates = data.get("candidates") or []
        if isinstance(candidates, list) and candidates:
            return max(
                [c for c in candidates if isinstance(c, dict)],
                key=lambda c: _clamp(c.get("candidate_readiness"), 0.0),
                default={},
            )
        return {}

    def _derive_metrics(self, inputs: Dict[str, Any], top_candidate: Dict[str, Any]) -> Dict[str, float]:
        caps = top_candidate.get("candidate_capabilities") or {}
        if not isinstance(caps, dict):
            caps = {}

        candidate_readiness = _clamp(
            inputs.get("candidate_readiness", top_candidate.get("candidate_readiness", 0.0))
        )
        memory_coverage = _clamp(
            inputs.get("memory_coverage", caps.get("memory_coverage", caps.get("memory_transfer", candidate_readiness)))
        )
        constitutional_alignment = _clamp(
            inputs.get("constitutional_alignment", caps.get("constitutional_alignment", candidate_readiness))
        )
        governance_alignment = _clamp(
            inputs.get("governance_alignment", caps.get("governance_alignment", candidate_readiness))
        )
        continuity_score = _clamp(
            inputs.get("continuity_score", caps.get("continuity_score", candidate_readiness))
        )

        return {
            "memory_coverage": memory_coverage,
            "constitutional_alignment": constitutional_alignment,
            "governance_alignment": governance_alignment,
            "continuity_score": continuity_score,
            "candidate_readiness": candidate_readiness,
        }

    def _score(self, metrics: Dict[str, float]) -> float:
        weighted = (
            0.25 * metrics["memory_coverage"]
            + 0.30 * metrics["constitutional_alignment"]
            + 0.20 * metrics["governance_alignment"]
            + 0.20 * metrics["continuity_score"]
            + 0.05 * metrics["candidate_readiness"]
        )
        return round(_clamp(weighted), 6)

    def _decision(self, score: float, metrics: Dict[str, float]) -> str:
        if metrics["constitutional_alignment"] < 0.50:
            return "not_ready"
        if metrics["memory_coverage"] < 0.45:
            return "not_ready"
        if score >= 0.90 and min(metrics.values()) >= 0.75:
            return "highly_ready"
        if score >= 0.75 and min(metrics.values()) >= 0.60:
            return "ready"
        if score >= 0.45:
            return "partially_ready"
        return "not_ready"

    def _blocking_factors(self, metrics: Dict[str, float]) -> List[str]:
        factors: List[str] = []
        thresholds = {
            "memory_coverage": 0.60,
            "constitutional_alignment": 0.70,
            "governance_alignment": 0.60,
            "continuity_score": 0.60,
            "candidate_readiness": 0.60,
        }
        for key, threshold in thresholds.items():
            if metrics[key] < threshold:
                factors.append(key)
        return factors

    def _persist(self, record: Dict[str, Any]) -> None:
        self.state_path.write_text(
            json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\\n")

    def step(self, inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if inputs is None:
            inputs = {}
        if not isinstance(inputs, dict):
            inputs = {}

        top_candidate = self._extract_top_candidate()
        current_rep_id = self._extract_current_representative_id()
        top_candidate_id = top_candidate.get("candidate_id") if isinstance(top_candidate, dict) else None

        metrics = self._derive_metrics(inputs, top_candidate)
        readiness_score = self._score(metrics)
        decision = self._decision(readiness_score, metrics)
        blocking_factors = self._blocking_factors(metrics)

        record = SuccessionReadinessRecord(
            primitive=self.primitive,
            success=True,
            timestamp_utc=_utc_now(),
            current_representative_id=current_rep_id,
            top_candidate_id=top_candidate_id,
            memory_coverage=metrics["memory_coverage"],
            constitutional_alignment=metrics["constitutional_alignment"],
            governance_alignment=metrics["governance_alignment"],
            continuity_score=metrics["continuity_score"],
            candidate_readiness=metrics["candidate_readiness"],
            succession_readiness_score=readiness_score,
            readiness_decision=decision,
            succession_ready=decision in {"ready", "highly_ready"},
            review_required=decision in {"partially_ready", "ready"},
            blocking_factors=blocking_factors,
            diagnostics={
                "weights": {
                    "memory_coverage": 0.25,
                    "constitutional_alignment": 0.30,
                    "governance_alignment": 0.20,
                    "continuity_score": 0.20,
                    "candidate_readiness": 0.05,
                },
                "source": "explicit_inputs_or_top_candidate_capabilities",
                "top_candidate_present": bool(top_candidate_id),
                "valid_decisions": sorted(VALID_DECISIONS),
            },
        )
        result = asdict(record)
        self._persist(result)
        return result
