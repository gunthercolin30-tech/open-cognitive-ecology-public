import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
CORE=(
"oif/interface/manifest_diff.py",
"oif2h_test_support.py",
"oif2h_manifest_diff_functional_test.py",
"oif2h_manifest_diff_degradation_test.py",
"oif2h_manifest_diff_non_regression_test.py",
"oif2h_manifest_diff_determinism_test.py",
"oif2h_manifest_diff_cross_format_test.py",
"oif2h_fast_acceptance_suite.py",
"oif2h_manifest_diff_final_lock.py",
)
CROWN=(
"oif2h_crown_identity_path_test.py",
"oif2h_crown_semantic_moves_test.py",
"oif2h_crown_limits_fail_closed_test.py",
"oif2h_crown_immutability_tamper_test.py",
"oif2h_crown_worker.py",
"oif2h_crown_multiprocess_determinism_test.py",
"oif2h_crown_no_execution_test.py",
"oif2h_crown_non_modification_test.py",
"oif2h_crown_fast_acceptance_suite.py",
)
for path in CORE+CROWN:
    if not (ROOT/path).is_file(): raise SystemExit("MISSING_PROTECTED_FILE: "+path)
subprocess.run([sys.executable,"oif2h_manifest_diff_final_lock.py"],cwd=str(ROOT),check=True)
subprocess.run([sys.executable,"oif2h_crown_fast_acceptance_suite.py"],cwd=str(ROOT),check=True)
hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in CORE+CROWN}
report={
"milestone":"OIF-2H-CROWN",
"status":"LOCKED",
"functional_only":True,
"phenomenology_undetermined":True,
"core_final_lock_verified":True,
"adversarial_tests":7,
"protected_hashes":hashes,
}
path=ROOT/"oif2h_crown_final_lock_report.json"
tmp=path.with_suffix(path.suffix+".tmp")
tmp.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
tmp.replace(path)
print("OIF2H_CROWN_FINAL_LOCK_OK")
