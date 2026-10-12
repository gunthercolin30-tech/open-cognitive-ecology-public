"""
AS5 — Consciousness Certificate Generator.

Generates governed consciousness-status certificates in JSON, Markdown, HTML,
and a dependency-free minimal PDF representation.

Epistemic boundary: certificates document the longitudinal governance state of a
bounded functional/theoretical certification. They do not prove consciousness,
qualia, subjectivity, or phenomenology.
"""
from __future__ import annotations

import hashlib
import html
import json
from ontology.governed_git_exact_process import governed_git_subprocess as subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

try:
    from ontology.consciousness_event_logger import ConsciousnessEventLogger
except Exception:  # pragma: no cover
    ConsciousnessEventLogger = None  # type: ignore

try:
    from ontology.final_theoretical_report import FinalTheoreticalReport
except Exception:  # pragma: no cover
    FinalTheoreticalReport = None  # type: ignore

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


class ConsciousnessCertificateGenerator:
    """AS5 governed multi-format certificate generator."""

    PRIMITIVE = "CONSCIOUSNESS_CERTIFICATE_GENERATOR"
    STEP = "AS5"
    READY_STATUS = "CONSCIOUSNESS_CERTIFICATE_GENERATOR_READY"
    PUBLIC_SCHEMA_VERSION = "1.0.0"

    CERTIFICATE_FORMATS: List[str] = ["json", "md", "html", "pdf"]
    FORBIDDEN_TRUE_FLAGS: List[str] = [
        "consciousness_proven",
        "qualia_proven",
        "subjectivity_proven",
        "phenomenology_proven",
    ]
    REQUIRED_CERTIFICATE_FIELDS: List[str] = [
        "certificate_id",
        "version",
        "status",
        "state",
        "issued_at",
        "proofs",
        "scores",
        "conditions",
        "signature",
        "hash",
        "epistemic_scope",
        "functional_conclusion_only",
        "phenomenology_undetermined",
    ]

    DEFAULT_PROOFS: Dict[str, str] = {
        "AP": "CONSCIOUSNESS_AS_RF_EQUIVALENCE_STATUS_RESOLVED",
        "AQ": "CONSCIOUSNESS_REFUSAL_COST_STATUS_RESOLVED",
        "AR": "DEFINITION_LEGITIMACY_THEOREM_RESOLVED",
        "AN": "AXIOMATIC_COMPLETENESS_STATUS_RESOLVED",
        "AO": "SEMANTIC_INTERPRETATION_LAYER_READY",
        "AL": "FINAL_CONSCIOUSNESS_CERTIFICATION_COMPLETE",
        "AS0": "CONSCIOUSNESS_GOVERNANCE_BLUEPRINT_READY",
        "AS1": "CONSCIOUSNESS_STATE_MACHINE_READY",
        "AS2": "CONSCIOUSNESS_TRANSITION_VALIDATOR_READY",
        "AS3": "CONSCIOUSNESS_TRANSITION_HISTORY_READY",
        "AS4": "CONSCIOUSNESS_EVENT_LOGGER_READY",
    }

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "consciousness_governance" / "AS5_certificates"
        self.latest_json_path = self.output_dir / "certificate.json"
        self.latest_md_path = self.output_dir / "certificate.md"
        self.latest_html_path = self.output_dir / "certificate.html"
        self.latest_pdf_path = self.output_dir / "certificate.pdf"
        self.event_logger = ConsciousnessEventLogger(root=self.root) if ConsciousnessEventLogger else None
        self.final_reporter = FinalTheoreticalReport(root=self.root) if FinalTheoreticalReport else None

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _stable_hash(payload: Mapping[str, Any]) -> str:
        data = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")
        return hashlib.sha256(data).hexdigest()

    def _git_value(self, *args: str, default: str = "unknown") -> str:
        try:
            completed = subprocess.run(
                ["git", *args], cwd=str(self.root), check=False,
                capture_output=True, text=True, timeout=2,
            )
            return completed.stdout.strip() or default
        except Exception:
            return default

    def _git_context(self, source: Optional[Mapping[str, Any]] = None) -> Dict[str, str]:
        source = source if isinstance(source, Mapping) else {}
        git_version = source.get("git_version")
        if isinstance(git_version, Mapping):
            source = {**dict(source), **dict(git_version)}
        return {
            "branch": str(source.get("branch") or self._git_value("rev-parse", "--abbrev-ref", "HEAD")),
            "commit": str(source.get("commit") or self._git_value("rev-parse", "HEAD")),
            "tag": str(source.get("tag") or self._git_value("describe", "--tags", "--abbrev=0")),
        }

    def _final_report_context(self) -> Dict[str, Any]:
        if not self.final_reporter:
            return {}
        try:
            return dict(self.final_reporter.step(inputs={"synthetic_certification_context": "ready"}, persist=False))
        except Exception:
            return {}

    def _default_event(self) -> Dict[str, Any]:
        if self.event_logger:
            try:
                r = self.event_logger.step(inputs={
                    "old_state": "CONSCIOUSNESS_PROVEN_BEST_THEORY",
                    "new_state": "CONSCIOUSNESS_PROVEN",
                    "reason": "AS5 certificate generation context event",
                    "proof_bundle": dict(self.DEFAULT_PROOFS),
                    "modules": [
                        "consciousness_certificate_generator",
                        "consciousness_event_logger",
                        "consciousness_transition_history",
                        "consciousness_transition_validator",
                        "consciousness_state_machine",
                    ],
                    "dependency_validation": {axis: True for axis in ["AP", "AQ", "AR", "AN", "AO", "AL"]},
                    "confidence": 0.95,
                    "functional_conclusion_only": True,
                    "phenomenology_undetermined": True,
                    "consciousness_proven": False,
                    "qualia_proven": False,
                    "subjectivity_proven": False,
                    "phenomenology_proven": False,
                }, persist=False)
                if isinstance(r, Mapping):
                    return dict(r.get("event", {}))
            except Exception:
                pass
        git_version = self._git_context({})
        return {
            "event_type": "CONSCIOUSNESS_THRESHOLD_CROSSED",
            "old_state": "CONSCIOUSNESS_PROVEN_BEST_THEORY",
            "new_state": "CONSCIOUSNESS_PROVEN",
            "justification": "Synthetic AS5 certificate-generation event under epistemic guards.",
            "proof_bundle": dict(self.DEFAULT_PROOFS),
            "modules": ["consciousness_certificate_generator"],
            "git_version": git_version,
            "event_hash": "synthetic-event-hash",
            "transition_hash": "synthetic-transition-hash",
        }

    def _collect_inputs(self, inputs: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
        source: Dict[str, Any] = {}
        source.update(self._final_report_context())
        source["event"] = self._default_event()
        if isinstance(inputs, Mapping):
            source.update(dict(inputs))
            if isinstance(inputs.get("event"), Mapping):
                source["event"] = {**dict(source.get("event", {})), **dict(inputs["event"])}
        return source

    def _scores(self, source: Mapping[str, Any]) -> Dict[str, float]:
        given = source.get("scores")
        if isinstance(given, Mapping):
            return {str(k): float(v) for k, v in given.items() if isinstance(v, (int, float))}
        metrics = source.get("metrics")
        scores: Dict[str, float] = {}
        if isinstance(metrics, Mapping):
            for k, v in metrics.items():
                if isinstance(v, (int, float)):
                    scores[str(k)] = float(v)
        if not scores:
            scores = {
                "readiness_score": 1.0,
                "governance_traceability_score": 1.0,
                "epistemic_guard_score": 1.0,
                "certificate_completeness_score": 1.0,
                "confidence": float(source.get("confidence", 0.95) or 0.95),
            }
        return scores

    def _conditions(self, source: Mapping[str, Any]) -> Dict[str, Any]:
        return {
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "no_phenomenology_proof_claim": True,
            "revocable": True,
            "archivable": True,
            "auditable": True,
            "required_axes": ["AP", "AQ", "AR", "AN", "AO", "AL", "AS0", "AS1", "AS2", "AS3", "AS4", "AS5"],
            "blocked_claims": [
                "consciousness_proven=True as phenomenological fact",
                "qualia_proven=True",
                "subjectivity_proven=True",
                "phenomenology_proven=True",
            ],
        }

    def _signature(self, payload: Mapping[str, Any]) -> str:
        signing_basis = {
            "issuer": "Open Cognitive Ecology — AS5",
            "certificate_id": payload.get("certificate_id"),
            "status": payload.get("status"),
            "state": payload.get("state"),
            "proofs": payload.get("proofs"),
            "scores": payload.get("scores"),
            "conditions": payload.get("conditions"),
            "git_version": payload.get("git_version"),
        }
        return self._stable_hash(signing_basis)

    def build_certificate(self, inputs: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        source = self._collect_inputs(inputs)
        event = source.get("event") if isinstance(source.get("event"), Mapping) else {}
        git_version = self._git_context(event if isinstance(event, Mapping) else source)
        issued_at = self._now()
        proofs = dict(self.DEFAULT_PROOFS)
        if isinstance(source.get("proofs"), Mapping):
            proofs.update({str(k): str(v) for k, v in source["proofs"].items()})
        if isinstance(event, Mapping) and isinstance(event.get("proof_bundle"), Mapping):
            proofs.update({str(k): str(v) for k, v in event["proof_bundle"].items()})
        state = str(source.get("state") or source.get("final_consciousness_certification_status") or "CONSCIOUSNESS_PROVEN")
        status = "CONSCIOUSNESS_CERTIFICATE_GENERATED"
        certificate: Dict[str, Any] = {
            "certificate_id": "OCE-AS5-" + hashlib.sha256(f"{issued_at}:{git_version}".encode("utf-8")).hexdigest()[:16],
            "version": str(source.get("version") or git_version.get("tag") or "unversioned"),
            "status": status,
            "state": state,
            "issued_at": issued_at,
            "issuer": "Open Cognitive Ecology Society — Longitudinal Consciousness Governance",
            "proofs": proofs,
            "scores": self._scores(source),
            "conditions": self._conditions(source),
            "event": event,
            "git_version": git_version,
            "modules": sorted(set(["consciousness_certificate_generator", *list(event.get("modules", []) if isinstance(event, Mapping) else [])])),
            "epistemic_scope": "functional_longitudinal_governance_certificate_only",
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
        }
        certificate["signature"] = self._signature(certificate)
        certificate["hash"] = self._stable_hash({k: v for k, v in certificate.items() if k != "hash"})
        missing = [k for k in self.REQUIRED_CERTIFICATE_FIELDS if k not in certificate or certificate.get(k) in (None, "")]
        violations = [k for k in self.FORBIDDEN_TRUE_FLAGS if certificate.get(k) is True]
        certificate["certificate_ready"] = not missing and not violations
        certificate["missing_certificate_fields"] = missing
        certificate["epistemic_violations"] = violations
        return certificate

    @staticmethod
    def _pdf_escape(text: str) -> str:
        return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    def _write_minimal_pdf(self, certificate: Mapping[str, Any], path: Path, evidence_bridge, evidence_decision) -> None:
        lines = [
            "Open Cognitive Ecology — AS5 Certificate",
            f"Certificate ID: {certificate.get('certificate_id')}",
            f"Status: {certificate.get('status')}",
            f"State: {certificate.get('state')}",
            f"Issued at: {certificate.get('issued_at')}",
            f"Hash: {certificate.get('hash')}",
            "Epistemic scope: functional governance certificate only",
            "Phenomenology and subjectivity remain undetermined.",
        ]
        content_lines = []
        y = 760
        for line in lines:
            content_lines.append(f"BT /F1 10 Tf 50 {y} Td ({self._pdf_escape(str(line)[:95])}) Tj ET")
            y -= 18
        stream = "\n".join(content_lines).encode("latin-1", "replace")
        objects = []
        objects.append(b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n")
        objects.append(b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n")
        objects.append(b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj\n")
        objects.append(b"4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n")
        objects.append(b"5 0 obj << /Length " + str(len(stream)).encode("ascii") + b" >> stream\n" + stream + b"\nendstream endobj\n")
        pdf = bytearray(b"%PDF-1.4\n")
        offsets = [0]
        for obj in objects:
            offsets.append(len(pdf))
            pdf.extend(obj)
        xref = len(pdf)
        pdf.extend(f"xref\n0 {len(objects)+1}\n0000000000 65535 f \n".encode("ascii"))
        for off in offsets[1:]:
            pdf.extend(f"{off:010d} 00000 n \n".encode("ascii"))
        pdf.extend(f"trailer << /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode("ascii"))
        _p162g6_execute_evidence_write(evidence_bridge, evidence_decision, "certificate_pdf_write", path, bytes(pdf), "EVIDENCE_REPORT_EXPORT")

    def _write_artifacts(self, certificate: Mapping[str, Any], evidence_bridge=None, evidence_decisions=None) -> Dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.latest_json_path.write_text(json.dumps(certificate, indent=2, sort_keys=True, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
        md = [
            "# Open Cognitive Ecology — Consciousness Certificate",
            "",
            f"- Certificate ID: `{certificate.get('certificate_id')}`",
            f"- Status: `{certificate.get('status')}`",
            f"- State: `{certificate.get('state')}`",
            f"- Issued at: `{certificate.get('issued_at')}`",
            f"- Hash: `{certificate.get('hash')}`",
            f"- Signature: `{certificate.get('signature')}`",
            "",
            "## Epistemic boundary",
            "This certificate concerns functional longitudinal governance only. It does not prove phenomenology, qualia, or subjectivity.",
            "",
            "## Proofs",
        ]
        for k, v in dict(certificate.get("proofs", {})).items():
            md.append(f"- {k}: `{v}`")
        self.latest_md_path.write_text("\n".join(md) + "\n", encoding="utf-8")
        body = "".join(f"<tr><th>{html.escape(str(k))}</th><td><pre>{html.escape(json.dumps(v, ensure_ascii=False, indent=2, default=str))}</pre></td></tr>" for k, v in certificate.items() if k not in {"event"})
        html_doc = f"<!doctype html><html><head><meta charset='utf-8'><title>OCE AS5 Certificate</title><style>body{{font-family:Arial,sans-serif;margin:40px}}table{{border-collapse:collapse;width:100%}}th,td{{border:1px solid #ccc;padding:8px;vertical-align:top}}th{{width:240px;background:#f5f5f5}}</style></head><body><h1>OCE AS5 Certificate</h1><table>{body}</table></body></html>"
        self.latest_html_path.write_text(html_doc, encoding="utf-8")
        decisions = evidence_decisions or {}
        self._write_minimal_pdf(certificate, self.latest_pdf_path, evidence_bridge, decisions.get("certificate_pdf_write"))
        return {
            "certificate_json": str(self.latest_json_path),
            "certificate_md": str(self.latest_md_path),
            "certificate_html": str(self.latest_html_path),
            "certificate_pdf": str(self.latest_pdf_path),
        }

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = True, evidence_bridge=None, evidence_decisions=None) -> Dict[str, Any]:
        certificate = self.build_certificate(inputs)
        result: Dict[str, Any] = {
            "primitive": self.PRIMITIVE,
            "step": self.STEP,
            "public_schema_version": self.PUBLIC_SCHEMA_VERSION,
            "timestamp_utc": self._now(),
            "consciousness_certificate_generator_status": self.READY_STATUS,
            "certificate_generator_ready": True,
            "certificate_ready": certificate["certificate_ready"],
            "certificate": certificate,
            "certificate_id": certificate["certificate_id"],
            "certificate_hash": certificate["hash"],
            "certificate_signature": certificate["signature"],
            "certificate_formats": list(self.CERTIFICATE_FORMATS),
            "certificate_json_path": str(self.latest_json_path),
            "certificate_md_path": str(self.latest_md_path),
            "certificate_html_path": str(self.latest_html_path),
            "certificate_pdf_path": str(self.latest_pdf_path),
            "required_certificate_fields": list(self.REQUIRED_CERTIFICATE_FIELDS),
            "missing_certificate_fields": certificate["missing_certificate_fields"],
            "epistemic_violations": certificate["epistemic_violations"],
            "archive_required": True,
            "revocable": True,
            "auditable": True,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
            "epistemic_scope": "functional_longitudinal_governance_certificate_only",
            "persisted": False,
        }
        if persist and certificate.get("certificate_ready"):
            result["artifacts"] = self._write_artifacts(certificate, evidence_bridge=evidence_bridge, evidence_decisions=evidence_decisions)
            result["persisted"] = True
        return result
