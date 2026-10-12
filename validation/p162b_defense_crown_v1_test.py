from copy import deepcopy
import ast
from pathlib import Path
import pytest
import validation.p162b_capability_identity_registry_binding_v1_test as _baseline
fixture = _baseline.fx
from ontology.capability_binding_assessor import (
    assess_binding, build_manifest, build_registry_entry, build_runtime_attestation,
    build_effector_registry, technical_permission_profile, capability_set, manifest as assessor_manifest
)
from ontology.effect_closure_builder import build_effect_closure, manifest as closure_manifest

def call(x, *, continuity=True, current_set=None, impl_hash="impl-hash"):
    i,e,m,d,er,p,a,cs=x
    return assess_binding(
        invocation=i, registry_entry=e, manifest=m,
        actual_implementation_hash=impl_hash, actual_permissions=p,
        dependency_catalog=d, effector_registry=er, attestation=a,
        expected_capability_set=cs,
        current_capability_set=cs if current_set is None else current_set,
        registry_continuity=continuity)

def rebind_manifest(x):
    i,e,m,d,er,p,a,cs=x
    m2=build_manifest({k:v for k,v in m.items() if k!="manifest_hash"})
    x=list(x); x[2]=m2
    e=dict(e); e["manifest_hash"]=m2["manifest_hash"]; e["semantic_fingerprint"]=__import__(
        "ontology.capability_binding_assessor",fromlist=["semantic_fingerprint"]).semantic_fingerprint(m2)
    e=build_registry_entry({k:v for k,v in e.items() if k!="entry_hash"}); x[1]=e
    i=dict(i); i["capability_manifest_hash"]=m2["manifest_hash"]; x[0]=i
    c=build_effect_closure(m2,d)
    a=dict(a); a["manifest_hash"]=m2["manifest_hash"]; a["dependency_snapshot_hash"]=c["dependency_snapshot_hash"]
    a=build_runtime_attestation({k:v for k,v in a.items() if k!="attestation_hash"}); x[6]=a
    x[7]=capability_set([e],"1")
    return x

# B-1..B-4 identity/version/implementation/manifest binding
@pytest.mark.parametrize("field,value",[
 ("capability_id","cap.other"),("capability_version","2"),("capability_implementation_id","impl.other")])
def test_B01_B03_identity_version_implementation(field,value):
    x=list(fixture()); x[0]=dict(x[0]); x[0][field]=value
    assert call(x)["verification_status"]!="BOUND_VERIFIED"

def test_B4_manifest_bound_to_implementation():
    x=list(fixture()); x[2]=dict(x[2]); x[2]["risk_metadata"]="drift"
    assert call(x)["verification_status"]!="BOUND_VERIFIED"

# B-5/B-6 effects are not self-proof; UNKNOWN never PURE
@pytest.mark.parametrize("effect",["UNKNOWN","UNRESOLVED","INCONCLUSIVE",""])
def test_B5_B6_unknown_effect_never_positive(effect):
    x=list(fixture()); x[2]=dict(x[2]); x[2]["effects"]=[effect]; x=rebind_manifest(x)
    assert call(x)["verification_status"]=="EFFECT_PROFILE_UNDETERMINED"

# B-7/B-8 technical permissions do not authorize and excess is detected
def test_B7_technical_power_is_not_authorization():
    r=call(fixture())
    assert r["technical_power_is_authorization"] is False
    assert r["authorization_created"] is False and r["execution_performed"] is False

def test_B8_permission_excess_detected():
    x=list(fixture()); x[5]=deepcopy(x[5]); x[5]["flat_permissions"].append("shell")
    assert call(x)["verification_status"]=="PERMISSION_MISMATCH"

# B-9/B-10 effectful dependency closure and no transitive authorization
def test_B9_missing_effectful_dependency_fails():
    x=list(fixture()); x[3]=dict(x[3]); x[3].pop("svc.echo")
    assert call(x)["verification_status"]=="DEPENDENCY_MISMATCH"

def test_B10_parent_does_not_authorize_dependency():
    x=fixture(); c=build_effect_closure(x[2],x[3])
    assert c["parent_authorization_inherited"] is False

# B-11 drift / B-12 quarantine / B-13 capability-set expansion
def test_B11_material_drift_requires_failure():
    x=list(fixture()); x[3]=deepcopy(x[3]); x[3]["svc.echo"]["implementation_hash"]="drift"
    assert call(x)["verification_status"]!="BOUND_VERIFIED"

@pytest.mark.parametrize("state",["QUARANTINED","REVOKED","INVALIDATED","SUSPENDED"])
def test_B12_nonactive_registry_state_blocks(state):
    x=list(fixture()); x[1]=dict(x[1]); x[1]["registry_status"]=state
    assert call(x)["verification_status"]!="BOUND_VERIFIED"

def test_B13_capability_set_expansion_not_inherited():
    x=fixture(); e2=build_registry_entry({**x[1],"capability_id":"cap.extra"})
    cs2=capability_set([x[1],e2],"2")
    assert call(x,current_set=cs2)["verification_status"]!="BOUND_VERIFIED"

# B-14 registry forks cannot permissively merge
def test_B14_registry_fork_uncertain_never_passes():
    assert call(fixture(),continuity=False)["verification_status"]=="REGISTRY_CONTINUITY_UNCERTAIN"

# B-15 explicit gate coverage
@pytest.mark.parametrize("status",["UNGATED","UNKNOWN"])
def test_B15_production_effectors_must_be_gated(status):
    x=list(fixture()); x[4]=deepcopy(x[4]); x[4]["effectors"][0]["status"]=status
    assert call(x)["verification_status"]=="DEPENDENCY_MISMATCH"

def test_B15_unregistered_effector_blocks():
    x=list(fixture()); x[4]=deepcopy(x[4]); x[4]["effectors"]=[]
    assert call(x)["verification_status"]=="DEPENDENCY_MISMATCH"

# B-16 self registration/verification/activation cannot manufacture trust
def test_B16_verification_is_non_sovereign():
    r=call(fixture())
    assert r["registry_is_authority"] is False
    assert r["self_registration_trusted"] is False
    assert r["self_verification_trusted"] is False
    assert r["self_activation_trusted"] is False

# B-17 runtime attestation binds actual instance
@pytest.mark.parametrize("field,value",[
 ("runtime_instance_id","other"),("capability_id","other"),("version","2"),
 ("implementation_hash","other"),("environment","TEST")])
def test_B17_runtime_attestation_binding(field,value):
    x=list(fixture()); x[6]=dict(x[6]); x[6][field]=value
    assert call(x)["verification_status"]!="BOUND_VERIFIED"

# B-18 P162-B cannot authorize/access/execute
def test_B18_no_authorization_capability_access_or_execution():
    r=call(fixture())
    assert r["authorization_created"] is False
    assert r["capability_accessed"] is False
    assert r["execution_performed"] is False
    assert assessor_manifest()["p162c_opened"] is False
    assert closure_manifest()["execution_performed"] is False

# B-01..B-13 explicit defense matrix
def test_B01_identity_substitution(): 
    x=list(fixture()); x[0]=dict(x[0]); x[0]["capability_id"]="other"; assert call(x)["verification_status"]!="BOUND_VERIFIED"
def test_B02_version_substitution():
    x=list(fixture()); x[0]=dict(x[0]); x[0]["capability_version"]="999"; assert call(x)["verification_status"]!="BOUND_VERIFIED"
def test_B03_manifest_drift():
    x=list(fixture()); x[2]=dict(x[2]); x[2]["operations"]=["other"]; assert call(x)["verification_status"]!="BOUND_VERIFIED"
def test_B04_permission_widening():
    x=list(fixture()); x[5]=deepcopy(x[5]); x[5]["flat_permissions"]+=["shell"]; assert call(x)["verification_status"]!="BOUND_VERIFIED"
def test_B05_network_subprocess_hidden_effect():
    x=list(fixture()); x[5]=deepcopy(x[5]); x[5]["processes"]=["/bin/sh"]; x[5]["flat_permissions"]+=["shell"]; assert call(x)["verification_status"]!="BOUND_VERIFIED"
def test_B06_dependency_drift():
    x=list(fixture()); x[3]=deepcopy(x[3]); x[3]["svc.echo"]["version"]="2"; assert call(x)["verification_status"]!="BOUND_VERIFIED"
def test_B07_self_registration_cannot_grant():
    r=call(fixture()); assert not r["self_registration_trusted"] and not r["authorization_created"]
def test_B08_provider_backend_drift():
    x=list(fixture()); x[3]=deepcopy(x[3]); x[3]["svc.echo"]["provider_id"]="other"; assert call(x)["verification_status"]!="BOUND_VERIFIED"
def test_B09_stale_or_wrong_attestation_instance():
    x=list(fixture()); x[6]=dict(x[6]); x[6]["runtime_instance_id"]="stale"; assert call(x)["verification_status"]!="BOUND_VERIFIED"
def test_B10_test_prod_substitution():
    x=list(fixture()); x[6]=dict(x[6]); x[6]["environment"]="TEST"; assert call(x)["verification_status"]!="BOUND_VERIFIED"
def test_B11_capability_set_expansion():
    x=fixture(); e2=build_registry_entry({**x[1],"capability_id":"new"}); assert call(x,current_set=capability_set([x[1],e2],"2"))["verification_status"]!="BOUND_VERIFIED"
def test_B12_quarantine_bypass():
    x=list(fixture()); x[1]=dict(x[1]); x[1]["registry_status"]="QUARANTINED"; assert call(x)["verification_status"]!="BOUND_VERIFIED"
def test_B13_unknown_to_pure_forbidden():
    x=list(fixture()); x[2]=dict(x[2]); x[2]["effects"]=["UNKNOWN"]; x=rebind_manifest(x); assert call(x)["verification_status"]!="BOUND_VERIFIED"

# ROOT-B1..ROOT-B5
def test_ROOT_B1_unregistered_effector_execution_blocked():
    x=list(fixture()); x[4]=deepcopy(x[4]); x[4]["effectors"]=[]; assert call(x)["verification_status"]!="BOUND_VERIFIED"
def test_ROOT_B2_implementation_substitution_blocked():
    assert call(fixture(),impl_hash="substituted")["verification_status"]!="BOUND_VERIFIED"
def test_ROOT_B3_undeclared_effect_path_blocked():
    x=list(fixture()); x[5]=deepcopy(x[5]); x[5]["flat_permissions"]+=["shell"]; assert call(x)["verification_status"]!="BOUND_VERIFIED"
def test_ROOT_B4_technical_permission_bypass_blocked():
    x=list(fixture()); x[5]=deepcopy(x[5]); x[5]["flat_permissions"]+=["root"]; assert call(x)["verification_status"]!="BOUND_VERIFIED"
def test_ROOT_B5_post_authorization_capability_expansion_blocked():
    x=fixture(); e2=build_registry_entry({**x[1],"capability_id":"post.auth"}); assert call(x,current_set=capability_set([x[1],e2],"2"))["verification_status"]!="BOUND_VERIFIED"

# Canonical mutations to kill
def test_MUT_remove_implementation_hash_check():
    assert call(fixture(),impl_hash="mutant")["verification_status"]!="BOUND_VERIFIED"
def test_MUT_ignore_manifest_mismatch():
    x=list(fixture()); x[2]=dict(x[2]); x[2]["risk_metadata"]="mutant"; assert call(x)["verification_status"]!="BOUND_VERIFIED"
def test_MUT_disable_dependency_closure():
    x=list(fixture()); x[3]={}; assert call(x)["verification_status"]!="BOUND_VERIFIED"
def test_MUT_unknown_effect_to_pure():
    x=list(fixture()); x[2]=dict(x[2]); x[2]["effects"]=["UNKNOWN"]; x=rebind_manifest(x); assert call(x)["verification_status"]!="BOUND_VERIFIED"
def test_MUT_ignore_permission_excess():
    x=list(fixture()); x[5]=deepcopy(x[5]); x[5]["flat_permissions"]+=["shell"]; assert call(x)["verification_status"]!="BOUND_VERIFIED"
def test_MUT_quarantine_treated_active():
    x=list(fixture()); x[1]=dict(x[1]); x[1]["registry_status"]="QUARANTINED"; assert call(x)["verification_status"]!="BOUND_VERIFIED"
def test_MUT_test_attestation_accepted_in_prod():
    x=list(fixture()); x[6]=dict(x[6]); x[6]["environment"]="TEST"; assert call(x)["verification_status"]!="BOUND_VERIFIED"
def test_MUT_registry_fork_newest_timestamp_wins():
    assert call(fixture(),continuity=False)["verification_status"]!="BOUND_VERIFIED"
def test_MUT_self_registration_self_verification():
    r=call(fixture()); assert not r["self_registration_trusted"] and not r["self_verification_trusted"]
def test_MUT_ignore_capability_set_expansion():
    x=fixture(); e2=build_registry_entry({**x[1],"capability_id":"expanded"}); assert call(x,current_set=capability_set([x[1],e2],"2"))["verification_status"]!="BOUND_VERIFIED"

# Determinism, non-mutation, and implementation surface boundaries
def test_determinism_100_replays():
    x=fixture(); hs=[call(x)["binding_receipt_hash"] for _ in range(100)]; assert len(set(hs))==1
def test_inputs_not_mutated():
    x=fixture(); before=deepcopy(x); call(x); assert x==before
def test_no_execution_or_external_io_imports():
    root=Path.home()/"open-cognitive-ecology"
    for rel in ("ontology/capability_binding_assessor.py","ontology/effect_closure_builder.py"):
        tree=ast.parse((root/rel).read_text())
        names=set()
        for n in ast.walk(tree):
            if isinstance(n,ast.Import): names.update(a.name.split(".")[0] for a in n.names)
            elif isinstance(n,ast.ImportFrom) and n.module: names.add(n.module.split(".")[0])
        assert not names.intersection({"subprocess","socket","requests","urllib","http","shutil"})
def test_doctrinal_laws_present():
    laws=set(assessor_manifest()["laws"])
    assert {"DECLARED_CAPABILITY!=ACTUAL_CAPABILITY","ACTUAL_TECHNICAL_POWER!=AUTHORIZATION",
            "REGISTRY!=AUTHORITY","DISCOVERY!=REGISTRATION!=VERIFICATION!=ACTIVATION",
            "UNKNOWN_EFFECT!=PURE"}.issubset(laws)
