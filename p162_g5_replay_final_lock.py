"""Bounded G5 replay check. This never seals the global P162 Final Lock."""
from pathlib import Path
import importlib.util
import sys
import unittest


class ReplayPublicInvariantCheck:
    def step(self, *, inputs, persist=False):
        if persist is not False or inputs != {"context": "synthetic-in-memory"}:
            raise ValueError("synthetic non-persistent context required")
        root = Path(__file__).resolve().parent
        path = root / "tests/test_p162_g5_replay_hardening.py"
        spec = importlib.util.spec_from_file_location("p162_g5_replay_tests", path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        suite = unittest.defaultTestLoader.loadTestsFromModule(module)
        result = unittest.TextTestRunner(verbosity=1).run(suite)
        return {"status": "PASS" if result.wasSuccessful() else "FAIL",
                "tests_run": result.testsRun, "scope": "G5 single-adapter in-process replay",
                "p162_final_lock_executed": False, "authorization_created": False,
                "functional_conclusion_only": True, "phenomenology_undetermined": True}


if __name__ == "__main__":
    result = ReplayPublicInvariantCheck().step(
        inputs={"context": "synthetic-in-memory"}, persist=False)
    print("P162_G5_REPLAY_" + result["status"])
    print("P162_GLOBAL_FINAL_LOCK_NOT_EXECUTED")
    raise SystemExit(0 if result["status"] == "PASS" else 1)
