\
"""AY1-D1a — deterministic documentary evidence extraction.

Extracts page text and observable cross-document title mentions. It never
creates, validates, or promotes a theoretical dependency relation.
"""
from __future__ import annotations

import hashlib
import importlib
import importlib.metadata
import json
import os
import re
import tempfile
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

PRIMITIVE = "DOCUMENTARY_EVIDENCE_EXTRACTOR"
STATUS_READY = "DOCUMENTARY_EVIDENCE_READY"
STATUS_DEGRADED = "DOCUMENTARY_EVIDENCE_DEGRADED"
PUBLIC_SCHEMA_VERSION = "1.0.0"
MATCH_TYPES = {"explicit_full_title_match", "normalized_title_match"}


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256(value: Any) -> str:
    return _sha256_bytes(_canonical(value).encode("utf-8"))


def _nfc(value: Any) -> str:
    return unicodedata.normalize("NFC", str(value or ""))


def _search_form(value: Any) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = unicodedata.normalize("NFC", text).casefold()
    text = re.sub(r"\\s+", " ", text).strip()
    return text


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _atomic_write(path: Path, content: str, filesystem_effect_context: Any, slot_prefix: str) -> None:
    if filesystem_effect_context is None:
        raise RuntimeError("governed filesystem effect context required")
    if not path.parent.exists():
        filesystem_effect_context.execute_path(slot_prefix + ":create_parent", "FS_CREATE_DIR", path.parent)
    filesystem_effect_context.execute_path(slot_prefix + ":write_replace", "FS_WRITE_REPLACE_BYTES", path, payload=content.encode("utf-8"))


def _backend() -> tuple[Any, str]:
    try:
        module = importlib.import_module("pypdf")
    except ImportError as exc:
        raise RuntimeError(
            "pypdf is required for PDF extraction; run install_ay1_d1_pdf_backend.py"
        ) from exc
    try:
        version = importlib.metadata.version("pypdf")
    except importlib.metadata.PackageNotFoundError:
        version = str(getattr(module, "__version__", "unknown"))
    return module, version


def _pdf_pages(path: Path) -> tuple[list[str], str, str]:
    pypdf, version = _backend()
    reader = pypdf.PdfReader(str(path), strict=False)
    pages = []
    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(_nfc(text).replace("\r\n", "\n").replace("\r", "\n"))
    return pages, "pypdf", version


def _documents(inputs: Mapping[str, Any]) -> list[dict[str, Any]]:
    raw = inputs.get("documents", [])
    if not isinstance(raw, list) or not all(isinstance(item, Mapping) for item in raw):
        raise TypeError("documents must be a list of mappings")
    docs = []
    for index, item in enumerate(raw):
        doc = dict(item)
        document_id = _nfc(doc.get("document_id") or doc.get("id")).strip()
        title = _nfc(doc.get("title")).strip()
        if not document_id or not title:
            raise ValueError(f"document {index} requires document_id and title")
        source_path = Path(str(doc.get("source_path", ""))).expanduser()
        page_texts = doc.get("page_texts")
        if page_texts is not None:
            if not isinstance(page_texts, list) or not all(isinstance(text, str) for text in page_texts):
                raise TypeError(f"document {index} page_texts must be a list of strings")
            pages = [_nfc(text).replace("\r\n", "\n").replace("\r", "\n") for text in page_texts]
            backend, backend_version = "synthetic", "1"
            document_sha256 = _nfc(doc.get("document_sha256")) or _sha256(pages)
        else:
            if not source_path.is_file():
                raise FileNotFoundError(f"document source missing: {source_path}")
            pages, backend, backend_version = _pdf_pages(source_path)
            document_sha256 = _sha256_bytes(source_path.read_bytes())
        docs.append({
            "document_id": document_id,
            "title": title,
            "source_path": str(source_path),
            "document_sha256": document_sha256,
            "pages": pages,
            "extraction_backend": backend,
            "backend_version": backend_version,
        })
    return sorted(docs, key=lambda item: item["document_id"])


def _excerpt(text: str, start: int, end: int, radius: int) -> tuple[str, int, int]:
    left = max(0, start - radius)
    right = min(len(text), end + radius)
    return text[left:right].strip(), left, right


def _evidence(docs: list[dict[str, Any]], radius: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    titles = [(doc["document_id"], doc["title"], _search_form(doc["title"])) for doc in docs]
    evidence: list[dict[str, Any]] = []
    pages: list[dict[str, Any]] = []
    for doc in docs:
        for page_number, original in enumerate(doc["pages"], start=1):
            normalized = _search_form(original)
            page_hash = _sha256_bytes(original.encode("utf-8"))
            pages.append({
                "document_id": doc["document_id"],
                "page_number": page_number,
                "page_text_sha256": page_hash,
                "character_count": len(original),
                "text_layer_present": bool(original.strip()),
            })
            for target_id, target_title, target_search in titles:
                if target_id == doc["document_id"] or not target_search:
                    continue
                cursor = 0
                while True:
                    found = normalized.find(target_search, cursor)
                    if found < 0:
                        break
                    # Character offsets apply to normalized searchable text; original excerpt
                    # is captured independently for integrity and review.
                    approx_start = min(len(original), found)
                    approx_end = min(len(original), found + len(target_search))
                    excerpt, excerpt_start, excerpt_end = _excerpt(original, approx_start, approx_end, radius)
                    identity = {
                        "document_id": doc["document_id"],
                        "page_number": page_number,
                        "referenced_document_id": target_id,
                        "match_start_normalized": found,
                        "match_end_normalized": found + len(target_search),
                        "excerpt_sha256": _sha256_bytes(excerpt.encode("utf-8")),
                    }
                    evidence.append({
                        "evidence_id": f"evidence:{_sha256(identity)[:24]}",
                        "document_id": doc["document_id"],
                        "document_sha256": doc["document_sha256"],
                        "page_number": page_number,
                        "page_text_sha256": page_hash,
                        "excerpt": excerpt,
                        "excerpt_sha256": identity["excerpt_sha256"],
                        "matched_title": target_title,
                        "referenced_document_id": target_id,
                        "match_type": "normalized_title_match",
                        "character_offsets": {
                            "normalized_start": found,
                            "normalized_end": found + len(target_search),
                            "excerpt_start_approx": excerpt_start,
                            "excerpt_end_approx": excerpt_end,
                        },
                        "extraction_backend": doc["extraction_backend"],
                        "backend_version": doc["backend_version"],
                        "relation_asserted": False,
                    })
                    cursor = found + max(1, len(target_search))
    unique = {item["evidence_id"]: item for item in evidence}
    return [unique[key] for key in sorted(unique)], sorted(pages, key=lambda item: (item["document_id"], item["page_number"]))


@dataclass
class DocumentaryEvidenceExtractor:
    root: Path | None = None

    def __post_init__(self) -> None:
        self.root = Path(self.root) if self.root is not None else Path.home() / "open-cognitive-ecology"

    def step(self, inputs: Mapping[str, Any] | None = None, persist: bool = False, filesystem_effect_context: Any = None) -> dict[str, Any]:
        supplied = dict(inputs or {})
        radius = int(supplied.get("excerpt_radius", 180))
        if radius < 40 or radius > 2000:
            raise ValueError("excerpt_radius must be between 40 and 2000")
        docs = _documents(supplied)
        evidence, pages = _evidence(docs, radius)
        pages_with_text = sum(1 for page in pages if page["text_layer_present"])
        degraded_reasons = []
        if not docs:
            degraded_reasons.append("no_documents")
        if docs and not pages:
            degraded_reasons.append("no_pages_extracted")
        if pages and pages_with_text == 0:
            degraded_reasons.append("no_text_layer_detected")
        status = STATUS_READY if not degraded_reasons else STATUS_DEGRADED
        core = {
            "schema_version": PUBLIC_SCHEMA_VERSION,
            "documents": [{key: doc[key] for key in (
                "document_id", "title", "source_path", "document_sha256",
                "extraction_backend", "backend_version"
            )} | {"page_count": len(doc["pages"])} for doc in docs],
            "pages": pages,
            "evidence": evidence,
            "ambiguous_references": [],
            "unresolved_documents": [doc["document_id"] for doc in docs if not any(
                item["document_id"] == doc["document_id"] for item in evidence
            )],
            "relation_generation_performed": False,
            "candidate_auto_promotion": False,
        }
        corpus_hash = _sha256(core)
        output_path = self.root / "theory_evolution" / "ay1_d1" / "documentary_evidence.json"
        result = {
            "primitive": PRIMITIVE,
            "status": status,
            "documentary_evidence_ready": status == STATUS_READY,
            "documentary_evidence": core,
            "documentary_evidence_hash": corpus_hash,
            "document_count": len(docs),
            "page_count": len(pages),
            "pages_with_text_count": pages_with_text,
            "evidence_count": len(evidence),
            "degraded_reasons": degraded_reasons,
            "persisted": False,
            "output_path": str(output_path),
            "timestamp_utc": supplied.get("timestamp_utc") or _utc_now(),
            "consciousness_proven": False,
            "subjectivity_proven": False,
            "qualia_proven": False,
            "phenomenology_proven": False,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
        }
        if persist:
            payload = dict(result)
            payload["persisted"] = True
            _atomic_write(output_path, json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n", filesystem_effect_context, "documentary_evidence")
            result["persisted"] = True
        return result
