"""Deterministic, read-only baseline auditor for OCE Interface Fabric (OIF-0).

This module performs static analysis only. It never imports or executes OCE
business modules. Reports are written atomically under ``oif_audit/``.
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import tempfile
from collections import defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Iterable

STATUS = "OIF_ACTIVE_INTERFACE_BASELINE_READY"
SCHEMA_VERSION = "oif-0-baseline-v1"

INTERFACE_TERMS = (
    "interface", "dashboard", "chat", "conversation", "conversational",
    "representative", "review", "terminal", "web", "portal", "console",
    "session", "dialogue", "runtime",
)
GENERATED_DIR_TERMS = (
    "archive", "backup", "backups", "bundle", "bundles", "export",
    "exports", "generated", "historical", "history", "publication",
    "snapshot", "snapshots", "required_files", "__macosx",
)
PERSISTENCE_METHODS = {
    "write_text", "write_bytes", "open", "dump", "dumps", "replace",
    "rename", "mkdir", "unlink", "touch", "rmdir", "makedirs",
    "connect", "executemany", "execute", "commit",
}
ENTRYPOINT_NAMES = {
    "main", "run", "run_forever", "serve", "launch", "start", "step",
}
GATE_TERMS = (
    "gate", "approval", "authorization", "compliance", "governance",
    "human_review", "controlled_execution", "constitutional",
)
REPRESENTATIVE_TERMS = (
    "supreme_representative", "representative_identity",
    "representative_status", "representative_selection",
    "representative_lineage", "civilizational_conversational_agent",
    "persistent_civilizational_conversational_agent",
)


class AuditError(RuntimeError):
    """Raised for an invalid or unsafe audit configuration."""


def _canonical(path: Path) -> Path:
    return path.expanduser().resolve(strict=False)


def _within(path: Path, root: Path) -> bool:
    try:
        _canonical(path).relative_to(_canonical(root))
        return True
    except ValueError:
        return False


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _stable_json_bytes(payload: Any) -> bytes:
    return (json.dumps(payload, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":")) + "\n").encode("utf-8")


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    except Exception:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass
        raise


def _safe_read(path: Path, root: Path) -> tuple[str | None, str | None]:
    if path.is_symlink() and not _within(path, root):
        return None, "symlink_outside_root"
    if not _within(path, root):
        return None, "path_outside_root"
    try:
        return path.read_text(encoding="utf-8"), None
    except UnicodeDecodeError:
        return None, "non_utf8_source"
    except OSError as exc:
        return None, f"read_error:{type(exc).__name__}"


def _call_name(node: ast.AST) -> str:
    parts: list[str] = []
    current: ast.AST | None = node
    while isinstance(current, ast.Attribute):
        parts.append(current.attr)
        current = current.value
    if isinstance(current, ast.Name):
        parts.append(current.id)
    return ".".join(reversed(parts))


def _literal_path(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr):
        return "<f-string>"
    return None


def _name_tokens(name: str) -> set[str]:
    stop = {"civilizational", "oce", "the", "and", "of", "runtime"}
    return {token for token in re.split(r"[^a-z0-9]+", name.lower())
            if len(token) > 2 and token not in stop}


@dataclass(frozen=True)
class ModuleRecord:
    module: str
    path: str
    source_sha256: str
    classification: str
    imports: tuple[str, ...]
    classes: tuple[str, ...]
    functions: tuple[str, ...]
    entrypoints: tuple[str, ...]
    persistence_calls: tuple[dict[str, Any], ...]
    gate_references: tuple[str, ...]
    representative_entrypoint: bool
    syntax_error: str | None


class _StaticVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.imports: set[str] = set()
        self.classes: set[str] = set()
        self.functions: set[str] = set()
        self.entrypoints: set[str] = set()
        self.persistence: list[dict[str, Any]] = []
        self.gates: set[str] = set()

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.imports.add(alias.name)
            self._gate(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        base = "." * node.level + (node.module or "")
        self.imports.add(base)
        self._gate(base)
        for alias in node.names:
            self._gate(alias.name)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.classes.add(node.name)
        self._gate(node.name)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.functions.add(node.name)
        if node.name in ENTRYPOINT_NAMES:
            self.entrypoints.add(node.name)
        self._gate(node.name)
        self.generic_visit(node)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Call(self, node: ast.Call) -> None:
        name = _call_name(node.func)
        lower = name.lower()
        method = lower.rsplit(".", 1)[-1]
        if method in PERSISTENCE_METHODS:
            target = _literal_path(node.args[0]) if node.args else None
            mode = None
            if method == "open":
                if len(node.args) > 1:
                    mode = _literal_path(node.args[1])
                for keyword in node.keywords:
                    if keyword.arg == "mode":
                        mode = _literal_path(keyword.value)
            self.persistence.append({
                "call": name,
                "line": int(getattr(node, "lineno", 0)),
                "target_literal": target,
                "mode_literal": mode,
            })
        self._gate(name)
        self.generic_visit(node)

    def _gate(self, text: str) -> None:
        lower = text.lower()
        if any(term in lower for term in GATE_TERMS):
            self.gates.add(text)


def _classify(relative: Path, module_name: str) -> str:
    lower_parts = [part.lower() for part in relative.parts]
    if any(any(term in part for term in GENERATED_DIR_TERMS) for part in lower_parts[:-1]):
        return "historical_or_generated"
    lower = module_name.lower()
    if "exporter" in lower or "generator" in lower:
        return "generated_output_producer"
    if "dashboard" in lower:
        return "dashboard_source"
    if "interface" in lower or "terminal" in lower or "console" in lower:
        return "interface_source"
    if "conversation" in lower or "conversational" in lower or "dialogue" in lower or "chat" in lower:
        return "conversation_source"
    if "representative" in lower:
        return "representative_source"
    if "review" in lower:
        return "review_source"
    if "runtime" in lower:
        return "runtime_source"
    return "related_source"


def _is_candidate(path: Path) -> bool:
    stem = path.stem.lower()
    joined = "/".join(part.lower() for part in path.parts)
    return any(term in stem or term in joined for term in INTERFACE_TERMS)


class OIFActiveInterfaceAuditor:
    """Build a reproducible OIF-0 static baseline without business execution."""

    def __init__(self, root: Path | str | None = None,
                 output_dir: Path | str | None = None) -> None:
        self.root = _canonical(Path(root) if root else Path.home() / "open-cognitive-ecology")
        self.output_dir = _canonical(Path(output_dir) if output_dir else self.root / "oif_audit")
        if not self.root.is_dir():
            raise AuditError(f"OCE root does not exist: {self.root}")
        if not _within(self.output_dir, self.root):
            raise AuditError("output_dir must remain inside ROOT")

    def _source_files(self) -> list[Path]:
        roots = [self.root / "ontology", self.root / "validation", self.root / "oif"]
        files: set[Path] = set()
        for base in roots:
            if not base.is_dir():
                continue
            for path in base.rglob("*.py"):
                if "__pycache__" in path.parts or path.name.endswith(".py.bak"):
                    continue
                if _is_candidate(path):
                    files.add(path)
        return sorted(files, key=lambda p: p.relative_to(self.root).as_posix())

    def _record(self, path: Path) -> ModuleRecord:
        relative = path.relative_to(self.root)
        module = relative.with_suffix("").as_posix().replace("/", ".")
        text, error = _safe_read(path, self.root)
        if text is None:
            return ModuleRecord(module, relative.as_posix(), "", _classify(relative, module),
                                (), (), (), (), (), (), False, error)
        digest = _sha256_bytes(text.encode("utf-8"))
        try:
            tree = ast.parse(text, filename=str(relative))
        except SyntaxError as exc:
            syntax = f"{exc.msg}@{exc.lineno}:{exc.offset}"
            return ModuleRecord(module, relative.as_posix(), digest, _classify(relative, module),
                                (), (), (), (), (), (), False, syntax)
        visitor = _StaticVisitor()
        visitor.visit(tree)
        representative = any(term in module.lower() for term in REPRESENTATIVE_TERMS)
        representative = representative and bool(visitor.entrypoints or visitor.classes)
        persistence = tuple(sorted(visitor.persistence,
                                   key=lambda x: (x["line"], x["call"], str(x["target_literal"]))))
        return ModuleRecord(
            module=module,
            path=relative.as_posix(),
            source_sha256=digest,
            classification=_classify(relative, module),
            imports=tuple(sorted(visitor.imports)),
            classes=tuple(sorted(visitor.classes)),
            functions=tuple(sorted(visitor.functions)),
            entrypoints=tuple(sorted(visitor.entrypoints)),
            persistence_calls=persistence,
            gate_references=tuple(sorted(visitor.gates)),
            representative_entrypoint=representative,
            syntax_error=None,
        )

    def _registry_status(self) -> dict[str, Any]:
        candidates = {
            "ontology_inventory_txt": self.root / "ontology_inventory.txt",
            "ontology_inventory_py": self.root / "ontology" / "ontology_inventory.py",
            "dependency_registry_root": self.root / "dependency_registry.py",
            "dependency_registry_ontology": self.root / "ontology" / "dependency_registry.py",
        }
        result: dict[str, Any] = {}
        for name, path in sorted(candidates.items()):
            if path.is_file() and _within(path, self.root):
                data = path.read_bytes()
                result[name] = {"present": True, "path": path.relative_to(self.root).as_posix(),
                                "sha256": _sha256_bytes(data), "size_bytes": len(data)}
            else:
                result[name] = {"present": False, "path": path.relative_to(self.root).as_posix()}
        return result

    def _redundancies(self, records: list[ModuleRecord]) -> list[dict[str, Any]]:
        pairs: list[dict[str, Any]] = []
        for index, left in enumerate(records):
            lt = _name_tokens(left.module)
            if not lt:
                continue
            for right in records[index + 1:]:
                rt = _name_tokens(right.module)
                union = lt | rt
                if not union:
                    continue
                score = len(lt & rt) / len(union)
                shared_imports = sorted(set(left.imports) & set(right.imports))
                if score >= 0.50 or (score >= 0.34 and len(shared_imports) >= 2):
                    pairs.append({
                        "left": left.module,
                        "right": right.module,
                        "name_jaccard": round(score, 6),
                        "shared_name_tokens": sorted(lt & rt),
                        "shared_imports": shared_imports,
                        "interpretation": "candidate_overlap_requires_human_review",
                    })
        return sorted(pairs, key=lambda p: (-p["name_jaccard"], p["left"], p["right"]))

    def build(self) -> dict[str, Any]:
        records = [self._record(path) for path in self._source_files()]
        record_dicts = [asdict(record) for record in records]
        source_fingerprint = _sha256_bytes(_stable_json_bytes([
            {"path": r.path, "sha256": r.source_sha256} for r in records
        ]))
        inventory = {
            "schema_version": SCHEMA_VERSION,
            "status": STATUS,
            "source_fingerprint": source_fingerprint,
            "module_count": len(records),
            "classification_counts": dict(sorted(self._counts(r.classification for r in records).items())),
            "registry_status": self._registry_status(),
            "modules": record_dicts,
        }
        dependency_map = {
            "schema_version": SCHEMA_VERSION,
            "source_fingerprint": source_fingerprint,
            "edges": sorted(
                ({"source": r.module, "target": target} for r in records for target in r.imports),
                key=lambda x: (x["source"], x["target"]),
            ),
        }
        persistence = {
            "schema_version": SCHEMA_VERSION,
            "source_fingerprint": source_fingerprint,
            "modules": [
                {"module": r.module, "path": r.path, "calls": list(r.persistence_calls)}
                for r in records if r.persistence_calls
            ],
        }
        gate_map = {
            "schema_version": SCHEMA_VERSION,
            "source_fingerprint": source_fingerprint,
            "modules": [
                {"module": r.module, "references": list(r.gate_references)}
                for r in records if r.gate_references
            ],
        }
        representative = {
            "schema_version": SCHEMA_VERSION,
            "source_fingerprint": source_fingerprint,
            "entrypoints": [
                {"module": r.module, "path": r.path, "classes": list(r.classes),
                 "entrypoints": list(r.entrypoints)}
                for r in records if r.representative_entrypoint
            ],
        }
        redundancy = {
            "schema_version": SCHEMA_VERSION,
            "source_fingerprint": source_fingerprint,
            "method": "name-token Jaccard plus shared-import evidence; candidates only",
            "candidates": self._redundancies(records),
        }
        syntax_errors = [
            {"module": r.module, "path": r.path, "error": r.syntax_error}
            for r in records if r.syntax_error
        ]
        reports: dict[str, Any] = {
            "oif_active_interface_inventory.json": inventory,
            "oif_dependency_map.json": dependency_map,
            "oif_redundancy_report.json": redundancy,
            "oif_persistence_boundary_report.json": persistence,
            "oif_gate_map.json": gate_map,
            "oif_representative_entrypoint_map.json": representative,
        }
        baseline = self._baseline_markdown(inventory, dependency_map, redundancy,
                                           persistence, gate_map, representative, syntax_errors)
        return {"reports": reports, "baseline_markdown": baseline,
                "source_fingerprint": source_fingerprint,
                "syntax_errors": syntax_errors, "records": record_dicts}

    @staticmethod
    def _counts(values: Iterable[str]) -> dict[str, int]:
        counts: dict[str, int] = defaultdict(int)
        for value in values:
            counts[value] += 1
        return dict(counts)

    def _baseline_markdown(self, inventory: dict[str, Any], dependency: dict[str, Any],
                           redundancy: dict[str, Any], persistence: dict[str, Any],
                           gates: dict[str, Any], representative: dict[str, Any],
                           syntax_errors: list[dict[str, Any]]) -> str:
        counts = inventory["classification_counts"]
        lines = [
            "# OIF-0 — Baseline reproductible", "",
            f"- Schéma : `{SCHEMA_VERSION}`",
            f"- Statut : `{STATUS}`",
            f"- Empreinte des sources : `{inventory['source_fingerprint']}`",
            f"- Modules candidats analysés : **{inventory['module_count']}**",
            f"- Arêtes d'import statiques : **{len(dependency['edges'])}**",
            f"- Candidats de redondance : **{len(redundancy['candidates'])}**",
            f"- Modules avec écritures potentielles : **{len(persistence['modules'])}**",
            f"- Modules avec références de gates : **{len(gates['modules'])}**",
            f"- Points d'entrée du représentant : **{len(representative['entrypoints'])}**",
            f"- Erreurs syntaxiques ou de lecture : **{len(syntax_errors)}**", "",
            "## Classifications", "",
        ]
        for key, value in sorted(counts.items()):
            lines.append(f"- `{key}` : {value}")
        lines += ["", "## Interprétation scientifique", "",
                  "Les redondances signalées sont des hypothèses statiques à examiner, pas des suppressions autorisées.",
                  "L'audit n'importe ni n'exécute aucun module métier et n'affirme aucune propriété phénoménale.", ""]
        return "\n".join(lines)

    def write(self) -> dict[str, Any]:
        built = self.build()
        written: dict[str, str] = {}
        report_hashes: dict[str, str] = {}
        for name, payload in sorted(built["reports"].items()):
            data = _stable_json_bytes(payload)
            path = self.output_dir / name
            _atomic_write(path, data)
            written[name] = str(path)
            report_hashes[name] = _sha256_bytes(data)
        baseline_data = built["baseline_markdown"].encode("utf-8")
        baseline_path = self.output_dir / "oif_baseline_report.md"
        _atomic_write(baseline_path, baseline_data)
        written[baseline_path.name] = str(baseline_path)
        report_hashes[baseline_path.name] = _sha256_bytes(baseline_data)
        manifest_lines = [f"{digest}  {name}" for name, digest in sorted(report_hashes.items())]
        manifest_data = ("\n".join(manifest_lines) + "\n").encode("utf-8")
        manifest_path = self.output_dir / "oif_baseline_manifest.sha256"
        _atomic_write(manifest_path, manifest_data)
        written[manifest_path.name] = str(manifest_path)
        return {
            "primitive": "oif_active_interface_auditor",
            "status": STATUS,
            "success": True,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "source_fingerprint": built["source_fingerprint"],
            "module_count": len(built["records"]),
            "syntax_error_count": len(built["syntax_errors"]),
            "output_dir": str(self.output_dir),
            "written": dict(sorted(written.items())),
        }

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = False) -> dict[str, Any]:
        inputs = dict(inputs or {})
        if inputs:
            allowed = {"persist"}
            unknown = sorted(set(inputs) - allowed)
            if unknown:
                raise AuditError(f"unsupported inputs: {unknown}")
            persist = bool(inputs.get("persist", persist))
        if persist:
            return self.write()
        built = self.build()
        return {
            "primitive": "oif_active_interface_auditor",
            "status": STATUS,
            "success": True,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "source_fingerprint": built["source_fingerprint"],
            "module_count": len(built["records"]),
            "syntax_error_count": len(built["syntax_errors"]),
            "persisted": False,
        }
