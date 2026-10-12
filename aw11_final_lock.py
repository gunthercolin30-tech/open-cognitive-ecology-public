import runpy
from pathlib import Path
path = Path.home() / "open-cognitive-ecology" / "ecological_stability_analyzer_final_lock.py"
runpy.run_path(str(path), run_name="__main__")
