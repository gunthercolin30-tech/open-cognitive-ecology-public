#!/usr/bin/env python3
"""
repair_dependency_registry.py
"""

from pathlib import Path
import re
import shutil

ROOT = Path.home() / "open-cognitive-ecology"

registry = ROOT / "ontology" / "dependency_registry.py"

backup = registry.with_suffix(".py.pre_repair.bak")

shutil.copy2(registry, backup)

content = registry.read_text(encoding="utf-8")

content = re.sub(
    r'^\s*\\n+\s*$',
    '',
    content,
    flags=re.MULTILINE,
)

content = re.sub(
    r'\\n\\n',
    '\n\n',
    content,
)

content = re.sub(
    r'\n{3,}',
    '\n\n',
    content,
)

registry.write_text(
    content,
    encoding="utf-8",
)

print(f"backup_created={backup}")
print(f"registry_repaired={registry}")
