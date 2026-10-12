import tempfile
from pathlib import Path
from oif.environment.nicegui_environment import diagnose
with tempfile.TemporaryDirectory() as t:
 r=diagnose(Path(t),Path(t)/".venv-oif"); assert r["status"]=="environment_missing" and r["error_count"]==1,r
print("OIF2_1_ENVIRONMENT_DEGRADATION_TEST_OK")
