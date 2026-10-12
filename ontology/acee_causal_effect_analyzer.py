"""ACEE9 — governed causal attribution of ACEE8 observed impacts."""
from __future__ import annotations
import fcntl, hashlib, json, math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, pstdev
from typing import Any, Dict, Mapping, Optional, Tuple
PRIMITIVE="ACEE_CAUSAL_EFFECT_ANALYZER"
STATUS_READY="ACEE_CAUSAL_EFFECT_RESOLVED"
STATUS_DEGRADED="ACEE_CAUSAL_EFFECT_DEGRADED"
PUBLIC_SCHEMA_VERSION="1.0.0"
def _now(): return datetime.now(timezone.utc).isoformat().replace("+00:00","Z")
def _mapping(v): return dict(v) if isinstance(v,Mapping) else {}
def _finite(v):
    if isinstance(v,bool): return None
    try: n=float(v)
    except (TypeError,ValueError,OverflowError): return None
    return n if math.isfinite(n) else None
def _clamp(v): return max(0.0,min(1.0,v))
def _canonical(v): return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def _sha(v): return hashlib.sha256(_canonical(v).encode("utf-8")).hexdigest()
@dataclass
class AceeCausalEffectAnalyzer:
    root: Optional[Path]=None
    def __post_init__(self):
        self.root=(Path(self.root) if self.root is not None else Path.home()/"open-cognitive-ecology").expanduser().resolve()
    def _paths(self)->Tuple[Path,Path,Path]:
        d=self.root/"acee_runtime"/"ACEE9_acee_causal_effect_analyzer"
        return d/"latest_causal_effect.json",d/"causal_effect_history.jsonl",d/".causal_effect.lock"
    def _previous(self,h):
        if not h.is_file(): return None,False
        try:
            lines=[x for x in h.read_text(encoding="utf-8").splitlines() if x.strip()]
            return (json.loads(lines[-1]),False) if lines else (None,False)
        except (OSError,json.JSONDecodeError,TypeError): return None,True
    def _build(self,s,previous_hash,corrupted):
        impact=_mapping(s.get("impact_evaluation")); intervention=_mapping(s.get("intervention")); effect=_finite(impact.get("impact_score"))
        reps=[]
        raw=s.get("replications",[])
        if isinstance(raw,(list,tuple)):
            for item in raw:
                n=_finite(item.get("effect_size") if isinstance(item,Mapping) else item)
                if n is not None: reps.append(n)
        counter=_finite(s.get("counterfactual_effect"))
        alts=s.get("alternative_explanations",[]); alts=[str(x) for x in alts] if isinstance(alts,(list,tuple,set)) else []
        blocking=[]
        if impact.get("comparison_valid") is not True: blocking.append("valid_impact_evaluation_required")
        if impact.get("ready_for_causal_analysis") is False: blocking.append("impact_not_ready_for_causal_analysis")
        if effect is None: blocking.append("finite_impact_score_required")
        if intervention.get("executed") is not True: blocking.append("executed_intervention_required")
        if not reps: blocking.append("replication_evidence_required")
        if counter is None: blocking.append("counterfactual_effect_required")
        if corrupted: blocking.append("history_corrupted")
        e=effect if effect is not None else 0.0
        rm=mean(reps) if reps else 0.0; rs=pstdev(reps) if len(reps)>1 else 0.0
        replication_consistency=_clamp(1.0-rs)
        counterfactual_consistency=_clamp(abs(e-counter)) if counter is not None else 0.0
        direction_alignment=1.0 if reps and ((rm>=0)==(e>=0)) else 0.0
        agreement=_clamp(1.0-abs(rm-e)) if reps else 0.0
        robustness=round(mean([replication_consistency,agreement,direction_alignment]),6) if reps else 0.0
        confounded=bool(alts) or (counter is not None and abs(e-counter)<max(0.01,abs(e)*0.25))
        probability=round(mean([robustness,counterfactual_consistency,0.0 if alts else 1.0,1.0 if intervention.get("executed") is True else 0.0]),6)
        confidence=round(probability*(0.75+0.25*min(1.0,len(reps)/4.0)),6)
        resolved=not blocking and not confounded and probability>=0.5
        direction="beneficial" if e>1e-12 else "harmful" if e<-1e-12 else "neutral"
        r={"primitive":PRIMITIVE,"public_schema_version":PUBLIC_SCHEMA_VERSION,"analysis_id":str(s.get("analysis_id") or "causal-unspecified"),"timestamp_utc":str(s.get("timestamp_utc") or _now()),"causal_status":STATUS_READY if resolved else STATUS_DEGRADED,"causal_effect_resolved":resolved,"causal_probability":probability,"causal_confidence":confidence,"effect_size":round(e,12),"effect_direction":direction,"replication_count":len(reps),"replication_mean_effect":round(rm,12),"replication_std":round(rs,12),"statistical_robustness":robustness,"counterfactual_effect":counter,"counterfactual_consistency":round(counterfactual_consistency,6),"alternative_explanations":alts,"alternative_explanations_eliminated":not alts,"confounding_detected":confounded,"blocking_reasons":sorted(set(blocking)),"ready_for_selection":resolved,"selection_decision_made":False,"rollback_executed":False,"acee11_called":False,"impact_evaluation_hash":impact.get("impact_hash"),"previous_analysis_hash":previous_hash,"history_corrupted":corrupted,"functional_conclusion_only":True,"phenomenology_undetermined":True,"consciousness_proven":False,"subjectivity_proven":False,"qualia_proven":False,"phenomenology_proven":False,"collective_consciousness_proven":False,"collective_subjectivity_proven":False,"collective_qualia_proven":False,"collective_phenomenology_proven":False}
        r["analysis_hash"]=_sha({k:v for k,v in r.items() if k!="analysis_hash"}); return r
    def step(self,inputs:Mapping[str,Any]|None=None,persist:bool=False)->Dict[str,Any]:
        s=_mapping(inputs); latest,history,lock=self._paths(); previous,corrupted=self._previous(history)
        r=self._build(s,previous.get("analysis_hash") if previous else None,corrupted); r.update({"persisted":False,"latest_path":str(latest),"history_path":str(history)})
        if not persist: return r
        latest.parent.mkdir(parents=True,exist_ok=True)
        with lock.open("a+",encoding="utf-8") as stream:
            fcntl.flock(stream.fileno(),fcntl.LOCK_EX); previous,corrupted=self._previous(history)
            rec=self._build(s,previous.get("analysis_hash") if previous else None,corrupted); rec.update({"persisted":True,"latest_path":str(latest),"history_path":str(history)})
            tmp=latest.with_suffix(".tmp"); tmp.write_text(json.dumps(rec,sort_keys=True,indent=2),encoding="utf-8"); tmp.replace(latest)
            with history.open("a",encoding="utf-8") as h: h.write(json.dumps(rec,sort_keys=True)+"\n"); h.flush()
            fcntl.flock(stream.fileno(),fcntl.LOCK_UN); return rec
