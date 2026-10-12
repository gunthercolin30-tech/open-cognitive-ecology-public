import subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parent
for name in [
 'acee6_e_manifest_integrity_test.py',
 'acee6_e_atomic_rollback_test.py',
 'acee6_e_cross_view_divergence_test.py',
 'acee6_e_path_security_test.py',
 'acee6_e_determinism_test.py',
]:
 r=subprocess.run([sys.executable,str(root/name)],cwd=str(root),timeout=180)
 assert r.returncode==0,name
print('ACEE6_E_FIVE_PRIORITIES_OK')
