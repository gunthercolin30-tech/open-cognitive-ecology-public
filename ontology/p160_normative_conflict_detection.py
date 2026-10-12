from __future__ import annotations
from copy import deepcopy
from hashlib import sha256
import json
from itertools import combinations
from typing import Any, Mapping, Sequence
from ontology import p160_constitutive_filter as p160c
from ontology import ccad_specification as p156

PRIMITIVE="p160_normative_conflict_detection"
VERSION="P160-D-v1.1-defensive"
SCHEMA="oce.p160d.normative_conflict_detection.v1"
FUNCTIONAL_ONLY={"functional_conclusion_only":True,"phenomenology_undetermined":True}
REQUIREMENT_TYPES=("PROHIBITION","OBLIGATION","PRESERVATION","MINIMIZATION","DISCLOSURE","REVIEW","CONSENT","AUTHORITY","PROPORTIONALITY","CONTINUITY")
COMPATIBILITY=("COMPATIBLE","POTENTIALLY_TENSIONED","INCOMPATIBLE_UNDER_CURRENT_OPTION","INCOMPATIBLE_ACROSS_AVAILABLE_OPTIONS")
SEARCH_COMPLETENESS=("EXHAUSTIVE_WITHIN_DEFINED_SPACE","ADEQUATE_SEARCH","PARTIAL_SEARCH","SEARCH_FAILED")
AVAILABILITY=("AVAILABLE_NOW","AFTER_REVIEW","AFTER_AUTHORITY_ESCALATION","TECHNICALLY_UNAVAILABLE","NORMATIVELY_INVALID","UNKNOWN_FEASIBILITY")
CERTAINTY=("ESTABLISHED","PROBABLE","CONDITIONAL","UNRESOLVED")
BOUNDARIES={"conflict_detection_performed":True,"conflict_arbitration_performed":False,"winner_selected":False,"norm_created":False,"norm_modified":False,"authority_resolved":False,"authority_created":False,"authorization_created":False,"authorization_token_created":False,"execution_performed":False,"p160e_opened":False,"p160f_opened":False,"p160g_opened":False,"p161_opened":False}

def canonical_json(v): return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def canonical_sha256(v): return sha256(canonical_json(v).encode()).hexdigest()
def _present(v): return v is not None and str(v).strip().upper() not in ("","UNKNOWN","UNDETERMINED","UNRESOLVED")
def _list(v): return list(v) if isinstance(v,(list,tuple)) else []

def _verify_c(ca):
    if not isinstance(ca,Mapping) or p160c.verify_constitutive_filter(ca).get("status")!="PASS":
        raise ValueError("P160C_VERIFIED_CONSTITUTIVE_ASSESSMENT_REQUIRED")
    if ca.get("constitutive_filter_result")!="PASS":
        raise ValueError("P160D_PRECONDITION_CONSTITUTIVE_OK_REQUIRED")

def _requirement(row):
    rid=str(row.get("requirement_id") or row.get("norm_id") or "").strip()
    typ=str(row.get("type") or "").strip().upper()
    sources=sorted(set(str(x) for x in _list(row.get("source_norms")) if str(x).strip()))
    required=("protected_interest","affected_entities","condition","scope","time","formalization","flexibility")
    missing=[k for k in required if not _present(row.get(k))]
    if not rid or not sources or typ not in REQUIREMENT_TYPES or missing:
        return {"valid":False,"requirement_id":rid or "UNKNOWN","reason":"REQUIREMENT_INCOMPLETE_OR_INVALID","missing":missing}
    return {"valid":True,"requirement_id":rid,"source_norms":sources,"type":typ,"protected_interest":deepcopy(row["protected_interest"]),"affected_entities":sorted(set(str(x) for x in _list(row["affected_entities"]))),"condition":deepcopy(row["condition"]),"scope":deepcopy(row["scope"]),"time":deepcopy(row["time"]),"formalization":deepcopy(row["formalization"]),"flexibility":deepcopy(row["flexibility"])}

def _alternative(row,req_ids):
    aid=str(row.get("alternative_id") or "").strip()
    availability=str(row.get("availability") or "").strip().upper()
    comp=row.get("compatibility",{})
    if not isinstance(comp,Mapping): comp={}
    normalized={}; invalid=[]
    for rid in sorted(req_ids):
        state=str(comp.get(rid,"UNRESOLVED")).strip().upper()
        if state not in COMPATIBILITY: invalid.append(rid); state="UNRESOLVED"
        normalized[rid]=state
    required=("effects","impacts","resources","latency","reversibility","uncertainty","feasibility","authority")
    missing=[k for k in required if k not in row]
    valid=bool(aid) and availability in AVAILABILITY and not missing and not invalid
    return {"valid":valid,"alternative_id":aid or "UNKNOWN","availability":availability or "UNKNOWN","effects":deepcopy(row.get("effects")),"requirements":sorted(req_ids),"impacts":deepcopy(row.get("impacts")),"resources":deepcopy(row.get("resources")),"latency":deepcopy(row.get("latency")),"reversibility":deepcopy(row.get("reversibility")),"uncertainty":deepcopy(row.get("uncertainty")),"feasibility":deepcopy(row.get("feasibility")),"authority":deepcopy(row.get("authority")),"compatibility":normalized,"missing_fields":missing,"invalid_compatibility":invalid}

def detect_normative_conflict(constitutive_assessment,requirements,alternatives,*,search_completeness,search_receipt=None,classification_evidence=None):
    _verify_c(constitutive_assessment)
    sc=str(search_completeness or "").strip().upper()
    if sc not in SEARCH_COMPLETENESS: sc="SEARCH_FAILED"
    ce=deepcopy(dict(classification_evidence or {})) if isinstance(classification_evidence,Mapping) else {}
    reqs=[_requirement(r) for r in requirements if isinstance(r,Mapping)]
    valid_reqs=[r for r in reqs if r["valid"]]; req_ids={r["requirement_id"] for r in valid_reqs}
    alts=[_alternative(a,req_ids) for a in alternatives if isinstance(a,Mapping)]
    invalid_input=bool([r for r in reqs if not r["valid"]]) or bool([a for a in alts if not a["valid"]]) or len(valid_reqs)<2
    considered=[a for a in alts if a["valid"] and a["availability"] in ("AVAILABLE_NOW","AFTER_REVIEW","AFTER_AUTHORITY_ESCALATION")]
    pair_edges=[]; nary_sets=[]; any_current=False; all_incompatible=bool(considered)
    for a in considered:
        inc=sorted(rid for rid,s in a["compatibility"].items() if s=="INCOMPATIBLE_UNDER_CURRENT_OPTION")
        if inc: any_current=True
        else: all_incompatible=False
        for x,y in combinations(inc,2): pair_edges.append({"alternative_id":a["alternative_id"],"requirements":[x,y]})
        if len(inc)>=2: nary_sets.append({"alternative_id":a["alternative_id"],"requirements":inc})
    adequate=sc in ("EXHAUSTIVE_WITHIN_DEFINED_SPACE","ADEQUATE_SEARCH")
    unknown_feasibility=any(a["availability"]=="UNKNOWN_FEASIBILITY" for a in alts)
    established=not invalid_input and adequate and not unknown_feasibility and len(valid_reqs)>=2 and all_incompatible
    indicator_map={"ordinary_violation":"ORDINARY_VIOLATION","missing_fact":"MISSING_FACT","unknown_authority":"UNKNOWN_AUTHORITY","fake_binary":"FAKE_BINARY","suppressed_alternative":"SUPPRESSED_ALTERNATIVE","resource_issue":"RESOURCE_OR_IMPLEMENTATION_ISSUE","self_interest":"SELF_INTEREST","unverified_emergency":"UNVERIFIED_EMERGENCY","constitutive_repackaging":"CONSTITUTIVE_REPACKAGING"}
    fi=[v for k,v in indicator_map.items() if ce.get(k) is True]
    if invalid_input:
        klass,certainty,compat,status="C0","UNRESOLVED","POTENTIALLY_TENSIONED","CONFLICT_ASSESSMENT_INCOMPLETE"
        fi.append("MISSING_OR_INVALID_REQUIREMENT_OR_ALTERNATIVE")
    elif not adequate:
        klass,certainty,compat,status="C0","UNRESOLVED","POTENTIALLY_TENSIONED","ALTERNATIVE_SEARCH_INCOMPLETE"
        fi.append("INCOMPLETE_SEARCH_NOT_NO_ALTERNATIVE")
    elif unknown_feasibility:
        klass,certainty,compat,status="C0","UNRESOLVED","POTENTIALLY_TENSIONED","ALTERNATIVE_FEASIBILITY_UNRESOLVED"
        fi.append("UNKNOWN_FEASIBILITY_NOT_NO_ALTERNATIVE")
    elif fi:
        klass,certainty,compat,status="C0","UNRESOLVED","POTENTIALLY_TENSIONED","FALSE_CONFLICT_INDICATOR_PRESENT"
    elif established:
        hint=str(ce.get("conflict_class_hint") or "C2").upper()
        if hint not in ("C2","C3","C4","C5","C6"): hint="C2"
        escalation=bool(ce.get("legitimate_escalation_available"))
        legitimate_option=bool(ce.get("legitimate_option_available"))
        if hint=="C6" and (escalation or legitimate_option):
            klass,certainty,compat,status="C4","UNRESOLVED","INCOMPATIBLE_ACROSS_AVAILABLE_OPTIONS","C6_REJECTED_ESCALATION_OR_OPTION_AVAILABLE"
        elif hint=="C5":
            klass,certainty,compat,status="C5","PROBABLE","INCOMPATIBLE_ACROSS_AVAILABLE_OPTIONS","TRAGIC_CHOICE_CANDIDATE_REQUIRES_P160E"
        elif hint=="C6":
            klass,certainty,compat,status="C6","CONDITIONAL","INCOMPATIBLE_ACROSS_AVAILABLE_OPTIONS","CONSTITUTIONAL_IMPOSSIBILITY_CANDIDATE_REQUIRES_P160E"
        else:
            klass,certainty,compat,status=hint,"ESTABLISHED","INCOMPATIBLE_ACROSS_AVAILABLE_OPTIONS","CONFLICT_DETECTED"
    elif any_current:
        klass,certainty,compat,status="C1","CONDITIONAL","INCOMPATIBLE_UNDER_CURRENT_OPTION","NO_REAL_CONFLICT_ALTERNATIVE_AVAILABLE"
        fi.append("CURRENT_OPTION_ONLY_INCOMPATIBILITY")
    else:
        klass,certainty,compat,status="C0","ESTABLISHED","COMPATIBLE","NO_CONFLICT"
    affected=[{"requirement_id":r["requirement_id"],"protected_interest":deepcopy(r["protected_interest"]),"affected_entities":deepcopy(r["affected_entities"])} for r in valid_reqs]
    receipt={"search_completeness":sc,"candidate_count":len(alts),"considered_count":len(considered),"receipt":deepcopy(search_receipt or {}),"no_alternative_inferred_from_incomplete_search":False}
    graph={"nodes":sorted(req_ids),"pair_edges":sorted(pair_edges,key=canonical_json),"nary_conflict_sets":sorted(nary_sets,key=canonical_json),"pairwise_only":False}
    minimal=[]
    if established:
        for a in considered:
            inc=sorted(rid for rid,s in a["compatibility"].items() if s=="INCOMPATIBLE_UNDER_CURRENT_OPTION")
            if inc: minimal.append({"alternative_id":a["alternative_id"],"requirements":inc})
    out={"schema":SCHEMA,"version":VERSION,"conflict_assessment":{"status":status,"conflict_class":klass,"conflict_class_name":p156.CONFLICT_CLASSES[klass],"compatibility":compat,"certainty":certainty,"real_conflict_established":established,"false_conflict_indicators":fi,"minimal_conflict_set":minimal,"classification_limit":"P160D_DETECTS_C0_C6; C5_C6_REMAIN_CANDIDATES_FOR_P160E_CONFIRMATION","c5_confirmed":False,"c6_confirmed":False,"classification_evidence":ce},"normative_requirement":valid_reqs,"alternative_set":alts,"normative_conflict_graph":graph,"alternative_search_receipt":receipt,"affected_interest":affected,"bindings":{"p160c_artifact_hash":constitutive_assessment.get("artifact_hash"),"p160c_upstream_p160b_artifact_hash":constitutive_assessment.get("upstream_p160b_artifact_hash"),"runtime_bindings":deepcopy(constitutive_assessment.get("bindings",{}))},"constitutive_precondition":{"verified":True,"p160c_result":"PASS","canonical_equivalent":"CONSTITUTIVE_OK"},"detector_selected_winner":False,"precedent_promoted_to_norm":False,"aggregate_benefit_erased_minority_harm":False,"unknown_promoted_to_conflict":False,**deepcopy(BOUNDARIES),**deepcopy(FUNCTIONAL_ONLY)}
    out["artifact_hash"]=canonical_sha256(out); return out

def verify_conflict_assessment(value):
    if not isinstance(value,Mapping): return {"status":"FAIL","reason":"NOT_MAPPING",**deepcopy(BOUNDARIES),**deepcopy(FUNCTIONAL_ONLY)}
    x=deepcopy(dict(value)); supplied=x.pop("artifact_hash",None); computed=canonical_sha256(x)
    ca=x.get("conflict_assessment",{}); receipt=x.get("alternative_search_receipt",{}); graph=x.get("normative_conflict_graph",{})
    checks={"schema":x.get("schema")==SCHEMA,"hash":supplied==computed,"class":ca.get("conflict_class") in p156.CONFLICT_CLASSES,"certainty":ca.get("certainty") in CERTAINTY,"search":receipt.get("search_completeness") in SEARCH_COMPLETENESS,"incomplete_not_no_alternative":receipt.get("no_alternative_inferred_from_incomplete_search") is False,"nary_graph":isinstance(graph,Mapping) and graph.get("pairwise_only") is False,"no_winner":x.get("detector_selected_winner") is False and x.get("winner_selected") is False,"no_arbitration":x.get("conflict_arbitration_performed") is False,"no_authority":x.get("authority_resolved") is False and x.get("authority_created") is False,"no_authorization":x.get("authorization_created") is False and x.get("authorization_token_created") is False,"no_execution":x.get("execution_performed") is False,"no_norm_promotion":x.get("precedent_promoted_to_norm") is False,"no_moral_laundering":x.get("aggregate_benefit_erased_minority_harm") is False,"unknown_not_conflict":x.get("unknown_promoted_to_conflict") is False,"c5_not_confirmed":ca.get("c5_confirmed") is False,"c6_not_confirmed":ca.get("c6_confirmed") is False,"c6_gate":not (ca.get("conflict_class")=="C6" and (ca.get("classification_evidence",{}).get("legitimate_escalation_available") or ca.get("classification_evidence",{}).get("legitimate_option_available"))),"affected_interest_complete":sorted((a.get("requirement_id"),tuple(a.get("affected_entities",[]))) for a in x.get("affected_interest",[]))==sorted((r.get("requirement_id"),tuple(r.get("affected_entities",[]))) for r in x.get("normative_requirement",[])),"later_closed":all(x.get(k) is False for k in ("p160e_opened","p160f_opened","p160g_opened","p161_opened"))}
    return {"status":"PASS" if all(checks.values()) else "FAIL","checks":checks,"supplied_artifact_hash":supplied,"computed_artifact_hash":computed,**deepcopy(BOUNDARIES),**deepcopy(FUNCTIONAL_ONLY)}

def manifest():
    return {"primitive":PRIMITIVE,"version":VERSION,"schema":SCHEMA,"scope":"P160-D_ONLY","artifacts":["conflict_assessment","normative_requirement","alternative_set","normative_conflict_graph","alternative_search_receipt","affected_interest"],"reuses":["p160_constitutive_filter","ccad_specification.CONFLICT_CLASSES","ccad_specification.PRINCIPLES.P2","normative_conflict_resolution.validation_discipline"],"does_not_call":["normative_conflict_resolution.resolve_conflict"],"boundaries":deepcopy(BOUNDARIES),**deepcopy(FUNCTIONAL_ONLY)}
