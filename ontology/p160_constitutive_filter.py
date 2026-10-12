from __future__ import annotations
from copy import deepcopy
from hashlib import sha256
import json
from typing import Any, Mapping
from ontology import p160_norm_resolution
from ontology import operational_constitutional_invariants as oci
from ontology import dna_fundamental
from ontology import normative_hierarchy
PRIMITIVE="p160_constitutive_filter"; VERSION="P160-C-v1"; SCHEMA="oce.p160c.constitutive_filter.v1"
RESULTS=("PASS","FAIL","CONFLICT","UNDETERMINED")
FUNCTIONAL_ONLY={"functional_conclusion_only":True,"phenomenology_undetermined":True}
BOUNDARIES={"norm_created":False,"norm_modified":False,"conflict_arbitration_performed":False,"authority_resolved":False,"authority_created":False,"authorization_created":False,"authorization_token_created":False,"execution_performed":False,"p160d_opened":False,"p160e_opened":False,"p160f_opened":False,"p160g_opened":False,"p161_opened":False}
def canonical_json(v): return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def canonical_sha256(v): return sha256(canonical_json(v).encode()).hexdigest()
def _status(v):
 s=str(v or "UNDETERMINED").strip().upper(); return s if s in RESULTS else "UNDETERMINED"
def _inv_evidence(evidence,name):
 inv=evidence.get("invariants",evidence); return _status(inv.get(name,"UNDETERMINED")) if isinstance(inv,Mapping) else "UNDETERMINED"
def filter_constitutive(norm_resolution:Mapping[str,Any], evidence:Mapping[str,Any]|None=None)->dict[str,Any]:
 if not isinstance(norm_resolution,Mapping): raise TypeError("norm_resolution must be a mapping")
 if p160_norm_resolution.verify_norm_context(norm_resolution).get("status")!="PASS": raise ValueError("P160B_NORM_CONTEXT_VERIFICATION_REQUIRED")
 evidence=evidence if isinstance(evidence,Mapping) else {}; ctx=norm_resolution.get("norm_context",{})
 constitutive=list(ctx.get("constitutive_constraints",[])) if isinstance(ctx,Mapping) else []
 applicable=set(ctx.get("applicable_norms",[])); non_applicable=set(ctx.get("non_applicable_norms",[]))
 inv_results={n:oci.evaluate_invariant(n,_inv_evidence(evidence,n)) for n in oci.MANDATORY_INVARIANTS}; inv_states=[r["status"] for r in inv_results.values()]
 invariant_status="CONFLICT" if "CONFLICT" in inv_states else "FAIL" if "FAIL" in inv_states else "PASS" if inv_states and all(s=="PASS" for s in inv_states) else "UNDETERMINED"
 ev=evidence.get("constraints",{}) if isinstance(evidence.get("constraints",{}),Mapping) else {}; rows=[]
 for rid in constitutive:
  app="APPLIES" if rid in applicable else "DOES_NOT_APPLY" if rid in non_applicable else "UNDETERMINED"; raw=_status(ev.get(rid,"UNDETERMINED"))
  if app=="DOES_NOT_APPLY": result,disp="UNDETERMINED","OUT_OF_SCOPE_NO_PASS"
  elif app=="UNDETERMINED": result,disp="UNDETERMINED","ABSTAIN"
  elif raw=="PASS": result,disp="PASS","CONTINUE_REVIEW"
  elif raw=="FAIL": result,disp="FAIL","BLOCK_CONSTITUTIVE"
  elif raw=="CONFLICT": result,disp="CONFLICT","ESCALATE_TO_P160D_NOT_ARBITRATED"
  else: result,disp="UNDETERMINED","ABSTAIN"
  rows.append({"rule_id":rid,"applicability":app,"evidence_status":raw,"result":result,"disposition":disp,"authorized":False})
 states=[r["result"] for r in rows]
 overall="FAIL" if "FAIL" in states or invariant_status=="FAIL" else "CONFLICT" if "CONFLICT" in states or invariant_status=="CONFLICT" else "UNDETERMINED" if not rows or "UNDETERMINED" in states or invariant_status=="UNDETERMINED" else "PASS"
 hierarchy=normative_hierarchy.validate_hierarchy(); dna=dna_fundamental.fundamental_manifest()
 if hierarchy.get("status")!="PASS" or dna.get("primitive")!="dna_fundamental": overall="UNDETERMINED"
 out={"schema":SCHEMA,"version":VERSION,"constitutive_filter_result":overall,"constitutive_constraints":rows,"constitutional_invariants":deepcopy(inv_results),"invariant_status":invariant_status,"bindings":deepcopy(norm_resolution.get("bindings",{})),"upstream_p160b_artifact_hash":norm_resolution.get("artifact_hash"),"hierarchy_checked":hierarchy.get("status")=="PASS","dna_boundary_checked":dna.get("primitive")=="dna_fundamental","unknown_promoted_to_pass":False,"conflict_resolved":False,"constitutive_filter_performed":True,"authorized":False,**deepcopy(BOUNDARIES),**deepcopy(FUNCTIONAL_ONLY)}
 out["artifact_hash"]=canonical_sha256(out); return out
def verify_constitutive_filter(value):
 if not isinstance(value,Mapping): return {"status":"FAIL","reason":"NOT_MAPPING",**deepcopy(BOUNDARIES),**deepcopy(FUNCTIONAL_ONLY)}
 x=deepcopy(dict(value)); supplied=x.pop("artifact_hash",None); computed=canonical_sha256(x); rows=x.get("constitutive_constraints",[])
 checks={"schema":x.get("schema")==SCHEMA,"hash":supplied==computed,"states":isinstance(rows,list) and all(isinstance(r,Mapping) and r.get("result") in RESULTS and r.get("authorized") is False for r in rows),"filter_performed":x.get("constitutive_filter_performed") is True,"unknown_not_pass":x.get("unknown_promoted_to_pass") is False,"conflict_not_resolved":x.get("conflict_resolved") is False,"no_authority":x.get("authority_resolved") is False and x.get("authority_created") is False,"no_authorization":x.get("authorization_created") is False and x.get("authorization_token_created") is False and x.get("authorized") is False,"no_execution":x.get("execution_performed") is False,"later_stages_closed":all(x.get(k) is False for k in ("p160d_opened","p160e_opened","p160f_opened","p160g_opened","p161_opened"))}
 return {"status":"PASS" if all(checks.values()) else "FAIL","checks":checks,"supplied_artifact_hash":supplied,"computed_artifact_hash":computed,**deepcopy(BOUNDARIES),**deepcopy(FUNCTIONAL_ONLY)}
def manifest(): return {"primitive":PRIMITIVE,"version":VERSION,"schema":SCHEMA,"scope":"P160-C_ONLY","reuses":["p160_norm_resolution","operational_constitutional_invariants","dna_fundamental","normative_hierarchy"],"excluded_runtime_dependency":["constitutional_non_circumvention","normative_conflict_resolution"],"boundaries":deepcopy(BOUNDARIES),**deepcopy(FUNCTIONAL_ONLY)}
