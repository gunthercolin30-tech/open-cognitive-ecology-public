"""Compile the bounded refinement and run its synthetic public invariants."""
from pathlib import Path
import py_compile
import tempfile
from p162_g5_replay_final_lock import ReplayPublicInvariantCheck


def main():
    root = Path(__file__).resolve().parent
    # Keep bytecode outside the project; macOS uses /private/tmp.
    parent = "/private/tmp" if Path("/private/tmp").is_dir() else None
    with tempfile.TemporaryDirectory(prefix="p162-g5-compile-", dir=parent) as directory:
        for index, relative in enumerate(("ontology/governed_effector_adapter.py",
                                          "tests/test_p162_g5_replay_hardening.py",
                                          "p162_g5_replay_final_lock.py")):
            py_compile.compile(str(root / relative),
                               cfile=str(Path(directory) / (str(index) + ".pyc")),
                               doraise=True)
    result = ReplayPublicInvariantCheck().step(
        inputs={"context": "synthetic-in-memory"}, persist=False)
    print("P162_G5_FAST_ACCEPTANCE_" + result["status"])
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
