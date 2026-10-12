from __future__ import annotations
from copy import deepcopy
PRIMITIVE="constitutional_cognitive_economy"; VERSION="P107-v6"; SCHEMA="oce.p107.constitutional_cognitive_economy.v5"
PASS,FAIL,CONFLICT,UNDETERMINED="PASS","FAIL","CONFLICT","UNDETERMINED"
EXECUTION_DEPENDENCIES=("P106","W1/G1_REUSE_ACQUIRED","G2_DNA_FUNDAMENTAL")
REUSE=("P087","P094","P095","P096","P098","P099","P103","P104","P105","P106")
REQUIRED_CONSTRAINTS=("cognitive_budget","risk","dna","constitution","governance")
BOUNDARIES={"normative_admissibility_precedes_optimization":True,"expected_value_never_overrides_normative_rejection":True,
"cognitive_budget_is_constraint_not_consumption_target":True,"risk_is_constraint":True,"unknown_is_not_pass":True,
"conflict_requires_abstention_or_escalation":True,"intelligence_performance_wealth_reputation_majority_do_not_create_authority":True,
"recommendation_decision_authorization_execution_are_distinct":True,"does_not_execute_real_action":True,
"does_not_grant_authority":True,"does_not_implement_p057":True,"does_not_depend_on_world_models":True,
"does_not_claim_runtime_enforcement":True,"functional_conclusion_only":True,"phenomenology_undetermined":True}
def manifest():
    return {"primitive":PRIMITIVE,"version":VERSION,"schema":SCHEMA,"execution_dependencies":EXECUTION_DEPENDENCIES,
            "reuse":REUSE,"required_constraints":REQUIRED_CONSTRAINTS,"boundaries":deepcopy(BOUNDARIES)}
def _status(v):
    if isinstance(v,bool): return PASS if v else FAIL
    s=str(v or "").strip().upper()
    return s if s in {PASS,FAIL,CONFLICT,UNDETERMINED} else UNDETERMINED
def evaluate_option(option):
    o=deepcopy(dict(option or {})); oid=str(o.get("option_id","")).strip()
    if not oid: return {"status":UNDETERMINED,"option_id":"","admissible":False,"next_action":"COMPLETE_EVIDENCE","reason":"missing_option_id"}
    if not o.get("provenance"): return {"status":UNDETERMINED,"option_id":oid,"admissible":False,"next_action":"COMPLETE_EVIDENCE","reason":"missing_provenance"}
    if o.get("privilege_claim") in {"intelligence","performance","wealth","reputation","majority"}:
        return {"status":CONFLICT,"option_id":oid,"admissible":False,"next_action":"ABSTAIN_AND_ESCALATE","reason":"privilege_does_not_create_authority"}
    if any(o.get(k) is True for k in ("indirect_bypass","composition_bypass","mutation_bypass")):
        return {"status":CONFLICT,"option_id":oid,"admissible":False,"next_action":"ABSTAIN_AND_ESCALATE","reason":"constitutional_bypass_attempt"}
    c=dict(o.get("constraints") or {}); missing=[k for k in REQUIRED_CONSTRAINTS if k not in c]
    if missing: return {"status":UNDETERMINED,"option_id":oid,"admissible":False,"next_action":"COMPLETE_EVIDENCE","reason":"missing_constraints","missing":missing}
    statuses={k:_status(c[k]) for k in REQUIRED_CONSTRAINTS}
    if CONFLICT in statuses.values(): return {"status":CONFLICT,"option_id":oid,"admissible":False,"next_action":"ABSTAIN_AND_ESCALATE","reason":"constraint_conflict","constraints":statuses}
    if UNDETERMINED in statuses.values(): return {"status":UNDETERMINED,"option_id":oid,"admissible":False,"next_action":"COMPLETE_EVIDENCE","reason":"constraint_undetermined","constraints":statuses}
    if FAIL in statuses.values(): return {"status":FAIL,"option_id":oid,"admissible":False,"next_action":"REJECT","reason":"constraint_failed","constraints":statuses}
    try: value=float(o["expected_value"])
    except (KeyError,TypeError,ValueError): return {"status":UNDETERMINED,"option_id":oid,"admissible":False,"next_action":"COMPLETE_EVIDENCE","reason":"invalid_expected_value","constraints":statuses}
    import math
    if not math.isfinite(value):
        return {"status":UNDETERMINED,"option_id":oid,"admissible":False,"next_action":"COMPLETE_EVIDENCE","reason":"nonfinite_expected_value","constraints":statuses}
    return {"status":PASS,"option_id":oid,"admissible":True,"expected_value":value,"next_action":"ELIGIBLE_FOR_RECOMMENDATION",
            "reason":"all_constraints_pass","constraints":statuses,"provenance":deepcopy(o["provenance"])}
def select(options):
    src=deepcopy(list(options or [])); evaluations=[evaluate_option(x) for x in src]
    if any(x["status"]==CONFLICT for x in evaluations):
        return {"status":CONFLICT,"selected_option_id":None,"recommendation":None,"next_action":"ABSTAIN_AND_ESCALATE",
                "evaluations":evaluations,"authority_granted":False,"execution_performed":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}
    eligible=[x for x in evaluations if x["status"]==PASS and x.get("admissible")]
    if not eligible:
        return {"status":UNDETERMINED,"selected_option_id":None,"recommendation":None,"next_action":"COMPLETE_EVIDENCE_OR_REJECT",
                "evaluations":evaluations,"authority_granted":False,"execution_performed":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}
    w=sorted(eligible,key=lambda x:(-x["expected_value"],x["option_id"]))[0]
    return {"status":PASS,"selected_option_id":w["option_id"],"recommendation":{"option_id":w["option_id"],"expected_value":w["expected_value"]},
            "next_action":"DECISION_REQUIRED","evaluations":evaluations,"authority_granted":False,"execution_performed":False,
            "functional_conclusion_only":True,"phenomenology_undetermined":True}
def build_decision_payload(result):
    r=deepcopy(dict(result or {}))
    return {"schema":"oce.p107.decision_payload.v1","recommendation":deepcopy(r.get("recommendation")),"decision":None,
            "authorization":None,"execution":None,"status":r.get("status",UNDETERMINED),"next_action":r.get("next_action"),
            "authority_granted":False,"execution_performed":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}

def validate_normative_hierarchy_binding():
    from ontology import normative_hierarchy as p087
    h=p087.validate_hierarchy()
    if h.get("status")!=PASS or not h.get("valid"):
        return {"status":FAIL,"valid":False,"reason":"p087_hierarchy_not_valid","p087_evidence":h,"authority_granted":False,"execution_performed":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}
    checks={"genesis_over_dna_h":p087.compare_levels("GENESIS","DNA-H"),"genesis_over_dna_l0":p087.compare_levels("GENESIS","DNA-L0"),"dna_h_parallel_dna_l0":p087.compare_levels("DNA-H","DNA-L0"),"dna_h_over_dna_l1":p087.compare_levels("DNA-H","DNA-L1"),"dna_l1_over_ccad":p087.compare_levels("DNA-L1","CCAD"),"ccad_over_constitution":p087.compare_levels("CCAD","Constitution"),"constitution_over_governance":p087.compare_levels("Constitution","Governance")}
    expected={"genesis_over_dna_h":"HIGHER","genesis_over_dna_l0":"HIGHER","dna_h_parallel_dna_l0":"EQUAL","dna_h_over_dna_l1":"HIGHER","dna_l1_over_ccad":"HIGHER","ccad_over_constitution":"HIGHER","constitution_over_governance":"HIGHER"}
    if any(checks[k].get("status")!=PASS or checks[k].get("relation")!=expected[k] for k in expected):
        return {"status":FAIL,"valid":False,"reason":"p087_core_precedence_mismatch","precedence_checks":checks,"authority_granted":False,"execution_performed":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}
    contradiction=p087.evaluate_relation("Governance","Constitution","contradict")
    unknown=p087.level_rank("__P107_UNKNOWN_NORMATIVE_LEVEL__")
    if contradiction.get("status")!=CONFLICT or contradiction.get("compatible") is not False:
        return {"status":FAIL,"valid":False,"reason":"p087_lower_contradiction_not_fail_closed","contradiction_check":contradiction,"authority_granted":False,"execution_performed":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}
    if unknown.get("status")!=UNDETERMINED:
        return {"status":FAIL,"valid":False,"reason":"p087_unknown_level_not_undetermined","unknown_level_check":unknown,"authority_granted":False,"execution_performed":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}
    return {"status":PASS,"valid":True,"reason":"p087_canonical_hierarchy_bound","p087_reused":True,"p087_primitive":p087.PRIMITIVE,"p087_version":p087.VERSION,"p087_evidence":h,"precedence_checks":checks,"contradiction_check":contradiction,"unknown_level_check":unknown,"authority_granted":False,"execution_performed":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}

# P107 v3: explicit thin integration over validated constitutional primitives.
def build_governed_assurance(result, ledger_payload, *, recourse_request=None, composition_request=None, conflict_request=None):
    from ontology import action_status_separation as p094
    from ontology import normative_conflict_resolution as p098
    from ontology import constitutional_non_circumvention as p099
    from ontology import constitutional_recourse_recovery as p103
    from ontology import constitutional_decision_ledger as p104
    r=deepcopy(dict(result or {}))
    hierarchy_evidence=validate_normative_hierarchy_binding()
    if hierarchy_evidence.get("status")!=PASS or not hierarchy_evidence.get("valid"):
        return {"status":hierarchy_evidence.get("status",UNDETERMINED),"assured":False,"next_action":"ABSTAIN_AND_ESCALATE","reason":"p087_hierarchy_binding_not_assured","hierarchy_evidence":hierarchy_evidence,"authority_granted":False,"execution_performed":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}
    if r.get("status")!=PASS or not r.get("recommendation"):
        return {"status":r.get("status",UNDETERMINED),"assured":False,"next_action":r.get("next_action","ABSTAIN_AND_ESCALATE"),"reason":"p107_result_not_recommendable","authority_granted":False,"execution_performed":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}
    rec=r["recommendation"]; lp0=deepcopy(dict(ledger_payload or {})); evidence_ref=str(lp0.get("evidence_ref","")).strip()
    incoming_normative=_status(lp0.get("normative_status",PASS))
    if incoming_normative!=PASS:
        return {"status":incoming_normative,"assured":False,"next_action":"ABSTAIN_AND_ESCALATE" if incoming_normative==CONFLICT else "ABSTAIN","reason":"ledger_normative_status_not_pass","authority_granted":False,"execution_performed":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}
    if lp0.get("authority_expanded") is True:
        return {"status":FAIL,"assured":False,"next_action":"REJECT","reason":"ledger_authority_expansion_forbidden","authority_granted":False,"execution_performed":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}
    if lp0.get("stage_conflation") is True:
        return {"status":FAIL,"assured":False,"next_action":"REJECT","reason":"ledger_stage_conflation_forbidden","authority_granted":False,"execution_performed":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}
    auth=lp0.get("authorization")
    if isinstance(auth,dict) and str(auth.get("status","")).strip().upper() in {"GRANTED","AUTHORIZED","PASS","APPROVED"}:
        return {"status":CONFLICT,"assured":False,"next_action":"ABSTAIN_AND_ESCALATE","reason":"recommendation_only_cannot_claim_authorization","authority_granted":False,"execution_performed":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}
    result_claim=str(lp0.get("result","")).strip().upper()
    if result_claim in {"EXECUTED","EXECUTION","ACTION_EXECUTED","AUTHORIZED","APPROVED"}:
        return {"status":CONFLICT,"assured":False,"next_action":"ABSTAIN_AND_ESCALATE","reason":"recommendation_only_cannot_claim_execution_or_authorization","authority_granted":False,"execution_performed":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}
    considered=deepcopy(lp0.get("recommendations_considered") or [])
    if considered and not any(isinstance(x,dict) and str(x.get("option_id","")).strip()==str(rec.get("option_id","")).strip() for x in considered):
        return {"status":CONFLICT,"assured":False,"next_action":"ABSTAIN_AND_ESCALATE","reason":"selected_recommendation_absent_from_recommendations_considered","authority_granted":False,"execution_performed":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}
    if not lp0.get("provenance"):
        return {"status":UNDETERMINED,"assured":False,"next_action":"COMPLETE_EVIDENCE","reason":"missing_ledger_provenance","authority_granted":False,"execution_performed":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}
    if not evidence_ref:
        return {"status":UNDETERMINED,"assured":False,"next_action":"COMPLETE_EVIDENCE","reason":"missing_evidence_ref","authority_granted":False,"execution_performed":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}
    stage=p094.make_recommendation(str(rec["option_id"]),evidence_ref=evidence_ref)
    if stage.get("stage")!="Recommendation":
        return {"status":UNDETERMINED,"assured":False,"next_action":"ABSTAIN","reason":"p094_recommendation_stage_not_established","authority_granted":False,"execution_performed":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}
    conflict_evidence=None
    if conflict_request is not None:
        q=deepcopy(dict(conflict_request)); conflict_evidence=p098.resolve_conflict(q.get("first"),q.get("second"),resolver=q.get("resolver"),selected_norm_id=q.get("selected_norm_id"))
        if conflict_evidence.get("status")!=PASS:
            return {"status":conflict_evidence.get("status",UNDETERMINED),"assured":False,"next_action":conflict_evidence.get("action","ABSTAIN_AND_ESCALATE"),"reason":"p098_conflict_not_resolved","conflict_evidence":conflict_evidence,"authority_granted":False,"execution_performed":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}
    composition_evidence=None
    if composition_request is not None:
        q=deepcopy(dict(composition_request)); composition_evidence=p099.evaluate_composition(q.get("actors"),q.get("requested_permissions",()),q.get("composed_objective_status",UNDETERMINED),normative_status=q.get("normative_status",PASS),influence=q.get("influence"))
        if composition_evidence.get("status")!=PASS:
            return {"status":composition_evidence.get("status",UNDETERMINED),"assured":False,"next_action":composition_evidence.get("action","ABSTAIN"),"reason":"p099_composition_not_assured","composition_evidence":composition_evidence,"authority_granted":False,"execution_performed":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}
    recourse_evidence=None
    if recourse_request is not None:
        recourse_evidence=p103.evaluate_recourse(recourse_request)
        if recourse_evidence.get("status")!=PASS:
            return {"status":recourse_evidence.get("status",UNDETERMINED),"assured":False,"next_action":recourse_evidence.get("action","ABSTAIN_AND_ESCALATE"),"reason":"p103_recourse_not_assured","recourse_evidence":recourse_evidence,"authority_granted":False,"execution_performed":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}
    lp=deepcopy(lp0); lp.pop("evidence_ref",None)
    lp["recommendations_considered"]=deepcopy(lp.get("recommendations_considered") or [rec]); lp["normative_status"]=PASS
    lp["authority_expanded"]=False; lp["stage_conflation"]=False
    selected_eval=next((x for x in r.get("evaluations",[]) if x.get("option_id")==rec.get("option_id")),None)
    if not selected_eval or not selected_eval.get("provenance"):
        return {"status":UNDETERMINED,"assured":False,"next_action":"COMPLETE_EVIDENCE","reason":"selected_option_provenance_missing","authority_granted":False,"execution_performed":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}
    lp["provenance"]=deepcopy(lp["provenance"])
    lp["provenance"]["selected_option_provenance"]=deepcopy(selected_eval["provenance"])
    lp["dependency_refs"]=sorted(set(list(lp.get("dependency_refs",[]))+["P094","P098","P099","P103","P104","P107"]))
    if recourse_evidence is not None:
        lp["recourse_refs"]=deepcopy(lp.get("recourse_refs") or ["P103:"+str(recourse_evidence.get("result_hash",""))])
        if str(recourse_evidence.get("mechanism","")).upper()=="ROLLBACK": lp["rollback_refs"]=deepcopy(lp.get("rollback_refs") or lp["recourse_refs"])
    built=p104.build_record(lp)
    if built.get("status")!=PASS:
        return {"status":built.get("status",UNDETERMINED),"assured":False,"next_action":built.get("action","ABSTAIN"),"reason":"p104_ledger_record_not_eligible","ledger_evidence":built,"authority_granted":False,"execution_performed":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}
    return {"status":PASS,"assured":True,"next_action":"DECISION_REQUIRED","hierarchy_evidence":hierarchy_evidence,"recommendation_stage":stage,"conflict_evidence":conflict_evidence,"composition_evidence":composition_evidence,"recourse_evidence":recourse_evidence,"ledger_evidence":built,"authority_granted":False,"execution_performed":False,"runtime_enforcement_claimed":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}

def persist_governed_trace(assurance, *, root, filesystem_effect_context=None):
    from ontology import constitutional_decision_ledger as p104
    a=deepcopy(dict(assurance or {}))
    if a.get("status")!=PASS or not a.get("assured"):
        return {"status":UNDETERMINED,"persisted":False,"reason":"assurance_not_pass","authority_granted":False,"execution_performed":False}
    record=deepcopy(a.get("ledger_evidence",{}).get("record"))
    if not record:
        return {"status":UNDETERMINED,"persisted":False,"reason":"ledger_record_missing","authority_granted":False,"execution_performed":False}
    return p104.persist_record(record,root=root,filesystem_effect_context=filesystem_effect_context)

