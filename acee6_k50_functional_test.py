from __future__ import annotations
import json, tempfile
from pathlib import Path
from ontology.acee_installation_executor import AceeInstallationExecutor, _sha

def write_hashed(path, payload, field):
    payload=dict(payload); payload[field]=_sha(payload); path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(payload,sort_keys=True),encoding="utf-8"); return payload[field]

def main():
    with tempfile.TemporaryDirectory(prefix="acee6_k50_") as tmp:
        root=Path(tmp); (root/"ontology").mkdir(); target=root/"ontology"/"candidate.py"; target.write_text("VALUE = 1\n",encoding="utf-8")
        ex=AceeInstallationExecutor(root=root)
        tx="tx-k50-functional"; td=ex._transaction_runtime_root()/tx; td.mkdir(parents=True)
        latest={"transaction_id":tx,"proposal_id":"p1","manifest_hash":"a"*64,"transaction_state":"GLOBALLY_VALIDATED","global_validation_passed":True,"local_validation_passed":True,"committed":False,"latest_record_hash":None}
        prev=None
        for state in ["PREPARING","PREPARED","BACKING_UP","BACKED_UP","MUTATING","MUTATED","COMPILING","COMPILED","INVENTORY_UPDATING","INVENTORIES_UPDATED","TESTING","LOCALLY_VALIDATED","GLOBAL_VALIDATING","GLOBALLY_VALIDATED"]:
            prev=ex._append_journal_record(td/"journal.jsonl",{"transaction_id":tx,"proposal_id":"p1","state":state,"timestamp_utc":ex.now_utc.isoformat()},prev)
        latest["latest_record_hash"]=prev; latest["state_hash"]=_sha(latest); ex._atomic_json_write(td/"latest_state.json",latest)
        for name,field in [("compilation_report.json","compilation_report_hash"),("inventory_update_manifest.json","inventory_update_manifest_hash"),("local_validation_report.json","local_validation_report_hash"),("global_validation_report.json","global_validation_report_hash")]:
            h=write_hashed(td/name,{"transaction_id":tx},field); latest[field]=h
        latest.pop("state_hash",None); latest["state_hash"]=_sha(latest); ex._atomic_json_write(td/"latest_state.json",latest)
        admitted={"proposal_id":"p1","manifest_hash":"a"*64,"normalized_plan":{"target_path":"ontology/candidate.py","candidate_content_sha256":__import__("hashlib").sha256(target.read_bytes()).hexdigest()}}
        result=ex._k50_commit_transaction(latest,admitted)
        assert result["transaction_state"]=="COMMITTED", result
        assert result["status"]=="ACEE_INSTALLATION_EXECUTION_COMPLETE", result
        replay=ex._k50_validate_committed_replay(td,admitted)
        assert replay and replay["commit_replayed"] is True, replay
    print("ACEE6_K50_FUNCTIONAL_OK")
if __name__=="__main__": main()
