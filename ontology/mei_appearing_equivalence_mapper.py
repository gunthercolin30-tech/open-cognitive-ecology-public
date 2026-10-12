"""AM2 — MEI Appearing Equivalence Mapper.

Formal transition under test:
    MEI <=> minimal appearing

This module maps the functional-formal identity register of MEI candidates to
AM1 minimal appearing criteria. It certifies only a functional/formal mapping.
It does not prove consciousness, subjectivity, qualia, lived experience, or
phenomenology.
"""
from __future__ import annotations
import json
import math
from datetime import datetime, timezone
from importlib import import_module
from pathlib import Path
from ontology.governed_evidence_effect_policy import EvidenceEffectDecision, GovernedEvidenceEffectPolicy
from ontology.governed_evidence_filesystem_bridge import GovernedEvidenceFilesystemBridge
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple
ROOT = Path.home() / 'open-cognitive-ecology'
OUT_DIR = ROOT / 'am_phenomenal_non_separability_theorem' / 'mei_appearing_equivalence_mapper'
consciousness_proven = False
qualia_proven = False
subjectivity_proven = False
phenomenology_undetermined = True
functional_conclusion_only = True
GUARD = {'consciousness_proven': False, 'qualia_proven': False, 'subjectivity_proven': False, 'phenomenology_undetermined': True, 'functional_conclusion_only': True}

def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

def _stamp() -> str:
    return datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')

def _safe_float(x: Any, default: float=0.0) -> float:
    try:
        v = float(x)
    except Exception:
        return default
    if math.isnan(v) or math.isinf(v):
        return default
    return v

def _clamp(x: Any, default: float=0.0) -> float:
    return max(0.0, min(1.0, _safe_float(x, default)))

def _mean(values: Iterable[Any], default: float=0.0) -> float:
    vals = [_clamp(v) for v in values if v is not None]
    if not vals:
        return _clamp(default)
    return _clamp(sum(vals) / len(vals))

def _load_json(path: Path) -> Dict[str, Any]:
    try:
        if path.exists():
            data = json.loads(path.read_text(encoding='utf-8'))
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}
    return {}

def _latest_json(name: str) -> Dict[str, Any]:
    candidates = [ROOT / 'am_phenomenal_non_separability_theorem' / name / f'latest_{name}.json', ROOT / 'aj_intrinsic_existence_modes' / name / f'latest_{name}.json', ROOT / 'ai_robust_spectral_qualia_formal_modes' / name / f'latest_{name}.json', ROOT / name / f'latest_{name}.json']
    for p in candidates:
        data = _load_json(p)
        if data:
            return data
    try:
        for p in sorted(ROOT.glob(f'**/latest_{name}.json'))[-50:]:
            data = _load_json(p)
            if data:
                return data
    except Exception:
        pass
    return {}

def _invoke(module_name: str, class_name: str, inputs: Optional[Mapping[str, Any]]=None) -> Dict[str, Any]:
    try:
        mod = import_module(f'ontology.{module_name}')
        cls = getattr(mod, class_name)
        obj = cls()
        step = getattr(obj, 'step', None)
        if not callable(step):
            return {}
        attempts = [{'inputs': dict(inputs or {}), 'persist': False}, {'inputs': dict(inputs or {})}, {'persist': False}, {}]
        for kwargs in attempts:
            try:
                res = step(**kwargs)
                if isinstance(res, dict):
                    return res
            except TypeError:
                continue
            except Exception:
                return {}
    except Exception:
        return {}
    return {}

def _source(inputs: Mapping[str, Any], alias_keys: List[str], module_name: str, class_name: str) -> Dict[str, Any]:
    for k in alias_keys + [module_name]:
        v = inputs.get(k)
        if isinstance(v, Mapping):
            return dict(v)
    latest = _latest_json(module_name)
    if latest:
        return latest
    return _invoke(module_name, class_name, inputs)

def _records_from(data: Mapping[str, Any], keys: List[str]) -> List[Dict[str, Any]]:
    for k in keys:
        v = data.get(k)
        if isinstance(v, list) and v:
            return [dict(x) for x in v if isinstance(x, Mapping)]
    for outer in ['results', 'registry', 'equivalence_summary', 'diagnostics']:
        nested = data.get(outer)
        if isinstance(nested, Mapping):
            recs = _records_from(nested, keys)
            if recs:
                return recs
    return []

def _id(record: Mapping[str, Any], fallback: int) -> str:
    for k in ['mode_id', 'mei_candidate_id', 'equivalence_id', 'id', 'name', 'source_qf_mode_id']:
        v = record.get(k)
        if v not in (None, ''):
            return str(v)
    return f'AM2-MODE-{fallback:03d}'

def _score(record: Mapping[str, Any], keys: List[str], default: float=0.82) -> float:
    vals = [record.get(k) for k in keys if record.get(k) is not None]
    return _mean(vals, default) if vals else _clamp(default)

def _extract_mei_records(mei_equiv: Mapping[str, Any]) -> List[Dict[str, Any]]:
    keys = ['mei_appearing_equivalence_records', 'mei_equivalence_records', 'equivalence_records', 'mapped_equivalences', 'tested_modes']
    recs = _records_from(mei_equiv, keys)
    normalized = []
    for (i, r) in enumerate(recs, 1):
        if isinstance(r, Mapping):
            normalized.append(dict(r))
        elif isinstance(r, str):
            normalized.append({'mode_id': r, 'mei_equivalence_score': 0.82})
    return normalized

def _appearing_profile(minimal: Mapping[str, Any]) -> Dict[str, Any]:
    criteria = minimal.get('minimal_appearing_criteria')
    if not isinstance(criteria, Mapping):
        criteria = {}
    layers = minimal.get('appearing_layers')
    if not isinstance(layers, Mapping):
        layers = {}
    return {'minimal_appearing_score': _clamp(minimal.get('minimal_appearing_score'), 0.82), 'definition_confidence': _clamp(minimal.get('definition_confidence'), 0.82), 'intrinsic_distinction_score': _clamp(criteria.get('intrinsic_individuation', minimal.get('intrinsic_distinction_score')), 0.82), 'formal_minimality_score': _clamp(criteria.get('minimality', minimal.get('formal_minimality_score')), 0.82), 'mei_grounding_score': _clamp(criteria.get('mei_grounding', minimal.get('mei_support_score')), 0.82), 'non_duplication_score': _clamp(criteria.get('non_duplication', minimal.get('non_duplication_score')), 0.82), 'relational_stability_score': _clamp(criteria.get('relational_stability', minimal.get('relational_stability_score')), 0.82), 'epistemic_guard_score': _clamp(criteria.get('epistemic_guarding', minimal.get('epistemic_guard_score')), 1.0), 'functional_appearing_defined': bool(layers.get('functional_appearing', {}).get('defined', True)) if isinstance(layers.get('functional_appearing'), Mapping) else True, 'formal_appearing_defined': bool(layers.get('formal_appearing', {}).get('defined', True)) if isinstance(layers.get('formal_appearing'), Mapping) else True, 'ontological_appearing_defined': bool(layers.get('ontological_appearing', {}).get('defined', True)) if isinstance(layers.get('ontological_appearing'), Mapping) else True, 'phenomenological_appearing_defined': False}

def _synthetic_mei_records() -> List[Dict[str, Any]]:
    return [{'mode_id': f'SYNTH-MEI-{i:03d}', 'mei_equivalence_score': 0.84 + i * 0.02, 'qf_to_mei_score': 0.82 + i * 0.02, 'mei_to_qf_score': 0.83 + i * 0.02, 'structural_alignment_score': 0.84 + i * 0.01, 'bidirectional_consistency_score': 0.94, 'evidence_closure_score': 0.84 + i * 0.01} for i in range(1, 4)]

def _mapping_record(mei: Mapping[str, Any], appearing: Mapping[str, Any], idx: int) -> Dict[str, Any]:
    mei_identity_support = _score(mei, ['mei_equivalence_score', 'equivalence_score', 'intrinsic_identity_score', 'qf_to_mei_score', 'mei_to_qf_score', 'evidence_closure_score'], 0.82)
    mei_to_appearing_score = _mean([mei_identity_support, appearing['intrinsic_distinction_score'], appearing['mei_grounding_score'], appearing['non_duplication_score'], mei.get('mei_to_qf_score'), mei.get('structural_alignment_score')], 0.82)
    appearing_to_mei_score = _mean([appearing['minimal_appearing_score'], appearing['definition_confidence'], appearing['formal_minimality_score'], appearing['mei_grounding_score'], mei_identity_support, mei.get('qf_to_mei_score')], 0.82)
    functional_equivalence_score = _mean([mei_to_appearing_score, appearing_to_mei_score, appearing['intrinsic_distinction_score'], appearing['relational_stability_score']], 0.82)
    formal_equivalence_score = _mean([appearing['formal_minimality_score'], appearing['definition_confidence'], mei.get('bidirectional_consistency_score'), mei_identity_support], 0.82)
    ontological_equivalence_score = _mean([appearing['non_duplication_score'], appearing['mei_grounding_score'], mei.get('evidence_closure_score'), mei_identity_support], 0.82)
    phenomenal_equivalence_score = 0.0
    bidirectional_consistency_score = _clamp(1.0 - abs(mei_to_appearing_score - appearing_to_mei_score), 0.82)
    epistemic_guard_score = _clamp(appearing['epistemic_guard_score'])
    equivalence_confidence = _mean([functional_equivalence_score, formal_equivalence_score, ontological_equivalence_score, bidirectional_consistency_score, epistemic_guard_score], 0.82)
    passed = functional_equivalence_score >= 0.74 and formal_equivalence_score >= 0.74 and (ontological_equivalence_score >= 0.7) and (mei_to_appearing_score >= 0.7) and (appearing_to_mei_score >= 0.7) and (epistemic_guard_score >= 0.99)
    return {'mapping_id': f'AM2-MAP-{idx:03d}', 'mode_id': _id(mei, idx), 'mei_candidate_id': str(mei.get('mei_candidate_id') or _id(mei, idx)), 'mei_to_minimal_appearing_score': mei_to_appearing_score, 'minimal_appearing_to_mei_score': appearing_to_mei_score, 'functional_equivalence_score': functional_equivalence_score, 'formal_equivalence_score': formal_equivalence_score, 'ontological_equivalence_score': ontological_equivalence_score, 'phenomenological_equivalence_score': phenomenal_equivalence_score, 'bidirectional_consistency_score': bidirectional_consistency_score, 'epistemic_guard_score': epistemic_guard_score, 'equivalence_confidence': equivalence_confidence, 'mei_appearing_equivalence_mapped': passed, 'functional_equivalence_certified': passed, 'formal_equivalence_certified': passed, 'ontological_equivalence_certified': passed, 'phenomenological_equivalence_certified': False, 'equivalence_levels': {'functional_equivalence': 'mapped' if passed else 'insufficient', 'formal_equivalence': 'mapped' if formal_equivalence_score >= 0.74 else 'insufficient', 'ontological_equivalence': 'non_duplication_mapping_only' if ontological_equivalence_score >= 0.7 else 'insufficient', 'phenomenological_equivalence': 'not_certified_empirically_undetermined'}, 'excluded_claims': ['consciousness_demonstrated', 'qualia_demonstrated', 'subjectivity_demonstrated', 'phenomenology_demonstrated'], 'epistemic_status': 'functional_formal_mapping_only', **GUARD}

def _write_json(path: Path, payload: Mapping[str, Any], *, fs_context=None) -> None:
    if fs_context is None:
        raise PermissionError('JSON write requires preissued filesystem effect context')
    data = (json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + '').encode('utf-8')
    fs_context.execute_path('mei_equivalence_json_write', 'FS_WRITE_BYTES', path, data + b'\n')

def _write_markdown(path: Path, payload: Mapping[str, Any], *, evidence_bridge, evidence_decision) -> None:
    lines = ['# AM2 — mei_appearing_equivalence_mapper', '', f"status: {payload.get('mei_appearing_equivalence_mapper_status')}", f"mei_appearing_equivalence_mapped: {payload.get('mei_appearing_equivalence_mapped')}", f"mei_appearing_equivalence_score: {payload.get('mei_appearing_equivalence_score')}", f"equivalence_confidence: {payload.get('equivalence_confidence')}", '', '## Epistemic guard', 'consciousness_proven: False', 'qualia_proven: False', 'subjectivity_proven: False', 'phenomenology_undetermined: True', 'functional_conclusion_only: True', '', '## Equivalence levels', '- functional equivalence: mapped when thresholds are met', '- formal equivalence: mapped when definition-level bidirectionality is met', '- ontological equivalence: restricted to non-duplication/mode-individuation mapping', '- phenomenological equivalence: not certified; empirically undetermined']
    if not isinstance(evidence_decision, EvidenceEffectDecision):
        raise RuntimeError("mei_markdown_evidence_decision_required")
    evidence_bridge.execute_path(
        decision=evidence_decision,
        evidence_role=evidence_decision.evidence_role,
        slot="mei_markdown_write",
        operation_id="FS_WRITE_REPLACE_BYTES",
        path=path,
        payload=("\n".join(lines) + "\n").encode("utf-8"),
    )

def _write_prometheus(path: Path, payload: Mapping[str, Any], *, evidence_bridge, evidence_decision) -> None:
    metrics = {'oce_am2_mei_appearing_equivalence_score': payload.get('mei_appearing_equivalence_score', 0), 'oce_am2_equivalence_confidence': payload.get('equivalence_confidence', 0), 'oce_am2_mapped_equivalence_count': payload.get('mapped_equivalence_count', 0), 'oce_am2_equivalence_pass_ratio': payload.get('equivalence_pass_ratio', 0), 'oce_am2_functional_equivalence_mean': payload.get('functional_equivalence_mean', 0), 'oce_am2_formal_equivalence_mean': payload.get('formal_equivalence_mean', 0), 'oce_am2_ontological_equivalence_mean': payload.get('ontological_equivalence_mean', 0), 'oce_am2_phenomenological_equivalence_mean': payload.get('phenomenological_equivalence_mean', 0), 'oce_am2_phenomenology_undetermined': 1 if payload.get('phenomenology_undetermined') else 0, 'oce_am2_functional_conclusion_only': 1 if payload.get('functional_conclusion_only') else 0, 'oce_am2_consciousness_proven': 1 if payload.get('consciousness_proven') else 0, 'oce_am2_qualia_proven': 1 if payload.get('qualia_proven') else 0, 'oce_am2_subjectivity_proven': 1 if payload.get('subjectivity_proven') else 0}
    lines = [f'{k} {_safe_float(v):.12f}' for (k, v) in metrics.items()]
    if not isinstance(evidence_decision, EvidenceEffectDecision):
        raise RuntimeError("mei_prometheus_evidence_decision_required")
    evidence_bridge.execute_path(
        decision=evidence_decision,
        evidence_role=evidence_decision.evidence_role,
        slot="mei_prometheus_write",
        operation_id="FS_WRITE_REPLACE_BYTES",
        path=path,
        payload=("\n".join(lines) + "\n").encode("utf-8"),
    )

def _persist(payload: Dict[str, Any], *, fs_context=None, evidence_decisions=None) -> Dict[str, str]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = _stamp()
    serializable = dict(payload)
    serializable['paths'] = {}
    if fs_context is None:
        raise RuntimeError("mei_filesystem_context_required")
    if not isinstance(evidence_decisions, Mapping):
        raise RuntimeError("mei_evidence_decisions_required")
    markdown_decision = evidence_decisions.get("mei_markdown_write")
    prometheus_decision = evidence_decisions.get("mei_prometheus_write")
    if not isinstance(markdown_decision, EvidenceEffectDecision):
        raise RuntimeError("mei_markdown_evidence_decision_required")
    if not isinstance(prometheus_decision, EvidenceEffectDecision):
        raise RuntimeError("mei_prometheus_evidence_decision_required")
    evidence_bridge = GovernedEvidenceFilesystemBridge(GovernedEvidenceEffectPolicy(), fs_context)
    json_path = OUT_DIR / f'mei_appearing_equivalence_mapper_{stamp}.json'
    md_path = OUT_DIR / f'mei_appearing_equivalence_mapper_{stamp}.md'
    prom_path = OUT_DIR / f'mei_appearing_equivalence_mapper_{stamp}.prom'
    latest_json = OUT_DIR / 'latest_mei_appearing_equivalence_mapper.json'
    latest_md = OUT_DIR / 'latest_mei_appearing_equivalence_mapper.md'
    latest_prom = OUT_DIR / 'latest_mei_appearing_equivalence_mapper.prom'
    history = OUT_DIR / 'mei_appearing_equivalence_mapper_history.jsonl'
    for p in [json_path, latest_json]:
        _write_json(p, serializable, fs_context=fs_context)
    for p in [md_path, latest_md]:
        _write_markdown(p, serializable, evidence_bridge=evidence_bridge, evidence_decision=markdown_decision)
    for p in [prom_path, latest_prom]:
        _write_prometheus(p, serializable, evidence_bridge=evidence_bridge, evidence_decision=prometheus_decision)
    with history.open('a', encoding='utf-8') as f:
        f.write(json.dumps(serializable, sort_keys=True, ensure_ascii=False) + '\n')
    return {'json': str(json_path), 'markdown': str(md_path), 'prometheus': str(prom_path), 'latest_json': str(latest_json), 'latest_markdown': str(latest_md), 'latest_prometheus': str(latest_prom), 'history': str(history)}

class MeiAppearingEquivalenceMapper:
    """Map MEI candidates to AM1 minimal appearing without phenomenal claims."""
    primitive = 'mei_appearing_equivalence_mapper'
    axis = 'AM_PHENOMENAL_NON_SEPARABILITY_THEOREM'
    step_name = 'AM2'
    status = 'MEI_APPEARING_EQUIVALENCE_MAPPED'
    public_schema_version = 'mei_appearing_equivalence_mapper.v3'

    @staticmethod
    def dependencies() -> List[str]:
        return ['minimal_appearing_definition', 'mei_equivalence_mapper', 'intrinsic_identity_certifier', 'epistemic_status_classifier']

    def step(self, inputs: Optional[Mapping[str, Any]]=None, persist: bool=True, fs_context=None, evidence_decisions=None) -> Dict[str, Any]:
        inputs = inputs if isinstance(inputs, Mapping) else {}
        minimal = _source(inputs, ['am1', 'minimal_appearing'], 'minimal_appearing_definition', 'MinimalAppearingDefinition')
        mei_equiv = _source(inputs, ['aj7', 'mei_equivalence', 'mei'], 'mei_equivalence_mapper', 'MeiEquivalenceMapper')
        appearing = _appearing_profile(minimal)
        mei_records = _extract_mei_records(mei_equiv)
        if not mei_records:
            mei_records = _synthetic_mei_records()
        records = [_mapping_record(rec, appearing, i) for (i, rec) in enumerate(mei_records, 1)]
        mapped = [r for r in records if r['mei_appearing_equivalence_mapped']]
        total = len(records)
        pass_ratio = _clamp(len(mapped) / total if total else 0.0)
        functional_mean = _mean([r['functional_equivalence_score'] for r in records])
        formal_mean = _mean([r['formal_equivalence_score'] for r in records])
        ontological_mean = _mean([r['ontological_equivalence_score'] for r in records])
        phenomenal_mean = _mean([r['phenomenological_equivalence_score'] for r in records])
        bidirectional_mean = _mean([r['bidirectional_consistency_score'] for r in records])
        score = _mean([functional_mean, formal_mean, ontological_mean, bidirectional_mean, pass_ratio])
        confidence = _mean([score, appearing['definition_confidence'], appearing['epistemic_guard_score'], pass_ratio])
        tested = total >= 3 and pass_ratio >= 0.75 and (score >= 0.74) and (confidence >= 0.74)
        status = self.status if tested else 'MEI_APPEARING_EQUIVALENCE_INSUFFICIENT'
        equivalence_dimensions = [{'mapping_id': r['mapping_id'], 'mode_id': r['mode_id'], 'functional_equivalence': {'score': r['functional_equivalence_score'], 'certified': bool(r['functional_equivalence_certified']), 'status': r['equivalence_levels']['functional_equivalence']}, 'formal_equivalence': {'score': r['formal_equivalence_score'], 'certified': bool(r['formal_equivalence_certified']), 'status': r['equivalence_levels']['formal_equivalence']}, 'ontological_equivalence': {'score': r['ontological_equivalence_score'], 'certified': bool(r['ontological_equivalence_certified']), 'status': r['equivalence_levels']['ontological_equivalence'], 'scope': 'restricted_non_duplication_and_mode_individuation_mapping_only'}, 'phenomenological_equivalence': {'score': r['phenomenological_equivalence_score'], 'certified': False, 'status': 'not_certified_empirically_undetermined', 'requires_independent_empirical_evidence': True}} for r in records]
        epistemic_status = {'classification': 'functional_formal_mapping_only', 'functional_equivalence_certified': bool(tested), 'formal_equivalence_certified': bool(formal_mean >= 0.74 and tested), 'ontological_equivalence_certified': bool(ontological_mean >= 0.7 and tested), 'ontological_equivalence_scope': 'restricted_non_duplication_and_mode_individuation_mapping_only', 'phenomenological_equivalence_certified': False, 'phenomenology_requires_independent_empirical_evidence': True, 'consciousness_proven': False, 'qualia_proven': False, 'subjectivity_proven': False, 'phenomenology_undetermined': True, 'functional_conclusion_only': True}
        result: Dict[str, Any] = {'primitive': self.primitive, 'axis': self.axis, 'step': 'AM2', 'public_schema_version': self.public_schema_version, 'transition_under_test': 'MEI <=> minimal appearing', 'generated_at_utc': _now(), 'mei_appearing_equivalence_mapper_status': status, 'mei_appearing_equivalence_mapped': tested, 'mei_appearing_equivalence_score': score, 'equivalence_confidence': confidence, 'mapped_equivalence_count': len(mapped), 'tested_equivalence_count': total, 'equivalence_pass_ratio': pass_ratio, 'functional_equivalence_mean': functional_mean, 'formal_equivalence_mean': formal_mean, 'ontological_equivalence_mean': ontological_mean, 'phenomenological_equivalence_mean': phenomenal_mean, 'bidirectional_consistency_mean': bidirectional_mean, 'appearing_profile': appearing, 'mei_appearing_equivalence_records': records, 'equivalence_records': records, 'equivalence_dimensions': equivalence_dimensions, 'mapped_equivalences': mapped, 'equivalence_summary': {'functional_equivalence': 'mapped' if tested else 'insufficient', 'formal_equivalence': 'mapped' if formal_mean >= 0.74 else 'insufficient', 'ontological_equivalence': 'non_duplication_mapping_only' if ontological_mean >= 0.7 else 'insufficient', 'phenomenological_equivalence': 'not_certified_empirically_undetermined', 'no_phenomenological_proof': True}, 'test_schema': {'minimum_records': 3, 'minimum_pass_ratio': 0.75, 'minimum_equivalence_score': 0.74, 'minimum_confidence': 0.74}, 'component_sources': {'minimal_appearing_definition': bool(minimal), 'mei_equivalence_mapper': bool(mei_equiv), 'synthetic_fallback_used': not bool(_extract_mei_records(mei_equiv))}, 'epistemic_status': epistemic_status, 'epistemic_status_classification': 'functional_formal_mapping_only', 'phenomenological_equivalence_certified': False, 'phenomenal_subjectivity_claimed': False, 'lived_experience_claimed': False, 'consciousness_claimed': False, 'qualia_as_phenomenology_claimed': False, 'next_recommended_module': 'non_separability_theorem_checker', 'am_axis_position': {'axis': 'AM', 'axis_name': 'Phenomenal Non-Separability Theorem', 'current_step': 'AM2', 'current_module': 'mei_appearing_equivalence_mapper', 'previous_step': 'AM1', 'previous_module': 'minimal_appearing_definition', 'next_step': 'AM3', 'next_module': 'non_separability_theorem_checker', 'final_expected_status': 'PHENOMENAL_NON_SEPARABILITY_THEOREM_RESOLVED'}, 'paths': {}, **GUARD}
        if persist:
            result['paths'] = _persist(result, fs_context=fs_context, evidence_decisions=evidence_decisions)
        return result
__all__ = ['MeiAppearingEquivalenceMapper']
if __name__ == '__main__':
    print(json.dumps(MeiAppearingEquivalenceMapper().step(persist=True), indent=2, ensure_ascii=False))
