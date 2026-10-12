from __future__ import annotations

import hashlib
import inspect
import json
import subprocess
import sys
import time
import tracemalloc
from pathlib import Path
from types import MappingProxyType

ROOT = Path.home() / "open-cognitive-ecology"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from oif.application.shell_service import ProviderSpec
from oif.interface.reference_catalog import (
    ReferenceCatalogue,
    ReferenceCatalogueViolation,
    ReferenceDescriptor,
    ReferenceKind,
)
from oif.interface.reference_resolver import (
    ReferenceRequest,
    ReferenceResolutionError,
    SecureReferenceResolver,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _expect_error(code: str, callback) -> None:
    try:
        callback()
    except ReferenceResolutionError as exc:
        assert exc.code == code, (exc.code, code)
        return
    raise AssertionError("expected ReferenceResolutionError: %s" % code)


def _descriptor(reference_id: str, kind: ReferenceKind = ReferenceKind.PROVIDER, **kwargs):
    return ReferenceDescriptor(reference_id=reference_id, kind=kind, **kwargs)


def campaign_catalogue_tamper() -> None:
    original = ReferenceCatalogue.from_entries((
        _descriptor("runtime-health", zone_id="runtime", metadata={"read_only": True}),
    ))
    replacement = ReferenceCatalogue.from_entries((
        _descriptor("runtime-health", zone_id="system", metadata={"read_only": True}),
    ))
    assert original.catalogue_sha256 != replacement.catalogue_sha256

    resolver = SecureReferenceResolver(replacement)
    _expect_error(
        "catalogue_hash_mismatch",
        lambda: resolver.resolve(ReferenceRequest(
            "runtime-health",
            ReferenceKind.PROVIDER,
            expected_catalogue_sha256=original.catalogue_sha256,
        )),
    )

    resolved = SecureReferenceResolver(original).resolve_exact(
        "runtime-health", ReferenceKind.PROVIDER, "runtime"
    )
    assert resolved.catalogue_sha256 == original.catalogue_sha256
    print("OIF2E_CATALOGUE_TAMPER_OK")


def campaign_source_mutation_isolation() -> None:
    source_metadata = {
        "labels": ["runtime", "read-only"],
        "nested": {"enabled": True, "limits": [1, 2, 3]},
    }
    entries = [
        _descriptor("runtime-health", zone_id="runtime", metadata=source_metadata),
    ]
    catalogue = ReferenceCatalogue.from_entries(entries)
    before_hash = catalogue.catalogue_sha256
    before_record = dict(catalogue.entries[0].canonical_record())

    source_metadata["labels"].append("mutated")
    source_metadata["nested"]["enabled"] = False
    source_metadata["nested"]["limits"].append(999)
    entries.clear()

    assert catalogue.catalogue_sha256 == before_hash
    assert dict(catalogue.entries[0].canonical_record()) == before_record
    assert tuple(catalogue.entries[0].metadata["labels"]) == ("runtime", "read-only")
    print("OIF2E_SOURCE_MUTATION_ISOLATION_OK")


def campaign_cross_kind_collision() -> None:
    shared = "shared-reference"
    catalogue = ReferenceCatalogue.from_entries(tuple(
        _descriptor(shared, kind, zone_id="system")
        for kind in ReferenceKind
    ))
    resolver = SecureReferenceResolver(catalogue)

    for kind in ReferenceKind:
        resolved = resolver.resolve_exact(shared, kind, "system")
        assert resolved.kind is kind

    _expect_error(
        "unknown_reference",
        lambda: resolver.resolve_exact("missing-reference", ReferenceKind.PROVIDER),
    )

    try:
        ReferenceCatalogue.from_entries((
            _descriptor(shared, ReferenceKind.PROVIDER),
            _descriptor(shared, ReferenceKind.PROVIDER),
        ))
    except ReferenceCatalogueViolation:
        pass
    else:
        raise AssertionError("same-kind duplicate was accepted")

    print("OIF2E_CROSS_KIND_COLLISION_OK")


def campaign_metadata_adversarial() -> None:
    metadata = {
        "booleans": [True, False],
        "numbers": [0, 1, -2, 3.5],
        "unicode": "écologie-cognitive-安全",
        "nested": {"alpha": {"beta": ["gamma", {"delta": None}]}},
        "unordered": {"b": 2, "a": 1},
    }
    descriptor = _descriptor("metadata-safe", metadata=metadata)
    assert isinstance(descriptor.metadata, MappingProxyType)
    assert isinstance(descriptor.metadata["booleans"], tuple)

    too_deep = current = {}
    for _ in range(40):
        nxt = {}
        current["level"] = nxt
        current = nxt
    try:
        _descriptor("metadata-deep", metadata=too_deep)
    except ReferenceCatalogueViolation:
        pass
    else:
        raise AssertionError("excessive metadata depth was accepted")

    cyclic = {}
    cyclic["self"] = cyclic
    try:
        _descriptor("metadata-cycle", metadata=cyclic)
    except (ReferenceCatalogueViolation, RecursionError):
        pass
    else:
        raise AssertionError("cyclic metadata was accepted")

    try:
        _descriptor("metadata-callable", metadata={"value": lambda: None})
    except ReferenceCatalogueViolation:
        pass
    else:
        raise AssertionError("callable metadata was accepted")

    try:
        _descriptor("metadata-forbidden", metadata={"callable": "x"})
    except ReferenceCatalogueViolation:
        pass
    else:
        raise AssertionError("forbidden metadata key was accepted")

    print("OIF2E_METADATA_ADVERSARIAL_OK")


def campaign_callable_non_exposure() -> None:
    calls = {"count": 0}

    def provider():
        calls["count"] += 1
        return {"unexpected": True}

    specs = (ProviderSpec(name="runtime-health", zone="runtime", provider=provider),)
    catalogue = ReferenceCatalogue.from_provider_specs(specs)
    resolved = SecureReferenceResolver(catalogue).resolve_exact(
        "runtime-health", ReferenceKind.PROVIDER, "runtime"
    )

    assert calls["count"] == 0
    assert not callable(resolved)
    assert not callable(resolved.metadata)

    forbidden_names = {"provider", "callable", "module", "qualname", "globals", "closure"}
    public_names = {name.casefold() for name in dir(resolved) if not name.startswith("_")}
    assert forbidden_names.isdisjoint(public_names)

    representation = repr(resolved)
    assert "function provider" not in representation
    assert "__globals__" not in representation
    assert provider.__qualname__ not in representation

    record = json.dumps(dict(catalogue.entries[0].canonical_record()), sort_keys=True)
    assert provider.__qualname__ not in record
    assert "0x" not in record
    assert calls["count"] == 0
    print("OIF2E_CALLABLE_NON_EXPOSURE_OK")


def _snapshot_sets(snapshot):
    return {
        ReferenceKind.PROVIDER: frozenset(snapshot.provider_ids),
        ReferenceKind.OPERATION: frozenset(snapshot.operation_ids),
        ReferenceKind.COMPONENT: frozenset(snapshot.component_types),
        ReferenceKind.RENDERER: frozenset(snapshot.renderer_ids),
    }


def campaign_snapshot_catalogue_coherence() -> None:
    catalogue = ReferenceCatalogue.from_entries((
        _descriptor("runtime-health", ReferenceKind.PROVIDER, zone_id="runtime"),
        _descriptor("refresh-runtime", ReferenceKind.OPERATION, zone_id="runtime"),
        _descriptor("health-card", ReferenceKind.COMPONENT, zone_id="runtime"),
        _descriptor("nicegui", ReferenceKind.RENDERER, zone_id="system"),
    ))
    snapshot = catalogue.registry_snapshot()
    snapshot_sets = _snapshot_sets(snapshot)
    for kind in ReferenceKind:
        assert snapshot_sets[kind] == catalogue.ids(kind)

    stale = ReferenceCatalogue.from_entries((
        _descriptor("runtime-health", ReferenceKind.PROVIDER, zone_id="runtime"),
        _descriptor("other-operation", ReferenceKind.OPERATION, zone_id="runtime"),
        _descriptor("health-card", ReferenceKind.COMPONENT, zone_id="runtime"),
        _descriptor("nicegui", ReferenceKind.RENDERER, zone_id="system"),
    ))
    stale_snapshot = stale.registry_snapshot()
    differences = {
        kind.value: (
            snapshot_sets[kind] - _snapshot_sets(stale_snapshot)[kind],
            _snapshot_sets(stale_snapshot)[kind] - snapshot_sets[kind],
        )
        for kind in ReferenceKind
    }
    assert differences["operation"] == (
        frozenset({"refresh-runtime"}), frozenset({"other-operation"})
    )
    print("OIF2E_SNAPSHOT_CATALOGUE_COHERENCE_OK")


def campaign_final_lock_tamper() -> None:
    report_path = ROOT / "oif2e_secure_reference_resolver_final_lock_report.json"
    lock_script = ROOT / "oif2e_secure_reference_resolver_final_lock.py"
    target = ROOT / "oif/interface/reference_resolver.py"

    assert lock_script.is_file(), lock_script
    assert report_path.is_file(), "run OIF2E Final Lock before the adversarial crown"

    report_bytes = report_path.read_bytes()
    target_bytes = target.read_bytes()
    try:
        report = json.loads(report_bytes.decode("utf-8"))
        expected = report["sha256"]["oif/interface/reference_resolver.py"]
        assert expected == hashlib.sha256(target_bytes).hexdigest()

        target.write_bytes(target_bytes + b"\n# OIF2E_CROWN_TEMPORARY_TAMPER\n")
        assert hashlib.sha256(target.read_bytes()).hexdigest() != expected

        target.write_bytes(target_bytes)
        assert _sha256(target) == expected

        tampered_report = dict(report)
        tampered_report["sha256"] = dict(report["sha256"])
        tampered_report["sha256"]["oif/interface/reference_resolver.py"] = "0" * 64
        report_path.write_text(json.dumps(tampered_report, sort_keys=True) + "\n", encoding="utf-8")
        loaded = json.loads(report_path.read_text(encoding="utf-8"))
        assert loaded["sha256"]["oif/interface/reference_resolver.py"] != _sha256(target)
    finally:
        target.write_bytes(target_bytes)
        report_path.write_bytes(report_bytes)

    assert target.read_bytes() == target_bytes
    assert report_path.read_bytes() == report_bytes
    print("OIF2E_FINAL_LOCK_TAMPER_OK")


def campaign_scale_stability() -> None:
    count_per_kind = 300
    entries = []
    for kind in ReferenceKind:
        for index in range(count_per_kind):
            entries.append(_descriptor(
                "%s-%04d" % (kind.value, index),
                kind,
                zone_id="system",
                metadata={"index": index, "read_only": True},
            ))

    tracemalloc.start()
    started = time.monotonic()
    catalogue_a = ReferenceCatalogue.from_entries(entries)
    catalogue_b = ReferenceCatalogue.from_entries(reversed(entries))
    resolver = SecureReferenceResolver(catalogue_a)
    for kind in ReferenceKind:
        for index in (0, 1, 149, 299):
            expected_id = "%s-%04d" % (kind.value, index)
            resolved = resolver.resolve_exact(expected_id, kind, "system")
            assert resolved.reference_id == expected_id
            assert resolved.metadata["index"] == index
    elapsed = time.monotonic() - started
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    assert len(catalogue_a.entries) == len(ReferenceKind) * count_per_kind
    assert catalogue_a.catalogue_sha256 == catalogue_b.catalogue_sha256
    assert elapsed < 15.0, elapsed
    assert peak < 64 * 1024 * 1024, peak
    assert current <= peak
    print("OIF2E_SCALE_STABILITY_OK")


def main() -> int:
    campaigns = (
        campaign_catalogue_tamper,
        campaign_source_mutation_isolation,
        campaign_cross_kind_collision,
        campaign_metadata_adversarial,
        campaign_callable_non_exposure,
        campaign_snapshot_catalogue_coherence,
        campaign_final_lock_tamper,
        campaign_scale_stability,
    )
    for campaign in campaigns:
        campaign()
    print("OIF2E_ADVERSARIAL_CROWN_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
