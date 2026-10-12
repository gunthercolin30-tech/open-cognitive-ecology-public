"""Strict OIF-2G profile for complex, still non-executable manifests."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Mapping, Tuple
from .specification import InterfaceSpecification

class ComplexManifestViolation(ValueError):
    pass

def _plain(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(k): _plain(v) for k, v in value.items()}
    if isinstance(value, tuple):
        return [_plain(v) for v in value]
    return value

@dataclass(frozen=True)
class ComplexManifestReport:
    valid: bool
    tab_count: int
    dormant_operation_count: int
    degraded_component_count: int
    provider_contract_count: int
    errors: Tuple[str, ...]

def validate_complex_profile(specification: InterfaceSpecification) -> ComplexManifestReport:
    if not isinstance(specification, InterfaceSpecification):
        raise ComplexManifestViolation("expected InterfaceSpecification")
    component_ids = {c.component_id for c in specification.components}
    contracts = {s.provider_id: s.data_contract for s in specification.data_sources}
    errors = []
    tab_count = dormant_count = degraded_count = contract_count = 0
    for component in specification.components:
        props = _plain(component.properties)
        input_contract = props.get("input_contract")
        if input_contract is not None:
            contract_count += 1
            if component.provider_id is None:
                errors.append(f"{component.component_id}: input_contract_without_provider")
            elif contracts.get(component.provider_id) != input_contract:
                errors.append(f"{component.component_id}: incompatible_contract")
        degradation = props.get("degradation")
        if degradation is not None:
            degraded_count += 1
            if not isinstance(degradation, dict):
                errors.append(f"{component.component_id}: invalid_degradation")
            else:
                if degradation.get("mode") != "partial": errors.append(f"{component.component_id}: degradation_must_be_partial")
                if degradation.get("preserve_component") is not True: errors.append(f"{component.component_id}: degradation_must_preserve_component")
                if degradation.get("unavailable_behavior") != "placeholder": errors.append(f"{component.component_id}: invalid_unavailable_behavior")
        dormant = props.get("dormant_operations", [])
        if not isinstance(dormant, list):
            errors.append(f"{component.component_id}: dormant_operations_must_be_list")
            dormant = []
        for operation in dormant:
            dormant_count += 1
            if not isinstance(operation, dict):
                errors.append(f"{component.component_id}: invalid_dormant_operation")
                continue
            if operation.get("enabled") is not False: errors.append(f"{component.component_id}: dormant_operation_enabled")
            if operation.get("execution_forbidden") is not True: errors.append(f"{component.component_id}: dormant_operation_not_forbidden")
            if str(operation.get("activation_stage", "")).casefold() != "oif-4": errors.append(f"{component.component_id}: invalid_activation_stage")
        if component.operation_ids:
            errors.append(f"{component.component_id}: active_operations_forbidden")
    for layout in specification.layout:
        for region in layout.regions:
            composition = _plain(region.properties).get("composition")
            if not composition: continue
            if not isinstance(composition, dict):
                errors.append(f"{region.region_id}: composition_must_be_mapping"); continue
            kind = composition.get("kind")
            if kind not in {"tabs","stack","grid"}: errors.append(f"{region.region_id}: unsupported_composition_kind")
            if kind == "tabs":
                tabs = composition.get("tabs", [])
                if not isinstance(tabs, list) or not tabs:
                    errors.append(f"{region.region_id}: tabs_required"); continue
                seen = set()
                for tab in tabs:
                    tab_count += 1
                    if not isinstance(tab, dict): errors.append(f"{region.region_id}: invalid_tab"); continue
                    tab_id = tab.get("tab_id")
                    if not isinstance(tab_id, str) or not tab_id: errors.append(f"{region.region_id}: invalid_tab_id")
                    elif tab_id in seen: errors.append(f"{region.region_id}: duplicate_tab_id")
                    seen.add(tab_id)
                    refs = tab.get("component_ids", [])
                    if not isinstance(refs, list): errors.append(f"{region.region_id}: tab_component_ids_must_be_list"); continue
                    for ref in refs:
                        if ref not in component_ids: errors.append(f"{region.region_id}: unknown_tab_component:{ref}")
    return ComplexManifestReport(not errors, tab_count, dormant_count, degraded_count, contract_count, tuple(errors))
