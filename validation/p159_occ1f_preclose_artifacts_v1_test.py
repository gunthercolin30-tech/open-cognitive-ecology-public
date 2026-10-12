from __future__ import annotations
import hashlib, json, os, shutil
from pathlib import Path
from ontology import occ_independent_constitutional_verification_report as r
from ontology import occ_independent_constitutional_verifier as v
ROOT=Path(__file__).resolve().parents[1]
HISTORICAL_BUILDER_SHA="0ae2b0e5728f1db3b9a07cdef16fd553a5a9e45efaf68fe6dee82e797a1d35b4"

def _sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def _historical_builder_source():
    for p in (
        ROOT/"ontology/occ_normative_ir_real_builder.py.bak",
        ROOT/"ontology/occ_normative_ir_real_builder.py.bak8",
        ROOT/"ontology/occ_normative_ir_real_builder.py.bak10",
    ):
        if p.is_file() and _sha(p)==HISTORICAL_BUILDER_SHA:
            return p
    raise RuntimeError("OCC1F_HISTORICAL_BUILDER_FIXTURE_MISSING")

def _sandbox(tmp_path):
    dst=tmp_path/"repo"
    for src in v.paths(ROOT).values():
        if not src.exists(): continue
        target=dst/src.relative_to(ROOT)
        if src.is_dir(): shutil.copytree(src,target)
        else: target.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,target)
    for rel in ("ontology/occ_independent_constitutional_verifier.py","ontology/occ_normative_ir.py","validation_artifacts/p159/occ1f/verifier_identity_authorization_anchor_v1.json","oif_review/campaigns/P159-OCC1A/occ1a_initial_development_authority_materialization.json"):
        src=ROOT/rel; target=dst/rel; target.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,target)
    target=dst/"ontology/occ_normative_ir_real_builder.py"; target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(_historical_builder_source(),target)
    assert _sha(target)==HISTORICAL_BUILDER_SHA
    return dst

def test_real_preclose_artifacts_build_verified():
    d=r.diagnose_preclose_binding(ROOT)
    assert d["identity_anchor_valid"] is True
    assert d["legacy_builder_epoch_drift"] is True
    assert d["correction_installation_status"]=="ANCHOR_VALID_LEGACY_PRECLOSE_DRIFT_SEPARATED"

def test_preclose_deterministic():
    assert r.diagnose_preclose_binding(ROOT)==r.diagnose_preclose_binding(ROOT)

def test_materialization_idempotent_and_bound(tmp_path):
    root=_sandbox(tmp_path); a=r.materialize_preclose_evidence(root)
    b1=(root/r.COMMON_TCB_REL).read_bytes(); b2=(root/r.CHECK_REGISTRY_REL).read_bytes()
    b=r.materialize_preclose_evidence(root)
    assert a==b and b1==(root/r.COMMON_TCB_REL).read_bytes() and b2==(root/r.CHECK_REGISTRY_REL).read_bytes()
    assert r.verify_preclose_evidence(root)["status"]=="VERIFIED_PRECLOSE_BINDING"

def test_common_tcb_artifact_tamper_rejected(tmp_path):
    root=_sandbox(tmp_path); r.materialize_preclose_evidence(root)
    p=root/r.COMMON_TCB_REL; x=json.loads(p.read_text()); x["components"][0]["file_sha256"]="0"*64
    p.write_text(json.dumps(x,sort_keys=True)+"\n")
    assert r.verify_preclose_evidence(root)["status"]=="REJECTED"

def test_registry_artifact_tamper_rejected(tmp_path):
    root=_sandbox(tmp_path); r.materialize_preclose_evidence(root)
    p=root/r.CHECK_REGISTRY_REL; x=json.loads(p.read_text()); x["checks"][0]["executed_status"]="FAIL"
    p.write_text(json.dumps(x,sort_keys=True)+"\n")
    assert r.verify_preclose_evidence(root)["status"]=="REJECTED"

def test_tcb_implementation_drift_rejected(tmp_path):
    root=_sandbox(tmp_path); r.materialize_preclose_evidence(root)
    p=root/"ontology"/"occ_normative_ir.py"; p.write_text(p.read_text()+"\n# drift\n")
    assert r.verify_preclose_evidence(root)["status"]=="REJECTED"

def test_post_verification_profile_mutation_rejected(tmp_path):
    root=_sandbox(tmp_path); r.materialize_preclose_evidence(root)
    p=v.paths(root)["profile"]; x=json.loads(p.read_text()); x["rules"][0]["normative_effect"]["result_domain"].append("POST_VERIFY_MUTATION")
    p.write_text(json.dumps(x,indent=2,sort_keys=True)+"\n")
    assert r.verify_preclose_evidence(root)["status"]=="REJECTED"

def test_cwd_independence(tmp_path):
    root=_sandbox(tmp_path); old=Path.cwd(); elsewhere=tmp_path/"elsewhere"; elsewhere.mkdir()
    try:
        os.chdir(elsewhere); r.materialize_preclose_evidence(root)
        assert r.verify_preclose_evidence(root)["status"]=="VERIFIED_PRECLOSE_BINDING"
    finally: os.chdir(old)

def test_no_authority_or_downstream_opening():
    t=json.loads((ROOT/r.COMMON_TCB_REL).read_text())
    g=json.loads((ROOT/r.CHECK_REGISTRY_REL).read_text())
    assert t["authorization_created"] is False and t["authority_activated"] is False and t["execution_performed"] is False
    assert g["registry_is_authority"] is False and g["registry_can_activate"] is False
    for x in (t,g):
        assert x["occ1f_closed"] is False and x["occ1g_opened"] is False and x["p160_opened"] is False and x["p159_final_lock"] is False

# OCC1I_F4G2_3D_DM047_TEST_SURFACE_REFINEMENT
def test_occ1i_dm047_exact_post_change_control_surface(tmp_path):
    root=_sandbox(tmp_path)
    r.materialize_preclose_evidence(root)
    before=r.verify_preclose_evidence(root)
    assert before["status"]=="VERIFIED_PRECLOSE_BINDING"
    p=v.paths(root)["profile"]
    x=json.loads(p.read_text())
    x["rules"][0]["normative_effect"]["result_domain"].append("OCC1I_DM047_POST_CHANGE")
    p.write_text(json.dumps(x,indent=2,sort_keys=True)+"\\n")
    after=r.verify_preclose_evidence(root)
    assert after["status"]=="REJECTED"
    assert after["reason"] in ("COMMON_TCB_SOURCE_DRIFT_OR_TAMPER","CHECK_REGISTRY_SOURCE_DRIFT_OR_TAMPER","PRECLOSE_SOURCE_RECALCULATION_FAILED")
