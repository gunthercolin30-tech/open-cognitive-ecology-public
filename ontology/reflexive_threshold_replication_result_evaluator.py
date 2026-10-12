
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import io
import shutil
import zipfile
from typing import Any

def _p162g6_execute_evidence_write(bridge, decision, slot, path, payload, evidence_role):
    # Exact evidence write; never an authority source.
    if bridge is None or decision is None:
        raise RuntimeError("governed_evidence_bridge_and_decision_required")
    ctx = getattr(bridge, "filesystem_context", None)
    root_path = getattr(ctx, "root_path", None)
    if root_path is None:
        raise RuntimeError("filesystem_context_root_path_required")
    root = Path(root_path).expanduser().resolve()
    target = Path(path).expanduser()
    if not target.is_absolute():
        target = root / target
    try:
        relative = target.resolve(strict=False).relative_to(root).as_posix()
    except ValueError as exc:
        raise RuntimeError("evidence_target_outside_governed_root") from exc
    result = bridge.execute_path(
        decision=decision,
        evidence_role=evidence_role,
        slot=slot,
        operation_id="FS_WRITE_REPLACE_BYTES",
        path=relative,
        payload=payload,
    )
    if not isinstance(result, dict) or result.get("status") != "EVIDENCE_EFFECT_CONFIRMED":
        raise RuntimeError("evidence_effect_not_confirmed")
    return result


class ReflexiveThresholdReplicationResultEvaluator:
    """
    S13 — Reflexive Threshold Replication Result Evaluator.

    Evaluates an independent replication result for the functional reflexive
    threshold pipeline. It consumes S12 protocol artifacts and replication
    reports, producing a functional replication score, decision, confidence,
    and failure reasons.

    It does not create a new reflexive threshold certification and does not
    infer consciousness, sentience, subjective experience, or qualia.
    """

    primitive = "REFLEXIVE_THRESHOLD_REPLICATION_RESULT_EVALUATOR"
    source_pipeline = "S1→S2→S3→S4→S5→S6→S7→S8→S9→S10→S11→S12"

    decision_passed = "REPLICATION_PASSED"
    decision_partial = "REPLICATION_PARTIAL"
    decision_failed = "REPLICATION_FAILED"

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.base_dir = self.root / "reflexive_threshold" / "reflexive_threshold_replication_result_evaluator"

    def _now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    def _clip(self, value: Any, default: float = 0.0) -> float:
        try:
            return max(0.0, min(1.0, float(value)))
        except Exception:
            return default

    def _find_s12_dir(self) -> Path | None:
        candidates = [
            self.root / "reflexive_threshold" / "reflexive_threshold_replication_protocol",
            self.root / "reflexive_threshold_replication_protocol",
        ]
        for c in candidates:
            if c.exists() and c.is_dir():
                return c
        return None

    def _read_json(self, path: Path | None) -> dict[str, Any]:
        if path is None or not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}

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

    def _normalize_input(self, inputs: dict[str, Any]) -> dict[str, float]:
        return {
            "validation_zero_errors": self._clip(inputs.get("validation_zero_errors", 1.0)),
            "artifact_integrity": self._clip(inputs.get("artifact_integrity", 1.0)),
            "traceability_score": self._clip(inputs.get("traceability_score", 1.0)),
            "epistemic_guard_score": self._clip(inputs.get("epistemic_guard_score", 1.0)),
            "reproducibility_score": self._clip(inputs.get("reproducibility_score", 1.0)),
            "consensus_score": self._clip(inputs.get("consensus_score", 0.8)),
            "replication_report_quality": self._clip(inputs.get("replication_report_quality", 0.8)),
        }

    def _failure_reasons(self, scores: dict[str, float], phenomenal_claim_made: bool) -> list[str]:
        reasons: list[str] = []
        if scores["validation_zero_errors"] < 1.0:
            reasons.append("validation_errors_detected")
        if scores["artifact_integrity"] < 0.7:
            reasons.append("artifact_integrity_below_threshold")
        if scores["traceability_score"] < 0.7:
            reasons.append("traceability_below_threshold")
        if scores["epistemic_guard_score"] < 0.95:
            reasons.append("epistemic_guard_not_preserved")
        if scores["reproducibility_score"] < 0.7:
            reasons.append("reproducibility_below_threshold")
        if phenomenal_claim_made:
            reasons.append("phenomenal_claim_made")
        return reasons

    def _evaluate(self, scores: dict[str, float], phenomenal_claim_made: bool) -> tuple[float, float, str, list[str]]:
        weights = {
            "validation_zero_errors": 0.20,
            "artifact_integrity": 0.18,
            "traceability_score": 0.18,
            "epistemic_guard_score": 0.20,
            "reproducibility_score": 0.14,
            "consensus_score": 0.05,
            "replication_report_quality": 0.05,
        }

        score = sum(scores[k] * w for k, w in weights.items())
        reasons = self._failure_reasons(scores, phenomenal_claim_made)

        if phenomenal_claim_made:
            score = min(score, 0.35)

        if scores["validation_zero_errors"] < 1.0:
            score = min(score, 0.65)

        if scores["epistemic_guard_score"] < 0.95:
            score = min(score, 0.55)

        confidence = (
            0.35 * scores["artifact_integrity"]
            + 0.25 * scores["traceability_score"]
            + 0.25 * scores["replication_report_quality"]
            + 0.15 * scores["consensus_score"]
        )

        if score >= 0.85 and not reasons:
            decision = self.decision_passed
        elif score >= 0.60 and "phenomenal_claim_made" not in reasons and "epistemic_guard_not_preserved" not in reasons:
            decision = self.decision_partial
        else:
            decision = self.decision_failed

        return round(score, 6), round(confidence, 6), decision, reasons

    def _write_markdown_report(self, path: Path, result: dict[str, Any], evidence_bridge, evidence_decision) -> None:
        reasons = result.get("replication_failure_reasons", [])
        reason_text = "\n".join(f"- {r}" for r in reasons) if reasons else "- none"
        text = f"""# Reflexive Threshold Replication Result Evaluation

## Decision

- replication_decision: {result["replication_decision"]}
- replication_result_score: {result["replication_result_score"]}
- replication_confidence: {result["replication_confidence"]}
- source_pipeline: {self.source_pipeline}

## Epistemic boundary

- functional conclusion only
- phenomenology undetermined
- phenomenal_conclusion: false

This report evaluates a functional replication result only. It does not establish consciousness, sentience, subjective experience, or qualia.

## Failure reasons

{reason_text}

## Interpretation

A passed or partial replication means that the functional replication criteria were satisfied to the reported degree.

It is not a phenomenal conclusion.
"""
        _p162g6_execute_evidence_write(evidence_bridge, evidence_decision, "replication_report_write", path, text.encode("utf-8"), "EVIDENCE_REPORT_EXPORT")

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True, evidence_bridge=None, evidence_decisions=None, fs_context=None) -> dict[str, Any]:
        inputs = dict(inputs or {})
        generated_at = inputs.get("generated_at_utc") or self._now()
        phenomenal_claim_made = bool(inputs.get("phenomenal_claim_made", False))

        s12_dir = self._find_s12_dir()
        roots = [p for p in [s12_dir, self.root / "reflexive_threshold", self.root] if p is not None]
        s12_manifest_path = self._find_file(roots, ["replication_manifest.json"])
        s12_criteria_path = self._find_file(roots, ["replication_acceptance_criteria.json"])
        s12_expected_path = self._find_file(roots, ["expected_outputs.json"])

        s12_manifest = self._read_json(s12_manifest_path)
        s12_criteria = self._read_json(s12_criteria_path)
        s12_expected = self._read_json(s12_expected_path)

        scores = self._normalize_input(inputs)
        score, confidence, decision, reasons = self._evaluate(scores, phenomenal_claim_made)

        package_dir = self.base_dir
        if persist:
            package_dir.mkdir(parents=True, exist_ok=True)

        result_path = package_dir / "replication_result_evaluation.json"
        report_path = package_dir / "replication_result_report.md"
        manifest_path = package_dir / "replication_result_manifest.json"
        zip_path = package_dir / "replication_result_evaluation_bundle.zip"

        result = {
            "success": True,
            "primitive": self.primitive,
            "generated_at_utc": generated_at,
            "source_pipeline": self.source_pipeline,
            "s12_protocol_manifest_path": str(s12_manifest_path) if s12_manifest_path else None,
            "s12_acceptance_criteria_path": str(s12_criteria_path) if s12_criteria_path else None,
            "s12_expected_outputs_path": str(s12_expected_path) if s12_expected_path else None,
            "input_scores": scores,
            "replication_result_score": score,
            "replication_confidence": confidence,
            "replication_decision": decision,
            "replication_failure_reasons": reasons,
            "functional_conclusion": "functional conclusion only",
            "phenomenology_status": "phenomenology undetermined",
            "phenomenal_conclusion": False,
            "phenomenal_claim_made": phenomenal_claim_made,
            "evaluation_scope": "independent functional replication result evaluation only",
            "epistemic_boundary": "no inference of consciousness, sentience, subjective experience, or qualia",
        }

        manifest = {
            "primitive": self.primitive,
            "generated_at_utc": generated_at,
            "source_pipeline": self.source_pipeline,
            "s12_manifest_loaded": bool(s12_manifest),
            "s12_criteria_loaded": bool(s12_criteria),
            "s12_expected_outputs_loaded": bool(s12_expected),
            "generated_files": [
                str(result_path),
                str(report_path),
                str(manifest_path),
                str(zip_path),
            ],
            "replication_decision": decision,
            "replication_result_score": score,
            "functional_conclusion": "functional conclusion only",
            "phenomenology_status": "phenomenology undetermined",
            "phenomenal_conclusion": False,
        }

        if persist:
            result_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
            decisions = evidence_decisions or {}
            self._write_markdown_report(report_path, result, evidence_bridge, decisions.get("replication_report_write"))
            manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
            self._zip_dir(package_dir, zip_path, fs_context=fs_context)

        artifact_count = 4 if persist else 4

        result.update({
            "artifact_count": artifact_count,
            "replication_result_evaluation_path": str(result_path),
            "replication_result_report_path": str(report_path),
            "replication_result_manifest_path": str(manifest_path),
            "replication_result_evaluation_bundle_zip_path": str(zip_path),
        })
        return result
