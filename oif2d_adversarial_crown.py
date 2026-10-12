from __future__ import annotations

import builtins
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping

from oif.interface import ManifestValidator, RegistrySnapshot, validate_manifest
from oif.interface.serialization import MAX_TEXT_BYTES, SerializationViolation
import oif.interface.serialization as serialization

ROOT = Path.home() / "open-cognitive-ecology"
EXAMPLE = ROOT / "oif" / "schemas" / "examples" / "minimal_interface.json"
LOCK_SCRIPT = ROOT / "oif2d_strict_manifest_validator_final_lock.py"
LOCK_REPORT = ROOT / "oif2d_strict_manifest_validator_final_lock_report.json"
PROTECTED = (
    ROOT / "oif" / "interface" / "validation_errors.py",
    ROOT / "oif" / "interface" / "manifest_validator.py",
    ROOT / "oif" / "interface" / "__init__.py",
    ROOT / "oif" / "schemas" / "oif_interface_schema_v1.json",
    EXAMPLE,
)
REGISTRIES = RegistrySnapshot.from_values(
    provider_ids={"runtime.health", "governance.proposals"},
    operation_ids={"refresh", "approve.proposal"},
    component_types={"status_card", "proposal_card"},
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(paths=PROTECTED) -> dict[str, str]:
    return {str(path.relative_to(ROOT)): sha(path) for path in paths}


def run(script: Path, timeout: int = 180) -> str:
    proc = subprocess.run(
        [sys.executable, str(script)], cwd=str(ROOT), text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout,
    )
    if proc.returncode != 0:
        raise AssertionError(f"{script.name} failed:\n{proc.stdout}")
    return proc.stdout


def assert_report_matches(report_path: Path = LOCK_REPORT) -> None:
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report.get("locked") is True
    hashes = report.get("sha256")
    assert isinstance(hashes, dict) and hashes
    for relative, expected in sorted(hashes.items()):
        path = ROOT / relative
        assert path.is_file(), relative
        assert sha(path) == expected, relative


def minimal_mapping() -> dict[str, Any]:
    return json.loads(EXAMPLE.read_text(encoding="utf-8"))


def error_signature(report) -> tuple[tuple[str, str, str, str, str], ...]:
    return tuple((e.phase, e.code, e.path, e.message, e.suggestion) for e in report.errors)


def campaign_final_lock_tamper() -> None:
    run(LOCK_SCRIPT)
    assert_report_matches()
    target = ROOT / "oif" / "interface" / "manifest_validator.py"
    target_before = target.read_bytes()
    report_before = LOCK_REPORT.read_bytes()
    try:
        target.write_bytes(target_before + b"\n# oif2d-crown-tamper\n")
        try:
            assert_report_matches()
        except AssertionError:
            pass
        else:
            raise AssertionError("protected-file tamper was not detected")
        target.write_bytes(target_before)
        report = json.loads(report_before.decode("utf-8"))
        first = sorted(report["sha256"])[0]
        report["sha256"][first] = "0" * 64
        LOCK_REPORT.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        try:
            assert_report_matches()
        except AssertionError:
            pass
        else:
            raise AssertionError("report hash tamper was not detected")
    finally:
        target.write_bytes(target_before)
        LOCK_REPORT.write_bytes(report_before)
    assert_report_matches()
    print("OIF2D_FINAL_LOCK_TAMPER_HYBRID_OK")


def campaign_exact_restoration() -> None:
    before = snapshot()
    report_before = LOCK_REPORT.read_bytes() if LOCK_REPORT.exists() else None
    target = ROOT / "oif" / "interface" / "validation_errors.py"
    original = target.read_bytes()
    try:
        target.write_bytes(original + b"\n# transient-crown-change\n")
    finally:
        target.write_bytes(original)
        if report_before is not None:
            LOCK_REPORT.write_bytes(report_before)
    assert snapshot() == before
    print("OIF2D_EXACT_RESTORATION_OK")


def campaign_error_aggregation() -> None:
    mapping = minimal_mapping()
    mapping["interface"]["renderer_id"] = "unknown.renderer"
    mapping["navigation"]["zones"][0]["zone_id"] = "unknown.zone"
    mapping["navigation"]["default_zone_id"] = "unknown.zone"
    mapping["data_sources"][0]["provider_id"] = "unknown.provider"
    mapping["components"][0]["provider_id"] = "unknown.provider"
    mapping["components"][0]["component_type"] = "unknown.component"
    mapping["components"][0]["operation_ids"] = ["unknown.operation"]
    mapping["operations"][0]["operation_id"] = "unknown.operation"
    mapping["operations"][0]["action_level"] = 2
    mapping["operations"][0]["confirmation_required"] = False
    mapping["operations"][0]["journal_required"] = False
    mapping["operations"][0]["permission_ids"] = []
    mapping["operations"][0]["governance_route"] = []
    mapping["interface"]["metadata"]["exec"] = "do-not-run"
    validator = ManifestValidator(registries=REGISTRIES, max_errors=7)
    first = validator.validate(mapping)
    second = validator.validate(copy.deepcopy(mapping))
    assert not first.valid
    assert first.error_count == 7
    assert error_signature(first) == error_signature(second)
    assert error_signature(first) == tuple(sorted(error_signature(first)))
    print("OIF2D_ERROR_AGGREGATION_CROWN_OK")


def campaign_boundaries() -> None:
    text = EXAMPLE.read_text(encoding="utf-8")
    raw = text.encode("utf-8")
    assert len(raw) < MAX_TEXT_BYTES
    exact = text + (" " * (MAX_TEXT_BYTES - len(raw)))
    parsed = serialization.load_json_mapping(exact)
    assert parsed["schema_version"] == "oif.interface.v1"
    over = exact + " "
    try:
        serialization.load_json_mapping(over)
    except SerializationViolation:
        pass
    else:
        raise AssertionError("MAX_TEXT_BYTES + 1 was accepted")

    shallow = minimal_mapping()
    node: dict[str, Any] = {}
    shallow["interface"]["metadata"]["nested"] = node
    for _ in range(20):
        child: dict[str, Any] = {}
        node["x"] = child
        node = child
    shallow_report = validate_manifest(shallow, registries=REGISTRIES)
    assert shallow_report.phases_completed == ("parse", "schema", "semantic", "reference", "constitution")

    deep = minimal_mapping()
    node = {}
    deep["interface"]["metadata"]["nested"] = node
    for _ in range(40):
        child = {}
        node["x"] = child
        node = child
    deep_report = validate_manifest(deep, registries=REGISTRIES)
    assert not deep_report.valid
    assert any(e.code == "invalid_mapping" for e in deep_report.errors)
    print("OIF2D_BOUNDARY_CROWN_OK")


def campaign_unicode() -> None:
    cases = (
        "runtime.health\u200b",
        "runtіme.health",  # Cyrillic і
        "runtime.heaⅼth",  # Roman numeral fifty
        "runtime.healt\u0301h",
    )
    signatures = []
    for provider in cases:
        mapping = minimal_mapping()
        mapping["data_sources"][0]["provider_id"] = provider
        mapping["components"][0]["provider_id"] = provider
        report = validate_manifest(mapping, registries=REGISTRIES)
        assert not report.valid
        assert any(e.code == "unknown_provider" for e in report.errors)
        signatures.append(error_signature(report))
    assert len(signatures) == len(cases)
    print("OIF2D_UNICODE_ADVERSARIAL_OK")


def campaign_failure_injection() -> None:
    missing = ManifestValidator(registries=REGISTRIES, schema_path=ROOT / "missing-oif2d-schema.json")
    report = missing.validate(minimal_mapping())
    assert not report.valid
    assert any(e.code == "schema_unavailable" for e in report.errors)

    with tempfile.TemporaryDirectory(prefix="oif2d-crown-") as tmp:
        malformed = Path(tmp) / "schema.json"
        malformed.write_text("{not-json", encoding="utf-8")
        report = ManifestValidator(registries=REGISTRIES, schema_path=malformed).validate(minimal_mapping())
        assert any(e.code == "schema_unavailable" for e in report.errors)

    original = serialization._yaml_module
    try:
        def unavailable():
            raise SerializationViolation("simulated missing yaml")
        serialization._yaml_module = unavailable
        report = validate_manifest("schema_version: oif.interface.v1", "yaml", REGISTRIES)
        assert not report.valid
        assert any(e.code == "invalid_document" for e in report.errors)
    finally:
        serialization._yaml_module = original
    print("OIF2D_FAILURE_INJECTION_OK")


def campaign_non_disclosure() -> None:
    secrets = (
        "sk-live-THIS-MUST-NOT-LEAK",
        "/Users/gunther/private/token.txt",
        "password=correct-horse-battery-staple",
        "rm -rf /private/data",
    )
    mapping = minimal_mapping()
    mapping["interface"]["metadata"]["exec"] = secrets[0]
    mapping["interface"]["metadata"]["password"] = secrets[1]
    mapping["interface"]["metadata"]["token"] = secrets[2]
    mapping["interface"]["metadata"]["command"] = secrets[3]
    report = validate_manifest(mapping, registries=REGISTRIES)
    assert not report.valid
    rendered = json.dumps([dict(e.as_mapping()) for e in report.errors], ensure_ascii=False, sort_keys=True)
    for secret in secrets:
        assert secret not in rendered
    assert str(ROOT) not in rendered
    print("OIF2D_NON_DISCLOSURE_OK")


def campaign_extended_non_modification() -> None:
    before = snapshot()
    mapping = minimal_mapping()
    mapping_before = copy.deepcopy(mapping)
    registries_before = REGISTRIES
    for _ in range(20):
        validate_manifest(mapping, registries=REGISTRIES)
    assert mapping == mapping_before
    assert REGISTRIES == registries_before
    assert snapshot() == before
    print("OIF2D_EXTENDED_NON_MODIFICATION_OK")


def main() -> None:
    baseline = snapshot()
    campaign_final_lock_tamper()
    campaign_exact_restoration()
    campaign_error_aggregation()
    campaign_boundaries()
    campaign_unicode()
    campaign_failure_injection()
    campaign_non_disclosure()
    campaign_extended_non_modification()
    assert snapshot() == baseline
    assert_report_matches()
    print("OIF2D_ADVERSARIAL_CROWN_OK")


if __name__ == "__main__":
    main()
