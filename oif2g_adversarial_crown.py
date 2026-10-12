from __future__ import annotations

import copy
import itertools
import json
import time
from pathlib import Path

from oif.interface.complex_manifest_adversarial_guard import (
    AdversarialGuardViolation, assert_yaml_json_parity, canonical_digest,
    degradation_plan, guard_mapping,
)
from oif.interface.complex_manifest_profile import validate_complex_profile
from oif.interface.serialization import load_json_mapping, load_yaml_mapping
from oif2g_test_support import MANIFEST_DIR, NAMES, validator

ROOT = Path(__file__).resolve().parent


def load_pair(name):
    return (load_yaml_mapping(MANIFEST_DIR / (name + ".yaml")),
            load_json_mapping(MANIFEST_DIR / (name + ".json")))


def depth_campaign(base):
    mutated = copy.deepcopy(base)
    cursor = mutated.setdefault("interface", {}).setdefault("metadata", {})
    for index in range(24):
        cursor["n%d" % index] = {}
        cursor = cursor["n%d" % index]
    report = guard_mapping(mutated, max_depth=16)
    assert not report.valid and "depth_limit_exceeded" in report.errors
    print("OIF2G_DEPTH_RECURSION_OK")
    return 1


def namespace_campaign(base):
    mutated = copy.deepcopy(base)
    collision = mutated["components"][0]["component_id"]
    mutated["layout"][0]["regions"][0]["region_id"] = collision
    report = guard_mapping(mutated)
    assert not report.valid and any(e.startswith("cross_namespace_collision") for e in report.errors)
    print("OIF2G_NAMESPACE_COLLISION_OK")
    return 1


def dormant_bypass_campaign():
    report = validator().validate(MANIFEST_DIR / "portal_pilot.yaml")
    assert report.valid
    base = load_yaml_mapping(MANIFEST_DIR / "portal_pilot.yaml")
    mutations = (("enabled", "false"), ("enabled", 0), ("execution_forbidden", "true"), ("activation_stage", "OIF4"))
    rejected = 0
    for key, value in mutations:
        mutated = copy.deepcopy(base)
        operation = mutated["components"][1]["properties"]["dormant_operations"][0]
        operation[key] = value
        spec = validator()._build_specification(mutated)
        profile = validate_complex_profile(spec)
        assert not profile.valid
        rejected += 1
    mutated = copy.deepcopy(base)
    mutated["components"][1]["operation_ids"] = ["refresh-runtime"]
    try:
        spec = validator()._build_specification(mutated)
    except Exception:
        rejected += 1
    else:
        assert not validate_complex_profile(spec).valid
        rejected += 1
    print("OIF2G_DORMANT_BYPASS_OK")
    return rejected


def metadata_campaign(base):
    payloads = (
        ("__import__", "os"), ("entrypoint", "x.y:z"), ("class_path", "x.y"),
        ("url", "file:///etc/passwd"), ("path", "../../secret"), ("home", "$HOME/key"),
    )
    rejected = 0
    for key, value in payloads:
        mutated = copy.deepcopy(base)
        mutated["interface"].setdefault("metadata", {})[key] = value
        report = guard_mapping(mutated)
        assert not report.valid
        rejected += 1
    print("OIF2G_METADATA_ADVERSARIAL_OK")
    return rejected


def divergence_campaign():
    rejected = 0
    for name in NAMES:
        yaml_mapping, json_mapping = load_pair(name)
        assert_yaml_json_parity(yaml_mapping, json_mapping)
        mutated = copy.deepcopy(json_mapping)
        mutated["interface"]["title"] += " mutated"
        try:
            assert_yaml_json_parity(yaml_mapping, mutated)
        except AdversarialGuardViolation:
            rejected += 1
        else:
            raise AssertionError("divergence accepted")
    print("OIF2G_YAML_JSON_DIVERGENCE_OK")
    return rejected


def degradation_campaign(base):
    providers = ("runtime-health", "validation-report", "civilizational-state")
    count = 0
    for mask in itertools.product((False, True), repeat=3):
        available = {provider for provider, enabled in zip(providers, mask) if enabled}
        plan = degradation_plan(base, available)
        assert len(plan) == len(base["components"])
        for component_id, status in plan:
            assert status in {"available", "placeholder"}
        count += 1
    assert count == 8
    print("OIF2G_COMBINATORIAL_DEGRADATION_OK")
    return count


def permutation_campaign(base):
    reordered = copy.deepcopy(base)
    metadata = reordered["interface"]["metadata"]
    reordered["interface"]["metadata"] = dict(reversed(list(metadata.items())))
    assert canonical_digest(base) == canonical_digest(reordered)
    changed = copy.deepcopy(base)
    changed["navigation"]["zones"][0]["order"] = 999
    assert canonical_digest(base) != canonical_digest(changed)
    print("OIF2G_PERMUTATION_DETERMINISM_OK")
    return 2


def scale_campaign(base):
    fixture = copy.deepcopy(base)
    template = fixture["components"][0]
    fixture["components"] = []
    for index in range(1024):
        component = copy.deepcopy(template)
        component["component_id"] = "scale.component.%04d" % index
        fixture["components"].append(component)
    fixture["layout"] = []
    for layout_index in range(64):
        regions = []
        for region_index in range(4):
            start = layout_index * 16 + region_index * 4
            regions.append({
                "region_id": "scale.region.%03d.%d" % (layout_index, region_index),
                "order": region_index,
                "component_ids": ["scale.component.%04d" % ((start + offset) % 1024) for offset in range(4)],
                "properties": {"composition": {"kind": "grid"}},
            })
        fixture["layout"].append({"layout_id": "scale.layout.%03d" % layout_index, "regions": regions})
    fixture["navigation"]["zones"] = []
    for index in range(32):
        fixture["navigation"]["zones"].append({
            "zone_id": "scale.zone.%02d" % index, "label": "Zone %d" % index,
            "description": "Scale fixture", "order": index,
            "layout_id": "scale.layout.%03d" % index, "access_mode": "read_only",
        })
    fixture["navigation"]["default_zone_id"] = "scale.zone.00"
    start = time.monotonic()
    first = guard_mapping(fixture, max_nodes=50000)
    elapsed = time.monotonic() - start
    assert first.valid, first.errors
    assert elapsed < 5.0, elapsed
    assert canonical_digest(fixture) == canonical_digest(copy.deepcopy(fixture))
    print("OIF2G_SCALE_STABILITY_OK")
    return {"components": 1024, "regions": 256, "layouts": 64, "zones": 32, "elapsed": elapsed}


def main():
    base, paired = load_pair("portal_pilot")
    assert_yaml_json_parity(base, paired)
    baseline = guard_mapping(base)
    assert baseline.valid, baseline.errors
    mutations = 0
    mutations += depth_campaign(base)
    mutations += namespace_campaign(base)
    mutations += dormant_bypass_campaign()
    mutations += metadata_campaign(base)
    mutations += divergence_campaign()
    mutations += degradation_campaign(base)
    mutations += permutation_campaign(base)
    scale = scale_campaign(base)
    report = {
        "milestone": "OIF-2G-adversarial-crown",
        "campaign_count": 8,
        "mutation_count": mutations,
        "unexpected_acceptance_count": 0,
        "operation_execution": False,
        "functional_only": True,
        "scale_fixture": scale,
    }
    (ROOT / "oif2g_adversarial_crown_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print("OIF2G_ADVERSARIAL_CROWN_OK")

if __name__ == "__main__":
    main()
