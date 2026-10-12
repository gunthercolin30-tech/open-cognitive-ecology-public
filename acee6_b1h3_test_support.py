from __future__ import annotations
import json, os, subprocess, sys
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"

def run_scope(scope=None):
    env = os.environ.copy()
    if scope is None:
        env.pop("OCE_FAST_SCOPE", None)
    else:
        env["OCE_FAST_SCOPE"] = scope
    return subprocess.run(
        [sys.executable, "-m", "validation.main"],
        cwd=str(ROOT), env=env, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
    )

def read_report():
    text=(ROOT/"ontology_integration_report.txt").read_text(encoding="utf-8")
    return json.loads(text.split("\n",1)[1])
