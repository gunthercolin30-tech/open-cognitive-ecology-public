from __future__ import annotations
import ast
from pathlib import Path
ROOT = Path(__file__).resolve().parent
FILES = [ROOT / "oif/ui/navigation_model.py", ROOT / "oif/ui/navigation_preferences.py", ROOT / "oif/ui/operational_shell.py"]
FORBIDDEN_MODEL = ("from nicegui", "import nicegui", "oif.adapters", "subprocess", "os.system", ".read_text(", ".write_text(", "open(")
FORBIDDEN_SHELL = ("CivilizationalStateAdapter", "ValidationReportAdapter", "RuntimeHealthAdapter", "subprocess", "os.system", ".read_text(", ".write_text(", "json.load(")

def main():
    for path in FILES: ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    model = FILES[0].read_text(encoding="utf-8")
    shell = FILES[2].read_text(encoding="utf-8")
    for token in FORBIDDEN_MODEL: assert token not in model, token
    for token in FORBIDDEN_SHELL: assert token not in shell, token
    assert "service.snapshot()" in shell
    assert "filter_cards(" in shell
    assert "render_civilizational_state_card(card)" in shell
    assert "app.storage.user" in shell
    assert "payload" not in (ROOT / "oif/ui/navigation_preferences.py").read_text(encoding="utf-8").split("as_dict", 1)[1].split("def sanitize_preferences", 1)[0]
    print("OIF2_3F_RENDERER_BOUNDARY_OK")
    return 0
if __name__ == "__main__": raise SystemExit(main())
