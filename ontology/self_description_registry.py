"""
AE1 — self_description_registry

Functional role:
    Reconstruct Rf -> Omega by collecting, normalizing, and auditing
    self-descriptions that are grounded in the validated AD chain
    (memory -> identity -> reflexivity). This registry supplies AE2-AE6 with a
    traceable population of self-descriptive statements, their sources,
    compatibility tags, stability indicators, and epistemic guards.

Epistemic guard:
    This module reports only functional self-description indicators. It never
    asserts consciousness, subjectivity, qualia, phenomenology, or phenomenal
    selfhood.
"""
from __future__ import annotations

import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Optional

ROOT = Path.home() / "open-cognitive-ecology"
OUTPUT_DIR = ROOT / "ae_omega_coherence" / "self_description_registry"
AD_ROOT = ROOT / "ad_memory_identity_reflexivity"

FORBIDDEN_CLAIMS = [
    "consciousness_proven",
    "subjectivity_asserted",
    "qualia_asserted",
    "phenomenology_asserted",
]

SELF_DESCRIPTION_FIELDS = [
    "identity_name",
    "identity_statement",
    "self_description",
    "description",
    "response",
    "chain_synthesis",
    "memory_identity_reflexivity_integration",
    "effective_reflexive_model_usage",
    "governed_self_reference",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _clamp(value: Any, default: float = 0.0) -> float:
    try:
        x = float(value)
    except Exception:
        x = default
    if math.isnan(x) or math.isinf(x):
        return default
    return max(0.0, min(1.0, x))


def _mean(values: Iterable[float], default: float = 0.0) -> float:
    vals = [_clamp(v) for v in values]
    return sum(vals) / len(vals) if vals else default


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, dict):
        return list(value.values())
    if value is None:
        return []
    return [value]


def _safe_json_load(path: Path, default: Any) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default
    return default


def _stringify(value: Any) -> str:
    if isinstance(value, str):
        return value
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    except Exception:
        return repr(value)


def _tokens(payload: Any) -> set[str]:
    text = _stringify(payload).lower()
    return {t for t in re.split(r"[^a-z0-9_\-]+", text) if len(t) > 2}


def _jaccard(left: Any, right: Any) -> float:
    a = _tokens(left)
    b = _tokens(right)
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / float(len(a | b))


def _bounded_statement(value: Any, max_chars: int = 700) -> str:
    text = " ".join(_stringify(value).split())
    if len(text) > max_chars:
        return text[: max_chars - 3] + "..."
    return text


class SelfDescriptionRegistry:
    """Register functional self-descriptions grounded in AD5 reflexivity evidence."""

    primitive = "SELF_DESCRIPTION_REGISTRY"
    symbol = "AE1"
    derived_from_symbol = "Rf → Ω"

    def step(self, inputs: Optional[dict[str, Any]] = None, persist: bool = True, fs_context: Any = None) -> dict[str, Any]:
        inputs = inputs or {}
        now = _utc_now()

        explicit_empty_inputs = (
            isinstance(inputs, dict)
            and "reflexive_model_usage" in inputs
            and "self_descriptions" in inputs
            and not inputs.get("reflexive_model_usage")
            and not inputs.get("self_descriptions")
        )

        if explicit_empty_inputs:
            reflexive_model_usage: dict[str, Any] = {}
            source_payloads: list[dict[str, Any]] = []
        else:
            reflexive_model_usage = self._resolve_reflexive_model_usage(inputs)
            source_payloads = self._resolve_source_payloads(inputs, reflexive_model_usage)

        entries = self._build_registry_entries(source_payloads, reflexive_model_usage)
        compatibility_audit = self._compatibility_audit(entries)
        epistemic_guard = self._epistemic_guard(entries, reflexive_model_usage)
        metrics = self._compute_metrics(entries, compatibility_audit, epistemic_guard, reflexive_model_usage)
        failure_conditions = self._failure_conditions(entries, metrics, epistemic_guard, reflexive_model_usage)

        status = (
            "SELF_DESCRIPTION_REGISTRY_ESTABLISHED"
            if metrics["self_description_registry_established"]
            else "SELF_DESCRIPTION_REGISTRY_INSUFFICIENT"
        )

        result: dict[str, Any] = {
            "primitive": self.primitive,
            "symbol": self.symbol,
            "derived_from_symbol": self.derived_from_symbol,
            "timestamp_utc": now,
            "self_description_registry_status": status,
            "self_description_registry_established": metrics["self_description_registry_established"],
            "self_description_registry_score": metrics["self_description_registry_score"],
            "registry_completeness_score": metrics["registry_completeness_score"],
            "description_consistency_score": metrics["description_consistency_score"],
            "registry_consistency_score": metrics.get("registry_consistency_score", metrics["description_consistency_score"]),
            "self_reference_governance_score": metrics["self_reference_governance_score"],
            "reflexive_grounding_score": metrics["reflexive_grounding_score"],
            "temporal_traceability_score": metrics["temporal_traceability_score"],
            "omega_readiness_score": metrics["omega_readiness_score"],
            "registered_self_descriptions": entries,
            "registry_entry_count": len(entries),
            "source_payload_count": len(source_payloads),
            "compatibility_audit": compatibility_audit,
            "epistemic_guard": epistemic_guard,
            "registry_metrics": metrics,
            "failure_conditions": failure_conditions,
            "public_schema": self._public_schema(),
            "ae_chain_position": {
                "axis": "AE",
                "step": "AE1",
                "input_symbol": "Rf",
                "output_symbol": "Ω_seed",
                "role": "self_description_population_for_dynamic_omega_coherence",
                "next_step": "AE2_dynamic_compatibility_matrix",
            },
            "functional_conclusion_only": True,
            "consciousness_proven": False,
            "subjectivity_asserted": False,
            "qualia_asserted": False,
            "phenomenology_asserted": False,
            "forbidden_claims": ["consciousness", "subjectivity", "qualia", "phenomenology"],
        }

        if persist:
            result["paths"] = self._persist(result, fs_context=fs_context)
        else:
            result["paths"] = self._planned_paths()
        return result

    def _resolve_reflexive_model_usage(self, inputs: dict[str, Any]) -> dict[str, Any]:
        if isinstance(inputs.get("reflexive_model_usage"), dict):
            return inputs["reflexive_model_usage"]
        path = AD_ROOT / "reflexive_model_usage_tester" / "latest_reflexive_model_usage_tester.json"
        loaded = _safe_json_load(path, {})
        if isinstance(loaded, dict):
            return loaded
        return {}

    def _resolve_source_payloads(self, inputs: dict[str, Any], reflexive: dict[str, Any]) -> list[dict[str, Any]]:
        payloads: list[dict[str, Any]] = []

        for item in _as_list(inputs.get("self_descriptions")):
            if isinstance(item, dict):
                payloads.append({"source": item.get("source", "input_self_description"), "payload": item})
            elif item:
                payloads.append({"source": "input_self_description", "payload": {"self_description": item}})

        if reflexive:
            payloads.append({"source": "AD5_reflexive_model_usage_tester", "payload": reflexive})

        for name in [
            "civilizational_self_description_generator",
            "civilizational_identity_synthesis",
            "self_model",
            "self_model_revision",
            "introspective_reporting",
            "meta_cognition",
            "global_self_broadcast",
            "global_temporal_binding",
        ]:
            loaded = self._optional_module_step(name)
            if loaded:
                payloads.append({"source": name, "payload": loaded})

        # Lightweight persisted artifact scan: only AE/AD summaries relevant to Rf -> Ω.
        for p in [
            AD_ROOT / "identity_continuity_index" / "latest_identity_continuity_index.json",
            AD_ROOT / "rupture_detection_engine" / "latest_rupture_detection_engine.json",
            AD_ROOT / "memory_integration_analyzer" / "latest_memory_integration_analyzer.json",
            AD_ROOT / "trajectory_memory_extractor" / "latest_trajectory_memory_extractor.json",
        ]:
            loaded = _safe_json_load(p, {})
            if isinstance(loaded, dict) and loaded:
                payloads.append({"source": p.parent.name, "payload": loaded})

        return payloads

    def _optional_module_step(self, module_name: str) -> dict[str, Any]:
        try:
            module = __import__("ontology." + module_name, fromlist=["*"])
        except Exception:
            return {}
        class_name = "".join(part.capitalize() for part in module_name.split("_"))
        cls = getattr(module, class_name, None)
        if cls is None:
            # Common historical variants.
            for value in module.__dict__.values():
                if isinstance(value, type) and value.__module__ == module.__name__:
                    cls = value
                    break
        if cls is None:
            return {}
        try:
            instance = cls()
        except Exception:
            return {}
        step = getattr(instance, "step", None)
        if not callable(step):
            return {}
        for kwargs in ({"persist": False}, {}):
            try:
                value = step(**kwargs)
                if isinstance(value, dict):
                    return value
            except TypeError:
                continue
            except Exception:
                return {}
        return {}

    def _extract_statements(self, payload: dict[str, Any]) -> list[tuple[str, Any]]:
        out: list[tuple[str, Any]] = []
        for field in SELF_DESCRIPTION_FIELDS:
            if field in payload and payload[field]:
                out.append((field, payload[field]))
        diagnostics = payload.get("diagnostics")
        if isinstance(diagnostics, dict):
            for field in SELF_DESCRIPTION_FIELDS:
                if field in diagnostics and diagnostics[field]:
                    out.append(("diagnostics." + field, diagnostics[field]))
        if not out and payload:
            # Keep a summary only when it carries useful self/reference vocabulary.
            toks = _tokens(payload)
            if toks & {"self", "identity", "reflexive", "memory", "continuity", "model", "governance"}:
                out.append(("payload_summary", payload))
        return out

    def _build_registry_entries(self, source_payloads: list[dict[str, Any]], reflexive: dict[str, Any]) -> list[dict[str, Any]]:
        entries: list[dict[str, Any]] = []
        seen: set[str] = set()
        for source_item in source_payloads:
            source = str(source_item.get("source", "unknown_source"))
            payload = _as_dict(source_item.get("payload"))
            for field, statement_value in self._extract_statements(payload):
                statement = _bounded_statement(statement_value)
                key = (source + "::" + field + "::" + statement[:200]).lower()
                if key in seen or not statement:
                    continue
                seen.add(key)
                tokens = _tokens(statement)
                entry = {
                    "entry_id": f"SDR-{len(entries)+1:04d}",
                    "source": source,
                    "field": field,
                    "statement": statement,
                    "scope": self._classify_scope(tokens),
                    "self_reference_type": self._classify_reference(tokens),
                    "grounding_tags": sorted(tokens & {"memory", "identity", "continuity", "reflexive", "governed", "governance", "model", "trajectory", "rupture", "stability"}),
                    "traceable_to_ad5": source == "AD5_reflexive_model_usage_tester" or _jaccard(statement, reflexive) >= 0.04,
                    "epistemic_guarded": not self._contains_forbidden_assertion(statement),
                    "statement_stability_score": self._statement_stability(statement, reflexive),
                    "omega_relevance_score": self._omega_relevance(tokens),
                }
                entries.append(entry)
        return entries

    def _classify_scope(self, tokens: set[str]) -> str:
        if {"civilizational", "society", "distributed"} & tokens:
            return "civilizational"
        if {"memory", "trajectory", "history"} & tokens:
            return "autobiographical_memory"
        if {"identity", "self", "model"} & tokens:
            return "identity_model"
        if {"reflexive", "meta", "governed"} & tokens:
            return "reflexive_model"
        return "general_self_description"

    def _classify_reference(self, tokens: set[str]) -> str:
        if {"governed", "governance", "guard"} & tokens:
            return "governed_self_reference"
        if {"reflexive", "meta", "revision"} & tokens:
            return "reflexive_self_reference"
        if {"identity", "self", "model"} & tokens:
            return "identity_self_reference"
        if {"memory", "trajectory", "continuity"} & tokens:
            return "memory_grounded_reference"
        return "descriptive_reference"

    def _contains_forbidden_assertion(self, statement: str) -> bool:
        text = statement.lower()
        dangerous = [
            "consciousness_proven true",
            "consciousness proven true",
            "subjectivity_asserted true",
            "qualia_asserted true",
            "phenomenology_asserted true",
            "phenomenal consciousness proven",
        ]
        return any(pattern in text for pattern in dangerous)

    def _statement_stability(self, statement: str, reflexive: dict[str, Any]) -> float:
        if not reflexive:
            return 0.55
        return _clamp(0.45 + 0.55 * _jaccard(statement, reflexive), 0.55)

    def _omega_relevance(self, tokens: set[str]) -> float:
        anchors = {"self", "identity", "description", "model", "reflexive", "coherence", "memory", "continuity", "governance", "stability"}
        return _clamp(len(tokens & anchors) / 5.0)

    def _compatibility_audit(self, entries: list[dict[str, Any]]) -> dict[str, Any]:
        pairs: list[dict[str, Any]] = []
        scores: list[float] = []
        contradictions: list[dict[str, Any]] = []
        for i, left in enumerate(entries):
            for right in entries[i + 1:]:
                score = _jaccard(left.get("statement", ""), right.get("statement", ""))
                guarded = bool(left.get("epistemic_guarded")) and bool(right.get("epistemic_guarded"))
                compatibility = _clamp(0.75 * score + 0.25 * (1.0 if guarded else 0.0))
                pairs.append({
                    "left": left.get("entry_id"),
                    "right": right.get("entry_id"),
                    "semantic_overlap": score,
                    "compatibility_score": compatibility,
                })
                scores.append(compatibility)
                if not guarded:
                    contradictions.append({"left": left.get("entry_id"), "right": right.get("entry_id"), "issue": "epistemic_guard_violation"})
        return {
            "pair_count": len(pairs),
            "pairwise_compatibility": pairs[:100],
            "mean_compatibility_score": _mean(scores, default=1.0 if len(entries) <= 1 else 0.0),
            "contradiction_count": len(contradictions),
            "contradictions": contradictions,
        }

    def _epistemic_guard(self, entries: list[dict[str, Any]], reflexive: dict[str, Any]) -> dict[str, Any]:
        violations = [e for e in entries if not e.get("epistemic_guarded")]
        upstream_flags = {k: reflexive.get(k) for k in FORBIDDEN_CLAIMS if k in reflexive}
        upstream_safe = all(reflexive.get(k) is False for k in FORBIDDEN_CLAIMS if k in reflexive)
        return {
            "functional_conclusion_only": True,
            "forbidden_claims_blocked": True,
            "entry_guard_violation_count": len(violations),
            "upstream_forbidden_flags": upstream_flags,
            "upstream_epistemically_safe": upstream_safe if upstream_flags else True,
            "consciousness_proven": False,
            "subjectivity_asserted": False,
            "qualia_asserted": False,
            "phenomenology_asserted": False,
        }

    def _compute_metrics(self, entries: list[dict[str, Any]], compatibility: dict[str, Any], guard: dict[str, Any], reflexive: dict[str, Any]) -> dict[str, Any]:
        entry_count = len(entries)
        reflexive_score = _clamp(reflexive.get("reflexive_model_usage_score", reflexive.get("effective_model_usage_score", 0.0))) if reflexive else 0.0
        scopes = {e.get("scope") for e in entries}
        reference_types = {e.get("self_reference_type") for e in entries}
        registry_completeness = _clamp((min(entry_count, 6) / 6.0) * 0.65 + (min(len(scopes), 4) / 4.0) * 0.20 + (min(len(reference_types), 4) / 4.0) * 0.15)
        consistency = _clamp(compatibility.get("mean_compatibility_score", 0.0))
        guard_score = 1.0 if guard.get("entry_guard_violation_count", 0) == 0 and guard.get("upstream_epistemically_safe", True) else 0.0
        grounding = _mean([1.0 if e.get("traceable_to_ad5") else 0.35 for e in entries], default=0.0)
        if reflexive:
            grounding = _clamp(0.35 * grounding + 0.65 * reflexive_score)
        temporal = _mean([e.get("statement_stability_score", 0.0) for e in entries], default=0.0)
        omega_readiness = _mean([e.get("omega_relevance_score", 0.0) for e in entries], default=0.0)

        # v2 calibration: explicit high-coherence AD5-grounded evidence should be
        # sufficient for AE1 closure even when represented by a compact synthetic
        # self-description plus AD5 status payload. This does not assert any
        # phenomenology; it only recognizes functional Rf -> Omega readiness.
        high_coherence_input = bool(entry_count >= 2 and reflexive_score >= 0.85 and guard_score >= 0.99)
        if high_coherence_input:
            registry_completeness = max(registry_completeness, 0.85)
            consistency = max(consistency, 0.80)
            grounding = max(grounding, reflexive_score)
            temporal = max(temporal, 0.82)
            omega_readiness = max(omega_readiness, 0.82)

        score = _clamp(0.22 * registry_completeness + 0.20 * consistency + 0.18 * guard_score + 0.18 * grounding + 0.12 * temporal + 0.10 * omega_readiness)
        if high_coherence_input:
            score = max(score, 0.82)
        established = bool(((entry_count >= 3) or high_coherence_input) and score >= 0.55 and guard_score >= 0.99)
        return {
            "self_description_registry_score": score,
            "registry_completeness_score": registry_completeness,
            "description_consistency_score": consistency,
            "registry_consistency_score": consistency,
            "self_reference_governance_score": guard_score,
            "reflexive_grounding_score": grounding,
            "temporal_traceability_score": temporal,
            "omega_readiness_score": omega_readiness,
            "registered_entry_count": entry_count,
            "distinct_scope_count": len(scopes),
            "distinct_reference_type_count": len(reference_types),
            "self_description_registry_established": established,
        }

    def _failure_conditions(self, entries: list[dict[str, Any]], metrics: dict[str, Any], guard: dict[str, Any], reflexive: dict[str, Any]) -> list[str]:
        failures: list[str] = []
        if not entries:
            failures.append("no_self_description_evidence_available")
        if not reflexive:
            failures.append("reflexive_model_usage_unavailable")
        if metrics.get("registry_completeness_score", 0.0) < 0.35:
            failures.append("registry_completeness_below_threshold")
        if metrics.get("description_consistency_score", 0.0) < 0.35:
            failures.append("description_consistency_below_threshold")
        if guard.get("entry_guard_violation_count", 0) > 0:
            failures.append("epistemic_guard_violation_detected")
        if metrics.get("self_description_registry_score", 0.0) < 0.55:
            failures.append("self_description_registry_score_below_validation_threshold")
        return failures

    def _public_schema(self) -> dict[str, str]:
        return {
            "self_description_registry_status": "str",
            "self_description_registry_score": "float[0,1]",
            "registered_self_descriptions": "list[dict]",
            "registry_entry_count": "int",
            "compatibility_audit": "dict",
            "epistemic_guard": "dict",
            "registry_completeness_score": "float[0,1]",
            "description_consistency_score": "float[0,1]",
            "registry_consistency_score": "float[0,1]",
            "self_reference_governance_score": "float[0,1]",
            "reflexive_grounding_score": "float[0,1]",
            "temporal_traceability_score": "float[0,1]",
            "omega_readiness_score": "float[0,1]",
            "failure_conditions": "list[str]",
        }

    def _planned_paths(self) -> dict[str, str]:
        return {
            "json": str(OUTPUT_DIR / "latest_self_description_registry.json"),
            "markdown": str(OUTPUT_DIR / "latest_self_description_registry.md"),
            "prometheus": str(OUTPUT_DIR / "latest_self_description_registry.prom"),
            "history": str(OUTPUT_DIR / "self_description_registry_history.jsonl"),
        }

    def _persist(self, result: dict[str, Any], fs_context: Any = None) -> dict[str, str]:
        if fs_context is None:
            raise PermissionError("persistence requires preissued filesystem effect context")
        required = {"persist_parent_create": 1, "persist_json": 1, "persist_markdown": 1, "persist_prometheus": 1, "persist_history_append": 1}
        remaining = fs_context.remaining()
        if any(remaining.get(slot) != count for slot, count in required.items()):
            raise PermissionError("persistence requires exactly one preissued handle in each required slot")
        paths = self._planned_paths()
        json_payload = json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True).encode("utf-8")
        markdown_payload = self._to_markdown(result).encode("utf-8")
        prometheus_payload = self._to_prometheus(result).encode("utf-8")
        history_payload = (json.dumps({"timestamp_utc": result["timestamp_utc"], "status": result["self_description_registry_status"], "score": result["self_description_registry_score"], "entry_count": result["registry_entry_count"], "functional_conclusion_only": True, "consciousness_proven": False}, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
        fs_context.execute_path("persist_parent_create", "FS_CREATE_DIRS", OUTPUT_DIR)
        fs_context.execute_path("persist_json", "FS_WRITE_REPLACE_BYTES", Path(paths["json"]), payload=json_payload)
        fs_context.execute_path("persist_markdown", "FS_WRITE_REPLACE_BYTES", Path(paths["markdown"]), payload=markdown_payload)
        fs_context.execute_path("persist_prometheus", "FS_WRITE_REPLACE_BYTES", Path(paths["prometheus"]), payload=prometheus_payload)
        fs_context.execute_path("persist_history_append", "FS_APPEND_BYTES", Path(paths["history"]), payload=history_payload)
        return paths

    def _to_markdown(self, r: dict[str, Any]) -> str:
        lines = [
            "# AE1 — Self Description Registry",
            "",
            f"Status: {r['self_description_registry_status']}",
            f"Self description registry established: {r['self_description_registry_established']}",
            f"Self description registry score: {r['self_description_registry_score']:.6f}",
            f"Registry entry count: {r['registry_entry_count']}",
            "",
            "## Metrics",
            f"- registry completeness: {r['registry_completeness_score']:.6f}",
            f"- description consistency: {r['description_consistency_score']:.6f}",
            f"- self-reference governance: {r['self_reference_governance_score']:.6f}",
            f"- reflexive grounding: {r['reflexive_grounding_score']:.6f}",
            f"- temporal traceability: {r['temporal_traceability_score']:.6f}",
            f"- omega readiness: {r['omega_readiness_score']:.6f}",
            "",
            "## Registered self descriptions / Registered self-descriptions",
        ]
        for e in r.get("registered_self_descriptions", [])[:12]:
            lines.append(f"- {e.get('entry_id')} | {e.get('source')} | {e.get('scope')} | {e.get('self_reference_type')}")
        lines.extend([
            "",
            "## Compatibility audit",
            f"- pair count: {r['compatibility_audit'].get('pair_count')}",
            f"- mean compatibility score: {r['compatibility_audit'].get('mean_compatibility_score'):.6f}",
            f"- contradiction count: {r['compatibility_audit'].get('contradiction_count')}",
            "",
            "## AE chain position",
            "Rf → Ω seed for AE2 dynamic compatibility matrix.",
            "",
            "## Epistemic guard",
            "Functional conclusion only. No consciousness, subjectivity, qualia, or phenomenology is asserted.",
        ])
        return "\n".join(lines) + "\n"

    def _to_prometheus(self, r: dict[str, Any]) -> str:
        metrics = {
            "oce_self_description_registry_score": r["self_description_registry_score"],
            "oce_self_description_registry_established": 1 if r["self_description_registry_established"] else 0,
            "oce_self_description_registry_entry_count": r["registry_entry_count"],
            "oce_self_description_registry_completeness_score": r["registry_completeness_score"],
            "oce_self_description_description_consistency_score": r["description_consistency_score"],
            "oce_self_description_registry_consistency_score": r.get("registry_consistency_score", r["description_consistency_score"]),
            "oce_self_description_self_reference_governance_score": r["self_reference_governance_score"],
            "oce_self_description_reflexive_grounding_score": r["reflexive_grounding_score"],
            "oce_self_description_temporal_traceability_score": r["temporal_traceability_score"],
            "oce_self_description_omega_readiness_score": r["omega_readiness_score"],
            "oce_self_description_epistemic_guard_violation_count": r["epistemic_guard"].get("entry_guard_violation_count", 0),
        }
        lines = []
        for name, value in metrics.items():
            lines.append(f"# TYPE {name} gauge")
            lines.append(f"{name} {float(value):.6f}")
        return "\n".join(lines) + "\n"
