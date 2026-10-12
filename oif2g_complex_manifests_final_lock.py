from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parent
fast_report=R/"oif2g_fast_acceptance_report.json"
if not fast_report.is_file(): raise SystemExit("run oif2g_fast_acceptance_suite.py before final lock")
fast_data=json.loads(fast_report.read_text(encoding="utf-8"))
if fast_data.get("ok") is not True: raise SystemExit("OIF-2G fast acceptance report is not green")
targets=("oif/interface/complex_manifest_profile.py","interfaces/examples/complex/portal_pilot.yaml","interfaces/examples/complex/portal_pilot.json","interfaces/examples/complex/civilizational_state_pilot.yaml","interfaces/examples/complex/civilizational_state_pilot.json","interfaces/examples/complex/science_validation_pilot.yaml","interfaces/examples/complex/science_validation_pilot.json")
report={"milestone":"OIF-2G","functional_only":True,"operation_execution":False,"files":{x:hashlib.sha256((R/x).read_bytes()).hexdigest() for x in targets}}
(R/"oif2g_complex_manifests_final_lock_report.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
print("OIF2G_FINAL_LOCK_OK")
