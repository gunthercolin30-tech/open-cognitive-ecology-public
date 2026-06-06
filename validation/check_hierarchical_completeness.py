"""Check that all ontology modules are classified and assigned a valid level."""

from pathlib import Path
from ontology.hierarchical_registry import HIERARCHICAL_LEVELS


EXCLUDED = {
    "__init__",
    "hierarchical_registry",
    "dependency_registry",
    "meta_concepts_registry",
}


def main():
    modules = [
        p.stem
        for p in Path("ontology").glob("*.py")
        if p.stem not in EXCLUDED
    ]

    missing = [m for m in modules if m not in HIERARCHICAL_LEVELS]
    undefined = [m for m in modules if HIERARCHICAL_LEVELS.get(m) is None]
    invalid = [
        m for m in modules
        if HIERARCHICAL_LEVELS.get(m) is not None
        and HIERARCHICAL_LEVELS[m] not in range(10)
    ]

    if missing:
        print("Missing entries:")
        for name in sorted(missing):
            print(f" - {name}")

    if undefined:
        print("Undefined hierarchical levels:")
        for name in sorted(undefined):
            print(f" - {name}")

    if invalid:
        print("Invalid hierarchical levels:")
        for name in sorted(invalid):
            print(f" - {name}: {HIERARCHICAL_LEVELS[name]}")

    if missing or undefined or invalid:
        raise SystemExit(1)

    print("All ontology modules are fully classified.")


if __name__ == "__main__":
    main()
