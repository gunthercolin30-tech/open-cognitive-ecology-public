import stat
from pathlib import Path
from tempfile import TemporaryDirectory

from acee6_b1_test_support import fixed_now, valid_acee5_decision
from ontology.acee_installation_executor import AceeInstallationExecutor


with TemporaryDirectory() as tmp:
    root = Path(tmp)
    (root / "ontology").mkdir()

    result = AceeInstallationExecutor(
        root=root,
        now_utc=fixed_now(),
    ).step(
        inputs=valid_acee5_decision(root),
        persist=True,
    )

    transaction_dir = Path(result["transaction_directory"])
    files = (
        Path(result["journal_path"]),
        Path(result["latest_state_path"]),
        Path(result["snapshot_path"]),
    )

    assert transaction_dir.is_dir()
    directory_mode = stat.S_IMODE(transaction_dir.stat().st_mode)
    assert directory_mode & stat.S_IWOTH == 0

    for path in files:
        assert path.is_file()
        assert not path.is_symlink()
        mode = stat.S_IMODE(path.stat().st_mode)
        assert mode & stat.S_IWOTH == 0
        assert mode & stat.S_IWGRP == 0
        assert path.stat().st_nlink == 1

    assert result["candidate_written"] is False
    assert result["inventory_modified"] is False

print("ACEE6_C_FILESYSTEM_PERMISSIONS_OK")
