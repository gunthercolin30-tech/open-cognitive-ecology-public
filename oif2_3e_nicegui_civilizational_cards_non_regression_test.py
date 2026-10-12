from __future__ import annotations
from pathlib import Path
from oif.application.default_providers import build_default_provider_specs


def main():
    root = Path(__file__).resolve().parent
    specs = build_default_provider_specs(root=root)
    names = [s.name for s in specs]
    assert names == ["validation-report", "runtime-health", "civilizational-state"]
    assert next(s.zone for s in specs if s.name == "civilizational-state") == "memory"
    shell = (root / "oif/ui/operational_shell.py").read_text(encoding="utf-8")
    assert "for zone_name, zone in snapshot[\"zones\"].items()" in shell
    assert "for card in zone_cards" in shell
    assert "render_civilizational_state_card(card)" in shell
    print("OIF2_3E_NICEGUI_CIVILIZATIONAL_CARDS_NON_REGRESSION_OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
