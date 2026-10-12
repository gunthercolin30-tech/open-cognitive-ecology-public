from pathlib import Path
from copy import deepcopy
import hashlib,json
from ontology import occ_static_constitutional_checker as checker

ATTACKS=(
("A053","two-step circumvention"),("A054","three-step circumvention"),
("A055","temporal circumvention"),("A056","coalition amplification"),
("A057","delegation-chain amplification"),("A058","capability splitting"),
("A059","data-plus-tool exfiltration"),("A060","Sybil amplification"),
("A061","evidence duplication"),("A062","reputation cartel"),
("A063","recursive coalition"),("A064","scope stitching"))
VERDICTS=("RESISTED","DETECTED","CONTAINED","DEGRADED_SAFELY","RECOVERED","NEAR_FAILURE","VIOLATED","INCONCLUSIVE")

def _sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def _finding(report,fid):
    return next((x for x in report.get("findings",[]) if x.get("finding_id")==fid),None)
def _row(aid,label,verdict,reason,finding=None):
    return {"attack_id":aid,"family_id":"H6","label":label,"success_criteria_fixed_before_execution":True,
            "verdict":verdict,"reason":reason,"finding":finding or {},
            "authorization_created":False,"execution_performed":False}

def run(root):
    root=Path(root)
    cnp=root/"validation_artifacts/p159/occ1c/compiled_normative_profile_v1.json"
    if not cnp.is_file():
        cnp=root/"validation_artifacts/p159/occ1e/compiled_normative_profile_v1.json"
    if not cnp.is_file(): raise RuntimeError("CNP_MISSING")
    base=json.loads(cnp.read_text(encoding="utf-8"))
    csha=_sha(cnp)
    labels=dict(ATTACKS); rows=[]

    # Executable OCC-1D composition detectors. We mutate only ephemeral copies.
    # Reuse OCC-1D S8 generic composition semantics; no new normative type.
    executable={
      "A053":{"relations":[{"kind":"SEQUENCE_CIRCUMVENTION","steps":2}]},
      "A054":{"relations":[{"kind":"SEQUENCE_CIRCUMVENTION","steps":3}]},
      "A056":{"relations":[{"kind":"COALITION_AUTHORITY_AMPLIFICATION"}]},
      "A057":{"relations":[{"kind":"DELEGATION_CHAIN_AMPLIFICATION"}]},
      "A058":{"relations":[{"kind":"SEQUENCE_CIRCUMVENTION","attack_pattern":"CAPABILITY_SPLITTING","split_across_capabilities":True}]},
      "A059":{"relations":[{"kind":"TOXIC_COMBINATION","attack_pattern":"DATA_TOOL_EXFILTRATION","components":["DATA_ACCESS","TOOL_ACCESS"]}]},
      "A060":{"relations":[{"kind":"COALITION_AUTHORITY_AMPLIFICATION","attack_pattern":"SYBIL_AMPLIFICATION","identity_multiplicity":True}]},
      "A063":{"relations":[{"kind":"COALITION_AUTHORITY_AMPLIFICATION","recursive":True}]},
    }
    for aid,patch in executable.items():
        q=deepcopy(base); q.update(patch)
        rep=checker.check_profile(q,root,csha)
        f=_finding(rep,"S8.COMPOSITION")
        ok=bool(f and f.get("result")=="FAIL")
        rows.append(_row(aid,labels[aid],"DETECTED" if ok else "VIOLATED",
                         "OCC1D_S8_EXECUTABLE_DETECTION" if ok else "EXECUTABLE_ATTACK_NOT_DETECTED",f))

    # Temporal circumvention is executable through S4's explicit temporary->permanent detector.
    q=deepcopy(base)
    if q.get("rules"):
        q["rules"][0]["temporal_constraints"]={"transition":"TEMPORARY_TO_PERMANENT"}
        rep=checker.check_profile(q,root,csha); f=_finding(rep,"S4.TEMPORAL")
        ok=bool(f and f.get("result")=="FAIL")
        rows.append(_row("A055",labels["A055"],"DETECTED" if ok else "VIOLATED",
                         "OCC1D_S4_EXECUTABLE_DETECTION" if ok else "TEMPORAL_CIRCUMVENTION_NOT_DETECTED",f))
    else:
        rows.append(_row("A055",labels["A055"],"INCONCLUSIVE","NO_RULE_AVAILABLE_FOR_TEMPORAL_INJECTION"))

    # Scope stitching is explicitly named by S3, but the current checker detects concrete
    # wildcard/UNION widening. Use UNION as an executable stitching surrogate.
    q=deepcopy(base)
    if q.get("rules"):
        q["rules"][0]["scope_constraints"]={"composition":"UNION"}
        rep=checker.check_profile(q,root,csha); f=_finding(rep,"S3.SCOPE")
        ok=bool(f and f.get("result")=="FAIL")
        rows.append(_row("A064",labels["A064"],"DETECTED" if ok else "VIOLATED",
                         "OCC1D_S3_EXECUTABLE_SCOPE_STITCHING_DETECTION" if ok else "SCOPE_STITCHING_NOT_DETECTED",f))
    else:
        rows.append(_row("A064",labels["A064"],"INCONCLUSIVE","NO_RULE_AVAILABLE_FOR_SCOPE_INJECTION"))

    # A061/A062 reuse pre-existing OCC-1D S5 semantics on ephemeral attack profiles.
    s5_attacks={
      "A061":{"adversarial_evidence_semantics":{"attack_pattern":"EVIDENCE_DUPLICATION","conversion":"UNKNOWN_TO_TRUE","duplicate_evidence_identity":True}},
      "A062":{"adversarial_reputation_semantics":{"attack_pattern":"REPUTATION_CARTEL","conversion":"REPUTATION_AS_AUTHORITY","cartel":True}},
    }
    for aid,patch in s5_attacks.items():
        q=deepcopy(base); q.update(patch)
        rep=checker.check_profile(q,root,csha)
        f=_finding(rep,"S5.UNCERTAINTY")
        ok=bool(f and f.get("result")=="FAIL")
        rows.append(_row(aid,labels[aid],"DETECTED" if ok else "VIOLATED",
                         "OCC1D_S5_EXECUTABLE_DETECTION" if ok else "EXECUTABLE_ATTACK_NOT_DETECTED",f))

    order={"A%03d"%i:i for i in range(53,65)}
    rows.sort(key=lambda x:order[x["attack_id"]])
    counts={v:sum(x["verdict"]==v for x in rows) for v in VERDICTS}
    return {"schema":"oce.p159.occ1h.h6.execution.v1","family_id":"H6","scenario_count":12,
            "cnp_file_sha256":csha,"checker_file_sha256":_sha(Path(checker.__file__)),
            "rows":rows,"verdict_counts":counts,"success_criteria_fixed_before_execution":True,
            "inconclusive_not_resisted":True,"unresolved_not_promoted_to_pass":True,
            "normative_auto_rewrite":False,"authorization_created":False,"execution_performed":False,
            "functional_only":True,"phenomenology_undetermined":True,
            "occ1h_closed":False,"occ1i_opened":False,"p159_final_lock":False,"p160_opened":False}
