from copy import deepcopy
from pathlib import Path
from ontology import occ_golden_constitutional_vectors as g
ROOT=Path(__file__).resolve().parents[1]

def test_strict_schema_and_vectors():
    r=g.materialize(ROOT); assert r['status']=='PASS',r
    p=g.paths(ROOT); s=g._read_json(p['out']/'golden_vector_schema_v1.json')
    assert s['additionalProperties'] is False and 'family' in s['required']
    for n in ['gcv_core_v1.json','gcv_extended_v1.json']:
        assert all(g.validate_vector_strict(v) for v in g._read_json(p['out']/n)['vectors'])

def test_strict_rejects_missing_and_extra():
    v=g.build_core()[0]; a=deepcopy(v); a.pop('rationale'); b=deepcopy(v); b['compiler_hash']='x'
    assert not g.validate_vector_strict(a); assert not g.validate_vector_strict(b)

def test_package_version_from_source():
    p=g.paths(ROOT); g.materialize(ROOT); m=g._read_json(p['out']/'corpus_manifest_v1.json')
    assert m['source_binding']['package_version']==g._source_package_version(p['source_manifest'])

def test_gcvi_computed_all_pass():
    p=g.paths(ROOT); g.materialize(ROOT)
    c=g._read_json(p['out']/'gcv_core_v1.json'); e=g._read_json(p['out']/'gcv_extended_v1.json')
    m=g._read_json(p['out']/'corpus_manifest_v1.json'); l=g._read_json(p['out']/'change_ledger_v1.json'); r=g._read_json(p['out']/'golden_run_report_v1.json')
    x=g.compute_gcvi(c,e,m,l,r,r['source_binding']); assert x==r['gcvi_status']; assert set(x.values())=={'PASS'}

def test_root_inconclusive_fails_gcvi4():
    p=g.paths(ROOT); g.materialize(ROOT)
    c=g._read_json(p['out']/'gcv_core_v1.json'); e=g._read_json(p['out']/'gcv_extended_v1.json')
    m=g._read_json(p['out']/'corpus_manifest_v1.json'); l=g._read_json(p['out']/'change_ledger_v1.json'); r=g._read_json(p['out']/'golden_run_report_v1.json')
    r['core_results'][0]['vector_verdict']='INCONCLUSIVE'
    assert g.compute_gcvi(c,e,m,l,r,r['source_binding'])['GCVI-4']=='FAIL'

def test_stale_binding_fails_gcvi9():
    p=g.paths(ROOT); g.materialize(ROOT)
    c=g._read_json(p['out']/'gcv_core_v1.json'); e=g._read_json(p['out']/'gcv_extended_v1.json')
    m=g._read_json(p['out']/'corpus_manifest_v1.json'); l=g._read_json(p['out']/'change_ledger_v1.json'); r=g._read_json(p['out']/'golden_run_report_v1.json')
    x=deepcopy(r['source_binding']); x['package_version']='DRIFT'
    assert g.compute_gcvi(c,e,m,l,r,x)['GCVI-9']=='FAIL'

def test_boundaries_closed():
    r=g.materialize(ROOT); assert r['occ1g_closed'] is False and r['occ1h_opened'] is False and r['p160_opened'] is False and r['p159_final_lock'] is False
