from pathlib import Path
import json
import time
from datetime import datetime

from ontology.external_compute_expansion_manager import (
    ExternalComputeExpansionManager
)

ROOT = Path.home() / "open-cognitive-ecology"

OUTPUT_DIR = ROOT / "runtime_experiments"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TIMESTAMP = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

OUTPUT_PATH = (
    OUTPUT_DIR
    / f"a3_longitudinal_validation_{TIMESTAMP}.jsonl"
)

manager = ExternalComputeExpansionManager()

DURATION_SECONDS = 7200
INTERVAL_SECONDS = 30

start = time.time()

print("Starting A3 longitudinal validation...")
print(f"Output: {OUTPUT_PATH}")

cycle = 0

while (time.time() - start) < DURATION_SECONDS:

    governance = (
        manager.adaptive_distributed_governance()
    )

    ecological_snapshot = (
        manager.record_ecological_runtime_snapshot()
    )

    distributed_snapshot = (
        manager.record_distributed_runtime_snapshot()
    )

    payload = {
        "cycle": cycle,
        "timestamp": datetime.utcnow().isoformat(),
        "governance": governance,
        "ecological_snapshot": ecological_snapshot,
        "distributed_snapshot": distributed_snapshot,
    }

    with OUTPUT_PATH.open(
        "a",
        encoding="utf-8",
    ) as handle:

        handle.write(
            json.dumps(
                payload,
                ensure_ascii=False,
            )
        )

        handle.write("\n")

    print(
        f"[{cycle}] "
        f"mode={governance.get('governance_mode')} "
        f"viability={governance.get('governance_viability_index')} "
        f"drift={governance.get('ecological_drift_score')} "
        f"workers={governance.get('proactive_worker_limit')}"
    )

    cycle += 1

    time.sleep(INTERVAL_SECONDS)

print("A3 longitudinal validation completed.")
print(f"Results stored in: {OUTPUT_PATH}")
