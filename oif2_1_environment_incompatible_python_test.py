from __future__ import annotations
import os, subprocess, sys, tempfile
from pathlib import Path

root = Path.home() / "open-cognitive-ecology"
install = root / "scripts/oif2_nicegui_install.sh"
candidates = [
    Path("/usr/bin/python3"),
    Path("/Library/Developer/CommandLineTools/usr/bin/python3"),
    Path("/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3"),
]
old_python = None
for candidate in candidates:
    if not candidate.is_file():
        continue
    probe = subprocess.run(
        [str(candidate), "-c", "import sys; raise SystemExit(0 if sys.version_info < (3,11) else 1)"],
        capture_output=True,
        timeout=30,
    )
    if probe.returncode == 0:
        old_python = candidate
        break

if old_python is None:
    print("OIF2_1_INCOMPATIBLE_PYTHON_TEST_SKIPPED_NO_OLD_PYTHON")
else:
    with tempfile.TemporaryDirectory(prefix="oif2_1_old_python_") as tmp:
        env_dir = Path(tmp) / ".venv-oif-test"
        e = os.environ.copy()
        e["OIF_ROOT"] = str(root)
        e["OIF_ENV_DIR"] = str(env_dir)
        e["OIF_PYTHON"] = str(old_python)
        p = subprocess.run(["bash", str(install)], cwd=root, env=e, text=True, capture_output=True, timeout=120)
        assert p.returncode != 0, p.stdout + p.stderr
        assert not env_dir.exists(), f"Environnement partiel conservé: {env_dir}"
        assert "Python >= 3.11" in (p.stdout + p.stderr), p.stdout + p.stderr
        print("OIF2_1_INCOMPATIBLE_PYTHON_ROLLBACK_TEST_OK")
