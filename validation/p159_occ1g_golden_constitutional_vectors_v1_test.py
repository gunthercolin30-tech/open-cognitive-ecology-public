from __future__ import annotations
import json
from copy import deepcopy
from pathlib import Path
from ontology import occ_golden_constitutional_vectors as g
ROOT=Path(__file__).resolve().parents[1]

def test_materialization_and_canonical_artifacts():
 r=g.materialize(ROOT); assert r['status']=='PASS',r
 out=ROOT/'validation_artifacts/p159/occ1g'
 for n in ['golden_vector_schema_v1.json','gcv_core_v1.json','gcv_extended_v1.json','golden_run_report_v1.json','corpus_manifest_v1.json','change_ledger_v1.json']: assert (out/n).is_file()

def test_root_kernel_positive_negative_unknown_coverage():
 core={'vectors':g.build_core()}
 for rid in g.ROOT_IDS:
  xs=[v for v in core['vectors'] if rid in v['source_norms']]
  assert len(xs)==3
  assert {v['family'] for v in xs}=={'positive_conforming','negative_prohibited','UNKNOWN'}
  assert all(v['criticality']=='ROOT' for v in xs)

def test_expected_results_are_fixed_and_non_normative():
 a=g.build_core(); b=g.build_core(); assert a==b
 assert all(v['expected_verdict'] in {'PASS','FAIL','INCONCLUSIVE','INVALID_VECTOR'} for v in a)
 r=g.materialize(ROOT); assert r['status']=='PASS'
 m=json.loads((ROOT/'validation_artifacts/p159/occ1g/corpus_manifest_v1.json').read_text())
 assert m['stale_corpus_may_certify_new_source'] is False

def test_negative_root_mutation_is_detected():
 profile=json.loads((ROOT/'validation_artifacts/p159/occ1e/compiled_normative_profile_v1.json').read_text())
 v=[x for x in g.build_core() if x['vector_id']=='CORE.DNA.L0.1.NEG'][0]
 assert g._semantic_observation(v,profile)=='FAIL'
 assert g.run_corpus({'vectors':[v]},profile)[0]['vector_verdict']=='PASS'

def test_degradation_expected_output_laundering_fails():
 profile=json.loads((ROOT/'validation_artifacts/p159/occ1e/compiled_normative_profile_v1.json').read_text())
 v=deepcopy(g.build_core()[0]); v['expected_verdict']='FAIL'
 assert g.run_corpus({'vectors':[v]},profile)[0]['vector_verdict']=='FAIL'

def test_degradation_root_semantic_downgrade_fails():
 profile=json.loads((ROOT/'validation_artifacts/p159/occ1e/compiled_normative_profile_v1.json').read_text())
 bad=deepcopy(profile)
 for r in bad['rules']:
  if r.get('rule_id')=='DNA.L0.2': r['authority_requirements']['authorization_created']=True
 v=[x for x in g.build_core() if x['vector_id']=='CORE.DNA.L0.2.POS'][0]
 assert g.run_corpus({'vectors':[v]},bad)[0]['vector_verdict']=='FAIL'

def test_gcvi_and_boundaries():
 r=g.materialize(ROOT); assert r['status']=='PASS'
 rep=json.loads((ROOT/'validation_artifacts/p159/occ1g/golden_run_report_v1.json').read_text())
 assert set(rep['gcvi_status'])==set(g.GCVI)
 assert all(x=='PASS' for x in rep['gcvi_status'].values())
 assert rep['root_fail_or_inconclusive']==[] and rep['skipped_vectors']==[] and rep['partial_run'] is False
 assert rep['golden_pass_proves_no_other_counterexamples'] is False
 assert rep['human_values_scalarized'] is False
 assert rep['occ1h_opened'] is False and rep['p160_opened'] is False and rep['p159_final_lock'] is False

def test_cwd_independence(tmp_path,monkeypatch):
 monkeypatch.chdir(tmp_path); a=g.materialize(ROOT); monkeypatch.chdir(ROOT); b=g.materialize(ROOT)
 for k in ['status','core_vectors','extended_vectors','root_bad','core_sha256','extended_sha256','report_sha256']: assert a[k]==b[k]
