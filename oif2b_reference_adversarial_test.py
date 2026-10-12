from __future__ import annotations
from dataclasses import replace
from oif.interface import SpecificationViolation
from oif.interface.models import (
    ComponentSpecification,
    DataSourceSpecification,
    OperationSpecification,
)
from oif2b_test_support import build_spec

spec = build_spec()

cases = [
    lambda: replace(
        spec,
        data_sources=(
            DataSourceSpecification(
                provider_id="runtime.health",
                zone_id="missing.zone",
                data_contract="runtime.health.v1",
            ),
        ),
    ),
    lambda: replace(
        spec,
        components=(
            ComponentSpecification(
                component_id="status.card",
                component_type="status_card",
                provider_id="missing.provider",
            ),
        ),
    ),
    lambda: replace(
        spec,
        components=(
            ComponentSpecification(
                component_id="status.card",
                component_type="status_card",
                provider_id="runtime.health",
                operation_ids=("missing.operation",),
            ),
        ),
    ),
    lambda: replace(
        spec,
        operations=(
            OperationSpecification(
                operation_id="refresh",
                action_level=spec.operations[0].action_level,
                permission_ids=("missing.permission",),
            ),
        ),
    ),
]

for build in cases:
    try:
        build()
        raise AssertionError("dangling reference accepted")
    except SpecificationViolation:
        pass

print("OIF2B_REFERENCE_ADVERSARIAL_OK")
