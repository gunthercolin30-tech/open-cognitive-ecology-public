#!/usr/bin/env python3
"""AY1 real-corpus campaign.

Consumes the latest AY0 TheoryGraph, generates only candidate relations from
document-title overlap, optionally ingests manually validated relations, and
runs AY1 twice to verify determinism. Candidate relations are never promoted.

A successful campaign may legitimately produce an AY1 degraded graph when no
validated relation set has been supplied. This is a scientifically valid
negative result, not a software failure.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys
import tempfile
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

ROOT = Path.home() / "open-cognitive-ecology"
DEFAULT_AY0_CAMPAIGNS = ROOT / "theory_evolution" / "ay0" / "campaigns"
DEFAULT_OUTPUT = ROOT / "theory_evolution" / "ay1" / "campaigns"

STOPWORDS = {
    "a", "an", "and", "as", "au", "aux", "avec", "based", "de", "des", "du",
    "et", "for", "la", "le", "les", "of", "on", "sous", "the", "under", "with",
    "intelligence", "intelligences",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
        try:
            directory_fd = os.open(str(path.parent), os.O_RDONLY)
        except OSError:
            directory_fd = None
        if directory_fd is not None:
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
    finally:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass


def normalize_text(value: Any) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(char for char in text if not unicodedata.combining(char))
    return unicodedata.normalize("NFC", text).lower()


def title_tokens(title: Any) -> set[str]:
    tokens = set(re.findall(r"[a-z0-9]+", normalize_text(title)))
    return {token for token in tokens if len(token) >= 4 and token not in STOPWORDS}


def jaccard(left: set[str], right: set[str]) -> float:
    union = left | right
    if not union:
        return 0.0
    return len(left & right) / len(union)


def latest_ay0_graph(campaign_root: Path) -> Path:
    candidates = sorted(
        (path for path in campaign_root.glob("*/theory_graph.json") if path.is_file()),
        key=lambda path: path.parent.name,
    )
    if not candidates:
        raise FileNotFoundError(f"No AY0 theory_graph.json under {campaign_root}")
    return candidates[-1]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_relation_list(path: Path | None, forced_status: str) -> list[dict[str, Any]]:
    if path is None:
        return []
    payload = load_json(path)
    if isinstance(payload, Mapping):
        payload = payload.get("relations", [])
    if not isinstance(payload, list) or not all(isinstance(item, Mapping) for item in payload):
        raise TypeError(f"{path} must contain a list of relation objects")
    result: list[dict[str, Any]] = []
    for item in payload:
        record = dict(item)
        existing = str(record.get("status", forced_status)).strip().lower()
        if existing != forced_status:
            raise ValueError(f"{path}: relation status must be {forced_status!r}")
        record["status"] = forced_status
        if forced_status == "validated" and not record.get("evidence"):
            raise ValueError(f"{path}: every validated relation requires explicit evidence")
        result.append(record)
    return result


def candidate_relations_from_titles(
    theory_graph: Mapping[str, Any],
    threshold: float,
) -> list[dict[str, Any]]:
    nodes = theory_graph.get("nodes", [])
    prepared = [
        (str(node["id"]), str(node.get("title", "")), title_tokens(node.get("title", "")))
        for node in nodes
        if isinstance(node, Mapping) and node.get("id")
    ]
    candidates: list[dict[str, Any]] = []
    for index, (left_id, left_title, left_tokens) in enumerate(prepared):
        for right_id, right_title, right_tokens in prepared[index + 1:]:
            score = jaccard(left_tokens, right_tokens)
            if score < threshold:
                continue
            # Direction is canonical only for storage determinism; no theoretical
            # direction is asserted by lexical similarity.
            source, target = sorted((left_id, right_id))
            evidence = (
                f"title_token_overlap:jaccard={score:.6f};"
                f"left={left_title!r};right={right_title!r}"
            )
            candidates.append({
                "source": source,
                "target": target,
                "relation": "supports",
                "status": "candidate",
                "confidence": round(score, 12),
                "evidence": [evidence],
                "provenance": "ay1_title_overlap_candidate",
            })
    return sorted(
        candidates,
        key=lambda item: (
            item["source"], item["target"], item["relation"],
            canonical(item.get("evidence", [])),
        ),
    )


def markdown_report(report: Mapping[str, Any]) -> str:
    metrics = report["metrics"]
    verification = report["verification"]
    lines = [
        "# AY1 — Real Corpus Campaign Evidence",
        "",
        f"- Campaign ID: `{report['campaign_id']}`",
        f"- Scientific status: `{report['scientific_status']}`",
        f"- AY1 runtime status: `{report['ay1_runtime_status']}`",
        f"- Verification valid: `{str(verification['valid']).lower()}`",
        f"- Dependency graph hash: `{report['theory_dependency_graph_hash']}`",
        "",
        "## Metrics",
        "",
    ]
    for key in sorted(metrics):
        lines.append(f"- `{key}`: `{metrics[key]}`")
    lines.extend(["", "## Verification", ""])
    for key in sorted(verification):
        lines.append(f"- `{key}`: `{verification[key]}`")
    lines.extend([
        "",
        "## Scientific interpretation",
        "",
        "- Candidate relations remain hypotheses only.",
        "- No candidate relation was automatically promoted.",
        "- AY1 is corpus-ready only when explicit validated relations are supplied.",
        "- A degraded graph with zero validated edges is an admissible negative result.",
        "",
    ])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ay0-theory-graph", type=Path, default=None)
    parser.add_argument("--ay0-campaign-root", type=Path, default=DEFAULT_AY0_CAMPAIGNS)
    parser.add_argument("--validated-relations", type=Path, default=None)
    parser.add_argument("--candidate-relations", type=Path, default=None)
    parser.add_argument("--title-overlap-threshold", type=float, default=0.25)
    parser.add_argument("--campaign-id", default=None)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    threshold = float(args.title_overlap_threshold)
    if not math.isfinite(threshold) or not 0.0 <= threshold <= 1.0:
        raise ValueError("title-overlap-threshold must be finite and in [0, 1]")

    graph_path = (
        args.ay0_theory_graph.expanduser().resolve(strict=True)
        if args.ay0_theory_graph is not None
        else latest_ay0_graph(args.ay0_campaign_root.expanduser().resolve(strict=True))
    )
    theory_graph = load_json(graph_path)
    if not isinstance(theory_graph, Mapping):
        raise TypeError("AY0 theory graph must be a JSON object")

    validated = load_relation_list(args.validated_relations, "validated")
    supplied_candidates = load_relation_list(args.candidate_relations, "candidate")
    generated_candidates = candidate_relations_from_titles(theory_graph, threshold)

    relation_identity: set[str] = set()
    relations: list[dict[str, Any]] = []
    for record in validated + supplied_candidates + generated_candidates:
        identity = sha256_text({
            "source": record.get("source"),
            "target": record.get("target"),
            "relation": record.get("relation"),
            "status": record.get("status"),
            "evidence": sorted(record.get("evidence", [])),
        })
        if identity not in relation_identity:
            relation_identity.add(identity)
            relations.append(record)

    sys.path.insert(0, str(ROOT))
    from ontology.theory_dependency_graph import TheoryDependencyGraph

    started = utc_now()
    campaign_id = args.campaign_id or datetime.now(timezone.utc).strftime(
        "ay1-real-%Y%m%dT%H%M%SZ"
    )

    source_hash_before = sha256_file(graph_path)
    with tempfile.TemporaryDirectory(prefix="oce_ay1_real_") as temp:
        base = Path(temp)
        first_inputs = {
            "theory_graph": theory_graph,
            "relations": relations,
            "timestamp_utc": "2000-01-01T00:00:00Z",
        }
        second_inputs = {
            "relations": list(reversed(relations)),
            "timestamp_utc": "2000-01-01T00:00:00Z",
            "theory_graph": theory_graph,
        }
        first = TheoryDependencyGraph(root=base / "run_a").step(
            inputs=first_inputs,
            persist=False,
        )
        second = TheoryDependencyGraph(root=base / "run_b").step(
            inputs=second_inputs,
            persist=False,
        )
    source_hash_after = sha256_file(graph_path)

    dependency_graph = first["theory_dependency_graph"]
    no_auto_promotion = (
        dependency_graph["candidate_auto_promotion"] is False
        and all(edge["status"] == "candidate" for edge in dependency_graph["candidate_edges"])
        and all(edge["status"] == "validated" for edge in dependency_graph["validated_edges"])
    )
    expected_ready = len(validated) > 0
    status_matches_evidence = (
        first["dependency_graph_ready"] is expected_ready
        and (
            first["status"] == "THEORY_DEPENDENCY_GRAPH_READY"
            if expected_ready
            else first["status"] == "THEORY_DEPENDENCY_GRAPH_DEGRADED"
        )
    )

    verification = {
        "valid": True,
        "deterministic_hash": (
            first["theory_dependency_graph_hash"]
            == second["theory_dependency_graph_hash"]
        ),
        "deterministic_graph": (
            canonical(first["theory_dependency_graph"])
            == canonical(second["theory_dependency_graph"])
        ),
        "ay0_input_unchanged": source_hash_before == source_hash_after,
        "candidate_auto_promotion_forbidden": no_auto_promotion,
        "status_matches_validated_evidence": status_matches_evidence,
        "functional_only": first["functional_conclusion_only"] is True,
        "phenomenology_undetermined": first["phenomenology_undetermined"] is True,
    }
    verification["valid"] = all(
        value is True for key, value in verification.items() if key != "valid"
    )

    scientific_status = (
        "THEORY_DEPENDENCY_GRAPH_READY"
        if first["dependency_graph_ready"]
        else "DEGRADED_NO_VALIDATED_RELATIONS"
    )
    metrics = {
        "node_count": first["node_count"],
        "validated_edge_count": first["validated_edge_count"],
        "candidate_edge_count": first["candidate_edge_count"],
        "generated_title_candidate_count": len(generated_candidates),
        "supplied_candidate_count": len(supplied_candidates),
        "supplied_validated_count": len(validated),
        "duplicate_record_count": len(dependency_graph["duplicate_records"]),
        "validated_cycle_detected": dependency_graph["validated_cycle_detected"],
    }

    report = {
        "primitive": "AY1_REAL_CORPUS_CAMPAIGN",
        "campaign_id": campaign_id,
        "started_utc": started,
        "completed_utc": utc_now(),
        "scientific_status": scientific_status,
        "ay1_runtime_status": first["status"],
        "dependency_graph_ready": first["dependency_graph_ready"],
        "theory_dependency_graph_hash": first["theory_dependency_graph_hash"],
        "theory_dependency_graph_schema_version": dependency_graph["schema_version"],
        "ay0_theory_graph_path": str(graph_path),
        "ay0_theory_graph_sha256": source_hash_before,
        "metrics": metrics,
        "verification": verification,
        "theory_dependency_graph": dependency_graph,
        "epistemic_invariants": {
            "consciousness_proven": first["consciousness_proven"],
            "subjectivity_proven": first["subjectivity_proven"],
            "qualia_proven": first["qualia_proven"],
            "phenomenology_proven": first["phenomenology_proven"],
            "functional_conclusion_only": first["functional_conclusion_only"],
            "phenomenology_undetermined": first["phenomenology_undetermined"],
        },
    }

    output_dir = args.output_root.expanduser().resolve(strict=False) / campaign_id
    report_json = output_dir / "ay1_real_corpus_campaign_report.json"
    report_md = output_dir / "ay1_real_corpus_campaign_report.md"
    graph_json = output_dir / "theory_dependency_graph.json"
    manifest_json = output_dir / "evidence_manifest.json"

    atomic_write(
        report_json,
        json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
    )
    atomic_write(report_md, markdown_report(report))
    atomic_write(
        graph_json,
        json.dumps(dependency_graph, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
    )

    evidence_files = [
        {"path": report_json.name, "sha256": sha256_file(report_json)},
        {"path": report_md.name, "sha256": sha256_file(report_md)},
        {"path": graph_json.name, "sha256": sha256_file(graph_json)},
    ]
    manifest = {
        "campaign_id": campaign_id,
        "files": evidence_files,
        "manifest_hash": sha256_text(evidence_files),
    }
    atomic_write(
        manifest_json,
        json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
    )

    print("AY1 real corpus campaign")
    print(f"- campaign_id: {campaign_id}")
    print(f"- output_dir: {output_dir}")
    print(f"- ay1_runtime_status: {first['status']}")
    print(f"- scientific_status: {scientific_status}")
    print(f"- node_count: {metrics['node_count']}")
    print(f"- validated_edge_count: {metrics['validated_edge_count']}")
    print(f"- candidate_edge_count: {metrics['candidate_edge_count']}")
    print(f"- theory_dependency_graph_hash: {first['theory_dependency_graph_hash']}")
    print(f"- verification.valid: {str(verification['valid']).lower()}")
    if verification["valid"]:
        print("AY1_REAL_CORPUS_CAMPAIGN_OK")
        return 0
    print("AY1_REAL_CORPUS_CAMPAIGN_FAILED")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
