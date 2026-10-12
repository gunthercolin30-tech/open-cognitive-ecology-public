
"""
AD2 — memory_integration_analyzer

Functional role:
    Integrate trajectory-memory evidence from AD1 with existing OCE memory,
    continuity, identity and reflexivity indicators.

Epistemic guard:
    This module reports only functional memory-integration indicators.
    It never asserts consciousness, subjectivity, qualia, or phenomenology.
"""
from __future__ import annotations

import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path.home() / "open-cognitive-ecology"
OUTPUT_DIR = ROOT / "ad_memory_identity_reflexivity" / "memory_integration_analyzer"


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


class MemoryIntegrationAnalyzer:
    """Analyze functional integration of trajectory memories into M.

    Public interface:
        step(inputs: dict | None = None, persist: bool = True) -> dict

    Inputs may contain:
        - trajectory_memory: explicit AD1 result
        - memory_modules: optional mapping of module outputs
        - synthetic_sources: optional list of source records

    Output status:
        - MEMORY_INTEGRATION_ANALYZED
        - MEMORY_INTEGRATION_INSUFFICIENT
    """

    primitive = "MEMORY_INTEGRATION_ANALYZER"
    symbol = "AD2"
    derived_from_symbol = "Π → M → I → Rf"

    MEMORY_COMPONENTS = [
        "trajectory_memory_extractor",
        "autobiographical_memory",
        "civilizational_memory",
        "civilizational_memory_archive",
        "distributed_civilizational_memory",
        "persistent_multi_scale_memory",
        "memory_consolidation",
        "memory_drift_monitor",
        "memory_transmission_protocol",
        "conversation_memory_archive",
        "dialogue_memory_persistence",
        "civilizational_dialogue_memory",
        "continuity_metrics_engine",
        "structural_continuity",
        "temporal_self_continuity",
        "identity_preservation_monitor",
        "civilizational_identity_preservation",
        "civilizational_identity_synthesis",
        "self_model",
        "self_model_revision",
        "reflexive_threshold",
        "reflexive_model_revision_ecology",
        "meta_cognition",
        "introspective_reporting",
    ]

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        inputs = inputs or {}
        now = _utc_now()

        explicit_empty_inputs = (
            isinstance(inputs, dict)
            and "trajectory_memory" in inputs
            and "memory_modules" in inputs
            and "synthetic_sources" in inputs
            and not inputs.get("trajectory_memory")
            and not inputs.get("memory_modules")
            and not _as_list(inputs.get("synthetic_sources"))
        )

        if explicit_empty_inputs:
            trajectory_memory = {}
            memory_modules = {}
            synthetic_sources = []
        else:
            trajectory_memory = self._resolve_trajectory_memory(inputs)
            memory_modules = self._collect_memory_modules(inputs)
            synthetic_sources = _as_list(inputs.get("synthetic_sources"))

        memory_sources = self._build_memory_sources(trajectory_memory, memory_modules, synthetic_sources)
        failure_conditions: list[str] = []

        if not memory_sources:
            failure_conditions.append("no_memory_sources_available")

        integration_matrix = self._build_integration_matrix(memory_sources)
        integration_links = self._build_integration_links(memory_sources)
        coherence_fields = self._build_coherence_fields(memory_sources, trajectory_memory)
        consolidation_channels = self._build_consolidation_channels(memory_sources)
        continuity_bindings = self._build_continuity_bindings(memory_sources, trajectory_memory)
        identity_bindings = self._build_identity_bindings(memory_sources, trajectory_memory)
        reflexive_bindings = self._build_reflexive_bindings(memory_sources, trajectory_memory)
        integration_conflicts = self._detect_conflicts(memory_sources)

        integration_metrics = self._compute_metrics(
            memory_sources=memory_sources,
            integration_matrix=integration_matrix,
            integration_links=integration_links,
            coherence_fields=coherence_fields,
            consolidation_channels=consolidation_channels,
            continuity_bindings=continuity_bindings,
            identity_bindings=identity_bindings,
            reflexive_bindings=reflexive_bindings,
            integration_conflicts=integration_conflicts,
        )

        memory_integration_analyzed = bool(memory_sources) and integration_metrics["memory_integration_score"] >= 0.2
        status = "MEMORY_INTEGRATION_ANALYZED" if memory_integration_analyzed else "MEMORY_INTEGRATION_INSUFFICIENT"
        if not memory_integration_analyzed and "insufficient_integration_evidence" not in failure_conditions:
            failure_conditions.append("insufficient_integration_evidence")

        result: dict[str, Any] = {
            "primitive": self.primitive,
            "symbol": self.symbol,
            "derived_from_symbol": self.derived_from_symbol,
            "timestamp_utc": now,
            "memory_integration_analyzer_status": status,
            "memory_integration_analyzed": memory_integration_analyzed,
            "memory_sources": memory_sources,
            "memory_source_count": len(memory_sources),
            "integrated_memory_profile": {
                "source_count": len(memory_sources),
                "integration_score": integration_metrics["memory_integration_score"],
                "coherence_score": integration_metrics.get("coherence_score", 0.0),
                "source_diversity": integration_metrics.get("source_diversity", 0.0),
                "status": status,
                "functional_conclusion_only": True,
            },
            "trajectory_memory_summary": {
                "available": bool(trajectory_memory),
                "event_count": int(trajectory_memory.get("event_count") or len(_as_list(trajectory_memory.get("trajectory_events")))) if isinstance(trajectory_memory, dict) else 0,
                "segment_count": int(trajectory_memory.get("segment_count") or len(_as_list(trajectory_memory.get("trajectory_segments")))) if isinstance(trajectory_memory, dict) else 0,
                "status": trajectory_memory.get("trajectory_memory_extractor_status") if isinstance(trajectory_memory, dict) else None,
            },
            "cross_memory_links": integration_links,
            "identity_relevant_memory": identity_bindings,
            "reflexive_relevant_memory": reflexive_bindings,
            "continuity_indicators": continuity_bindings,
            "integration_matrix": integration_matrix,
            "integration_links": integration_links,
            "coherence_fields": coherence_fields,
            "consolidation_channels": consolidation_channels,
            "continuity_bindings": continuity_bindings,
            "identity_bindings": identity_bindings,
            "reflexive_bindings": reflexive_bindings,
            "integration_conflicts": integration_conflicts,
            "integration_metrics": integration_metrics,
            "memory_integration_score": integration_metrics["memory_integration_score"],
            "failure_conditions": failure_conditions,
            "epistemic_guard": {
                "functional_conclusion_only": True,
                "consciousness_proven": False,
                "phenomenology_asserted": False,
                "subjectivity_asserted": False,
                "qualia_asserted": False,
            },
            "consciousness_proven": False,
            "functional_conclusion_only": True,
            "phenomenology_asserted": False,
            "subjectivity_asserted": False,
            "qualia_asserted": False,
        }

        if persist:
            result["paths"] = self._persist(result)
        else:
            result["paths"] = self._planned_paths()
        return result

    def _resolve_trajectory_memory(self, inputs: dict[str, Any]) -> dict[str, Any]:
        explicit = inputs.get("trajectory_memory") or inputs.get("ad1")
        if isinstance(explicit, dict):
            return explicit
        try:
            from ontology.trajectory_memory_extractor import TrajectoryMemoryExtractor
            return TrajectoryMemoryExtractor().step(persist=False)
        except Exception:
            latest = ROOT / "ad_memory_identity_reflexivity" / "trajectory_memory_extractor" / "latest_trajectory_memory_extractor.json"
            try:
                if latest.exists():
                    data = json.loads(latest.read_text(encoding="utf-8"))
                    if isinstance(data, dict):
                        return data
            except Exception:
                return {}
        return {}

    def _collect_memory_modules(self, inputs: dict[str, Any]) -> dict[str, Any]:
        explicit = inputs.get("memory_modules")
        if isinstance(explicit, dict):
            return explicit

        outputs: dict[str, Any] = {}
        # Use safe, lightweight calls only. Many legacy modules require args; failures are ignored.
        calls = [
            ("memory_consolidation", "MemoryConsolidation", {"retained_patterns": [1, 1, 1], "consistency_signals": [1, 1], "persistence_signals": [1, 1]}),
            ("memory_drift_monitor", "MemoryDriftMonitor", {}),
            ("civilizational_memory", "CivilizationalMemory", {}),
            ("civilizational_memory_archive", "CivilizationalMemoryArchive", {}),
            ("distributed_civilizational_memory", "DistributedCivilizationalMemory", {}),
            ("continuity_metrics_engine", "ContinuityMetricsEngine", {}),
            ("civilizational_identity_synthesis", "CivilizationalIdentitySynthesis", {}),
            ("reflexive_threshold", "ReflexiveThreshold", {}),
            ("meta_cognition", "MetaCognition", {}),
            ("introspective_reporting", "IntrospectiveReporting", {}),
        ]
        for module_name, class_name, kwargs in calls:
            try:
                module = __import__(f"ontology.{module_name}", fromlist=[class_name])
                cls = getattr(module, class_name)
                inst = cls()
                if kwargs:
                    out = inst.step(**kwargs)
                else:
                    out = inst.step()
                if isinstance(out, dict):
                    outputs[module_name] = out
            except Exception:
                continue
        return outputs

    def _build_memory_sources(self, trajectory_memory: dict[str, Any], memory_modules: dict[str, Any], synthetic_sources: list[Any]) -> list[dict[str, Any]]:
        sources: list[dict[str, Any]] = []
        if trajectory_memory:
            metrics = _as_dict(trajectory_memory.get("trajectory_metrics")) or _as_dict(trajectory_memory.get("memory_trajectory_metrics"))
            sources.append({
                "source_id": "AD1_trajectory_memory",
                "source_type": "trajectory_memory",
                "module": "trajectory_memory_extractor",
                "available": True,
                "event_count": int(trajectory_memory.get("event_count") or len(_as_list(trajectory_memory.get("trajectory_events")))),
                "segment_count": int(trajectory_memory.get("segment_count") or len(_as_list(trajectory_memory.get("trajectory_segments")))),
                "metric_keys": sorted(metrics.keys()),
                "functional_score": self._score_mapping(metrics, default=0.75),
                "categories": self._categories_from_text(trajectory_memory),
            })
        for name, payload in sorted(memory_modules.items()):
            if not isinstance(payload, dict):
                continue
            sources.append({
                "source_id": f"module_{name}",
                "source_type": "memory_module",
                "module": name,
                "available": True,
                "event_count": len(_as_list(payload.get("events") or payload.get("records") or payload.get("history") or payload.get("items"))),
                "segment_count": len(_as_list(payload.get("segments") or payload.get("states") or payload.get("snapshots"))),
                "metric_keys": sorted([k for k, v in payload.items() if isinstance(v, (int, float, bool)) or k.endswith("score") or k.endswith("index")]),
                "functional_score": self._score_mapping(payload, default=0.6),
                "categories": self._categories_from_text(payload),
            })
        for i, item in enumerate(synthetic_sources):
            payload = item if isinstance(item, dict) else {"value": item}
            sources.append({
                "source_id": f"synthetic_{i:03d}",
                "source_type": "synthetic",
                "module": str(payload.get("module", "synthetic")),
                "available": True,
                "event_count": len(_as_list(payload.get("events"))),
                "segment_count": len(_as_list(payload.get("segments"))),
                "metric_keys": sorted([k for k, v in payload.items() if isinstance(v, (int, float, bool))]),
                "functional_score": self._score_mapping(payload, default=0.5),
                "categories": self._categories_from_text(payload),
            })
        return sources

    def _build_integration_matrix(self, sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
        matrix: list[dict[str, Any]] = []
        for a in sources:
            for b in sources:
                if a["source_id"] >= b["source_id"]:
                    continue
                cats_a = set(a.get("categories", []))
                cats_b = set(b.get("categories", []))
                keys_a = set(a.get("metric_keys", []))
                keys_b = set(b.get("metric_keys", []))
                overlap = 0.0
                denom = len(cats_a | cats_b) + len(keys_a | keys_b)
                if denom:
                    overlap = (len(cats_a & cats_b) + len(keys_a & keys_b)) / denom
                coupling = _clamp((overlap + a.get("functional_score", 0.0) + b.get("functional_score", 0.0)) / 3.0)
                matrix.append({
                    "source_a": a["source_id"],
                    "source_b": b["source_id"],
                    "category_overlap": _clamp(overlap),
                    "integration_coupling": coupling,
                })
        return matrix

    def _build_integration_links(self, sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
        links = []
        for s in sources:
            cats = set(s.get("categories", []))
            if "memory" in cats or s.get("source_type") == "trajectory_memory":
                links.append({"from": s["source_id"], "to": "integrated_memory_field", "link_type": "memory_binding", "strength": _clamp(s.get("functional_score", 0.0))})
            if "identity" in cats:
                links.append({"from": s["source_id"], "to": "identity_continuity_field", "link_type": "identity_binding", "strength": _clamp(s.get("functional_score", 0.0))})
            if "reflexivity" in cats:
                links.append({"from": s["source_id"], "to": "reflexive_model_field", "link_type": "reflexive_binding", "strength": _clamp(s.get("functional_score", 0.0))})
        return links

    def _build_coherence_fields(self, sources: list[dict[str, Any]], trajectory_memory: dict[str, Any]) -> dict[str, Any]:
        cats = set()
        for s in sources:
            cats.update(s.get("categories", []))
        tm = _as_dict(trajectory_memory.get("trajectory_metrics")) or _as_dict(trajectory_memory.get("memory_trajectory_metrics"))
        return {
            "memory_coherence": self._presence_score(sources, ["memory", "validation", "runtime"]),
            "temporal_coherence": _clamp(tm.get("temporal_ordering_score", tm.get("temporal_coverage", 0.75 if trajectory_memory else 0.0))),
            "cross_source_coherence": _clamp(len(cats) / 6.0),
            "coherence_categories": sorted(cats),
        }

    def _build_consolidation_channels(self, sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
        channels = []
        for target in ["archive", "distributed", "dialogue", "trajectory", "identity", "reflexive"]:
            matching = [s for s in sources if target in s.get("module", "") or target in s.get("categories", [])]
            channels.append({
                "channel": target,
                "source_count": len(matching),
                "channel_strength": self._mean([_clamp(s.get("functional_score", 0.0)) for s in matching]) if matching else 0.0,
            })
        return channels

    def _build_continuity_bindings(self, sources: list[dict[str, Any]], trajectory_memory: dict[str, Any]) -> list[dict[str, Any]]:
        bindings = []
        markers = _as_list(trajectory_memory.get("continuity_markers"))
        bindings.append({"binding": "trajectory_to_continuity", "evidence_count": len(markers), "binding_strength": _clamp(0.5 + min(len(markers), 10) / 20.0) if trajectory_memory else 0.0})
        for s in sources:
            if "continuity" in s.get("module", "") or "identity" in s.get("categories", []):
                bindings.append({"binding": f"{s['source_id']}_continuity", "evidence_count": s.get("event_count", 0), "binding_strength": _clamp(s.get("functional_score", 0.0))})
        return bindings

    def _build_identity_bindings(self, sources: list[dict[str, Any]], trajectory_memory: dict[str, Any]) -> list[dict[str, Any]]:
        events = _as_list(trajectory_memory.get("identity_relevant_events"))
        bindings = [{"binding": "trajectory_to_identity", "evidence_count": len(events), "binding_strength": _clamp(0.5 + min(len(events), 10) / 20.0) if trajectory_memory else 0.0}]
        for s in sources:
            if "identity" in s.get("module", "") or "identity" in s.get("categories", []):
                bindings.append({"binding": f"{s['source_id']}_identity", "evidence_count": s.get("event_count", 0), "binding_strength": _clamp(s.get("functional_score", 0.0))})
        return bindings

    def _build_reflexive_bindings(self, sources: list[dict[str, Any]], trajectory_memory: dict[str, Any]) -> list[dict[str, Any]]:
        events = _as_list(trajectory_memory.get("reflexive_relevant_events"))
        bindings = [{"binding": "trajectory_to_reflexivity", "evidence_count": len(events), "binding_strength": _clamp(0.5 + min(len(events), 10) / 20.0) if trajectory_memory else 0.0}]
        for s in sources:
            if "reflex" in s.get("module", "") or "meta" in s.get("module", "") or "reflexivity" in s.get("categories", []):
                bindings.append({"binding": f"{s['source_id']}_reflexivity", "evidence_count": s.get("event_count", 0), "binding_strength": _clamp(s.get("functional_score", 0.0))})
        return bindings

    def _detect_conflicts(self, sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
        conflicts = []
        for s in sources:
            score = _clamp(s.get("functional_score", 0.0))
            if score < 0.2:
                conflicts.append({"source_id": s["source_id"], "conflict_type": "low_functional_score", "severity": _clamp(1.0 - score)})
        return conflicts

    def _compute_metrics(self, **kwargs: Any) -> dict[str, float]:
        sources = kwargs["memory_sources"]
        matrix = kwargs["integration_matrix"]
        links = kwargs["integration_links"]
        coherence = kwargs["coherence_fields"]
        channels = kwargs["consolidation_channels"]
        continuity = kwargs["continuity_bindings"]
        identity = kwargs["identity_bindings"]
        reflexive = kwargs["reflexive_bindings"]
        conflicts = kwargs["integration_conflicts"]

        source_availability = _clamp(len(sources) / 4.0)
        source_diversity = _clamp(len({s.get("source_type") for s in sources}) / 3.0)
        trajectory_binding_score = 1.0 if any(s.get("source_type") == "trajectory_memory" for s in sources) else 0.0
        cross_source_integration = self._mean([_clamp(x.get("integration_coupling", 0.0)) for x in matrix]) if matrix else source_availability
        coherence_score = self._mean([_clamp(v) for k, v in coherence.items() if isinstance(v, (int, float))])
        consolidation_score = self._mean([_clamp(c.get("channel_strength", 0.0)) for c in channels])
        continuity_score = self._mean([_clamp(b.get("binding_strength", 0.0)) for b in continuity])
        identity_score = self._mean([_clamp(b.get("binding_strength", 0.0)) for b in identity])
        reflexive_score = self._mean([_clamp(b.get("binding_strength", 0.0)) for b in reflexive])
        conflict_penalty = self._mean([_clamp(c.get("severity", 0.0)) for c in conflicts]) if conflicts else 0.0
        memory_integration_score = _clamp(self._mean([
            source_availability,
            source_diversity,
            trajectory_binding_score,
            cross_source_integration,
            coherence_score,
            consolidation_score,
            continuity_score,
            identity_score,
            reflexive_score,
        ]) * (1.0 - 0.35 * conflict_penalty))
        return {
            "source_availability": source_availability,
            "source_diversity": source_diversity,
            "trajectory_binding_score": trajectory_binding_score,
            "cross_source_integration": cross_source_integration,
            "coherence_score": coherence_score,
            "consolidation_score": consolidation_score,
            "continuity_binding_score": continuity_score,
            "identity_binding_score": identity_score,
            "reflexive_binding_score": reflexive_score,
            "conflict_penalty": conflict_penalty,
            "memory_integration_score": memory_integration_score,
        }

    def _score_mapping(self, mapping: dict[str, Any], default: float = 0.5) -> float:
        values: list[float] = []
        def walk(x: Any) -> None:
            if isinstance(x, bool):
                values.append(1.0 if x else 0.0)
            elif isinstance(x, (int, float)):
                key_score = _clamp(x)
                values.append(key_score)
            elif isinstance(x, dict):
                for v in x.values():
                    walk(v)
            elif isinstance(x, (list, tuple)):
                if x:
                    values.append(_clamp(len(x) / 10.0))
                for v in list(x)[:5]:
                    walk(v)
        walk(mapping)
        if not values:
            return default
        # avoid counts dominating by taking capped mean
        return self._mean(values[:100])

    def _categories_from_text(self, payload: Any) -> list[str]:
        text = json.dumps(payload, ensure_ascii=False, default=str).lower()[:50000]
        categories = []
        terms = {
            "memory": ["memory", "archive", "history", "trajectory"],
            "identity": ["identity", "self_model", "selfhood", "lineage"],
            "continuity": ["continuity", "persistent", "transmission", "temporal"],
            "reflexivity": ["reflexive", "meta", "introspective", "revision"],
            "validation": ["validation", "certification", "error_count", "success"],
            "runtime": ["runtime", "cycle", "experiment", "dashboard"],
        }
        for cat, needles in terms.items():
            if any(n in text for n in needles):
                categories.append(cat)
        return categories or ["memory"]

    def _presence_score(self, sources: list[dict[str, Any]], categories: list[str]) -> float:
        present = set()
        for s in sources:
            present.update(s.get("categories", []))
        if not categories:
            return 0.0
        return _clamp(len(present & set(categories)) / len(categories))

    def _mean(self, values: list[float]) -> float:
        return _clamp(sum(values) / len(values)) if values else 0.0

    def _planned_paths(self) -> dict[str, str]:
        return {
            "json": str(OUTPUT_DIR / "latest_memory_integration_analyzer.json"),
            "markdown": str(OUTPUT_DIR / "latest_memory_integration_analyzer.md"),
            "prometheus": str(OUTPUT_DIR / "latest_memory_integration_analyzer.prom"),
        }

    def _persist(self, result: dict[str, Any]) -> dict[str, str]:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        paths = self._planned_paths()
        Path(paths["json"]).write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str), encoding="utf-8")
        Path(paths["markdown"]).write_text(self._to_markdown(result), encoding="utf-8")
        Path(paths["prometheus"]).write_text(self._to_prometheus(result), encoding="utf-8")
        hist = OUTPUT_DIR / "memory_integration_analyzer_history.jsonl"
        with hist.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"timestamp_utc": result["timestamp_utc"], "status": result["memory_integration_analyzer_status"], "score": result["memory_integration_score"]}, ensure_ascii=False, sort_keys=True) + "\n")
        return paths

    def _to_markdown(self, r: dict[str, Any]) -> str:
        m = r["integration_metrics"]
        lines = [
            "# AD2 — Memory Integration Analyzer",
            "",
            f"Status: {r['memory_integration_analyzer_status']}",
            f"Memory integration analyzed: {r['memory_integration_analyzed']}",
            f"Memory integration score: {r['memory_integration_score']:.6f}",
            "",
            "## Memory sources",
            f"Memory source count: {r['memory_source_count']}",
            "",
            "## Integration metrics",
        ]
        for k, v in m.items():
            lines.append(f"- {k}: {v:.6f}")
        lines += [
            "",
            "## Integration structures",
            f"- integration_links: {len(r['integration_links'])}",
            f"- integration_matrix_pairs: {len(r['integration_matrix'])}",
            f"- continuity_bindings: {len(r['continuity_bindings'])}",
            f"- identity_bindings: {len(r['identity_bindings'])}",
            f"- reflexive_bindings: {len(r['reflexive_bindings'])}",
            "",
            "## Epistemic guard",
            "Functional conclusion only. No consciousness, subjectivity, qualia, or phenomenology is asserted.",
        ]
        return "\n".join(lines) + "\n"

    def _to_prometheus(self, r: dict[str, Any]) -> str:
        lines = [
            "# HELP memory_integration_analyzed Functional AD2 integration flag",
            "# TYPE memory_integration_analyzed gauge",
            f"memory_integration_analyzed {1 if r['memory_integration_analyzed'] else 0}",
            "# HELP memory_integration_score Functional AD2 memory integration score",
            "# TYPE memory_integration_score gauge",
            f"memory_integration_score {r['memory_integration_score']:.6f}",
            "# TYPE memory_integration_source_count gauge",
            f"memory_integration_source_count {r['memory_source_count']}",
            "# TYPE memory_integration_link_count gauge",
            f"memory_integration_link_count {len(r['integration_links'])}",
        ]
        for k, v in r["integration_metrics"].items():
            metric = "memory_integration_" + re.sub(r"[^a-zA-Z0-9_:]", "_", k)
            lines.append(f"# TYPE {metric} gauge")
            lines.append(f"{metric} {float(v):.6f}")
        return "\n".join(lines) + "\n"
