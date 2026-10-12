import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
PROTECTED=('oif/interface/manifest_diff.py','oif2h_test_support.py','oif2h_manifest_diff_functional_test.py','oif2h_manifest_diff_degradation_test.py','oif2h_manifest_diff_non_regression_test.py','oif2h_manifest_diff_determinism_test.py','oif2h_manifest_diff_cross_format_test.py','oif2h_fast_acceptance_suite.py')
subprocess.run([sys.executable,'oif2h_fast_acceptance_suite.py'],check=True)
hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in PROTECTED}
report={'milestone':'OIF-2H','status':'LOCKED','functional_only':True,'phenomenology_undetermined':True,'protected_hashes':hashes}
(ROOT/'oif2h_manifest_diff_final_lock_report.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8')
print('OIF2H_MANIFEST_DIFF_FINAL_LOCK_OK')
