from pathlib import Path
import json
import time
from datetime import datetime

from ontology.external_compute_expansion_manager import (
    ExternalComputeExpansionManager
)

ROOT = Path.home() / "open-cognitive-ecology"
OUTPUT_DIR = ROOT / "runtime_experiments"
DURATION_SECONDS = 7200
INTERVAL_SECONDS = 30


def run_validation(
    duration_seconds: int = DURATION_SECONDS,
    interval_seconds: int = INTERVAL_SECONDS,
):
    """Run the A3 longitudinal validation explicitly.

    Importing this module must remain side-effect free. The long-running
    experiment is executed only when run_validation() or main() is called.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    output_path = OUTPUT_DIR / f"a3_longitudinal_validation_{timestamp}.jsonl"

    manager = ExternalComputeExpansionManager()
    start = time.time()

    print("Starting A3 longitudinal validation...")
    print(f"Output: {output_path}")

    cycle = 0

    while (time.time() - start) < duration_seconds:
        governance = manager.adaptive_distributed_governance()
        ecological_snapshot = manager.record_ecological_runtime_snapshot()
        distributed_snapshot = manager.record_distributed_runtime_snapshot()

        payload = {
            "cycle": cycle,
            "timestamp": datetime.utcnow().isoformat(),
            "governance": governance,
            "ecological_snapshot": ecological_snapshot,
            "distributed_snapshot": distributed_snapshot,
        }

        with output_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False))
            handle.write("\n")

        print(
            f"[{cycle}] "
            f"mode={governance.get('governance_mode')} "
            f"viability={governance.get('governance_viability_index')} "
            f"drift={governance.get('ecological_drift_score')} "
            f"workers={governance.get('proactive_worker_limit')}"
        )

        cycle += 1
        time.sleep(interval_seconds)

    print("A3 longitudinal validation completed.")
    print(f"Results stored in: {output_path}")

    return {
        "success": True,
        "primitive": "run_a3_longitudinal_validation",
        "cycles_executed": cycle,
        "output_path": str(output_path),
        "duration_seconds": duration_seconds,
        "interval_seconds": interval_seconds,
        "import_side_effect_guarded": True,
    }


def main():
    return run_validation()


if __name__ == "__main__":
    main()
