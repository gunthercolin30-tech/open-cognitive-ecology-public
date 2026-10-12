import os
from pathlib import Path
from tempfile import TemporaryDirectory

from acee6_b1_test_support import fixed_now
from acee6_e_test_support import payload, seed
from ontology.acee_installation_executor import (
    AceeInstallationExecutor,
)


def assert_rejected(root: Path, expected: str) -> None:
    try:
        AceeInstallationExecutor(
            root=root,
            now_utc=fixed_now(),
        ).step(
            inputs=payload(root),
            persist=True,
        )
    except ValueError as exc:
        assert expected in str(exc), {
            "expected": expected,
            "actual": str(exc),
        }
    else:
        raise AssertionError(
            f"Expected rejection containing {expected!r}"
        )


# Symlink direct sur un inventaire.
with TemporaryDirectory() as tmp:
    root = Path(tmp)
    seed(root)

    target = root / "ontology_inventory.txt"
    external = root / "external_inventory.txt"

    external.write_text(
        target.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    target.unlink()
    os.symlink(external, target)

    assert_rejected(
        root,
        "inventory_symlink_rejected",
    )


# Hardlink entre deux représentations distinctes.
with TemporaryDirectory() as tmp:
    root = Path(tmp)
    seed(root)

    inventory = root / "ontology_inventory.txt"
    catalog = root / "global_module_catalog.txt"

    catalog.unlink()
    os.link(inventory, catalog)

    assert_rejected(
        root,
        "inventory_hardlink_collision",
    )


print("ACEE6_E_PATH_SECURITY_OK")
