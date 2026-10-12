from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"


class ComparativeSimilarityEngine:
    primitive = "comparative_similarity_engine"
    step_id = "AU4"
    public_schema_version = "1.0.0"

    DEFAULT_DIMENSIONS = ["RF", "OMEGA", "PI", "MEI", "CRI", "GOV", "LONG", "AUDIT"]
    DEFAULT_WEIGHTS = {"RF":0.20,"OMEGA":0.15,"PI":0.15,"MEI":0.15,"CRI":0.15,"GOV":0.08,"LONG":0.07,"AUDIT":0.05}
    DEFAULT_PROFILES = [
        {"architecture_id":"oce_rf_star","architecture_type":"open_cognitive_ecology","comparison_ready":True,"profile_confidence":0.90,"rf_profile_vector":{"RF":1.0,"OMEGA":0.96,"PI":0.94,"MEI":0.93,"CRI":0.91,"GOV":1.0,"LONG":0.92,"AUDIT":1.0}},
        {"architecture_id":"generic_llm_baseline","architecture_type":"llm","comparison_ready":True,"profile_confidence":0.45,"rf_profile_vector":{"RF":0.55,"OMEGA":0.40,"PI":0.68,"MEI":0.20,"CRI":0.35,"GOV":0.45,"LONG":0.30,"AUDIT":0.55}},
        {"architecture_id":"agentic_system_baseline","architecture_type":"agentic_system","comparison_ready":True,"profile_confidence":0.45,"rf_profile_vector":{"RF":0.62,"OMEGA":0.52,"PI":0.70,"MEI":0.28,"CRI":0.42,"GOV":0.55,"LONG":0.45,"AUDIT":0.60}},
    ]

    @staticmethod
    def _clamp01(value):
        if value is None:
            return None
        if isinstance(value, bool):
            return 1.0 if value else 0.0
        if isinstance(value, (int, float)):
            return round(max(0.0, min(1.0, float(value))), 6)
        return None

    def _profiles(self, inputs):
        raw = inputs.get("architecture_profiles")
        if not isinstance(raw, list):
            raw = inputs.get("profiles")
        if not isinstance(raw, list):
            return list(self.DEFAULT_PROFILES)
        return [item for item in raw if isinstance(item, dict)]

    def _dimensions(self, inputs, profiles):
        raw = inputs.get("comparison_dimensions")
        dims = [x for x in raw if isinstance(x, str)] if isinstance(raw, list) else []
        if dims:
            return dims
        observed = set()
        for p in profiles:
            v = p.get("rf_profile_vector")
            if isinstance(v, dict):
                observed.update(map(str, v.keys()))
        inferred = [d for d in self.DEFAULT_DIMENSIONS if d in observed]
        return inferred or list(self.DEFAULT_DIMENSIONS)

    def _weights(self, inputs, dimensions):
        raw = inputs.get("dimension_weights")
        vals = {}
        for d in dimensions:
            x = raw.get(d) if isinstance(raw, dict) else self.DEFAULT_WEIGHTS.get(d, 1.0)
            vals[d] = float(x) if isinstance(x, (int, float)) and x > 0 else 1.0
        total = sum(vals.values()) or 1.0
        return {d: round(v / total, 8) for d, v in vals.items()}

    def _vector(self, profile):
        raw = profile.get("rf_profile_vector")
        if not isinstance(raw, dict):
            raw = profile.get("metrics")
        raw = raw if isinstance(raw, dict) else {}
        return {str(k): self._clamp01(v) for k, v in raw.items()}

    def _pair(self, left_profile, right_profile, dimensions, weights):
        left_id = str(left_profile.get("architecture_id") or "unknown_left")
        right_id = str(right_profile.get("architecture_id") or "unknown_right")
        left = self._vector(left_profile)
        right = self._vector(right_profile)
        per_dim = {}
        comparable = []
        weighted_sum = 0.0
        used_weight = 0.0
        for d in dimensions:
            lv, rv = left.get(d), right.get(d)
            if isinstance(lv, float) and isinstance(rv, float):
                sim = round(1.0 - abs(lv - rv), 6)
                per_dim[d] = sim
                comparable.append(d)
                w = weights.get(d, 0.0)
                weighted_sum += sim * w
                used_weight += w
            else:
                per_dim[d] = None
        absolute = round(weighted_sum / used_weight, 6) if used_weight else 0.0
        coverage = round(len(comparable) / float(len(dimensions) or 1), 6)
        if comparable:
            lvals = [float(left[d]) for d in comparable]
            rvals = [float(right[d]) for d in comparable]
            dot = sum(a*b for a,b in zip(lvals,rvals))
            ln = math.sqrt(sum(v*v for v in lvals))
            rn = math.sqrt(sum(v*v for v in rvals))
            cosine = round(max(0.0, min(1.0, dot/(ln*rn))), 6) if ln and rn else 0.0
        else:
            cosine = 0.0
        structural = round((absolute + cosine) / 2.0, 6)
        confs = [x for x in [self._clamp01(left_profile.get("profile_confidence")), self._clamp01(right_profile.get("profile_confidence"))] if isinstance(x,float)]
        evidence_conf = round(sum(confs)/len(confs),6) if confs else 0.0
        return {
            "pair_id": f"{left_id}::{right_id}",
            "left_architecture_id": left_id,
            "right_architecture_id": right_id,
            "dimension_similarities": per_dim,
            "comparable_dimensions": comparable,
            "comparable_dimension_count": len(comparable),
            "comparison_coverage": coverage,
            "weighted_absolute_similarity": absolute,
            "cosine_similarity": cosine,
            "structural_similarity": structural,
            "evidence_confidence": evidence_conf,
            "confidence_adjusted_similarity": round(structural*coverage*evidence_conf,6),
            "comparison_valid": bool(comparable and coverage > 0.0),
        }

    def step(self, inputs=None, persist=False):
        inputs = inputs if isinstance(inputs, dict) else {}
        profiles = self._profiles(inputs)
        dimensions = self._dimensions(inputs, profiles)
        weights = self._weights(inputs, dimensions)
        ready_profiles = [p for p in profiles if p.get("comparison_ready", True) and p.get("architecture_id")]
        matrix = {str(p["architecture_id"]): {} for p in ready_profiles}
        pairwise = []
        for i, left in enumerate(ready_profiles):
            lid = str(left["architecture_id"])
            matrix[lid][lid] = 1.0
            for right in ready_profiles[i+1:]:
                rid = str(right["architecture_id"])
                rec = self._pair(left, right, dimensions, weights)
                pairwise.append(rec)
                score = float(rec["structural_similarity"])
                matrix[lid][rid] = score
                matrix[rid][lid] = score
        valid = [r for r in pairwise if r["comparison_valid"]]
        scores = [float(r["structural_similarity"]) for r in valid]
        core = {"RF","OMEGA","PI","MEI","CRI"}.issubset(set(dimensions))
        symmetric = all(abs(matrix[a].get(b,-1.0)-matrix[b].get(a,-2.0)) < 1e-9 for a in matrix for b in matrix if a != b)
        ready = bool(core and len(ready_profiles) >= 2 and len(valid) >= 1 and symmetric)
        result = {
            "primitive": self.primitive,
            "step": self.step_id,
            "public_schema_version": self.public_schema_version,
            "status": "COMPARATIVE_SIMILARITY_ENGINE_READY" if ready else "COMPARATIVE_SIMILARITY_ENGINE_INCOMPLETE",
            "comparative_similarity_status": "COMPARATIVE_SIMILARITY_ENGINE_READY" if ready else "COMPARATIVE_SIMILARITY_ENGINE_INCOMPLETE",
            "comparative_similarity_engine_ready": ready,
            "similarity_matrix_ready": ready,
            "architecture_profile_count": len(profiles),
            "comparison_ready_profile_count": len(ready_profiles),
            "pairwise_comparison_count": len(pairwise),
            "valid_pairwise_comparison_count": len(valid),
            "comparison_dimensions": dimensions,
            "comparison_dimension_count": len(dimensions),
            "core_dimensions_present": core,
            "dimension_weights": weights,
            "pairwise_similarities": pairwise,
            "similarity_matrix": matrix,
            "mean_structural_similarity": round(sum(scores)/len(scores),6) if scores else 0.0,
            "most_similar_pair": max(valid, key=lambda x:x["structural_similarity"]) if valid else None,
            "least_similar_pair": min(valid, key=lambda x:x["structural_similarity"]) if valid else None,
            "similarity_metric": {"primary":"mean_weighted_absolute_and_cosine_similarity","range":[0.0,1.0],"identity":1.0,"symmetry_required":True},
            "normalization_policy": {"input_range":[0.0,1.0],"out_of_range_values":"clamp","weights_normalized_to_one":True},
            "validation_policy": {"requires_two_ready_profiles":True,"requires_core_dimensions":True,"requires_symmetric_matrix":True,"requires_public_invariants_only":True},
            "auditability_policy": {"record_pairwise_dimensions":True,"record_coverage":True,"record_profile_confidence":True,"record_dimension_weights":True},
            "epistemic_guards": {"functional_conclusion_only":True,"phenomenology_undetermined":True,"similarity_is_not_identity":True,"similarity_is_not_proof_of_consciousness":True},
            "allowed_claims": ["functional_profile_similarity_computed","pairwise_similarity_matrix_constructed"],
            "blocked_claims": ["consciousness_proven","qualia_proven","subjectivity_proven","phenomenology_proven","architectures_ontologically_identical"],
            "target_axis_status": "COMPARATIVE_RF_SCIENCE_IN_PROGRESS",
            "downstream_modules": ["consciousness_distance_metric","clustering_engine","taxonomy_builder","comparative_dashboard","comparative_history","comparative_science_certifier"],
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "inputs_observed": sorted(inputs.keys()),
            "persist_requested": bool(persist),
            "persisted": False,
            "output_path": None,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        }
        if persist:
            out_dir = ROOT / "comparative_science" / "similarity"
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / "latest_comparative_similarity.json"
            out_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
            result["persisted"] = True
            result["output_path"] = str(out_path)
        return result


if __name__ == "__main__":
    print(ComparativeSimilarityEngine().step(persist=True)["comparative_similarity_status"])
