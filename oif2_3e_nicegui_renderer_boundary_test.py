from __future__ import annotations
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TARGETS = [ROOT / "oif/ui/civilizational_state_cards.py", ROOT / "oif/ui/operational_shell.py"]
FORBIDDEN_TEXT = ("representative_succession", "CivilizationalStateAdapter", ".read_text(", ".write_text(", "json.load(", "subprocess", "os.system", "open(")


def main():
    component = TARGETS[0].read_text(encoding="utf-8")
    shell = TARGETS[1].read_text(encoding="utf-8")
    for path in TARGETS:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for token in FORBIDDEN_TEXT:
        assert token not in component, token
    assert "render_civilizational_state_card(card)" in shell
    assert 'card["provider"] == "civilizational-state"' in shell
    assert 'ui.json_editor({"content": {"json": card["payload"]}})' in shell
    assert "OIF2ReadOnlyApplicationService" in shell
    print("OIF2_3E_NICEGUI_RENDERER_BOUNDARY_OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
