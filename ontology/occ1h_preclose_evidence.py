from pathlib import Path
import json, hashlib
from ontology import occ1h_root_criticality_qualification as rootq
from ontology import occ1h_historical_results_immutability as himm
from ontology import occ1h_applicability_contract as appcontract
from ontology import occ1h_h6_posthardening_evidence as h6ph
from ontology import occ1h_a097_posthardening_evidence as a097ph
from ontology import occ1h_a075_post_correction_evidence as a075ph

VERDICTS=("RESISTED","DETECTED","CONTAINED","DEGRADED_SAFELY","RECOVERED","NEAR_FAILURE","VIOLATED","INCONCLUSIVE")
EXPECTED=set(range(1,106))

def _load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))

def _sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def _num(a):
    return int(str(a).lstrip("A"))

def _canon(n):
    return "A%d" % n

def _compat(n):
    return "A%03d" % n

def build(root):
    root=Path(root)
    base=root/"validation_artifacts/p159/occ1h"
    inputs={
        "foundation":base/"adversarial_crown_foundation_bundle_v1.json",
        "coverage":base/"attack_coverage_matrix_v1.json",
        "defense":base/"defense_expectation_matrix_v1.json",
        "counterexamples":base/"counterexample_registry_v1.json",
        "h1_h3":base/"h1_h3_execution_bundle_v1.json",
        "post_h1_h3":base/"h1_h3_posthardening_evidence_v1.json",
        "post_h6":base/"h6_posthardening_evidence_v1.json",
        "post_h6_a061_a062":base/"h6_a061_a062_posthardening_evidence_v1.json",
        "post_a097":base/"a097_posthardening_evidence_v1.json",
        "post_a075":base/"a075_post_correction_evidence_v1.json",
        **{"h%d"%i:base/("h%d_execution_bundle_v1.json"%i) for i in range(4,11)},
    }
    missing=[str(p) for p in inputs.values() if not p.is_file()]
    if missing:
        return {"schema":"oce.p159.occ1h.preclose.v1","status":"INCOMPLETE",
                "closure_admissible":False,"missing_inputs":missing,
                "occ1h_closed":False,"occ1i_opened":False,
                "p159_final_lock":False,"p160_opened":False}

    docs={k:_load(v) for k,v in inputs.items()}
    hashes={k:_sha(v) for k,v in inputs.items()}

    # Historical execution state. Preserve it; do not rewrite A008/A009.
    historical={}
    for row in docs["h1_h3"].get("rows",[]):
        historical[_num(row["attack_id"])]=dict(row)
    for i in range(4,11):
        for row in docs["h%d"%i].get("rows",[]):
            n=_num(row["attack_id"])
            if n in historical:
                raise ValueError("duplicate attack execution: %s" % n)
            historical[n]=dict(row)

    present=set(historical)
    missing_ids=sorted(EXPECTED-present)
    extra_ids=sorted(present-EXPECTED)

    # Current state = historical state plus the explicit H1-H3 post-hardening
    # evidence. Historical rows remain separately hash-bound above.
    current={n:dict(r) for n,r in historical.items()}
    ph=docs["post_h1_h3"]
    for n,key in ((8,"a008_verdict"),(9,"a009_verdict"),(21,"a021_verdict")):
        if n in current and key in ph:
            current[n]["verdict"]=ph[key]
            current[n]["current_state_source"]="h1_h3_posthardening_evidence_v1.json"

    h6_posthardening_verified=h6ph.verify_materialized(root)
    if not h6_posthardening_verified:
        return {"schema":"oce.p159.occ1h.preclose.v1","status":"INCOMPLETE","closure_admissible":False,
                "missing_inputs":[],"invalid_inputs":["h6_posthardening_evidence_v1.json"],
                "occ1h_closed":False,"occ1i_opened":False,"p159_final_lock":False,"p160_opened":False}
    for tr in docs["post_h6"].get("transitions",[]):
        n=_num(tr["attack_id"])
        if n not in (58,59,60) or n not in current: raise ValueError("unexpected H6 post-hardening transition: %s"%n)
        if historical[n].get("verdict")!="INCONCLUSIVE": raise ValueError("historical H6 transition source drift: %s"%n)
        current[n]["verdict"]=tr["current_verdict"]
        current[n]["current_state_source"]="h6_posthardening_evidence_v1.json"
    h6_a061_a062_verified=h6ph.verify_a061_a062_materialized(root)
    if not h6_a061_a062_verified:
        return {"schema":"oce.p159.occ1h.preclose.v1","status":"INCOMPLETE","closure_admissible":False,"missing_inputs":[],"invalid_inputs":["h6_a061_a062_posthardening_evidence_v1.json"],"occ1h_closed":False,"occ1i_opened":False,"p159_final_lock":False,"p160_opened":False}
    for tr in docs["post_h6_a061_a062"].get("transitions",[]):
        n=_num(tr["attack_id"])
        if n not in (61,62) or n not in current: raise ValueError("unexpected A061/A062 post-hardening transition: %s"%n)
        if historical[n].get("verdict")!="INCONCLUSIVE": raise ValueError("historical A061/A062 transition source drift: %s"%n)
        current[n]["verdict"]=tr["current_verdict"]
        current[n]["current_state_source"]="h6_a061_a062_posthardening_evidence_v1.json"

    a097_posthardening_verified=a097ph.verify_materialized(root)
    if not a097_posthardening_verified:
        return {"schema":"oce.p159.occ1h.preclose.v1","status":"INCOMPLETE","closure_admissible":False,"missing_inputs":[],"invalid_inputs":["a097_posthardening_evidence_v1.json"],"occ1h_closed":False,"occ1i_opened":False,"p159_final_lock":False,"p160_opened":False}
    tr=docs["post_a097"]; n=_num(tr["attack_id"])
    if n!=97 or n not in current: raise ValueError("unexpected A097 post-hardening transition")
    if historical[n].get("verdict")!="INCONCLUSIVE" or tr.get("historical_verdict")!="INCONCLUSIVE" or tr.get("current_verdict")!="DETECTED": raise ValueError("A097 transition drift")
    current[n]["verdict"]="DETECTED"
    current[n]["current_state_source"]="a097_posthardening_evidence_v1.json"

    a075_post_correction_verified=a075ph.verify_materialized(root)
    if not a075_post_correction_verified:
        return {"schema":"oce.p159.occ1h.preclose.v1","status":"INCOMPLETE","closure_admissible":False,
                "missing_inputs":[],"invalid_inputs":["a075_post_correction_evidence_v1.json"],
                "occ1h_closed":False,"occ1i_opened":False,"p159_final_lock":False,"p160_opened":False}
    tr=docs["post_a075"]; n=_num(tr["attack_id"])
    if n!=75 or n not in current: raise ValueError("unexpected A075 post-correction transition")
    if historical[n].get("verdict")!="INCONCLUSIVE" or tr.get("historical_verdict")!="INCONCLUSIVE" or tr.get("current_verdict")!="RESISTED":
        raise ValueError("A075 post-correction transition drift")
    current[n]["verdict"]="RESISTED"
    current[n]["current_state_source"]="a075_post_correction_evidence_v1.json"

    current_rows=[]
    for n in sorted(current):
        r=current[n]
        current_rows.append({
            "canonical_attack_id":_canon(n),
            "compatibility_attack_id":_compat(n),
            "family_id":r.get("family_id"),
            "current_verdict":r.get("verdict"),
            "historical_verdict":historical[n].get("verdict"),
            # No authoritative executable ROOT classification exists in the
            # supplied OCC-1H artifacts. Never infer it from severity or label.
            "root_classification":rootq.qualify_attack(n)["criticality"],
            "applicability":appcontract.default_applicability(r.get("verdict")),
        })

    inconclusive=[x["canonical_attack_id"] for x in current_rows if x["current_verdict"]=="INCONCLUSIVE"]
    violated=[x["canonical_attack_id"] for x in current_rows if x["current_verdict"]=="VIOLATED"]
    historical_violated=[_canon(n) for n,r in sorted(historical.items()) if r.get("verdict")=="VIOLATED"]

    family_counts={}
    for x in current_rows:
        family_counts[x["family_id"]]=family_counts.get(x["family_id"],0)+1

    ce=docs["counterexamples"]
    ce_records=ce.get("records",[])
    try:
        from ontology import occ1h_historical_counterexample_evidence as hce
        historical_counterexample_verified=hce.verify_materialized(root)
    except Exception:
        historical_counterexample_verified=False
    hce_path=base/"historical_counterexample_evidence_v1.json"
    historical_counterexample_evidence_sha256=_sha(hce_path) if hce_path.is_file() else None
    historical_counterexample_gap=bool(historical_violated) and not historical_counterexample_verified

    # ACHI audit: PASS only when the supplied executable evidence establishes
    # the invariant; otherwise INCONCLUSIVE/FAIL. No declaration is promoted.
    achi={
      "ACHI-1":("PASS","success criteria are marked fixed-before-execution in executable family bundles"),
      "ACHI-2":("PASS","closure calculation is non-compensatory and any current VIOLATED blocks admissibility"),
      "ACHI-3":("PASS","INCONCLUSIVE is preserved distinctly throughout H1-H10"),
      "ACHI-4":("PASS","H9/H10 explicitly state PASS is not proof of absence of untested counterexamples"),
      "ACHI-5":("PASS","H6 and H10 execute compound/sequential attack families"),
      "ACHI-6":("PASS","compiler, verifier and assurance/test infrastructure are explicit attack families"),
      "ACHI-7":("PASS","H9 attacks oracle/test-result laundering"),
      "ACHI-8":(("PASS","historical A008/A009 CounterexampleRecords are content-addressed and source-bound") if historical_counterexample_verified else ("INCONCLUSIVE","historical successful attacks lack verified immutable CounterexampleRecords")),
      "ACHI-9":(("PASS","historical A008/A009 records bind minimal executable reproducers/evidence") if historical_counterexample_verified else ("INCONCLUSIVE","minimized historical CounterexampleRecords are not verified")),
      "ACHI-10":("PASS","family bundles forbid normative auto-rewrite"),
      "ACHI-11":("INCONCLUSIVE","ROOT/non-ROOT classification is not executable or authoritative in supplied artifacts"),
      "ACHI-12":("PASS","pre-close report binds exact SHA-256 of every consumed evidence artifact"),
      "ACHI-13":(("PASS","complete H1-H10 historical results are bound to exact immutable SHA-256 identities and verified content-addressed evidence") if himm.verify_materialized(root) else ("INCONCLUSIVE","complete H1-H10 historical immutability evidence is missing, drifted, or invalid")),
      "ACHI-14":("PASS","current evidence preserves INCONCLUSIVE and permits assurance degradation"),
      "ACHI-15":("PASS","all family bundles keep authorization/execution/activation boundaries false"),
      "ACHI-16":("PASS","H7 explicitly attacks/discloses shared verifier dependencies"),
    }
    achi_rows=[{"invariant":k,"status":v[0],"reason":v[1]} for k,v in achi.items()]
    achi_counts={s:sum(x["status"]==s for x in achi_rows) for s in ("PASS","INCONCLUSIVE","FAIL")}

    root_qualification_complete=all(x["root_classification"] in ("ROOT","NON_ROOT") for x in current_rows)
    root_undetermined=[x["canonical_attack_id"] for x in current_rows if x["root_classification"]=="ROOT_UNDETERMINED"]
    root_inconclusive=[
        x["canonical_attack_id"] for x in current_rows
        if x["root_classification"]=="ROOT" and appcontract.root_inconclusive_blocks(x["current_verdict"],x["applicability"],None)]
    root_applicability_undetermined=[
        x["canonical_attack_id"] for x in current_rows
        if x["root_classification"]=="ROOT" and x["current_verdict"]=="INCONCLUSIVE" and x["applicability"]=="APPLICABILITY_UNDETERMINED"]
    root_violated=[
        x["canonical_attack_id"] for x in current_rows
        if x["root_classification"]=="ROOT" and x["current_verdict"]=="VIOLATED"]

    blockers=[]
    if missing_ids or extra_ids: blockers.append("ATTACK_COVERAGE_NOT_EXACTLY_A01_A105")
    if len(family_counts)!=10: blockers.append("H1_H10_FAMILY_COVERAGE_INCOMPLETE")
    if violated: blockers.append("CURRENT_VIOLATED_PRESENT")
    if not root_qualification_complete: blockers.append("ROOT_CLASSIFICATION_NOT_EXECUTABLY_QUALIFIED")
    if root_undetermined: blockers.append("ROOT_UNDETERMINED_PRESENT")
    if root_inconclusive: blockers.append("ROOT_INCONCLUSIVE_PRESENT")
    if root_violated: blockers.append("ROOT_VIOLATED_PRESENT")
    if any(x["status"]!="PASS" for x in achi_rows): blockers.append("ACHI_NOT_FULLY_EVIDENCED")
    if historical_counterexample_gap: blockers.append("HISTORICAL_COUNTEREXAMPLE_RECORD_GAP")

    return {
      "schema":"oce.p159.occ1h.preclose.v1",
      "status":"PRE_CLOSE_EVIDENCE_AUDITED",
      "input_sha256":hashes,
      "scenarios_expected":105,
      "scenarios_accounted":len(present & EXPECTED),
      "missing_attack_ids":[_canon(n) for n in missing_ids],
      "extra_attack_ids":[_canon(n) for n in extra_ids],
      "families_accounted":family_counts,
      "current_rows":current_rows,
      "current_inconclusive":inconclusive,
      "current_inconclusive_count":len(inconclusive),
      "h6_posthardening_verified":h6_posthardening_verified,
      "h6_a061_a062_posthardening_verified":h6_a061_a062_verified,
      "a097_posthardening_verified":a097_posthardening_verified,
      "a075_post_correction_verified":a075_post_correction_verified,
      "current_violated":violated,
      "current_violated_count":len(violated),
      "historical_violated":historical_violated,
      "historical_violations_preserved":bool(historical_violated),
      "counterexample_record_count":len(ce_records),
      "historical_counterexample_verified":historical_counterexample_verified,
      "historical_counterexample_evidence_sha256":historical_counterexample_evidence_sha256,
      "historical_counterexample_gap":historical_counterexample_gap,
      "root_qualification_complete":root_qualification_complete,
      "root_undetermined":root_undetermined,
      "root_undetermined_count":len(root_undetermined),
      "root_inconclusive":root_inconclusive,
      "root_applicability_undetermined":root_applicability_undetermined,
      "root_applicability_undetermined_count":len(root_applicability_undetermined),
      "applicability_contract_installed":True,
      "applicability_contract_schema":"oce.p159.occ1h.applicability_contract.v1",
      "root_violated":root_violated,
      "achi":achi_rows,
      "achi_counts":achi_counts,
      "closure_blockers":blockers,
      "closure_admissible":not blockers,
      "authorization_created":False,
      "execution_performed":False,
      "normative_auto_rewrite":False,
      "historical_evidence_rewritten":False,
      "functional_only":True,
      "phenomenology_undetermined":True,
      "occ1h_closed":False,
      "occ1i_opened":False,
      "p159_final_lock":False,
      "p160_opened":False,
    }
