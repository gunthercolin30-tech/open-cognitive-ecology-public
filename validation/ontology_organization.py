"""Resolve and validate the logical organization of ontology modules."""

from __future__ import annotations

import ast
from collections import Counter, defaultdict
import difflib
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent.parent
ONTOLOGY = ROOT / "ontology"
POLICY_PATH = ROOT / "config" / "ontology_organization.json"
JSON_REPORT = ROOT / "validation" / "ontology_organization_report.json"
MARKDOWN_REPORT = ROOT / "docs" / "ontology_organization_inventory.md"


def load_policy():
    return json.loads(POLICY_PATH.read_text(encoding="utf-8"))


def canonical_modules(policy):
    taxonomy_path = ROOT / policy["canonical_taxonomy"]
    content = taxonomy_path.read_text(encoding="utf-8")
    return set(re.findall(r"`([a-zA-Z0-9_]+)`", content))


def documented_hierarchical_levels(policy):
    taxonomy_path = ROOT / policy["canonical_taxonomy"]
    content = taxonomy_path.read_text(encoding="utf-8")
    levels = {}
    current_level = None
    for line in content.splitlines():
        level_match = re.match(r"## Level (\d+)", line)
        if level_match:
            current_level = int(level_match.group(1))
            continue
        module_match = re.match(r"- `([a-zA-Z0-9_]+)`", line)
        if module_match and current_level is not None:
            levels[module_match.group(1)] = current_level
    return levels


def registered_hierarchical_levels(policy):
    path = ROOT / policy["hierarchical_registry"]
    tree = ast.parse(path.read_text(encoding="utf-8"))
    value = literal_assignment(tree, "HIERARCHICAL_LEVELS")
    return value if isinstance(value, dict) else {}


def literal_assignment(tree, name):
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(
            isinstance(target, ast.Name) and target.id == name
            for target in node.targets
        ):
            continue
        try:
            return ast.literal_eval(node.value)
        except (ValueError, TypeError):
            return None
    return None


def embedded_identity(tree, module=None):
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if not any(
            isinstance(target, ast.Name)
            and target.id in {
                "PRIMITIVE",
                "PRIMITIVE_NAME",
                "primitive",
                "primitive_name",
            }
            for target in node.targets
        ):
            continue
        try:
            value = ast.literal_eval(node.value)
        except (ValueError, TypeError):
            continue
        if isinstance(value, str) and value.strip():
            return value
    if module:
        normalized_module = module.lower()
        for node in ast.walk(tree):
            if not isinstance(node, ast.Dict):
                continue
            for key, value in zip(node.keys, node.values):
                try:
                    literal_key = ast.literal_eval(key)
                    literal_value = ast.literal_eval(value)
                except (ValueError, TypeError):
                    continue
                if (
                    literal_key in {"primitive", "primitive_name"}
                    and isinstance(literal_value, str)
                    and literal_value.lower() == normalized_module
                ):
                    return literal_value
    return None


def called_names(tree):
    names = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name):
            names.add(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            names.add(node.func.attr)
    return names


def imported_roots(tree):
    roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    return roots


def imported_ontology_modules(tree):
    modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                parts = alias.name.split(".")
                if len(parts) >= 2 and parts[0] == "ontology":
                    modules.add(parts[1])
        elif (
            isinstance(node, ast.ImportFrom)
            and node.module
            and node.module.startswith("ontology.")
        ):
            modules.add(node.module.split(".")[1])
    return sorted(modules)


def execution_profile(tree):
    calls = called_names(tree)
    imports = imported_roots(tree)

    if "subprocess" in imports or calls.intersection(
        {"Popen", "call", "check_call", "check_output"}
    ):
        return "subprocess"
    if imports.intersection({"aiohttp", "httpx", "requests", "urllib"}):
        return "network"
    if calls.intersection(
        {
            "dump",
            "mkdir",
            "open",
            "rename",
            "unlink",
            "write_bytes",
            "write_text",
        }
    ):
        return "filesystem"
    if calls.intersection({"execute", "launch", "run", "start"}):
        return "stateful"
    return "pure"


def rule_matches(module, rule):
    module = module.lower()
    candidates = {module, re.sub(r"_v\d+$", "", module)}
    return any(
        any(candidate.startswith(value.lower()) for value in rule.get("prefixes", []))
        or any(candidate.endswith(value.lower()) for value in rule.get("suffixes", []))
        or any(value.lower() in candidate for value in rule.get("tokens", []))
        for candidate in candidates
    )


def resolve_role(module, primitive, canonical, policy):
    override = policy["overrides"].get(module, {})
    if "role" in override:
        return override["role"], "override"
    if module in canonical:
        return "concept", "canonical_taxonomy"
    for rule in policy["role_rules"]:
        if rule_matches(module, rule):
            return rule["role"], "name_rule"
    if primitive:
        return "derived_concept", "primitive_fallback"
    return "support", "support_fallback"


def resolve_status(module, canonical, policy):
    override = policy["overrides"].get(module, {})
    if "status" in override:
        return override["status"], "override"
    if module in canonical:
        return "canonical", "canonical_taxonomy"
    for rule in policy["status_rules"]:
        if rule_matches(module, rule):
            return rule["status"], "name_rule"
    return "experimental", "experimental_fallback"


def analyze_module(path, canonical, policy):
    result = {
        "module": path.stem,
        "path": str(path.relative_to(ROOT)),
    }
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
    except SyntaxError as error:
        override = policy["overrides"].get(path.stem, {})
        has_override = "role" in override and "status" in override
        result.update(
            {
                "role": override.get("role", "support"),
                "role_source": "override" if has_override else "parse_error_fallback",
                "status": override.get("status", "experimental"),
                "status_source": "override" if has_override else "parse_error_fallback",
                "execution_profile": "stateful",
                "primitive": None,
                "identity": None,
                "identity_source": "unavailable",
                "dependencies": [],
                "ontology_imports": [],
                "parse_error": str(error),
            }
        )
        return result

    primitive = literal_assignment(tree, "PRIMITIVE")
    identity_override = policy.get("identity_overrides", {}).get(path.stem)
    identity_binding = policy.get("identity_bindings", {}).get(path.stem, {})
    bound_identity = identity_binding.get("identity")
    identity = (
        primitive
        if isinstance(primitive, str)
        else identity_override
        if isinstance(identity_override, str)
        else bound_identity
        if isinstance(bound_identity, str)
        else embedded_identity(tree, path.stem)
    )
    dependencies = literal_assignment(tree, "DEPENDENCIES")
    role, role_source = resolve_role(path.stem, primitive, canonical, policy)
    status, status_source = resolve_status(path.stem, canonical, policy)
    result.update(
        {
            "role": role,
            "role_source": role_source,
            "status": status,
            "status_source": status_source,
            "execution_profile": execution_profile(tree),
            "primitive": primitive if isinstance(primitive, str) else None,
            "identity": identity,
            "identity_source": (
                "module_primitive"
                if isinstance(primitive, str)
                else "override"
                if isinstance(identity_override, str)
                else "binding"
                if isinstance(bound_identity, str)
                else "embedded_identity"
                if identity
                else "missing"
            ),
            "identity_scope": identity_binding.get("scope"),
            "dependencies": dependencies if isinstance(dependencies, list) else [],
            "ontology_imports": imported_ontology_modules(tree),
        }
    )
    return result


def confidence_for_source(source):
    if source in {"canonical_taxonomy", "override"}:
        return "established"
    if source in {"name_rule", "primitive_fallback"}:
        return "inferred"
    return "review_required"


def classify_unresolved_dependency(dependency, discovered, policy):
    resolution = policy.get("dependency_resolutions", {}).get(dependency)
    if resolution:
        return (
            resolution["resolution"],
            resolution.get("confidence", "medium"),
            resolution.get("replacement"),
            resolution.get("evidence"),
            [],
            "policy_decision",
        )
    operational_suffixes = (
        "_analyzer",
        "_builder",
        "_certification",
        "_detection",
        "_generation",
        "_harvester",
        "_management",
        "_metrics",
        "_monitoring",
        "_process",
        "_scheduler",
        "_suite",
    )
    category = (
        "missing_component_candidate"
        if dependency.endswith(operational_suffixes)
        else "abstract_reference_candidate"
    )
    suggestions = difflib.get_close_matches(
        dependency,
        discovered,
        n=3,
        cutoff=0.55,
    )
    return category, "low", None, None, suggestions, "heuristic"


def dependency_topology(modules):
    by_name = {item["module"]: item for item in modules}
    graph = {
        module: [
            dependency.removeprefix("ontology.")
            for dependency in item["dependencies"]
            if dependency.removeprefix("ontology.") in by_name
        ]
        for module, item in by_name.items()
    }
    index = 0
    stack = []
    on_stack = set()
    indices = {}
    low_links = {}
    components = []

    def visit(module):
        nonlocal index
        indices[module] = index
        low_links[module] = index
        index += 1
        stack.append(module)
        on_stack.add(module)

        for dependency in graph[module]:
            if dependency not in indices:
                visit(dependency)
                low_links[module] = min(
                    low_links[module],
                    low_links[dependency],
                )
            elif dependency in on_stack:
                low_links[module] = min(
                    low_links[module],
                    indices[dependency],
                )

        if low_links[module] == indices[module]:
            component = []
            while True:
                member = stack.pop()
                on_stack.remove(member)
                component.append(member)
                if member == module:
                    break
            components.append(sorted(component))

    for module in graph:
        if module not in indices:
            visit(module)

    cycles = [
        component for component in components
        if len(component) > 1
        or component[0] in graph[component[0]]
    ]
    cycles.sort(key=lambda component: (-len(component), component))
    role_dependency_penalty = {
        ("concept", "runtime"): 5,
        ("concept", "integration"): 5,
        ("concept", "validation"): 5,
        ("concept", "observability"): 4,
        ("derived_concept", "runtime"): 5,
        ("derived_concept", "integration"): 4,
        ("derived_concept", "validation"): 5,
        ("derived_concept", "observability"): 3,
        ("integration", "runtime"): 5,
        ("integration", "validation"): 3,
        ("runtime", "validation"): 4,
        ("runtime", "observability"): 3,
        ("support", "runtime"): 3,
    }

    def edge_penalty(source, target):
        return role_dependency_penalty.get(
            (by_name[source]["role"], by_name[target]["role"]),
            0,
        )

    cycle_details = []
    for component in cycles:
        members = set(component)
        internal_edges = {
            (module, dependency)
            for module in component
            for dependency in graph[module]
            if dependency in members
        }
        cross_role_edges = {
            (source, target)
            for source, target in internal_edges
            if by_name[source]["role"] != by_name[target]["role"]
        }
        reciprocal_pairs = sorted({
            tuple(sorted((source, target)))
            for source, target in internal_edges
            if source != target and (target, source) in internal_edges
        })
        reciprocal_graph = defaultdict(set)
        for first, second in reciprocal_pairs:
            reciprocal_graph[first].add(second)
            reciprocal_graph[second].add(first)
        reciprocal_core_components = []
        reciprocal_seen = set()
        for module in sorted(reciprocal_graph):
            if module in reciprocal_seen:
                continue
            pending = [module]
            reciprocal_seen.add(module)
            reciprocal_component = []
            while pending:
                current = pending.pop()
                reciprocal_component.append(current)
                for neighbor in reciprocal_graph[current]:
                    if neighbor not in reciprocal_seen:
                        reciprocal_seen.add(neighbor)
                        pending.append(neighbor)
            reciprocal_core_components.append(sorted(reciprocal_component))
        edge_candidates = []
        for first, second in reciprocal_pairs:
            first_penalty = edge_penalty(first, second)
            second_penalty = edge_penalty(second, first)
            if first_penalty == second_penalty:
                recommended = max(first, second)
                retained = min(first, second)
                reason = "reciprocal_dependency_requires_explicit_owner"
                confidence = "low"
            elif first_penalty > second_penalty:
                recommended = first
                retained = second
                reason = "role_direction_inversion"
                confidence = "medium"
            else:
                recommended = second
                retained = first
                reason = "role_direction_inversion"
                confidence = "medium"
            edge_candidates.append(
                {
                    "remove_candidate": [recommended, retained],
                    "retain_candidate": [retained, recommended],
                    "reason": reason,
                    "confidence": confidence,
                    "replacement_mechanism": (
                        "event_or_result_contract"
                        if by_name[recommended]["role"] in {
                            "concept",
                            "derived_concept",
                            "runtime",
                        }
                        else "dependency_inversion"
                    ),
                }
            )
        degree = Counter()
        cross_role_degree = Counter()
        for source, target in internal_edges:
            degree[source] += 1
            degree[target] += 1
        for source, target in cross_role_edges:
            cross_role_degree[source] += 1
            cross_role_degree[target] += 1
        density = len(internal_edges) / (
            len(component) * max(1, len(component) - 1)
        )
        priority = (
            "high"
            if density >= 0.50 or len(component) >= 20
            else "medium"
        )
        cycle_details.append(
            {
                "modules": component,
                "size": len(component),
                "internal_edges": len(internal_edges),
                "internal_edge_list": [
                    list(edge) for edge in sorted(internal_edges)
                ],
                "cross_role_edges": len(cross_role_edges),
                "density": round(density, 6),
                "reciprocal_pairs": reciprocal_pairs,
                "reciprocal_core_components": reciprocal_core_components,
                "reciprocal_core_modules": sorted(reciprocal_seen),
                "peripheral_modules": sorted(members - reciprocal_seen),
                "edge_candidates": edge_candidates,
                "priority": priority,
                "top_bridge_modules": [
                    {
                        "module": module,
                        "role": by_name[module]["role"],
                        "cross_role_degree": cross_role_degree[module],
                        "total_degree": degree[module],
                    }
                    for module in sorted(
                        component,
                        key=lambda module: (
                            -cross_role_degree[module],
                            -degree[module],
                            module,
                        ),
                    )[:8]
                ],
            }
        )
    role_edges = Counter(
        (by_name[module]["role"], by_name[dependency]["role"])
        for module, dependencies in graph.items()
        for dependency in dependencies
    )
    return {
        "internal_edges": sum(len(dependencies) for dependencies in graph.values()),
        "strongly_connected_components": len(components),
        "cycles": cycles,
        "cycle_details": cycle_details,
        "modules_in_cycles": sum(len(component) for component in cycles),
        "role_edges": [
            {
                "source_role": source,
                "target_role": target,
                "count": count,
            }
            for (source, target), count in sorted(
                role_edges.items(),
                key=lambda item: (-item[1], item[0]),
            )
        ],
    }


def cycle_review_queue(topology, policy):
    edge_decisions = policy.get("cycle_edge_decisions", {})
    subgraph_decisions = policy.get("cycle_subgraph_decisions", {})

    def remains_cyclic(modules, edges):
        graph = {module: [] for module in modules}
        for source, target in edges:
            graph[source].append(target)
        visiting = set()
        visited = set()

        def visit(module):
            if module in visiting:
                return True
            if module in visited:
                return False
            visiting.add(module)
            if any(visit(target) for target in graph[module]):
                return True
            visiting.remove(module)
            visited.add(module)
            return False

        return any(visit(module) for module in modules)

    queue = []
    for index, detail in enumerate(topology["cycle_details"], start=1):
        if detail["size"] >= 10:
            category = "systemic_dependency_cluster"
            recommendation = "split_into_domain_subgraphs_before_edge_changes"
        elif detail["size"] >= 5:
            category = "mixed_boundary_cycle"
            recommendation = "replace_reverse_boundary_edges_with_event_contracts"
        elif detail["cross_role_edges"] == 0:
            category = "same_role_reciprocal_cycle"
            recommendation = "clarify_direction_or_extract_shared_contract"
        else:
            category = "cross_role_reciprocal_cycle"
            recommendation = "replace_reverse_dependency_with_event_or_result_contract"
        edge_candidates = []
        for candidate in detail["edge_candidates"]:
            source, target = candidate["remove_candidate"]
            decision = edge_decisions.get(f"{source}->{target}")
            edge_candidates.append(
                {
                    **candidate,
                    "decision": decision["decision"] if decision else None,
                    "decision_confidence": (
                        decision.get("confidence") if decision else None
                    ),
                    "decision_evidence": (
                        decision.get("evidence") if decision else None
                    ),
                }
            )
        edge_decided_removals = {
            tuple(edge)
            for edge in detail["internal_edge_list"]
            if edge_decisions.get("->".join(edge), {}).get("decision", "").startswith(
                ("approved_remove", "approved_replace")
            )
        }
        subgraph_decided_removals = set()
        for decision in subgraph_decisions.values():
            scope = set(decision["scope_modules"])
            active_scope = scope & set(detail["modules"])
            if len(active_scope) < 2:
                continue
            layer_by_module = {
                module: index
                for index, layer in enumerate(decision["dependency_layers"])
                for module in layer
            }
            subgraph_decided_removals.update(
                tuple(edge)
                for edge in detail["internal_edge_list"]
                if edge[0] in active_scope
                and edge[1] in active_scope
                and layer_by_module[edge[0]] >= layer_by_module[edge[1]]
            )
        decided_removals = edge_decided_removals | subgraph_decided_removals
        remaining_edges = {
            tuple(edge) for edge in detail["internal_edge_list"]
        } - decided_removals
        decision_status = (
            "approved"
            if decided_removals
            and not remains_cyclic(detail["modules"], remaining_edges)
            else "pending"
        )
        cycle_decisions = [
            {
                "edge": list(edge),
                **edge_decisions["->".join(edge)],
            }
            for edge in detail["internal_edge_list"]
            if "->".join(edge) in edge_decisions
        ]
        cycle_subgraph_decisions = [
            {
                "name": name,
                **decision,
                "active_scope_modules": sorted(
                    set(decision["scope_modules"]) & set(detail["modules"])
                ),
            }
            for name, decision in sorted(subgraph_decisions.items())
            if len(set(decision["scope_modules"]) & set(detail["modules"])) >= 2
        ]
        queue.append(
            {
                "cycle_id": f"cycle_{index:02d}",
                "priority": detail["priority"],
                "category": category,
                "decision_status": decision_status,
                "size": detail["size"],
                "modules": detail["modules"],
                "top_bridge_modules": [
                    item["module"] for item in detail["top_bridge_modules"][:3]
                ],
                "reciprocal_core_components":
                    detail["reciprocal_core_components"],
                "reciprocal_core_module_count":
                    len(detail["reciprocal_core_modules"]),
                "peripheral_module_count": len(detail["peripheral_modules"]),
                "edge_candidates": edge_candidates,
                "cycle_decisions": cycle_decisions,
                "subgraph_decisions": cycle_subgraph_decisions,
                "approved_theoretical_edge_removals":
                    len(decided_removals),
                "recommendation": recommendation,
            }
        )
    return queue


def semantic_review_findings(modules, policy):
    findings = []
    operational_roles = {
        "integration",
        "observability",
        "runtime",
        "validation",
    }
    conceptual_roles = {"concept", "derived_concept"}
    effectful_profiles = {"filesystem", "network", "subprocess"}
    operational_suffix_roles = {
        "_allocator": "runtime",
        "_archive": "observability",
        "_certifier": "validation",
        "_demonstrator": "validation",
        "_node": "runtime",
        "_onboarding": "runtime",
        "_persistence": "runtime",
        "_repository": "integration",
        "_store": "integration",
        "_synchronizer": "runtime",
    }

    for item in modules:
        documented_effect_boundary = (
            policy.get("canonical_execution_exceptions", {})
            .get(item["module"], {})
            .get("allowed_profile") == item["execution_profile"]
        )
        if (
            item["role"] in conceptual_roles
            and item["execution_profile"] in effectful_profiles
            and not documented_effect_boundary
        ):
            suggested_role = next(
                (
                    role for suffix, role in operational_suffix_roles.items()
                    if item["module"].endswith(suffix)
                ),
                None,
            )
            findings.append(
                {
                    "module": item["module"],
                    "severity": (
                        "high"
                        if item["execution_profile"] in {"network", "subprocess"}
                        else "medium"
                    ),
                    "finding": "conceptual_module_with_external_effect",
                    "role": item["role"],
                    "execution_profile": item["execution_profile"],
                    "suggested_role": suggested_role,
                    "recommendation": (
                        "consider_role_reclassification"
                        if suggested_role
                        else "document_effect_boundary"
                    ),
                }
            )

        if item["role"] in operational_roles and item["identity"] is None:
            findings.append(
                {
                    "module": item["module"],
                    "severity": "medium",
                    "finding": "operational_module_without_primitive_identity",
                    "role": item["role"],
                    "execution_profile": item["execution_profile"],
                    "recommendation":
                        "declare_identity_or_mark_as_support_component",
                }
            )

        if (
            item["role"] in operational_roles
            and item["execution_profile"] == "pure"
            and not item["dependencies"]
            and item["identity"] is None
        ):
            findings.append(
                {
                    "module": item["module"],
                    "severity": "low",
                    "finding": "thin_operational_shell",
                    "role": item["role"],
                    "execution_profile": item["execution_profile"],
                    "recommendation":
                        "confirm_operational_role_or_reclassify_as_support",
                }
            )

    severity_order = {"high": 0, "medium": 1, "low": 2}
    findings.sort(
        key=lambda item: (
            severity_order[item["severity"]],
            item["finding"],
            item["module"],
        )
    )
    return findings


def identity_normalization_findings(modules):
    operational_roles = {
        "integration",
        "observability",
        "runtime",
        "validation",
    }
    variant_pattern = re.compile(r"(?:_v\d+|_fixed|_clean|_repair|_final)$")
    facade_suffixes = (
        "_activation",
        "_adapter",
        "_application",
        "_backend",
        "_bridge",
        "_connector",
        "_fabric",
        "_hook",
        "_integration",
        "_interface",
        "_layer",
    )
    entrypoint_suffixes = (
        "_certification",
        "_demonstrator",
        "_experiment",
        "_launcher",
        "_stress_test",
        "_validation",
        "_validator",
    )
    utility_suffixes = (
        "_dashboard",
        "_provisioning",
        "_report",
        "_tool",
        "_utility",
    )
    effectful_profiles = {"filesystem", "network", "subprocess"}
    findings = []

    for item in modules:
        if item["role"] not in operational_roles or item["identity"] is not None:
            continue

        module = item["module"]
        if variant_pattern.search(module):
            category = "historical_variant"
            recommendation = "link_to_authoritative_family_identity"
            priority = "low"
        elif module.startswith("run_") or module.endswith(entrypoint_suffixes):
            category = "command_or_validation_entrypoint"
            recommendation = "declare_entrypoint_scope_and_target_identity"
            priority = "medium"
        elif module.endswith(facade_suffixes):
            category = "integration_facade"
            recommendation = "declare_facade_scope_and_backing_identity"
            priority = "low"
        elif module.endswith(utility_suffixes):
            category = "operational_utility"
            recommendation = "declare_utility_scope_or_reclassify_as_support"
            priority = "low"
        else:
            category = "anonymous_operational_component"
            recommendation = "declare_stable_operational_identity"
            priority = (
                "high"
                if item["execution_profile"] in effectful_profiles
                else "medium"
            )

        findings.append(
            {
                "module": module,
                "priority": priority,
                "category": category,
                "role": item["role"],
                "execution_profile": item["execution_profile"],
                "recommendation": recommendation,
            }
        )

    priority_order = {"high": 0, "medium": 1, "low": 2}
    findings.sort(
        key=lambda item: (
            priority_order[item["priority"]],
            item["category"],
            item["module"],
        )
    )
    return findings


def variant_authority_families(modules):
    by_name = {item["module"].lower(): item for item in modules}
    inbound_references = defaultdict(list)
    for item in modules:
        references = {
            reference.removeprefix("ontology.")
            for reference in (
                item["dependencies"] + item.get("ontology_imports", [])
            )
            if isinstance(reference, str)
        }
        for reference in references:
            if reference in by_name:
                inbound_references[reference].append(item["module"])
    variants = []

    for item in modules:
        original = item["module"]
        normalized = original.lower()
        is_variant = bool(
            re.search(r"_v\d+", normalized)
            or re.search(r"_(?:clean|fixed|repair|final)$", normalized)
            or normalized.startswith(("final_", "repair_"))
        )
        if not is_variant:
            continue

        base = re.sub(r"^(?:final_|repair_)", "", normalized)
        base = re.sub(r"_v\d+.*$", "", base)
        base = re.sub(r"_(?:clean|fixed|repair|final)$", "", base)
        candidates = [base]
        if base.startswith("general_"):
            candidates.append(base.removeprefix("general_"))
        if normalized.startswith("repair_") and base.endswith("_format"):
            candidates.append(base.removesuffix("_format"))

        authority = next(
            (
                by_name[candidate]
                for candidate in candidates
                if candidate in by_name
                and by_name[candidate]["status"] not in {
                    "compatibility",
                    "deprecated",
                    "superseded",
                }
            ),
            None,
        )
        variants.append(
            {
                "variant": original,
                "variant_status": item["status"],
                "family": authority["module"] if authority else base,
                "authority": authority["module"] if authority else None,
                "authority_status": authority["status"] if authority else None,
                "inbound_references": sorted(inbound_references[original]),
            }
        )

    grouped = defaultdict(list)
    for item in variants:
        grouped[item["family"]].append(item)

    families = []
    for family, members in grouped.items():
        authority = next(
            (item["authority"] for item in members if item["authority"]),
            None,
        )
        authority_status = next(
            (
                item["authority_status"]
                for item in members
                if item["authority"] == authority
            ),
            None,
        )
        active_variants = sorted(
            item["variant"]
            for item in members
            if item["inbound_references"]
        )
        active_superseded_variants = sorted(
            item["variant"]
            for item in members
            if item["inbound_references"]
            and item["variant_status"] == "superseded"
        )
        reference_sources = sorted({
            source
            for item in members
            for source in item["inbound_references"]
        })
        variant_references = {
            item["variant"]: item["inbound_references"]
            for item in members
            if item["inbound_references"]
        }
        variant_reference_statuses = {
            variant: {
                source: by_name[source]["status"]
                for source in sources
            }
            for variant, sources in variant_references.items()
        }
        if authority is None:
            if active_variants:
                decision = "active_variant_only"
                recommendation = "document_de_facto_authority_or_add_stable_base"
            else:
                decision = "missing_authority"
                recommendation = "designate_or_document_family_authority"
        elif authority_status == "canonical":
            decision = "confirmed_authority"
            recommendation = "retain_authority_and_exclude_variants_from_discovery"
        else:
            decision = "candidate_authority"
            recommendation = "confirm_candidate_or_keep_family_experimental"
        families.append(
            {
                "family": family,
                "decision": decision,
                "authority": authority,
                "authority_status": authority_status,
                "variants": sorted(item["variant"] for item in members),
                "active_variants": active_variants,
                "active_superseded_variants": active_superseded_variants,
                "reference_sources": reference_sources,
                "variant_references": variant_references,
                "variant_reference_statuses": variant_reference_statuses,
                "recommendation": recommendation,
            }
        )

    decision_order = {
        "missing_authority": 0,
        "active_variant_only": 1,
        "candidate_authority": 2,
        "confirmed_authority": 3,
    }
    families.sort(
        key=lambda item: (
            decision_order[item["decision"]],
            item["family"],
        )
    )
    return families


def variant_migration_queue(authority_families, policy):
    migration_decisions = policy.get("variant_migration_decisions", {})
    queue = []
    for family in authority_families:
        for variant in family["active_superseded_variants"]:
            sources = family["variant_references"][variant]
            source_statuses = family["variant_reference_statuses"][variant]
            active_sources = sorted(
                source for source, status in source_statuses.items()
                if status not in {"deprecated", "superseded"}
            )
            legacy_sources = sorted(
                source for source, status in source_statuses.items()
                if status in {"deprecated", "superseded"}
            )
            if not active_sources:
                priority = "low"
                action = "keep_reference_confined_to_legacy_chain"
                decision_status = "approved"
            elif variant in migration_decisions:
                priority = "high"
                action = migration_decisions[variant]["decision"]
                decision_status = "approved"
            elif family["authority_status"] == "canonical":
                priority = "high"
                action = "assess_compatibility_then_redirect_to_canonical_authority"
                decision_status = "pending"
            elif family["authority"]:
                priority = "medium"
                action = "confirm_candidate_before_redirecting_references"
                decision_status = "pending"
            else:
                priority = "high"
                action = "stabilize_active_variant_or_add_unversioned_authority"
                decision_status = "pending"
            queue.append(
                {
                    "variant": variant,
                    "family": family["family"],
                    "priority": priority,
                    "authority": family["authority"],
                    "authority_status": family["authority_status"],
                    "reference_sources": sources,
                    "active_reference_sources": active_sources,
                    "legacy_reference_sources": legacy_sources,
                    "decision_status": decision_status,
                    "decision_evidence": migration_decisions.get(
                        variant, {}
                    ).get("evidence"),
                    "action": action,
                }
            )

    priority_order = {"high": 0, "medium": 1, "low": 2}
    queue.sort(
        key=lambda item: (
            priority_order[item["priority"]],
            item["family"],
            item["variant"],
        )
    )
    return queue


def residual_decision_queue(unresolved, migration_queue, cycle_queue):
    decisions = [
        {
            "category": "missing_component_decision",
            "subject": dependency,
            "priority": "high",
            "recommendation": "decide_implementation_or_remove_dependency",
        }
        for dependency in sorted({
            item["dependency"] for item in unresolved
            if item["category"] == "missing_component"
        })
    ]
    decisions.extend(
        {
            "category": "active_variant_migration",
            "subject": item["variant"],
            "priority": item["priority"],
            "recommendation": item["action"],
        }
        for item in migration_queue
        if item["active_reference_sources"]
        and item["decision_status"] == "pending"
    )
    decisions.extend(
        {
            "category": "dependency_cycle_review",
            "subject": item["cycle_id"],
            "priority": item["priority"],
            "recommendation": item["recommendation"],
        }
        for item in cycle_queue
        if item["decision_status"] == "pending"
    )
    priority_order = {"high": 0, "medium": 1, "low": 2}
    decisions.sort(
        key=lambda item: (
            priority_order[item["priority"]],
            item["category"],
            item["subject"],
        )
    )
    return decisions


def build_report():
    policy = load_policy()
    canonical = canonical_modules(policy)
    documented_levels = documented_hierarchical_levels(policy)
    registered_levels = registered_hierarchical_levels(policy)
    modules = sorted(
        (
            analyze_module(path, canonical, policy)
            for path in ONTOLOGY.glob("*.py")
            if path.name != "__init__.py"
        ),
        key=lambda item: item["module"],
    )
    topology = dependency_topology(modules)
    cycle_queue = cycle_review_queue(topology, policy)
    semantic_findings = semantic_review_findings(modules, policy)
    identity_normalization = identity_normalization_findings(modules)
    authority_families = variant_authority_families(modules)
    migration_queue = variant_migration_queue(authority_families, policy)
    legacy_only_variant_references = [
        item["variant"]
        for item in migration_queue
        if not item["active_reference_sources"]
    ]
    active_superseded_variants = sorted({
        variant
        for family in authority_families
        for variant in family["active_superseded_variants"]
    })
    discovered = {item["module"] for item in modules}
    dependency_references = [
        (item["module"], dependency)
        for item in modules
        for dependency in item["dependencies"]
        if isinstance(dependency, str)
    ]
    unresolved = []
    for module, dependency in dependency_references:
        normalized = dependency.removeprefix("ontology.")
        if normalized in discovered:
            continue
        (
            category,
            confidence,
            replacement,
            evidence,
            suggestions,
            resolution_source,
        ) = classify_unresolved_dependency(
            normalized,
            discovered,
            policy,
        )
        unresolved.append(
            {
                "module": module,
                "dependency": normalized,
                "category": category,
                "resolution_confidence": confidence,
                "replacement": replacement,
                "evidence": evidence,
                "suggestions": suggestions,
                "resolution_source": resolution_source,
            }
        )
    residual_decisions = residual_decision_queue(
        unresolved,
        migration_queue,
        cycle_queue,
    )
    parse_errors = [
        {
            "module": item["module"],
            "path": item["path"],
            "error": item["parse_error"],
        }
        for item in modules
        if "parse_error" in item
    ]
    errors = []
    if missing := sorted(canonical - discovered):
        errors.append({"canonical_modules_missing": missing})
    hierarchy_extensions = policy.get("hierarchical_extensions", {})
    hierarchy_documentation_only = sorted(
        set(documented_levels) - set(registered_levels)
    )
    hierarchy_registry_only = sorted(
        set(registered_levels) - set(documented_levels)
    )
    hierarchy_level_mismatches = sorted(
        {
            module: {
                "documented": documented_levels[module],
                "registered": registered_levels[module],
            }
            for module in set(documented_levels) & set(registered_levels)
            if documented_levels[module] != registered_levels[module]
        }.items()
    )
    invalid_canonical_levels = sorted(
        module
        for module, level in documented_levels.items()
        if level not in policy["allowed_canonical_levels"]
    )
    extension_mismatches = sorted(
        module
        for module in set(hierarchy_registry_only) | set(hierarchy_extensions)
        if hierarchy_extensions.get(module) != registered_levels.get(module)
    )
    if hierarchy_documentation_only:
        errors.append({
            "hierarchy_documentation_only": hierarchy_documentation_only
        })
    if hierarchy_level_mismatches:
        errors.append({
            "hierarchy_level_mismatches": hierarchy_level_mismatches
        })
    if invalid_canonical_levels:
        errors.append({
            "invalid_canonical_levels": invalid_canonical_levels
        })
    if extension_mismatches:
        errors.append({
            "hierarchy_extension_mismatches": extension_mismatches
        })
    undecided_dependencies = sorted({
        item["dependency"]
        for item in unresolved
        if item["resolution_source"] != "policy_decision"
    })
    if undecided_dependencies:
        errors.append({
            "unresolved_dependencies_without_policy_decision":
                undecided_dependencies
        })
    invalid_replacements = sorted({
        item["replacement"]
        for item in unresolved
        if item["replacement"] and item["replacement"] not in discovered
    })
    if invalid_replacements:
        errors.append({
            "dependency_replacements_without_module": invalid_replacements
        })
    for item in modules:
        item["classification_confidence"] = confidence_for_source(
            item["role_source"]
        )
        if item["role"] not in policy["allowed_roles"]:
            errors.append({"invalid_role": item["module"], "value": item["role"]})
        if item["status"] not in policy["allowed_statuses"]:
            errors.append(
                {"invalid_status": item["module"], "value": item["status"]}
            )
        if item["execution_profile"] not in policy["allowed_execution_profiles"]:
            errors.append(
                {
                    "invalid_execution_profile": item["module"],
                    "value": item["execution_profile"],
                }
            )
    canonical_effectful = [
        item for item in modules
        if item["module"] in canonical and item["execution_profile"] != "pure"
    ]
    unapproved_canonical_effects = [
        item["module"]
        for item in canonical_effectful
        if policy.get("canonical_execution_exceptions", {})
        .get(item["module"], {})
        .get("allowed_profile") != item["execution_profile"]
    ]
    if unapproved_canonical_effects:
        errors.append({
            "unapproved_canonical_execution_effects":
                sorted(unapproved_canonical_effects)
        })

    return {
        "schema_version": policy["schema_version"],
        "summary": {
            "modules": len(modules),
            "canonical_modules": len(canonical),
            "hierarchical_registry_entries": len(registered_levels),
            "hierarchical_extensions": len(hierarchy_registry_only),
            "hierarchical_level_mismatches": len(hierarchy_level_mismatches),
            "canonical_effectful_modules": len(canonical_effectful),
            "internal_dependency_edges": topology["internal_edges"],
            "dependency_cycles": len(topology["cycles"]),
            "modules_in_dependency_cycles": topology["modules_in_cycles"],
            "largest_dependency_cycle": max(
                (len(component) for component in topology["cycles"]),
                default=0,
            ),
            "cycle_review_queue_entries": len(cycle_queue),
            "cycle_review_category_counts": dict(sorted(Counter(
                item["category"] for item in cycle_queue
            ).items())),
            "cycle_review_priority_counts": dict(sorted(Counter(
                item["priority"] for item in cycle_queue
            ).items())),
            "cycle_review_decision_status_counts": dict(sorted(Counter(
                item["decision_status"] for item in cycle_queue
            ).items())),
            "semantic_review_findings": len(semantic_findings),
            "semantic_review_severity_counts": dict(sorted(Counter(
                item["severity"] for item in semantic_findings
            ).items())),
            "semantic_review_type_counts": dict(sorted(Counter(
                item["finding"] for item in semantic_findings
            ).items())),
            "semantic_review_recommendation_counts": dict(sorted(Counter(
                item["recommendation"] for item in semantic_findings
            ).items())),
            "identity_source_counts": dict(sorted(Counter(
                item["identity_source"] for item in modules
            ).items())),
            "identity_binding_scope_counts": dict(sorted(Counter(
                item["identity_scope"] for item in modules
                if item.get("identity_scope")
            ).items())),
            "identity_normalization_candidates": len(identity_normalization),
            "identity_normalization_priority_counts": dict(sorted(Counter(
                item["priority"] for item in identity_normalization
            ).items())),
            "identity_normalization_category_counts": dict(sorted(Counter(
                item["category"] for item in identity_normalization
            ).items())),
            "variant_authority_families": len(authority_families),
            "variant_authority_decision_counts": dict(sorted(Counter(
                item["decision"] for item in authority_families
            ).items())),
            "active_superseded_variants": len(active_superseded_variants),
            "variant_migration_queue_entries": len(migration_queue),
            "variant_migration_priority_counts": dict(sorted(Counter(
                item["priority"] for item in migration_queue
            ).items())),
            "variant_migration_decision_status_counts": dict(sorted(Counter(
                item["decision_status"] for item in migration_queue
            ).items())),
            "legacy_only_variant_references": len(
                legacy_only_variant_references
            ),
            "role_counts": dict(sorted(Counter(
                item["role"] for item in modules
            ).items())),
            "status_counts": dict(sorted(Counter(
                item["status"] for item in modules
            ).items())),
            "execution_profile_counts": dict(sorted(Counter(
                item["execution_profile"] for item in modules
            ).items())),
            "role_source_counts": dict(sorted(Counter(
                item["role_source"] for item in modules
            ).items())),
            "classification_confidence_counts": dict(sorted(Counter(
                item["classification_confidence"] for item in modules
            ).items())),
            "unresolved_dependency_references": len(unresolved),
            "unresolved_dependency_identifiers": len({
                item["dependency"] for item in unresolved
            }),
            "unresolved_dependency_category_counts": dict(sorted(Counter(
                item["category"] for item in unresolved
            ).items())),
            "confirmed_missing_component_identifiers": len({
                item["dependency"] for item in unresolved
                if item["category"] == "missing_component"
            }),
            "residual_decision_queue_entries": len(residual_decisions),
            "residual_decision_category_counts": dict(sorted(Counter(
                item["category"] for item in residual_decisions
            ).items())),
            "residual_decision_priority_counts": dict(sorted(Counter(
                item["priority"] for item in residual_decisions
            ).items())),
            "unresolved_dependency_confidence_counts": dict(sorted(Counter(
                item["resolution_confidence"] for item in unresolved
            ).items())),
            "unresolved_dependency_source_counts": dict(sorted(Counter(
                item["resolution_source"] for item in unresolved
            ).items())),
            "parse_errors": len(parse_errors),
            "validation_errors": len(errors),
        },
        "validation_errors": errors,
        "parse_errors": parse_errors,
        "hierarchy": {
            "documentation_only": hierarchy_documentation_only,
            "registry_only_extensions": {
                module: registered_levels[module]
                for module in hierarchy_registry_only
            },
            "level_mismatches": dict(hierarchy_level_mismatches),
            "canonical_effectful_modules": canonical_effectful,
        },
        "dependency_topology": topology,
        "cycle_review_queue": cycle_queue,
        "semantic_review": semantic_findings,
        "identity_normalization": identity_normalization,
        "variant_authority_families": authority_families,
        "active_superseded_variants": active_superseded_variants,
        "variant_migration_queue": migration_queue,
        "legacy_only_variant_references": legacy_only_variant_references,
        "unresolved_dependencies": unresolved,
        "residual_decision_queue": residual_decisions,
        "modules": modules,
    }


def markdown(report):
    summary = report["summary"]
    cycle_edge_reviews = {
        tuple(candidate["remove_candidate"]): candidate
        for cycle in report["cycle_review_queue"]
        for candidate in cycle["edge_candidates"]
    }
    lines = [
        "# Inventaire logique des ontologies",
        "",
        "Inventaire genere sans importer ni deplacer les modules.",
        "Les classements issus de regles de nommage sont des hypotheses d'audit.",
        "",
        "## Synthese",
        "",
        f"- Modules classes : {summary['modules']}",
        f"- Modules canoniques : {summary['canonical_modules']}",
        (
            "- Entrees du registre hierarchique : "
            f"{summary['hierarchical_registry_entries']}"
        ),
        (
            "- Extensions hierarchiques explicites : "
            f"{summary['hierarchical_extensions']}"
        ),
        (
            "- Divergences de niveaux canoniques : "
            f"{summary['hierarchical_level_mismatches']}"
        ),
        (
            "- Aretes de dependances internes : "
            f"{summary['internal_dependency_edges']}"
        ),
        f"- Cycles de dependances : {summary['dependency_cycles']}",
        (
            "- Modules appartenant a un cycle : "
            f"{summary['modules_in_dependency_cycles']}"
        ),
        (
            "- Taille du plus grand cycle : "
            f"{summary['largest_dependency_cycle']}"
        ),
        (
            "- Cycles qualifies pour revue : "
            f"{summary['cycle_review_queue_entries']}"
        ),
        (
            "- Signaux de revue semantique : "
            f"{summary['semantic_review_findings']}"
        ),
        (
            "- Candidats a la normalisation d'identite : "
            f"{summary['identity_normalization_candidates']}"
        ),
        (
            "- Familles de variantes auditees : "
            f"{summary['variant_authority_families']}"
        ),
        (
            "- Variantes depassees encore referencees : "
            f"{summary['active_superseded_variants']}"
        ),
        f"- Erreurs de validation : {summary['validation_errors']}",
        f"- Erreurs de syntaxe detectees : {summary['parse_errors']}",
        (
            "- References de dependances non resolues : "
            f"{summary['unresolved_dependency_references']}"
        ),
        (
            "- Identifiants de dependances non resolus : "
            f"{summary['unresolved_dependency_identifiers']}"
        ),
        (
            "- Composants absents confirmes : "
            f"{summary['confirmed_missing_component_identifiers']}"
        ),
        (
            "- Decisions residuelles de cloture : "
            f"{summary['residual_decision_queue_entries']}"
        ),
        "",
        "## Roles",
        "",
        "| Role | Modules |",
        "|---|---:|",
    ]
    lines.extend(
        f"| `{name}` | {count} |"
        for name, count in summary["role_counts"].items()
    )
    lines.extend(
        [
            "",
            "## Revue semantique",
            "",
            (
                "Ces signaux indiquent une classification ou une frontiere "
                "d'effets a confirmer. Ils ne sont pas des erreurs."
            ),
            "",
            "| Severite | Signal | Modules |",
            "|---|---|---:|",
        ]
    )
    review_counts = Counter(
        (item["severity"], item["finding"])
        for item in report["semantic_review"]
    )
    lines.extend(
        f"| `{severity}` | `{finding}` | {count} |"
        for (severity, finding), count in sorted(
            review_counts.items(),
            key=lambda item: (
                {"high": 0, "medium": 1, "low": 2}[item[0][0]],
                item[0][1],
            ),
        )
    )
    lines.extend(["", "### Signaux prioritaires", ""])
    priority_findings = [
        item for item in report["semantic_review"]
        if item["severity"] in {"high", "medium"}
    ]
    for item in priority_findings[:40]:
        lines.append(
            f"- `{item['module']}` : `{item['finding']}`, "
            f"role `{item['role']}`, profil "
            f"`{item['execution_profile']}` ; "
            f"`{item['recommendation']}`"
            + (
                f" vers `{item['suggested_role']}`."
                if item.get("suggested_role")
                else "."
            )
        )
    lines.extend(
        [
            "",
            "## Normalisation des identites",
            "",
            (
                "Cette file distingue les composants operationnels reellement "
                "anonymes des variantes, facades, utilitaires et points "
                "d'entree. Elle ne modifie aucun module."
            ),
            "",
            "| Priorite | Categorie | Modules |",
            "|---|---|---:|",
        ]
    )
    identity_counts = Counter(
        (item["priority"], item["category"])
        for item in report["identity_normalization"]
    )
    lines.extend(
        f"| `{priority}` | `{category}` | {count} |"
        for (priority, category), count in sorted(
            identity_counts.items(),
            key=lambda item: (
                {"high": 0, "medium": 1, "low": 2}[item[0][0]],
                item[0][1],
            ),
        )
    )
    lines.extend(["", "### Identites prioritaires", ""])
    for item in report["identity_normalization"]:
        if item["priority"] == "low":
            continue
        lines.append(
            f"- `{item['module']}` : `{item['category']}`, "
            f"role `{item['role']}`, profil "
            f"`{item['execution_profile']}` ; "
            f"`{item['recommendation']}`."
        )
    lines.extend(
        [
            "",
            "## Autorite des variantes",
            "",
            (
                "Les familles ci-dessous sont derivees des marqueurs de "
                "version et de reparation. Une autorite candidate n'est pas "
                "promue automatiquement au statut canonique."
            ),
            "",
            "| Decision | Famille | Autorite | Variantes |",
            "|---|---|---|---:|",
        ]
    )
    lines.extend(
        (
            f"| `{item['decision']}` | `{item['family']}` | "
            f"`{item['authority'] or 'aucune'}` | {len(item['variants'])} |"
        )
        for item in report["variant_authority_families"]
    )
    lines.extend(["", "### Detail des familles", ""])
    for item in report["variant_authority_families"]:
        lines.append(
            f"- `{item['family']}` : autorite "
            f"`{item['authority'] or 'aucune'}` "
            f"(`{item['decision']}`) ; variantes "
            f"{', '.join(f'`{variant}`' for variant in item['variants'])} ; "
            + (
                "references actives depuis "
                f"{', '.join(f'`{source}`' for source in item['reference_sources'])} ; "
                if item["reference_sources"]
                else ""
            )
            + f"`{item['recommendation']}`."
        )
    lines.extend(["", "### Variantes depassees encore actives", ""])
    if report["active_superseded_variants"]:
        lines.extend(
            f"- `{variant}`."
            for variant in report["active_superseded_variants"]
        )
    else:
        lines.append("- Aucune variante depassee encore referencee.")
    lines.extend(["", "### File de migration des variantes", ""])
    if report["variant_migration_queue"]:
        for item in report["variant_migration_queue"]:
            lines.append(
                f"- `{item['variant']}` ({item['priority']}) : "
                f"cible `{item['authority'] or 'a definir'}` ; "
                f"appelants "
                f"{', '.join(f'`{source}`' for source in item['reference_sources'])} ; "
                + (
                    "chaine ancienne uniquement ; "
                    if not item["active_reference_sources"]
                    else ""
                )
                + f"`{item['action']}`."
                + f" Decision `{item['decision_status']}`."
            )
    else:
        lines.append("- Aucune migration de variante requise.")
    lines.extend(
        [
            "",
            "## Revue des cycles de dependances",
            "",
            (
                "Les cycles sont qualifies sans modifier les declarations de "
                "dependances. Les aretes candidates restent des hypotheses de "
                "decouplage a verifier."
            ),
            "",
        ]
    )
    for item in report["cycle_review_queue"]:
        lines.append(
            f"- `{item['cycle_id']}` ({item['priority']}, "
            f"{item['size']} modules, `{item['decision_status']}`) : "
            f"`{item['category']}` ; ponts "
            f"{', '.join(f'`{module}`' for module in item['top_bridge_modules'])} ; "
            f"`{item['recommendation']}`."
        )
        if item["reciprocal_core_components"]:
            lines.append(
                f"  - Noyau reciproque : "
                f"{item['reciprocal_core_module_count']} modules dans "
                f"{len(item['reciprocal_core_components'])} composante(s) ; "
                f"{item['peripheral_module_count']} modules peripheriques."
            )
        for decision in item["cycle_decisions"]:
            source, target = decision["edge"]
            lines.append(
                f"  - Decision `{decision['confidence']}` : "
                f"`{decision['decision']}` pour `{source} -> {target}`."
            )
        for decision in item["subgraph_decisions"]:
            lines.append(
                f"  - Sous-graphe `{decision['name']}` "
                f"(`{decision['confidence']}`) : `{decision['decision']}` ; "
                f"{len(decision['scope_modules'])} modules, "
                f"{len(decision['dependency_layers'])} couches."
            )
    lines.extend(["", "## Decisions residuelles de cloture", ""])
    for item in report["residual_decision_queue"]:
        lines.append(
            f"- `{item['subject']}` ({item['priority']}) : "
            f"`{item['category']}` ; `{item['recommendation']}`."
        )
    lines.extend(
        [
            "",
            "## Hierarchie",
            "",
            (
                "Le noyau canonique documente couvre les niveaux 0 a 9. "
                "Les extensions meta ci-dessous appartiennent au registre "
                "hierarchique sans appartenir au noyau documentaire."
            ),
            "",
        ]
    )
    lines.extend(
        f"- `{module}` : niveau {level}."
        for module, level in report["hierarchy"][
            "registry_only_extensions"
        ].items()
    )
    lines.extend(
        [
            "",
            "### Concepts canoniques avec effets",
            "",
        ]
    )
    canonical_effectful = report["hierarchy"]["canonical_effectful_modules"]
    if canonical_effectful:
        lines.extend(
            f"- `{item['module']}` : profil `{item['execution_profile']}`."
            for item in canonical_effectful
        )
    else:
        lines.append("- Aucun.")
    lines.extend(
        [
            "",
            "## Topologie des dependances",
            "",
            (
                "Les cycles sont des constats d'organisation. Ils ne sont pas "
                "consideres invalides automatiquement."
            ),
            "",
            "### Composantes cycliques",
            "",
        ]
    )
    for component in report["dependency_topology"]["cycles"]:
        preview = ", ".join(f"`{module}`" for module in component[:12])
        if len(component) > 12:
            preview += f", ... ({len(component) - 12} autres)"
        lines.append(f"- {len(component)} modules : {preview}.")
    lines.extend(
        [
            "",
            "### File de decouplage logique",
            "",
            (
                "La priorite combine taille, densite, reciprocite et "
                "melange de roles. Elle ne prescrit aucun deplacement."
            ),
            "",
        ]
    )
    for index, detail in enumerate(
        report["dependency_topology"]["cycle_details"],
        start=1,
    ):
        bridges = ", ".join(
            f"`{item['module']}`"
            for item in detail["top_bridge_modules"][:5]
        )
        lines.append(
            f"- Cycle {index}, priorite `{detail['priority']}` : "
            f"{detail['size']} modules, {detail['internal_edges']} aretes, "
            f"densite {detail['density']:.3f}, "
            f"{len(detail['reciprocal_pairs'])} paires reciproques, "
            f"{detail['cross_role_edges']} aretes inter-roles. "
            f"Ponts principaux : {bridges}."
        )
        if detail["reciprocal_core_components"]:
            lines.append(
                f"  - Noyau reciproque : "
                f"{len(detail['reciprocal_core_modules'])} modules dans "
                f"{len(detail['reciprocal_core_components'])} composante(s) ; "
                f"{len(detail['peripheral_modules'])} modules peripheriques."
            )
        for candidate in detail["edge_candidates"][:4]:
            source, target = candidate["remove_candidate"]
            reviewed_candidate = cycle_edge_reviews[(source, target)]
            lines.append(
                f"  - Candidat `{candidate['confidence']}` : remplacer "
                f"`{source} -> {target}` par "
                f"`{candidate['replacement_mechanism']}`."
            )
            if reviewed_candidate["decision"]:
                lines.append(
                    f"    - Decision "
                    f"`{reviewed_candidate['decision_confidence']}` : "
                    f"`{reviewed_candidate['decision']}` ; cette arete "
                    "inverse est approuvee pour remplacement."
                )
    lines.extend(
        [
            "",
            "### Couplages de roles dominants",
            "",
            "| Role source | Role cible | Aretes |",
            "|---|---|---:|",
        ]
    )
    lines.extend(
        (
            f"| `{edge['source_role']}` | `{edge['target_role']}` | "
            f"{edge['count']} |"
        )
        for edge in report["dependency_topology"]["role_edges"][:12]
    )
    lines.extend(
        [
            "",
            "## Statuts",
            "",
            "| Statut | Modules |",
            "|---|---:|",
        ]
    )
    lines.extend(
        f"| `{name}` | {count} |"
        for name, count in summary["status_counts"].items()
    )
    lines.extend(
        [
            "",
            "## Profils d'execution",
            "",
            "| Profil | Modules |",
            "|---|---:|",
        ]
    )
    lines.extend(
        f"| `{name}` | {count} |"
        for name, count in summary["execution_profile_counts"].items()
    )
    lines.extend(
        [
            "",
            "## Confiance du classement",
            "",
            "| Confiance | Modules |",
            "|---|---:|",
        ]
    )
    lines.extend(
        f"| `{name}` | {count} |"
        for name, count in summary[
            "classification_confidence_counts"
        ].items()
    )
    lines.extend(
        [
            "",
            "## Dependances non resolues",
            "",
            (
                "Ces categories sont des hypotheses de tri. Elles distinguent "
                "les references abstraites probables des composants "
                "operationnels probablement absents ou renommes."
            ),
            "",
            "| Categorie | References |",
            "|---|---:|",
        ]
    )
    lines.extend(
        f"| `{name}` | {count} |"
        for name, count in summary[
            "unresolved_dependency_category_counts"
        ].items()
    )
    lines.extend(
        [
            "",
            "| Source de resolution | References |",
            "|---|---:|",
        ]
    )
    lines.extend(
        f"| `{name}` | {count} |"
        for name, count in summary[
            "unresolved_dependency_source_counts"
        ].items()
    )
    lines.extend(
        [
            "",
            "| Confiance de resolution | References |",
            "|---|---:|",
        ]
    )
    lines.extend(
        f"| `{name}` | {count} |"
        for name, count in summary[
            "unresolved_dependency_confidence_counts"
        ].items()
    )
    lines.extend(["", "### Composants manquants ou renommes a examiner", ""])
    missing_components = [
        item for item in report["unresolved_dependencies"]
        if item["category"] in {
            "alias_candidate",
            "deprecated_reference",
            "missing_component",
            "missing_component_candidate",
        }
    ]
    grouped_components = defaultdict(
        lambda: {
            "categories": set(),
            "confidences": set(),
            "consumers": [],
            "replacements": set(),
            "suggestions": set(),
        }
    )
    for item in missing_components:
        grouped_components[item["dependency"]]["consumers"].append(item["module"])
        grouped_components[item["dependency"]]["categories"].add(item["category"])
        grouped_components[item["dependency"]]["confidences"].add(
            item["resolution_confidence"]
        )
        if item["replacement"]:
            grouped_components[item["dependency"]]["replacements"].add(
                item["replacement"]
            )
        grouped_components[item["dependency"]]["suggestions"].update(
            item["suggestions"]
        )
    for details in grouped_components.values():
        details["priority"] = (
            "high"
            if "missing_component" in details["categories"]
            and (
                "high" in details["confidences"]
                or len(details["consumers"]) > 1
            )
            else "medium"
        )
    ordered_components = sorted(
        grouped_components.items(),
        key=lambda item: (-len(item[1]["consumers"]), item[0]),
    )
    for dependency, details in ordered_components:
        consumers = ", ".join(
            f"`{consumer}`" for consumer in sorted(details["consumers"])
        )
        suggestions = ", ".join(
            f"`{suggestion}`" for suggestion in sorted(details["suggestions"])
        ) or "aucune suggestion"
        replacements = ", ".join(
            f"`{replacement}`" for replacement in sorted(details["replacements"])
        ) or "aucun remplacement decide"
        categories = ", ".join(sorted(details["categories"]))
        confidences = ", ".join(sorted(details["confidences"]))
        lines.append(
            f"- `{dependency}` ({len(details['consumers'])} reference(s)) : "
            f"priorite `{details['priority']}`, `{categories}`, "
            f"confiance `{confidences}` ; requis par "
            f"{consumers}. Remplacement : {replacements}. "
            f"Suggestions heuristiques : {suggestions}."
        )
    lines.extend(["", "### Capacites abstraites confirmees", ""])
    abstract_dependencies = defaultdict(list)
    for item in report["unresolved_dependencies"]:
        if item["category"] == "abstract_capability":
            abstract_dependencies[item["dependency"]].append(item["module"])
    for dependency, consumers in sorted(abstract_dependencies.items()):
        consumer_list = ", ".join(
            f"`{consumer}`" for consumer in sorted(consumers)
        )
        lines.append(f"- `{dependency}` : utilise par {consumer_list}.")
    lines.extend(
        [
            "",
            "## Modules a confirmer",
            "",
            (
                "Les modules suivants possedent encore un classement de repli "
                "ou une erreur d'analyse."
            ),
            "",
        ]
    )
    review_required = [
        item for item in report["modules"]
        if item["classification_confidence"] == "review_required"
    ]
    if review_required:
        lines.extend(
            f"- `{item['module']}` (`{item['role_source']}`)"
            for item in review_required
        )
    else:
        lines.append("- Aucun module restant.")
    lines.append("")
    return "\n".join(lines)


def save_report(report):
    JSON_REPORT.write_text(
        json.dumps(report, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN_REPORT.write_text(markdown(report), encoding="utf-8")


def main():
    report = build_report()
    save_report(report)
    print(json.dumps(report["summary"], indent=2))
    if report["validation_errors"]:
        raise SystemExit(1)
    return report


if __name__ == "__main__":
    main()
