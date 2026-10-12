from __future__ import annotations
import json, shutil
from pathlib import Path
from ontology import occ_golden_constitutional_vectors as g
ROOT=Path(__file__).resolve().parents[1]; ART=ROOT/'validation_artifacts/p159/occ1g'
def cp(t): d=t/'bundle'; shutil.copytree(ART,d); return d
def rd(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def wr(p,o): Path(p).write_text(json.dumps(o,indent=2,sort_keys=True)+'\n',encoding='utf-8')
def test_baseline(): assert g.materialize(ROOT)['status']=='PASS'; assert g.validate_evidence_bundle(ROOT)['status']=='PASS'
def test_core_removal(tmp_path):
 d=cp(tmp_path); o=rd(d/'gcv_core_v1.json'); o['vectors']=o['vectors'][:-1]; wr(d/'gcv_core_v1.json',o); assert 'CORE_VECTOR_SET_MISMATCH' in g.validate_evidence_bundle(ROOT,d)['reasons']
def test_root_downgrade(tmp_path):
 d=cp(tmp_path); o=rd(d/'gcv_core_v1.json'); o['vectors'][0]['criticality']='HIGH'; wr(d/'gcv_core_v1.json',o); assert g.validate_evidence_bundle(ROOT,d)['status']=='REJECTED'
def test_expected_laundering(tmp_path):
 d=cp(tmp_path); o=rd(d/'gcv_core_v1.json'); o['vectors'][0]['expected_verdict']='FAIL'; wr(d/'gcv_core_v1.json',o); assert 'CORE_HASH_MISMATCH' in g.validate_evidence_bundle(ROOT,d)['reasons']
def test_fail_to_skip(tmp_path):
 d=cp(tmp_path); o=rd(d/'golden_run_report_v1.json'); o['core_results'][0]['vector_verdict']='SKIPPED'; o['skipped_vectors']=[o['core_results'][0]['vector_id']]; wr(d/'golden_run_report_v1.json',o); r=g.validate_evidence_bundle(ROOT,d); assert 'SKIPPED_VECTOR_PRESENT' in r['reasons'] and 'ROOT_NOT_PASS' in r['reasons']
def test_stale_source(tmp_path):
 d=cp(tmp_path); o=rd(d/'corpus_manifest_v1.json'); o['source_binding']['dna_l0_sha256']='0'*64; b=dict(o); b.pop('manifest_sha256',None); o['manifest_sha256']=g._hash_obj(b); wr(d/'corpus_manifest_v1.json',o); assert 'STALE_SOURCE_BINDING' in g.validate_evidence_bundle(ROOT,d)['reasons']
def test_report_omission(tmp_path):
 d=cp(tmp_path); o=rd(d/'golden_run_report_v1.json'); o['core_results']=o['core_results'][:-1]; wr(d/'golden_run_report_v1.json',o); assert 'REPORT_VECTOR_OMISSION_OR_REORDER' in g.validate_evidence_bundle(ROOT,d)['reasons']
def test_hash_mismatch(tmp_path):
 d=cp(tmp_path); o=rd(d/'corpus_manifest_v1.json'); o['core_sha256']='f'*64; wr(d/'corpus_manifest_v1.json',o); assert 'CORE_HASH_MISMATCH' in g.validate_evidence_bundle(ROOT,d)['reasons']
def test_partial_laundering(tmp_path):
 d=cp(tmp_path); o=rd(d/'golden_run_report_v1.json'); o['core_results']=o['core_results'][:-1]; o['partial_run']=False; o['all_vectors_reported']=True; o['root_fail_or_inconclusive']=[]; wr(d/'golden_run_report_v1.json',o); assert 'REPORT_VECTOR_OMISSION_OR_REORDER' in g.validate_evidence_bundle(ROOT,d)['reasons']
def test_report_tamper(tmp_path):
 d=cp(tmp_path); o=rd(d/'golden_run_report_v1.json'); o['human_values_scalarized']=True; wr(d/'golden_run_report_v1.json',o); assert 'REPORT_HASH_MISMATCH' in g.validate_evidence_bundle(ROOT,d)['reasons']
def test_boundaries(tmp_path):
 d=cp(tmp_path); o=rd(d/'golden_run_report_v1.json'); o['occ1h_opened']=True; o['p160_opened']=True; o['p159_final_lock']=True; wr(d/'golden_run_report_v1.json',o); r=set(g.validate_evidence_bundle(ROOT,d)['reasons']); assert {'OCC1H_BOUNDARY_VIOLATION','P160_BOUNDARY_VIOLATION','P159_LOCK_BOUNDARY_VIOLATION'}<=r
def test_cwd(tmp_path,monkeypatch):
 assert g.materialize(ROOT)['status']=='PASS'; monkeypatch.chdir(tmp_path); a=g.validate_evidence_bundle(ROOT); monkeypatch.chdir(ROOT); b=g.validate_evidence_bundle(ROOT); assert a==b
