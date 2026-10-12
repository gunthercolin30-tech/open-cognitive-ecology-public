from __future__ import annotations

import os
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory

from acee6_b1_test_support import fixed_now, valid_acee5_decision
from ontology.acee_installation_executor import AceeInstallationExecutor, _sha


def rebind(decision):
    manifest = decision["installation_manifest"]
    manifest["manifest_hash"] = _sha(
        {key: value for key, value in manifest.items() if key != "manifest_hash"}
    )
    decision["result_hash"] = _sha(
        {key: value for key, value in decision.items() if key != "result_hash"}
    )


def admitted_for(root: Path, parent_name: str):
    decision = deepcopy(valid_acee5_decision(root))
    manifest = decision["installation_manifest"]
    manifest["target_path"] = f"ontology/{parent_name}/candidate.py"
    manifest["backup_path"] = f"ontology/{parent_name}/candidate.py.bak"
    rebind(decision)
    executor = AceeInstallationExecutor(root=root, now_utc=fixed_now())
    admitted = executor.step(decision)
    assert admitted["admissible"] is True, admitted
    return executor, admitted


def main() -> None:
    # Parent directory inode swap after admission must be detected.
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        parent = root / "ontology" / "safe"
        parent.mkdir(parents=True)
        executor, admitted = admitted_for(root, "safe")

        original = root / "ontology" / "safe.original"
        parent.rename(original)
        parent.mkdir()

        target, reasons = executor._secure_mutation_target(admitted)
        assert target.name == "candidate.py", (target, reasons)
        assert "mutation_target_parent_inode_divergence" in reasons, reasons

    # Parent directory symlink swap to outside ROOT must fail closed.
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        parent = root / "ontology" / "safe"
        parent.mkdir(parents=True)
        executor, admitted = admitted_for(root, "safe")

        outside = root.parent / f"{root.name}-outside"
        outside.mkdir(exist_ok=True)
        parent.rmdir()
        os.symlink(str(outside), str(parent))
        try:
            target, reasons = executor._secure_mutation_target(admitted)
            assert target is None, (target, reasons)
            assert "mutation_target_outside_root" in reasons, reasons
        finally:
            parent.unlink(missing_ok=True)
            try:
                outside.rmdir()
            except OSError:
                pass

    print("ACEE6_H_PARENT_TOCTOU_REVALIDATION_OK")


if __name__ == "__main__":
    main()
