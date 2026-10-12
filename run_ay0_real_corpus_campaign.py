#!/usr/bin/env python3
"""AY0 real-corpus campaign runner.

Reads corpus roots and ZIP archives without modifying them, runs
TheoryCorpusAuditor in a temporary validation root, checks determinism and
source immutability, then atomically publishes evidence reports under
theory_evolution/ay0/campaigns/<campaign_id>/.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

ROOT = Path.home() / "open-cognitive-ecology"
ALLOWED_SUFFIXES = {".pdf", ".txt", ".md", ".tex", ".json", ".yaml", ".yml"}
MAX_MEMBER_BYTES = 512 * 1024 * 1024
MAX_TOTAL_BYTES = 4 * 1024 * 1024 * 1024


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


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


def safe_rel(path: Path, root: Path) -> str:
    try:
        return path.resolve(strict=False).relative_to(root.resolve(strict=False)).as_posix()
    except ValueError:
        return path.resolve(strict=False).as_posix()


def source_files(root: Path) -> list[Path]:
    if not root.is_dir():
        return []
    files: list[Path] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if any(part.startswith(".") or part == "__MACOSX" for part in relative.parts):
            continue
        if path.suffix.lower() in ALLOWED_SUFFIXES:
            files.append(path)
    return files


def manifest_for_roots(roots: Iterable[Path]) -> list[dict[str, Any]]:
    manifest: list[dict[str, Any]] = []
    for root in sorted({path.resolve(strict=False) for path in roots}, key=str):
        for path in source_files(root):
            stat = path.stat()
            manifest.append({
                "root": str(root),
                "path": safe_rel(path, root),
                "size_bytes": stat.st_size,
                "sha256": sha256_file(path),
            })
    return manifest


def validate_zip_member(info: zipfile.ZipInfo, destination: Path) -> None:
    name = info.filename.replace("\\", "/")
    pure = Path(name)
    if pure.is_absolute() or ".." in pure.parts:
        raise ValueError(f"unsafe ZIP member path: {name}")
    if info.file_size > MAX_MEMBER_BYTES:
        raise ValueError(f"ZIP member too large: {name}")
    mode = (info.external_attr >> 16) & 0o170000
    if mode == 0o120000:
        raise ValueError(f"ZIP symlink refused: {name}")
    target = (destination / pure).resolve(strict=False)
    try:
        target.relative_to(destination.resolve(strict=False))
    except ValueError as exc:
        raise ValueError(f"ZIP member escapes destination: {name}") from exc


def extract_zip_safely(archive: Path, destination: Path) -> Path:
    total = 0
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as zf:
        members = sorted(zf.infolist(), key=lambda info: info.filename)
        for info in members:
            validate_zip_member(info, destination)
            total += info.file_size
            if total > MAX_TOTAL_BYTES:
                raise ValueError("ZIP uncompressed total exceeds safety limit")
        for info in members:
            name = info.filename.replace("\\", "/")
            target = destination / Path(name)
            if info.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info, "r") as source, target.open("wb") as sink:
                shutil.copyfileobj(source, sink, length=1024 * 1024)
    return destination


def load_records(path: Path | None) -> list[dict[str, Any]]:
    if path is None:
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        payload = payload.get("records", [])
    if not isinstance(payload, list) or not all(isinstance(item, dict) for item in payload):
        raise TypeError("records JSON must be a list of objects or {'records': [...]}")
    return payload


def discover_defaults() -> tuple[list[Path], list[Path]]:
    directories: list[Path] = []
    archives: list[Path] = []
    candidates = [
        ROOT / "gunther_corpus",
        ROOT / "theory_corpus",
        ROOT / "corpus",
        Path.home() / "Downloads" / "gunther_corpus",
        Path.home() / "Downloads" / "gunther_corpus.zip",
        Path.home() / "Desktop" / "gunther_corpus",
        Path.home() / "Desktop" / "gunther_corpus.zip",
    ]
    for candidate in candidates:
        if candidate.is_dir():
            directories.append(candidate)
        elif candidate.is_file() and candidate.suffix.lower() == ".zip":
            archives.append(candidate)
    return directories, archives


def markdown_report(report: dict[str, Any]) -> str:
    metrics = report["metrics"]
    lines = [
        "# AY0 — Real Corpus Campaign Evidence",
        "",
        f"- Campaign ID: `{report['campaign_id']}`",
        f"- Started UTC: `{report['started_utc']}`",
        f"- Completed UTC: `{report['completed_utc']}`",
        f"- Verification valid: `{str(report['verification']['valid']).lower()}`",
        f"- Theory graph hash: `{report['theory_graph_hash']}`",
        "",
        "## Metrics",
        "",
    ]
    for key in sorted(metrics):
        lines.append(f"- `{key}`: `{metrics[key]}`")
    lines.extend([
        "",
        "## Verification",
        "",
    ])
    for key in sorted(report["verification"]):
        lines.append(f"- `{key}`: `{report['verification'][key]}`")
    lines.extend([
        "",
        "## Epistemic invariants",
        "",
    ])
    for key in sorted(report["epistemic_invariants"]):
        lines.append(f"- `{key}`: `{report['epistemic_invariants'][key]}`")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus-root", action="append", default=[], help="Read-only corpus directory; repeatable")
    parser.add_argument("--corpus-zip", action="append", default=[], help="Read-only corpus ZIP; repeatable")
    parser.add_argument("--records-json", type=Path, default=None, help="Optional structured AY0 records")
    parser.add_argument("--campaign-id", default=None)
    parser.add_argument("--output-root", type=Path, default=ROOT / "theory_evolution" / "ay0" / "campaigns")
    args = parser.parse_args()

    explicit_roots = [Path(value).expanduser().resolve(strict=False) for value in args.corpus_root]
    explicit_zips = [Path(value).expanduser().resolve(strict=False) for value in args.corpus_zip]
    if not explicit_roots and not explicit_zips:
        explicit_roots, explicit_zips = discover_defaults()

    missing = [str(path) for path in explicit_roots if not path.is_dir()]
    missing += [str(path) for path in explicit_zips if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing corpus inputs: " + ", ".join(missing))
    if not explicit_roots and not explicit_zips:
        raise FileNotFoundError(
            "no corpus found; pass --corpus-root PATH or --corpus-zip PATH"
        )

    sys.path.insert(0, str(ROOT))
    from ontology.theory_corpus_auditor import TheoryCorpusAuditor

    started = utc_now()
    campaign_id = args.campaign_id or datetime.now(timezone.utc).strftime("ay0-real-%Y%m%dT%H%M%SZ")
    records = load_records(args.records_json)

    original_manifest_before = manifest_for_roots(explicit_roots)
    archive_manifest_before = [
        {"path": str(path), "size_bytes": path.stat().st_size, "sha256": sha256_file(path)}
        for path in sorted(explicit_zips, key=str)
    ]

    with tempfile.TemporaryDirectory(prefix="oce_ay0_real_campaign_") as temp:
        temp_root = Path(temp)
        extracted_roots: list[Path] = []
        for index, archive in enumerate(sorted(explicit_zips, key=str)):
            destination = temp_root / "extracted" / f"{index:03d}_{archive.stem}"
            extracted_roots.append(extract_zip_safely(archive, destination))

        audit_roots = explicit_roots + extracted_roots
        input_payload = {
            "corpus_roots": audit_roots,
            "records": records,
            "timestamp_utc": "2000-01-01T00:00:00Z",
        }
        first = TheoryCorpusAuditor(root=temp_root / "run_a").step(inputs=input_payload, persist=False)
        second = TheoryCorpusAuditor(root=temp_root / "run_b").step(
            inputs={
                "records": list(records),
                "timestamp_utc": "2000-01-01T00:00:00Z",
                "corpus_roots": list(reversed(audit_roots)),
            },
            persist=False,
        )

        original_manifest_after = manifest_for_roots(explicit_roots)
        archive_manifest_after = [
            {"path": str(path), "size_bytes": path.stat().st_size, "sha256": sha256_file(path)}
            for path in sorted(explicit_zips, key=str)
        ]

        graph = first["theory_graph"]
        counts = graph["node_counts"]
        verification = {
            "valid": True,
            "status_ready": first["status"] == "THEORY_CORPUS_AUDITED",
            "audit_completed": first["audit_completed"] is True,
            "deterministic_hash": first["theory_graph_hash"] == second["theory_graph_hash"],
            "deterministic_graph": canonical(first["theory_graph"]) == canonical(second["theory_graph"]),
            "source_inputs_unchanged": original_manifest_before == original_manifest_after,
            "zip_inputs_unchanged": archive_manifest_before == archive_manifest_after,
            "edges_empty_for_ay0": graph.get("edges") == [],
            "functional_only": first.get("functional_conclusion_only") is True,
            "phenomenology_undetermined": first.get("phenomenology_undetermined") is True,
        }
        verification["valid"] = all(
            value is True for key, value in verification.items() if key != "valid"
        )

        metrics = {
            "node_count": first["node_count"],
            "source_count": first["source_count"],
            "structured_claim_count": first["structured_claim_count"],
            "duplicate_count": len(graph.get("duplicate_records", [])),
            "warning_count": len(graph.get("warnings", [])),
            "source_document_count": counts.get("source_document", 0),
            "article_count": counts.get("article", 0),
            "book_count": counts.get("book", 0),
            "chapter_count": counts.get("chapter", 0),
            "axiom_count": counts.get("axiom", 0),
            "definition_count": counts.get("definition", 0),
            "theorem_count": counts.get("theorem", 0),
            "lemma_count": counts.get("lemma", 0),
            "proof_count": counts.get("proof", 0),
            "assumption_count": counts.get("assumption", 0),
            "derived_artifact_count": counts.get("derived_artifact", 0),
            "infrastructure_artifact_count": counts.get("infrastructure_artifact", 0),
            "input_directory_count": len(explicit_roots),
            "input_zip_count": len(explicit_zips),
        }

        report = {
            "primitive": "AY0_REAL_CORPUS_CAMPAIGN",
            "campaign_id": campaign_id,
            "started_utc": started,
            "completed_utc": utc_now(),
            "verification": verification,
            "metrics": metrics,
            "theory_graph_hash": first["theory_graph_hash"],
            "theory_graph_schema_version": graph.get("schema_version"),
            "input_directories": [str(path) for path in explicit_roots],
            "input_archives": archive_manifest_before,
            "source_manifest": original_manifest_before,
            "theory_graph": graph,
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
    report_json = output_dir / "ay0_real_corpus_campaign_report.json"
    report_md = output_dir / "ay0_real_corpus_campaign_report.md"
    graph_json = output_dir / "theory_graph.json"
    manifest_json = output_dir / "evidence_manifest.json"

    atomic_write(report_json, json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    atomic_write(report_md, markdown_report(report))
    atomic_write(graph_json, json.dumps(report["theory_graph"], ensure_ascii=False, sort_keys=True, indent=2) + "\n")

    evidence_manifest = {
        "campaign_id": campaign_id,
        "files": [
            {"path": report_json.name, "sha256": sha256_file(report_json)},
            {"path": report_md.name, "sha256": sha256_file(report_md)},
            {"path": graph_json.name, "sha256": sha256_file(graph_json)},
        ],
    }
    evidence_manifest["manifest_hash"] = sha256_bytes(canonical(evidence_manifest["files"]).encode("utf-8"))
    atomic_write(manifest_json, json.dumps(evidence_manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n")

    print("AY0 real corpus campaign")
    print(f"- campaign_id: {campaign_id}")
    print(f"- output_dir: {output_dir}")
    print(f"- status: {first['status']}")
    print(f"- node_count: {metrics['node_count']}")
    print(f"- source_count: {metrics['source_count']}")
    print(f"- structured_claim_count: {metrics['structured_claim_count']}")
    print(f"- duplicate_count: {metrics['duplicate_count']}")
    print(f"- warning_count: {metrics['warning_count']}")
    print(f"- theory_graph_hash: {report['theory_graph_hash']}")
    print(f"- verification.valid: {str(verification['valid']).lower()}")
    if verification["valid"]:
        print("AY0_REAL_CORPUS_CAMPAIGN_OK")
        return 0
    print("AY0_REAL_CORPUS_CAMPAIGN_FAILED")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
