#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import json
import tempfile
from pathlib import Path

from validation import oce_v2_global_audit as audit

ROOT = Path.home() / "open-cognitive-ecology"
REQUIRED_DOMAINS = set(audit.DOMAIN_RULES)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_manifest(root: Path, files: dict[str, str], identity: str = "fixture-baseline") -> None:
    payload = {
        "baseline_identity_sha256": identity,
        "functional_file_count": len(files),
        "functional_files": files,
    }
    (root / "p007_baseline_manifest.json").write_text(
        json.dumps(payload, sort_keys=True),
        encoding="utf-8",
    )


def _assert_module_shape(module: dict) -> None:
    required = {
        "path", "sha256", "bytes", "line_count", "parse_status",
        "imports", "calls", "classes", "functions", "primitive",
        "declared_dependencies", "interfaces", "domains",
    }
    assert required.issubset(module)
    assert isinstance(module["path"], str) and module["path"]
    assert len(module["sha256"]) == 64
    int(module["sha256"], 16)
    assert isinstance(module["bytes"], int) and module["bytes"] >= 0
    assert isinstance(module["line_count"], int) and module["line_count"] >= 0
    for key in ("imports", "calls", "classes", "functions",
                "declared_dependencies", "interfaces", "domains"):
        assert isinstance(module[key], list)
        assert module[key] == sorted(module[key])
        assert len(module[key]) == len(set(module[key]))


def test_real_report_internal_consistency() -> None:
    report = audit.build_audit(ROOT)
    modules = report["modules"]
    summary = report["summary"]

    paths = [m["path"] for m in modules]
    assert len(paths) == len(set(paths))
    assert paths == sorted(paths)
    assert summary["python_source_count"] == len(modules)

    for module in modules:
        _assert_module_shape(module)

    parse_errors = [m["path"] for m in modules if m["parse_status"] != "OK"]
    assert report["parse_errors"] == parse_errors
    assert summary["parse_error_count"] == len(parse_errors)
    assert summary["syntax_finding_count"] == len(report["syntax_findings"])
    expected_status = "FINDINGS_PRESENT" if parse_errors else "NO_SYNTAX_FINDINGS"
    assert summary["architecture_findings_status"] == expected_status

    assert summary["static_import_edge_count"] == sum(len(m["imports"]) for m in modules)
    assert summary["static_call_symbol_count"] == sum(len(m["calls"]) for m in modules)
    assert summary["public_interface_symbol_count"] == sum(len(m["interfaces"]) for m in modules)
    print("P008_E2_INTERNAL_CONSISTENCY_OK")


def test_domain_coverage_bijection() -> None:
    report = audit.build_audit(ROOT)
    modules = report["modules"]
    coverage = report["domain_coverage"]
    counts = report["summary"]["domain_module_counts"]

    assert set(coverage) == REQUIRED_DOMAINS
    assert set(counts) == REQUIRED_DOMAINS

    module_paths = {m["path"] for m in modules}
    for domain in sorted(REQUIRED_DOMAINS):
        expected = sorted(m["path"] for m in modules if domain in m["domains"])
        assert coverage[domain] == expected
        assert counts[domain] == len(expected)
        assert set(expected).issubset(module_paths)
        assert len(expected) > 0
    print("P008_E2_DOMAIN_COVERAGE_OK")


def test_real_files_metadata_binding() -> None:
    report = audit.build_audit(ROOT)
    for module in report["modules"]:
        path = ROOT / module["path"]
        assert path.is_file()
        raw = path.read_bytes()
        assert module["sha256"] == hashlib.sha256(raw).hexdigest()
        assert module["bytes"] == len(raw)
        text = raw.decode("utf-8", errors="replace")
        assert module["line_count"] == len(text.splitlines())
        rel = Path(module["path"])
        assert not rel.is_absolute()
        assert ".." not in rel.parts
        assert not audit._is_excluded(rel)
    print("P008_E2_METADATA_BINDING_OK")


def test_baseline_comparison_set_arithmetic() -> None:
    report = audit.build_audit(ROOT)
    baseline = report["baseline_comparison"]
    assert baseline["status"] == "OBSERVED"

    manifest = json.loads((ROOT / "p007_baseline_manifest.json").read_text(encoding="utf-8"))
    raw = manifest["functional_files"]
    locked = set(raw.keys() if isinstance(raw, dict) else raw)
    locked_py = {p for p in locked if p.endswith(".py")}

    present = {
        p.relative_to(ROOT).as_posix()
        for p in audit._baseline_python_paths(ROOT)
    }
    tracked = {
        p.relative_to(ROOT).as_posix()
        for p in audit._git_tracked_python_paths(ROOT)
    }
    audited = {m["path"] for m in report["modules"]}

    assert baseline["baseline_identity_sha256"] == manifest["baseline_identity_sha256"]
    assert baseline["baseline_python_path_count"] == len(locked_py)
    assert baseline["baseline_python_paths_present_now"] == len(present)
    assert baseline["current_tracked_python_path_count"] == len(tracked)
    assert baseline["current_audited_python_source_count"] == len(audited)
    assert baseline["tracked_python_paths_added_vs_baseline"] == sorted(tracked - locked_py)
    assert baseline["baseline_python_paths_missing_now"] == sorted(locked_py - present)
    assert baseline["tracked_python_paths_excluded_from_audit_scope"] == sorted(tracked - audited)
    assert baseline["baseline_python_paths_excluded_from_audit_scope"] == sorted(present - audited)
    print("P008_E2_BASELINE_ARITHMETIC_OK")


def test_provenance_and_epistemic_contract() -> None:
    report = audit.build_audit(ROOT)
    git = report["git"]
    assert set(git) == {"branch", "head", "describe"}
    assert all(isinstance(git[k], str) and git[k] for k in git)

    epistemic = report["epistemic_status"]
    assert epistemic["architecture_completeness"] == "UNKNOWN"
    assert epistemic["runtime_call_exercised"] == "UNKNOWN"
    assert epistemic["dynamic_import_resolution"] == "UNKNOWN"
    assert epistemic["phenomenal_subjectivity"] == "UNDETERMINED"
    assert epistemic["functional_conclusion_only"] is True
    assert isinstance(epistemic["notes"], list) and epistemic["notes"]
    print("P008_E2_PROVENANCE_EPISTEMIC_OK")


def test_fingerprint_contract() -> None:
    first = audit.build_audit(ROOT)
    second = audit.build_audit(ROOT)
    assert first["audit_fingerprint_sha256"] == second["audit_fingerprint_sha256"]
    assert first["generated_at_utc"] != ""
    assert second["generated_at_utc"] != ""

    def stable(report: dict) -> dict:
        result = copy.deepcopy(report)
        result.pop("generated_at_utc", None)
        result.pop("audit_fingerprint_sha256", None)
        return result

    assert stable(first) == stable(second)
    encoded = json.dumps(
        stable(first), sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    assert first["audit_fingerprint_sha256"] == hashlib.sha256(encoded).hexdigest()
    print("P008_E2_FINGERPRINT_CONTRACT_OK")


def test_baseline_drift_detection_fixture() -> None:
    with tempfile.TemporaryDirectory(prefix="p008-e2-drift-") as td:
        root = Path(td)
        kept = root / "kept.py"
        kept.write_text("VALUE = 1\n", encoding="utf-8")
        missing_name = "missing.py"
        _write_manifest(
            root,
            {
                "kept.py": _sha(kept),
                missing_name: "0" * 64,
            },
        )
        report = audit.build_audit(root)
        baseline = report["baseline_comparison"]
        assert baseline["status"] == "OBSERVED"
        assert baseline["baseline_python_path_count"] == 2
        assert baseline["baseline_python_paths_present_now"] == 1
        assert baseline["baseline_python_paths_missing_now"] == [missing_name]
        assert report["summary"]["python_source_count"] == 1
    print("P008_E2_BASELINE_DRIFT_OK")


def test_report_tamper_oracle() -> None:
    report = audit.build_audit(ROOT)
    tampered = copy.deepcopy(report)
    tampered["summary"]["static_import_edge_count"] += 1
    actual = sum(len(m["imports"]) for m in tampered["modules"])
    assert tampered["summary"]["static_import_edge_count"] != actual

    tampered2 = copy.deepcopy(report)
    domain = sorted(REQUIRED_DOMAINS)[0]
    tampered2["summary"]["domain_module_counts"][domain] += 1
    assert tampered2["summary"]["domain_module_counts"][domain] != len(
        tampered2["domain_coverage"][domain]
    )
    print("P008_E2_TAMPER_ORACLE_OK")


def main() -> int:
    test_real_report_internal_consistency()
    test_domain_coverage_bijection()
    test_real_files_metadata_binding()
    test_baseline_comparison_set_arithmetic()
    test_provenance_and_epistemic_contract()
    test_fingerprint_contract()
    test_baseline_drift_detection_fixture()
    test_report_tamper_oracle()
    print("P008_ARCHITECTURAL_COMPLETENESS_CROWN_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
