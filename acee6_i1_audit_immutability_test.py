#!/usr/bin/env python3
from datetime import datetime,timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import json,hashlib
from ontology.acee_installation_executor import AceeInstallationExecutor,_sha
def digest(p):
 h=hashlib.sha256();[h.update(x.read_bytes()) for x in sorted(p.rglob("*")) if x.is_file()];return h.hexdigest()
with TemporaryDirectory() as t:
 root=Path(t);p=root/"acee6_transactions"/"tx";p.mkdir(parents=True);r={"transaction_id":"tx","state":"PREPARED","previous_record_hash":None};r["record_hash"]=_sha(r);(p/"journal.jsonl").write_text(json.dumps(r)+"\n");l={"transaction_id":"tx","transaction_state":"PREPARED","latest_record_hash":r["record_hash"]};l["state_hash"]=_sha(l);(p/"latest_state.json").write_text(json.dumps(l));b=digest(root);AceeInstallationExecutor(root=root,now_utc=datetime(2026,7,16,tzinfo=timezone.utc)).recover_transaction("tx",persist=False);assert digest(root)==b
print("ACEE6_I1_AUDIT_IMMUTABILITY_OK")
