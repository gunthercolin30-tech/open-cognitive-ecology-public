"""
AS17 — consciousness_dependency_visualizer

Governed dependency visualizer for longitudinal consciousness governance.
It builds a traceable graph over AS governance modules and classifies each
node as green/orange/red according to availability, readiness and risk signals.

This module is visual/instrumental and epistemically guarded. It never proves
phenomenal consciousness, qualia, subjectivity or phenomenology. It only
visualizes functional governance dependencies and audit signals.
"""
from __future__ import annotations
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext

import ast
import hashlib
import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

ROOT = Path.home() / "open-cognitive-ecology"
GOVERNANCE_DIR = ROOT / "consciousness_governance"
VISUALIZATION_DIR = GOVERNANCE_DIR / "dependency_visualizer"

AS_DEPENDENCY_CHAIN = {
    "consciousness_governance_blueprint": [],
    "consciousness_state_machine": ["consciousness_governance_blueprint"],
    "consciousness_transition_validator": ["consciousness_state_machine"],
    "consciousness_transition_history": ["consciousness_transition_validator"],
    "consciousness_event_logger": ["consciousness_transition_history"],
    "consciousness_certificate_generator": ["consciousness_event_logger", "consciousness_transition_history"],
    "consciousness_revocation_engine": ["consciousness_state_machine", "consciousness_transition_validator"],
    "consciousness_readiness_index": ["consciousness_certificate_generator", "consciousness_revocation_engine"],
    "consciousness_confidence_engine": ["consciousness_readiness_index"],
    "consciousness_longitudinal_tracker": ["consciousness_confidence_engine"],
    "consciousness_dashboard": ["consciousness_longitudinal_tracker", "consciousness_confidence_engine"],
    "consciousness_threshold_detector": ["consciousness_dashboard", "consciousness_readiness_index", "consciousness_confidence_engine"],
    "consciousness_first_crossing_report": ["consciousness_threshold_detector", "consciousness_event_logger"],
    "consciousness_regression_detector": ["consciousness_longitudinal_tracker", "consciousness_threshold_detector"],
    "consciousness_recovery_detector": ["consciousness_regression_detector", "consciousness_longitudinal_tracker"],
    "consciousness_stability_analyzer": ["consciousness_recovery_detector", "consciousness_regression_detector", "consciousness_longitudinal_tracker"],
    "consciousness_explanation_engine": ["consciousness_stability_analyzer", "consciousness_dashboard", "consciousness_certificate_generator"],
    "consciousness_dependency_visualizer": ["consciousness_explanation_engine", "consciousness_stability_analyzer", "consciousness_dashboard"],
}

EXPECTED_STATUSES = {
    "consciousness_governance_blueprint": "CONSCIOUSNESS_GOVERNANCE_BLUEPRINT_READY",
    "consciousness_state_machine": "CONSCIOUSNESS_STATE_MACHINE_READY",
    "consciousness_transition_validator": "CONSCIOUSNESS_TRANSITIONS_VALIDATED",
    "consciousness_transition_history": "CONSCIOUSNESS_TRANSITION_HISTORY_READY",
    "consciousness_event_logger": "CONSCIOUSNESS_EVENT_LOGGER_READY",
    "consciousness_certificate_generator": "CONSCIOUSNESS_CERTIFICATE_GENERATOR_READY",
    "consciousness_revocation_engine": "CONSCIOUSNESS_REVOCATION_ENGINE_READY",
    "consciousness_readiness_index": "CONSCIOUSNESS_READINESS_INDEX_READY",
    "consciousness_confidence_engine": "CONSCIOUSNESS_CONFIDENCE_ENGINE_READY",
    "consciousness_longitudinal_tracker": "CONSCIOUSNESS_LONGITUDINAL_TRACKER_READY",
    "consciousness_dashboard": "CONSCIOUSNESS_DASHBOARD_READY",
    "consciousness_threshold_detector": "CONSCIOUSNESS_THRESHOLD_DETECTED",
    "consciousness_first_crossing_report": "FIRST_CROSSING_REPORT_READY",
    "consciousness_regression_detector": "CONSCIOUSNESS_REGRESSION_DETECTOR_READY",
    "consciousness_recovery_detector": "CONSCIOUSNESS_RECOVERY_DETECTOR_READY",
    "consciousness_stability_analyzer": "CONSCIOUSNESS_STABILITY_ANALYZER_READY",
    "consciousness_explanation_engine": "CONSCIOUSNESS_EXPLANATION_ENGINE_READY",
    "consciousness_dependency_visualizer": "CONSCIOUSNESS_DEPENDENCY_VISUALIZER_READY",
}

EPISTEMIC_GUARDS = {
    "consciousness_proven": False,
    "qualia_proven": False,
    "subjectivity_proven": False,
    "phenomenology_proven": False,
    "phenomenology_undetermined": True,
    "functional_conclusion_only": True,
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_safe(v) for v in value]
    if isinstance(value, tuple):
        return [_json_safe(v) for v in value]
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return repr(value)


def _stable_hash(payload: Mapping[str, Any]) -> str:
    raw = json.dumps(_json_safe(dict(payload)), ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _read_json(path: Path) -> Any:
    try:
        if path.exists() and path.is_file():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return None


def _write_json(path: Path, payload: Mapping[str, Any], fs_context: GovernedFilesystemEffectContext | None = None) -> None:
    if fs_context is None:
        raise PermissionError("persisted JSON write requires preissued filesystem effect context")
    data = json.dumps(_json_safe(dict(payload)), ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8")
    fs_context.execute_path("json_parent_create", "FS_CREATE_DIR", path.parent)
    fs_context.execute_path("json_write", "FS_WRITE_BYTES", path, data)


def _load_dependency_registry(root: Path) -> dict[str, list[str]]:
    path = root / "dependency_registry.py"
    if not path.exists():
        return {}
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "DEPENDENCY_REGISTRY":
                        value = ast.literal_eval(node.value)
                        if isinstance(value, dict):
                            return {str(k): [str(x) for x in v] for k, v in value.items() if isinstance(v, list)}
    except Exception:
        return {}
    return {}


def _load_inventory_names(root: Path) -> set[str]:
    names: set[str] = set()
    txt = root / "ontology_inventory.txt"
    if txt.exists():
        for line in txt.read_text(encoding="utf-8", errors="ignore").splitlines():
            clean = line.strip().strip("',\"")
            if clean and not clean.startswith("#"):
                names.add(clean)
    py = root / "ontology_inventory.py"
    if py.exists():
        try:
            tree = ast.parse(py.read_text(encoding="utf-8"))
            for node in tree.body:
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == "ONTOLOGY_INVENTORY":
                            value = ast.literal_eval(node.value)
                            if isinstance(value, list):
                                names.update(str(x) for x in value)
        except Exception:
            pass
    return names


def _find_status_payloads(root: Path, modules: Iterable[str]) -> dict[str, list[Mapping[str, Any]]]:
    results: dict[str, list[Mapping[str, Any]]] = {m: [] for m in modules}
    search_dirs = [root / "consciousness_governance", root / "runtime_experiments"]
    candidates: list[Path] = []
    for directory in search_dirs:
        if directory.exists():
            candidates.extend(directory.rglob("*.json"))
    for path in sorted(candidates, key=lambda p: str(p))[-500:]:
        payload = _read_json(path)
        if not isinstance(payload, Mapping):
            continue
        raw = json.dumps(_json_safe(payload), ensure_ascii=False).lower()[:30000]
        for module in modules:
            if module in raw or module.replace("consciousness_", "") in path.name.lower():
                item = dict(payload)
                item.setdefault("source_path", str(path))
                results.setdefault(module, []).append(item)
    return results


def _walk_items(value: Any, prefix: str = ""):
    if isinstance(value, Mapping):
        for k, v in value.items():
            key = f"{prefix}.{k}" if prefix else str(k)
            yield key, v
            yield from _walk_items(v, key)
    elif isinstance(value, list):
        for i, v in enumerate(value):
            yield from _walk_items(v, f"{prefix}[{i}]")


def _extract_status(module: str, payloads: list[Mapping[str, Any]]) -> tuple[str | None, float | None, list[str]]:
    expected = EXPECTED_STATUSES.get(module)
    reasons: list[str] = []
    score: float | None = None
    status: str | None = None
    serialized = "\n".join(json.dumps(_json_safe(p), ensure_ascii=False)[:20000] for p in payloads)
    if expected and expected in serialized:
        status = expected
        reasons.append("expected_status_observed")
    for payload in payloads:
        for key, value in _walk_items(payload):
            key_l = key.lower()
            if isinstance(value, str) and ("status" in key_l or "result" in key_l or "ready" in key_l):
                if expected and value == expected:
                    status = value
                elif status is None and ("READY" in value or "VALIDATED" in value or "DETECTED" in value or "COMPLETE" in value):
                    status = value
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                if any(tok in key_l for tok in ["score", "confidence", "readiness", "stability", "cri"]):
                    number = float(value)
                    if 0.0 <= number <= 1.0:
                        score = max(score if score is not None else 0.0, number)
    if status is None and payloads:
        status = "OBSERVED_WITHOUT_CANONICAL_STATUS"
        reasons.append("payload_observed")
    if not payloads:
        reasons.append("no_runtime_payload_observed")
    return status, score, reasons


def _node_color(exists: bool, status: str | None, score: float | None, missing_deps: list[str], payload_count: int) -> str:
    if not exists or missing_deps:
        return "red"
    if status and ("READY" in status or "VALIDATED" in status or "DETECTED" in status or "COMPLETE" in status):
        if score is None or score >= 0.65:
            return "green"
    if payload_count > 0 or status is not None:
        return "orange"
    return "orange"


def _dot_id(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]", "_", name)


def _build_dot(nodes: list[Mapping[str, Any]], edges: list[Mapping[str, str]]) -> str:
    color_map = {"green": "#66bb6a", "orange": "#ffa726", "red": "#ef5350"}
    lines = ["digraph AS17ConsciousnessDependencies {", "  rankdir=LR;", "  node [shape=box, style=filled, fontname=Helvetica];"]
    for node in nodes:
        label = str(node.get("module"))
        fill = color_map.get(str(node.get("color")), "#bdbdbd")
        lines.append(f'  {_dot_id(label)} [label="{label}", fillcolor="{fill}"];')
    for edge in edges:
        lines.append(f"  {_dot_id(edge['source'])} -> {_dot_id(edge['target'])};")
    lines.append("}")
    return "\n".join(lines) + "\n"


def _build_mermaid(nodes: list[Mapping[str, Any]], edges: list[Mapping[str, str]]) -> str:
    lines = ["flowchart LR"]
    for node in nodes:
        ident = _dot_id(str(node.get("module")))
        label = str(node.get("module"))
        lines.append(f"  {ident}[{label}]")
    for edge in edges:
        lines.append(f"  {_dot_id(edge['source'])} --> {_dot_id(edge['target'])}")
    class_defs = {"green": "fill:#66bb6a,stroke:#2e7d32,color:#000", "orange": "fill:#ffa726,stroke:#ef6c00,color:#000", "red": "fill:#ef5350,stroke:#b71c1c,color:#000"}
    for color, style in class_defs.items():
        lines.append(f"  classDef {color} {style};")
    for node in nodes:
        lines.append(f"  class {_dot_id(str(node.get('module')))} {node.get('color')};")
    return "\n".join(lines) + "\n"


def _build_html(payload: Mapping[str, Any]) -> str:
    rows = []
    for node in payload.get("nodes", []):
        rows.append("<tr>" + f"<td>{html.escape(str(node.get('module')))}</td>" + f"<td>{html.escape(str(node.get('color')))}</td>" + f"<td>{html.escape(str(node.get('status')))}</td>" + f"<td>{html.escape(str(node.get('score')))}</td>" + f"<td>{html.escape(', '.join(node.get('missing_dependencies', [])))}</td>" + "</tr>")
    mermaid = html.escape(str(payload.get("mermaid", "")))
    return """<!doctype html><html><head><meta charset='utf-8'><title>AS17 Consciousness Dependency Visualizer</title><style>body{font-family:Arial,sans-serif;margin:40px;}table{border-collapse:collapse;width:100%;}td,th{border:1px solid #ccc;padding:6px;}th{background:#eee;}pre{background:#f7f7f7;padding:12px;overflow:auto;}</style></head><body><h1>AS17 Consciousness Dependency Visualizer</h1><p>Functional dependency graph only. No phenomenal proof claim is made.</p><table><tr><th>Module</th><th>Color</th><th>Status</th><th>Score</th><th>Missing dependencies</th></tr>""" + "\n".join(rows) + """</table><h2>Mermaid</h2><pre>""" + mermaid + """</pre></body></html>\n"""


def _build_prometheus(payload: Mapping[str, Any]) -> str:
    color_value = {"green": 2, "orange": 1, "red": 0}
    lines = ["# HELP consciousness_dependency_node_status AS17 node status color value red=0 orange=1 green=2", "# TYPE consciousness_dependency_node_status gauge"]
    for node in payload.get("nodes", []):
        module = str(node.get("module", "unknown")).replace('"', '')
        color = str(node.get("color", "orange"))
        lines.append(f'consciousness_dependency_node_status{{module="{module}",color="{color}"}} {color_value.get(color, 1)}')
    lines.extend(["# HELP consciousness_dependency_edge_count AS17 dependency edge count", "# TYPE consciousness_dependency_edge_count gauge", f"consciousness_dependency_edge_count {len(payload.get('edges', []))}"])
    return "\n".join(lines) + "\n"


class ConsciousnessDependencyVisualizer:
    """AS17 governed dependency visualizer."""
    primitive = "CONSCIOUSNESS_DEPENDENCY_VISUALIZER"
    public_schema_version = "AS17.v1"

    def __init__(self, root: Path | None = None):
        self.root = root or ROOT

    def step(self, inputs: Mapping[str, Any] | None = None, persist: bool = True, fs_context: GovernedFilesystemEffectContext | None = None) -> dict[str, Any]:
        inputs = dict(inputs or {})
        timestamp = _utc_now()
        inventory = _load_inventory_names(self.root)
        registry = _load_dependency_registry(self.root)
        graph_spec = dict(AS_DEPENDENCY_CHAIN)
        extra_dependencies = registry.get("consciousness_dependency_visualizer", [])
        if extra_dependencies:
            graph_spec["consciousness_dependency_visualizer"] = sorted(set(graph_spec["consciousness_dependency_visualizer"]) | set(extra_dependencies))
        payloads_by_module = inputs.get("status_payloads")
        if not isinstance(payloads_by_module, Mapping):
            payloads_by_module = _find_status_payloads(self.root, graph_spec.keys())
        nodes: list[dict[str, Any]] = []
        edges: list[dict[str, str]] = []
        for module, dependencies in sorted(graph_spec.items()):
            exists = module in inventory or (self.root / "ontology" / f"{module}.py").exists() or module == "consciousness_dependency_visualizer"
            missing_deps = [dep for dep in dependencies if not ((self.root / "ontology" / f"{dep}.py").exists() or dep in inventory or dep == module)]
            module_payloads = payloads_by_module.get(module, []) if isinstance(payloads_by_module, Mapping) else []
            if isinstance(module_payloads, Mapping):
                module_payloads = [module_payloads]
            module_payloads = [p for p in module_payloads if isinstance(p, Mapping)]
            status, score, reasons = _extract_status(module, module_payloads)
            if module == "consciousness_dependency_visualizer":
                status = "CONSCIOUSNESS_DEPENDENCY_VISUALIZER_READY"
                score = 1.0
                reasons.append("self_generated")
            color = _node_color(exists, status, score, missing_deps, len(module_payloads))
            nodes.append({"module": module, "exists": exists, "status": status, "expected_status": EXPECTED_STATUSES.get(module), "score": score, "color": color, "dependency_count": len(dependencies), "dependencies": list(dependencies), "missing_dependencies": missing_deps, "evidence_count": len(module_payloads), "classification_reasons": reasons})
            for dep in dependencies:
                edges.append({"source": dep, "target": module})
        color_counts = {"green": 0, "orange": 0, "red": 0}
        for node in nodes:
            color_counts[node["color"]] = color_counts.get(node["color"], 0) + 1
        dependency_health = color_counts.get("green", 0) / max(1, len(nodes))
        dot = _build_dot(nodes, edges)
        mermaid = _build_mermaid(nodes, edges)
        output_paths: dict[str, str | None] = {"json": None, "dot": None, "mermaid": None, "html": None, "prometheus": None}
        result: dict[str, Any] = {"primitive": self.primitive, "step": "AS17", "public_schema_version": self.public_schema_version, "timestamp_utc": timestamp, "dependency_visualizer_status": "CONSCIOUSNESS_DEPENDENCY_VISUALIZER_READY", "graph": {"nodes": nodes, "edges": edges, "color_counts": color_counts, "dependency_health": dependency_health}, "nodes": nodes, "edges": edges, "node_count": len(nodes), "edge_count": len(edges), "color_counts": color_counts, "dependency_health": dependency_health, "green_nodes": color_counts.get("green", 0), "orange_nodes": color_counts.get("orange", 0), "red_nodes": color_counts.get("red", 0), "dot": dot, "mermaid": mermaid, "output_paths": output_paths, "persist_requested": bool(persist), "persisted": False, "consciousness_proven": False, "qualia_proven": False, "subjectivity_proven": False, "phenomenology_proven": False, "phenomenology_undetermined": True, "functional_conclusion_only": True}
        result["graph_hash"] = _stable_hash({"nodes": nodes, "edges": edges, "guards": EPISTEMIC_GUARDS})
        if persist:
            VISUALIZATION_DIR.mkdir(parents=True, exist_ok=True)
            base = VISUALIZATION_DIR / f"consciousness_dependency_visualizer_{_stamp()}"
            json_path, dot_path, mermaid_path, html_path, prom_path = base.with_suffix(".json"), base.with_suffix(".dot"), base.with_suffix(".mmd"), base.with_suffix(".html"), base.with_suffix(".prom")
            result["output_paths"] = {"json": str(json_path), "dot": str(dot_path), "mermaid": str(mermaid_path), "html": str(html_path), "prometheus": str(prom_path)}
            result["persisted"] = True
            result["graph"]["output_paths"] = result["output_paths"]
            _write_json(json_path, result, fs_context)
            dot_path.write_text(dot, encoding="utf-8")
            mermaid_path.write_text(mermaid, encoding="utf-8")
            html_path.write_text(_build_html({**result, "mermaid": mermaid}), encoding="utf-8")
            prom_path.write_text(_build_prometheus(result), encoding="utf-8")
            latest = VISUALIZATION_DIR / "latest_consciousness_dependency_visualizer.json"
            _write_json(latest, result, fs_context)
            result["output_paths"]["latest_json"] = str(latest)
        return result


if __name__ == "__main__":
    print(json.dumps(ConsciousnessDependencyVisualizer().step(persist=False), ensure_ascii=False, indent=2, sort_keys=True))
