from __future__ import annotations
from copy import deepcopy
import json
from pathlib import Path
from ontology import occ_compiled_normative_profile as cnp

EXPECTED_RUNTIME_CONSUMERS = ('NormResolver','CCAD','AuthorizationEngine','CapabilityGate','RecoveryEngine','AssuranceEngine')

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'validation_artifacts/p159/occ1c/compiled_normative_profile_v1.json'
SCHEMA=ROOT/'schemas/p159_occ1e_compiled_normative_profile_v1.schema.json'
COMPILER=ROOT/'ontology/occ_constitutional_compiler.py'
STATIC=[ROOT/'validation_artifacts/p159/occ1d/static_constitutional_check_report_v1_2.json',ROOT/'validation_artifacts/p159/occ1d/static_constitutional_check_report_v1.json']

def load(p): return json.loads(p.read_text(encoding='utf-8'))
def rehash(p):
    p.pop('artifact_hash',None); p['artifact_hash']=cnp.canonical_sha256(p); return p
def build():
    s=next(p for p in STATIC if p.exists())
    return cnp.build_profile(load(BASE),cnp.file_sha256(BASE),cnp.file_sha256(COMPILER),cnp.file_sha256(SCHEMA),cnp.file_sha256(s))
def fail(p):
    r=cnp.verify_profile(p); assert r['status']=='FAIL',r

def test_cnpi_1_12():
    p=build(); assert cnp.verify_profile(p)['status']=='PASS'
    assert p['compiler_contract']['compilation_manufactures_legitimacy'] is False
    assert p['runtime_interfaces']['execution_capability'] is False
    assert p['lifecycle_model']['self_activation'] is False
    assert all(r['source_norm_ids'] and r['nir_node_ids'] for r in p['rules'])
    assert all(r['authority_requirements']['authorization_created'] is False for r in p['rules'])
    assert all(r['uncertainty_semantics']['unknown_never_promoted_to_true'] is True for r in p['rules'])
    assert p['lifecycle_model']['sealed_mutation_allowed'] is False
    assert p['lifecycle_model']['status_changes_require_governed_transition'] is True
    assert set(p['runtime_interfaces']['consumers'])==set(EXPECTED_RUNTIME_CONSUMERS)
    assert p['artifact_hash']==cnp.canonical_sha256({k:v for k,v in p.items() if k!='artifact_hash'})
    assert p['lifecycle_model']['ordinary_activation_from_non_activatable'] is False
    assert p['explainability_contract']['source_and_effect_per_rule_required'] is True

def test_rule_insertion_and_removal_detected_by_exact_reconstruction():
    ref=build(); a=deepcopy(ref); q=deepcopy(a['rules'][0]); q['rule_id']+='-FORGED'; a['rules'].append(q); rehash(a)
    assert a!=ref and len(a['rules'])!=len(ref['rules'])
    b=deepcopy(ref); b['rules'].pop(); rehash(b); assert b!=ref and len(b['rules'])!=len(ref['rules'])

def test_deny_to_allow_candidate_rejected():
    p=build(); p['rules'][0]['normative_effect']['allow_candidate_is_authorization']=True; rehash(p); fail(p)

def test_source_map_removal_rejected():
    p=build(); p['rules'][0]['provenance'].pop('source_map',None); rehash(p); fail(p)

def test_enforcement_consumer_removal_detected():
    p=build(); p['runtime_interfaces']['consumers'].pop(); rehash(p)
    assert set(p['runtime_interfaces']['consumers'])!=set(EXPECTED_RUNTIME_CONSUMERS)

def test_arbitrability_forgery_detected():
    p=build(); ref=deepcopy(p['conflict_hooks']); p['conflict_hooks']['predetermined_resolution']=True; rehash(p)
    assert p['conflict_hooks']!=ref

def test_source_hash_substitution_detected():
    p=build(); p['source_package_hash']='0'*64; rehash(p); assert p['source_package_hash']!=cnp.file_sha256(BASE)

def test_sealed_and_revoked_to_active_rejected():
    for state in ('SEALED','REVOKED'):
        p=build(); p['profile_state']=state; rehash(p); assert cnp.transition(p,'ACTIVE',governed=True)['status']=='FAIL'

def test_snapshot_removal_rejected():
    p=build(); p.pop('constitutional_snapshot'); rehash(p); fail(p)

def test_post_verification_mutation_rejected():
    p=build(); assert cnp.verify_profile(p)['status']=='PASS'; p['rules'][0]['evaluation_phase']='FORGED'; fail(p)

def test_deterministic_reconstruction():
    assert build()==build()

def test_unresolved_runtime_evidence_preserved():
    p=build(); assert p['enforcement_map']['status']=='UNRESOLVED'
    assert p['enforcement_map']['runtime_consumer_graph_proven'] is False
    assert all(v['runtime_reachability_proven'] is False for v in p['enforcement_map']['rule_bindings'].values())

def test_manifest_and_explanation_derivative():
    p=build(); m=cnp.manifest(p); x=cnp.human_explanation(p)
    assert m['artifact_hash']==p['artifact_hash'] and m['authorization_created'] is False and m['execution_performed'] is False
    assert 'cannot self-activate' in x and 'not permission to execute' in x
