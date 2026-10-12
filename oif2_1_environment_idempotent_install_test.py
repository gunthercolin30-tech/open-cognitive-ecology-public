from __future__ import annotations
import hashlib, os, subprocess, tempfile
from pathlib import Path

root = Path.home() / "open-cognitive-ecology"
install = root / "scripts/oif2_nicegui_install.sh"
with tempfile.TemporaryDirectory(prefix="oif2_1_idempotent_") as tmp:
    env_dir = Path(tmp) / ".venv-oif-test"
    e = os.environ.copy()
    e["OIF_ROOT"] = str(root)
    e["OIF_ENV_DIR"] = str(env_dir)
    freezes = []
    for _ in range(2):
        p = subprocess.run(["bash", str(install)], cwd=root, env=e, text=True, capture_output=True, timeout=1200)
        assert p.returncode == 0, p.stdout + p.stderr
        f = subprocess.run([str(env_dir / "bin/python"), "-m", "pip", "freeze", "--all"], text=True, capture_output=True, timeout=120)
        assert f.returncode == 0, f.stdout + f.stderr
        freezes.append(hashlib.sha256(f.stdout.encode()).hexdigest())
    assert freezes[0] == freezes[1], freezes
print("OIF2_1_ENVIRONMENT_IDEMPOTENT_INSTALL_TEST_OK")
