import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
D=json.loads((R/'validation_artifacts/p159/occ1i/f6c_golden_meta_validation_causal_pilot_v1.json').read_text())
def test_cases(): assert set(D['cases'])=={'DM048','DM049','DM051','DM052','DM054','DM056','DM057'}
def test_count(): assert D['killed_count']+D['inconclusive_count']==7
def test_minimum(): assert all(x['minimum_distinct_detectors']==2 for x in D['cases'].values())
def test_effective(): assert all(x['mutation_effective'] is True for x in D['cases'].values())
def test_family_count(): assert all(x['distinct_protective_detections']==sum(1 for f in x['protective_families'].values() if f['detected']) for x in D['cases'].values())
def test_verdict(): assert all(x['causal_verdict']==('KILLED' if x['distinct_protective_detections']>=2 else 'INCONCLUSIVE') for x in D['cases'].values())
def test_no_prod(): assert D['production_runtime_modified'] is False and D['canonical_sources_modified'] is False
def test_next(): assert D['next_required_stage'] in {'F6_C_GAP_REFINEMENT','F7_META_MUTATION_CROWN'}
def test_epistemics(): assert D['functional_conclusion_only'] is True and D['phenomenology_undetermined'] is True
def test_boundaries(): assert D['p159_final_lock'] is False and D['p160_opened'] is False
