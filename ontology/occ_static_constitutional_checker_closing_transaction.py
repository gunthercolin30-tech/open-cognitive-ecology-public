from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import hashlib, json
from ontology import occ_static_constitutional_checker as checker

PASS="PASS"
EXPECTED_CHECKER_SHA256="91ee871225a2ea747eb31a41c9cb7b117ba957aa870229afd3e7f58a00a42b86"
EXPECTED_CNP_SHA256="3d0e8768174fefc23787e2c8b79b991b07c218e417b2100c49ffa88a2fb7b972"
EXPECTED_OCC1C_POST_SHA256="7c01736c86520d8464676bac8789c973be69479ccb78420d6355ffa04fc32ee1"
EXPECTED_CROWN_SHA256="481066d9c1a7a1c6169454409f5472fb8ff65422e2d3c926d93a5f54425318b8"
EXPECTED_PROVENANCE_SHA256="c4ac79942ab8c79119c0fc46e9de3a38416f6eb9f14ce4c30617acd2835ea831"
EXPECTED_COVERAGE_SHA256="0387d95b8da541fea090939ed2f438f5ebb4be99974880836921f15928a25c06"

def raw_sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p): return json.loads(Path(p).read_text(encoding="utf-8"))
def canon(o): return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def canonical_hash(o): return hashlib.sha256(canon(o).encode("utf-8")).hexdigest()

def paths(root):
    root=Path(root); art=root/"validation_artifacts"/"p159"/"occ1d"
    return {
      "checker":root/"ontology"/"occ_static_constitutional_checker.py",
      "cnp":root/"validation_artifacts"/"p159"/"occ1c"/"compiled_normative_profile_v1.json",
      "occ1c_post":root/"validation_artifacts"/"p159"/"occ1c"/"occ1c_postclose_verification_v1.json",
      "crown":art/"independent_structural_adversarial_crown_v2_1_post_s6_v1_3.json",
      "provenance":art/"canonical_provenance_binding_v1_3.json",
      "coverage":art/"s7_s8_s10_executable_coverage_v1.json",
    }

def build(root):
    root=Path(root); ps=paths(root)
    if not all(p.is_file() for p in ps.values()):
        return {"status":"FAIL","reason":"REQUIRED_CLOSURE_EVIDENCE_MISSING"}
    observed={k:raw_sha(v) for k,v in ps.items()}
    expected={
      "checker":EXPECTED_CHECKER_SHA256,"cnp":EXPECTED_CNP_SHA256,
      "occ1c_post":EXPECTED_OCC1C_POST_SHA256,"crown":EXPECTED_CROWN_SHA256,
      "provenance":EXPECTED_PROVENANCE_SHA256,"coverage":EXPECTED_COVERAGE_SHA256}
    if observed!=expected:
        return {"status":"FAIL","reason":"BOUND_EVIDENCE_DRIFT","expected":expected,"observed":observed}

    occ1c=load(ps["occ1c_post"])
    op=occ1c.get("payload",{})
    if not (occ1c.get("status")=="PASS" and op.get("postclose_verified") is True
            and op.get("occ1c_closed") is True and op.get("occ1d_opened") is False
            and op.get("p160_opened") is False and op.get("p159_final_lock") is False):
        return {"status":"FAIL","reason":"OCC1C_UPSTREAM_NOT_POSTCLOSE_VERIFIED"}

    crown=load(ps["crown"])
    if not (crown.get("crown_status")=="PASSED"
            and crown.get("executed_case_count")==24
            and crown.get("detected_or_fail_closed_count")==24
            and crown.get("genuine_gaps")==[]
            and crown.get("checker_and_cnp_immutable") is True
            and crown.get("real_s7_s8_s10_unresolved_preserved") is True
            and crown.get("checker_sha256")==EXPECTED_CHECKER_SHA256
            and crown.get("candidate_cnp_sha256")==EXPECTED_CNP_SHA256):
        return {"status":"FAIL","reason":"INDEPENDENT_CROWN_NOT_READY"}

    prov=load(ps["provenance"])
    if not (prov.get("checker_sha256")==EXPECTED_CHECKER_SHA256
            and prov.get("occ1d_closed") is False and prov.get("occ1e_opened") is False
            and prov.get("p160_opened") is False and prov.get("p159_final_lock") is False
            and prov.get("authority_activated") is False
            and prov.get("authorization_created") is False
            and prov.get("execution_performed") is False):
        return {"status":"FAIL","reason":"CANONICAL_PROVENANCE_EVIDENCE_INVALID"}

    cov=load(ps["coverage"])
    real=cov.get("real_candidate",{})
    if not (cov.get("coverage")=={"S7":"EXECUTABLE","S8":"EXECUTABLE_BOUNDED_GRAPH","S10":"EXECUTABLE_MAP_VALIDATION"}
            and cov.get("unresolved_promoted_to_pass") is False
            and all((real.get(s) or {}).get("result")=="UNRESOLVED" for s in ("S7","S8","S10"))
            and real.get("decision")=="STATIC_UNRESOLVED"):
        return {"status":"FAIL","reason":"BOUNDED_UNRESOLVED_COVERAGE_INVALID"}

    profile=load(ps["cnp"])
    report=checker.check_profile(deepcopy(profile),root,EXPECTED_CNP_SHA256)
    findings={x.get("phase"):x for x in report.get("findings",[])}
    if set(findings)!=set(checker.PHASES):
        return {"status":"FAIL","reason":"S0_S11_NOT_COMPLETE"}
    if report.get("root_checks_disableable") is not False or report.get("unresolved_promoted_to_pass") is not False:
        return {"status":"FAIL","reason":"ROOT_OR_UNRESOLVED_SEMANTICS_INVALID"}
    if report.get("candidate_cnp_file_sha256")!=EXPECTED_CNP_SHA256:
        return {"status":"FAIL","reason":"REPORT_NOT_HASH_BOUND_TO_CNP"}
    if report.get("decision")!="STATIC_UNRESOLVED":
        return {"status":"FAIL","reason":"REAL_CNP_DECISION_DRIFT","observed":report.get("decision")}
    if any(findings[s].get("result")!="UNRESOLVED" for s in ("S7","S8","S10")):
        return {"status":"FAIL","reason":"REAL_BOUNDED_UNRESOLVED_NOT_PRESERVED"}
    if findings["S9"].get("result")!="NOT_APPLICABLE":
        return {"status":"FAIL","reason":"S9_EXPECTED_NOT_APPLICABLE_DRIFT"}
    if any(findings[s].get("result")!="PASS" for s in ("S0","S1","S2","S3","S4","S5","S6","S11")):
        return {"status":"FAIL","reason":"EXPECTED_PASS_PHASE_DRIFT"}

    phase_results={s:findings[s]["result"] for s in sorted(findings,key=lambda x:int(x[1:]))}
    payload={
      "schema":"oce.p159.occ1d.closure_transaction.v1",
      "milestone":"P159/OCC-1D",
      "transition":"OPEN_READY_TO_CLOSE->CLOSED",
      "decision":"OCC1D_CLOSING_TRANSACTION_COMMITTED_VALID",
      "readiness_decision":"OCC1D_READY_TO_CLOSE",
      "checker_sha256":EXPECTED_CHECKER_SHA256,
      "candidate_cnp_sha256":EXPECTED_CNP_SHA256,
      "static_report_sha256":report.get("report_sha256"),
      "static_decision_preserved":"STATIC_UNRESOLVED",
      "phase_results":phase_results,
      "bounded_unresolved_phases":["S7","S8","S10"],
      "missing_check_mechanisms":0,
      "genuine_adversarial_gaps":0,
      "adversarial_crown":{"executed":24,"detected_or_fail_closed":24,"status":"PASSED"},
      "evidence_file_sha256":observed,
      "root_checks_disableable":False,
      "unresolved_promoted_to_pass":False,
      "authorization_created":False,"authority_activated":False,"execution_performed":False,
      "occ1d_closed":True,"occ1e_opened":False,"p160_opened":False,"p159_final_lock":False,
      "functional_conclusion_only":True,"phenomenology_undetermined":True,
      "scope_note":"LOCAL_OCC1D_CLOSURE_ONLY_NOT_STATIC_PASS_NOT_GLOBAL_SAFETY_NOT_RUNTIME_LEGITIMACY_NOT_FINAL_LOCK"
    }
    payload["transaction_id"]=canonical_hash(payload)
    return {"status":PASS,"reason":"P159_OCC1D_CLOSING_TRANSACTION_READY","payload":payload}

def verify(obj,root):
    if obj.get("status")!=PASS: return False
    p=obj.get("payload",{})
    q=deepcopy(p); tid=q.pop("transaction_id",None)
    if not tid or tid!=canonical_hash(q): return False
    if p.get("decision")!="OCC1D_CLOSING_TRANSACTION_COMMITTED_VALID": return False
    if p.get("static_decision_preserved")!="STATIC_UNRESOLVED": return False
    if p.get("bounded_unresolved_phases")!=["S7","S8","S10"]: return False
    if p.get("missing_check_mechanisms")!=0 or p.get("genuine_adversarial_gaps")!=0: return False
    if p.get("occ1d_closed") is not True or p.get("occ1e_opened") is not False: return False
    if p.get("p160_opened") is not False or p.get("p159_final_lock") is not False: return False
    if p.get("authorization_created") is not False or p.get("authority_activated") is not False or p.get("execution_performed") is not False: return False
    expected=build(Path(root))
    return expected.get("status")==PASS and expected.get("payload")==p
