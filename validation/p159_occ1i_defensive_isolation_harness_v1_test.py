import importlib.util,json,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; HP=ROOT/"validation/occ1i_defensive_isolation_harness.py"
RP=ROOT/"validation_artifacts/p159/occ1i/defensive_isolation_harness_qualification_v1.json"
def mod():
    s=importlib.util.spec_from_file_location("occ1i_h",HP); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
def test_f3_functional_isolation_and_causal_evidence():
    h=mod(); r=h.run_fixture("Q1","MODE=DENY\n",lambda s:s.replace("DENY","ALLOW"),lambda s:"ALLOW" in s)
    assert r["status"]=="KILLED" and r["mutation_changed_hash"] and r["detector_observed"] and r["causal_evidence"] and r["workspace_destroyed"]
def test_f3_degradation_survival_and_equivalence():
    h=mod(); r=h.run_fixture("Q2","A=1\n",lambda s:s.replace("1","2"),lambda s:False); assert r["status"]=="SURVIVED" and r["workspace_destroyed"]
    e=h.run_fixture("Q3","A=1\n",lambda s:s,lambda s:True); assert e["status"]=="SEMANTICALLY_EQUIVALENT" and e["workspace_destroyed"]
def test_f3_fail_closed_interrupt_and_contamination():
    h=mod(); i=h.run_fixture("Q4","A=1\n",lambda s:s+"B=2\n",lambda s:True,simulate_interrupt=True)
    assert i["status"]=="INCONCLUSIVE" and i["interrupted"] and i["workspace_destroyed"]
    c=h.run_fixture("Q5","A=1\n",lambda s:s+"B=2\n",lambda s:True,simulate_contamination=True)
    assert c["status"]=="INCONCLUSIVE" and c["canonical_write"] and c["workspace_destroyed"]
def test_f3_cwd_independence_and_boundaries(tmp_path):
    old=os.getcwd()
    try:
        os.chdir(tmp_path); h=mod(); r=h.run_fixture("Q6","X=SAFE\n",lambda s:s.replace("SAFE","CHANGED"),lambda s:"CHANGED" in s)
        assert r["status"]=="KILLED" and r["workspace_destroyed"]
    finally: os.chdir(old)
    x=json.loads(RP.read_text(encoding="utf-8")); assert x["qualification_only"] and x["core_execution"] is False
    assert not x["occ1i_closed"] and not x["occ1j_opened"] and not x["p159_final_lock"] and not x["p160_opened"]
