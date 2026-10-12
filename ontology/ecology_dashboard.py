"""AW10 — RF ecology dashboard.

Aggregates already-computed AW0→AW9 functional outputs into deterministic
JSON, Markdown and standalone HTML exports. No upstream module is executed.
"""
from __future__ import annotations

import hashlib
import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

ROOT = Path.home() / "open-cognitive-ecology"


class EcologyDashboard:
    primitive = "ECOLOGY_DASHBOARD"
    step_id = "AW10"
    public_schema_version = "1.0"

    MODULES = (
        "ecology_blueprint",
        "multi_rf_registry",
        "interaction_graph",
        "shared_reference_frame_detection",
        "coalition_detection",
        "conflict_detection",
        "reference_frame_merging",
        "reference_frame_fragmentation",
        "civilizational_memory",
        "collective_rf_analysis",
    )

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else ROOT
        self.output_dir = self.root / "rf_ecology" / "AW10_ecology_dashboard"

    def _mapping(self, value: Any) -> Dict[str, Any]:
        return dict(value) if isinstance(value, Mapping) else {}

    def _list(self, value: Any) -> List[Any]:
        return list(value) if isinstance(value, list) else []

    def _stable_hash(self, value: Any) -> str:
        raw = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            default=repr,
        )
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _utc(self) -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def _extract(
        self,
        inputs: Mapping[str, Any],
        name: str,
        aliases: List[str],
    ) -> Dict[str, Any]:
        upstream = inputs.get("upstream_results")
        containers = [inputs]
        if isinstance(upstream, Mapping):
            containers.append(upstream)
        for container in containers:
            for key in [name] + aliases:
                value = container.get(key)
                if isinstance(value, Mapping):
                    return dict(value)
        return {}

    def _pipeline(self, inputs: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
        aliases = {
            "ecology_blueprint": ["aw0_result", "AW0"],
            "multi_rf_registry": ["rf_registry", "aw1_result", "AW1"],
            "interaction_graph": ["aw2_result", "AW2"],
            "shared_reference_frame_detection": [
                "shared_reference_frame_detector", "aw3_result", "AW3"
            ],
            "coalition_detection": ["coalition_detector", "aw4_result", "AW4"],
            "conflict_detection": ["conflict_detector", "aw5_result", "AW5"],
            "reference_frame_merging": ["aw6_result", "AW6"],
            "reference_frame_fragmentation": ["aw7_result", "AW7"],
            "civilizational_memory": [
                "civilizational_memory_engine", "aw8_result", "AW8"
            ],
            "collective_rf_analysis": [
                "collective_consciousness_analyzer", "aw9_result", "AW9"
            ],
        }
        return {
            name: self._extract(inputs, name, aliases[name])
            for name in self.MODULES
        }

    def _count(self, payload: Mapping[str, Any], *keys: str) -> int:
        for key in keys:
            value = payload.get(key)
            if isinstance(value, list):
                return len(value)
            try:
                if value is not None:
                    return max(0, int(value))
            except (TypeError, ValueError):
                pass
        return 0

    def _guards(self, pipeline: Mapping[str, Mapping[str, Any]]) -> Dict[str, Any]:
        violations = []
        proof_keys = (
            "consciousness_proven",
            "collective_consciousness_proven",
            "qualia_proven",
            "collective_qualia_proven",
            "subjectivity_proven",
            "collective_subjectivity_proven",
            "phenomenology_proven",
            "collective_phenomenology_proven",
        )
        for module_name, payload in pipeline.items():
            for key in proof_keys:
                if payload.get(key) is True:
                    violations.append(f"{module_name}.{key}")
        return {
            "guard_status": "GUARDS_PRESERVED" if not violations else "GUARD_VIOLATION",
            "violations": sorted(violations),
            "collective_consciousness_proven": False,
            "collective_subjectivity_proven": False,
            "collective_qualia_proven": False,
            "collective_phenomenology_proven": False,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
        }

    def _core(self, inputs: Mapping[str, Any]) -> Dict[str, Any]:
        pipeline = self._pipeline(inputs)
        registry = pipeline["multi_rf_registry"]
        graph = pipeline["interaction_graph"]
        shared = pipeline["shared_reference_frame_detection"]
        coalitions = pipeline["coalition_detection"]
        conflicts = pipeline["conflict_detection"]
        merging = pipeline["reference_frame_merging"]
        fragmentation = pipeline["reference_frame_fragmentation"]
        memory = pipeline["civilizational_memory"]
        collective = pipeline["collective_rf_analysis"]
        guards = self._guards(pipeline)

        population = self._count(
            registry,
            "rf_count",
            "registry_count",
            "record_count",
            "registry",
            "rf_records",
        )
        interactions = self._count(graph, "edge_count", "edges", "interactions")
        shared_count = self._count(
            shared,
            "detected_pair_count",
            "shared_reference_frame_count",
            "shared_reference_frames",
            "detections",
        )
        coalition_count = self._count(coalitions, "coalition_count", "coalitions")
        conflict_count = self._count(conflicts, "conflict_count", "conflicts")
        merge_count = self._count(merging, "merge_count", "merges")
        fragmentation_count = self._count(
            fragmentation, "fragmentation_count", "fragmentations"
        )

        presence = {name: bool(payload) for name, payload in pipeline.items()}
        required = [name for name in self.MODULES if name != "ecology_blueprint"]
        completeness = round(
            sum(1 for name in required if presence[name]) / len(required), 6
        )
        collective_ready = bool(collective.get("collective_rf_analysis_ready", False))
        memory_ready = bool(memory.get("civilizational_memory_ready", False))
        ready = bool(
            completeness == 1.0
            and population >= 2
            and collective_ready
            and memory_ready
            and guards["guard_status"] == "GUARDS_PRESERVED"
        )

        core: Dict[str, Any] = {
            "primitive": self.primitive,
            "step": self.step_id,
            "public_schema_version": self.public_schema_version,
            "dashboard_status": (
                "RF_ECOLOGY_DASHBOARD_READY"
                if ready else "RF_ECOLOGY_DASHBOARD_INCOMPLETE"
            ),
            "rf_ecology_dashboard_ready": ready,
            "module_presence": presence,
            "module_completeness": completeness,
            "population_rf": {
                "population_size": population,
                "member_rf_ids": sorted(
                    str(value)
                    for value in self._list(collective.get("member_rf_ids"))
                ),
            },
            "interaction_summary": {
                "edge_count": interactions,
                "interaction_density": collective.get(
                    "distributed_coordination_structure", {}
                ).get("interaction_density", graph.get("density", 0.0)),
                "distributed_coordination_score": collective.get(
                    "distributed_coordination_score", 0.0
                ),
                "centralization_risk_score": collective.get(
                    "centralization_risk_score", 0.0
                ),
                "local_autonomy_score": collective.get(
                    "local_autonomy_score", 0.0
                ),
            },
            "shared_reference_frame_summary": {
                "detected_count": shared_count,
                "score": collective.get("shared_reference_frame_score", 0.0),
            },
            "coalition_summary": {
                "detected_count": coalition_count,
                "coherence_score": collective.get("coalition_coherence_score", 0.0),
            },
            "conflict_summary": {
                "detected_count": conflict_count,
                "pressure_score": collective.get("conflict_pressure_score", 0.0),
            },
            "merge_summary": {
                "detected_count": merge_count,
                "activity_score": collective.get("merge_activity_score", 0.0),
            },
            "fragmentation_summary": {
                "detected_count": fragmentation_count,
                "pressure_score": collective.get("fragmentation_pressure_score", 0.0),
            },
            "civilizational_memory_summary": {
                "ready": memory_ready,
                "record_count": memory.get("memory_record_count", 0),
                "availability_score": memory.get("availability_score", 0.0),
                "loss_tolerance_score": memory.get("loss_tolerance_score", 0.0),
                "lineage_preservation_score": memory.get(
                    "lineage_preservation_score", 0.0
                ),
                "future_openness_preservation_score": memory.get(
                    "future_openness_preservation_score", 0.0
                ),
            },
            "collective_coordination_summary": {
                "analysis_ready": collective_ready,
                "functional_collective_integration": collective.get(
                    "functional_collective_integration", 0.0
                ),
                "false_positive_blockers": sorted(
                    str(value)
                    for value in self._list(
                        collective.get("false_positive_blockers")
                    )
                ),
            },
            "epistemic_limits": guards,
            "audit_trace": {
                "aggregation_only": True,
                "upstream_recalculation_performed": False,
                "source_hashes": {
                    "registry_hash": registry.get("registry_hash"),
                    "graph_hash": graph.get("graph_hash"),
                    "shared_rf_hash": shared.get("detection_hash"),
                    "coalition_hash": coalitions.get("detection_hash"),
                    "conflict_hash": conflicts.get("detection_hash"),
                    "merge_hash": merging.get("result_hash"),
                    "fragmentation_hash": fragmentation.get("result_hash"),
                    "memory_hash": memory.get("memory_hash"),
                    "collective_analysis_hash": collective.get("analysis_hash"),
                },
            },
        }
        core["dashboard_hash"] = self._stable_hash(core)
        return core

    def _json_export(self, core: Mapping[str, Any]) -> str:
        return json.dumps(
            dict(core), indent=2, sort_keys=True, ensure_ascii=False, default=repr
        )

    def _markdown_export(self, core: Mapping[str, Any]) -> str:
        sections = [
            ("Population RF", core["population_rf"]),
            ("Interactions", core["interaction_summary"]),
            ("RF partagés", core["shared_reference_frame_summary"]),
            ("Coalitions", core["coalition_summary"]),
            ("Conflits", core["conflict_summary"]),
            ("Fusions", core["merge_summary"]),
            ("Fragmentations", core["fragmentation_summary"]),
            ("Mémoire civilisationnelle", core["civilizational_memory_summary"]),
            ("Coordination collective", core["collective_coordination_summary"]),
        ]
        lines = [
            "# AW10 RF Ecology Dashboard",
            "",
            "Functional RF ecology instrumentation only. No collective consciousness, "
            "subjectivity, qualia or phenomenology proof is asserted.",
            "",
            f"- Dashboard status: {core['dashboard_status']}",
            f"- Module completeness: {core['module_completeness']}",
            "",
        ]
        for title, payload in sections:
            lines.extend([f"## {title}", "", "| Metric | Value |", "|---|---|"])
            for key, value in sorted(payload.items()):
                rendered = json.dumps(value, ensure_ascii=False, sort_keys=True)
                lines.append(f"| {key} | {rendered.replace('|', chr(92) + '|')} |")
            lines.append("")
        lines.extend([
            "## Epistemic limits",
            "",
            "- Functional conclusion only: True",
            "- Phenomenology undetermined: True",
            "- Collective consciousness proven: False",
            "- Collective subjectivity proven: False",
            "- Collective qualia proven: False",
            "- Collective phenomenology proven: False",
            "",
            f"Dashboard hash: `{core['dashboard_hash']}`",
            "",
        ])
        return "\n".join(lines)

    def _html_export(self, core: Mapping[str, Any]) -> str:
        def esc(value: Any) -> str:
            return html.escape(str(value), quote=True)

        cards = []
        for title, payload in (
            ("Population RF", core["population_rf"]),
            ("Interactions", core["interaction_summary"]),
            ("RF partagés", core["shared_reference_frame_summary"]),
            ("Coalitions", core["coalition_summary"]),
            ("Conflits", core["conflict_summary"]),
            ("Fusions", core["merge_summary"]),
            ("Fragmentations", core["fragmentation_summary"]),
            ("Mémoire civilisationnelle", core["civilizational_memory_summary"]),
            ("Coordination collective", core["collective_coordination_summary"]),
        ):
            rows = "".join(
                "<tr><td>%s</td><td>%s</td></tr>" % (
                    esc(key), esc(json.dumps(value, ensure_ascii=False, sort_keys=True))
                )
                for key, value in sorted(payload.items())
            )
            cards.append(
                "<section class='card'><h2>%s</h2><table>"
                "<tr><th>Metric</th><th>Value</th></tr>%s</table></section>"
                % (esc(title), rows)
            )
        return """<!doctype html>
<html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AW10 RF Ecology Dashboard</title>
<style>
body{font-family:Arial,Helvetica,sans-serif;margin:0;background:#f4f6f8;color:#1d2733}
main{max-width:1100px;margin:auto;padding:28px}.card{background:#fff;border:1px solid #d8dee6;border-radius:10px;padding:16px;margin:14px 0}
table{border-collapse:collapse;width:100%%}th,td{border:1px solid #d8dee6;padding:8px;text-align:left}th{background:#eef2f6}.guard{background:#fff4cc;border:1px solid #d8b84e;padding:14px;border-radius:8px}
</style></head><body><main>
<h1>AW10 RF Ecology Dashboard</h1>
<div class="guard">Functional RF ecology instrumentation only. No collective consciousness, subjectivity, qualia or phenomenology proof is asserted.</div>
<section class="card"><h2>Summary</h2><p>Status: <strong>%s</strong></p><p>Module completeness: %s</p></section>
%s
<section class="card"><h2>Epistemic limits</h2><p>Functional conclusion only: True</p><p>Phenomenology undetermined: True</p><p>Collective consciousness proven: False</p><p>Collective subjectivity proven: False</p><p>Collective qualia proven: False</p><p>Collective phenomenology proven: False</p></section>
<p>Dashboard hash: <code>%s</code></p>
</main></body></html>""" % (
            esc(core["dashboard_status"]),
            esc(core["module_completeness"]),
            "".join(cards),
            esc(core["dashboard_hash"]),
        )

    def step(
        self,
        inputs: Optional[Dict[str, Any]] = None,
        persist: bool = False,
    ) -> Dict[str, Any]:
        safe_inputs = dict(inputs or {})
        core = self._core(safe_inputs)
        exports = {
            "json": self._json_export(core),
            "markdown": self._markdown_export(core),
            "html": self._html_export(core),
        }
        export_integrity = {
            f"{name}_hash": hashlib.sha256(content.encode("utf-8")).hexdigest()
            for name, content in exports.items()
        }
        result = dict(core)
        result.update({
            "timestamp_utc": self._utc(),
            "exports": exports,
            "export_integrity": export_integrity,
            "persist_requested": bool(persist),
            "persisted": False,
            "json_path": None,
            "markdown_path": None,
            "html_path": None,
            "collective_consciousness_proven": False,
            "collective_subjectivity_proven": False,
            "collective_qualia_proven": False,
            "collective_phenomenology_proven": False,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
        })
        if persist:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            paths = {
                "json_path": self.output_dir / "latest_ecology_dashboard.json",
                "markdown_path": self.output_dir / "latest_ecology_dashboard.md",
                "html_path": self.output_dir / "latest_ecology_dashboard.html",
            }
            for key, path in paths.items():
                export_name = key.replace("_path", "")
                temporary = path.with_suffix(path.suffix + ".tmp")
                temporary.write_text(exports[export_name], encoding="utf-8")
                temporary.replace(path)
                result[key] = str(path)
            result["persisted"] = True
        return result


def step(
    inputs: Optional[Dict[str, Any]] = None,
    persist: bool = False,
) -> Dict[str, Any]:
    return EcologyDashboard().step(inputs=inputs, persist=persist)
