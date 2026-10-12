import runpy
from pathlib import Path

path = Path.home() / "open-cognitive-ecology" / "ecology_dashboard_final_lock.py"
if not path.is_file():
    raise FileNotFoundError(path)
runpy.run_path(str(path), run_name="__main__")
