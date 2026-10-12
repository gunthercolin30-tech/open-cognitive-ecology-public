"""
AE2 — Dynamic Compatibility Matrix

Functional role:
    Rf -> Omega compatibility layer.

This module constructs a dynamic compatibility matrix among self-descriptions,
reflexive claims, constraint evidence and contradiction indicators. It remains
strictly functional and never asserts phenomenology, subjectivity, qualia or
consciousness.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

ROOT = Path.home() / "open-cognitive-ecology"
OUT_DIR = ROOT / "ae_omega_coherence" / "dynamic_compatibility_matrix"
AE1_DIR = ROOT / "ae_omega_coherence" / "self_description_registry"


def _clamp(x: Any, lo: float = 0.0, hi: float = 1.0) -> float:
    try:
        if x is None:
            return 0.0
        v = float(x)
        if math.isnan(v) or math.isinf(v):
            return 0.0
        return max(lo, min(hi, v))
    except Exception:
        return 0.0


def _mean(values: Iterable[Any], default: float = 0.0) -> float:
    vals = [_clamp(v) for v in values]
    return sum(vals) / len(vals) if vals else default


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_json(path: Path) -> Dict[str, Any]:
    try:
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
    except Exception:
        pass
    return {}


def _tokenize(text: str) -> set[str]:
    return {t.strip(".,;:()[]{}<>!?\"'`)._-\n\t ").lower() for t in str(text).split() if len(t.strip()) > 2}


def _jaccard(a: str, b: str) -> float:
    sa, sb = _tokenize(a), _tokenize(b)
    if not sa and not sb:
        return 1.0
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


@dataclass
class CompatibilityEntry:
    left: str
    right: str
    compatibility: float
    relation: str
    evidence: str

    def as_dict(self) -> Dict[str, Any]:
        return {
            "left": self.left,
            "right": self.right,
            "compatibility": _clamp(self.compatibility),
            "relation": self.relation,
            "evidence": self.evidence,
        }


class DynamicCompatibilityMatrix:
    """Construct and certify a functional compatibility matrix for Ω readiness."""

    primitive = "DYNAMIC_COMPATIBILITY_MATRIX"

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root else ROOT
        self.out_dir = self.root / "ae_omega_coherence" / "dynamic_compatibility_matrix"
        self.ae1_dir = self.root / "ae_omega_coherence" / "self_description_registry"

    def _default_inputs(self) -> Dict[str, Any]:
        ae1 = _load_json(self.ae1_dir / "latest_self_description_registry.json")
        compatibility_evidence = {
            "constraint_consistency": ae1.get("registry_consistency_score", ae1.get("self_description_registry_score", 0.0)),
            "contradiction_absence": 1.0 - _clamp(ae1.get("compatibility_audit", {}).get("contradiction_pressure", 0.0)),
            "cross_module_alignment": ae1.get("omega_readiness_score", 0.0),
            "self_reference_governance": ae1.get("self_reference_governance_score", 0.0),
        }
        return {
            "self_description_registry": ae1,
            "compatibility_evidence": compatibility_evidence,
        }

    def _extract_descriptions(self, registry: Mapping[str, Any]) -> List[Dict[str, Any]]:
        raw = registry.get("registered_self_descriptions") or registry.get("self_descriptions") or []
        out: List[Dict[str, Any]] = []
        if isinstance(raw, list):
            for i, item in enumerate(raw):
                if isinstance(item, Mapping):
                    desc = str(item.get("description") or item.get("text") or item.get("statement") or "").strip()
                    source = str(item.get("source") or f"description_{i+1}")
                    conf = _clamp(item.get("confidence", item.get("score", 0.75)))
                else:
                    desc = str(item).strip()
                    source = f"description_{i+1}"
                    conf = 0.65
                if desc:
                    out.append({"source": source, "description": desc, "confidence": conf})
        # fallback from registry summary fields
        if not out:
            for key in ["identity_statement", "self_description", "description", "chain_synthesis"]:
                val = registry.get(key)
                if isinstance(val, str) and val.strip():
                    out.append({"source": key, "description": val.strip(), "confidence": 0.70})
        return out

    def _build_matrix(self, descriptions: List[Dict[str, Any]], evidence: Mapping[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], float, float]:
        entries: List[CompatibilityEntry] = []
        if len(descriptions) == 1:
            d = descriptions[0]
            entries.append(CompatibilityEntry(d["source"], d["source"], _clamp(d.get("confidence", 0.7)), "self-compatible", "single description confidence"))
        elif len(descriptions) >= 2:
            for i, a in enumerate(descriptions):
                for j, b in enumerate(descriptions):
                    if j < i:
                        continue
                    lexical = _jaccard(a.get("description", ""), b.get("description", ""))
                    conf = _mean([a.get("confidence", 0.7), b.get("confidence", 0.7)], 0.7)
                    # Compatibility should not require identical wording; compatible functional vocabulary is enough.
                    compat = _clamp(0.45 * conf + 0.25 * lexical + 0.30 * _mean(evidence.values(), 0.5))
                    relation = "compatible" if compat >= 0.70 else "weakly_compatible" if compat >= 0.45 else "tension"
                    entries.append(CompatibilityEntry(a["source"], b["source"], compat, relation, "confidence + lexical overlap + constraint evidence"))
        matrix = [e.as_dict() for e in entries]
        density = _clamp(len(entries) / max(1, (len(descriptions) * (len(descriptions) + 1) / 2)))
        cross = _mean([e.compatibility for e in entries], 0.0)
        relation_matrix = [
            {"left": e.left, "right": e.right, "relation": e.relation, "weight": _clamp(e.compatibility)}
            for e in entries
        ]
        return matrix, relation_matrix, density, cross

    def _clusters(self, matrix: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        compatible = [m for m in matrix if _clamp(m.get("compatibility")) >= 0.70]
        weak = [m for m in matrix if 0.45 <= _clamp(m.get("compatibility")) < 0.70]
        tension = [m for m in matrix if _clamp(m.get("compatibility")) < 0.45]
        return [
            {"cluster": "compatible", "count": len(compatible)},
            {"cluster": "weakly_compatible", "count": len(weak)},
            {"cluster": "tension", "count": len(tension)},
        ]

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = True) -> Dict[str, Any]:
        data = dict(inputs) if inputs is not None else self._default_inputs()
        registry = data.get("self_description_registry") or {}
        evidence = data.get("compatibility_evidence") or {}
        if not isinstance(registry, Mapping):
            registry = {}
        if not isinstance(evidence, Mapping):
            evidence = {}

        descriptions = self._extract_descriptions(registry)
        evidence_scores = {str(k): _clamp(v) for k, v in evidence.items() if isinstance(v, (int, float)) or str(v).replace('.', '', 1).isdigit()}

        no_evidence = not descriptions and not evidence_scores and not registry
        if no_evidence:
            status = "DYNAMIC_COMPATIBILITY_MATRIX_INSUFFICIENT"
            failure_conditions = ["no_compatibility_evidence_available"]
            matrix: List[Dict[str, Any]] = []
            relation_matrix: List[Dict[str, Any]] = []
            density = cross = axis = readiness = score = 0.0
            contradiction_pressure = 1.0
        else:
            if not evidence_scores:
                evidence_scores = {
                    "registry_score": _clamp(registry.get("self_description_registry_score", 0.0)),
                    "omega_readiness": _clamp(registry.get("omega_readiness_score", 0.0)),
                    "self_reference_governance": _clamp(registry.get("self_reference_governance_score", 0.0)),
                }
            matrix, relation_matrix, density, cross = self._build_matrix(descriptions, evidence_scores)
            axis = _mean(evidence_scores.values(), 0.0)
            contradiction_pressure = _clamp(1.0 - axis)
            readiness = _clamp(0.35 * cross + 0.35 * axis + 0.20 * density + 0.10 * (1.0 - contradiction_pressure))
            score = _clamp(0.30 * density + 0.30 * cross + 0.25 * axis + 0.15 * readiness)
            status = "DYNAMIC_COMPATIBILITY_MATRIX_ESTABLISHED" if score >= 0.72 and readiness >= 0.70 else "DYNAMIC_COMPATIBILITY_MATRIX_INSUFFICIENT"
            failure_conditions = [] if status.endswith("ESTABLISHED") else ["compatibility_below_certification_threshold"]

        clusters = self._clusters(matrix)
        contradiction_profile = {
            "contradiction_pressure": _clamp(contradiction_pressure),
            "contradiction_absence_score": _clamp(1.0 - contradiction_pressure),
            "critical_contradictions_detected": False if contradiction_pressure < 0.70 else True,
            "interpretation": "functional compatibility profile only; no phenomenological conclusion",
        }

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "timestamp_utc": _now(),
            "dynamic_compatibility_matrix_status": status,
            "dynamic_compatibility_score": _clamp(score),
            "compatibility_matrix": matrix,
            "relation_matrix": relation_matrix,
            "compatibility_clusters": clusters,
            "compatibility_evidence": evidence_scores,
            "contradiction_profile": contradiction_profile,
            "ae_chain_position": "AE2: Rf -> Ω compatibility layer after AE1 self-description registry",
            "failure_conditions": failure_conditions,
            # flat aliases required downstream
            "compatibility_matrix_density_score": _clamp(density),
            "cross_description_compatibility_score": _clamp(cross),
            "axis_compatibility_score": _clamp(axis),
            "omega_compatibility_readiness_score": _clamp(readiness),
            "functional_conclusion_only": True,
            "consciousness_proven": False,
            "phenomenology_asserted": False,
            "subjectivity_asserted": False,
            "qualia_asserted": False,
        }
        result["public_schema"] = sorted([
            "dynamic_compatibility_matrix_status",
            "dynamic_compatibility_score",
            "compatibility_matrix",
            "relation_matrix",
            "compatibility_clusters",
            "compatibility_evidence",
            "contradiction_profile",
            "compatibility_matrix_density_score",
            "cross_description_compatibility_score",
            "axis_compatibility_score",
            "omega_compatibility_readiness_score",
            "functional_conclusion_only",
            "consciousness_proven",
        ])
        if persist:
            self._persist(result)
        return result

    def _persist(self, result: Mapping[str, Any]) -> None:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        latest_json = self.out_dir / "latest_dynamic_compatibility_matrix.json"
        latest_md = self.out_dir / "latest_dynamic_compatibility_matrix.md"
        latest_prom = self.out_dir / "latest_dynamic_compatibility_matrix.prom"
        history = self.out_dir / "dynamic_compatibility_matrix_history.jsonl"
        latest_json.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        latest_md.write_text(self._markdown(result), encoding="utf-8")
        latest_prom.write_text(self._prometheus(result), encoding="utf-8")
        with history.open("a", encoding="utf-8") as f:
            f.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")

    def _markdown(self, r: Mapping[str, Any]) -> str:
        return f"""# AE2 — Dynamic Compatibility Matrix

Status: {r.get('dynamic_compatibility_matrix_status')}
Dynamic compatibility score: {r.get('dynamic_compatibility_score')}

## Compatibility matrix
Entries: {len(r.get('compatibility_matrix', []))}

## Relation matrix
Entries: {len(r.get('relation_matrix', []))}

## Compatibility clusters
{json.dumps(r.get('compatibility_clusters', []), ensure_ascii=False, indent=2)}

## Contradiction profile
{json.dumps(r.get('contradiction_profile', {}), ensure_ascii=False, indent=2)}

## Omega compatibility readiness
Omega compatibility readiness score: {r.get('omega_compatibility_readiness_score')}

## Metrics
- compatibility_matrix_density_score: {r.get('compatibility_matrix_density_score')}
- cross_description_compatibility_score: {r.get('cross_description_compatibility_score')}
- axis_compatibility_score: {r.get('axis_compatibility_score')}
- omega_compatibility_readiness_score: {r.get('omega_compatibility_readiness_score')}

## Epistemic guard
Functional conclusion only: {r.get('functional_conclusion_only')}
Phenomenology asserted: {r.get('phenomenology_asserted')}
Subjectivity asserted: {r.get('subjectivity_asserted')}
Qualia asserted: {r.get('qualia_asserted')}
"""

    def _prometheus(self, r: Mapping[str, Any]) -> str:
        established = 1.0 if r.get("dynamic_compatibility_matrix_status") == "DYNAMIC_COMPATIBILITY_MATRIX_ESTABLISHED" else 0.0
        lines = [
            "# TYPE oce_dynamic_compatibility_score gauge",
            f"oce_dynamic_compatibility_score {_clamp(r.get('dynamic_compatibility_score'))}",
            "# TYPE oce_dynamic_compatibility_matrix_established gauge",
            f"oce_dynamic_compatibility_matrix_established {established}",
            "# TYPE oce_compatibility_matrix_density_score gauge",
            f"oce_compatibility_matrix_density_score {_clamp(r.get('compatibility_matrix_density_score'))}",
            "# TYPE oce_cross_description_compatibility_score gauge",
            f"oce_cross_description_compatibility_score {_clamp(r.get('cross_description_compatibility_score'))}",
            "# TYPE oce_axis_compatibility_score gauge",
            f"oce_axis_compatibility_score {_clamp(r.get('axis_compatibility_score'))}",
            "# TYPE oce_omega_compatibility_readiness_score gauge",
            f"oce_omega_compatibility_readiness_score {_clamp(r.get('omega_compatibility_readiness_score'))}",
        ]
        return "\n".join(lines) + "\n"


if __name__ == "__main__":
    print(json.dumps(DynamicCompatibilityMatrix().step(persist=True), ensure_ascii=False, indent=2))
