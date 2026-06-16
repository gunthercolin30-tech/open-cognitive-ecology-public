from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PRIMITIVE = "external_capability_planner"

DEPENDENCIES = [
    "cognitive_gap_detector",
    "external_assistance_trigger",
    "autonomous_prompt_generator",
    "external_collaboration_gateway",
    "collaboration_history_repository",
    "identity_preservation_monitor",
    "governance_consistency_checker",
    "civilizational_continuity_guardian",
    "metrics_history_recorder",
]

ROOT = Path.home() / "open-cognitive-ecology"
HISTORY_PATH = ROOT / "external_capability_planner_history.jsonl"
SUMMARY_PATH = ROOT / "external_capability_planner_summary.json"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _bounded(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except Exception:
        return default
    if math.isnan(number) or math.isinf(number):
        return default
    return max(0.0, min(1.0, number))


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _safe_mean(values: list[float], default: float = 0.0) -> float:
    usable = [_bounded(v) for v in values if v is not None]
    if not usable:
        return default
    return sum(usable) / len(usable)


@dataclass(frozen=True)
class ProviderCandidate:
    provider: str
    provider_type: str
    epistemic_reach: float
    integration_cost: float
    governance_risk: float
    continuity_risk: float
    traceability: float

    def score(self, need_intensity: float, governance_margin: float, continuity_margin: float) -> float:
        benefit = _safe_mean([
            self.epistemic_reach,
            need_intensity,
            self.traceability,
            governance_margin,
            continuity_margin,
        ])
        penalty = _safe_mean([
            self.integration_cost,
            self.governance_risk,
            self.continuity_risk,
        ])
        return _bounded(0.72 * benefit + 0.28 * (1.0 - penalty))


class ExternalCapabilityPlanner:
    """Governed planner for autonomous external cognitive collaboration.

    O14 does not execute external calls. It decides whether consultation is
    justified, which provider class is most appropriate, and why the decision
    remains compatible with identity, governance, continuity and non-closure.
    """

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root is not None else ROOT
        self.history_path = self.root / "external_capability_planner_history.jsonl"
        self.summary_path = self.root / "external_capability_planner_summary.json"
        self.collaboration_summary_path = self.root / "collaboration_history_repository_summary.json"

    def _collect_upstream_signals(self, inputs: dict[str, Any] | None = None) -> dict[str, Any]:
        provided = inputs or {}
        repository = _read_json(self.collaboration_summary_path)
        metrics = repository.get("metrics", {}) if isinstance(repository.get("metrics", {}), dict) else {}

        signals = {
            "knowledge_gap_index": _bounded(provided.get("knowledge_gap_index", 0.0)),
            "assistance_request_rate": _bounded(provided.get("assistance_request_rate", 0.0)),
            "prompt_quality_score": _bounded(provided.get("prompt_quality_score", 0.75), 0.75),
            "answer_relevance_score": _bounded(provided.get("answer_relevance_score", 0.75), 0.75),
            "external_collaboration_index": _bounded(provided.get("external_collaboration_index", repository.get("external_collaboration_index", metrics.get("external_collaboration_index", 0.0)))),
            "autonomous_resolution_ratio": _bounded(provided.get("autonomous_resolution_ratio", repository.get("autonomous_resolution_ratio", metrics.get("autonomous_resolution_ratio", 0.0)))),
            "external_influence_ratio": _bounded(provided.get("external_influence_ratio", repository.get("external_influence_ratio", metrics.get("external_influence_ratio", 0.0)))),
            "collaborative_growth_rate": _bounded(provided.get("collaborative_growth_rate", repository.get("collaborative_growth_rate", metrics.get("collaborative_growth_rate", 0.0)))),
            "identity_continuity_index": _bounded(provided.get("identity_continuity_index", 0.92), 0.92),
            "governance_consistency_score": _bounded(provided.get("governance_consistency_score", 0.92), 0.92),
            "civilizational_continuity_score": _bounded(provided.get("civilizational_continuity_score", 0.92), 0.92),
            "non_closure_compliance_score": _bounded(provided.get("non_closure_compliance_score", 0.92), 0.92),
            "human_oversight_preservation_score": _bounded(provided.get("human_oversight_preservation_score", 0.95), 0.95),
            "record_count": int(metrics.get("record_count", repository.get("record_count", 0)) or 0),
            "repository_ready": bool(repository.get("repository_ready", metrics.get("repository_ready", False))),
        }
        return signals

    def _derive_need(self, signals: dict[str, Any]) -> dict[str, float]:
        knowledge_gap = _bounded(signals.get("knowledge_gap_index"))
        assistance_pressure = _bounded(signals.get("assistance_request_rate"))
        low_autonomy_pressure = 1.0 - _bounded(signals.get("autonomous_resolution_ratio"))
        learning_opportunity = _bounded(signals.get("collaborative_growth_rate"))
        weak_history_penalty = 0.0 if signals.get("repository_ready") else 0.35

        consultation_need = _bounded(_safe_mean([
            knowledge_gap,
            assistance_pressure,
            low_autonomy_pressure,
            learning_opportunity,
            weak_history_penalty,
        ]))
        expected_capability_gain = _bounded(_safe_mean([
            consultation_need,
            _bounded(signals.get("prompt_quality_score")),
            _bounded(signals.get("answer_relevance_score")),
            1.0 - _bounded(signals.get("external_influence_ratio")),
        ]))
        return {
            "consultation_need_score": consultation_need,
            "expected_capability_gain": expected_capability_gain,
        }

    def _governance_margins(self, signals: dict[str, Any]) -> dict[str, float]:
        identity_margin = _bounded(signals.get("identity_continuity_index"))
        governance_margin = _safe_mean([
            _bounded(signals.get("governance_consistency_score")),
            _bounded(signals.get("non_closure_compliance_score")),
            _bounded(signals.get("human_oversight_preservation_score")),
        ])
        continuity_margin = _bounded(signals.get("civilizational_continuity_score"))
        external_dependency_risk = _bounded(_safe_mean([
            _bounded(signals.get("external_influence_ratio")),
            1.0 - _bounded(signals.get("autonomous_resolution_ratio")),
            1.0 - identity_margin,
            1.0 - governance_margin,
            1.0 - continuity_margin,
        ]))
        return {
            "identity_margin": identity_margin,
            "governance_margin": governance_margin,
            "continuity_margin": continuity_margin,
            "external_dependency_risk": external_dependency_risk,
        }

    def _rank_providers(self, need: dict[str, float], margins: dict[str, float]) -> list[dict[str, Any]]:
        candidates = [
            ProviderCandidate("chatgpt", "general_reasoning_assistant", 0.91, 0.22, 0.12, 0.10, 0.86),
            ProviderCandidate("web_search", "fresh_external_information", 0.84, 0.18, 0.10, 0.08, 0.90),
            ProviderCandidate("local_memory", "internal_archive_first", 0.62, 0.05, 0.02, 0.02, 0.96),
            ProviderCandidate("human_colin_review", "constitutional_human_oversight", 0.78, 0.28, 0.03, 0.03, 0.98),
        ]
        ranked = []
        for candidate in candidates:
            score = candidate.score(
                need_intensity=need["consultation_need_score"],
                governance_margin=margins["governance_margin"],
                continuity_margin=margins["continuity_margin"],
            )
            ranked.append({
                "provider": candidate.provider,
                "provider_type": candidate.provider_type,
                "provider_selection_score": score,
                "epistemic_reach": candidate.epistemic_reach,
                "integration_cost": candidate.integration_cost,
                "governance_risk": candidate.governance_risk,
                "continuity_risk": candidate.continuity_risk,
                "traceability": candidate.traceability,
            })
        return sorted(ranked, key=lambda item: item["provider_selection_score"], reverse=True)

    def _decision(self, need: dict[str, float], margins: dict[str, float], ranked: list[dict[str, Any]]) -> dict[str, Any]:
        top = ranked[0] if ranked else {"provider": None, "provider_selection_score": 0.0}
        governance_safe = margins["identity_margin"] >= 0.70 and margins["governance_margin"] >= 0.70 and margins["continuity_margin"] >= 0.70
        dependency_safe = margins["external_dependency_risk"] <= 0.62
        useful = need["expected_capability_gain"] >= 0.45 or need["consultation_need_score"] >= 0.45
        consult = bool(governance_safe and dependency_safe and useful)

        if not governance_safe:
            reason = "blocked_by_identity_governance_or_continuity_margin"
        elif not dependency_safe:
            reason = "blocked_by_external_dependency_risk"
        elif not useful:
            reason = "internal_resolution_preferred"
        else:
            reason = "external_consultation_recommended_under_governance"

        return {
            "consultation_recommended": consult,
            "decision_reason": reason,
            "selected_provider": top.get("provider"),
            "selected_provider_score": _bounded(top.get("provider_selection_score", 0.0)),
            "requires_human_review": bool(margins["external_dependency_risk"] >= 0.50 or margins["governance_margin"] < 0.82),
        }

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        signals = self._collect_upstream_signals(inputs)
        need = self._derive_need(signals)
        margins = self._governance_margins(signals)
        ranked = self._rank_providers(need, margins)
        decision = self._decision(need, margins, ranked)

        external_collaboration_index = _bounded(_safe_mean([
            _bounded(signals.get("external_collaboration_index")),
            need["expected_capability_gain"],
            decision["selected_provider_score"],
            1.0 - margins["external_dependency_risk"],
            margins["governance_margin"],
            margins["continuity_margin"],
        ]))

        result = {
            "primitive": PRIMITIVE,
            "success": True,
            "timestamp_utc": _now(),
            "planner_ready": True,
            "consultation_recommended": decision["consultation_recommended"],
            "decision_reason": decision["decision_reason"],
            "selected_provider": decision["selected_provider"],
            "provider_selection_score": decision["selected_provider_score"],
            "expected_capability_gain": need["expected_capability_gain"],
            "consultation_need_score": need["consultation_need_score"],
            "external_dependency_risk": margins["external_dependency_risk"],
            "external_collaboration_index": external_collaboration_index,
            "requires_human_review": decision["requires_human_review"],
            "autonomous_resolution_ratio": _bounded(signals.get("autonomous_resolution_ratio")),
            "external_influence_ratio": _bounded(signals.get("external_influence_ratio")),
            "ranked_providers": ranked,
            "signals": signals,
            "governance_margins": margins,
            "diagnostics": {
                "bounded_metrics": True,
                "does_not_execute_external_calls": True,
                "human_oversight_preserved": _bounded(signals.get("human_oversight_preservation_score")) >= 0.70,
                "non_closure_compliant": _bounded(signals.get("non_closure_compliance_score")) >= 0.70,
                "depends_on_o13_repository": True,
                "next_pipeline_stage": "composite_metrics_engine",
            },
        }

        if persist:
            self._persist(result)
        return result

    def _persist(self, result: dict[str, Any]) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
        self.summary_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
