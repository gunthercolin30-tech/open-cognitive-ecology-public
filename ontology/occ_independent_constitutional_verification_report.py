from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
import tempfile
from typing import Any, Dict

from ontology import occ_independent_constitutional_verifier as verifier

SCHEMA = "oce.p159.occ1f.independent_constitutional_verification_report.v1"
MILESTONE = "P159/OCC-1F"
REPORT_REL = Path("validation_artifacts/p159/occ1f/independent_constitutional_verification_report_v1.json")

def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def _canonical_hash(value: Any) -> str:
    return sha256(_canonical_bytes(value)).hexdigest()

def _file_sha(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()

def _snapshot(paths):
    out = {}
    for path in paths:
        path = Path(path)
        out[str(path)] = _file_sha(path) if path.is_file() else None
    return out

def build_report(root: Path) -> Dict[str, Any]:
    root = Path(root)
    v = verifier.verify(root)
    findings = list(v.get("findings", []))
    counts = {k: 0 for k in ("PASS", "FAIL", "INCONCLUSIVE", "SKIPPED")}
    registry = []
    for item in findings:
        status = item.get("status", "INCONCLUSIVE")
        if status not in counts:
            status = "INCONCLUSIVE"
        counts[status] += 1
        registry.append({
            "check_id": item.get("check_id"),
            "status": status,
            "reason": item.get("reason"),
            "evidence": item.get("evidence"),
        })

    report = {
        "schema": SCHEMA,
        "milestone": MILESTONE,
        "report_role": "INDEPENDENT_DIAGNOSTIC_EVIDENCE",
        "verdict": v.get("verdict"),
        "verdict_reason": v.get("reason"),
        "verified_profile": {
            "path": "validation_artifacts/p159/occ1e/compiled_normative_profile_v1.json",
            "file_sha256": v.get("profile_artifact_sha256"),
            "semantic_hash": v.get("profile_semantic_hash"),
            "independently_reconstructed_nir_sha256": v.get("source_nir_sha256"),
        },
        "check_registry": registry,
        "check_counts": counts,
        "failed_check_ids": list(v.get("failed_check_ids", [])),
        "inconclusive_check_ids": list(v.get("inconclusive_check_ids", [])),
        "common_tcb": list(v.get("common_tcb", [])),
        "independence": {
            "compiler_imported": bool(v.get("compiler_imported", False)),
            "static_checker_imported": bool(v.get("static_checker_imported", False)),
            "occ1e_builder_imported": bool(v.get("occ1e_builder_imported", False)),
            "compiler_hash_trusted_without_recalculation": bool(v.get("compiler_hash_trusted_without_recalculation", False)),
            "repair_performed": bool(v.get("repair_performed", False)),
        },
        "authority_boundary": {
            "authorization_created": bool(v.get("authorization_created", False)),
            "authority_activated": bool(v.get("authority_activated", False)),
            "execution_performed": bool(v.get("execution_performed", False)),
        },
        "epistemic_limits": {
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "indeterminate_is_not_verified": True,
            "upstream_unresolved_is_not_promoted": True,
            "local_verification_is_not_global_safety": True,
        },
        "downstream_state": {
            "occ1f_closed": False,
            "occ1g_opened": False,
            "p160_opened": False,
            "p159_final_lock": False,
        },
        "source_verifier_report_sha256": v.get("report_sha256"),
    }
    report["report_sha256"] = _canonical_hash(report)
    return report

def validate_report(report: Dict[str, Any]) -> bool:
    if report.get("schema") != SCHEMA or report.get("milestone") != MILESTONE:
        return False
    supplied = report.get("report_sha256")
    payload = deepcopy(report)
    payload.pop("report_sha256", None)
    if supplied != _canonical_hash(payload):
        return False
    counts = report.get("check_counts", {})
    registry = report.get("check_registry", [])
    actual = {k: 0 for k in ("PASS", "FAIL", "INCONCLUSIVE", "SKIPPED")}
    for item in registry:
        status = item.get("status")
        if status not in actual:
            return False
        actual[status] += 1
    if actual != counts:
        return False
    if report.get("verdict") == verifier.VERIFIED and actual["INCONCLUSIVE"]:
        return False
    ds = report.get("downstream_state", {})
    if any(ds.get(k) is not False for k in ("occ1f_closed", "occ1g_opened", "p160_opened", "p159_final_lock")):
        return False
    indep = report.get("independence", {})
    if indep.get("repair_performed") is not False:
        return False
    return True

def materialize(root: Path, filesystem_effect_context=None) -> Dict[str, Any]:
    root = Path(root)
    if filesystem_effect_context is None:
        raise RuntimeError("occ1f_report_filesystem_effect_context_required")
    inputs = verifier.paths(root)
    protected = [p for p in inputs.values() if p.exists()]
    before = _snapshot(protected)
    report = build_report(root)
    if not validate_report(report):
        raise RuntimeError("OCC1F_REPORT_SELF_VALIDATION_FAILED")

    target = root / REPORT_REL
    payload = (json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")
    filesystem_effect_context.begin()
    if not target.parent.exists():
        filesystem_effect_context.execute_path("occ1f_report_create_dirs", "FS_CREATE_DIRS", target.parent)
    filesystem_effect_context.execute_path("occ1f_report_write_replace", "FS_WRITE_REPLACE_BYTES", target, payload)

    after = _snapshot(protected)
    if before != after:
        raise RuntimeError("OCC1F_UPSTREAM_MUTATION_DETECTED")

    reread = json.loads(target.read_text(encoding="utf-8"))
    if reread != report or not validate_report(reread):
        raise RuntimeError("OCC1F_REPORT_PERSISTENCE_VALIDATION_FAILED")
    return report

def verify_materialized(root: Path) -> Dict[str, Any]:
    root = Path(root)
    target = root / REPORT_REL
    if not target.is_file():
        return {"status": "INDETERMINATE", "reason": "REPORT_MISSING"}
    try:
        persisted = json.loads(target.read_text(encoding="utf-8"))
    except Exception:
        return {"status": "REJECTED", "reason": "REPORT_UNREADABLE"}
    if not validate_report(persisted):
        return {"status": "REJECTED", "reason": "REPORT_INTEGRITY_INVALID"}
    expected = build_report(root)
    if persisted != expected:
        return {"status": "REJECTED", "reason": "REPORT_SOURCE_DRIFT_OR_TAMPER"}
    return {
        "status": "VERIFIED_REPORT_BINDING",
        "verdict": persisted["verdict"],
        "report_sha256": persisted["report_sha256"],
        "profile_file_sha256": persisted["verified_profile"]["file_sha256"],
        "occ1f_closed": False,
        "occ1g_opened": False,
        "p160_opened": False,
        "p159_final_lock": False,
    }


COMMON_TCB_REL = Path("validation_artifacts/p159/occ1f/common_tcb_manifest_v1.json")
CHECK_REGISTRY_REL = Path("validation_artifacts/p159/occ1f/verifier_check_registry_v1.json")
VERIFIER_IDENTITY_ANCHOR_REL = Path("validation_artifacts/p159/occ1f/verifier_identity_authorization_anchor_v1.json")
SOURCE_AUTHORITY_REL = Path("oif_review/campaigns/P159-OCC1A/occ1a_initial_development_authority_materialization.json")
VERIFIER_IDENTITY_ANCHOR_SCHEMA = "oce.p159.occ1f.verifier_identity_authorization_anchor.v1"
COMMON_TCB_SCHEMA = "oce.p159.occ1f.common_tcb_manifest.v1"
CHECK_REGISTRY_SCHEMA = "oce.p159.occ1f.verifier_check_registry.v1"

def _atomic_json_write(
    target: Path,
    value: Dict[str, Any],
    filesystem_effect_context=None,
) -> None:
    if filesystem_effect_context is None:
        raise RuntimeError("occ1f_preclose_filesystem_effect_context_required")
    payload = (
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    ).encode("utf-8")
    filesystem_effect_context.execute_path(
        "occ1f_preclose_write_replace",
        "FS_WRITE_REPLACE_BYTES",
        target,
        payload,
    )

def _module_identity(module) -> Dict[str, Any]:
    path = Path(module.__file__).resolve()
    return {"module": module.__name__, "path": str(path), "file_sha256": _file_sha(path)}

def build_common_tcb_manifest(root: Path) -> Dict[str, Any]:
    import hashlib as _hashlib
    import json as _json
    from ontology import occ_normative_ir as _nir
    from ontology import occ_normative_ir_real_builder as _builder
    root = Path(root)
    _expected_tcb_hashes = {
        "ontology/occ_normative_ir.py": "fda1e90e101ca5568a54a70b4f4dcac2b8833c8d8b38474387448eaa957ebde3",
        "ontology/occ_normative_ir_real_builder.py": "0ae2b0e5728f1db3b9a07cdef16fd553a5a9e45efaf68fe6dee82e797a1d35b4",
    }
    for _rel, _expected_hash in _expected_tcb_hashes.items():
        _p = root / _rel
        if not _p.is_file() or _file_sha(_p) != _expected_hash:
            raise RuntimeError("OCC1F_COMMON_TCB_ON_DISK_DRIFT:%s" % _rel)
    v = verifier.verify(root)
    report = build_report(root)
    verifier_path = root / "ontology" / "occ_independent_constitutional_verifier.py"
    if not verifier_path.is_file():
        raise RuntimeError("OCC1F_VERIFIER_SOURCE_MISSING")
    declared = list(v.get("common_tcb", []))
    expected = list(verifier.COMMON_TCB)
    if declared != expected:
        raise RuntimeError("OCC1F_COMMON_TCB_DECLARATION_DRIFT")
    components = [
        {"tcb_id": "python_json_parser", **_module_identity(_json)},
        {"tcb_id": "python_hashlib_sha256", **_module_identity(_hashlib)},
        {"tcb_id": "ontology.occ_normative_ir.canonical_sha256",
         "module": _nir.__name__, "path": str((root / "ontology/occ_normative_ir.py").resolve()),
         "file_sha256": _file_sha(root / "ontology/occ_normative_ir.py"), "symbol": "canonical_sha256"},
        {"tcb_id": "ontology.occ_normative_ir_real_builder",
         "module": _builder.__name__, "path": str((root / "ontology/occ_normative_ir_real_builder.py").resolve()),
         "file_sha256": _file_sha(root / "ontology/occ_normative_ir_real_builder.py")},
    ]
    if [x["tcb_id"] for x in components] != expected:
        raise RuntimeError("OCC1F_COMMON_TCB_COMPONENT_ORDER_DRIFT")
    artifact = {
        "schema": COMMON_TCB_SCHEMA,
        "milestone": MILESTONE,
        "artifact_role": "COMMON_TCB_MANIFEST",
        "verifier_identity": {
            "version": verifier.VERSION,
            "schema": verifier.SCHEMA,
            "file_sha256": _file_sha(verifier_path),
        },
        "verified_profile_file_sha256": v.get("profile_artifact_sha256"),
        "verification_report_sha256": report.get("report_sha256"),
        "components": components,
        "common_mode_risk_explicit": True,
        "compiler_in_tcb": False,
        "static_checker_in_tcb": False,
        "occ1e_builder_in_tcb": False,
        "authorization_created": False,
        "authority_activated": False,
        "execution_performed": False,
        "occ1f_closed": False,
        "occ1g_opened": False,
        "p160_opened": False,
        "p159_final_lock": False,
    }
    artifact["artifact_sha256"] = _canonical_hash(artifact)
    return artifact

def build_check_registry(root: Path) -> Dict[str, Any]:
    root = Path(root)
    v = verifier.verify(root)
    report = build_report(root)
    verifier_path = root / "ontology" / "occ_independent_constitutional_verifier.py"
    findings = v.get("findings", [])
    checks = []
    for item in findings:
        cid = item.get("check_id")
        if isinstance(cid, str) and cid.startswith("IVI-"):
            checks.append({
                "check_id": cid,
                "executed_status": item.get("status"),
                "reason": item.get("reason"),
            })
    expected = ["IVI-%d" % i for i in range(1, 13)]
    if [x["check_id"] for x in checks] != expected:
        raise RuntimeError("OCC1F_CANONICAL_CHECK_REGISTRY_DRIFT")
    artifact = {
        "schema": CHECK_REGISTRY_SCHEMA,
        "milestone": MILESTONE,
        "artifact_role": "VERIFIER_CHECK_REGISTRY",
        "verifier_identity": {
            "version": verifier.VERSION,
            "schema": verifier.SCHEMA,
            "file_sha256": _file_sha(verifier_path),
        },
        "verified_profile_file_sha256": v.get("profile_artifact_sha256"),
        "verification_report_sha256": report.get("report_sha256"),
        "canonical_ivi_ids": expected,
        "checks": checks,
        "checks_executed": len(checks),
        "checks_failed": v.get("checks_failed"),
        "checks_inconclusive": v.get("checks_inconclusive"),
        "verdict": v.get("verdict"),
        "registry_is_authority": False,
        "registry_can_activate": False,
        "occ1f_closed": False,
        "occ1g_opened": False,
        "p160_opened": False,
        "p159_final_lock": False,
    }
    artifact["artifact_sha256"] = _canonical_hash(artifact)
    return artifact

def _validate_self_hash(value: Dict[str, Any]) -> bool:
    supplied = value.get("artifact_sha256")
    payload = deepcopy(value)
    payload.pop("artifact_sha256", None)
    return isinstance(supplied, str) and supplied == _canonical_hash(payload)

def _verify_verifier_identity_anchor(root: Path) -> Dict[str, Any]:
    root=Path(root); ap=root/VERIFIER_IDENTITY_ANCHOR_REL; sp=root/SOURCE_AUTHORITY_REL; vp=root/"ontology/occ_independent_constitutional_verifier.py"
    if not ap.is_file(): return {"status":"REJECTED","reason":"VERIFIER_IDENTITY_ANCHOR_MISSING"}
    if not sp.is_file(): return {"status":"REJECTED","reason":"SOURCE_INSTITUTIONAL_AUTHORITY_MISSING"}
    try: a=json.loads(ap.read_text(encoding="utf-8")); s=json.loads(sp.read_text(encoding="utf-8"))
    except Exception: return {"status":"REJECTED","reason":"IDENTITY_ANCHOR_UNREADABLE"}
    if a.get("schema")!=VERIFIER_IDENTITY_ANCHOR_SCHEMA or not _validate_self_hash(a): return {"status":"REJECTED","reason":"VERIFIER_IDENTITY_ANCHOR_INTEGRITY_INVALID"}
    src=a.get("source_institutional_authority",{})
    if src.get("file_sha256")!=_file_sha(sp) or s.get("human_confirmed") is not True or s.get("authority_id")!=src.get("authority_id"): return {"status":"REJECTED","reason":"SOURCE_AUTHORITY_BINDING_INVALID"}
    c=a.get("constraints",{}); keys=("verifier_may_create_anchor","verifier_may_rewrite_anchor","preclose_materializer_may_create_anchor","preclose_materializer_may_rewrite_anchor","automatic_identity_rebinding","implicit_rotation","authority_expansion","root_override_all","execution_authority_created")
    if any(c.get(k) is not False for k in keys): return {"status":"REJECTED","reason":"IDENTITY_ANCHOR_BOUNDARY_INVALID"}
    cur=_file_sha(vp); authorized=a.get("authorized_verifier",{}).get("file_sha256")
    if authorized!=cur: return {"status":"REJECTED","reason":"VERIFIER_IDENTITY_NOT_INDEPENDENTLY_AUTHORIZED","authorized_verifier_sha256":authorized,"current_verifier_sha256":cur}
    return {"status":"VERIFIED_IDENTITY_ANCHOR","anchor_artifact_sha256":a.get("artifact_sha256"),"authorized_verifier_sha256":cur}

def materialize_preclose_evidence(root: Path, filesystem_effect_context=None) -> Dict[str, Any]:
    root = Path(root)
    anchor_status=_verify_verifier_identity_anchor(root)
    if anchor_status.get("status")!="VERIFIED_IDENTITY_ANCHOR": raise RuntimeError("OCC1F_VERIFIER_IDENTITY_NOT_AUTHORIZED:"+str(anchor_status.get("reason")))
    inputs = verifier.paths(root)
    protected = [p for p in inputs.values() if p.exists()]
    verifier_path = root / "ontology" / "occ_independent_constitutional_verifier.py"
    if verifier_path.exists():
        protected.append(verifier_path)
    protected.extend([root/VERIFIER_IDENTITY_ANCHOR_REL,root/SOURCE_AUTHORITY_REL])
    before = _snapshot(protected)
    tcb = build_common_tcb_manifest(root)
    registry = build_check_registry(root)
    if tcb["verification_report_sha256"] != registry["verification_report_sha256"]:
        raise RuntimeError("OCC1F_PRECLOSE_REPORT_BINDING_MISMATCH")
    if filesystem_effect_context is None:
        raise RuntimeError("occ1f_preclose_filesystem_effect_context_required")
    filesystem_effect_context.begin()
    preclose_parent = (root / COMMON_TCB_REL).parent
    if not preclose_parent.exists():
        filesystem_effect_context.execute_path(
            "occ1f_preclose_create_dirs",
            "FS_CREATE_DIRS",
            preclose_parent,
        )
    _atomic_json_write(root / COMMON_TCB_REL, tcb, filesystem_effect_context)
    _atomic_json_write(root / CHECK_REGISTRY_REL, registry, filesystem_effect_context)
    after = _snapshot(protected)
    if before != after:
        raise RuntimeError("OCC1F_PRECLOSE_UPSTREAM_MUTATION_DETECTED")
    status = verify_preclose_evidence(root)
    if status.get("status") != "VERIFIED_PRECLOSE_BINDING":
        raise RuntimeError("OCC1F_PRECLOSE_PERSISTENCE_VALIDATION_FAILED: %s" % status)
    return {"common_tcb_manifest": tcb, "verifier_check_registry": registry}

def diagnose_preclose_binding(root: Path) -> Dict[str, Any]:
    root = Path(root)
    anchor_status = _verify_verifier_identity_anchor(root)
    preclose_status = verify_preclose_evidence(root)
    detail = str(preclose_status.get("detail") or "")
    legacy = (
        anchor_status.get("status") == "VERIFIED_IDENTITY_ANCHOR"
        and preclose_status.get("status") == "REJECTED"
        and preclose_status.get("reason") == "PRECLOSE_SOURCE_RECALCULATION_FAILED"
        and "OCC1F_COMMON_TCB_ON_DISK_DRIFT:ontology/occ_normative_ir_real_builder.py" in detail
    )
    status = "INCONCLUSIVE"
    if legacy:
        status = "ANCHOR_VALID_LEGACY_PRECLOSE_DRIFT_SEPARATED"
    elif anchor_status.get("status") == "VERIFIED_IDENTITY_ANCHOR" and preclose_status.get("status") == "VERIFIED_PRECLOSE_BINDING":
        status = "ANCHOR_VALID_PRECLOSE_VERIFIED"
    return {"identity_anchor_status":anchor_status.get("status"),"identity_anchor_valid":anchor_status.get("status")=="VERIFIED_IDENTITY_ANCHOR","preclose_status":preclose_status.get("status"),"preclose_reason":preclose_status.get("reason"),"preclose_detail":preclose_status.get("detail"),"legacy_builder_epoch_drift":legacy,"correction_installation_status":status}

def verify_preclose_evidence(root: Path) -> Dict[str, Any]:
    root = Path(root)
    anchor_status=_verify_verifier_identity_anchor(root)
    if anchor_status.get("status")!="VERIFIED_IDENTITY_ANCHOR": return anchor_status
    tcb_path = root / COMMON_TCB_REL
    reg_path = root / CHECK_REGISTRY_REL
    if not tcb_path.is_file() or not reg_path.is_file():
        return {"status": "INDETERMINATE", "reason": "PRECLOSE_ARTIFACT_MISSING"}
    try:
        tcb = json.loads(tcb_path.read_text(encoding="utf-8"))
        reg = json.loads(reg_path.read_text(encoding="utf-8"))
    except Exception:
        return {"status": "REJECTED", "reason": "PRECLOSE_ARTIFACT_UNREADABLE"}
    if not _validate_self_hash(tcb) or not _validate_self_hash(reg):
        return {"status": "REJECTED", "reason": "PRECLOSE_ARTIFACT_INTEGRITY_INVALID"}
    try:
        expected_tcb = build_common_tcb_manifest(root)
        expected_reg = build_check_registry(root)
    except Exception as exc:
        return {"status": "REJECTED", "reason": "PRECLOSE_SOURCE_RECALCULATION_FAILED", "detail": str(exc)}
    if tcb != expected_tcb:
        return {"status": "REJECTED", "reason": "COMMON_TCB_SOURCE_DRIFT_OR_TAMPER"}
    if reg != expected_reg:
        return {"status": "REJECTED", "reason": "CHECK_REGISTRY_SOURCE_DRIFT_OR_TAMPER"}
    if reg.get("verdict") != verifier.VERIFIED or reg.get("checks_failed") != 0 or reg.get("checks_inconclusive") != 0:
        return {"status": "REJECTED", "reason": "PRECLOSE_VERIFIER_NOT_FULLY_VERIFIED"}
    return {
        "status": "VERIFIED_PRECLOSE_BINDING",
        "common_tcb_manifest_sha256": tcb["artifact_sha256"],
        "verifier_check_registry_sha256": reg["artifact_sha256"],
        "verification_report_sha256": reg["verification_report_sha256"],
        "occ1f_closed": False,
        "occ1g_opened": False,
        "p160_opened": False,
        "p159_final_lock": False,
    }


def main(root: Path | None = None, filesystem_effect_context=None) -> int:
    root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
    report = materialize(root, filesystem_effect_context)
    binding = verify_materialized(root)
    print("OCC1F_DIAGNOSTIC_REPORT_MATERIALIZED")
    print("verdict=%s" % report["verdict"])
    print("pass=%d" % report["check_counts"]["PASS"])
    print("fail=%d" % report["check_counts"]["FAIL"])
    print("inconclusive=%d" % report["check_counts"]["INCONCLUSIVE"])
    print("skipped=%d" % report["check_counts"]["SKIPPED"])
    print("inconclusive_ids=%s" % ",".join(report["inconclusive_check_ids"]))
    print("report_sha256=%s" % report["report_sha256"])
    print("binding_status=%s" % binding["status"])
    print("OCC1F_CLOSED_FALSE")
    print("OCC1G_NOT_OPENED")
    print("P160_NOT_OPENED")
    print("P159_FINAL_LOCK_FALSE")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
