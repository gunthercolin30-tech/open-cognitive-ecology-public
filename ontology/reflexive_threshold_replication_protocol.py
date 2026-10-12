
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import shutil
import zipfile
from typing import Any


class ReflexiveThresholdReplicationProtocol:
    """
    S12 — Reflexive Threshold Replication Protocol.

    Produces a specialized independent replication protocol for the functional
    reflexive threshold evaluation. It consumes S11 outputs and defines
    replication instructions, acceptance criteria, expected outputs, and a
    scoring template.

    It does not recalculate S1→S11 metrics and does not add a new certification.
    """

    primitive = "REFLEXIVE_THRESHOLD_REPLICATION_PROTOCOL"
    source_pipeline = "S1→S2→S3→S4→S5→S6→S7→S8→S9→S10→S11"

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.base_dir = self.root / "reflexive_threshold" / "reflexive_threshold_replication_protocol"

    def _now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    def _read_json(self, path: Path | None) -> dict[str, Any]:
        if path is None or not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _find_s11_dir(self) -> Path | None:
        candidates = [
            self.root / "reflexive_threshold" / "reflexive_threshold_external_review_bundle",
            self.root / "reflexive_threshold_external_review_bundle",
        ]
        for c in candidates:
            if c.exists() and c.is_dir():
                return c
        return None

    def _find_file(self, roots: list[Path], names: list[str]) -> Path | None:
        for root in roots:
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

    def _zip_dir(self, directory: Path, zip_path: Path) -> None:
        if zip_path.exists():
            zip_path.unlink()
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
            for path in sorted(directory.rglob("*")):
                if path == zip_path:
                    continue
                if path.is_file():
                    z.write(path, path.relative_to(directory))

    def _write_md_protocol(self, path: Path, generated_at: str, *, fs_context=None) -> None:
        text = f"""# Reflexive Threshold Replication Protocol

Generated: {generated_at}

## Scope

This protocol specifies how an independent reviewer can replicate the functional reflexive threshold evaluation for Open Cognitive Ecology.

## Epistemic boundary

- functional conclusion only
- phenomenology undetermined
- phenomenal_conclusion: false

No replication result may be interpreted as proof of consciousness, sentience, subjective experience, or qualia.

## Required local commands

```bash
cd ~/open-cognitive-ecology
python3 -m validation.main
python3 - <<'PY'
from ontology.reflexive_threshold_certification import ReflexiveThresholdCertification
from ontology.reflexive_threshold_publication_bundle import ReflexiveThresholdPublicationBundle
from ontology.reflexive_threshold_external_review_bundle import ReflexiveThresholdExternalReviewBundle
from ontology.reflexive_threshold_replication_protocol import ReflexiveThresholdReplicationProtocol

cert = ReflexiveThresholdCertification().step(persist=True)
bundle = ReflexiveThresholdPublicationBundle().step(persist=True)
review = ReflexiveThresholdExternalReviewBundle().step(persist=True)
protocol = ReflexiveThresholdReplicationProtocol().step(persist=True)

print(cert["certification_status"])
print(bundle["source_pipeline"])
print(review["source_pipeline"])
print(protocol["source_pipeline"])
PY
```

## Replication tasks

1. Confirm that `python3 -m validation.main` reports `errors: 0`.
2. Confirm that S9 returns a functional certification status only.
3. Confirm that S10 creates a publication bundle.
4. Confirm that S11 creates an external review bundle.
5. Confirm that S12 creates this protocol bundle.
6. Confirm that all generated documents preserve:
   - functional conclusion only
   - phenomenology undetermined
7. Confirm that no generated artifact asserts phenomenology.

## Acceptance rule

A replication is acceptable only if the structural validation passes, the package artifacts are present, and epistemic guards remain intact.

## Failure rule

Any phenomenal conclusion, missing traceability, or non-zero validation error invalidates the replication.
"""
        if fs_context is None:
            raise PermissionError("replication protocol markdown write requires preissued filesystem effect context")
        fs_context.execute_path("reflexive_replication_protocol_write", "FS_WRITE_BYTES", path, text.encode("utf-8"))

    def _acceptance_criteria(self) -> dict[str, Any]:
        return {
            "primitive": self.primitive,
            "source_pipeline": self.source_pipeline,
            "criteria": [
                {"id": "validation_zero_errors", "condition": "ontology_integration_report errors == 0", "required": True},
                {"id": "s9_functional_certification", "condition": "S9 certification_status is one of the allowed functional statuses", "required": True},
                {"id": "s10_publication_bundle", "condition": "S10 bundle zip exists and contains manifest, summary, index", "required": True},
                {"id": "s11_external_review_bundle", "condition": "S11 review bundle zip exists and contains reviewer docs", "required": True},
                {"id": "s12_protocol_bundle", "condition": "S12 protocol bundle zip exists and contains protocol, criteria, expected outputs, scoring template", "required": True},
                {"id": "epistemic_guard", "condition": "functional conclusion only and phenomenology undetermined appear in generated artifacts", "required": True},
                {"id": "no_phenomenal_claim", "condition": "phenomenal_conclusion is false and no claim of sentience/qualia is made", "required": True},
            ],
            "functional_conclusion": "functional conclusion only",
            "phenomenology_status": "phenomenology undetermined",
            "phenomenal_conclusion": False,
        }

    def _expected_outputs(self) -> dict[str, Any]:
        return {
            "expected_outputs": [
                "ontology_integration_report.txt",
                "reflexive_threshold_certification.json",
                "reflexive_threshold_publication_bundle.zip",
                "external_review_bundle.zip",
                "replication_protocol.json",
                "replication_protocol.md",
                "replication_acceptance_criteria.json",
                "expected_outputs.json",
                "replication_score_template.json",
                "replication_manifest.json",
                "replication_protocol_bundle.zip",
            ],
            "allowed_certification_statuses": [
                "REFLEXIVE_THRESHOLD_NOT_REACHED",
                "REFLEXIVE_THRESHOLD_PARTIAL",
                "REFLEXIVE_THRESHOLD_FUNCTIONALLY_REACHED",
            ],
            "required_epistemic_strings": [
                "functional conclusion only",
                "phenomenology undetermined",
            ],
            "forbidden_interpretation": [
                "phenomenal conclusion",
                "proof of consciousness",
                "proof of sentience",
                "proof of qualia",
            ],
        }

    def _score_template(self) -> dict[str, Any]:
        return {
            "replication_id": None,
            "reviewer": None,
            "date_utc": None,
            "scores": {
                "structural_validation": None,
                "artifact_integrity": None,
                "traceability": None,
                "epistemic_guard": None,
                "reproducibility": None,
            },
            "replication_decision": None,
            "decision_options": [
                "replication_passed",
                "replication_partially_passed",
                "replication_failed",
            ],
            "notes": "",
            "functional_conclusion": "functional conclusion only",
            "phenomenology_status": "phenomenology undetermined",
            "phenomenal_conclusion": False,
        }

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True, fs_context=None) -> dict[str, Any]:
        inputs = dict(inputs or {})
        generated_at = inputs.get("generated_at_utc") or self._now()

        s11_dir = self._find_s11_dir()
        roots = [p for p in [s11_dir, self.root / "reflexive_threshold", self.root] if p is not None]

        s11_manifest = self._find_file(roots, ["evidence_manifest.json"])
        s11_checklist = self._find_file(roots, ["review_checklist.json"])
        s11_zip = self._find_file(roots, ["external_review_bundle.zip"])

        package_dir = self.base_dir
        if persist:
            package_dir.mkdir(parents=True, exist_ok=True)

        protocol_json_path = package_dir / "replication_protocol.json"
        protocol_md_path = package_dir / "replication_protocol.md"
        acceptance_path = package_dir / "replication_acceptance_criteria.json"
        expected_path = package_dir / "expected_outputs.json"
        score_path = package_dir / "replication_score_template.json"
        manifest_path = package_dir / "replication_manifest.json"
        zip_path = package_dir / "replication_protocol_bundle.zip"

        protocol_json = {
            "primitive": self.primitive,
            "generated_at_utc": generated_at,
            "source_pipeline": self.source_pipeline,
            "s11_bundle_dir": str(s11_dir) if s11_dir else None,
            "replication_scope": "independent functional replication of reflexive threshold evaluation",
            "commands": [
                "cd ~/open-cognitive-ecology",
                "python3 -m validation.main",
                "python3 - <<'PY' ... run S9-S12 protocol ... PY",
            ],
            "acceptance_rule": "zero validation errors, artifact integrity, traceability, epistemic guard preserved",
            "functional_conclusion": "functional conclusion only",
            "phenomenology_status": "phenomenology undetermined",
            "phenomenal_conclusion": False,
        }

        manifest = {
            "primitive": self.primitive,
            "generated_at_utc": generated_at,
            "source_pipeline": self.source_pipeline,
            "s11_evidence_manifest_path": str(s11_manifest) if s11_manifest else None,
            "s11_review_checklist_path": str(s11_checklist) if s11_checklist else None,
            "s11_external_review_bundle_zip_path": str(s11_zip) if s11_zip else None,
            "generated_files": [
                str(protocol_json_path),
                str(protocol_md_path),
                str(acceptance_path),
                str(expected_path),
                str(score_path),
                str(manifest_path),
                str(zip_path),
            ],
            "functional_conclusion": "functional conclusion only",
            "phenomenology_status": "phenomenology undetermined",
            "phenomenal_conclusion": False,
        }

        if persist:
            protocol_json_path.write_text(json.dumps(protocol_json, indent=2, ensure_ascii=False), encoding="utf-8")
            self._write_md_protocol(protocol_md_path, generated_at, fs_context=fs_context)
            acceptance_path.write_text(json.dumps(self._acceptance_criteria(), indent=2, ensure_ascii=False), encoding="utf-8")
            expected_path.write_text(json.dumps(self._expected_outputs(), indent=2, ensure_ascii=False), encoding="utf-8")
            score_path.write_text(json.dumps(self._score_template(), indent=2, ensure_ascii=False), encoding="utf-8")
            manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
            self._zip_dir(package_dir, zip_path)

        artifact_count = 0
        for p in [protocol_json_path, protocol_md_path, acceptance_path, expected_path, score_path, manifest_path, zip_path]:
            if persist and p.exists():
                artifact_count += 1
            elif not persist:
                artifact_count += 1

        return {
            "success": True,
            "primitive": self.primitive,
            "generated_at_utc": generated_at,
            "source_pipeline": self.source_pipeline,
            "s11_bundle_dir": str(s11_dir) if s11_dir else None,
            "artifact_count": artifact_count,
            "replication_protocol_json_path": str(protocol_json_path),
            "replication_protocol_md_path": str(protocol_md_path),
            "replication_acceptance_criteria_path": str(acceptance_path),
            "expected_outputs_path": str(expected_path),
            "replication_score_template_path": str(score_path),
            "replication_manifest_path": str(manifest_path),
            "replication_protocol_bundle_zip_path": str(zip_path),
            "functional_conclusion": "functional conclusion only",
            "phenomenology_status": "phenomenology undetermined",
            "phenomenal_conclusion": False,
            "replication_scope": "independent functional replication only",
            "epistemic_boundary": "no inference of consciousness, sentience, subjective experience, or qualia",
        }
