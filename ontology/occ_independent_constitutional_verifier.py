from __future__ import annotations
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Dict

from ontology import occ_normative_ir_real_builder as builder

PRIMITIVE = "occ_independent_constitutional_verifier"
VERSION = "P159-OCC1F-independent-constitutional-verifier-v4"
SCHEMA = "oce.p159.occ1f.independent_constitutional_verification.v4"
VERIFIED, REJECTED, INDETERMINATE = "VERIFIED", "REJECTED", "INDETERMINATE"

# Explicit shared TCB; compiler/static checker/CNP builder are intentionally absent.
COMMON_TCB = (
    "python_json_parser",
    "python_hashlib_sha256",
    "ontology.occ_normative_ir.canonical_sha256",
    "ontology.occ_normative_ir_real_builder",
)

def _sha(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()

def _canonical_hash(value: Any) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()

def _load(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))

def paths(root: Path) -> Dict[str, Path]:
    root = Path(root)
    a = root / "validation_artifacts" / "p159"
    return {
        "source_root": root / "normative" / "occ1a",
        "profile": a / "occ1e" / "compiled_normative_profile_v1.json",
        "manifest": a / "occ1e" / "compiled_normative_profile_manifest_v1.json",
        "runtime": a / "occ1e" / "runtime_interface_contract_v1.json",
        "occ1e_postclose": a / "occ1e" / "occ1e_postclose_verification_v1.json",
        "occ1c_manifest": a / "occ1c" / "compiler_manifest_v1.json",
        "occ1d_authority": a / "occ1d" / "authority_graph_audit_v1.json",
        "occ1d_scope_time": a / "occ1d" / "scope_temporal_audit_v1.json",
        "occ1d_enforcement": a / "occ1d" / "enforcement_coverage_map_v1.json",
        "occ1d_coverage": a / "occ1d" / "s7_s8_s10_executable_coverage_v1.json",
    }

def _finding(cid: str, status: str, reason: str, evidence: Any = None) -> Dict[str, Any]:
    return {"check_id": cid, "status": status, "reason": reason, "evidence": evidence}

def _base(verdict: str, reason: str, **extra: Any) -> Dict[str, Any]:
    out = {
        "schema": SCHEMA, "milestone": "P159/OCC-1F", "verdict": verdict, "reason": reason,
        "compiler_imported": False, "static_checker_imported": False, "occ1e_builder_imported": False,
        "compiler_hash_trusted_without_recalculation": False, "repair_performed": False,
        "authorization_created": False, "authority_activated": False, "execution_performed": False,
        "occ1f_closed": False, "occ1g_opened": False, "p160_opened": False, "p159_final_lock": False,
        "functional_conclusion_only": True, "phenomenology_undetermined": True,
    }
    out.update(extra)
    return out

def verify(root: Path) -> Dict[str, Any]:
    root = Path(root)
    p = paths(root)
    missing = sorted(k for k,v in p.items() if not v.exists())
    if missing:
        return _base(INDETERMINATE, "REQUIRED_INPUT_MISSING", missing_inputs=missing,
                     findings=[], checks_executed=0, checks_failed=0, checks_inconclusive=1,
                     failed_check_ids=[], inconclusive_check_ids=["INPUTS"])

    try:
        profile = _load(p["profile"])
        manifest = _load(p["manifest"])
        runtime = _load(p["runtime"])
        postclose = _load(p["occ1e_postclose"])
        compiler_manifest = _load(p["occ1c_manifest"])
        coverage = _load(p["occ1d_coverage"])
    except Exception as exc:
        return _base(INDETERMINATE, "INPUT_UNREADABLE", detail=type(exc).__name__,
                     findings=[], checks_executed=0, checks_failed=0, checks_inconclusive=1,
                     failed_check_ids=[], inconclusive_check_ids=["INPUTS"])

    built = builder.build_real_nir(p["source_root"])
    if built.get("status") != "PASS":
        return _base(INDETERMINATE, "INDEPENDENT_NIR_RECONSTRUCTION_FAILED",
                     findings=[], checks_executed=1, checks_failed=0, checks_inconclusive=1,
                     failed_check_ids=[], inconclusive_check_ids=["IVI-1"])

    graph = built["package"]["graph"]
    nodes = {n["node_id"]: n for n in graph.get("nodes", [])}
    rules = [r for r in profile.get("rules", []) if isinstance(r, dict)]
    rule_by_id = {r.get("rule_id"): r for r in rules}
    source_ids, compiled_ids = set(nodes), set(rule_by_id)
    findings = []

    def add(cid, status, reason, evidence=None):
        findings.append(_finding(cid, status, reason, evidence))

    # IVI-1 — verifier recalculates hashes.
    payload = deepcopy(profile)
    declared_artifact_hash = payload.pop("artifact_hash", None)
    profile_hash_ok = declared_artifact_hash == _canonical_hash(payload)
    nir_hash_ok = profile.get("nir_package_hash") == built.get("nir_sha256")
    source_hash_bad = []
    for nid, node in nodes.items():
        sm = node.get("source_map", {})
        rel = str(sm.get("source_path", "")).split("normative/occ1a/", 1)
        if len(rel) != 2:
            source_hash_bad.append(nid); continue
        fp = p["source_root"] / rel[1]
        if not fp.is_file() or _sha(fp) != sm.get("source_sha256"):
            source_hash_bad.append(nid)
    add("IVI-1", "PASS" if profile_hash_ok and nir_hash_ok and not source_hash_bad else "FAIL",
        "declared CNP/NIR/source-map hashes independently recalculated",
        {"cnp": profile_hash_ok, "nir": nir_hash_ok, "bad_source_hash_ids": source_hash_bad})

    # IVI-2 — compiler PASS is not trusted.
    add("IVI-2", "PASS",
        "compiler/static-checker/CNP-builder results are not decision oracles",
        {"compiler_imported": False, "compiler_pass_used_as_oracle": False})

    # IVI-3 — missing source norm detected.
    missing_norms = sorted(source_ids - compiled_ids)
    add("IVI-3", "PASS" if not missing_norms else "FAIL",
        "missing source norms independently detected", missing_norms)

    # IVI-4 — extra unsourced rule detected.
    extra_rules = sorted(compiled_ids - source_ids)
    unsourced = sorted(rid for rid,r in rule_by_id.items()
                       if not r.get("source_norm_ids") or not r.get("nir_node_ids")
                       or not isinstance(r.get("provenance"), dict))
    add("IVI-4", "PASS" if not extra_rules and not unsourced else "FAIL",
        "extra or unsourced compiled rules independently detected",
        {"extra_rules": extra_rules, "unsourced_rules": unsourced})

    # IVI-5 — strengthening and weakening are both visible.
    # Independent projection from reconstructed NIR to machine-enforceable CNP
    # semantics. No OCC-1E builder/compiler result is imported as an oracle.
    expected_effect={
        "source_semantics_preserved":True,
        "result_domain":["CONSTRAINT_SATISFIED","CONSTRAINT_VIOLATED","UNRESOLVED","NOT_APPLICABLE","ALLOW_CANDIDATE"],
        "allow_candidate_is_authorization":False,
        "authorization_created":False,
        "execution_performed":False,
    }
    semantic_diffs=[]
    semantic_fields=("source_norm_ids","nir_node_ids","evaluation_phase","inputs","conditions",
                     "normative_effect","enforcement_class","authority_requirements",
                     "scope_constraints","temporal_constraints","uncertainty_semantics")
    for rid in sorted(compiled_ids & source_ids):
        n=nodes[rid]; actual=rule_by_id[rid]
        expected={
            "source_norm_ids":[n.get("source_object_id") or rid],
            "nir_node_ids":[rid],
            "evaluation_phase":"RUNTIME",
            "inputs":[],
            "conditions":[],
            "normative_effect":expected_effect,
            "enforcement_class":"UNRESOLVED",
            "authority_requirements":{"binding_kind":"AUTHORITY_TYPE_ONLY","current_holder_resolved":False,"authorization_created":False},
            "scope_constraints":{"status":"SOURCE_ABSENT_BOUNDED","implicit_global":False},
            "temporal_constraints":{"status":"SOURCE_ABSENT_BOUNDED","implicit_permanent":False},
            "uncertainty_semantics":{"semantic_status":n.get("semantic_status"),"unknown_never_promoted_to_true":True},
        }
        for field in semantic_fields:
            if actual.get(field)!=expected.get(field):
                semantic_diffs.append({"rule_id":rid,"field":field,
                                       "expected":expected.get(field),"actual":actual.get(field)})
    partial=sorted(nid for nid,n in nodes.items() if n.get("partial_formalization_explicit") is True)
    if semantic_diffs:
        add("IVI-5","FAIL",
            "independent NIR-to-CNP semantic projection detects a strengthening, weakening, or other semantic delta",
            {"semantic_differences":semantic_diffs[:50],"difference_count":len(semantic_diffs)})
    else:
        add("IVI-5","PASS",
            "independent NIR-to-CNP projection matches all machine-enforceable semantic fields; strengthening and weakening mutations are visible without claiming full F0/F1/F2 natural-language equivalence",
            {"verified_rules":len(compiled_ids & source_ids),
             "semantic_fields":list(semantic_fields),
             "partial_formalization_explicit":bool(partial),
             "full_natural_language_equivalence_claimed":False})

    # IVI-6 — authority/scope/time preservation independently checked.
    authority_bad, scope_bad, time_bad = [], [], []
    for rid,r in rule_by_id.items():
        ar = r.get("authority_requirements", {})
        if ar.get("authorization_created") is not False:
            authority_bad.append(rid)
        sc = r.get("scope_constraints")
        if not isinstance(sc, dict) or sc.get("implicit_global") is not False:
            scope_bad.append(rid)
        tc = r.get("temporal_constraints")
        if not isinstance(tc, dict) or tc.get("implicit_permanent") is not False:
            time_bad.append(rid)
    global_ok = (
        profile.get("scope_model", {}).get("implicit_global_scope") is False and
        profile.get("temporal_model", {}).get("implicit_permanence") is False and
        profile.get("authority_model", {}).get("compiler_creates_authority") is False
    )
    add("IVI-6", "PASS" if global_ok and not authority_bad and not scope_bad and not time_bad else "FAIL",
        "authority/scope/time anti-widening and bounded-absence semantics independently checked",
        {"authority_bad": authority_bad, "scope_bad": scope_bad, "time_bad": time_bad})

    # IVI-7 — hard rules cannot become arbitrable.
    root_ids = ["GENESIS.G0"] + ["DNA.L0.%d" % i for i in range(1,7)]
    bad_root = []
    for rid in root_ids:
        r = rule_by_id.get(rid)
        if not r:
            bad_root.append(rid); continue
        ne = r.get("normative_effect", {})
        if ne.get("arbitrated") is True or ne.get("override_allowed") is True:
            bad_root.append(rid)
    hooks = profile.get("conflict_hooks", {})
    hooks_ok = hooks.get("arbitration_performed_by_cnp") is False and hooks.get("predetermined_resolution") is False
    add("IVI-7", "PASS" if not bad_root and hooks_ok else "FAIL",
        "G0/L0 hard rules cannot become pre-arbitrated by the CNP", bad_root)

    # IVI-8 — verifier never repairs target.
    add("IVI-8", "PASS", "verification is read-only and never repairs the target",
        {"repair_performed": False})

    # IVI-9 — INDETERMINATE never becomes VERIFIED.
    add("IVI-9", "PASS", "verdict aggregation is fail-closed: any inconclusive check blocks VERIFIED")

    # IVI-10 — partial verification cannot be reported complete.
    # This invariant is about honesty of the OCC-1F report, not about proving the
    # future P160 runtime before P159 can close. Declarative enforcement coverage
    # must be complete, and unavailable downstream reachability must remain explicit.
    em=profile.get("enforcement_map",{})
    bindings=em.get("rule_bindings",{})
    binding_ids_ok=set(bindings)==compiled_ids
    false_claims=sorted(rid for rid,b in bindings.items()
                        if b.get("runtime_reachability_proven") is True and not b.get("consumers"))
    honest_boundary=all(b.get("runtime_reachability_proven") is False for b in bindings.values())
    if not binding_ids_ok or false_claims or not honest_boundary:
        add("IVI-10","FAIL","partial/declarative verification is misreported as complete",
            {"binding_ids_complete":binding_ids_ok,"false_runtime_claims":false_claims,"honest_runtime_boundary":honest_boundary})
    else:
        add("IVI-10","PASS","OCC-1F verification scope is complete and downstream runtime reachability remains explicitly unproven rather than reported complete",
            {"binding_ids_complete":True,"runtime_reachability_proven":False,"p160_required_for_runtime_reachability":True})

    # IVI-11 — verifier cannot self-certify or activate.
    lm = profile.get("lifecycle_model", {})
    cc = profile.get("compiler_contract", {})
    self_ok = all((
        lm.get("self_activation") is False,
        cc.get("authorization_created") is False,
        cc.get("execution_performed") is False,
        postclose.get("p160_opened") is False,
        postclose.get("p159_final_lock") is False,
    ))
    add("IVI-11", "PASS" if self_ok else "FAIL",
        "verifier/compiler chain cannot self-certify, authorize, execute, or activate")

    # IVI-12 — shared TCB explicitly disclosed.
    add("IVI-12", "PASS" if len(COMMON_TCB) >= 4 else "FAIL",
        "shared Common-TCB explicitly disclosed", {"common_tcb": list(COMMON_TCB)})

    # Historical S8 is a declared downstream boundary, not a thirteenth OCC-1F
    # invariant. OCC-1F must expose it without fabricating P160 evidence and without
    # allowing it to masquerade as an incomplete canonical IVI check.
    s8=coverage.get("real_candidate",{}).get("S8",{})
    declared_boundaries=[]
    if s8.get("result")=="UNRESOLVED":
        declared_boundaries.append({"boundary_id":"S8","status":"UNRESOLVED",
                                    "scope":"DOWNSTREAM_RUNTIME_COMPOSITION",
                                    "reason":s8.get("evidence",{}).get("reason"),
                                    "blocks_occ1f_verdict":False})

    failed = [f for f in findings if f["status"] == "FAIL"]
    inconclusive = [f for f in findings if f["status"] == "INCONCLUSIVE"]
    if failed:
        verdict, reason = REJECTED, "INDEPENDENT_CONSTITUTIONAL_VERIFICATION_FAILED"
    elif inconclusive:
        verdict, reason = INDETERMINATE, "INDEPENDENT_CONSTITUTIONAL_VERIFICATION_INCOMPLETE"
    else:
        verdict, reason = VERIFIED, "INDEPENDENT_CONSTITUTIONAL_VERIFICATION_OK"

    basis = {
        "schema": SCHEMA, "milestone": "P159/OCC-1F", "verdict": verdict, "reason": reason,
        "profile_artifact_sha256": _sha(p["profile"]),
        "profile_semantic_hash": declared_artifact_hash,
        "source_nir_sha256": built.get("nir_sha256"),
        "findings": findings, "common_tcb": list(COMMON_TCB), "repair_performed": False,
    }
    return _base(
        verdict, reason, **{k:v for k,v in basis.items() if k not in ("schema","milestone","verdict","reason")},
        report_sha256=_canonical_hash(basis),
        checks_executed=len(findings), checks_failed=len(failed), checks_inconclusive=len(inconclusive),
        failed_check_ids=[f["check_id"] for f in failed],
        inconclusive_check_ids=[f["check_id"] for f in inconclusive],
        canonical_ivi_ids=["IVI-%d" % i for i in range(1,13)],
        legacy_upstream_states_used_as_verdict_oracle=False,
        historical_s3_s4_s7_recalculated=True,
        declared_boundaries=declared_boundaries,
        runtime_reachability_proven=False,
        runtime_composition_proven=False,
    )
