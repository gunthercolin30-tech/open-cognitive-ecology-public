"""Compile the bounded refinement and run its synthetic public invariants."""
from pathlib import Path
import py_compile
import tempfile
from p162_pc4_recovery_final_lock import RecoveryPublicInvariantCheck


def main():
    root = Path(__file__).resolve().parent
    # Keep bytecode outside the project; macOS uses /private/tmp.
    parent = "/private/tmp" if Path("/private/tmp").is_dir() else None
    with tempfile.TemporaryDirectory(prefix="p162-pc4-compile-", dir=parent) as directory:
        for index, relative in enumerate(("ontology/reservation_recovery_manager.py",
                                          "tests/test_p162_pc4_recovery_hardening.py",
                                          "p162_pc4_recovery_final_lock.py")):
            py_compile.compile(str(root / relative),
                               cfile=str(Path(directory) / (str(index) + ".pyc")),
                               doraise=True)
    result = RecoveryPublicInvariantCheck().step(
        inputs={"context": "synthetic-disposable-journal"}, persist=False)
    print("P162_PC4_RECOVERY_FAST_ACCEPTANCE_" + result["status"])
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
