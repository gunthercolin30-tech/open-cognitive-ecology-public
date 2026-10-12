#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,sys
if len(sys.argv)!=3:raise SystemExit("USAGE: python3 validation/p160jx_cross_host_compare_v1.py MAC_JSON UBUNTU_JSON")
A=Path(sys.argv[1]);B=Path(sys.argv[2])
a=json.loads(A.read_text(encoding="utf-8"));b=json.loads(B.read_text(encoding="utf-8"))
assert a["schema"]==b["schema"]=="oce.p160jx.cross_host_evidence.v1"
ha=a["host"];hb=b["host"]
assert ha["system"]=="Darwin" and hb["system"]=="Linux", (ha,hb)
assert "arm" in ha["machine"].lower() or "aarch64" in ha["machine"].lower()
assert "arm" in hb["machine"].lower() or "aarch64" in hb["machine"].lower()
assert a["runtime"]["g_sha256"]==b["runtime"]["g_sha256"]=="12e46324fb8887c94a1f33074e2431177ba5b5ff1b9e2c956ff825097a1a705c"
assert a["runtime"]["j_sha256"]==b["runtime"]["j_sha256"]
assert set(a["vectors"])==set(b["vectors"])
for k in sorted(a["vectors"]):
 assert a["vectors"][k]["sha256"]==b["vectors"][k]["sha256"],k
 assert a["vectors"][k]["canonical_json"]==b["vectors"][k]["canonical_json"],k
assert a["aggregate_hash"]==b["aggregate_hash"]
for d in (a,b):
 assert all(v is False for v in d["boundaries"].values())
print("P160JX_CROSS_HOST_EQUIVALENCE_OK")
print("DARWIN="+ha["machine"]+" PY="+ha["python"])
print("LINUX="+hb["machine"]+" PY="+hb["python"])
print("AGGREGATE_HASH="+a["aggregate_hash"])
print("J_SHA256="+a["runtime"]["j_sha256"])
print("P160K_OPENED=false");print("P161_OPENED=false")
