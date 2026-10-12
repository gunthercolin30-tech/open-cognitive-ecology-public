from pathlib import Path
from ontology.consciousness_dashboard import ConsciousnessDashboard

r = ConsciousnessDashboard().step(
    inputs={},
    persist=True,
)

assert r["persisted"] is True
assert r["json_path"]
assert r["html_path"]
assert r["prometheus_path"]
assert Path(r["json_path"]).exists()
assert Path(r["html_path"]).exists()
assert Path(r["prometheus_path"]).exists()

print("AS10_PERSISTENCE_OK")
print(r["html_path"])
