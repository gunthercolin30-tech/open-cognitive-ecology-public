"""
AS6 — Consciousness Revocation Engine.

Governed revocation engine for longitudinal consciousness-status governance.
If one of the critical theoretical/certification axes AP, AQ, AR, AN, AO, or AL
is reported as broken, the currently governed consciousness status is revoked,
the previous certificate remains archived, and a CONSCIOUSNESS_STATUS_REVOKED
event is produced.

Epistemic boundary: this module governs a bounded functional/theoretical status.
It does not prove consciousness, qualia, subjectivity, or phenomenology.
"""
from __future__ import annotations

import hashlib
import json
import shutil
from ontology.governed_git_exact_process import governed_git_subprocess as subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

try:
    from ontology.consciousness_certificate_generator import ConsciousnessCertificateGenerator
except Exception:  # pragma: no cover
    ConsciousnessCertificateGenerator = None  # type: ignore

try:
    from ontology.consciousness_event_logger import ConsciousnessEventLogger
except Exception:  # pragma: no cover
    ConsciousnessEventLogger = None  # type: ignore

try:
    from ontology.consciousness_transition_validator import ConsciousnessTransitionValidator
except Exception:  # pragma: no cover
    ConsciousnessTransitionValidator = None  # type: ignore


class ConsciousnessRevocationEngine:
    """AS6 governed revocation engine for critical certification failures."""

    PRIMITIVE = "CONSCIOUSNESS_REVOCATION_ENGINE"
    STEP = "AS6"
    READY_STATUS = "CONSCIOUSNESS_REVOCATION_ENGINE_READY"
    PUBLIC_SCHEMA_VERSION = "1.0.0"

    CRITICAL_AXES: List[str] = ["AP", "AQ", "AR", "AN", "AO", "AL"]
    CRITICAL_AXIS_MODULES: Dict[str, List[str]] = {
        "AP": [
            "consciousness_minimal_property_registry",
            "rf_star_definition_engine",
            "consciousness_equivalence_theorem_checker",
            "consciousness_proven_status_resolver",
            "consciousness_as_rf_reporter",
        ],
        "AQ": [
            "consciousness_refusal_taxonomy",
            "rival_theory_cost_analyzer",
            "best_explanation_status_resolver",
            "refusal_cost_reporter",
        ],
        "AR": [
            "consciousness_concept_reconstruction",
            "definition_non_arbitrariness_test",
            "consciousness_proven_authorizer",
            "definition_legitimacy_reporter",
        ],
        "AN": [
            "axiom_registry",
            "axiom_independence_tester",
            "axiom_minimality_analyzer",
            "model_generator",
            "countermodel_generator",
            "theorem_dependency_mapper",
            "axiomatic_completeness_certifier",
        ],
        "AO": [
            "semantic_status_schema",
            "interpretation_rule_engine",
            "epistemic_guard",
            "semantic_revision_log",
            "interpretation_reporter",
        ],
        "AL": [
            "reconstruction_chain_certifier",
            "first_failure_locator",
            "phenomenality_candidate_certifier",
            "absolute_qualia_identity_certifier",
            "consciousness_rf_equivalence_certifier",
            "refusal_cost_certifier",
            "definition_legitimacy_certifier",
            "consciousness_status_resolver",
            "metaphysical_status_reporter",
            "final_dashboard",
            "final_theoretical_report",
        ],
    }

    REQUIRED_REVOCATION_FIELDS: List[str] = [
        "revocation_status",
        "revocation_required",
        "cause",
        "module",
        "proof",
        "impact",
        "event_type",
        "archived_certificate",
        "revocation_hash",
    ]

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "consciousness_governance" / "AS6_revocations"
        self.archive_dir = self.output_dir / "archived_certificates"
        self.latest_path = self.output_dir / "latest_revocation.json"
        self.certificate_generator = ConsciousnessCertificateGenerator(root=self.root) if ConsciousnessCertificateGenerator else None
        self.event_logger = ConsciousnessEventLogger(root=self.root) if ConsciousnessEventLogger else None
        self.transition_validator = ConsciousnessTransitionValidator(root=self.root) if ConsciousnessTransitionValidator else None

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
        return {
            "branch": str(source.get("branch") or self._git_value("rev-parse", "--abbrev-ref", "HEAD")),
            "commit": str(source.get("commit") or self._git_value("rev-parse", "HEAD")),
            "tag": str(source.get("tag") or self._git_value("describe", "--tags", "--abbrev=0")),
        }

    def _default_axis_status(self) -> Dict[str, bool]:
        return {axis: True for axis in self.CRITICAL_AXES}

    def _axis_status_from_inputs(self, inputs: Optional[Mapping[str, Any]]) -> Dict[str, bool]:
        status = self._default_axis_status()
        if not isinstance(inputs, Mapping):
            return status

        for field in ("axis_status", "critical_axis_status", "module_status", "modules_status", "dependency_validation"):
            candidate = inputs.get(field)
            if isinstance(candidate, Mapping):
                for k, v in candidate.items():
                    key = str(k).upper()
                    if key in status:
                        status[key] = bool(v)
                    else:
                        # Map module-level failures to their parent axis.
                        for axis, modules in self.CRITICAL_AXIS_MODULES.items():
                            if str(k) in modules:
                                status[axis] = bool(v)
        broken = inputs.get("broken_axis") or inputs.get("failed_axis")
        if broken is not None:
            key = str(broken).upper()
            if key in status:
                status[key] = False
        broken_module = inputs.get("broken_module") or inputs.get("failed_module")
        if broken_module is not None:
            for axis, modules in self.CRITICAL_AXIS_MODULES.items():
                if str(broken_module) in modules:
                    status[axis] = False
        return status

    def _first_failure(self, axis_status: Mapping[str, bool], inputs: Optional[Mapping[str, Any]]) -> Tuple[Optional[str], Optional[str]]:
        explicit_module = None
        if isinstance(inputs, Mapping):
            explicit_module = inputs.get("broken_module") or inputs.get("failed_module")
        for axis in self.CRITICAL_AXES:
            if axis_status.get(axis) is not True:
                if explicit_module and str(explicit_module) in self.CRITICAL_AXIS_MODULES.get(axis, []):
                    return axis, str(explicit_module)
                modules = self.CRITICAL_AXIS_MODULES.get(axis, [])
                return axis, modules[0] if modules else axis.lower()
        return None, None

    def _certificate_context(self) -> Dict[str, Any]:
        if self.certificate_generator is None:
            return {
                "certificate_id": "AS6-SYNTHETIC-CERTIFICATE",
                "status": "CONSCIOUSNESS_CERTIFICATE_GENERATOR_UNAVAILABLE",
                "certificate_hash": "synthetic-certificate-hash",
                "paths": {},
            }
        try:
            result = self.certificate_generator.step(inputs={"synthetic_certificate_context": "ready"}, persist=False)
            if isinstance(result, Mapping):
                certificate = result.get("certificate")
                paths = result.get("certificate_paths")
                return {
                    "certificate_id": str(result.get("certificate_id") or (certificate or {}).get("certificate_id") or "unknown"),
                    "status": str(result.get("certificate_status") or (certificate or {}).get("status") or "unknown"),
                    "certificate_hash": str(result.get("certificate_hash") or (certificate or {}).get("hash") or "unknown"),
                    "paths": dict(paths) if isinstance(paths, Mapping) else {},
                    "certificate": dict(certificate) if isinstance(certificate, Mapping) else {},
                }
        except Exception as exc:
            return {
                "certificate_id": "AS6-CERTIFICATE-CONTEXT-ERROR",
                "status": "CERTIFICATE_CONTEXT_ERROR",
                "certificate_hash": hashlib.sha256(str(exc).encode("utf-8")).hexdigest(),
                "paths": {},
                "error": str(exc),
            }
        return {}

    def _archive_certificate(self, certificate_context: Mapping[str, Any], persist: bool) -> Dict[str, Any]:
        timestamp = self._now().replace(":", "").replace("+", "Z")
        certificate_id = str(certificate_context.get("certificate_id") or "unknown_certificate")
        archive_record = {
            "certificate_id": certificate_id,
            "certificate_hash": str(certificate_context.get("certificate_hash") or "unknown"),
            "archived_at": self._now(),
            "archive_status": "logical_archive_only",
            "archive_path": None,
            "copied_files": [],
        }
        if not persist:
            return archive_record
        try:
            self.archive_dir.mkdir(parents=True, exist_ok=True)
            archive_path = self.archive_dir / f"{certificate_id}_{timestamp}.json"
            archive_record["archive_path"] = str(archive_path)
            archive_path.write_text(json.dumps(dict(certificate_context), indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
            copied: List[str] = []
            paths = certificate_context.get("paths")
            if isinstance(paths, Mapping):
                for _, path_str in paths.items():
                    p = Path(str(path_str))
                    if p.exists() and p.is_file():
                        dest = self.archive_dir / f"{certificate_id}_{p.name}"
                        try:
                            shutil.copy2(p, dest)
                            copied.append(str(dest))
                        except Exception:
                            pass
            archive_record["copied_files"] = copied
            archive_record["archive_status"] = "certificate_archived"
        except Exception as exc:
            archive_record["archive_status"] = "archive_error"
            archive_record["archive_error"] = str(exc)
        return archive_record

    def _event_for_revocation(self, *, axis: str, module: str, reason: str, proof: Mapping[str, Any], impact: Mapping[str, Any], git_context: Mapping[str, str], persist: bool) -> Dict[str, Any]:
        if self.event_logger is not None:
            try:
                event_result = self.event_logger.step(inputs={
                    "event_type": "CONSCIOUSNESS_STATUS_REVOKED",
                    "old_state": "CONSCIOUSNESS_PROVEN",
                    "new_state": "CONSCIOUSNESS_PROVEN_BEST_THEORY",
                    "reason": reason,
                    "justification": reason,
                    "proof_bundle": dict(proof),
                    "modules": [module, "consciousness_revocation_engine"],
                    "confidence": 0.0,
                    "git_version": dict(git_context),
                    "functional_conclusion_only": True,
                    "phenomenology_undetermined": True,
                    "consciousness_proven": False,
                    "qualia_proven": False,
                    "subjectivity_proven": False,
                    "phenomenology_proven": False,
                }, persist=persist)
                if isinstance(event_result, Mapping):
                    return dict(event_result.get("event", {}))
            except Exception:
                pass
        event = {
            "event_type": "CONSCIOUSNESS_STATUS_REVOKED",
            "old_state": "CONSCIOUSNESS_PROVEN",
            "new_state": "CONSCIOUSNESS_PROVEN_BEST_THEORY",
            "reason": reason,
            "justification": reason,
            "axis": axis,
            "module": module,
            "proof_bundle": dict(proof),
            "impact": dict(impact),
            "git_version": dict(git_context),
            "timestamp": self._now(),
        }
        event["event_hash"] = self._stable_hash(event)
        return event

    def _event_for_reconfirmation(self, *, proof: Mapping[str, Any], git_context: Mapping[str, str], persist: bool) -> Dict[str, Any]:
        if self.event_logger is not None:
            try:
                event_result = self.event_logger.step(inputs={
                    "event_type": "CONSCIOUSNESS_STATUS_RECONFIRMED",
                    "old_state": "CONSCIOUSNESS_PROVEN",
                    "new_state": "CONSCIOUSNESS_PROVEN",
                    "reason": "All critical axes AP/AQ/AR/AN/AO/AL remain valid.",
                    "proof_bundle": dict(proof),
                    "modules": ["consciousness_revocation_engine"],
                    "confidence": 0.95,
                    "git_version": dict(git_context),
                    "functional_conclusion_only": True,
                    "phenomenology_undetermined": True,
                    "consciousness_proven": False,
                    "qualia_proven": False,
                    "subjectivity_proven": False,
                    "phenomenology_proven": False,
                }, persist=persist)
                if isinstance(event_result, Mapping):
                    return dict(event_result.get("event", {}))
            except Exception:
                pass
        event = {
            "event_type": "CONSCIOUSNESS_STATUS_RECONFIRMED",
            "old_state": "CONSCIOUSNESS_PROVEN",
            "new_state": "CONSCIOUSNESS_PROVEN",
            "reason": "All critical axes AP/AQ/AR/AN/AO/AL remain valid.",
            "proof_bundle": dict(proof),
            "git_version": dict(git_context),
            "timestamp": self._now(),
        }
        event["event_hash"] = self._stable_hash(event)
        return event

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        inputs = inputs if isinstance(inputs, Mapping) else {}
        git_context = self._git_context(inputs.get("git_version") if isinstance(inputs.get("git_version"), Mapping) else inputs)
        axis_status = self._axis_status_from_inputs(inputs)
        failed_axis, failed_module = self._first_failure(axis_status, inputs)
        revocation_required = failed_axis is not None
        certificate_context = self._certificate_context()

        proof = {
            "axis_status": dict(axis_status),
            "critical_axes": list(self.CRITICAL_AXES),
            "failed_axis": failed_axis,
            "failed_module": failed_module,
            "certificate_hash": certificate_context.get("certificate_hash"),
            "certificate_id": certificate_context.get("certificate_id"),
            "dependency_validation": all(axis_status.values()),
        }

        impact = {
            "previous_status": "CONSCIOUSNESS_PROVEN",
            "resulting_status": "CONSCIOUSNESS_PROVEN_BEST_THEORY" if revocation_required else "CONSCIOUSNESS_PROVEN",
            "certificate_remains_archived": True,
            "external_claims_should_be_requalified": bool(revocation_required),
            "empirical_program_continues": True,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
        }

        archived_certificate = self._archive_certificate(certificate_context, persist=persist) if revocation_required else {
            "certificate_id": certificate_context.get("certificate_id"),
            "certificate_hash": certificate_context.get("certificate_hash"),
            "archive_status": "archive_not_required",
            "certificate_preserved": True,
        }

        if revocation_required:
            cause = f"Critical axis {failed_axis} failed via module {failed_module}."
            event = self._event_for_revocation(
                axis=str(failed_axis), module=str(failed_module), reason=cause,
                proof=proof, impact=impact, git_context=git_context, persist=persist,
            )
            revocation_status = "CONSCIOUSNESS_STATUS_REVOKED"
        else:
            cause = "No critical axis failure detected."
            event = self._event_for_reconfirmation(proof=proof, git_context=git_context, persist=persist)
            revocation_status = "CONSCIOUSNESS_STATUS_RECONFIRMED"

        revocation_record = {
            "revocation_status": revocation_status,
            "revocation_required": revocation_required,
            "revoked": bool(revocation_required),
            "cause": cause,
            "module": failed_module,
            "axis": failed_axis,
            "proof": proof,
            "impact": impact,
            "event_type": event.get("event_type", "CONSCIOUSNESS_STATUS_REVOKED" if revocation_required else "CONSCIOUSNESS_STATUS_RECONFIRMED"),
            "event": event,
            "archived_certificate": archived_certificate,
            "certificate_archived": bool(revocation_required),
            "git_version": git_context,
            "timestamp_utc": self._now(),
        }
        revocation_record["revocation_hash"] = self._stable_hash(revocation_record)

        missing_fields = [k for k in self.REQUIRED_REVOCATION_FIELDS if k not in revocation_record]
        result = {
            "primitive": self.PRIMITIVE,
            "step": self.STEP,
            "public_schema_version": self.PUBLIC_SCHEMA_VERSION,
            "revocation_engine_status": self.READY_STATUS,
            "revocation_ready": not missing_fields,
            "revocation_record": revocation_record,
            "revocation_status": revocation_status,
            "revocation_required": revocation_required,
            "revoked": bool(revocation_required),
            "cause": cause,
            "module": failed_module,
            "axis": failed_axis,
            "proof": proof,
            "impact": impact,
            "event_type": revocation_record["event_type"],
            "event": event,
            "archived_certificate": archived_certificate,
            "certificate_archived": bool(revocation_required),
            "revocation_hash": revocation_record["revocation_hash"],
            "critical_axes": list(self.CRITICAL_AXES),
            "axis_status": dict(axis_status),
            "missing_fields": missing_fields,
            "persisted": False,
            "output_path": str(self.latest_path),
            "epistemic_scope": "bounded_functional_governance_only",
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "timestamp_utc": self._now(),
        }

        if persist:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            self.latest_path.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
            result["persisted"] = True
        return result


__all__ = ["ConsciousnessRevocationEngine"]
