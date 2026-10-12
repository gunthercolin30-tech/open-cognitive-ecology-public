\
"""ACEE0 — governed integration audit for Autonomous Cognitive Evolution Engine.

This primitive is observational. It inventories, classifies and histories the
coverage of ACEE0–ACEE20 without mutating or executing evolution engines.
"""
from __future__ import annotations

import ast
import hashlib
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

PRIMITIVE = "ACEE_INTEGRATION_AUDITOR"
DEPENDENCIES = [
    "ontology_redundancy_audit",
    "ontology_gap_detector",
    "autonomous_capability_discovery",
    "theorem_dependency_mapper",
    "metrics_history_recorder",
    "validation_history_archive",
    "epistemic_guard",
    "governance_consistency_checker",
]
STATUS_COMPLETE = "ACEE_INTEGRATION_AUDIT_COMPLETE"
STATUS_DEGRADED = "ACEE_INTEGRATION_AUDIT_DEGRADED"
PUBLIC_SCHEMA_VERSION = "1.0.0"

ACEE_CAPABILITIES: dict[str, tuple[str, ...]] = {
    "ACEE0": ("integration", "audit", "coverage", "redundancy", "dependency"),
    "ACEE1": ("capability", "map", "coverage"),
    "ACEE2": ("meta", "orchestrator", "controlled_evolution_orchestrator"),
    "ACEE3": ("bridge", "adapter", "auto_improvement_runtime_bridge"),
    "ACEE4": ("autonomous", "cycle", "runtime_experiment_manager"),
    "ACEE5": ("code", "generation", "governed", "gate"),
    "ACEE6": ("installation", "executor"),
    "ACEE7": ("validation", "runner"),
    "ACEE8": ("impact", "evaluator", "effectiveness"),
    "ACEE9": ("causal", "effect", "analyzer"),
    "ACEE10": ("selection", "policy"),
    "ACEE11": ("rollback", "recovery", "reversibility"),
    "ACEE12": ("architecture", "genealogy", "genealogical"),
    "ACEE13": ("lineage", "manager"),
    "ACEE14": ("best", "architecture", "archive"),
    "ACEE15": ("autonomous", "scheduler"),
    "ACEE16": ("longitudinal", "tracker", "history"),
    "ACEE17": ("dashboard",),
    "ACEE18": ("prediction", "engine"),
    "ACEE19": ("meta", "analysis"),
    "ACEE20": ("final", "certifier", "certification"),
}

PIVOT_MODULES = (
    "auto_improvement_runtime_bridge",
    "controlled_evolution_orchestrator",
    "recursive_self_improvement_controller",
    "recursive_self_improvement_governor",
    "evolution_sandbox",
    "constitutional_evolution_gate",
    "runtime_experiment_manager",
    "genealogical_evolution_dashboard",
    "scientific_meta_analysis_engine",
)

CATEGORY_MARKERS: dict[str, tuple[str, ...]] = {
    "existing_orchestrators": ("orchestrator", "controller", "governor"),
    "existing_bridges": ("bridge", "adapter"),
    "existing_dashboards": ("dashboard",),
    "existing_validation_engines": ("validation", "validator", "certifier", "test"),
    "existing_governance_modules": ("govern", "constitutional", "approval", "gate"),
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _finite_score(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    if not math.isfinite(number):
        return default
    return max(0.0, min(1.0, number))


def _normalize_names(values: Iterable[Any]) -> list[str]:
    return sorted({str(value).strip() for value in values if str(value).strip()})


def _read_inventory_text(path: Path) -> set[str]:
    if not path.is_file():
        return set()
    try:
        return {line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()}
    except OSError:
        return set()


def _read_inventory_python(path: Path) -> set[str]:
    if not path.is_file():
        return set()
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in tree.body:
            if isinstance(node, ast.Assign):
                if any(isinstance(target, ast.Name) and target.id == "ONTOLOGY_INVENTORY" for target in node.targets):
                    value = ast.literal_eval(node.value)
                    if isinstance(value, (list, tuple, set)):
                        return {str(item) for item in value}
    except (OSError, SyntaxError, ValueError):
        return set()
    return set()


def _read_dependency_registry(path: Path) -> dict[str, list[str]]:
    if not path.is_file():
        return {}
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        registry: dict[str, list[str]] = {}
        for node in tree.body:
            if isinstance(node, ast.Assign) and any(
                isinstance(target, ast.Name) and target.id == "DEPENDENCY_REGISTRY"
                for target in node.targets
            ):
                value = ast.literal_eval(node.value)
                if isinstance(value, dict):
                    registry.update({str(k): [str(x) for x in v] for k, v in value.items() if isinstance(v, (list, tuple))})
            if isinstance(node, ast.Try):
                for child in ast.walk(node):
                    if isinstance(child, ast.Assign) and isinstance(child.value, (ast.List, ast.Tuple)):
                        for target in child.targets:
                            if (
                                isinstance(target, ast.Subscript)
                                and isinstance(target.value, ast.Name)
                                and target.value.id == "DEPENDENCY_REGISTRY"
                            ):
                                try:
                                    key = ast.literal_eval(target.slice)
                                    values = ast.literal_eval(child.value)
                                except Exception:
                                    continue
                                if isinstance(key, str) and isinstance(values, (list, tuple)):
                                    registry[key] = [str(x) for x in values]
        return registry
    except (OSError, SyntaxError, ValueError):
        return {}


def _detect_cycles(graph: Mapping[str, Iterable[str]]) -> list[list[str]]:
    cycles: set[tuple[str, ...]] = set()
    state: dict[str, int] = {}
    stack: list[str] = []

    def visit(node: str) -> None:
        state[node] = 1
        stack.append(node)
        for neighbor in sorted(set(graph.get(node, []))):
            if neighbor not in graph:
                continue
            if state.get(neighbor, 0) == 0:
                visit(neighbor)
            elif state.get(neighbor) == 1 and neighbor in stack:
                start = stack.index(neighbor)
                cycle = stack[start:] + [neighbor]
                body = cycle[:-1]
                if body:
                    rotations = [tuple(body[i:] + body[:i]) for i in range(len(body))]
                    canonical = min(rotations)
                    cycles.add(canonical + (canonical[0],))
        stack.pop()
        state[node] = 2

    for node in sorted(graph):
        if state.get(node, 0) == 0:
            visit(node)
    return [list(cycle) for cycle in sorted(cycles)]


@dataclass
class AceeIntegrationAuditor:
    root: Path | None = None

    def __post_init__(self) -> None:
        self.root = Path(self.root) if self.root is not None else Path.home() / "open-cognitive-ecology"

    def _default_modules(self) -> list[str]:
        sources = set()
        sources |= _read_inventory_text(self.root / "ontology_inventory.txt")
        sources |= _read_inventory_python(self.root / "ontology_inventory.py")
        sources |= _read_inventory_python(self.root / "ontology" / "ontology_inventory.py")
        ontology_dir = self.root / "ontology"
        if ontology_dir.is_dir():
            sources |= {path.stem for path in ontology_dir.glob("*.py") if path.name != "__init__.py"}
        return _normalize_names(sources)

    def _build_context(self, inputs: Mapping[str, Any] | None) -> dict[str, Any]:
        supplied = dict(inputs or {})
        modules = supplied.get("modules") or supplied.get("module_inventory") or self._default_modules()
        dependencies = supplied.get("dependencies")
        if not isinstance(dependencies, Mapping):
            dependencies = _read_dependency_registry(self.root / "dependency_registry.py")
        return {
            "modules": _normalize_names(modules if isinstance(modules, Iterable) and not isinstance(modules, (str, bytes)) else []),
            "dependencies": {
                str(key): _normalize_names(value if isinstance(value, Iterable) and not isinstance(value, (str, bytes)) else [])
                for key, value in dependencies.items()
            },
            "explicit_duplicates": supplied.get("duplicate_candidates", []),
            "timestamp": supplied.get("audit_timestamp_utc"),
        }

    def _coverage(self, modules: list[str]) -> tuple[dict[str, Any], list[str], list[str], list[str]]:
        matrix: dict[str, Any] = {}
        reuse_candidates: set[str] = set()
        refinement_candidates: set[str] = set()
        missing_capabilities: list[str] = []
        lowered = {module: module.lower() for module in modules}

        for acee_id in sorted(ACEE_CAPABILITIES, key=lambda value: int(value[4:])):
            markers = ACEE_CAPABILITIES[acee_id]
            scored: list[tuple[float, str]] = []
            for module, name in lowered.items():
                matches = sum(1 for marker in markers if marker in name)
                score = matches / len(markers)
                if score > 0:
                    scored.append((score, module))
            scored.sort(key=lambda item: (-item[0], item[1]))
            best_score = scored[0][0] if scored else 0.0
            candidates = [module for score, module in scored if score == best_score][:8]
            if acee_id == "ACEE0" and "acee_integration_auditor" in modules:
                best_score = 1.0
                candidates = ["acee_integration_auditor"]
            if best_score >= 0.75:
                coverage = "covered"
                action = "reuse"
                reuse_candidates.update(candidates)
            elif best_score > 0.0:
                coverage = "partial"
                action = "refine_or_integrate"
                refinement_candidates.update(candidates)
            else:
                coverage = "missing"
                action = "create_after_audit"
                missing_capabilities.append(acee_id)
            matrix[acee_id] = {
                "coverage": coverage,
                "coverage_score": round(_finite_score(best_score), 6),
                "candidate_modules": candidates,
                "recommended_action": action,
                "justification": (
                    f"{len(candidates)} candidate module(s) matched {markers}."
                    if candidates else f"No installed module matched capability markers {markers}."
                ),
            }
        return matrix, sorted(reuse_candidates), sorted(refinement_candidates), missing_capabilities

    def _duplicates(self, modules: list[str], explicit: Any) -> list[dict[str, Any]]:
        candidates: dict[tuple[str, str], dict[str, Any]] = {}
        tokenized = {module: set(module.split("_")) for module in modules}
        for index, left in enumerate(modules):
            for right in modules[index + 1:]:
                union = tokenized[left] | tokenized[right]
                if not union:
                    continue
                score = len(tokenized[left] & tokenized[right]) / len(union)
                if score >= 0.8:
                    candidates[(left, right)] = {
                        "module_a": left,
                        "module_b": right,
                        "similarity_score": round(score, 6),
                        "classification": "review_required",
                        "justification": "High normalized token overlap; no automatic deletion or replacement is authorized.",
                    }
        if isinstance(explicit, Iterable) and not isinstance(explicit, (str, bytes, Mapping)):
            for item in explicit:
                if isinstance(item, Mapping):
                    left = str(item.get("module_a", "")).strip()
                    right = str(item.get("module_b", "")).strip()
                    if left and right and left != right:
                        key = tuple(sorted((left, right)))
                        candidates[key] = {
                            "module_a": key[0],
                            "module_b": key[1],
                            "similarity_score": _finite_score(item.get("similarity_score", 1.0)),
                            "classification": "review_required",
                            "justification": str(item.get("justification") or "Explicit duplicate candidate supplied for governed review."),
                        }
        return [candidates[key] for key in sorted(candidates)]

    def _inventory_consistency(self, modules: list[str]) -> dict[str, Any]:
        text = _read_inventory_text(self.root / "ontology_inventory.txt")
        root_py = _read_inventory_python(self.root / "ontology_inventory.py")
        ontology_py = _read_inventory_python(self.root / "ontology" / "ontology_inventory.py")
        available = [inventory for inventory in (text, root_py, ontology_py) if inventory]
        consistent = bool(available) and all(inventory == available[0] for inventory in available[1:])
        return {
            "consistent": consistent,
            "ontology_inventory_txt_count": len(text),
            "root_python_inventory_count": len(root_py),
            "ontology_python_inventory_count": len(ontology_py),
            "observed_module_count": len(modules),
        }

    def _history_paths(self) -> tuple[Path, Path]:
        directory = self.root / "acee_runtime" / "ACEE0_acee_integration_auditor"
        return directory / "latest_integration_audit.json", directory / "integration_audit_history.jsonl"

    def _load_previous(self, history_path: Path) -> dict[str, Any] | None:
        if not history_path.is_file():
            return None
        try:
            lines = [line for line in history_path.read_text(encoding="utf-8").splitlines() if line.strip()]
            return json.loads(lines[-1]) if lines else None
        except (OSError, json.JSONDecodeError):
            return {"history_corrupted": True}

    def step(self, inputs: Mapping[str, Any] | None = None, persist: bool = False) -> dict[str, Any]:
        context = self._build_context(inputs)
        modules = context["modules"]
        dependencies = context["dependencies"]
        coverage_matrix, reuse_candidates, refinement_candidates, missing_capabilities = self._coverage(modules)
        duplicate_candidates = self._duplicates(modules, context["explicit_duplicates"])
        cycles = _detect_cycles(dependencies)
        missing_dependencies = sorted({dependency for values in dependencies.values() for dependency in values if dependency not in modules})
        inventory_consistency = self._inventory_consistency(modules)
        latest_path, history_path = self._history_paths()
        previous = self._load_previous(history_path)
        history_corrupted = bool(previous and previous.get("history_corrupted"))
        previous_hash = "" if not previous or history_corrupted else str(previous.get("audit_hash", ""))
        covered = [key for key, value in coverage_matrix.items() if value["coverage"] == "covered"]
        partial = [key for key, value in coverage_matrix.items() if value["coverage"] == "partial"]
        coverage_score = round(sum(value["coverage_score"] for value in coverage_matrix.values()) / len(coverage_matrix), 6)
        degraded_reasons = []
        if not modules:
            degraded_reasons.append("empty_module_inventory")
        if history_corrupted:
            degraded_reasons.append("history_corrupted")
        if not inventory_consistency["consistent"] and inputs is None:
            degraded_reasons.append("inventory_inconsistency")
        audit_timestamp = str(context["timestamp"] or _utc_now())
        if context["timestamp"] is not None:
            try:
                datetime.fromisoformat(audit_timestamp.replace("Z", "+00:00"))
            except ValueError:
                degraded_reasons.append("invalid_audit_timestamp")
        categories = {
            category: [module for module in modules if any(marker in module.lower() for marker in markers)]
            for category, markers in CATEGORY_MARKERS.items()
        }
        recommended_actions = []
        for key, value in coverage_matrix.items():
            recommended_actions.append({
                "capability": key,
                "action": value["recommended_action"],
                "targets": value["candidate_modules"],
                "justification": value["justification"],
            })
        changes = {
            "previous_audit_available": bool(previous and not history_corrupted),
            "coverage_score_delta": round(coverage_score - _finite_score(previous.get("coverage_score"), coverage_score), 6) if previous and not history_corrupted else 0.0,
            "module_count_delta": len(modules) - int(previous.get("module_count", len(modules))) if previous and not history_corrupted else 0,
        }
        payload = {
            "primitive": PRIMITIVE,
            "public_schema_version": PUBLIC_SCHEMA_VERSION,
            "audit_status": STATUS_DEGRADED if degraded_reasons else STATUS_COMPLETE,
            "audit_completed": not degraded_reasons,
            "audit_timestamp_utc": audit_timestamp,
            "module_count": len(modules),
            "existing_modules": modules,
            "existing_pivot_modules": sorted(set(modules) & set(PIVOT_MODULES)),
            **categories,
            "coverage_matrix": coverage_matrix,
            "coverage_score": coverage_score,
            "covered_capabilities": covered,
            "partially_covered_capabilities": partial,
            "missing_capabilities": missing_capabilities,
            "duplicate_candidates": duplicate_candidates,
            "reuse_candidates": reuse_candidates,
            "refinement_candidates": refinement_candidates,
            "creation_candidates": missing_capabilities,
            "recommended_actions": recommended_actions,
            "recommendation_justifications_complete": all(bool(item["justification"].strip()) for item in recommended_actions),
            "dependency_graph": dependencies,
            "dependency_cycles": cycles,
            "dependency_cycle_count": len(cycles),
            "missing_dependencies": missing_dependencies,
            "missing_dependency_count": len(missing_dependencies),
            "inventory_consistency": inventory_consistency,
            "changes_since_previous_audit": changes,
            "previous_audit_hash": previous_hash,
            "degraded_reasons": degraded_reasons,
            "consciousness_proven": False,
            "subjectivity_proven": False,
            "qualia_proven": False,
            "phenomenology_proven": False,
            "collective_consciousness_proven": False,
            "collective_subjectivity_proven": False,
            "collective_qualia_proven": False,
            "collective_phenomenology_proven": False,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
        }
        payload["integration_hash"] = _sha256({
            "modules": modules,
            "coverage_matrix": coverage_matrix,
            "duplicates": duplicate_candidates,
            "dependencies": dependencies,
        })
        audit_body = dict(payload)
        audit_body.pop("audit_timestamp_utc", None)
        payload["audit_id"] = "ACEE0-" + payload["integration_hash"][:16]
        payload["audit_hash"] = _sha256({"previous_audit_hash": previous_hash, "payload": audit_body})
        payload["persisted"] = False
        payload["output_path"] = str(latest_path)
        payload["history_path"] = str(history_path)
        if persist:
            latest_path.parent.mkdir(parents=True, exist_ok=True)
            stored = dict(payload)
            stored["persisted"] = True
            latest_path.write_text(json.dumps(stored, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
            with history_path.open("a", encoding="utf-8") as handle:
                handle.write(_canonical(stored) + "\n")
            payload = stored
        return payload


if __name__ == "__main__":
    print(json.dumps(AceeIntegrationAuditor().step(inputs={}, persist=False), indent=2, ensure_ascii=False))
