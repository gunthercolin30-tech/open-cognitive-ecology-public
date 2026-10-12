from __future__ import annotations
import py_compile
import tempfile
from pathlib import Path
from ontology.acee_meta_orchestrator import AceeMetaOrchestrator


def context():
    audit={"audit_completed":True,"audit_status":"ACEE_INTEGRATION_AUDIT_COMPLETE","audit_id":"a1","audit_hash":"a"*64}
    cmap={"capability_map_ready":True,"capability_map_status":"ACEE_CAPABILITY_MAP_READY","mapping_hash":"b"*64,"capability_matrix":{"ACEE4":{"coverage_level":"partially_covered","coverage_score":0.5,"primary_module":"controlled_evolution_orchestrator","recommended_action":"refine"},"ACEE5":{"coverage_level":"deferred","coverage_score":0.0}}}
    normalized={"adapter_ready":True,"adapter_status":"ACEE_BRIDGE_ADAPTER_READY","normalized_hash":"c"*64,"status":"approved","source_module":"controlled_evolution_orchestrator","rollback_available":True,"rollback_required":False}
    return {"integration_audit":audit,"capability_map":cmap,"normalized_engine_result":normalized,"governor_decision":{"approved":True},"constitutional_decision":{"approved":True},"human_review_required":False,"cycle_timestamp_utc":"2026-07-13T16:10:00Z"}


def main():
    with tempfile.TemporaryDirectory() as td:
        py_compile.compile("ontology/acee_meta_orchestrator.py", cfile=str(Path(td)/"acee_meta_orchestrator.pyc"), doraise=True)
    result=AceeMetaOrchestrator(root=Path("/nonexistent")).step(inputs=context(),persist=False)
    assert result["orchestrator_status"]=="ACEE_META_ORCHESTRATOR_READY"
    assert result["cycle_status"]=="execution_eligible"
    assert result["execution_authorized"] is True
    assert result["execution_dispatched"] is False
    assert result["selected_engine"]=="controlled_evolution_orchestrator"
    assert len(result["trace_hash"])==64
    assert result["functional_conclusion_only"] is True
    print("ACEE2_FAST_ACCEPTANCE_OK")

if __name__=="__main__": main()
