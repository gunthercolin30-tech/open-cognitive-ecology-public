from __future__ import annotations

def main():
    from nicegui import app, ui
    from oif.ui import navigation_model, navigation_preferences, operational_shell
    assert app is not None and ui is not None
    assert navigation_model.build_navigation_model is not None
    assert navigation_preferences.sanitize_preferences is not None
    assert operational_shell.build_page is not None
    print("OIF2_3F_NICEGUI_IMPORT_SMOKE_OK")
    return 0
if __name__ == "__main__": raise SystemExit(main())
