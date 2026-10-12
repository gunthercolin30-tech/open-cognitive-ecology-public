from __future__ import annotations
import json, os, platform, subprocess
from pathlib import Path
from typing import Any

def _run(command: list[str], timeout: int = 45) -> dict[str, Any]:
    try:
        p = subprocess.run(command, text=True, capture_output=True, timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"returncode": 127, "stdout": "", "stderr": str(exc)}
    return {"returncode": p.returncode, "stdout": p.stdout.strip(), "stderr": p.stderr.strip()}

def diagnose(root: Path | None = None, env_dir: Path | None = None) -> dict[str, Any]:
    root = (root or Path(os.environ.get("OIF_ROOT", Path.home() / "open-cognitive-ecology"))).resolve()
    env_dir = (env_dir or Path(os.environ.get("OIF_ENV_DIR", root / ".venv-oif"))).resolve()
    python = env_dir / "bin" / "python"
    r = {"primitive":"OIF2_NICEGUI_ENVIRONMENT","classification":"technical_infrastructure_only","environment_exists":env_dir.is_dir(),"python_exists":python.is_file(),"isolated":False,"pip_check_ok":False,"imports_ok":False,"lock_present":(root/"requirements/oif-nicegui.lock.txt").is_file(),"functional_conclusion_only":True,"phenomenology_undetermined":True,"consciousness_proven":False,"subjectivity_proven":False,"qualia_proven":False,"phenomenology_proven":False}
    if not python.is_file():
        r.update(status="environment_missing", error_count=1)
        return r
    code = "import importlib.util,json,sys; from pathlib import Path; cfg=Path(sys.prefix)/'pyvenv.cfg'; text=cfg.read_text(errors='replace') if cfg.exists() else ''; mods=['nicegui','fastapi','starlette','uvicorn','pydantic','httpx','websockets','jinja2']; print(json.dumps({'version':sys.version,'compatible':sys.version_info >= (3,11),'isolated':sys.prefix!=sys.base_prefix and 'include-system-site-packages = false' in text.lower(),'imports':{m:importlib.util.find_spec(m) is not None for m in mods}}))"
    p = _run([str(python), "-c", code])
    if p["returncode"] == 0:
        d = json.loads(p["stdout"])
        r.update(python_version=d["version"], python_compatible=bool(d["compatible"]), isolated=bool(d["isolated"]), imports=d["imports"])
        r["imports_ok"] = all(d["imports"].values())
    else:
        r["probe_error"] = p["stderr"]
        r["python_compatible"] = False
    c = _run([str(python), "-m", "pip", "check"])
    r["pip_check_ok"] = c["returncode"] == 0
    r["pip_check"] = c["stdout"] or c["stderr"]
    r["platform"] = platform.platform()
    r["machine"] = platform.machine()
    r["status"] = "operational" if r.get("python_compatible") and r["isolated"] and r["imports_ok"] and r["pip_check_ok"] else "degraded"
    r["error_count"] = 0 if r["status"] == "operational" else 1
    return r

if __name__ == "__main__":
    print(json.dumps(diagnose(), indent=2, sort_keys=True))
