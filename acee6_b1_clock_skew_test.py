from copy import deepcopy
from datetime import timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from acee6_b1_test_support import fixed_now, valid_acee5_decision
from ontology.acee_installation_executor import AceeInstallationExecutor, _sha, MAX_FUTURE_SKEW_SECONDS
with TemporaryDirectory() as t:
 r=Path(t); (r/"ontology").mkdir(); now=fixed_now(); base=valid_acee5_decision(r)
 cases=[("bad","decision_timestamp_invalid"),((now+timedelta(seconds=MAX_FUTURE_SKEW_SECONDS+1)).isoformat(),"manifest_timestamp_in_future")]
 for value,reason in cases:
  d=deepcopy(base); d["timestamp_utc"]=value; d["result_hash"]=_sha({k:v for k,v in d.items() if k!="result_hash"}); x=AceeInstallationExecutor(root=r,now_utc=now).step(d); assert reason in x["blocking_reasons"]
 d=deepcopy(base); d["timestamp_utc"]=(now+timedelta(seconds=MAX_FUTURE_SKEW_SECONDS)).isoformat(); d["result_hash"]=_sha({k:v for k,v in d.items() if k!="result_hash"}); assert AceeInstallationExecutor(root=r,now_utc=now).step(d)["admissible"]
print("ACEE6_B1_CLOCK_SKEW_OK")
