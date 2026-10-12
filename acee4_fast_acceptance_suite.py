from __future__ import annotations
import py_compile, tempfile
from pathlib import Path
from ontology.acee_autonomous_cycle_manager import AceeAutonomousCycleManager, PHASES

def context():
    return {"cycle_id":"cycle-001","timestamp_utc":"2026-07-13T20:00:00Z","requested_phases":list(PHASES),"phase_results":{p:{"status":"completed","score":0.95} for p in PHASES}|{"selection":{"status":"completed","decision":"accept","score":0.96},"rollback_or_acceptance":{"status":"completed","decision":"accepted","score":0.95}},"governance_decision":{"approved":True},"constitutional_decision":{"approved":True},"closure_pressure":0.05}

def main():
    with tempfile.TemporaryDirectory() as td: py_compile.compile("ontology/acee_autonomous_cycle_manager.py",cfile=str(Path(td)/"x.pyc"),doraise=True)
    r=AceeAutonomousCycleManager(root=Path("/nonexistent")).step(inputs=context(),persist=False)
    assert r["cycle_status"]=="ACEE_AUTONOMOUS_CYCLE_COMPLETE" and r["accepted"] is True and r["cycle_complete"] is True
    assert r["execution_dispatched"] is False and r["rollback_executed_by_manager"] is False
    assert len(r["cycle_hash"])==64 and r["functional_conclusion_only"] is True
    print("ACEE4_FAST_ACCEPTANCE_OK")
if __name__=="__main__": main()
