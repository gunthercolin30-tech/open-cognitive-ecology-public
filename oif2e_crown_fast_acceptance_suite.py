from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
SCRIPT = ROOT / "oif2e_adversarial_crown.py"

result = subprocess.run(
    [sys.executable, str(SCRIPT)],
    cwd=str(ROOT),
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    timeout=120,
)
if result.returncode != 0:
    raise AssertionError(result.stdout)
required = (
    "OIF2E_CATALOGUE_TAMPER_OK",
    "OIF2E_SOURCE_MUTATION_ISOLATION_OK",
    "OIF2E_CROSS_KIND_COLLISION_OK",
    "OIF2E_METADATA_ADVERSARIAL_OK",
    "OIF2E_CALLABLE_NON_EXPOSURE_OK",
    "OIF2E_SNAPSHOT_CATALOGUE_COHERENCE_OK",
    "OIF2E_FINAL_LOCK_TAMPER_OK",
    "OIF2E_SCALE_STABILITY_OK",
    "OIF2E_ADVERSARIAL_CROWN_OK",
)
for marker in required:
    assert marker in result.stdout, (marker, result.stdout)
print("OIF2E_CROWN_FAST_ACCEPTANCE_OK")
