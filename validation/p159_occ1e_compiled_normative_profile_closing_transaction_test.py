from __future__ import annotations

import json
import shutil
from pathlib import Path

from ontology import occ_compiled_normative_profile_closing_transaction as close

ROOT = Path(__file__).resolve().parents[1]

def test_functional_close_is_locally_bounded():
    r = close.evaluate(ROOT)
    assert r["decision"] == "OCC1E_CLOSING_TRANSACTION_COMMITTED_VALID", r
    assert r["occ1e_closed"] is True
    assert all(r["checks"].values())
    assert r["runtime_consumer_graph_proven"] is False
    assert r["enforcement_status"] == "UNRESOLVED"
    assert r["authorization_created"] is False
    assert r["execution_performed"] is False
    assert r["occ1f_opened"] is False
    assert r["p160_opened"] is False
    assert r["p159_final_lock"] is False

def test_determinism_and_idempotent_identity():
    a = close.evaluate(ROOT)
    b = close.evaluate(ROOT)
    assert a == b
    assert a["transaction_id"] == b["transaction_id"]

def _sandbox(tmp_path):
    dst = tmp_path / "repo"
    needed = close._paths(ROOT)
    for key, src in needed.items():
        if key == "output":
            continue
        rel = src.relative_to(ROOT)
        target = dst / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, target)
    return dst

def test_degradation_profile_tamper_fails_closed(tmp_path):
    root = _sandbox(tmp_path)
    p = close._paths(root)["profile"]
    obj = json.loads(p.read_text(encoding="utf-8"))
    obj["rules"][0]["evaluation_phase"] = "FORGED"
    p.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    r = close.evaluate(root)
    assert r["occ1e_closed"] is False
    assert r["checks"]["profile_file_hash_bound"] is False or r["checks"]["profile_semantic_hash_valid"] is False

def test_degradation_manifest_tamper_fails_closed(tmp_path):
    root = _sandbox(tmp_path)
    p = close._paths(root)["manifest"]
    obj = json.loads(p.read_text(encoding="utf-8"))
    obj["rule_count"] = 47
    p.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    r = close.evaluate(root)
    assert r["occ1e_closed"] is False
    assert r["checks"]["manifest_hash_bound"] is False or r["checks"]["rule_count_48"] is False

def test_degradation_schema_tamper_fails_closed(tmp_path):
    root = _sandbox(tmp_path)
    p = close._paths(root)["schema"]
    p.write_text(p.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    r = close.evaluate(root)
    assert r["occ1e_closed"] is False
    assert r["checks"]["schema_hash_bound"] is False

def test_degradation_source_anchor_tamper_fails_closed(tmp_path):
    root = _sandbox(tmp_path)
    p = close._paths(root)["source"]
    p.write_text(p.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    r = close.evaluate(root)
    assert r["occ1e_closed"] is False
    assert r["checks"]["occ1c_source_hash_bound"] is False

def test_degradation_runtime_contract_tamper_fails_closed(tmp_path):
    root = _sandbox(tmp_path)
    p = close._paths(root)["runtime"]
    obj = json.loads(p.read_text(encoding="utf-8"))
    obj["authorization_capability"] = True
    p.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    r = close.evaluate(root)
    assert r["occ1e_closed"] is False
    assert r["checks"]["runtime_hash_bound"] is False or r["checks"]["no_authorization_manufactured"] is False
