#!/usr/bin/env python3
from __future__ import annotations

import runpy
from pathlib import Path

ROOT = Path.home() / "open-cognitive-ecology"
CANONICAL_FINAL_LOCK = ROOT / "developmental_prediction_engine_final_lock.py"

if not CANONICAL_FINAL_LOCK.is_file():
    raise FileNotFoundError(
        f"Missing canonical AV8 final lock: {CANONICAL_FINAL_LOCK}"
    )

runpy.run_path(str(CANONICAL_FINAL_LOCK), run_name="__main__")
