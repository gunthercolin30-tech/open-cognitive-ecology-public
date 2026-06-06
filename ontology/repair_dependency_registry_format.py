#!/usr/bin/env python3
"""
repair_dependency_registry_format.py
"""

from pathlib import Path
import shutil

ROOT = Path.home() / "open-cognitive-ecology"

REGISTRY_PATH = (
    ROOT
    / "ontology"
    / "dependency_registry.py"
)

def main():

    if not REGISTRY_PATH.exists():

        print(
            "dependency_registry.py introuvable."
        )

        return

    backup = REGISTRY_PATH.with_suffix(
        ".py.bak"
    )

    shutil.copy2(
        REGISTRY_PATH,
        backup,
    )

    print(
        f"Backup créé : {backup}"
    )

    source = REGISTRY_PATH.read_text(
        encoding="utf-8"
    )

    repaired = source.replace(
        "\\n",
        "\n"
    )

    REGISTRY_PATH.write_text(
        repaired,
        encoding="utf-8"
    )

    print(
        "dependency_registry.py réparé."
    )

if __name__ == "__main__":

    main()
