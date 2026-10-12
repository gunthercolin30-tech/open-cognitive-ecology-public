import hashlib, json
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parent
FILES=("oif/interface/abstract_renderer.py","interfaces/examples/minimal/home_minimal.yaml","interfaces/examples/minimal/home_minimal.json","interfaces/examples/minimal/runtime_health_minimal.yaml","interfaces/examples/minimal/runtime_health_minimal.json","interfaces/examples/minimal/civilizational_state_minimal.yaml","interfaces/examples/minimal/civilizational_state_minimal.json","oif2f_minimal_manifests_functional_test.py","oif2f_minimal_manifests_degradation_test.py","oif2f_minimal_manifests_round_trip_test.py","oif2f_minimal_manifests_abstract_render_test.py","oif2f_minimal_manifests_security_test.py","oif2f_minimal_manifests_non_modification_test.py","oif2f_minimal_manifests_non_regression_test.py","oif2f_fast_acceptance_suite.py")
records=[]
for rel in FILES:
 p=ROOT/rel; assert p.is_file(), rel
 records.append({"path":rel,"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"size_bytes":p.stat().st_size})
payload={"milestone":"OIF-2F","status":"locked","functional_conclusion_only":True,"phenomenology_undetermined":True,"generated_at_utc":datetime.now(timezone.utc).isoformat(),"files":records}
canonical=json.dumps(payload,ensure_ascii=False,sort_keys=True,separators=(",",":"))
payload["report_sha256"]=hashlib.sha256(canonical.encode()).hexdigest()
path=ROOT/"oif2f_minimal_manifests_final_lock_report.json"
tmp=path.with_suffix(path.suffix+".tmp"); tmp.write_text(json.dumps(payload,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8"); tmp.replace(path)
print("OIF2F_FINAL_LOCK_OK")
