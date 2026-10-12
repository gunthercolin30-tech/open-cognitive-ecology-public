
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import io
import zipfile
from typing import Any


class ReflexiveThresholdExternalReviewBundle:
    """
    S11 — Reflexive Threshold External Review Bundle.

    Produces a specialized, self-contained external review package for the
    functional reflexive threshold evaluation. It consumes the S10 publication
    bundle and does not recalculate upstream metrics, make phenomenal claims,
    or introduce a new certification.

    Epistemic guard:
    - functional conclusion only
    - phenomenology undetermined
    """

    primitive = "REFLEXIVE_THRESHOLD_EXTERNAL_REVIEW_BUNDLE"
    source_pipeline = "S1→S2→S3→S4→S5→S6→S7→S8→S9→S10"

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.base_dir = self.root / "reflexive_threshold" / "reflexive_threshold_external_review_bundle"

    def _now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    def _read_json(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _latest_s10_bundle_dir(self) -> Path | None:
        candidates = [
            self.root / "reflexive_threshold" / "reflexive_threshold_publication_bundle",
            self.root / "reflexive_threshold_publication_bundle",
        ]
        for candidate in candidates:
            if candidate.exists() and candidate.is_dir():
                return candidate
        return None

    def _find_file(self, names: list[str], search_roots: list[Path]) -> Path | None:
        for root in search_roots:
            if not root.exists():
                continue
            for name in names:
                direct = root / name
                if direct.exists() and direct.is_file():
                    return direct
            for path in root.rglob("*"):
                if path.is_file() and path.name in names:
                    return path
        return None

    def _copy_if_exists(self, source: Path | None, dest_dir: Path, dest_name: str | None = None, *, fs_context=None) -> dict[str, Any]:
        if source is None or not source.exists() or not source.is_file():
            return {"copied": False, "source": str(source) if source else None, "destination": None}
        if fs_context is None:
            raise PermissionError("external review artifact copy requires preissued filesystem effect context")
        if not fs_context.source_root_id or fs_context.source_root_path is None:
            raise RuntimeError("external review artifact copy requires governed source-root binding")
        dest = dest_dir / (dest_name or source.name)
        fs_context.execute_path("external_review_artifact_dir_create", "FS_CREATE_DIRS", dest_dir)
        fs_context.execute_copy2(
            "external_review_artifact_copy",
            fs_context.source_root_id,
            fs_context.source_root_path,
            source,
            dest,
        )
        return {"copied": True, "source": str(source), "destination": str(dest)}

    def _write_reviewer_readme(self, path: Path, certification: dict[str, Any], manifest: dict[str, Any], *, fs_context=None) -> None:
        status = certification.get("certification_status", "unknown")
        confidence = certification.get("certification_confidence", "unknown")
        evidence = certification.get("certification_evidence_strength", "unknown")
        text = f"""# External Review Package — Reflexive Threshold Evaluation

## Purpose

This package supports independent review of Open Cognitive Ecology's functional reflexive threshold evaluation.

It is not a claim of consciousness, sentience, subjective experience, or qualia.

## Epistemic status

- functional conclusion only
- phenomenology undetermined
- phenomenal_conclusion: false

## Certification summary

- certification_status: {status}
- certification_confidence: {confidence}
- certification_evidence_strength: {evidence}
- source_pipeline: {self.source_pipeline}

## What to review

1. Verify that the certification is derived from S1→S10 artifacts.
2. Check that the package contains no phenomenal conclusion.
3. Inspect the certification JSON and HTML.
4. Inspect dashboard and evidence artifacts when present.
5. Re-run the local validation command if source access is available:
   `python3 -m validation.main`.

## Interpretation boundary

A positive or partial result means only that functional indicators associated with the reflexive threshold are measured and aggregated in the current architecture.

It does not establish phenomenology.
"""
        if fs_context is None:
            raise PermissionError("reviewer readme write requires preissued filesystem effect context")
        fs_context.execute_path("external_review_readme_write", "FS_WRITE_BYTES", path, text.encode("utf-8"))

    def _write_replication_protocol(self, path: Path, *, fs_context=None) -> None:
        text = f"""# Replication Protocol — Functional Reflexive Threshold

## Scope

Replicate the S1→S10 functional pipeline and compare the resulting S11 review package.

## Required commands

```bash
cd ~/open-cognitive-ecology
python3 -m validation.main
python3 - <<'PY'
from ontology.reflexive_threshold_external_review_bundle import ReflexiveThresholdExternalReviewBundle
r = ReflexiveThresholdExternalReviewBundle().step(persist=True)
print(r)
PY
```

## Expected constraints

- error_count must remain 0.
- Generated package must preserve:
  - functional conclusion only
  - phenomenology undetermined
  - phenomenal_conclusion = false
- No test may infer consciousness, sentience, subjective experience, or qualia.

## Review outputs

The reviewer should report:

- whether artifacts are present and readable;
- whether traceability to S1→S10 is preserved;
- whether the epistemic guard is respected;
- whether the package is sufficient for independent functional review.
"""
        if fs_context is None:
            raise PermissionError("replication protocol write requires preissued filesystem effect context")
        fs_context.execute_path("external_review_replication_protocol_write", "FS_WRITE_BYTES", path, text.encode("utf-8"))

    def _build_checklist(self, certification: dict[str, Any]) -> dict[str, Any]:
        return {
            "primitive": self.primitive,
            "source_pipeline": self.source_pipeline,
            "review_items": [
                {"id": "traceability", "question": "Does the package trace S1 through S10?", "required": True},
                {"id": "certification_json", "question": "Is certification JSON available?", "required": True},
                {"id": "human_readable_summary", "question": "Is a reviewer README available?", "required": True},
                {"id": "replication_protocol", "question": "Is a replication protocol available?", "required": True},
                {"id": "epistemic_guard", "question": "Are functional-only and phenomenology-undetermined statements present?", "required": True},
                {"id": "no_phenomenal_claim", "question": "Does the package avoid consciousness/sentience/qualia conclusions?", "required": True},
            ],
            "certification_status": certification.get("certification_status"),
            "functional_conclusion": "functional conclusion only",
            "phenomenology_status": "phenomenology undetermined",
            "phenomenal_conclusion": False,
        }

    def _zip_dir(self, directory: Path, zip_path: Path, *, fs_context=None) -> None:
        """Build the archive without mutating the target, then replace it through the preissued TCB."""
        if fs_context is None:
            raise PermissionError("external review bundle zip write requires preissued filesystem effect context")

        payload_buffer = io.BytesIO()
        with zipfile.ZipFile(payload_buffer, "w", compression=zipfile.ZIP_DEFLATED) as z:
            for path in sorted(directory.rglob("*")):
                if path == zip_path:
                    continue
                if path.is_file():
                    z.write(path, path.relative_to(directory))

        fs_context.execute_path(
            "external_review_bundle_zip_write",
            "FS_WRITE_REPLACE_BYTES",
            zip_path,
            payload_buffer.getvalue(),
        )

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True, fs_context=None) -> dict[str, Any]:
        inputs = dict(inputs or {})
        generated_at = inputs.get("generated_at_utc") or self._now()

        s10_dir = self._latest_s10_bundle_dir()
        search_roots = [p for p in [s10_dir, self.root / "reflexive_threshold", self.root] if p is not None]

        manifest_path = self._find_file(["publication_manifest.json"], search_roots)
        certification_path = self._find_file(
            ["reflexive_threshold_certification.json", "certification.json"],
            search_roots,
        )
        certification_html = self._find_file(
            ["reflexive_threshold_certification.html", "certification.html"],
            search_roots,
        )
        dashboard_html = self._find_file(
            ["reflexive_threshold_dashboard.html", "dashboard.html"],
            search_roots,
        )
        executive_summary = self._find_file(["executive_summary.md"], search_roots)

        manifest = self._read_json(manifest_path) if manifest_path else {}
        certification = self._read_json(certification_path) if certification_path else {}
        if not certification and isinstance(manifest.get("certification"), dict):
            certification = manifest["certification"]

        package_dir = self.base_dir
        artifacts_dir = package_dir / "artifacts"

        copied = []
        expected = {
            "publication_manifest.json": manifest_path,
            "certification.json": certification_path,
            "certification.html": certification_html,
            "dashboard.html": dashboard_html,
            "s10_executive_summary.md": executive_summary,
        }

        reviewer_readme_path = package_dir / "reviewer_readme.md"
        replication_protocol_path = package_dir / "replication_protocol.md"
        checklist_path = package_dir / "review_checklist.json"
        evidence_manifest_path = package_dir / "evidence_manifest.json"
        zip_path = package_dir / "external_review_bundle.zip"

        if persist:
            package_dir.mkdir(parents=True, exist_ok=True)
            artifacts_dir.mkdir(parents=True, exist_ok=True)

            for dest_name, source in expected.items():
                copied.append(self._copy_if_exists(source, artifacts_dir, dest_name, fs_context=fs_context))

            self._write_reviewer_readme(reviewer_readme_path, certification, manifest, fs_context=fs_context)
            self._write_replication_protocol(replication_protocol_path, fs_context=fs_context)
            checklist_path.write_text(
                json.dumps(self._build_checklist(certification), indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

            evidence_manifest = {
                "primitive": self.primitive,
                "generated_at_utc": generated_at,
                "source_pipeline": self.source_pipeline,
                "s10_bundle_dir": str(s10_dir) if s10_dir else None,
                "copied_artifacts": copied,
                "missing_artifacts": [name for name, source in expected.items() if source is None],
                "functional_conclusion": "functional conclusion only",
                "phenomenology_status": "phenomenology undetermined",
                "phenomenal_conclusion": False,
            }
            evidence_manifest_path.write_text(
                json.dumps(evidence_manifest, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

            self._zip_dir(package_dir, zip_path, fs_context=fs_context)
        else:
            copied = [
                {"copied": bool(source), "source": str(source) if source else None, "destination": None}
                for source in expected.values()
            ]

        artifact_count = sum(1 for item in copied if item.get("copied"))
        missing = [name for name, source in expected.items() if source is None]

        return {
            "success": True,
            "primitive": self.primitive,
            "generated_at_utc": generated_at,
            "source_pipeline": self.source_pipeline,
            "s10_bundle_dir": str(s10_dir) if s10_dir else None,
            "artifact_count": artifact_count,
            "missing_expected_artifact_count": len(missing),
            "missing_expected_artifacts": missing,
            "reviewer_readme_path": str(reviewer_readme_path),
            "replication_protocol_path": str(replication_protocol_path),
            "review_checklist_path": str(checklist_path),
            "evidence_manifest_path": str(evidence_manifest_path),
            "external_review_bundle_zip_path": str(zip_path),
            "certification_status": certification.get("certification_status"),
            "certification_confidence": certification.get("certification_confidence"),
            "certification_evidence_strength": certification.get("certification_evidence_strength"),
            "functional_conclusion": "functional conclusion only",
            "phenomenology_status": "phenomenology undetermined",
            "phenomenal_conclusion": False,
            "review_scope": "external functional review only",
            "epistemic_boundary": "no inference of consciousness, sentience, subjective experience, or qualia",
        }
