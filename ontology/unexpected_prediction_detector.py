
"""AT6 — unexpected_prediction_detector.

Classifies RF* predictions into expected, new, counter-intuitive and surprising
classes using theorem-derived predictions, discriminative analysis, measurable
signatures and falsification protocols. This module remains strictly functional
and predictive; it never asserts phenomenology, qualia or subjectivity.
"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional
ROOT = Path.home() / "open-cognitive-ecology"

def _now() -> str: return datetime.now(timezone.utc).isoformat().replace("+00:00","Z")
def _flt(x:Any,d:float=0.0)->float:
    try: v=float(x)
    except Exception: return d
    return max(0.0,min(1.0,v))
def _lst(x:Any)->List[Any]:
    if x is None: return []
    if isinstance(x,list): return x
    if isinstance(x,tuple): return list(x)
    if isinstance(x,dict): return [x]
    return [x]
def _slug(x:Any)->str:
    s=str(x or "unknown").lower(); out=[]
    for c in s:
        if c.isalnum(): out.append(c)
        elif out and out[-1] != "_": out.append("_")
    return "".join(out).strip("_") or "unknown"

class UnexpectedPredictionDetector:
    primitive="UNEXPECTED_PREDICTION_DETECTOR"
    step_name="AT6"
    public_schema_version="1.0.0"
    status="UNEXPECTED_PREDICTIONS_DETECTED"
    epistemic_guards={
        "consciousness_proven":False,"qualia_proven":False,"subjectivity_proven":False,"phenomenology_proven":False,
        "phenomenology_undetermined":True,"functional_conclusion_only":True,
        "allowed_scope":["prediction_novelty_detection","functional_surprise_scoring","experimental_priority_ranking"],
        "blocked_scope":["phenomenal_consciousness_proof","qualia_proof","subjectivity_proof","ontological_final_closure"],
    }
    expected_categories={"structural","dynamic","topological","spectral","developmental","collective"}
    conventional_keywords={"workspace","broadcast","higher_order","integrated_information","prediction_error","functional_role","access","attention"}
    rf_keywords={"reference","frame","constraint","closure","non_closure","topological","spectral","civilizational","governance","continuity","reflexive"}

    def _load_previous(self)->Dict[str,Any]:
        out={}
        for key, mod, cls in [
            ("at5_result","ontology.falsification_protocol_generator","FalsificationProtocolGenerator"),
            ("at4_result","ontology.measurable_signature_builder","MeasurableSignatureBuilder"),
            ("at3_result","ontology.discriminative_prediction_engine","DiscriminativePredictionEngine"),
            ("at2_result","ontology.theorem_prediction_generator","TheoremPredictionGenerator"),
        ]:
            try:
                module=__import__(mod, fromlist=[cls]); out[key]=getattr(module,cls)().step(inputs={}, persist=False)
            except Exception:
                pass
        return out

    def _records(self, inputs:Mapping[str,Any])->List[Dict[str,Any]]:
        ctx=dict(inputs or {})
        if not any(k in ctx for k in ["falsification_protocols","measurable_signatures","discriminative_predictions","theorem_predictions"]):
            ctx.update(self._load_previous())
        candidates=[]
        for key in ["falsification_protocols","protocols"]:
            candidates += _lst(ctx.get(key))
        for parent in ["at5_result","falsification_protocol_generator"]:
            if isinstance(ctx.get(parent),Mapping): candidates += _lst(ctx[parent].get("falsification_protocols"))
        for parent, child in [("at4_result","measurable_signatures"),("at3_result","discriminative_predictions"),("at2_result","theorem_predictions")]:
            if isinstance(ctx.get(parent),Mapping): candidates += _lst(ctx[parent].get(child))
        for key in ["measurable_signatures","discriminative_predictions","theorem_predictions","predictions"]:
            candidates += _lst(ctx.get(key))
        records=[]
        seen=set()
        for i,item in enumerate(candidates,1):
            if not isinstance(item,Mapping): continue
            pid=str(item.get("prediction_id") or item.get("id") or item.get("protocol_id") or item.get("signature_id") or f"prediction_{i}")
            if pid in seen: continue
            seen.add(pid)
            text=" ".join(str(item.get(k,"")) for k in ["prediction","claim","description","rf_prediction","theorem","category"])
            category=str(item.get("category") or item.get("prediction_category") or "uncategorized")
            records.append({
                "prediction_id":pid,"category":category,"prediction":text or f"RF* {category} prediction",
                "source_protocol_id":item.get("protocol_id"),"source_signature_id":item.get("signature_id"),
                "discriminative_power":_flt(item.get("discriminative_power") or item.get("rf_specificity") or item.get("protocol_scores",{}).get("discriminative_power"),0.55),
                "measurement_readiness":_flt(item.get("measurement_readiness") or item.get("protocol_scores",{}).get("measurement_readiness"),0.55),
                "falsifiability_score":_flt(item.get("falsifiability_score") or item.get("protocol_scores",{}).get("falsifiability_score"),0.55),
                "raw":dict(item),
            })
        if not records:
            for cat in ["topological","spectral","collective"]:
                records.append({"prediction_id":f"synthetic_{cat}","category":cat,"prediction":f"RF* yields a potentially surprising {cat} functional consequence.","source_protocol_id":None,"source_signature_id":None,"discriminative_power":0.6,"measurement_readiness":0.55,"falsifiability_score":0.6,"raw":{}})
        return records

    def _classify(self, r:Mapping[str,Any], idx:int)->Dict[str,Any]:
        text=str(r.get("prediction","")).lower(); cat=str(r.get("category") or "uncategorized")
        disc=_flt(r.get("discriminative_power"),0.55); meas=_flt(r.get("measurement_readiness"),0.55); fals=_flt(r.get("falsifiability_score"),0.55)
        rf_hits=sum(1 for k in self.rf_keywords if k in text or k in cat.lower())
        conv_hits=sum(1 for k in self.conventional_keywords if k in text)
        category_novelty = 0.15 if cat in self.expected_categories else 0.45
        novelty=round(max(0.0,min(1.0,0.25 + 0.25*disc + category_novelty + 0.05*rf_hits - 0.04*conv_hits)),3)
        counter=round(max(0.0,min(1.0,0.15 + 0.2*disc + (0.15 if "non" in text or "absence" in text or "closure" in text else 0.0) + (0.1 if cat in {"topological","spectral","collective"} else 0.0))),3)
        surprise=round(max(0.0,min(1.0,(novelty+counter+disc+fals)/4.0)),3)
        if surprise>=0.68: cls="surprising"
        elif counter>=0.52: cls="counter_intuitive"
        elif novelty>=0.55: cls="new"
        else: cls="expected"
        return {"unexpected_prediction_id":f"AT6-{idx:04d}-{_slug(r.get('prediction_id'))}","prediction_id":r.get("prediction_id"),"category":cat,"prediction":r.get("prediction"),"classification":cls,"novelty_score":novelty,"counter_intuitiveness_score":counter,"surprise_score":surprise,"rf_specificity_score":disc,"measurement_readiness":meas,"falsifiability_score":fals,"source_protocol_id":r.get("source_protocol_id"),"source_signature_id":r.get("source_signature_id"),"recommended_follow_up":"prioritize_for_protocolized_testing" if cls in {"surprising","counter_intuitive"} else "track_as_standard_prediction","claim_scope":"functional_prediction_only"}

    def _summary(self, items:List[Mapping[str,Any]])->Dict[str,Any]:
        counts={k:0 for k in ["expected","new","counter_intuitive","surprising"]}
        for it in items: counts[it.get("classification","expected")]=counts.get(it.get("classification","expected"),0)+1
        scores=[_flt(i.get("surprise_score"),0.0) for i in items]
        return {"unexpected_prediction_count":len(items),"classification_counts":counts,"mean_surprise_score":round(sum(scores)/len(scores),3) if scores else 0.0,"max_surprise_score":round(max(scores),3) if scores else 0.0,"priority_follow_up_count":sum(1 for i in items if i.get("recommended_follow_up")=="prioritize_for_protocolized_testing")}

    def step(self, inputs:Optional[Mapping[str,Any]]=None, persist:bool=False)->Dict[str,Any]:
        recs=self._records(dict(inputs or {})); det=[self._classify(r,i) for i,r in enumerate(recs,1)]
        cats=sorted({d["classification"] for d in det}); summary=self._summary(det)
        outpath=ROOT/"predictive_theory"/"unexpected"/"latest_unexpected_predictions.json"; persisted=False
        if persist:
            outpath.parent.mkdir(parents=True,exist_ok=True)
            outpath.write_text(json.dumps({"primitive":self.primitive,"step":self.step_name,"status":self.status,"unexpected_predictions":det,"summary":summary,"timestamp_utc":_now()},indent=2,sort_keys=True),encoding="utf-8"); persisted=True
        return {"primitive":self.primitive,"step":self.step_name,"public_schema_version":self.public_schema_version,"status":self.status,"prediction_count":len(recs),"unexpected_prediction_count":len(det),"unexpected_predictions":det,"classified_prediction_categories":cats,"unexpected_prediction_summary":summary,"detection_policy":{"novelty_scoring":True,"counter_intuitiveness_scoring":True,"surprise_priority_ranking":True,"functional_scope_only":True},"validation_policy":{"requires_AT5_protocol_follow_up":True,"surprising_predictions_are_not_proofs":True,"independent_replication_required":True},"epistemic_guards":dict(self.epistemic_guards),"functional_conclusion_only":True,"phenomenology_undetermined":True,"consciousness_proven":False,"qualia_proven":False,"subjectivity_proven":False,"phenomenology_proven":False,"persist_requested":bool(persist),"persisted":persisted,"output_path":str(outpath) if persist else None,"timestamp_utc":_now()}
__all__=["UnexpectedPredictionDetector"]
