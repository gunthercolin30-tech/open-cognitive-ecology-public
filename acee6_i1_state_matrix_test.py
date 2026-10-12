#!/usr/bin/env python3
from datetime import datetime,timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import json
from ontology.acee_installation_executor import AceeInstallationExecutor,_sha
PRE={"PREPARING","PREPARED","BACKING_UP","BACKED_UP"};POST={"MUTATING","MUTATED","COMPILING","COMPILED","INVENTORY_UPDATING","INVENTORIES_UPDATED","TESTING","LOCALLY_VALIDATED","GLOBAL_VALIDATION_RUNNING","GLOBAL_VALIDATED","COMMITTING","REPORTING","FAULT_INJECTED"};TERM={"ROLLED_BACK","QUARANTINE","COMMITTED","REJECTED"}
def tx(root,i,s):
 p=root/"acee6_transactions"/i;p.mkdir(parents=True);r={"transaction_id":i,"state":s,"timestamp_utc":"2026-07-16T00:00:00+00:00","previous_record_hash":None};r["record_hash"]=_sha(r);(p/"journal.jsonl").write_text(json.dumps(r)+"\n");l={"transaction_id":i,"transaction_state":s,"latest_record_hash":r["record_hash"]};l["state_hash"]=_sha(l);(p/"latest_state.json").write_text(json.dumps(l)+"\n")
with TemporaryDirectory() as t:
 root=Path(t);e=AceeInstallationExecutor(root=root,now_utc=datetime(2026,7,16,tzinfo=timezone.utc))
 for s in sorted(PRE|POST|TERM):
  i="tx-"+s.lower();tx(root,i,s);r=e.recover_transaction(i,persist=False);assert (s in PRE and r["crash_recovery_action"]=="resume_safe") or (s in POST and r["rollback_required"] is True) or (s in TERM and r["status"]=="ACEE6_CRASH_RECOVERY_NOT_REQUIRED"),(s,r)
print("ACEE6_I1_STATE_MATRIX_OK")
