"""Adversarial, non-executing guard for OIF-2G complex manifests."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Mapping, Sequence, Tuple

FORBIDDEN_KEYS = frozenset({
    "__class__", "__dict__", "__import__", "eval", "exec", "callable",
    "entrypoint", "class_path", "javascript", "shell", "command_path",
})
FORBIDDEN_FRAGMENTS = ("file://", "http://", "https://", "../", "$home", "${")

class AdversarialGuardViolation(ValueError):
    pass

@dataclass(frozen=True)
class GuardReport:
    valid: bool
    node_count: int
    max_depth_seen: int
    errors: Tuple[str, ...]


def _walk(value: Any, depth: int, max_depth: int, state: Dict[str, int], errors: list) -> None:
    state["nodes"] += 1
    state["depth"] = max(state["depth"], depth)
    if state["nodes"] > state["max_nodes"]:
        errors.append("node_limit_exceeded")
        return
    if depth > max_depth:
        errors.append("depth_limit_exceeded")
        return
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key).casefold()
            if key_text in FORBIDDEN_KEYS:
                errors.append("forbidden_key:%s" % key_text)
            _walk(child, depth + 1, max_depth, state, errors)
    elif isinstance(value, (list, tuple)):
        for child in value:
            _walk(child, depth + 1, max_depth, state, errors)
    elif isinstance(value, str):
        folded = value.casefold()
        for fragment in FORBIDDEN_FRAGMENTS:
            if fragment in folded:
                errors.append("forbidden_fragment:%s" % fragment)


def _collect_ids(mapping: Mapping[str, Any]) -> Dict[str, set]:
    spaces = {name: set() for name in ("zone", "layout", "region", "component", "tab", "provider", "operation")}
    nav = mapping.get("navigation", {})
    for zone in nav.get("zones", []) if isinstance(nav, Mapping) else []:
        if isinstance(zone, Mapping) and isinstance(zone.get("zone_id"), str): spaces["zone"].add(zone["zone_id"])
    for layout in mapping.get("layout", []) if isinstance(mapping.get("layout", []), list) else []:
        if not isinstance(layout, Mapping): continue
        if isinstance(layout.get("layout_id"), str): spaces["layout"].add(layout["layout_id"])
        for region in layout.get("regions", []) if isinstance(layout.get("regions", []), list) else []:
            if not isinstance(region, Mapping): continue
            if isinstance(region.get("region_id"), str): spaces["region"].add(region["region_id"])
            comp = region.get("properties", {}).get("composition", {}) if isinstance(region.get("properties", {}), Mapping) else {}
            for tab in comp.get("tabs", []) if isinstance(comp, Mapping) and isinstance(comp.get("tabs", []), list) else []:
                if isinstance(tab, Mapping) and isinstance(tab.get("tab_id"), str): spaces["tab"].add(tab["tab_id"])
    for component in mapping.get("components", []) if isinstance(mapping.get("components", []), list) else []:
        if isinstance(component, Mapping) and isinstance(component.get("component_id"), str): spaces["component"].add(component["component_id"])
    for source in mapping.get("data_sources", []) if isinstance(mapping.get("data_sources", []), list) else []:
        if isinstance(source, Mapping) and isinstance(source.get("provider_id"), str): spaces["provider"].add(source["provider_id"])
    for operation in mapping.get("operations", []) if isinstance(mapping.get("operations", []), list) else []:
        if isinstance(operation, Mapping) and isinstance(operation.get("operation_id"), str): spaces["operation"].add(operation["operation_id"])
    return spaces


def guard_mapping(mapping: Mapping[str, Any], max_depth: int = 16, max_nodes: int = 20000) -> GuardReport:
    if not isinstance(mapping, Mapping):
        raise AdversarialGuardViolation("manifest mapping required")
    errors = []
    state = {"nodes": 0, "depth": 0, "max_nodes": int(max_nodes)}
    _walk(mapping, 0, int(max_depth), state, errors)
    spaces = _collect_ids(mapping)
    names = tuple(spaces)
    allowed_cross_space_reuse = {frozenset(("zone", "tab"))}
    for index, left in enumerate(names):
        for right in names[index + 1:]:
            if frozenset((left, right)) in allowed_cross_space_reuse:
                continue
            collisions = spaces[left] & spaces[right]
            for identifier in sorted(collisions):
                errors.append("cross_namespace_collision:%s:%s:%s" % (left, right, identifier))
    return GuardReport(not errors, state["nodes"], state["depth"], tuple(sorted(set(errors))))


def canonical_digest(mapping: Mapping[str, Any]) -> str:
    payload = json.dumps(mapping, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def assert_yaml_json_parity(yaml_mapping: Mapping[str, Any], json_mapping: Mapping[str, Any]) -> None:
    if canonical_digest(yaml_mapping) != canonical_digest(json_mapping):
        raise AdversarialGuardViolation("yaml_json_semantic_divergence")


def degradation_plan(mapping: Mapping[str, Any], available_providers: Iterable[str]) -> Tuple[Tuple[str, str], ...]:
    available = frozenset(available_providers)
    result = []
    for component in mapping.get("components", []):
        if not isinstance(component, Mapping):
            continue
        component_id = str(component.get("component_id", ""))
        provider_id = component.get("provider_id")
        status = "available" if provider_id is None or provider_id in available else "placeholder"
        result.append((component_id, status))
        if component.get("operation_ids"):
            raise AdversarialGuardViolation("operation_activation_during_degradation")
    return tuple(result)
