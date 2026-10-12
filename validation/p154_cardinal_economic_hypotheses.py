"""P154 — Cardinal economic hypotheses H1-H7. Functional evidence-governance contract only."""
from __future__ import annotations
from typing import Any, Mapping
import hashlib,json,math
CANONICAL_ID="P154"
DECISIONS=("GO","GO_WITH_CHANGES","RETHINK","STOP_COMPONENT")
HYPOTHESES={
"H1":{"title":"OCE > BestOfBreedStack","priority":"EARLY_CARDINAL","signal":"DeltaValue_OCE","default_threshold":0.0,"failure_consequence":"REPOSITION_OR_SIMPLIFY_OCE"},
"H2":{"title":"PersistentSpecialist > StatelessAlternative","priority":"EARLY_CARDINAL","signal":"NetPersistenceGain","default_threshold":0.0,"failure_consequence":"DO_NOT_BUILD_INDIVIDUAL_ECONOMY"},
"H3":{"title":"Experience -> HigherValue and/or LowerCost","priority":"EARLY_CARDINAL","signal":"LongitudinalImprovement","default_threshold":0.0,"failure_consequence":"WEAKEN_COGNITIVE_CAPITAL_THESIS"},
"H4":{"title":"CognitiveCompilationGain > 0","priority":"LATER","signal":"CognitiveCompilationGain","default_threshold":1.0,"failure_consequence":"DO_NOT_CENTER_BUSINESS_ON_COMPILATION"},
"H5":{"title":"CollectiveSynergyGain > 0","priority":"LATER","signal":"CollectiveSynergyGain","default_threshold":0.0,"failure_consequence":"REDUCE_OR_LIMIT_CROWD_ENGINE"},
"H6":{"title":"Governance/Trust creates measurable economic value","priority":"LATER","signal":"GovernanceTrustEconomicValue","default_threshold":0.0,"failure_consequence":"KEEP_GOVERNANCE_AS_CONSTRAINT_NOT_STANDALONE_PRODUCT"},
"H7":{"title":"MarketplaceLiquidity > Threshold","priority":"LATE","signal":"MarketplaceLiquidity","default_threshold":None,"failure_consequence":"DO_NOT_BUILD_OR_MAINTAIN_MARKETPLACE"}}
def _canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def _hash(x): return hashlib.sha256(_canonical(x)).hexdigest()
def _finite(v,f):
    if isinstance(v,bool): raise ValueError(f+": boolean invalid")
    try: x=float(v)
    except (TypeError,ValueError): raise ValueError(f+": numeric required")
    if not math.isfinite(x): raise ValueError(f+": finite numeric required")
    return x
def _text(v,f):
    s=str(v or "").strip()
    if not s: raise ValueError(f+": required")
    return s
def preregister(*,hypothesis_id,protocol,baseline,threshold=None,target_family,next_reevaluation_date,preregistered_at):
    hid=str(hypothesis_id).upper().strip()
    if hid not in HYPOTHESES: raise ValueError("unknown hypothesis_id")
    h=HYPOTHESES[hid]
    if not isinstance(baseline,Mapping): raise ValueError("baseline mapping required")
    if threshold is None: threshold=h["default_threshold"]
    if threshold is None: raise ValueError(hid+": threshold must be defined ex ante")
    body={"canonical_id":CANONICAL_ID,"hypothesis_id":hid,"title":h["title"],"priority":h["priority"],"signal":h["signal"],
      "protocol":_text(protocol,"protocol"),"baseline":{"name":_text(baseline.get("name"),"baseline.name"),"provenance":_text(baseline.get("provenance"),"baseline.provenance")},
      "threshold":_finite(threshold,"threshold"),"target_family":_text(target_family,"target_family"),
      "next_reevaluation_date":_text(next_reevaluation_date,"next_reevaluation_date"),"preregistered_at":_text(preregistered_at,"preregistered_at"),
      "failure_consequence":h["failure_consequence"],"functional_conclusion_only":True,"phenomenology_undetermined":True}
    return dict(body,preregistration_hash=_hash(body))
def evaluate(registration,evidence):
    if not isinstance(registration,Mapping) or not isinstance(evidence,Mapping): raise ValueError("mapping required")
    reg=dict(registration); expected=reg.pop("preregistration_hash",None)
    if not expected or _hash(reg)!=expected: raise ValueError("preregistration integrity failure")
    hid=reg.get("hypothesis_id")
    if evidence.get("hypothesis_id")!=hid: raise ValueError("hypothesis mismatch")
    if evidence.get("preregistration_hash")!=expected: raise ValueError("evidence/preregistration mismatch")
    common={"canonical_id":CANONICAL_ID,"hypothesis_id":hid,"priority":reg["priority"],"failure_consequence":reg["failure_consequence"],
      "preregistration_hash":expected,"functional_conclusion_only":True,"phenomenology_undetermined":True,"economic_hypothesis_empirically_proven":False}
    if evidence.get("verified") is not True or evidence.get("external_signal") is not True:
        return dict(common,status="UNKNOWN",decision="RETHINK",reason="verified_external_signal_required",economic_claim_allowed=False)
    result=_finite(evidence.get("result"),"result"); confidence=_finite(evidence.get("confidence"),"confidence")
    uncertainty=_finite(evidence.get("uncertainty"),"uncertainty")
    if not 0<=confidence<=1: raise ValueError("confidence must be within [0,1]")
    if uncertainty<0: raise ValueError("uncertainty must be non-negative")
    reps=evidence.get("replications")
    if isinstance(reps,bool) or not isinstance(reps,int) or reps<1: raise ValueError("replications must be integer >= 1")
    provenance=_text(evidence.get("provenance"),"provenance"); threshold=_finite(reg["threshold"],"threshold")
    passed=result>threshold; durable=evidence.get("durable_failure") is True
    if passed: status,decision="SUPPORTED_BY_CURRENT_EVIDENCE","GO"
    elif durable: status,decision="DURABLY_FALSIFIED","STOP_COMPONENT"
    else: status,decision="NOT_SUPPORTED","RETHINK"
    normalized={"result":result,"threshold":threshold,"confidence":confidence,"uncertainty":uncertainty,"replications":reps,"provenance":provenance,"external_signal":True,"verified":True}
    return dict(common,status=status,decision=decision,passed=passed,evidence=normalized,evidence_hash=_hash(normalized),economic_claim_allowed=passed)
def hypothesis_table(): return [dict(hypothesis_id=k,**v) for k,v in HYPOTHESES.items()]
