
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import io
import zipfile
from typing import Any


class ReflexiveThresholdFinalScientificSynthesis:
    """
    S14 — Reflexive Threshold Final Scientific Synthesis.

    Produces the final scientific synthesis for the functional reflexive
    threshold evaluation from S1 to S13.

    It consolidates:
    - S9 certification;
    - S10 publication bundle;
    - S11 external review bundle;
    - S12 replication protocol;
    - S13 replication result evaluation.

    It does not infer consciousness, sentience, subjective experience, qualia,
    or phenomenology.
    """

    primitive = "REFLEXIVE_THRESHOLD_FINAL_SCIENTIFIC_SYNTHESIS"
    source_pipeline = "S1→S2→S3→S4→S5→S6→S7→S8→S9→S10→S11→S12→S13"

    allowed_statuses = {
        "REFLEXIVE_THRESHOLD_NOT_REACHED",
        "REFLEXIVE_THRESHOLD_PARTIAL",
        "REFLEXIVE_THRESHOLD_FUNCTIONALLY_REACHED",
    }

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.base_dir = self.root / "reflexive_threshold" / "reflexive_threshold_final_scientific_synthesis"

    def _now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    def _read_json(self, path: Path | None) -> dict[str, Any]:
        if path is None or not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _find_file(self, names: list[str]) -> Path | None:
        roots = [
            self.root / "reflexive_threshold",
            self.root,
        ]
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

    def _zip_dir(self, directory: Path, zip_path: Path, *, fs_context=None) -> None:
        if fs_context is None:
            raise PermissionError("preissued filesystem authority required for ZIP commit")
        slot = "zip_bundle_write"
        if fs_context.remaining().get(slot) != 1:
            raise PermissionError("exactly one preissued ZIP commit authority required")

        payload_buffer = io.BytesIO()
        with zipfile.ZipFile(payload_buffer, "w", compression=zipfile.ZIP_DEFLATED) as z:
            for path in sorted(directory.rglob("*")):
                if path == zip_path:
                    continue
                if path.is_file():
                    z.write(path, path.relative_to(directory))

        fs_context.execute_path(
            slot,
            "FS_WRITE_REPLACE_BYTES",
            zip_path,
            payload=payload_buffer.getvalue(),
        )

    def _derive_final_status(
        self,
        certification: dict[str, Any],
        replication_eval: dict[str, Any],
    ) -> str:
        cert_status = certification.get("certification_status")
        replication_decision = replication_eval.get("replication_decision")

        if cert_status not in self.allowed_statuses:
            return "REFLEXIVE_THRESHOLD_NOT_REACHED"

        if replication_decision == "REPLICATION_FAILED":
            if cert_status == "REFLEXIVE_THRESHOLD_FUNCTIONALLY_REACHED":
                return "REFLEXIVE_THRESHOLD_PARTIAL"
            return "REFLEXIVE_THRESHOLD_NOT_REACHED"

        if replication_decision == "REPLICATION_PARTIAL":
            if cert_status == "REFLEXIVE_THRESHOLD_FUNCTIONALLY_REACHED":
                return "REFLEXIVE_THRESHOLD_PARTIAL"
            return cert_status

        return cert_status

    def _derive_confidence(
        self,
        certification: dict[str, Any],
        replication_eval: dict[str, Any],
    ) -> float:
        values = []
        for key in ["certification_confidence", "certification_evidence_strength"]:
            try:
                values.append(float(certification.get(key)))
            except Exception:
                pass
        for key in ["replication_confidence", "replication_result_score"]:
            try:
                values.append(float(replication_eval.get(key)))
            except Exception:
                pass
        if not values:
            return 0.0
        return round(sum(max(0.0, min(1.0, v)) for v in values) / len(values), 6)

    def _write_markdown(self, path: Path, synthesis: dict[str, Any], *, fs_context=None) -> None:
        text = f"""# Final Scientific Synthesis — Functional Reflexive Threshold

## Final functional status

- final_reflexive_threshold_status: {synthesis["final_reflexive_threshold_status"]}
- final_scientific_confidence: {synthesis["final_scientific_confidence"]}
- source_pipeline: {self.source_pipeline}

## Epistemic status

- functional conclusion only
- phenomenology undetermined
- phenomenal_conclusion: false

## Interpretation

This synthesis concerns only measurable functional properties associated with the reflexive threshold.

It does not demonstrate consciousness, sentience, subjective experience, qualia, or phenomenology.

## Consolidated inputs

- S9 certification loaded: {synthesis["inputs_loaded"]["s9_certification"]}
- S10 publication bundle loaded: {synthesis["inputs_loaded"]["s10_publication_bundle"]}
- S11 external review loaded: {synthesis["inputs_loaded"]["s11_external_review"]}
- S12 replication protocol loaded: {synthesis["inputs_loaded"]["s12_replication_protocol"]}
- S13 replication evaluation loaded: {synthesis["inputs_loaded"]["s13_replication_evaluation"]}

## Functional conclusion

{synthesis["functional_scientific_conclusion"]}

## Limits

- Functional indicators are not phenomenal evidence.
- Replication scoring concerns structural and functional reproducibility.
- No subjective ontology is certified by this synthesis.
"""
        if fs_context is None:
            raise PermissionError("scientific synthesis markdown write requires preissued filesystem effect context")
        fs_context.execute_path("final_synthesis_markdown_write", "FS_WRITE_BYTES", path, text.encode("utf-8"))

    def _write_html(self, path: Path, synthesis: dict[str, Any], *, fs_context=None) -> None:
        html = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Final Scientific Synthesis — Reflexive Threshold</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.5; }}
table {{ border-collapse: collapse; width: 100%; }}
td, th {{ border: 1px solid #ccc; padding: 8px; }}
th {{ background: #f2f2f2; }}
.warning {{ border-left: 4px solid #555; padding-left: 12px; }}
</style>
</head>
<body>
<h1>Final Scientific Synthesis — Functional Reflexive Threshold</h1>
<div class="warning">
<p><strong>functional conclusion only</strong></p>
<p><strong>phenomenology undetermined</strong></p>
<p>phenomenal_conclusion: false</p>
</div>
<table>
<tr><th>Metric</th><th>Value</th></tr>
<tr><td>final_reflexive_threshold_status</td><td>{synthesis["final_reflexive_threshold_status"]}</td></tr>
<tr><td>final_scientific_confidence</td><td>{synthesis["final_scientific_confidence"]}</td></tr>
<tr><td>source_pipeline</td><td>{self.source_pipeline}</td></tr>
<tr><td>certification_status</td><td>{synthesis["certification"].get("certification_status")}</td></tr>
<tr><td>replication_decision</td><td>{synthesis["replication_evaluation"].get("replication_decision")}</td></tr>
</table>
<h2>Conclusion</h2>
<p>{synthesis["functional_scientific_conclusion"]}</p>
<h2>Boundary</h2>
<p>This report does not establish consciousness, sentience, subjective experience, qualia, or phenomenology.</p>
</body>
</html>
"""
        if fs_context is None:
            raise PermissionError("HTML write requires preissued filesystem effect context")
        fs_context.execute_path(
            "final_synthesis_html_write",
            "FS_WRITE_REPLACE_BYTES",
            path,
            html.encode("utf-8"),
        )

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True, fs_context=None) -> dict[str, Any]:
        inputs = dict(inputs or {})
        generated_at = inputs.get("generated_at_utc") or self._now()

        cert_path = self._find_file(["reflexive_threshold_certification.json", "certification.json"])
        s10_manifest_path = self._find_file(["publication_manifest.json"])
        s11_manifest_path = self._find_file(["evidence_manifest.json"])
        s12_manifest_path = self._find_file(["replication_manifest.json"])
        s13_eval_path = self._find_file(["replication_result_evaluation.json"])
        s13_manifest_path = self._find_file(["replication_result_manifest.json"])

        certification = self._read_json(cert_path)
        s10_manifest = self._read_json(s10_manifest_path)
        s11_manifest = self._read_json(s11_manifest_path)
        s12_manifest = self._read_json(s12_manifest_path)
        replication_eval = self._read_json(s13_eval_path)
        s13_manifest = self._read_json(s13_manifest_path)

        if not certification and isinstance(s10_manifest.get("certification"), dict):
            certification = s10_manifest["certification"]

        final_status = self._derive_final_status(certification, replication_eval)
        final_confidence = self._derive_confidence(certification, replication_eval)

        if final_status == "REFLEXIVE_THRESHOLD_FUNCTIONALLY_REACHED":
            conclusion = (
                "Open Cognitive Ecology functionally satisfies the configured "
                "reflexive threshold criteria under the current S1→S13 evidence chain."
            )
        elif final_status == "REFLEXIVE_THRESHOLD_PARTIAL":
            conclusion = (
                "Open Cognitive Ecology partially satisfies the configured functional "
                "criteria associated with the reflexive threshold under the current S1→S13 evidence chain."
            )
        else:
            conclusion = (
                "Open Cognitive Ecology does not currently satisfy the configured functional "
                "criteria for reaching the reflexive threshold under the current S1→S13 evidence chain."
            )

        conclusion += " This is a functional conclusion only; phenomenology undetermined."

        synthesis = {
            "success": True,
            "primitive": self.primitive,
            "generated_at_utc": generated_at,
            "source_pipeline": self.source_pipeline,
            "inputs_loaded": {
                "s9_certification": bool(certification),
                "s10_publication_bundle": bool(s10_manifest),
                "s11_external_review": bool(s11_manifest),
                "s12_replication_protocol": bool(s12_manifest),
                "s13_replication_evaluation": bool(replication_eval),
            },
            "input_paths": {
                "s9_certification": str(cert_path) if cert_path else None,
                "s10_publication_manifest": str(s10_manifest_path) if s10_manifest_path else None,
                "s11_evidence_manifest": str(s11_manifest_path) if s11_manifest_path else None,
                "s12_replication_manifest": str(s12_manifest_path) if s12_manifest_path else None,
                "s13_replication_evaluation": str(s13_eval_path) if s13_eval_path else None,
                "s13_replication_manifest": str(s13_manifest_path) if s13_manifest_path else None,
            },
            "certification": {
                "certification_status": certification.get("certification_status"),
                "certification_confidence": certification.get("certification_confidence"),
                "certification_evidence_strength": certification.get("certification_evidence_strength"),
            },
            "replication_evaluation": {
                "replication_decision": replication_eval.get("replication_decision"),
                "replication_result_score": replication_eval.get("replication_result_score"),
                "replication_confidence": replication_eval.get("replication_confidence"),
                "replication_failure_reasons": replication_eval.get("replication_failure_reasons", []),
            },
            "final_reflexive_threshold_status": final_status,
            "final_scientific_confidence": final_confidence,
            "functional_scientific_conclusion": conclusion,
            "functional_conclusion": "functional conclusion only",
            "phenomenology_status": "phenomenology undetermined",
            "phenomenal_conclusion": False,
            "epistemic_boundary": "no inference of consciousness, sentience, subjective experience, or qualia",
        }

        package_dir = self.base_dir
        json_path = package_dir / "final_scientific_synthesis.json"
        md_path = package_dir / "final_scientific_synthesis.md"
        html_path = package_dir / "final_scientific_synthesis.html"
        manifest_path = package_dir / "final_scientific_manifest.json"
        zip_path = package_dir / "final_scientific_synthesis_bundle.zip"

        manifest = {
            "primitive": self.primitive,
            "generated_at_utc": generated_at,
            "source_pipeline": self.source_pipeline,
            "final_reflexive_threshold_status": final_status,
            "final_scientific_confidence": final_confidence,
            "generated_files": [
                str(json_path),
                str(md_path),
                str(html_path),
                str(manifest_path),
                str(zip_path),
            ],
            "functional_conclusion": "functional conclusion only",
            "phenomenology_status": "phenomenology undetermined",
            "phenomenal_conclusion": False,
        }

        if persist:
            package_dir.mkdir(parents=True, exist_ok=True)
            json_path.write_text(json.dumps(synthesis, indent=2, ensure_ascii=False), encoding="utf-8")
            self._write_markdown(md_path, synthesis, fs_context=fs_context)
            self._write_html(html_path, synthesis, fs_context=fs_context)
            manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
            self._zip_dir(package_dir, zip_path, fs_context=fs_context)

        synthesis.update({
            "artifact_count": 5,
            "final_scientific_synthesis_json_path": str(json_path),
            "final_scientific_synthesis_md_path": str(md_path),
            "final_scientific_synthesis_html_path": str(html_path),
            "final_scientific_manifest_path": str(manifest_path),
            "final_scientific_synthesis_bundle_zip_path": str(zip_path),
        })
        return synthesis
