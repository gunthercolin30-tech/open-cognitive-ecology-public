from __future__ import annotations
import json, shutil, tempfile
from copy import deepcopy
from pathlib import Path
from acee2_fast_acceptance_suite import context
from ontology.acee_meta_orchestrator import AceeMetaOrchestrator

def main():
    adapter=AceeMetaOrchestrator(root=Path("/nonexistent"))
    c=context(); a=adapter.step(inputs=c,persist=False); b=adapter.step(inputs=deepcopy(c),persist=False)
    assert a["trace_hash"]==b["trace_hash"]
    reordered={k:c[k] for k in reversed(list(c))}; d=adapter.step(inputs=reordered,persist=False); assert a["trace_hash"]==d["trace_hash"]
    rejected=context(); rejected["governor_decision"]={"approved":False}; r=adapter.step(inputs=rejected,persist=False)
    assert r["cycle_status"]=="governance_rejected" and r["execution_authorized"] is False
    blocked=context(); blocked["constitutional_decision"]={"approved":False}; r=adapter.step(inputs=blocked,persist=False)
    assert r["cycle_status"]=="execution_blocked" and r["execution_eligible"] is False
    human=context(); human["human_review_required"]=True; human["human_review"]={"approved":False}; r=adapter.step(inputs=human,persist=False)
    assert r["cycle_status"]=="human_review_required"
    rollback=context(); rollback["normalized_engine_result"]={**rollback["normalized_engine_result"],"rollback_required":True}; r=adapter.step(inputs=rollback,persist=False)
    assert r["cycle_status"]=="rollback_required" and r["next_action"]=="request_governed_rollback"
    root=Path(tempfile.mkdtemp(prefix="acee2_history_"))
    try:
        p=AceeMetaOrchestrator(root=root); x=p.step(inputs=context(),persist=True); c2=context(); c2["cycle_timestamp_utc"]="2026-07-13T16:11:00Z"; y=p.step(inputs=c2,persist=True)
        assert y["previous_trace_hash"]==x["trace_hash"]
        records=[json.loads(line) for line in Path(y["history_path"]).read_text(encoding="utf-8").splitlines() if line.strip()]
        assert len(records)==2 and records[1]["previous_trace_hash"]==records[0]["trace_hash"]
        Path(y["history_path"]).write_text("{broken\n",encoding="utf-8"); z=p.step(inputs=context(),persist=False); assert z["history_corrupted"] is True
    finally: shutil.rmtree(root,ignore_errors=True)
    for key in ("consciousness_proven","subjectivity_proven","qualia_proven","phenomenology_proven","collective_consciousness_proven"): assert a[key] is False
    print("ACEE2_SPECIALIZED_TESTS_OK")
if __name__=="__main__": main()
