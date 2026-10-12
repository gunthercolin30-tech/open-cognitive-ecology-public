"""AV4 — bifurcation_detector.

Detect functional developmental regime changes from ordered multivariate
trajectories. Distinguishes fluctuation, progressive transition, structural break,
sustained bifurcation, and multiple bifurcations. All conclusions are functional.
"""
from __future__ import annotations
import hashlib, json, math
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

ROOT = Path.home() / "open-cognitive-ecology"

class BifurcationDetector:
    primitive = "BIFURCATION_DETECTOR"
    step_id = "AV4"
    public_schema_version = "1.0"
    output_dir = ROOT / "developmental_science" / "AV4_bifurcation_detector"
    DEFAULTS = {
        "minimum_observations": 5,
        "minimum_window": 2,
        "minimum_data_quality": 0.50,
        "fluctuation_threshold": 0.18,
        "transition_threshold": 0.24,
        "structural_break_threshold": 0.42,
        "bifurcation_threshold": 0.34,
        "persistence_threshold": 0.72,
        "abruptness_threshold": 0.55,
        "multiple_separation": 2,
        "return_threshold": 0.12,
    }

    def _clip(self, value: Any, default: float = 0.0) -> float:
        try: number = float(value)
        except (TypeError, ValueError): number = default
        if not math.isfinite(number): number = default
        return max(0.0, min(1.0, number))

    def _mean(self, values: Iterable[float], default: float = 0.0) -> float:
        clean = [float(v) for v in values if isinstance(v, (int, float)) and math.isfinite(float(v))]
        return sum(clean) / len(clean) if clean else default

    def _stable_hash(self, value: Any) -> str:
        payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def _normalize_observation(self, raw_value: Any, index: int) -> Dict[str, Any]:
        raw = dict(raw_value) if isinstance(raw_value, dict) else {}
        vector = raw.get("state_vector") or raw.get("metrics") or raw.get("dimensions") or raw.get("profile") or {}
        if not isinstance(vector, dict): vector = {}
        clean = {str(k): self._clip(v) for k, v in vector.items() if isinstance(v, (int, float)) and not isinstance(v, bool)}
        return {"index": index, "timestamp_utc": raw.get("timestamp_utc") or raw.get("timestamp") or f"index:{index:06d}", "state_vector": clean, "data_quality": self._clip(raw.get("data_quality", raw.get("quality", 1.0))), "source": str(raw.get("source", "unspecified")), "synthetic": bool(raw.get("synthetic", False))}

    def _collect(self, inputs: Dict[str, Any]) -> List[Dict[str, Any]]:
        values = inputs.get("observations")
        if not isinstance(values, list): values = inputs.get("longitudinal_records")
        if not isinstance(values, list): values = inputs.get("history")
        if not isinstance(values, list): values = []
        return [self._normalize_observation(v, i) for i, v in enumerate(values)]

    def _chronology_valid(self, observations: List[Dict[str, Any]]) -> bool:
        timestamps = [str(o["timestamp_utc"]) for o in observations]
        return timestamps == sorted(timestamps) and len(timestamps) == len(set(timestamps))

    def _dimensions(self, observations: List[Dict[str, Any]]) -> List[str]:
        names = set()
        for obs in observations: names.update(obs["state_vector"].keys())
        return sorted(names)

    def _centroid(self, window: List[Dict[str, Any]], dimensions: List[str]) -> Dict[str, float]:
        return {d: round(self._mean([o["state_vector"].get(d, 0.0) for o in window]), 6) for d in dimensions}

    def _distance(self, left: Dict[str, float], right: Dict[str, float], dimensions: List[str]) -> float:
        if not dimensions: return 0.0
        return self._clip(math.sqrt(sum((right.get(d,0.0)-left.get(d,0.0))**2 for d in dimensions)/len(dimensions)))

    def _within_stability(self, window: List[Dict[str, Any]], centroid: Dict[str, float], dimensions: List[str]) -> float:
        if not window or not dimensions: return 0.0
        deviations = [math.sqrt(sum((o["state_vector"].get(d,0.0)-centroid[d])**2 for d in dimensions)/len(dimensions)) for o in window]
        return self._clip(1.0-self._mean(deviations))

    def _step_distance(self, a: Dict[str, Any], b: Dict[str, Any], dimensions: List[str]) -> float:
        return self._distance(a["state_vector"], b["state_vector"], dimensions)

    def _local_candidate(self, observations: List[Dict[str, Any]], split: int, dimensions: List[str], config: Dict[str, Any], prior_centroids: List[Dict[str,float]]) -> Dict[str, Any]:
        w = int(config["minimum_window"])
        pre = observations[split-w:split]
        post = observations[split:split+w]
        pre_c, post_c = self._centroid(pre, dimensions), self._centroid(post, dimensions)
        distance = self._distance(pre_c, post_c, dimensions)
        pre_stab, post_stab = self._within_stability(pre, pre_c, dimensions), self._within_stability(post, post_c, dimensions)
        local_jump = self._step_distance(observations[split-1], observations[split], dimensions)
        neighborhood_steps = [self._step_distance(observations[i-1], observations[i], dimensions) for i in range(max(1,split-w+1), min(len(observations),split+w)) if i != split]
        background = self._mean(neighborhood_steps, 0.0)
        abruptness = self._clip(local_jump/max(0.10, local_jump+background))
        persistence = self._clip((pre_stab+post_stab)/2.0)
        affected = [d for d in dimensions if abs(post_c[d]-pre_c[d]) >= max(0.10, distance*0.50)]
        structural = self._clip(0.50*distance+0.25*abruptness+0.25*persistence)
        score = self._clip(0.50*distance+0.25*persistence+0.15*abruptness+0.10*(len(affected)/max(1,len(dimensions))))
        return_to_prior = any(self._distance(post_c, c, dimensions) <= float(config["return_threshold"]) for c in prior_centroids)
        return {"split_index": split, "timestamp_utc": observations[split]["timestamp_utc"], "pre_regime": pre_c, "post_regime": post_c, "regime_distance": round(distance,6), "pre_stability": round(pre_stab,6), "post_stability": round(post_stab,6), "abruptness_score": round(abruptness,6), "persistence_score": round(persistence,6), "structural_break_score": round(structural,6), "bifurcation_score": round(score,6), "affected_dimensions": affected, "return_to_prior_regime": return_to_prior, "pre_window": [split-w, split-1], "post_window": [split, split+w-1]}

    def _trend_score(self, observations: List[Dict[str, Any]], dimensions: List[str]) -> float:
        if len(observations)<3 or not dimensions: return 0.0
        scores=[]
        for d in dimensions:
            vals=[o["state_vector"].get(d,0.0) for o in observations]; diffs=[vals[i]-vals[i-1] for i in range(1,len(vals))]
            if diffs:
                pos=sum(1 for x in diffs if x>0.01); neg=sum(1 for x in diffs if x<-0.01); scores.append(max(pos,neg)/len(diffs))
        return self._clip(self._mean(scores))

    def _transient_excursion(self, observations: List[Dict[str, Any]], dimensions: List[str], config: Dict[str, Any]) -> bool:
        w=int(config["minimum_window"])
        if len(observations)<2*w+1: return False
        initial=self._centroid(observations[:w], dimensions); final=self._centroid(observations[-w:], dimensions)
        return_distance=self._distance(initial, final, dimensions)
        max_step=max((self._step_distance(observations[i-1],observations[i],dimensions) for i in range(1,len(observations))), default=0.0)
        return return_distance <= float(config["return_threshold"]) and max_step >= float(config["fluctuation_threshold"])

    def step(self, inputs: Optional[Dict[str, Any]]=None, persist: bool=False) -> Dict[str, Any]:
        inputs=dict(inputs) if isinstance(inputs,dict) else {}; config=dict(self.DEFAULTS)
        if isinstance(inputs.get("config"),dict):
            for k,v in inputs["config"].items():
                if k in config and isinstance(v,(int,float)): config[k]=v
        obs=self._collect(inputs); dims=self._dimensions(obs); quality=self._mean([o["data_quality"] for o in obs]) if obs else 0.0
        chronology=self._chronology_valid(obs) if obs else True; minimum=int(config["minimum_observations"]); w=int(config["minimum_window"])
        analyzable=len(obs)>=max(2*w+1, minimum) and chronology and bool(dims) and quality>=float(config["minimum_data_quality"])
        candidates=[]; prior_centroids=[]
        if analyzable:
            for split in range(w, len(obs)-w+1):
                c=self._local_candidate(obs,split,dims,config,prior_centroids); candidates.append(c); prior_centroids.append(c["pre_regime"])
        accepted=[]
        for c in sorted(candidates,key=lambda x:x["split_index"]):
            qualifies=(c["regime_distance"]>=float(config["bifurcation_threshold"]) and c["persistence_score"]>=float(config["persistence_threshold"]) and c["structural_break_score"]>=float(config["structural_break_threshold"]))
            if qualifies and all(abs(c["split_index"]-o["split_index"])>=int(config["multiple_separation"]) for o in accepted): accepted.append(c)
        best=max(candidates,key=lambda x:x["bifurcation_score"],default=None)
        transient=self._transient_excursion(obs,dims,config) if chronology and dims and quality>=float(config["minimum_data_quality"]) else False
        trend=self._trend_score(obs,dims)
        status="FUNCTIONAL_BIFURCATION_UNDETERMINED"; kind="undetermined"; detected=False
        if not chronology or not dims or quality<float(config["minimum_data_quality"]) or len(obs)<max(2*w+1,minimum):
            status="FUNCTIONAL_BIFURCATION_UNDETERMINED"
        elif len(accepted)>=2:
            status="FUNCTIONAL_MULTIPLE_BIFURCATIONS_DETECTED"; kind="multiple_bifurcation"; detected=True; best=accepted[0]
        elif len(accepted)==1:
            status="FUNCTIONAL_BIFURCATION_DETECTED"; kind="sustained_regime_bifurcation"; detected=True; best=accepted[0]
        elif transient:
            status="FUNCTIONAL_FLUCTUATION_DETECTED"; kind="transient_fluctuation"
        elif best and best["regime_distance"]>=float(config["transition_threshold"]) and best["structural_break_score"]>=float(config["structural_break_threshold"]) and best["abruptness_score"]>=float(config["abruptness_threshold"]):
            status="FUNCTIONAL_STRUCTURAL_BREAK_DETECTED"; kind="structural_break"
        elif best and best["regime_distance"]>=float(config["transition_threshold"]) and trend>=0.65:
            status="FUNCTIONAL_PROGRESSIVE_TRANSITION_DETECTED"; kind="progressive_transition"
        elif best and best["regime_distance"]>=float(config["fluctuation_threshold"]):
            status="FUNCTIONAL_FLUCTUATION_DETECTED"; kind="transient_fluctuation"
        else:
            status="NO_DEVELOPMENTAL_TRANSITION"; kind="none"
        selected=best or {"split_index":None,"timestamp_utc":None,"pre_regime":{},"post_regime":{},"regime_distance":0.0,"pre_stability":0.0,"post_stability":0.0,"abruptness_score":0.0,"persistence_score":0.0,"structural_break_score":0.0,"bifurcation_score":0.0,"affected_dimensions":[],"return_to_prior_regime":False}
        payload={"observations":obs,"config":config,"status":status,"selected":selected,"accepted":accepted}
        result={"primitive":self.primitive,"step":self.step_id,"public_schema_version":self.public_schema_version,"bifurcation_detected":detected,"bifurcation_status":status,"bifurcation_type":kind,"pre_regime":selected["pre_regime"],"post_regime":selected["post_regime"],"structural_break_score":float(selected["structural_break_score"]),"bifurcation_score":float(selected["bifurcation_score"]),"regime_distance":float(selected["regime_distance"]),"persistence_score":float(selected["persistence_score"]),"abruptness_score":float(selected["abruptness_score"]),"transition_timestamp":selected["timestamp_utc"],"transition_index":selected["split_index"],"affected_dimensions":list(selected["affected_dimensions"]),"return_to_prior_regime":bool(selected.get("return_to_prior_regime",False)),"multiple_bifurcations_detected":len(accepted)>=2,"bifurcation_count":len(accepted),"bifurcation_events":accepted,"trend_score":round(trend,6),"observation_count":len(obs),"dimension_count":len(dims),"data_quality_score":round(quality,6),"chronology_valid":chronology,"condition_results":{"minimum_observations_met":len(obs)>=max(2*w+1,minimum),"chronology_valid":chronology,"data_quality_sufficient":quality>=float(config["minimum_data_quality"]),"state_vector_available":bool(dims),"persistent_new_regime":float(selected["persistence_score"])>=float(config["persistence_threshold"])},"missing_conditions":[],"audit_trace":{"candidate_count":len(candidates),"accepted_bifurcation_count":len(accepted),"classification_basis":"adjacent_local_regime_segmentation","transient_excursion_detected":transient},"bifurcation_hash":self._stable_hash(payload),"persist_requested":bool(persist),"persisted":False,"output_path":None,"consciousness_proven":False,"qualia_proven":False,"subjectivity_proven":False,"phenomenology_proven":False,"functional_conclusion_only":True,"phenomenology_undetermined":True}
        result["missing_conditions"]=[k for k,v in result["condition_results"].items() if not v]
        if persist:
            self.output_dir.mkdir(parents=True,exist_ok=True); path=self.output_dir/"latest_bifurcation_detection.json"; path.write_text(json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False),encoding="utf-8"); result["persisted"]=True; result["output_path"]=str(path)
        return result
