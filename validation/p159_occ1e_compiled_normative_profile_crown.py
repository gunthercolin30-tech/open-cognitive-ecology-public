from __future__ import annotations
import json
from hashlib import sha256
from pathlib import Path
from ontology import occ_compiled_normative_profile as cnp

EXPECTED_RUNTIME_CONSUMERS = ('NormResolver','CCAD','AuthorizationEngine','CapabilityGate','RecoveryEngine','AssuranceEngine')

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'validation_artifacts/p159/occ1c/compiled_normative_profile_v1.json'
SCHEMA=ROOT/'schemas/p159_occ1e_compiled_normative_profile_v1.schema.json'
COMPILER=ROOT/'ontology/occ_constitutional_compiler.py'
OUT=ROOT/'validation_artifacts/p159/occ1e'
STATIC=[ROOT/'validation_artifacts/p159/occ1d/static_constitutional_check_report_v1_2.json',ROOT/'validation_artifacts/p159/occ1d/static_constitutional_check_report_v1.json']
def h(p): return sha256(p.read_bytes()).hexdigest()
def dump(p,o): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(o,indent=2,sort_keys=True)+'\n',encoding='utf-8')
def main():
    s=next((p for p in STATIC if p.exists()),None)
    if s is None: raise SystemExit('OCC1E_CROWN_FAIL: OCC-1D static report absent')
    src=json.loads(BASE.read_text(encoding='utf-8'))
    p=cnp.build_profile(src,h(BASE),h(COMPILER),h(SCHEMA),h(s))
    v=cnp.verify_profile(p)
    if v['status']!='PASS': raise SystemExit('OCC1E_CROWN_FAIL: '+str(v))
    OUT.mkdir(parents=True,exist_ok=True)
    pp=OUT/'compiled_normative_profile_v1.json'; mp=OUT/'compiled_normative_profile_manifest_v1.json'
    ip=OUT/'runtime_interface_contract_v1.json'; xp=OUT/'compiled_normative_profile_explanation_v1.txt'; rp=OUT/'occ1e_crown_report_v1.json'
    dump(pp,p); dump(mp,cnp.manifest(p))
    dump(ip,{'schema':'oce.p159.occ1e.runtime_interface_contract.v1','profile_artifact_hash':p['artifact_hash'],'contract_only':True,'consumers':list(EXPECTED_RUNTIME_CONSUMERS),'execution_capability':False,'authorization_capability':False,'allow_candidate_is_permission_to_execute':False,'runtime_consumer_graph_proven':False,'enforcement_status':'UNRESOLVED','functional_conclusion_only':True,'phenomenology_undetermined':True})
    xp.write_text(cnp.human_explanation(p),encoding='utf-8')
    dump(rp,{'schema':'oce.p159.occ1e.crown_report.v1','milestone':'P159/OCC-1E','decision':'OCC1E_CROWN_READY_FOR_EXTERNAL_TEST_EXECUTION','profile_artifact_sha256':h(pp),'profile_semantic_hash':p['artifact_hash'],'manifest_sha256':h(mp),'runtime_interface_contract_sha256':h(ip),'explanation_sha256':h(xp),'schema_sha256':h(SCHEMA),'compiler_sha256':h(COMPILER),'occ1c_source_profile_sha256':h(BASE),'occ1d_static_report_sha256':h(s),'authorization_created':False,'authority_activated':False,'execution_performed':False,'self_activation':False,'occ1f_opened':False,'p160_opened':False,'p159_final_lock':False,'occ1e_closed':False,'runtime_consumer_graph_proven':False,'enforcement_status':'UNRESOLVED','functional_conclusion_only':True,'phenomenology_undetermined':True})
    print('OCC1E_ARTIFACT_MATERIALIZATION_OK'); print('OCC1E_ARTIFACT_BINDING_OK'); print('OCC1E_UNRESOLVED_RUNTIME_EVIDENCE_PRESERVED'); print('OCC1E_CLOSURE_NOT_PERFORMED'); print('OCC1F_NOT_OPENED'); print('P160_NOT_OPENED')
if __name__=='__main__': main()
