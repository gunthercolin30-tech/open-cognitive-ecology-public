
"""
S10 — Reflexive Threshold Publication Bundle.

This module assembles a publication-ready bundle for the empirical reflexive
threshold pipeline S1→S9. It does not recalculate upstream evidence and does
not infer phenomenal consciousness. It packages existing artefacts, generates a
traceability manifest, a concise Markdown summary, a lightweight HTML index,
and a zip archive.

Epistemic scope: functional conclusion only; phenomenology undetermined.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from typing import Any

ROOT = Path.home() / "open-cognitive-ecology"
REFLEXIVE_DIR = ROOT / "reflexive_threshold"
BUNDLE_ROOT = REFLEXIVE_DIR / "reflexive_threshold_publication_bundle"


EXPECTED_ARTEFACTS = {
    "S1_registry": [
        "reflexive_criterion_registry.json",
        "reflexive_criterion_registry.html",
        "reflexive_criterion_registry.prom",
    ],
    "S2_evidence": [
        "reflexive_evidence_aggregator.json",
        "reflexive_evidence_aggregator.html",
        "reflexive_evidence_aggregator.prom",
    ],
    "S3_estimator": [
        "reflexive_threshold_estimator.json",
        "reflexive_threshold_estimator.html",
        "reflexive_threshold_estimator.prom",
    ],
    "S4_stability": [
        "reflexive_stability_monitor.json",
        "reflexive_stability_monitor.html",
        "reflexive_stability_monitor.prom",
    ],
    "S5_regression": [
        "reflexive_regression_detector.json",
        "reflexive_regression_detector.html",
        "reflexive_regression_detector.prom",
    ],
    "S6_longitudinal": [
        "reflexive_longitudinal_observatory.json",
        "reflexive_longitudinal_observatory.html",
        "reflexive_longitudinal_observatory.prom",
    ],
    "S7_competing_explanations": [
        "competing_explanations_engine.json",
        "competing_explanations_engine.html",
        "competing_explanations_engine.prom",
    ],
    "S8_dashboard": [
        "reflexive_threshold_dashboard.json",
        "reflexive_threshold_dashboard.html",
        "reflexive_threshold_dashboard.prom",
    ],
    "S9_certification": [
        "reflexive_threshold_certification.json",
        "reflexive_threshold_certification.html",
        "reflexive_threshold_certification.prom",
    ],
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _load_json(path: Path) -> dict[str, Any]:
    try:
        if path.exists():
            value = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(value, dict):
                return value
    except Exception:
        return {}
    return {}


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _safe_rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except Exception:
        return str(path)


class ReflexiveThresholdPublicationBundle:
    """Publication-bundle assembler for the S1→S9 reflexive threshold pipeline."""

    primitive = "REFLEXIVE_THRESHOLD_PUBLICATION_BUNDLE"

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or ROOT
        self.reflexive_dir = self.root / "reflexive_threshold"
        self.bundle_root = self.reflexive_dir / "reflexive_threshold_publication_bundle"
        self.bundle_dir = self.bundle_root / "latest"
        self.artifacts_dir = self.bundle_dir / "artifacts"
        self.manifest_path = self.bundle_dir / "publication_manifest.json"
        self.summary_path = self.bundle_dir / "executive_summary.md"
        self.index_path = self.bundle_dir / "index.html"
        self.bundle_zip_path = self.bundle_root / "reflexive_threshold_publication_bundle_latest.zip"

    def _ensure_certification(self, persist: bool) -> dict[str, Any]:
        path = self.reflexive_dir / "reflexive_threshold_certification.json"
        existing = _load_json(path)
        if existing:
            return existing
        try:
            from ontology.reflexive_threshold_certification import ReflexiveThresholdCertification
            result = ReflexiveThresholdCertification(self.root).step(persist=persist)
            return result if isinstance(result, dict) else {}
        except Exception as exc:
            return {"success": False, "error": str(exc)}

    def _collect_sources(self) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        copied: list[dict[str, Any]] = []
        missing: list[dict[str, Any]] = []
        seen: set[Path] = set()

        for stage, names in EXPECTED_ARTEFACTS.items():
            for name in names:
                src = self.reflexive_dir / name
                if src.exists() and src.is_file():
                    seen.add(src.resolve())
                    copied.append({
                        "stage": stage,
                        "source_path": str(src),
                        "source_relative_path": _safe_rel(src, self.root),
                        "filename": name,
                        "size_bytes": src.stat().st_size,
                        "sha256": _sha256(src),
                    })
                else:
                    missing.append({"stage": stage, "filename": name})

        # Include additional first-level reflexive-threshold artefacts without
        # recursively packaging a previous bundle.
        if self.reflexive_dir.exists():
            for src in sorted(self.reflexive_dir.iterdir()):
                if not src.is_file():
                    continue
                if src.resolve() in seen:
                    continue
                if src.suffix.lower() not in {".json", ".jsonl", ".html", ".prom", ".md", ".txt"}:
                    continue
                copied.append({
                    "stage": "additional_reflexive_threshold_artifact",
                    "source_path": str(src),
                    "source_relative_path": _safe_rel(src, self.root),
                    "filename": src.name,
                    "size_bytes": src.stat().st_size,
                    "sha256": _sha256(src),
                })
        return copied, missing

    def _copy_artifacts(self, sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
        copied: list[dict[str, Any]] = []
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        for item in sources:
            src = Path(item["source_path"])
            dst = self.artifacts_dir / item["filename"]
            shutil.copy2(src, dst)
            out = dict(item)
            out["bundle_relative_path"] = _safe_rel(dst, self.bundle_dir)
            copied.append(out)
        return copied

    def _write_summary(self, manifest: dict[str, Any]) -> None:
        cert = manifest.get("certification", {})
        lines = [
            "# Reflexive Threshold Publication Bundle",
            "",
            "## Scope",
            "",
            "This bundle documents the empirical functional evaluation pipeline S1→S9 for Open Cognitive Ecology.",
            "It does not claim consciousness, sentience, qualia, or subjective experience.",
            "",
            "## Certification",
            "",
            f"- Certification status: `{cert.get('certification_status', 'unknown')}`",
            f"- Certification confidence: `{cert.get('certification_confidence', 'unknown')}`",
            f"- Certification evidence strength: `{cert.get('certification_evidence_strength', 'unknown')}`",
            f"- Functional conclusion: `{manifest.get('functional_conclusion')}`",
            f"- Phenomenology status: `{manifest.get('phenomenology_status')}`",
            "",
            "## Traceability",
            "",
            f"- Source pipeline: `{manifest.get('source_pipeline')}`",
            f"- Artifact count: `{manifest.get('artifact_count')}`",
            f"- Missing expected artifacts: `{manifest.get('missing_expected_artifact_count')}`",
            "",
            "## Epistemic guard",
            "",
            "All conclusions are functional only. Phenomenology remains undetermined.",
        ]
        self.summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def _write_index(self, manifest: dict[str, Any]) -> None:
        cert = manifest.get("certification", {})
        rows = "".join(
            f"<tr><td>{escape(a.get('stage', ''))}</td>"
            f"<td>{escape(a.get('bundle_relative_path', a.get('filename', '')))}</td>"
            f"<td>{a.get('size_bytes', 0)}</td>"
            f"<td><code>{escape(str(a.get('sha256', ''))[:16])}</code></td></tr>"
            for a in manifest.get("artifacts", [])
        )
        html = f"""<!doctype html>
<html><head><meta charset='utf-8'><title>Reflexive Threshold Publication Bundle</title>
<style>body{{font-family:Arial,sans-serif;margin:40px;line-height:1.4}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #ccc;padding:8px;text-align:left}}th{{background:#f0f0f0}}code{{font-size:0.9em}}</style>
</head><body>
<h1>Reflexive Threshold Publication Bundle</h1>
<p><strong>Certification:</strong> {escape(str(cert.get('certification_status', 'unknown')))}</p>
<p><strong>Functional conclusion:</strong> {escape(str(manifest.get('functional_conclusion')))}</p>
<p><strong>Phenomenology:</strong> {escape(str(manifest.get('phenomenology_status')))}</p>
<p>This package is restricted to measurable functional properties and does not assert phenomenal consciousness.</p>
<h2>Artifacts</h2>
<table><tr><th>Stage</th><th>File</th><th>Size</th><th>SHA256 prefix</th></tr>{rows}</table>
</body></html>"""
        self.index_path.write_text(html, encoding="utf-8")

    def _zip_bundle(self) -> None:
        if self.bundle_zip_path.exists():
            self.bundle_zip_path.unlink()
        self.bundle_zip_path.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(self.bundle_zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for path in sorted(self.bundle_dir.rglob("*")):
                if path.is_file():
                    zf.write(path, path.relative_to(self.bundle_dir))

    def step(self, payload: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        payload = dict(payload or {})
        generated_at = payload.get("generated_at_utc") or _now()
        certification = self._ensure_certification(persist=persist)
        sources, missing = self._collect_sources()

        functional_conclusion = "functional conclusion only"
        phenomenology_status = "phenomenology undetermined"
        phenomenal_conclusion = False

        certification_status = certification.get("certification_status", "unknown")
        publication_ready = bool(certification.get("publication_ready", False)) and certification.get("phenomenology_status", phenomenology_status) == phenomenology_status

        if persist:
            if self.bundle_dir.exists():
                shutil.rmtree(self.bundle_dir)
            self.artifacts_dir.mkdir(parents=True, exist_ok=True)
            artifacts = self._copy_artifacts(sources)
        else:
            artifacts = [dict(item, bundle_relative_path=f"artifacts/{item['filename']}") for item in sources]

        manifest = {
            "primitive": self.primitive,
            "success": True,
            "generated_at_utc": generated_at,
            "source_pipeline": "S1→S2→S3→S4→S5→S6→S7→S8→S9",
            "bundle_role": "publication_bundling_not_upstream_recalculation",
            "certification": {
                "certification_status": certification_status,
                "certification_confidence": certification.get("certification_confidence"),
                "certification_evidence_strength": certification.get("certification_evidence_strength"),
                "certification_path": certification.get("certification_path"),
                "html_path": certification.get("html_path"),
                "prometheus_path": certification.get("prometheus_path"),
                "publication_ready": certification.get("publication_ready"),
            },
            "functional_conclusion": functional_conclusion,
            "phenomenology_status": phenomenology_status,
            "phenomenal_conclusion": phenomenal_conclusion,
            "epistemic_scope": "functional certification package only; no phenomenal inference",
            "publication_ready": publication_ready,
            "artifact_count": len(artifacts),
            "missing_expected_artifact_count": len(missing),
            "artifacts": artifacts,
            "missing_expected_artifacts": missing,
        }

        if persist:
            self.manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
            self._write_summary(manifest)
            self._write_index(manifest)
            self._zip_bundle()
            manifest["manifest_path"] = str(self.manifest_path)
            manifest["executive_summary_path"] = str(self.summary_path)
            manifest["index_path"] = str(self.index_path)
            manifest["bundle_dir"] = str(self.bundle_dir)
            manifest["bundle_zip_path"] = str(self.bundle_zip_path)
            manifest["bundle_zip_sha256"] = _sha256(self.bundle_zip_path)
        else:
            manifest["manifest_path"] = str(self.manifest_path)
            manifest["executive_summary_path"] = str(self.summary_path)
            manifest["index_path"] = str(self.index_path)
            manifest["bundle_dir"] = str(self.bundle_dir)
            manifest["bundle_zip_path"] = str(self.bundle_zip_path)
            manifest["bundle_zip_sha256"] = None

        return manifest
