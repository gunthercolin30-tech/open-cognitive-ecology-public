from pathlib import Path
from ontology.consciousness_dashboard import ConsciousnessDashboard

r = ConsciousnessDashboard().step(
    inputs={},
    persist=True,
)

html = Path(r["html_path"]).read_text(encoding="utf-8")

checks = [
    ("dashboard", "dashboard"),
    ("CRI", "CRI"),
    ("confidence", "confidence"),
    ("state", "state"),
    ("timeline", "timeline"),
]

for label, token in checks:
    assert token.lower() in html.lower(), f"{label} missing"

print("AS10_HTML_OK")
print(r["html_path"])
