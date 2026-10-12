from __future__ import annotations

def main():
    from nicegui import ui
    from oif.ui.civilizational_state_cards import render_civilizational_state_card
    from oif.ui.operational_shell import build_page
    assert ui is not None
    assert callable(render_civilizational_state_card)
    assert callable(build_page)
    print("OIF2_3E_NICEGUI_IMPORT_SMOKE_OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
