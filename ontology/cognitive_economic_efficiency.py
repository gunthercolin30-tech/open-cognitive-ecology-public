"""P151 — Cognitive Economic Efficiency. Functional metric only."""
from __future__ import annotations
from typing import Any, Mapping, Sequence
import hashlib,json,math
PRIMITIVE="cognitive_economic_efficiency"; CANONICAL_ID="P151"
DEPENDENCIES=["strategy_selection","metrics_history_recorder","outcome_monitoring","trajectory_outcome_evaluation"]
COST_COMPONENTS=("compute","energy","api","human","maintenance","coordination","governance","risk")
def _hash(x): return hashlib.sha256(json.dumps(dict(x),sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
def _num(v,f):
    if isinstance(v,bool): raise ValueError(f+": boolean invalid")
    try: x=float(v)
    except (TypeError,ValueError): raise ValueError(f+": numeric required")
    if not math.isfinite(x) or x<0: raise ValueError(f+": finite non-negative required")
    return x
def _prov(v,f):
    s=str(v or "").strip()
    if not s: raise ValueError(f+": provenance required")
    return s
class CognitiveEconomicEfficiency:
 def evaluate(self,*,verified_economic_value,costs,unit,period_id):
    unit=str(unit or "").strip(); period_id=str(period_id or "").strip()
    if not unit or not period_id: raise ValueError("unit and period_id required")
    if not isinstance(costs,Mapping): raise ValueError("costs mapping required")
    missing=[k for k in COST_COMPONENTS if k not in costs or costs[k] is None]
    if verified_economic_value is None: missing.append("verified_economic_value")
    common={"canonical_id":CANONICAL_ID,"primitive":PRIMITIVE,"period_id":period_id,"unit":unit,"functional_conclusion_only":True,"phenomenology_undetermined":True}
    if missing: return dict(common,status="UNKNOWN",cee=None,total_cognitive_cost=None,verified_economic_value_created=None,missing_evidence=sorted(missing),economic_claim_allowed=False)
    if not isinstance(verified_economic_value,Mapping): raise ValueError("value mapping required")
    if verified_economic_value.get("verified") is not True: return dict(common,status="UNKNOWN",cee=None,total_cognitive_cost=None,verified_economic_value_created=None,missing_evidence=["verified_economic_value.verification"],economic_claim_allowed=False)
    if str(verified_economic_value.get("unit","")).strip()!=unit: raise ValueError("value unit mismatch")
    value=_num(verified_economic_value.get("amount"),"value.amount"); vp=_prov(verified_economic_value.get("provenance"),"value")
    normalized={}; total=0.0
    for k in COST_COMPONENTS:
        r=costs[k]
        if not isinstance(r,Mapping): raise ValueError(k+": mapping required")
        if str(r.get("unit","")).strip()!=unit: raise ValueError(k+": unit mismatch")
        if r.get("measured") is not True: return dict(common,status="UNKNOWN",cee=None,total_cognitive_cost=None,verified_economic_value_created=None,missing_evidence=[k+".measurement"],economic_claim_allowed=False)
        a=_num(r.get("amount"),k+".amount"); p=_prov(r.get("provenance"),k); total+=a; normalized[k]={"amount":a,"unit":unit,"measured":True,"provenance":p}
    if total<=0: return dict(common,status="UNDEFINED_ZERO_COST",cee=None,total_cognitive_cost=total,verified_economic_value_created=value,missing_evidence=[],economic_claim_allowed=False)
    evidence={"period_id":period_id,"unit":unit,"value":{"amount":value,"verified":True,"provenance":vp},"costs":normalized}
    return dict(common,status="COMPUTED",cee=value/total,total_cognitive_cost=total,verified_economic_value_created=value,cost_components=normalized,evidence_hash=_hash(evidence),missing_evidence=[],economic_claim_allowed=True)
 @staticmethod
 def trend(records:Sequence[Mapping[str,Any]]):
    if isinstance(records,(str,bytes)) or not isinstance(records,Sequence): raise ValueError("records sequence required")
    c=[r for r in records if isinstance(r,Mapping) and r.get("status")=="COMPUTED"]
    if len(c)<2: return {"status":"UNKNOWN","cee_t_increasing":None,"reason":"insufficient_computed_periods"}
    if len({r.get("unit") for r in c})!=1: raise ValueError("common unit required")
    v=[_num(r.get("cee"),"cee") for r in c]
    return {"status":"COMPUTED","cee_t_increasing":all(b>a for a,b in zip(v,v[1:])),"period_count":len(v),"first_cee":v[0],"last_cee":v[-1],"functional_conclusion_only":True,"phenomenology_undetermined":True}
