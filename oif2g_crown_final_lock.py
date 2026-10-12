from pathlib import Path
import hashlib, json, subprocess, sys
ROOT = Path(__file__).resolve().parent
subprocess.run([sys.executable, str(ROOT / "oif2g_crown_fast_acceptance_suite.py")], cwd=str(ROOT), check=True)
targets = ("oif/interface/complex_manifest_adversarial_guard.py", "oif2g_adversarial_crown.py", "oif2g_crown_non_modification_test.py", "oif2g_crown_fast_acceptance_suite.py")
report = {"milestone":"OIF-2G-adversarial-crown","functional_only":True,"operation_execution":False,"files":{rel:hashlib.sha256((ROOT/rel).read_bytes()).hexdigest() for rel in targets}}
(ROOT / "oif2g_crown_final_lock_report.json").write_text(json.dumps(report, indent=2, sort_keys=True)+"\n", encoding="utf-8")
print("OIF2G_CROWN_FINAL_LOCK_OK")
