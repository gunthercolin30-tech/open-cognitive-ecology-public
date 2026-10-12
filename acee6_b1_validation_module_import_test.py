from __future__ import annotations

import importlib
import types

import validation

package_attribute = getattr(validation, "main", None)
module = importlib.import_module("validation.main")

assert callable(package_attribute)
assert isinstance(module, types.ModuleType)
assert module.__name__ == "validation.main"
assert module is not package_attribute
assert hasattr(module, "ACEE6_ALIASES")
assert callable(module.main)

print("ACEE6_B1_VALIDATION_MODULE_IMPORT_OK")
