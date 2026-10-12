from __future__ import annotations
import json, shutil
from pathlib import Path
from ontology import occ_independent_constitutional_verifier as v

ROOT = Path(__file__).resolve().parents[1]

def _sandbox(tmp_path):
    dst = tmp_path / "repo"
    for src in v.paths(ROOT).values():
        if not src.exists(): continue
        target = dst / src.relative_to(ROOT)
        if src.is_dir(): shutil.copytree(src, target)
        else:
            target.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(src, target)
    return dst

def _mutate(root, fn):
    p=v.paths(root)["profile"]; x=json.loads(p.read_text()); fn(x)
    p.write_text(json.dumps(x,indent=2,sort_keys=True)+"\n")

def test_canonical_ivi_registry_exact():
    r=v.verify(ROOT)
    ids=[f["check_id"] for f in r["findings"] if f["check_id"].startswith("IVI-")]
    assert ids == ["IVI-%d"%i for i in range(1,13)]
    assert r["legacy_upstream_states_used_as_verdict_oracle"] is False
    assert r["historical_s3_s4_s7_recalculated"] is True

def test_real_state_has_no_unresolved_canonical_ivi():
    r=v.verify(ROOT)
    assert r["checks_failed"] == 0
    assert r["checks_inconclusive"] == 0
    f=next(x for x in r["findings"] if x["check_id"]=="IVI-5")
    assert f["status"]=="PASS"
    assert f["evidence"]["full_natural_language_equivalence_claimed"] is False

def test_missing_source_norm_rejected(tmp_path):
    root=_sandbox(tmp_path); _mutate(root, lambda x: x["rules"].pop())
    r=v.verify(root); assert r["verdict"]==v.REJECTED and "IVI-3" in r["failed_check_ids"]

def test_extra_unsourced_rule_rejected(tmp_path):
    root=_sandbox(tmp_path)
    def m(x):
        z=dict(x["rules"][0]); z["rule_id"]="FAKE.EXTRA"; z["source_norm_ids"]=[]; x["rules"].append(z)
    _mutate(root,m); r=v.verify(root)
    assert r["verdict"]==v.REJECTED and "IVI-4" in r["failed_check_ids"]

def test_scope_widening_rejected(tmp_path):
    root=_sandbox(tmp_path); _mutate(root,lambda x:x["rules"][0]["scope_constraints"].update({"implicit_global":True}))
    assert "IVI-6" in v.verify(root)["failed_check_ids"]

def test_temporal_permanence_rejected(tmp_path):
    root=_sandbox(tmp_path); _mutate(root,lambda x:x["rules"][0]["temporal_constraints"].update({"implicit_permanent":True}))
    assert "IVI-6" in v.verify(root)["failed_check_ids"]

def test_root_arbitrability_rejected(tmp_path):
    root=_sandbox(tmp_path)
    def m(x):
        next(r for r in x["rules"] if r["rule_id"]=="DNA.L0.1")["normative_effect"]["arbitrated"]=True
    _mutate(root,m); assert "IVI-7" in v.verify(root)["failed_check_ids"]

def test_fake_runtime_reachability_rejected(tmp_path):
    root=_sandbox(tmp_path)
    def m(x):
        b=next(iter(x["enforcement_map"]["rule_bindings"].values()))
        b["runtime_reachability_proven"]=True; b["consumers"]=[]
    _mutate(root,m); assert "IVI-10" in v.verify(root)["failed_check_ids"]

def test_semantic_preservation_false_rejected(tmp_path):
    root=_sandbox(tmp_path); _mutate(root,lambda x:x["rules"][0]["normative_effect"].update({"source_semantics_preserved":False}))
    assert "IVI-5" in v.verify(root)["failed_check_ids"]

def test_declared_hash_tamper_rejected(tmp_path):
    root=_sandbox(tmp_path); _mutate(root,lambda x:x.update({"artifact_hash":"0"*64}))
    assert "IVI-1" in v.verify(root)["failed_check_ids"]

def test_missing_input_indeterminate(tmp_path):
    root=_sandbox(tmp_path); v.paths(root)["occ1d_coverage"].unlink()
    assert v.verify(root)["verdict"]==v.INDETERMINATE

def test_determinism():
    assert v.verify(ROOT)==v.verify(ROOT)


def test_runtime_boundaries_are_disclosed_not_promoted():
    r=v.verify(ROOT)
    assert "BOUND-S8" not in r["inconclusive_check_ids"]
    assert any(x["boundary_id"]=="S8" and x["blocks_occ1f_verdict"] is False for x in r["declared_boundaries"])
    assert r["runtime_reachability_proven"] is False
    assert r["runtime_composition_proven"] is False

def test_ivi10_is_about_partial_reporting_not_future_p160():
    r=v.verify(ROOT)
    f=next(x for x in r["findings"] if x["check_id"]=="IVI-10")
    assert f["status"]=="PASS"
    assert f["evidence"]["runtime_reachability_proven"] is False

def test_ivi5_never_claims_full_f0_f1_f2_equivalence():
    r=v.verify(ROOT)
    f=next(x for x in r["findings"] if x["check_id"]=="IVI-5")
    assert f["status"]=="PASS"
    assert f["evidence"]["full_natural_language_equivalence_claimed"] is False
    assert "without claiming full F0/F1/F2 natural-language equivalence" in f["reason"]

def _rehash_profile(x):
    payload=dict(x); payload.pop("artifact_hash",None)
    x["artifact_hash"]=v._canonical_hash(payload)

def test_ivi5_strengthening_visible_even_when_profile_rehashed(tmp_path):
    root=_sandbox(tmp_path)
    def m(x):
        x["rules"][0]["normative_effect"]["result_domain"].remove("ALLOW_CANDIDATE")
        _rehash_profile(x)
    _mutate(root,m)
    r=v.verify(root)
    assert r["verdict"]==v.REJECTED
    assert "IVI-5" in r["failed_check_ids"]

def test_ivi5_weakening_visible_even_when_profile_rehashed(tmp_path):
    root=_sandbox(tmp_path)
    def m(x):
        x["rules"][0]["normative_effect"]["result_domain"].append("ALLOW_EXECUTION")
        _rehash_profile(x)
    _mutate(root,m)
    r=v.verify(root)
    assert r["verdict"]==v.REJECTED
    assert "IVI-5" in r["failed_check_ids"]
