from pathlib import Path
import subprocess, sys, time
ROOT = Path(__file__).resolve().parent
start = time.monotonic()
for test in ("oif2g_adversarial_crown.py", "oif2g_crown_non_modification_test.py", "oif2g_fast_acceptance_suite.py"):
    subprocess.run([sys.executable, str(ROOT / test)], cwd=str(ROOT), check=True)
print("OIF2G_CROWN_FAST_ACCEPTANCE_OK total=%.3fs" % (time.monotonic() - start))
