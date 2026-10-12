\
#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path.home() / "open-cognitive-ecology"


def sha256_file(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""): h.update(chunk)
    return h.hexdigest()


def atomic_write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text); handle.flush(); os.fsync(handle.fileno())
        os.replace(name, path)
    finally:
        try: os.unlink(name)
        except FileNotFoundError: pass


def latest_graph():
    paths = sorted((ROOT / "theory_evolution" / "ay0" / "campaigns").glob("*/theory_graph.json"))
    if not paths: raise FileNotFoundError("No AY0 theory_graph.json found")
    return paths[-1]


def main():
    from ontology.documentary_evidence_extractor import DocumentaryEvidenceExtractor
    graph_path = latest_graph()
    graph = json.loads(graph_path.read_text(encoding="utf-8"))
    corpus = ROOT / "gunther_corpus"
    documents = []
    for node in graph["nodes"]:
        source = corpus / node["source_path"]
        if not source.is_file(): raise FileNotFoundError(source)
        documents.append({"document_id": node["id"], "title": node["title"], "source_path": str(source)})
    before = {str(Path(doc["source_path"])): sha256_file(Path(doc["source_path"])) for doc in documents}
    with tempfile.TemporaryDirectory(prefix="oce_ay1_d1_real_") as tmp:
        a = DocumentaryEvidenceExtractor(root=Path(tmp) / "a").step(inputs={"documents": documents, "timestamp_utc": "2000-01-01T00:00:00Z"}, persist=False)
        b = DocumentaryEvidenceExtractor(root=Path(tmp) / "b").step(inputs={"documents": list(reversed(documents)), "timestamp_utc": "2000-01-01T00:00:00Z"}, persist=False)
    after = {str(Path(doc["source_path"])): sha256_file(Path(doc["source_path"])) for doc in documents}
    verification = {
        "valid": True,
        "deterministic_hash": a["documentary_evidence_hash"] == b["documentary_evidence_hash"],
        "deterministic_payload": a["documentary_evidence"] == b["documentary_evidence"],
        "source_inputs_unchanged": before == after,
        "relation_generation_forbidden": a["documentary_evidence"]["relation_generation_performed"] is False,
        "candidate_auto_promotion_forbidden": a["documentary_evidence"]["candidate_auto_promotion"] is False,
        "functional_only": a["functional_conclusion_only"] is True,
        "phenomenology_undetermined": a["phenomenology_undetermined"] is True,
    }
    verification["valid"] = all(v is True for k, v in verification.items() if k != "valid")
    campaign_id = datetime.now(timezone.utc).strftime("ay1-d1-real-%Y%m%dT%H%M%SZ")
    out = ROOT / "theory_evolution" / "ay1_d1" / "campaigns" / campaign_id
    report = {
        "primitive": "AY1_D1_REAL_DOCUMENTARY_CAMPAIGN",
        "campaign_id": campaign_id,
        "status": a["status"],
        "documentary_evidence_hash": a["documentary_evidence_hash"],
        "metrics": {k: a[k] for k in ("document_count", "page_count", "pages_with_text_count", "evidence_count")},
        "verification": verification,
        "documentary_evidence": a["documentary_evidence"],
    }
    report_json = out / "ay1_d1_documentary_campaign_report.json"
    evidence_json = out / "documentary_evidence.json"
    coverage_json = out / "extraction_coverage_report.json"
    manifest_json = out / "documentary_evidence_manifest.json"
    atomic_write(report_json, json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    atomic_write(evidence_json, json.dumps(a["documentary_evidence"]["evidence"], ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    atomic_write(coverage_json, json.dumps({"documents": a["documentary_evidence"]["documents"], "pages": a["documentary_evidence"]["pages"], "unresolved_documents": a["documentary_evidence"]["unresolved_documents"]}, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    files = [{"path": p.name, "sha256": sha256_file(p)} for p in (report_json, evidence_json, coverage_json)]
    atomic_write(manifest_json, json.dumps({"campaign_id": campaign_id, "files": files}, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    print("AY1-D1 real documentary campaign")
    print(f"- campaign_id: {campaign_id}")
    print(f"- status: {a['status']}")
    print(f"- document_count: {a['document_count']}")
    print(f"- page_count: {a['page_count']}")
    print(f"- pages_with_text_count: {a['pages_with_text_count']}")
    print(f"- evidence_count: {a['evidence_count']}")
    print(f"- verification.valid: {str(verification['valid']).lower()}")
    print("AY1_D1_REAL_DOCUMENTARY_CAMPAIGN_OK" if verification["valid"] else "AY1_D1_REAL_DOCUMENTARY_CAMPAIGN_FAILED")
    raise SystemExit(0 if verification["valid"] else 1)


if __name__ == "__main__": main()
