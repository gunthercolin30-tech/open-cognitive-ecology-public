#!/usr/bin/env python3
import time

from ontology.autonomous_external_collaboration_runner import (
    AutonomousExternalCollaborationRunner,
)
from ontology.longitudinal_reconciliation import (
    LongitudinalReconciliation,
)
from validation.integration_report import (
    _prepare_instance_for_validation,
)


def main():
    external = AutonomousExternalCollaborationRunner()
    external_adapters = _prepare_instance_for_validation(external)

    start = time.monotonic()
    external_result = external.step({})
    external_elapsed = time.monotonic() - start

    assert (
        "external_collaboration_bounded_validation_stub"
        in external_adapters
    )
    assert external_result["validation_probe"] is True
    assert external_result["external_call_performed"] is False
    assert external_result["subprocess_performed"] is False
    assert external_elapsed < 2.0

    longitudinal = LongitudinalReconciliation()
    longitudinal_adapters = _prepare_instance_for_validation(
        longitudinal
    )

    start = time.monotonic()
    longitudinal_result = longitudinal.step()
    longitudinal_elapsed = time.monotonic() - start

    assert (
        "longitudinal_reconciliation_bounded_validation_stub"
        in longitudinal_adapters
    )
    assert longitudinal_result["validation_probe"] is True
    assert longitudinal_result["cycle_count"] == 1
    assert longitudinal_result["persisted"] is False
    assert longitudinal_elapsed < 2.0

    print("ACEE20_GLOBAL_VALIDATION_ADAPTERS_OK")


if __name__ == "__main__":
    main()
