"""Calibrated qualitative analysis of OIF-0 redundancy candidates.

This analyzer is read-only with respect to ontology and runtime sources.  It
uses convergent static evidence, records contradictions explicitly, and never
merges, deletes, deprecates, or rewrites candidate modules.  Lexical role
markers are hints only and can never decide a classification alone.
"""
from __future__ import annotations

import ast
import csv
import hashlib
import io
import json
import os
import re
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Set, Tuple

SCHEMA_VERSION = "oif-0-redundancy-qualitative-v2"
STATUS = "OIF_REDUNDANCY_QUALITATIVE_ANALYSIS_READY"
CLASSES = (
    "DISTINCT",
    "COMPLEMENTARY",
    "VIEW",
    "ADAPTER",
    "PARTIAL_OVERLAP",
    "PROBABLE_REDUNDANCY",
    "HUMAN_REVIEW_REQUIRED",
)
ROLE_TOKENS = {
    "dashboard": "VIEW", "view": "VIEW", "exporter": "VIEW",
    "renderer": "VIEW", "html": "VIEW",
    "interface": "ADAPTER", "adapter": "ADAPTER", "bridge": "ADAPTER",
    "integration": "ADAPTER", "terminal": "ADAPTER",
    "runtime": "COMPLEMENTARY", "manager": "COMPLEMENTARY",
    "controller": "COMPLEMENTARY", "monitor": "COMPLEMENTARY",
    "archive": "COMPLEMENTARY", "registry": "COMPLEMENTARY",
    "engine": "COMPLEMENTARY",
}
RENDER_MARKERS = {"render", "display", "dashboard", "html", "export", "serialize", "present", "view"}
ADAPTER_MARKERS = {"adapt", "bridge", "convert", "transform", "translate", "delegate", "wrap", "forward", "dispatch"}
STOP = {"ontology", "oif", "audit", "py", "the", "and", "of"}


def _canonical_json(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".%s." % path.name, dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass
        raise


def _tokens(name: str) -> Set[str]:
    parts = re.split(r"[^a-z0-9]+", name.lower().replace(".", "_"))
    return {part for part in parts if part and part not in STOP}


def _jaccard(left: Iterable[str], right: Iterable[str]) -> float:
    a, b = set(left), set(right)
    if not a and not b:
        return 0.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _public_names(tree: ast.AST) -> Set[str]:
    return {
        node.name for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        and not node.name.startswith("_")
    }


def _call_names(tree: ast.AST) -> Set[str]:
    names: Set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name):
            names.add(func.id)
        elif isinstance(func, ast.Attribute):
            chain = []
            current: ast.AST = func
            while isinstance(current, ast.Attribute):
                chain.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                chain.append(current.id)
            names.add(".".join(reversed(chain)))
    return names


def _literal_writes(tree: ast.AST) -> Set[str]:
    writes: Set[str] = set()
    markers = {"write_text", "write_bytes", "open", "replace", "rename", "unlink", "mkdir"}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        name = func.attr if isinstance(func, ast.Attribute) else func.id if isinstance(func, ast.Name) else ""
        if name not in markers:
            continue
        for arg in node.args[:2]:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                writes.add(arg.value)
    return writes


def _imports(tree: ast.AST) -> Set[str]:
    values: Set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            values.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            values.add(node.module)
    return values


def _doc_tokens(tree: ast.AST) -> Set[str]:
    return _tokens(ast.get_docstring(tree) or "")


def _module_record(root: Path, baseline: Mapping[str, Any]) -> Dict[str, Any]:
    module = str(baseline["module"])
    path = root / str(baseline["path"])
    source = path.read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(source, filename=str(path))
    return {
        "module": module,
        "path": str(baseline["path"]),
        "classification": baseline.get("classification"),
        "entrypoints": sorted(set(baseline.get("entrypoints", []))),
        "gate_references": sorted(set(baseline.get("gate_references", []))),
        "representative_entrypoint": bool(baseline.get("representative_entrypoint")),
        "public_names": sorted(_public_names(tree)),
        "call_names": sorted(_call_names(tree)),
        "imports": sorted(_imports(tree)),
        "literal_writes": sorted(_literal_writes(tree)),
        "doc_tokens": sorted(_doc_tokens(tree)),
        "source_sha256": _sha256(source.encode("utf-8")),
        "line_count": len(source.splitlines()),
    }


def _role(module: str) -> str | None:
    toks = _tokens(module)
    for token, role in ROLE_TOKENS.items():
        if token in toks:
            return role
    return None


def _imports_peer(record: Mapping[str, Any], peer_module: str) -> bool:
    peer_leaf = peer_module.rsplit(".", 1)[-1]
    for imported in record["imports"]:
        if imported == peer_module or imported.endswith("." + peer_leaf):
            return True
    return False


def _marker_presence(values: Iterable[str], markers: Set[str]) -> bool:
    tokens: Set[str] = set()
    for value in values:
        tokens.update(_tokens(value))
    return bool(tokens & markers)


def _confidence(support: int, contradictions: int, category: str, score: float) -> str:
    margin = support - contradictions
    if category == "HUMAN_REVIEW_REQUIRED":
        return "LOW"
    if margin >= 3 and score >= 0.55:
        return "HIGH"
    if margin >= 1:
        return "MEDIUM"
    return "LOW"


def _classify(
    left: Mapping[str, Any],
    right: Mapping[str, Any],
    candidate: Mapping[str, Any],
) -> Tuple[str, List[str], List[str], float, str, str]:
    api = _jaccard(left["public_names"], right["public_names"])
    calls = _jaccard(left["call_names"], right["call_names"])
    imports = _jaccard(left["imports"], right["imports"])
    docs = _jaccard(left["doc_tokens"], right["doc_tokens"])
    names = float(candidate.get("name_jaccard", 0.0))
    score = round(0.30 * names + 0.30 * api + 0.18 * calls + 0.12 * imports + 0.10 * docs, 6)

    boundary_differences: List[str] = []
    if bool(left["literal_writes"]) != bool(right["literal_writes"]):
        boundary_differences.append("persistence_presence_differs")
    if bool(left["gate_references"]) != bool(right["gate_references"]):
        boundary_differences.append("governance_gate_presence_differs")
    if left["representative_entrypoint"] != right["representative_entrypoint"]:
        boundary_differences.append("representative_entrypoint_differs")
    if left["classification"] != right["classification"]:
        boundary_differences.append("baseline_classification_differs")

    role_left, role_right = _role(left["module"]), _role(right["module"])
    left_to_right = _imports_peer(left, right["module"])
    right_to_left = _imports_peer(right, left["module"])
    directional_dependency = left_to_right ^ right_to_left
    same_source = left["source_sha256"] == right["source_sha256"]
    line_ratio = min(left["line_count"], right["line_count"]) / max(left["line_count"], right["line_count"], 1)
    api_size_ratio = min(len(left["public_names"]), len(right["public_names"])) / max(len(left["public_names"]), len(right["public_names"]), 1)

    base = [
        "name_jaccard=%.3f" % names,
        "public_api_jaccard=%.3f" % api,
        "call_jaccard=%.3f" % calls,
        "import_jaccard=%.3f" % imports,
        "doc_jaccard=%.3f" % docs,
        "combined_score=%.3f" % score,
        "line_count_ratio=%.3f" % line_ratio,
        "api_size_ratio=%.3f" % api_size_ratio,
        "role_left=%s" % (role_left or "NONE"),
        "role_right=%s" % (role_right or "NONE"),
    ] + boundary_differences

    support: List[str] = []
    contradictions: List[str] = []

    view_sides = [record for record, role in ((left, role_left), (right, role_right)) if role == "VIEW"]
    exactly_one_view = len(view_sides) == 1
    view_record = view_sides[0] if exactly_one_view else None
    view_peer = right if view_record is left else left
    view_dependency = bool(view_record and _imports_peer(view_record, view_peer["module"]))
    view_render_signal = bool(view_record and (
        _marker_presence(view_record["public_names"], RENDER_MARKERS)
        or _marker_presence(view_record["call_names"], RENDER_MARKERS)
        or _marker_presence(view_record["doc_tokens"], RENDER_MARKERS)
    ))
    view_api_narrower = bool(view_record and len(view_record["public_names"]) <= len(view_peer["public_names"]))
    if exactly_one_view:
        support.append("single_view_role_hint")
        if view_dependency:
            support.append("view_imports_peer")
        if view_render_signal:
            support.append("rendering_semantics_detected")
        if view_api_narrower:
            support.append("view_api_not_broader_than_peer")
        if bool(view_record["literal_writes"]) and not bool(view_peer["literal_writes"]):
            contradictions.append("view_has_unique_persistence_boundary")
        if bool(view_record["gate_references"]) and not bool(view_peer["gate_references"]):
            contradictions.append("view_has_unique_governance_boundary")
        if not view_dependency and not directional_dependency:
            contradictions.append("no_view_to_peer_dependency")
        if len(support) >= 3 and len(contradictions) == 0:
            return "VIEW", base + support, contradictions, score, "multi_evidence_view_relation", _confidence(len(support), 0, "VIEW", score)

    adapter_sides = [record for record, role in ((left, role_left), (right, role_right)) if role == "ADAPTER"]
    exactly_one_adapter = len(adapter_sides) == 1
    adapter_record = adapter_sides[0] if exactly_one_adapter else None
    adapter_peer = right if adapter_record is left else left
    adapter_dependency = bool(adapter_record and _imports_peer(adapter_record, adapter_peer["module"]))
    adapter_signal = bool(adapter_record and (
        _marker_presence(adapter_record["public_names"], ADAPTER_MARKERS)
        or _marker_presence(adapter_record["call_names"], ADAPTER_MARKERS)
        or _marker_presence(adapter_record["doc_tokens"], ADAPTER_MARKERS)
    ))
    adapter_support: List[str] = []
    adapter_contradictions: List[str] = []
    if exactly_one_adapter:
        adapter_support.append("single_adapter_role_hint")
        if adapter_dependency:
            adapter_support.append("adapter_imports_peer")
        if adapter_signal:
            adapter_support.append("transformation_or_delegation_semantics_detected")
        if api < 0.80:
            adapter_support.append("api_exposure_differs")
        if not adapter_dependency and not directional_dependency:
            adapter_contradictions.append("no_adapter_to_peer_dependency")
        if same_source or (api >= 0.95 and calls >= 0.90):
            adapter_contradictions.append("duplication_signal_conflicts_with_adapter_role")
        if len(adapter_support) >= 3 and len(adapter_contradictions) == 0:
            return "ADAPTER", base + adapter_support, adapter_contradictions, score, "multi_evidence_adapter_relation", _confidence(len(adapter_support), 0, "ADAPTER", score)

    if same_source:
        support = ["identical_source_sha256"]
        return "PROBABLE_REDUNDANCY", base + support, boundary_differences, score, "identical_source_evidence", _confidence(4, len(boundary_differences), "PROBABLE_REDUNDANCY", max(score, 0.9))

    if score >= 0.82 and api >= 0.75 and calls >= 0.65 and imports >= 0.55 and not boundary_differences:
        support = ["high_multi_evidence_overlap", "no_distinct_boundary_detected"]
        return "PROBABLE_REDUNDANCY", base + support, [], score, "high_convergent_overlap", _confidence(4, 0, "PROBABLE_REDUNDANCY", score)

    if boundary_differences and score >= 0.58:
        support = ["material_similarity", "distinct_operational_boundary"]
        return "COMPLEMENTARY", base + support, [], score, "similar_but_boundary_separated", _confidence(2, 0, "COMPLEMENTARY", score)

    if score >= 0.58 or (api >= 0.50 and (calls >= 0.35 or imports >= 0.35)):
        support = ["material_overlap_without_duplication_proof"]
        contradictions = boundary_differences[:]
        return "PARTIAL_OVERLAP", base + support, contradictions, score, "partial_multi_evidence_overlap", _confidence(2, len(contradictions), "PARTIAL_OVERLAP", score)

    if boundary_differences and score < 0.45:
        support = ["low_overlap", "distinct_boundaries"]
        return "DISTINCT", base + support, [], score, "low_overlap_with_boundary_separation", _confidence(3, 0, "DISTINCT", score)

    if score < 0.30 and api < 0.30 and calls < 0.30:
        support = ["low_aggregate_overlap"]
        return "DISTINCT", base + support, [], score, "low_convergent_overlap", _confidence(3, 0, "DISTINCT", score)

    contradictions = boundary_differences[:]
    if exactly_one_view:
        contradictions.extend([item for item in ("lexical_view_hint_without_sufficient_structure",) if item not in contradictions])
    if exactly_one_adapter:
        contradictions.extend([item for item in ("lexical_adapter_hint_without_sufficient_structure",) if item not in contradictions])
    return "HUMAN_REVIEW_REQUIRED", base + ["insufficient_or_conflicting_static_evidence"], contradictions, score, "uncertain_multi_evidence_case", "LOW"


class OIFRedundancyCandidateAnalyzer:
    def __init__(self, root: Path | None = None, report_dir: Path | None = None) -> None:
        self.root = (root or (Path.home() / "open-cognitive-ecology")).resolve()
        self.report_dir = (report_dir or (self.root / "oif_audit")).resolve()

    def build(self) -> Dict[str, Any]:
        inventory = json.loads((self.report_dir / "oif_active_interface_inventory.json").read_text(encoding="utf-8"))
        candidates_payload = json.loads((self.report_dir / "oif_redundancy_report.json").read_text(encoding="utf-8"))
        fingerprint = inventory["source_fingerprint"]
        if candidates_payload.get("source_fingerprint") != fingerprint:
            raise ValueError("OIF baseline fingerprint mismatch")

        records: Dict[str, Dict[str, Any]] = {}
        for baseline in inventory["modules"]:
            records[baseline["module"]] = _module_record(self.root, baseline)

        analyses: List[Dict[str, Any]] = []
        seen: Set[Tuple[str, str]] = set()
        for raw in candidates_payload["candidates"]:
            pair = tuple(sorted((str(raw["left"]), str(raw["right"]))))
            if pair in seen:
                raise ValueError("duplicate candidate pair: %r" % (pair,))
            seen.add(pair)
            if pair[0] not in records or pair[1] not in records:
                raise ValueError("candidate module missing from inventory: %r" % (pair,))
            category, evidence, contradictions, score, rule, confidence = _classify(records[pair[0]], records[pair[1]], raw)
            analyses.append({
                "candidate_id": _sha256((pair[0] + "\0" + pair[1]).encode("utf-8"))[:20],
                "left": pair[0], "right": pair[1],
                "classification": category,
                "confidence": confidence,
                "combined_score": score,
                "evidence": evidence,
                "contradicting_evidence": sorted(set(contradictions)),
                "decision_rule": rule,
                "recommendation": {
                    "PROBABLE_REDUNDANCY": "human_review_before_any_merge_or_deprecation",
                    "PARTIAL_OVERLAP": "refine_responsibility_boundaries",
                    "HUMAN_REVIEW_REQUIRED": "manual_semantic_review_required",
                    "VIEW": "retain_and_document_view_relationship",
                    "ADAPTER": "retain_and_document_adapter_relationship",
                    "COMPLEMENTARY": "retain_and_document_complementarity",
                    "DISTINCT": "retain",
                }[category],
                "automatic_change_authorized": False,
            })

        analyses.sort(key=lambda item: (item["classification"], -item["combined_score"], item["left"], item["right"]))
        counts = Counter(item["classification"] for item in analyses)
        review = [item for item in analyses if item["classification"] in {"PROBABLE_REDUNDANCY", "PARTIAL_OVERLAP", "HUMAN_REVIEW_REQUIRED"}]

        graph: Dict[str, Set[str]] = defaultdict(set)
        for item in review:
            graph[item["left"]].add(item["right"])
            graph[item["right"]].add(item["left"])
        clusters: List[Dict[str, Any]] = []
        visited: Set[str] = set()
        for node in sorted(graph):
            if node in visited:
                continue
            stack, members = [node], []
            while stack:
                current = stack.pop()
                if current in visited:
                    continue
                visited.add(current)
                members.append(current)
                stack.extend(sorted(graph[current] - visited, reverse=True))
            member_set = set(members)
            ids = [item["candidate_id"] for item in review if item["left"] in member_set and item["right"] in member_set]
            clusters.append({"cluster_id": _sha256("\0".join(sorted(members)).encode("utf-8"))[:16], "modules": sorted(members), "candidate_ids": sorted(ids)})

        return {
            "schema_version": SCHEMA_VERSION,
            "status": STATUS,
            "source_fingerprint": fingerprint,
            "candidate_count": len(analyses),
            "classification_counts": {name: counts.get(name, 0) for name in CLASSES},
            "automatic_changes_made": False,
            "methodological_guard": "static evidence supports triage only; semantic human review is mandatory before merge, deletion, or deprecation",
            "calibration_guard": "lexical role markers are hints and never sufficient alone",
            "analyses": analyses,
            "review_queue": review,
            "clusters": sorted(clusters, key=lambda item: item["cluster_id"]),
        }

    def write(self, output_dir: Path | None = None) -> Dict[str, Any]:
        output = (output_dir or self.report_dir).resolve()
        result = self.build()
        files: Dict[str, bytes] = {}
        files["oif_redundancy_qualitative_analysis.json"] = _canonical_json({k: v for k, v in result.items() if k not in {"review_queue", "clusters"}})
        files["oif_redundancy_review_queue.json"] = _canonical_json({"schema_version": SCHEMA_VERSION, "source_fingerprint": result["source_fingerprint"], "items": result["review_queue"]})
        files["oif_redundancy_clusters.json"] = _canonical_json({"schema_version": SCHEMA_VERSION, "source_fingerprint": result["source_fingerprint"], "clusters": result["clusters"]})

        stream = io.StringIO(newline="")
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["candidate_id", "left", "right", "classification", "confidence", "combined_score", "decision_rule", "recommendation", "automatic_change_authorized"])
        for item in result["analyses"]:
            writer.writerow([item["candidate_id"], item["left"], item["right"], item["classification"], item["confidence"], "%.6f" % item["combined_score"], item["decision_rule"], item["recommendation"], "false"])
        files["oif_redundancy_evidence_matrix.csv"] = stream.getvalue().encode("utf-8")

        lines = [
            "# OIF-0 calibrated qualitative redundancy analysis", "",
            "Status: `%s`" % STATUS, "",
            "Candidates analyzed: **%d**" % result["candidate_count"], "",
            "No module was merged, deleted, deprecated, or rewritten.", "",
            "Lexical role markers are hints and never sufficient alone.", "",
            "## Classification counts", "",
        ]
        for name in CLASSES:
            lines.append("- `%s`: %d" % (name, result["classification_counts"][name]))
        lines.extend(["", "## Governance", "", result["methodological_guard"], ""])
        files["oif_redundancy_qualitative_report.md"] = ("\n".join(lines)).encode("utf-8")

        output.mkdir(parents=True, exist_ok=True)
        for name, data in files.items():
            _atomic_write(output / name, data)
        manifest = "".join("%s  %s\n" % (_sha256(files[name]), name) for name in sorted(files))
        _atomic_write(output / "oif_redundancy_qualitative_manifest.sha256", manifest.encode("utf-8"))
        return result

    def step(self, inputs: Mapping[str, Any] | None = None, persist: bool = False) -> Dict[str, Any]:
        inputs = dict(inputs or {})
        unknown = sorted(set(inputs) - {"output_dir"})
        if unknown:
            raise ValueError("unknown inputs: %s" % ", ".join(unknown))
        output = Path(inputs["output_dir"]).expanduser() if inputs.get("output_dir") else None
        if output is not None:
            output = output.resolve()
            try:
                output.relative_to(self.root)
            except ValueError as exc:
                raise ValueError("output_dir must remain inside repository root") from exc
        return self.write(output) if persist else self.build()
