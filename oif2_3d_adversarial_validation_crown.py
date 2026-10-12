from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

ROOT = Path.home() / "open-cognitive-ecology"


def fail(message: str) -> None:
    raise AssertionError(message)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def make_ready_fixture(root: Path) -> None:
    base = root / "representative_succession"
    write_json(
        base / "civilizational_identity_preservation.json",
        {
            "civilizational_identity_preserved": True,
            "civilizational_identity_loss_detected": False,
            "recovery_required": False,
        },
    )
    write_json(
        base / "representative_registry.json",
        {
            "current_representative": {
                "civilization_identity": "Open Cognitive Ecology Society",
                "representative_id": "REP-TEST",
                "representative_name": "Test Representative",
                "representative_is_central": False,
                "representative_is_revocable": True,
                "status": "active",
            }
        },
    )
    write_json(
        base / "continuity_metrics_engine.json",
        {
            "continuity_validated": True,
            "continuity_decision": "validated",
            "recovery_required": False,
        },
    )
    write_json(
        base / "succession_execution.json",
        {
            "latest_succession_event": {
                "execution_status": "not_requested",
                "succession_executed": False,
                "civilizational_continuity_preserved": True,
            }
        },
    )


def source_hashes(root: Path) -> dict[str, str]:
    base = root / "representative_succession"
    return {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(base.glob("*.json"))
    }


def test_ready_and_epistemic_contract(adapter_cls: type) -> None:
    with tempfile.TemporaryDirectory(prefix="oif2_3d_ready_") as tmp:
        root = Path(tmp)
        make_ready_fixture(root)
        result = adapter_cls(root=root).read()
        assert result["status"] == "ready"
        assert result["available_source_count"] == 4
        assert result["invalid_source_count"] == 0
        assert result["read_only"] is True
        assert result["translation_only"] is True
        assert result["producer_execution"] is False
        assert result["synthetic_cross_source_score"] is False
        assert result["consciousness_proven"] is False
        assert result["subjectivity_proven"] is False
        assert result["qualia_proven"] is False
        assert result["phenomenology_proven"] is False
        assert result["functional_conclusion_only"] is True
        assert result["phenomenology_undetermined"] is True


def test_json_adversaries(adapter_cls: type) -> None:
    cases = {
        "root_array": "[]",
        "nan": '{"continuity_validated": NaN}',
        "infinity": '{"continuity_validated": Infinity}',
        "negative_infinity": '{"continuity_validated": -Infinity}',
        "truncated": '{"continuity_validated": true',
        "invalid_utf8": None,
    }
    for name, content in cases.items():
        with tempfile.TemporaryDirectory(prefix=f"oif2_3d_{name}_") as tmp:
            root = Path(tmp)
            make_ready_fixture(root)
            target = root / "representative_succession/continuity_metrics_engine.json"
            if content is None:
                target.write_bytes(b"\xff\xfe\xfd")
            else:
                target.write_text(content, encoding="utf-8")
            section = adapter_cls(root=root).read()["sections"]["continuity_state"]
            assert section["availability"] == "invalid", name
            assert section["status"] == "unavailable", name
            assert section["payload"] is None, name


def test_size_and_filesystem_adversaries(adapter_cls: type, max_bytes: int) -> None:
    with tempfile.TemporaryDirectory(prefix="oif2_3d_size_") as tmp:
        root = Path(tmp)
        make_ready_fixture(root)
        target = root / "representative_succession/continuity_metrics_engine.json"
        target.write_bytes(b"{" + b" " * max_bytes + b"}")
        section = adapter_cls(root=root).read()["sections"]["continuity_state"]
        assert section["availability"] == "invalid"
        assert section["error_type"] == "SourceTooLarge"

    with tempfile.TemporaryDirectory(prefix="oif2_3d_directory_") as tmp:
        root = Path(tmp)
        make_ready_fixture(root)
        target = root / "representative_succession/continuity_metrics_engine.json"
        target.unlink()
        target.mkdir()
        section = adapter_cls(root=root).read()["sections"]["continuity_state"]
        assert section["availability"] == "invalid"
        assert section["error_type"] == "UnsafeSource"

    with tempfile.TemporaryDirectory(prefix="oif2_3d_symlink_") as tmp:
        root = Path(tmp)
        make_ready_fixture(root)
        target = root / "representative_succession/continuity_metrics_engine.json"
        real = root / "real.json"
        shutil.move(target, real)
        target.symlink_to(real)
        section = adapter_cls(root=root).read()["sections"]["continuity_state"]
        assert section["availability"] == "invalid"
        assert section["error_type"] == "DirectSourceSymlinkRejected"


def test_whitelist_enforcement(adapter_cls: type, format_error: type) -> None:
    with tempfile.TemporaryDirectory(prefix="oif2_3d_whitelist_") as tmp:
        root = Path(tmp)
        make_ready_fixture(root)
        adapter = adapter_cls(root=root)
        unauthorized = root / "representative_succession/unauthorized.json"
        write_json(unauthorized, {})
        try:
            adapter._governed_paths(unauthorized)
        except format_error:
            pass
        else:
            fail("unauthorized source path was accepted")


def test_status_matrix(adapter_cls: type) -> None:
    with tempfile.TemporaryDirectory(prefix="oif2_3d_status_") as tmp:
        root = Path(tmp)
        make_ready_fixture(root)
        base = root / "representative_succession"

        write_json(
            base / "civilizational_identity_preservation.json",
            {
                "civilizational_identity_preserved": False,
                "civilizational_identity_loss_detected": True,
                "recovery_required": True,
            },
        )
        assert adapter_cls(root=root).read()["status"] == "degraded"

        make_ready_fixture(root)
        registry = json.loads((base / "representative_registry.json").read_text())
        registry["current_representative"]["representative_is_central"] = True
        write_json(base / "representative_registry.json", registry)
        section = adapter_cls(root=root).read()["sections"]["representative_state"]
        assert section["status"] == "degraded"

        make_ready_fixture(root)
        (base / "succession_execution.json").unlink()
        result = adapter_cls(root=root).read()
        assert result["status"] == "degraded"
        assert result["sections"]["succession_state"]["availability"] == "missing"


def test_source_immutability_and_copy_isolation(adapter_cls: type) -> None:
    with tempfile.TemporaryDirectory(prefix="oif2_3d_immutable_") as tmp:
        root = Path(tmp)
        make_ready_fixture(root)
        before = source_hashes(root)
        adapter = adapter_cls(root=root)
        first = adapter.read()
        first["sections"]["representative_state"]["payload"]["current_representative"][
            "representative_name"
        ] = "MUTATED-COPY"
        second = adapter.read()
        actual = second["sections"]["representative_state"]["payload"][
            "current_representative"
        ]["representative_name"]
        assert actual == "Test Representative"
        assert source_hashes(root) == before


def test_change_during_read_rejected(adapter_cls: type, format_error: type) -> None:
    with tempfile.TemporaryDirectory(prefix="oif2_3d_toctou_") as tmp:
        root = Path(tmp)
        make_ready_fixture(root)
        adapter = adapter_cls(root=root)
        original = adapter._read_source
        triggered = False

        def wrapped(name: str, path: Path) -> dict[str, Any]:
            nonlocal triggered
            result = original(name, path)
            if not triggered:
                triggered = True
                target = root / "representative_succession/succession_execution.json"
                current = target.read_text(encoding="utf-8")
                target.write_text(current + " ", encoding="utf-8")
            return result

        adapter._read_source = wrapped  # type: ignore[method-assign]
        try:
            adapter.read()
        except format_error as exc:
            assert "changed during read" in str(exc)
        else:
            fail("TOCTOU source mutation was not rejected")


def test_concurrency_and_performance(adapter_cls: type) -> None:
    with tempfile.TemporaryDirectory(prefix="oif2_3d_concurrency_") as tmp:
        root = Path(tmp)
        make_ready_fixture(root)
        adapter = adapter_cls(root=root)
        errors: list[BaseException] = []
        lock = threading.Lock()

        def worker(_: int) -> str:
            try:
                result = adapter.read()
                assert result["status"] == "ready"
                assert result["available_source_count"] == 4
                return result["sections"]["representative_state"]["status"]
            except BaseException as exc:
                with lock:
                    errors.append(exc)
                return "error"

        started = time.perf_counter()
        with ThreadPoolExecutor(max_workers=16) as executor:
            outputs = list(executor.map(worker, range(256)))
        elapsed = time.perf_counter() - started
        assert not errors, errors
        assert set(outputs) == {"ready"}
        # Generous ceiling: detects pathological regressions, not machine speed.
        assert elapsed < 15.0, f"256 reads took {elapsed:.3f}s"
        print(f"concurrent_reads=256 elapsed_seconds={elapsed:.3f}")


def test_provider_and_shell_contract() -> None:
    from oif.application.default_providers import build_default_provider_specs
    from oif.application.shell_service import OIF2ReadOnlyApplicationService

    providers = build_default_provider_specs(root=ROOT)
    matches = [spec for spec in providers if spec.name == "civilizational-state"]
    assert len(matches) == 1
    assert matches[0].zone == "memory"
    snapshot = OIF2ReadOnlyApplicationService(providers=providers).snapshot()
    cards = {card["provider"]: card for card in snapshot["cards"]}
    card = cards["civilizational-state"]
    assert card["zone"] == "memory"
    assert card["access"] == "read_only"


def test_final_lock_integrity() -> None:
    report_path = ROOT / "oif2_3d_civilizational_state_adapter_final_lock_report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["status"] == "locked"
    assert report["zone"] == "memory"
    assert report["synthetic_cross_source_score"] is False
    for relative, expected in report["hashes"].items():
        actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        assert actual == expected, relative

    tampered = dict(report)
    tampered["zone"] = "identity"
    assert tampered != report
    assert tampered["zone"] != "memory"


def main() -> int:
    if not ROOT.is_dir():
        fail(f"repository absent: {ROOT}")

    from oif.adapters.civilizational_state_adapter import (
        MAX_SOURCE_BYTES,
        CivilizationalStateAdapter,
        CivilizationalStateFormatError,
    )

    tests = [
        ("ready_epistemic_contract", lambda: test_ready_and_epistemic_contract(CivilizationalStateAdapter)),
        ("json_adversaries", lambda: test_json_adversaries(CivilizationalStateAdapter)),
        ("size_filesystem_adversaries", lambda: test_size_and_filesystem_adversaries(CivilizationalStateAdapter, MAX_SOURCE_BYTES)),
        ("whitelist_enforcement", lambda: test_whitelist_enforcement(CivilizationalStateAdapter, CivilizationalStateFormatError)),
        ("status_matrix", lambda: test_status_matrix(CivilizationalStateAdapter)),
        ("immutability_copy_isolation", lambda: test_source_immutability_and_copy_isolation(CivilizationalStateAdapter)),
        ("toctou_rejection", lambda: test_change_during_read_rejected(CivilizationalStateAdapter, CivilizationalStateFormatError)),
        ("concurrency_performance", lambda: test_concurrency_and_performance(CivilizationalStateAdapter)),
        ("provider_shell_contract", test_provider_and_shell_contract),
        ("final_lock_integrity", test_final_lock_integrity),
    ]

    started = time.perf_counter()
    for name, test in tests:
        test()
        print(f"OIF2_3D_CROWN_{name.upper()}_OK")
    elapsed = time.perf_counter() - started
    print(f"OIF2_3D_ADVERSARIAL_VALIDATION_CROWN_OK total_seconds={elapsed:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
