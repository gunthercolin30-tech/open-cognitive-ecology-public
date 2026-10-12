import json
import tempfile
from pathlib import Path
from aw10_context import build_context
from ontology.ecology_dashboard import EcologyDashboard

with tempfile.TemporaryDirectory(prefix="oce_aw10_exports_") as tmp:
    result = EcologyDashboard(root=Path(tmp)).step(inputs=build_context(), persist=True)
    parsed = json.loads(Path(result["json_path"]).read_text(encoding="utf-8"))
    markdown = Path(result["markdown_path"]).read_text(encoding="utf-8")
    html = Path(result["html_path"]).read_text(encoding="utf-8")
    assert parsed["dashboard_hash"] == result["dashboard_hash"]
    for section in ("Population RF", "Interactions", "RF partagés", "Coalitions", "Conflits", "Fusions", "Fragmentations", "Mémoire civilisationnelle", "Coordination collective"):
        assert section in markdown
        assert section in html
    assert "<html" in html.lower() and "</html>" in html.lower()
    assert "http://" not in html and "https://" not in html
print("AW10_EXPORT_VALIDATION_OK")
