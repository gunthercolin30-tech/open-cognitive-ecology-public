import json
import shutil
from pathlib import Path
from ontology import occ_compiled_normative_profile_postclose_verifier as pc

ROOT = Path(__file__).resolve().parents[1]

def test_postclose_nominal():
    r=pc.verify(ROOT)
    assert r["decision"]=="OCC1E_CLOSED_POSTCLOSE_VERIFIED", r
    assert r["postclose_verified"] is True
    assert all(r["checks"].values())
    assert r["source_drift_detected"] is False
    assert r["occ1f_opened"] is False and r["p160_opened"] is False and r["p159_final_lock"] is False

def test_determinism():
    assert pc.verify(ROOT) == pc.verify(ROOT)

def sandbox(tmp_path):
    dst=tmp_path/"repo"
    for k,src in pc.paths(ROOT).items():
        if k=="output": continue
        target=dst/src.relative_to(ROOT)
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(src,target)
    return dst

def test_profile_drift_rejected(tmp_path):
    root=sandbox(tmp_path); p=pc.paths(root)["profile"]
    obj=json.loads(p.read_text()); obj["profile_version"]="FORGED"
    p.write_text(json.dumps(obj,sort_keys=True,indent=2)+"\n")
    r=pc.verify(root)
    assert r["postclose_verified"] is False
    assert r["source_drift_detected"] is True

def test_manifest_drift_rejected(tmp_path):
    root=sandbox(tmp_path); p=pc.paths(root)["manifest"]
    p.write_text(p.read_text()+"\n")
    r=pc.verify(root)
    assert r["postclose_verified"] is False
    assert r["source_drift_detected"] is True

def test_closure_tamper_rejected(tmp_path):
    root=sandbox(tmp_path); p=pc.paths(root)["closure"]
    obj=json.loads(p.read_text()); obj["occ1f_opened"]=True
    p.write_text(json.dumps(obj,sort_keys=True,indent=2)+"\n")
    r=pc.verify(root)
    assert r["postclose_verified"] is False
    assert r["checks"]["downstream_unopened"] is False
