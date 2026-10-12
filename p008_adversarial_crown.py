#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
from contextlib import contextmanager
from pathlib import Path

from validation import oce_v2_global_audit as audit

ROOT = Path.home() / "open-cognitive-ecology"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_manifest(root: Path, files: dict[str, str] | None = None) -> None:
    files = files or {}
    payload = {
        "baseline_identity_sha256": "fixture-baseline",
        "functional_file_count": len(files),
        "functional_files": files,
    }
    (root / "p007_baseline_manifest.json").write_text(
        json.dumps(payload, sort_keys=True),
        encoding="utf-8",
    )


def _git(root: Path, *args: str) -> str:
    cp = subprocess.run(
        ["git", *args],
        cwd=str(root),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return cp.stdout.strip()


def _init_git(root: Path) -> None:
    _git(root, "init", "-q")
    _git(root, "config", "user.email", "p008@example.invalid")
    _git(root, "config", "user.name", "P008 Fixture")


def _commit_all(root: Path) -> None:
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", "fixture")


@contextmanager
def _cwd(path: Path):
    old = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old)


def test_real_functional_and_known_finding() -> None:
    report = audit.build_audit(ROOT)
    assert report["summary"]["python_source_count"] > 0
    assert report["summary"]["audit_execution_status"] == "COMPLETED"
    findings = report["syntax_findings"]
    ao5 = [x for x in findings if x["path"] == "ao5_extended_acceptance_suite_v2.py"]
    assert len(ao5) == 1
    assert ao5[0]["baseline_member"] is True
    assert ao5[0]["git_tracked"] is False
    assert ao5[0]["classification"] == "BASELINE_SYNTAX_FINDING"
    print("P008_CROWN_FUNCTIONAL_OK")


def test_determinism_and_cwd_independence() -> None:
    first = audit.build_audit(ROOT)
    with tempfile.TemporaryDirectory(prefix="p008-cwd-") as td:
        with _cwd(Path(td)):
            second = audit.build_audit(ROOT)
    assert first["audit_fingerprint_sha256"] == second["audit_fingerprint_sha256"]
    print("P008_CROWN_DETERMINISM_CWD_OK")


def test_real_source_immutability() -> None:
    paths = audit.source_paths(ROOT)
    before = {p.relative_to(ROOT).as_posix(): _sha(p) for p in paths}
    audit.build_audit(ROOT)
    after = {p.relative_to(ROOT).as_posix(): _sha(p) for p in paths}
    assert before == after
    print("P008_CROWN_NON_MUTATION_OK")


def test_unknown_fail_safe() -> None:
    report = audit.build_audit(ROOT)
    e = report["epistemic_status"]
    assert e["architecture_completeness"] == "UNKNOWN"
    assert e["runtime_call_exercised"] == "UNKNOWN"
    assert e["dynamic_import_resolution"] == "UNKNOWN"
    assert e["functional_conclusion_only"] is True
    print("P008_CROWN_UNKNOWN_FAIL_SAFE_OK")


def test_anti_vacuity() -> None:
    with tempfile.TemporaryDirectory(prefix="p008-empty-") as td:
        root = Path(td)
        try:
            audit.source_paths(root)
        except RuntimeError as exc:
            assert "scope is empty" in str(exc)
        else:
            raise AssertionError("empty scope was accepted")
    print("P008_CROWN_ANTI_VACUITY_OK")


def test_syntax_injection_detection() -> None:
    with tempfile.TemporaryDirectory(prefix="p008-syntax-") as td:
        root = Path(td)
        bad = root / "broken.py"
        bad.write_text('x = "unterminated\\n', encoding="utf-8")
        _write_manifest(root, {"broken.py": _sha(bad)})
        report = audit.build_audit(root)
        assert report["summary"]["parse_error_count"] == 1
        assert report["summary"]["architecture_findings_status"] == "FINDINGS_PRESENT"
        assert report["syntax_findings"][0]["classification"] == "BASELINE_SYNTAX_FINDING"
    print("P008_CROWN_SYNTAX_DEGRADATION_OK")


def test_untracked_foreign_file_immunity() -> None:
    with tempfile.TemporaryDirectory(prefix="p008-untracked-") as td:
        root = Path(td)
        _init_git(root)
        tracked = root / "tracked.py"
        tracked.write_text("VALUE = 1\\n", encoding="utf-8")
        _write_manifest(root, {"tracked.py": _sha(tracked)})
        _commit_all(root)
        first = audit.build_audit(root)
        rogue = root / "rogue_local.py"
        rogue.write_text('x = "unterminated\\n', encoding="utf-8")
        second = audit.build_audit(root)
        assert first["audit_fingerprint_sha256"] == second["audit_fingerprint_sha256"]
        assert all(m["path"] != "rogue_local.py" for m in second["modules"])
    print("P008_CROWN_UNTRACKED_IMMUNITY_OK")


def test_replication_package_isolation() -> None:
    with tempfile.TemporaryDirectory(prefix="p008-repl-") as td:
        root = Path(td)
        active = root / "active.py"
        active.write_text("VALUE = 1\n", encoding="utf-8")
        repl = root / "replication_packages" / "pkg" / "broken.py"
        repl.parent.mkdir(parents=True)
        repl.write_text('x = "unterminated\\n', encoding="utf-8")
        _write_manifest(
            root,
            {
                "active.py": _sha(active),
                "replication_packages/pkg/broken.py": _sha(repl),
            },
        )
        report = audit.build_audit(root)
        assert report["summary"]["python_source_count"] == 1
        assert report["summary"]["parse_error_count"] == 0
        assert report["modules"][0]["path"] == "active.py"
    print("P008_CROWN_REPLICATION_ISOLATION_OK")


def test_corrupt_baseline_manifest_fail_safe() -> None:
    with tempfile.TemporaryDirectory(prefix="p008-manifest-") as td:
        root = Path(td)
        _init_git(root)
        tracked = root / "tracked.py"
        tracked.write_text("VALUE = 1\\n", encoding="utf-8")
        (root / "p007_baseline_manifest.json").write_text("{broken", encoding="utf-8")
        _commit_all(root)
        report = audit.build_audit(root)
        assert report["baseline_comparison"]["status"] == "UNKNOWN"
        assert report["summary"]["python_source_count"] == 1
    print("P008_CROWN_MANIFEST_CORRUPTION_OK")


def main() -> int:
    test_real_functional_and_known_finding()
    test_determinism_and_cwd_independence()
    test_real_source_immutability()
    test_unknown_fail_safe()
    test_anti_vacuity()
    test_syntax_injection_detection()
    test_untracked_foreign_file_immunity()
    test_replication_package_isolation()
    test_corrupt_baseline_manifest_fail_safe()
    print("P008_ADVERSARIAL_CROWN_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
