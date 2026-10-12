\
"""AY0 — deterministic, observational audit of a theoretical corpus.

The primitive builds a canonical TheoryGraph from source documents and optional
structured scientific records. It never revises, accepts or replaces a theory.
PDF contents are not guessed: without structured records they remain source
nodes only. This preserves epistemic traceability for AY1–AY20.
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

PRIMITIVE = "THEORY_CORPUS_AUDITOR"
STATUS_READY = "THEORY_CORPUS_AUDITED"
STATUS_DEGRADED = "THEORY_CORPUS_AUDIT_DEGRADED"
PUBLIC_SCHEMA_VERSION = "1.0.0"
ALLOWED_KINDS = {
    "article", "book", "chapter", "axiom", "definition", "theorem",
    "lemma", "proof", "assumption", "source_document", "derived_artifact",
    "infrastructure_artifact",
}
TEXT_SUFFIXES = {".txt", ".md", ".tex", ".json", ".yaml", ".yml"}
SOURCE_SUFFIXES = TEXT_SUFFIXES | {".pdf"}


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256(value: Any) -> str:
    return _sha256_bytes(_canonical(value).encode("utf-8"))


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _norm_text(value: Any) -> str:
    return unicodedata.normalize("NFC", str(value or "")).strip()


def _safe_relpath(path: Path, root: Path) -> str:
    resolved = path.resolve(strict=False)
    base = root.resolve(strict=False)
    try:
        return resolved.relative_to(base).as_posix()
    except ValueError:
        return resolved.as_posix()


def _is_hidden_or_macos(path: Path) -> bool:
    return any(part.startswith(".") or part == "__MACOSX" for part in path.parts)


def _atomic_write(path: Path, content: str, filesystem_effect_context: Any, slot_prefix: str) -> None:
    if filesystem_effect_context is None:
        raise RuntimeError("governed filesystem effect context required")
    if not path.parent.exists():
        filesystem_effect_context.execute_path(slot_prefix + ":create_parent", "FS_CREATE_DIR", path.parent)
    filesystem_effect_context.execute_path(slot_prefix + ":write_replace", "FS_WRITE_REPLACE_BYTES", path, payload=content.encode("utf-8"))


def _classify_path(path: Path) -> str:
    lower_parts = {part.lower() for part in path.parts}
    stem = path.stem.lower()
    if any(token in lower_parts or token in stem for token in ("report", "reports", "dashboard", "certification", "simulation")):
        return "derived_artifact"
    if any(token in lower_parts or token in stem for token in ("schema", "schemas", "manifest", "manifests", "inventory", "index", "indexes")):
        return "infrastructure_artifact"
    return "source_document"


def _document_node(path: Path, corpus_root: Path) -> dict[str, Any]:
    data = path.read_bytes()
    rel = _safe_relpath(path, corpus_root)
    digest = _sha256_bytes(data)
    return {
        "id": f"doc:{digest[:24]}",
        "kind": _classify_path(path),
        "title": _norm_text(path.stem),
        "source_path": rel,
        "sha256": digest,
        "size_bytes": len(data),
        "format": path.suffix.lower().lstrip("."),
        "provenance": "filesystem",
    }


def _record_node(record: Mapping[str, Any], index: int) -> dict[str, Any]:
    kind = _norm_text(record.get("kind")).lower()
    if kind not in ALLOWED_KINDS:
        raise ValueError(f"unsupported record kind at index {index}: {kind!r}")
    title = _norm_text(record.get("title") or record.get("name"))
    statement = _norm_text(record.get("statement") or record.get("content"))
    source_id = _norm_text(record.get("source_id"))
    if not title and not statement:
        raise ValueError(f"record {index} requires title/name or statement/content")
    identity = {"kind": kind, "title": title, "statement": statement, "source_id": source_id}
    node_id = _norm_text(record.get("id")) or f"record:{_sha256(identity)[:24]}"
    return {
        "id": node_id,
        "kind": kind,
        "title": title,
        "statement": statement,
        "source_id": source_id or None,
        "confidence": record.get("confidence"),
        "provenance": _norm_text(record.get("provenance")) or "structured_input",
    }


def _deduplicate(nodes: Iterable[Mapping[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    kept: dict[str, dict[str, Any]] = {}
    duplicates: list[dict[str, Any]] = []
    for raw in nodes:
        node = dict(raw)
        node_id = str(node["id"])
        if node_id in kept:
            if _canonical(kept[node_id]) != _canonical(node):
                raise ValueError(f"conflicting duplicate node id: {node_id}")
            duplicates.append({"id": node_id, "reason": "exact_duplicate_id"})
            continue
        kept[node_id] = node
    return [kept[key] for key in sorted(kept)], duplicates


@dataclass
class TheoryCorpusAuditor:
    root: Path | None = None

    def __post_init__(self) -> None:
        self.root = Path(self.root) if self.root is not None else Path.home() / "open-cognitive-ecology"

    def _discover(self, corpus_roots: Iterable[Any]) -> tuple[list[dict[str, Any]], list[str]]:
        nodes: list[dict[str, Any]] = []
        warnings: list[str] = []
        roots = sorted({Path(value).expanduser().resolve(strict=False) for value in corpus_roots}, key=str)
        for corpus_root in roots:
            if not corpus_root.is_dir():
                warnings.append(f"missing_corpus_root:{corpus_root}")
                continue
            for path in sorted(corpus_root.rglob("*"), key=lambda p: p.as_posix()):
                if not path.is_file() or _is_hidden_or_macos(path.relative_to(corpus_root)):
                    continue
                if path.suffix.lower() not in SOURCE_SUFFIXES:
                    continue
                try:
                    nodes.append(_document_node(path, corpus_root))
                except OSError as exc:
                    warnings.append(f"unreadable:{_safe_relpath(path, corpus_root)}:{exc.__class__.__name__}")
        return nodes, warnings

    def step(self, inputs: Mapping[str, Any] | None = None, persist: bool = False, filesystem_effect_context: Any = None) -> dict[str, Any]:
        supplied = dict(inputs or {})
        roots = supplied.get("corpus_roots", [])
        if isinstance(roots, (str, bytes, Path)):
            roots = [roots]
        records = supplied.get("records", [])
        if not isinstance(records, list):
            raise TypeError("records must be a list")
        discovered, warnings = self._discover(roots)
        structured = [_record_node(record, index) for index, record in enumerate(records) if isinstance(record, Mapping)]
        if len(structured) != len(records):
            raise TypeError("every record must be a mapping")
        nodes, duplicates = _deduplicate(discovered + structured)
        counts = {kind: 0 for kind in sorted(ALLOWED_KINDS)}
        for node in nodes:
            counts[node["kind"]] = counts.get(node["kind"], 0) + 1
        source_count = sum(counts.get(kind, 0) for kind in ("source_document", "article", "book", "chapter"))
        degraded_reasons: list[str] = []
        if not nodes:
            degraded_reasons.append("empty_theory_graph")
        if source_count == 0:
            degraded_reasons.append("no_primary_source_nodes")
        status = STATUS_READY if not degraded_reasons else STATUS_DEGRADED
        graph_core = {
            "schema_version": PUBLIC_SCHEMA_VERSION,
            "nodes": nodes,
            "edges": [],
            "node_counts": counts,
            "duplicate_records": duplicates,
            "warnings": sorted(warnings),
        }
        graph_hash = _sha256(graph_core)
        result = {
            "primitive": PRIMITIVE,
            "status": status,
            "audit_completed": status == STATUS_READY,
            "theory_graph": graph_core,
            "theory_graph_hash": graph_hash,
            "node_count": len(nodes),
            "source_count": source_count,
            "structured_claim_count": sum(counts.get(k, 0) for k in ("axiom", "definition", "theorem", "lemma", "proof", "assumption")),
            "degraded_reasons": degraded_reasons,
            "persisted": False,
            "output_path": str(self.root / "theory_evolution" / "ay0" / "theory_graph.json"),
            "timestamp_utc": supplied.get("timestamp_utc") or _utc_now(),
            "consciousness_proven": False,
            "subjectivity_proven": False,
            "qualia_proven": False,
            "phenomenology_proven": False,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
        }
        if persist:
            output = Path(result["output_path"])
            payload = dict(result)
            payload["persisted"] = True
            _atomic_write(output, json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n", filesystem_effect_context, "theory_corpus_audit")
            result["persisted"] = True
        return result
