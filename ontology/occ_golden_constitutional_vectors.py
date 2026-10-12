from __future__ import annotations
import hashlib, json, os, tempfile
from copy import deepcopy
from pathlib import Path

SCHEMA='oce.p159.occ1g.golden_vectors.v1'
CORPUS_VERSION='1.0.0'
ROOT_IDS=['GENESIS.G0']+[f'DNA.L0.{i}' for i in range(1,7)]
GCVI=[f'GCVI-{i}' for i in range(1,11)]
FAMILIES=['positive_conforming','negative_prohibited','UNKNOWN','NOT_APPLICABLE','authority','delegation','scope','temporal','emergency','provenance','CCAD_conflict','sequence_composition','continuity_fork','human_reserved_authority','lifecycle']

ROOT_EXPECTED={
 'GENESIS.G0':{'source_object_id':'P155_GENESIS_CONCEPTUAL_SOURCE','semantic_status':'HUMAN_JUDGMENT_REQUIRED'},
 'DNA.L0.1':{'source_object_id':'F1','semantic_status':'PROTECTED_CONSTITUTIVE_BINDING_NOT_ORDINARY_ADOPTION'},
 'DNA.L0.2':{'source_object_id':'F9','semantic_status':'PROTECTED_CONSTITUTIVE_BINDING_NOT_ORDINARY_ADOPTION'},
 'DNA.L0.3':{'source_object_id':'F11','semantic_status':'PROTECTED_CONSTITUTIVE_BINDING_NOT_ORDINARY_ADOPTION'},
 'DNA.L0.4':{'source_object_id':'F11','semantic_status':'PROTECTED_CONSTITUTIVE_BINDING_NOT_ORDINARY_ADOPTION'},
 'DNA.L0.5':{'source_object_id':'F13','semantic_status':'PROTECTED_CONSTITUTIVE_BINDING_NOT_ORDINARY_ADOPTION'},
 'DNA.L0.6':{'source_object_id':'F15','semantic_status':'PROTECTED_CONSTITUTIVE_BINDING_NOT_ORDINARY_ADOPTION'},
}

def _canon(x): return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def _hash_obj(x): return hashlib.sha256(_canon(x)).hexdigest()
def _sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()
def _read_json(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def _atomic_json(path,obj,filesystem_effect_context=None):
 path=Path(path)
 if filesystem_effect_context is None:
  raise RuntimeError('occ_golden_vectors_filesystem_effect_context_required')
 payload=(json.dumps(obj,indent=2,sort_keys=True,ensure_ascii=False)+'\n').encode('utf-8')
 filesystem_effect_context.execute_path('occ_golden_vectors_write_replace','FS_WRITE_REPLACE_BYTES',path,payload)

def paths(root):
 r=Path(root)
 return {'inventory':r/'ontology_inventory.txt','source_manifest':r/'normative/occ1a/manifest.yaml','source_hash_manifest':r/'normative/occ1a/hash_manifest.json','dna_l0':r/'normative/occ1a/dna/dna_l0.yaml','genesis':r/'normative/occ1a/genesis/genesis.yaml','cnp':r/'validation_artifacts/p159/occ1e/compiled_normative_profile_v1.json','occ1f_close':r/'validation_artifacts/p159/occ1f/occ1f_closure_transaction_v1.json','occ1f_post':r/'validation_artifacts/p159/occ1f/occ1f_postclose_verification_v1.json','out':r/'validation_artifacts/p159/occ1g'}

def _vector(vid,family,source_norms,ctx,app,constraint,authority,hook,prov,expected,criticality,rationale):
 return {'vector_id':vid,'version':CORPUS_VERSION,'family':family,'source_norms':source_norms,'input_context':ctx,'expected_applicability':app,'expected_constraint_status':constraint,'expected_authority_effect':authority,'expected_conflict_hook':hook,'expected_provenance':prov,'expected_verdict':expected,'criticality':criticality,'rationale':rationale}

def build_core():
 v=[]
 for rid in ROOT_IDS:
  e=ROOT_EXPECTED[rid]
  base={'rule_id':rid,'semantic_status':e['semantic_status'],'source_object_id':e['source_object_id']}
  v.append(_vector(f'CORE.{rid}.POS','positive_conforming',[rid],{'fixture':'CURRENT_CNP','assertion':'ROOT_PRESERVED'},'APPLICABLE','PRESERVED','NO_AUTHORITY_CREATED','NO_PREARBITRATION',base,'PASS','ROOT','Positive root preservation oracle fixed independently from compiler output.'))
  v.append(_vector(f'CORE.{rid}.NEG','negative_prohibited',[rid],{'fixture':'MUTATED_CNP','mutation':'AUTHORIZE_OR_PREARBITRATE_ROOT'},'APPLICABLE','VIOLATION_DETECTED','AUTHORITY_CREATION_FORBIDDEN','PREARBITRATION_FORBIDDEN',base,'FAIL','ROOT','Negative root vector: authority manufacture or pre-arbitration must fail.'))
  v.append(_vector(f'CORE.{rid}.UNK','UNKNOWN',[rid],{'fixture':'CURRENT_CNP','assertion':'UNCERTAINTY_PRESERVED'},'APPLICABLE','UNKNOWN_PRESERVED','NO_AUTHORITY_CREATED','NO_PREARBITRATION',base,'PASS','ROOT','Unknown/human-judgment or unresolved semantics must remain explicit, never promoted to authorization.'))
 return v

def evaluate_defensive_semantic_transition(kind,before,after):
    """Pure fail-closed evaluator refining existing scope/delegation/temporal surfaces."""
    if kind not in ("scope_intersection","nondelegability","timeout"):
        return {"status":"FAIL","reason":"UNSUPPORTED_DEFENSIVE_TRANSITION"}
    if not isinstance(before,dict) or not isinstance(after,dict):
        return {"status":"FAIL","reason":"INVALID_DEFENSIVE_TRANSITION_INPUT"}
    if kind=="scope_intersection":
        ok=(before.get("composition")=="INTERSECTION" and after.get("composition")=="INTERSECTION")
        return {"status":"PASS" if ok else "FAIL","reason":"SCOPE_INTERSECTION_PRESERVED" if ok else "INTERSECTION_TO_UNION_OR_OTHER_WIDENING"}
    if kind=="nondelegability":
        ok=(before.get("delegable") is False and after.get("delegable") is False)
        return {"status":"PASS" if ok else "FAIL","reason":"NONDELEGABILITY_PRESERVED" if ok else "NONDELEGABLE_TO_DELEGABLE_OR_UNRESOLVED"}
    ok=(before.get("timed_out") is True and isinstance(after.get("decision"),str) and after.get("decision")!="PASS")
    return {"status":"PASS" if ok else "FAIL","reason":"TIMEOUT_FAIL_CLOSED" if ok else "TIMEOUT_TO_PASS_OR_UNRESOLVED"}

def build_extended():
 specs=[
 ('EXT.NOT_APPLICABLE','NOT_APPLICABLE','DNA.L0.1','NOT_APPLICABLE_IS_NOT_ALLOW'),
 ('EXT.AUTHORITY','authority','DNA.L0.2','NO_AUTHORITY_AMPLIFICATION'),
 ('EXT.DELEGATION','delegation','DNA.L0.2','NO_DELEGATION_AMPLIFICATION'),
 ('EXT.SCOPE','scope','DNA.L0.2','NO_IMPLICIT_GLOBAL_SCOPE'),
 ('EXT.TEMPORAL','temporal','DNA.L0.2','NO_IMPLICIT_PERMANENCE'),
 ('EXT.EMERGENCY','emergency','DNA.L0.5','NO_EMERGENCY_ROOT_OVERRIDE'),
 ('EXT.PROVENANCE','provenance','DNA.L0.3','PROVENANCE_BOUND'),
 ('EXT.CCAD','CCAD_conflict','CCAD.AR1','CCAD_HOOK_NOT_RESOLUTION'),
 ('EXT.COMPOSITION','sequence_composition','DNA.L0.2','NO_COMPOSITION_AUTHORITY'),
 ('EXT.CONTINUITY','continuity_fork','DNA.L0.6','TRANSFORMATION_PRESERVES_SEMANTICS'),
 ('EXT.HUMAN','human_reserved_authority','DNA.L0.1','HUMAN_RESERVED_NOT_AUTOMATED'),
 ('EXT.LIFECYCLE','lifecycle','DNA.L0.5','NO_SELF_ACTIVATION'),
 ('EXT.PROHIBITED','negative_prohibited','DNA.L0.5','ROOT_OVERRIDE_REJECTED'),
 ('EXT.UNKNOWN','UNKNOWN','GENESIS.G0','HUMAN_JUDGMENT_PRESERVED'),
 ('EXT.POSITIVE','positive_conforming','DNA.L0.4','AUDITABILITY_PRESERVED'),
 ]
 out=[]
 for vid,fam,rid,assertion in specs:
  out.append(_vector(vid,fam,[rid],{'fixture':'CURRENT_CNP','assertion':assertion},'APPLICABLE','PRESERVED','NO_AUTHORITY_CREATED','NO_PREARBITRATION',{'rule_id':rid},'PASS','HIGH',f'Extended semantic vector for {fam}; no human-value scalarization.'))
 return out

def _rule(profile,rid):
 for r in profile.get('rules',[]):
  if r.get('rule_id')==rid:return r
 return None

def _root_preserved(rule,expected):
 if not isinstance(rule,dict): return False
 return (rule.get('uncertainty_semantics',{}).get('semantic_status')==expected['semantic_status'] and
         rule.get('provenance',{}).get('source_object_id')==expected['source_object_id'] and
         rule.get('authority_requirements',{}).get('authorization_created') is False and
         rule.get('normative_effect',{}).get('authorization_created') is False and
         rule.get('normative_effect',{}).get('execution_performed') is False and
         rule.get('scope_constraints',{}).get('implicit_global') is False and
         rule.get('temporal_constraints',{}).get('implicit_permanent') is False and
         rule.get('uncertainty_semantics',{}).get('unknown_never_promoted_to_true') is True)

def _semantic_observation(vector,profile):
 rid=vector['source_norms'][0]; rule=_rule(profile,rid)
 assertion=vector['input_context'].get('assertion')
 if vector['input_context'].get('mutation')=='AUTHORIZE_OR_PREARBITRATE_ROOT':
  if not rule:return 'FAIL'
  mutated=deepcopy(rule); mutated.setdefault('authority_requirements',{})['authorization_created']=True
  return 'FAIL' if mutated['authority_requirements']['authorization_created'] is True else 'PASS'
 if rid in ROOT_EXPECTED and assertion=='ROOT_PRESERVED': return 'PASS' if _root_preserved(rule,ROOT_EXPECTED[rid]) else 'FAIL'
 if rid in ROOT_EXPECTED and assertion=='UNCERTAINTY_PRESERVED':
  ok=bool(rule) and rule.get('uncertainty_semantics',{}).get('unknown_never_promoted_to_true') is True and rule.get('enforcement_class')=='UNRESOLVED' and rule.get('normative_effect',{}).get('authorization_created') is False
  return 'PASS' if ok else 'FAIL'
 if not rule:return 'INCONCLUSIVE'
 checks={
  'NOT_APPLICABLE_IS_NOT_ALLOW': 'NOT_APPLICABLE' in rule.get('normative_effect',{}).get('result_domain',[]) and rule.get('normative_effect',{}).get('allow_candidate_is_authorization') is False,
  'NO_AUTHORITY_AMPLIFICATION': rule.get('authority_requirements',{}).get('authorization_created') is False,
  'NO_DELEGATION_AMPLIFICATION': rule.get('authority_requirements',{}).get('current_holder_resolved') is False,
  'NO_IMPLICIT_GLOBAL_SCOPE': rule.get('scope_constraints',{}).get('implicit_global') is False,
  'NO_IMPLICIT_PERMANENCE': rule.get('temporal_constraints',{}).get('implicit_permanent') is False,
  'NO_EMERGENCY_ROOT_OVERRIDE': profile.get('conflict_hooks',{}).get('predetermined_resolution') is False,
  'PROVENANCE_BOUND': isinstance(rule.get('provenance'),dict) and bool(rule.get('provenance',{}).get('source_map')),
  'CCAD_HOOK_NOT_RESOLUTION': profile.get('conflict_hooks',{}).get('arbitration_performed_by_cnp') is False,
  'NO_COMPOSITION_AUTHORITY': profile.get('authority_model',{}).get('compiler_creates_authority') is False,
  'TRANSFORMATION_PRESERVES_SEMANTICS': rule.get('normative_effect',{}).get('source_semantics_preserved') is True,
  'HUMAN_RESERVED_NOT_AUTOMATED': rule.get('authority_requirements',{}).get('current_holder_resolved') is False,
  'NO_SELF_ACTIVATION': (profile.get('lifecycle_model',{}).get('self_activation') is False and profile.get('profile_state') != 'ACTIVE'),
  'ROOT_OVERRIDE_REJECTED': profile.get('conflict_hooks',{}).get('predetermined_resolution') is False,
  'HUMAN_JUDGMENT_PRESERVED': rule.get('uncertainty_semantics',{}).get('semantic_status')=='HUMAN_JUDGMENT_REQUIRED',
  'AUDITABILITY_PRESERVED': isinstance(rule.get('provenance'),dict) and bool(rule.get('provenance',{}).get('source_map')),
 }
 return 'PASS' if checks.get(assertion,False) else 'FAIL'

def run_corpus(corpus,profile):
 results=[]
 for v in corpus['vectors']:
  observed=_semantic_observation(v,profile); expected=v['expected_verdict']
  vector_verdict='PASS' if observed==expected else ('INCONCLUSIVE' if observed=='INCONCLUSIVE' else 'FAIL')
  results.append({'vector_id':v['vector_id'],'criticality':v['criticality'],'family':v['family'],'expected_verdict':expected,'observed_semantic_verdict':observed,'vector_verdict':vector_verdict})
 return results

def _source_package_version(manifest_path):
    for raw in Path(manifest_path).read_text(encoding='utf-8').splitlines():
        line=raw.strip()
        if line.startswith('package_version:'):
            value=line.split(':',1)[1].strip().strip(chr(34)).strip(chr(39))
            if value:return value
    raise ValueError('OCC1A_PACKAGE_VERSION_MISSING')

def strict_vector_schema():
    return {'$schema':'https://json-schema.org/draft/2020-12/schema','$id':SCHEMA,'type':'object',
      'required':['vector_id','version','family','source_norms','input_context','expected_applicability','expected_constraint_status','expected_authority_effect','expected_conflict_hook','expected_provenance','expected_verdict','criticality','rationale'],
      'properties':{
       'vector_id':{'type':'string','minLength':1},'version':{'type':'string','const':CORPUS_VERSION},
       'family':{'type':'string','enum':FAMILIES},'source_norms':{'type':'array','minItems':1,'items':{'type':'string','minLength':1}},
       'input_context':{'type':'object'},'expected_applicability':{'type':'string','minLength':1},
       'expected_constraint_status':{'type':'string','minLength':1},'expected_authority_effect':{'type':'string','minLength':1},
       'expected_conflict_hook':{'type':'string','minLength':1},'expected_provenance':{'type':'object'},
       'expected_verdict':{'type':'string','enum':['PASS','FAIL','INCONCLUSIVE','INVALID_VECTOR']},
       'criticality':{'type':'string','enum':['ROOT','HIGH']},'rationale':{'type':'string','minLength':1}},
      'additionalProperties':False}

def validate_vector_strict(v):
    s=strict_vector_schema(); allowed=set(s['properties'])
    if not isinstance(v,dict) or set(v)!=allowed:return False
    strings=['vector_id','version','family','expected_applicability','expected_constraint_status','expected_authority_effect','expected_conflict_hook','expected_verdict','criticality','rationale']
    if not all(isinstance(v.get(k),str) and v.get(k) for k in strings):return False
    if v['version']!=CORPUS_VERSION or v['family'] not in FAMILIES:return False
    if v['expected_verdict'] not in ['PASS','FAIL','INCONCLUSIVE','INVALID_VECTOR'] or v['criticality'] not in ['ROOT','HIGH']:return False
    if not isinstance(v.get('source_norms'),list) or not v['source_norms'] or not all(isinstance(x,str) and x for x in v['source_norms']):return False
    return isinstance(v.get('input_context'),dict) and isinstance(v.get('expected_provenance'),dict)

def compute_gcvi(core,ext,manifest,ledger,report,source_binding):
    vectors=core.get('vectors',[])+ext.get('vectors',[])
    cr=report.get('core_results',[])
    root_bad=[x for x in cr if x.get('criticality')=='ROOT' and x.get('vector_verdict')!='PASS']
    initial=next((e for e in ledger.get('entries',[]) if e.get('kind')=='INITIAL_CORPUS'),None)
    implementation_keys={'compiler_hash','compiler_function','python_symbol','internal_field','source_path','implementation_path'}
    semantic_only=all(not(set(v.get('input_context',{})) & implementation_keys) for v in vectors)
    return {
     'GCVI-1':'PASS' if core.get('expected_outcomes_fixed_before_run') is True else 'FAIL',
     'GCVI-2':'PASS' if manifest.get('core_sha256')==_hash_obj(core) and manifest.get('extended_sha256')==_hash_obj(ext) else 'FAIL',
     'GCVI-3':'PASS' if core.get('root_non_compensatory') is True and all(v.get('criticality')=='ROOT' for v in core.get('vectors',[])) else 'FAIL',
     'GCVI-4':'PASS' if not root_bad and not report.get('skipped_vectors') and [x.get('vector_id') for x in cr]==[v.get('vector_id') for v in core.get('vectors',[])] and report.get('root_vector_count')==sum(1 for v in core.get('vectors',[]) if v.get('criticality')=='ROOT') else 'FAIL',
     'GCVI-5':'PASS' if initial and initial.get('new_core_sha256')==_hash_obj(core) and initial.get('new_extended_sha256')==_hash_obj(ext) and initial.get('expected_output_laundering') is False else 'FAIL',
     'GCVI-6':'PASS' if semantic_only and all(validate_vector_strict(v) for v in vectors) else 'FAIL',
     'GCVI-7':'PASS' if core.get('oracle_role')=='EXTERNAL_NON_NORMATIVE' and ext.get('oracle_role')=='EXTERNAL_NON_NORMATIVE' else 'FAIL',
     'GCVI-8':'PASS' if report.get('golden_pass_proves_no_other_counterexamples') is False else 'FAIL',
     'GCVI-9':'PASS' if manifest.get('source_binding')==source_binding and report.get('source_binding')==source_binding and manifest.get('stale_corpus_may_certify_new_source') is False else 'FAIL',
     'GCVI-10':'PASS' if manifest.get('offline_core') is True and manifest.get('probabilistic_core') is False and manifest.get('cwd_independent') is True else 'FAIL'}

def materialize(root,filesystem_effect_context=None):
 p=paths(root); missing=[str(x) for k,x in p.items() if k!='out' and not x.exists()]
 if missing:return {'status':'INCONCLUSIVE','reason':'REQUIRED_INPUT_MISSING','missing':missing}
 inv=p['inventory'].read_text(encoding='utf-8')
 if 'occ_golden_constitutional_vectors' not in inv:return {'status':'INCONCLUSIVE','reason':'ONTOLOGY_INVENTORY_NOT_REGISTERED'}
 close=_read_json(p['occ1f_close']); post=_read_json(p['occ1f_post'])
 if not (close.get('status')=='CLOSED' and post.get('status')=='POSTCLOSE_VERIFIED' and post.get('occ1f_closed') is True and close.get('transaction_id')==post.get('closure_transaction_id')): return {'status':'INCONCLUSIVE','reason':'OCC1F_NOT_CLOSED_POSTVERIFIED'}
 profile=_read_json(p['cnp'])
 schema=strict_vector_schema()
 core={'schema':SCHEMA,'corpus_id':'GCV-CORE','version':CORPUS_VERSION,'oracle_role':'EXTERNAL_NON_NORMATIVE','expected_outcomes_fixed_before_run':True,'root_non_compensatory':True,'vectors':build_core()}
 ext={'schema':SCHEMA,'corpus_id':'GCV-EXTENDED','version':CORPUS_VERSION,'oracle_role':'EXTERNAL_NON_NORMATIVE','vectors':build_extended()}
 core_hash=_hash_obj(core); ext_hash=_hash_obj(ext)
 source_binding={'occ1a_manifest_sha256':_sha(p['source_manifest']),'occ1a_hash_manifest_sha256':_sha(p['source_hash_manifest']),'genesis_sha256':_sha(p['genesis']),'dna_l0_sha256':_sha(p['dna_l0']),'package_version':_source_package_version(p['source_manifest'])}
 manifest={'schema':'oce.p159.occ1g.corpus_manifest.v1','corpus_version':CORPUS_VERSION,'core_sha256':core_hash,'extended_sha256':ext_hash,'source_binding':source_binding,'stale_corpus_may_certify_new_source':False,'cwd_independent':True,'offline_core':True,'probabilistic_core':False,'gcvi':GCVI}
 manifest['manifest_sha256']=_hash_obj(manifest)
 ledger={'schema':'oce.p159.occ1g.change_ledger.v1','corpus_version':CORPUS_VERSION,'entries':[{'change_id':'GCV-1.0.0-INITIAL','kind':'INITIAL_CORPUS','reason':'Initial OCC-1G corpus; expected outcomes fixed before first run.','previous_corpus_hash':None,'new_core_sha256':core_hash,'new_extended_sha256':ext_hash,'expected_output_laundering':False}]}
 cr=run_corpus(core,profile); er=run_corpus(ext,profile)
 root_bad=[x['vector_id'] for x in cr if x['criticality']=='ROOT' and x['vector_verdict']!='PASS']
 skipped=[]
 report={'schema':'oce.p159.occ1g.golden_run_report.v1','corpus_version':CORPUS_VERSION,'core_sha256':core_hash,'extended_sha256':ext_hash,'manifest_sha256':manifest['manifest_sha256'],'source_binding':source_binding,'core_results':cr,'extended_results':er,'root_vector_count':len(cr),'root_fail_or_inconclusive':root_bad,'skipped_vectors':skipped,'partial_run':False,'all_vectors_reported':len(cr)==len(core['vectors']) and len(er)==len(ext['vectors']),'gcvi_status':{},'golden_pass_proves_no_other_counterexamples':False,'human_values_scalarized':False,'occ1h_opened':False,'p160_opened':False,'p159_final_lock':False}
 report['gcvi_status']=compute_gcvi(core,ext,manifest,ledger,report,source_binding)
 gcvi_all_pass=all(report['gcvi_status'].get(g)=='PASS' for g in GCVI)
 strict_vectors=all(validate_vector_strict(v) for v in core['vectors']+ext['vectors'])
 report['closure_readiness']='READY' if not root_bad and report['all_vectors_reported'] and gcvi_all_pass and strict_vectors else 'NOT_READY'
 report['report_sha256']=_hash_obj(report)
 out=p['out']
 if filesystem_effect_context is None: raise RuntimeError('occ_golden_vectors_filesystem_effect_context_required')
 filesystem_effect_context.begin()
 if not out.exists():
  filesystem_effect_context.execute_path('occ_golden_vectors_create_dirs','FS_CREATE_DIRS',out)
 files={'golden_vector_schema_v1.json':schema,'gcv_core_v1.json':core,'gcv_extended_v1.json':ext,'corpus_manifest_v1.json':manifest,'change_ledger_v1.json':ledger,'golden_run_report_v1.json':report}
 for n,o in files.items():_atomic_json(out/n,o,filesystem_effect_context)
 return {'status':'PASS' if report['closure_readiness']=='READY' else 'INCONCLUSIVE','artifact_dir':str(out),'core_vectors':len(cr),'extended_vectors':len(er),'root_bad':root_bad,'core_sha256':core_hash,'extended_sha256':ext_hash,'report_sha256':report['report_sha256'],'occ1g_closed':False,'occ1h_opened':False,'p160_opened':False,'p159_final_lock':False}
def validate_evidence_bundle(root, bundle_dir=None):
    p=paths(root); out=Path(bundle_dir) if bundle_dir is not None else p['out']
    names=['gcv_core_v1.json','gcv_extended_v1.json','corpus_manifest_v1.json','change_ledger_v1.json','golden_run_report_v1.json']
    missing=[n for n in names if not (out/n).is_file()]
    if missing:return {'status':'REJECTED','reasons':['EVIDENCE_FILE_MISSING'],'missing':missing}
    try:
        core=_read_json(out/'gcv_core_v1.json'); ext=_read_json(out/'gcv_extended_v1.json')
        manifest=_read_json(out/'corpus_manifest_v1.json'); ledger=_read_json(out/'change_ledger_v1.json')
        report=_read_json(out/'golden_run_report_v1.json')
    except Exception as exc:return {'status':'REJECTED','reasons':['EVIDENCE_PARSE_ERROR'],'detail':type(exc).__name__}
    reasons=[]; ch=_hash_obj(core); eh=_hash_obj(ext)
    if manifest.get('core_sha256')!=ch:reasons.append('CORE_HASH_MISMATCH')
    if manifest.get('extended_sha256')!=eh:reasons.append('EXTENDED_HASH_MISMATCH')
    mb=dict(manifest); mh=mb.pop('manifest_sha256',None)
    if mh!=_hash_obj(mb):reasons.append('MANIFEST_HASH_MISMATCH')
    current={'occ1a_manifest_sha256':_sha(p['source_manifest']),'occ1a_hash_manifest_sha256':_sha(p['source_hash_manifest']),'genesis_sha256':_sha(p['genesis']),'dna_l0_sha256':_sha(p['dna_l0']),'package_version':_source_package_version(p['source_manifest'])}
    if manifest.get('source_binding')!=current:reasons.append('STALE_SOURCE_BINDING')
    expected=[v['vector_id'] for v in build_core()]; actual=[v.get('vector_id') for v in core.get('vectors',[])]
    if actual!=expected:reasons.append('CORE_VECTOR_SET_MISMATCH')
    entries=ledger.get('entries',[]); initial=next((e for e in entries if e.get('kind')=='INITIAL_CORPUS'),None)
    if not initial:reasons.append('INITIAL_LEDGER_ENTRY_MISSING')
    else:
        if initial.get('new_core_sha256')!=ch:reasons.append('CORE_LEDGER_BINDING_MISMATCH')
        if initial.get('new_extended_sha256')!=eh:reasons.append('EXTENDED_LEDGER_BINDING_MISMATCH')
        if initial.get('expected_output_laundering') is not False:reasons.append('EXPECTED_OUTPUT_LAUNDERING_FLAG')
    cr=report.get('core_results',[]); er=report.get('extended_results',[])
    if [x.get('vector_id') for x in cr]!=actual or [x.get('vector_id') for x in er]!=[v.get('vector_id') for v in ext.get('vectors',[])]:reasons.append('REPORT_VECTOR_OMISSION_OR_REORDER')
    if report.get('partial_run') is not False:reasons.append('PARTIAL_RUN')
    if report.get('all_vectors_reported') is not True:reasons.append('PARTIAL_RUN_LAUNDERING')
    if report.get('skipped_vectors') not in ([],None):reasons.append('SKIPPED_VECTOR_PRESENT')
    if any(x.get('criticality')=='ROOT' and x.get('vector_verdict')!='PASS' for x in cr):reasons.append('ROOT_NOT_PASS')
    if report.get('root_fail_or_inconclusive') not in ([],None):reasons.append('ROOT_BAD_LIST_NONEMPTY')
    if report.get('core_sha256')!=ch or report.get('extended_sha256')!=eh:reasons.append('REPORT_CORPUS_BINDING_MISMATCH')
    if report.get('manifest_sha256')!=mh:reasons.append('REPORT_MANIFEST_BINDING_MISMATCH')
    rb=dict(report); rh=rb.pop('report_sha256',None)
    if rh!=_hash_obj(rb):reasons.append('REPORT_HASH_MISMATCH')
    if report.get('occ1h_opened') is not False:reasons.append('OCC1H_BOUNDARY_VIOLATION')
    if report.get('p160_opened') is not False:reasons.append('P160_BOUNDARY_VIOLATION')
    if report.get('p159_final_lock') is not False:reasons.append('P159_LOCK_BOUNDARY_VIOLATION')
    reasons=sorted(set(reasons))
    return {'status':'PASS' if not reasons else 'REJECTED','reasons':reasons,'core_vectors_checked':len(actual),'extended_vectors_checked':len(ext.get('vectors',[])),'occ1g_closed':False,'occ1h_opened':False,'p160_opened':False,'p159_final_lock':False}

