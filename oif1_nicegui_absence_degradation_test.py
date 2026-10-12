from __future__ import annotations

import builtins
import importlib
import sys
from pathlib import Path


def main() -> None:
    root = Path.home() / "open-cognitive-ecology"
    sys.path.insert(0, str(root))
    original_import = builtins.__import__

    def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "nicegui" or name.startswith("nicegui."):
            raise ModuleNotFoundError("nicegui intentionally unavailable")
        return original_import(name, globals, locals, fromlist, level)

    builtins.__import__ = guarded_import
    try:
        constitution = importlib.import_module("oif_functional_constitution")
        service = importlib.import_module("oif.ui.campaign_service")
        assert constitution is not None
        assert service is not None
        try:
            importlib.import_module("oif.ui.review_app")
        except ModuleNotFoundError as exc:
            assert "nicegui" in str(exc)
        else:
            raise AssertionError("renderer imported without NiceGUI")
    finally:
        builtins.__import__ = original_import

    print("OIF1_CONSTITUTION_WITHOUT_NICEGUI_OK")
    print("OIF1_SERVICE_WITHOUT_NICEGUI_OK")
    print("OIF1_RENDERER_FAILS_CLOSED_WITHOUT_NICEGUI_OK")
    print("OIF1_NICEGUI_ABSENCE_DEGRADATION_TEST_OK")


if __name__ == "__main__":
    main()
