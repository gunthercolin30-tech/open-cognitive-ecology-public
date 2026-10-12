import json
from pathlib import Path
from tempfile import TemporaryDirectory
from acee6_b1_test_support import fixed_now
from acee6_f1_test_support import payload,seed
from ontology.acee_installation_executor import AceeInstallationExecutor
with TemporaryDirectory() as tmp:
 root=Path(tmp);seed(root);p=payload(root);a=AceeInstallationExecutor(root=root,now_utc=fixed_now()).step(inputs=p,persist=True);rp=Path(a["local_validation_report_path"]);d=json.loads(rp.read_text());d["error_count"]=999;rp.write_text(json.dumps(d,sort_keys=True));b=AceeInstallationExecutor(root=root,now_utc=fixed_now()).step(inputs=p,persist=True);assert b["transaction_state"]=="STATE_CORRUPTED",b;assert "existing_local_validation_report_hash_invalid" in b["blocking_reasons"]
print("ACEE6_F1_REPORT_TAMPER_OK")
