from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path


ROOT = Path.home() / "open-cognitive-ecology"
REFINER = Path.home() / "Downloads" / "refine_acee_best_architecture_archive.py"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tracked_files() -> list[Path]:
    files = [
        ROOT / "ontology" / "acee_best_architecture_archive.py",
        ROOT / "ontology_inventory.txt",
        ROOT / "ontology_inventory.py",
        ROOT / "ontology" / "ontology_inventory.py",
        ROOT / "dependency_registry.py",
        ROOT / "global_module_catalog.txt",
        ROOT / "global_module_catalog.py",
        ROOT / "global_module_catalog.json",
    ]
    files.extend(sorted(ROOT.glob("acee14_*.py")))
    return [
        path
        for path in files
        if path.is_file() and not path.name.endswith(".bak")
    ]


def main() -> None:
    assert REFINER.is_file(), REFINER
    before_paths = tracked_files()
    before = {str(path): sha(path) for path in before_paths}

    completed = subprocess.run(
        ["python3", str(REFINER)],
        cwd=str(ROOT),
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        print(completed.stdout)
        print(completed.stderr)
    assert completed.returncode == 0
    assert (
        "ACEE14_BEST_ARCHITECTURE_ARCHIVE_REFINEMENT_READY"
        in completed.stdout
    )

    after_paths = tracked_files()
    after = {str(path): sha(path) for path in after_paths}
    assert set(before) == set(after)
    assert before == after

    print("ACEE14_REFINER_IDEMPOTENT_OK")


if __name__ == "__main__":
    main()
