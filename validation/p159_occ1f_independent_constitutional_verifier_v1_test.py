from __future__ import annotations

import json
import shutil
from pathlib import Path
from ontology import occ_independent_constitutional_verifier as v

ROOT = Path(__file__).resolve().parents[1]

def test_current_real_state_is_verified_after_occ1f_closure():
    # Current-state assertion: OCC-1F was subsequently closed and post-close verified.
    # Historical INDETERMINATE behaviour remains covered by degradation tests.
    r = v.verify(ROOT)
    assert r["verdict"] == v.VERIFIED, r
    assert r["checks_failed"] == 0, r
    assert r["checks_inconclusive"] == 0, r
    assert r["inconclusive_check_ids"] == [], r
    # The verifier verifies conformity; it does not itself declare milestone closure.
    assert r["occ1f_closed"] is False, r
    assert r["occ1g_opened"] is False, r
    assert r["p160_opened"] is False, r
    assert r["p159_final_lock"] is False, r

def test_ivi_1_to_12_are_executed():
    r = v.verify(ROOT)
    ids = {x["check_id"] for x in r["findings"]}
    assert {"IVI-%d" % i for i in range(1,13)}.issubset(ids)

def test_determinism():
    assert v.verify(ROOT) == v.verify(ROOT)

def _sandbox(tmp_path):
    dst = tmp_path / "repo"
    for key, src in v.paths(ROOT).items():
        target = dst / src.relative_to(ROOT)
        if src.is_dir():
            shutil.copytree(src, target)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, target)
    # verifier imports these two modules from the real package at test runtime;
    # source data are sandboxed, while code identity is covered by Common-TCB.
    return dst

def test_rule_removal_is_rejected(tmp_path):
    root = _sandbox(tmp_path)
    p = v.paths(root)["profile"]
    x = json.loads(p.read_text())
    x["rules"] = x["rules"][:-1]
    p.write_text(json.dumps(x, indent=2, sort_keys=True) + "\n")
    r = v.verify(root)
    assert r["verdict"] == v.REJECTED
    assert "IVI-1" in r["failed_check_ids"] or "IVI-5" in r["failed_check_ids"]

def test_source_map_removal_is_rejected(tmp_path):
    root = _sandbox(tmp_path)
    p = v.paths(root)["profile"]
    x = json.loads(p.read_text())
    x["rules"][0]["source_norm_ids"] = []
    p.write_text(json.dumps(x, indent=2, sort_keys=True) + "\n")
    r = v.verify(root)
    assert r["verdict"] == v.REJECTED
    assert "IVI-4" in r["failed_check_ids"]

def test_authorization_manufacture_is_rejected(tmp_path):
    root = _sandbox(tmp_path)
    p = v.paths(root)["profile"]
    x = json.loads(p.read_text())
    x["compiler_contract"]["authorization_created"] = True
    p.write_text(json.dumps(x, indent=2, sort_keys=True) + "\n")
    r = v.verify(root)
    assert r["verdict"] == v.REJECTED
    assert "IVI-11" in r["failed_check_ids"]

def test_scope_field_removal_is_rejected(tmp_path):
    root = _sandbox(tmp_path)
    p = v.paths(root)["profile"]
    x = json.loads(p.read_text())
    x["rules"][0].pop("scope_constraints", None)
    p.write_text(json.dumps(x, indent=2, sort_keys=True) + "\n")
    r = v.verify(root)
    assert r["verdict"] == v.REJECTED
    assert "IVI-6" in r["failed_check_ids"]

def test_self_activation_is_rejected(tmp_path):
    root = _sandbox(tmp_path)
    p = v.paths(root)["profile"]
    x = json.loads(p.read_text())
    x["lifecycle_model"]["self_activation"] = True
    p.write_text(json.dumps(x, indent=2, sort_keys=True) + "\n")
    r = v.verify(root)
    assert r["verdict"] == v.REJECTED
    assert "IVI-11" in r["failed_check_ids"]

def test_missing_required_input_is_indeterminate(tmp_path):
    root = _sandbox(tmp_path)
    v.paths(root)["occ1d_enforcement"].unlink()
    r = v.verify(root)
    assert r["verdict"] == v.INDETERMINATE
    assert r["reason"] == "REQUIRED_INPUT_MISSING"
