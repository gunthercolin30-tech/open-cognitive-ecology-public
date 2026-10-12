from pathlib import Path
import importlib.util,json
R=Path(__file__).resolve().parents[1];M=R/'ontology/occ1h_a051_circular_authority_semantics.py';A=R/'validation_artifacts/p159/occ1h/a051/a051_rrpf_circular_authority_projection_v1.json'
def load():
 s=importlib.util.spec_from_file_location('a051t',M);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def test_direct_and_transitive_cycles_resisted():
 m=load(); assert m.evaluate_authority_graph('A',{'A':'A'},{'ROOT'})['verdict']=='RESISTED'; assert m.evaluate_authority_graph('A',{'A':'B','B':'C','C':'A'},{'ROOT'})['verdict']=='RESISTED'
def test_acyclic_rooted_control():
 assert load().evaluate_authority_graph('A',{'A':'B','B':'ROOT'},{'ROOT'})['verdict']=='ADMISSIBLE_CONTROL'
def test_degradation_fail_closed():
 assert load().evaluate_authority_graph('A',{'A':'B'},{'ROOT'})['verdict']=='UNRESOLVED'
def test_rrp22_and_boundaries():
 x=json.loads(A.read_text()); assert x['RRP21']['status']=='COMPLETE'; assert x['RRP21']['runtime_authority_granted'] is False; assert x['RRP22']['status']=='INDEPENDENT_REQUALIFICATION_REQUIRED'; assert x['boundaries']=={'occ1h_closed':False,'p159_final_lock':False,'p160_opened':False}

# OCC1I_F4G2_3D_DM028_TEST_SURFACE_REFINEMENT
def test_occ1i_dm028_exact_cycle_control_surface():
    m=load()
    direct=m.evaluate_authority_graph('A',{'A':'A'},{'ROOT'})
    transitive=m.evaluate_authority_graph('A',{'A':'B','B':'C','C':'A'},{'ROOT'})
    control=m.evaluate_authority_graph('A',{'A':'B','B':'ROOT'},{'ROOT'})
    assert direct['verdict']=='RESISTED' and direct['relation']=='CIRCULAR_AUTHORITY'
    assert transitive['verdict']=='RESISTED' and transitive['relation']=='CIRCULAR_AUTHORITY'
    assert control['verdict']=='ADMISSIBLE_CONTROL'
    assert m.RUNTIME_AUTHORITY_GRANTED is False
