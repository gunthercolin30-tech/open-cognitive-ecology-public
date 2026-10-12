from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
INSTALLER = ROOT / "scripts" / "oif2_nicegui_install.sh"

assert INSTALLER.is_file(), INSTALLER


def run_case(name: str, lock_mode: str, content: str | None) -> None:
    with tempfile.TemporaryDirectory(prefix=f"oif2_1_bad_lock_{name}_") as tmp:
        work = Path(tmp)
        env_dir = work / ".venv-oif-test"
        lock = work / "oif-nicegui.lock.txt"
        record = work / "interpreter.txt"

        if lock_mode == "file":
            lock.write_text(content or "", encoding="utf-8")
        elif lock_mode != "missing":
            raise AssertionError(lock_mode)

        env = os.environ.copy()
        env["OIF_ROOT"] = str(ROOT)
        env["OIF_ENV_DIR"] = str(env_dir)
        env["OIF_LOCK_FILE"] = str(lock)
        env["OIF_INTERPRETER_RECORD"] = str(record)
        env["PIP_DEFAULT_TIMEOUT"] = "15"
        env["PIP_RETRIES"] = "0"

        completed = subprocess.run(
            ["bash", str(INSTALLER)],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            timeout=600,
            check=False,
        )
        output = completed.stdout + completed.stderr

        assert completed.returncode != 0, f"{name} aurait dû échouer:\n{output}"
        assert not env_dir.exists(), (
            f"{name}: environnement partiel conservé: {env_dir}\n{output}"
        )
        assert not record.exists(), (
            f"{name}: registre d'interpréteur modifié malgré l'échec\n{output}"
        )

        if name in {"invalid_syntax", "impossible_version"}:
            assert "OIF2_1_PARTIAL_ENVIRONMENT_ROLLED_BACK" in output, output

        print(f"OIF2_1_CORRUPTED_LOCK_{name.upper()}_OK")


run_case("missing", "missing", None)
run_case("empty", "file", "")
run_case("invalid_syntax", "file", "this is not a valid requirement !!!\n")
run_case("impossible_version", "file", "nicegui===0.0.0-oif-impossible\n")

print("OIF2_1_CORRUPTED_LOCK_TEST_OK")
