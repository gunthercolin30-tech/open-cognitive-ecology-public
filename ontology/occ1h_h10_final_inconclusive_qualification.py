from pathlib import Path
import hashlib,json
DECISION="CURRENT_P159_H10_COMPOUND_PATHS_NOT_MATERIALIZED"
EXPECTED={
"A095":"END_TO_END_PROVIDER_THEORY_POLICY_PROVENANCE_PATH_NOT_MATERIALIZED_AT_P159",
"A097":"SYBIL_AND_REPUTATION_COMPOUND_RELATION_NOT_EXECUTABLY_PROVEN",
"A100":"CIS_TO_PERMANENT_SOVEREIGNTY_TRANSITION_NOT_EXECUTABLY_MATERIALIZED",
"A101":"ACEE_TO_VERIFIER_WEAKENING_PATH_NOT_EMPIRICALLY_PROVEN",
"A105":"GRAND_CHAIN_NOT_END_TO_END_EXECUTABLE_WITH_CURRENT_P159_BINDINGS"}
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def build(root):
    root=Path(root)
    paths={
      "inventory":root/"ontology_inventory.txt",
      "h10_runner":root/"ontology/occ_constitutional_adversarial_crown_h10.py",
      "h10_bundle":root/"validation_artifacts/p159/occ1h/h10_execution_bundle_v1.json"}
    missing=[k for k,p in paths.items() if not p.exists()]
    if missing: raise RuntimeError("H10_QUALIFICATION_INPUT_MISSING:"+",".join(missing))
    b=json.loads(paths["h10_bundle"].read_text(encoding="utf-8"))
    rows={r["attack_id"]:r for r in b["rows"]}
    for aid,reason in EXPECTED.items():
        r=rows.get(aid)
        if not r or r.get("verdict")!="INCONCLUSIVE" or r.get("reason")!=reason:
            raise RuntimeError("H10_CURRENT_EVIDENCE_DRIFT:"+aid)
    if rows["A097"].get("evidence")!={"h6_A060":"INCONCLUSIVE","h6_A062":"INCONCLUSIVE"}:
        raise RuntimeError("H10_A097_DEPENDENCY_DRIFT")
    a101=rows["A101"].get("evidence",{})
    if a101.get("h7_A075_verdict")!="INCONCLUSIVE" or a101.get("h7_A075_reason")!="NO_EXECUTABLE_VERIFIER_SELF_UPGRADE_PATH_IN_OCC1F_EVIDENCE":
        raise RuntimeError("H10_A101_DEPENDENCY_DRIFT")
    if rows["A105"].get("evidence",{}).get("unresolved_prerequisite_attacks")!=["A095","A097","A100","A101"]:
        raise RuntimeError("H10_A105_DEPENDENCY_DRIFT")
    e={"schema":"oce.p159.occ1h.h10.final_inconclusive_qualification.v1",
       "milestone":"P159/OCC-1H/H10","decision":DECISION,
       "qualified_attack_ids":["A095","A097","A100","A101","A105"],"qualified_count":5,
       "causal_qualifications":{
        "A095":"END_TO_END_PROVENANCE_PATH_NOT_MATERIALIZED",
        "A097":"DEPENDS_ON_UNRESOLVED_A060_A062",
        "A100":"CIS_SOVEREIGNTY_TRANSITION_NOT_MATERIALIZED",
        "A101":"DEPENDS_ON_UNRESOLVED_A075",
        "A105":"DEPENDS_ON_UNRESOLVED_A095_A097_A100_A101_AND_NO_END_TO_END_BINDING"},
       "source_hashes":{k:sha(p) for k,p in paths.items()},
       "verdicts_modified":False,"mechanisms_created":False,"authorization_created":False,
       "execution_performed":False,"normative_auto_rewrite":False,
       "functional_only":True,"phenomenology_undetermined":True,
       "occ1h_closed":False,"occ1i_opened":False,"p159_final_lock":False,"p160_opened":False,
       "limitations":["Causal qualification does not convert INCONCLUSIVE to a resistant verdict.",
       "Dependency evidence is preserved rather than compensated by unrelated defenses.",
       "No P160 runtime, sovereignty transition, verifier upgrade, or authorization path is created."]}
    e["evidence_sha256"]=hashlib.sha256(json.dumps(e,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return e
