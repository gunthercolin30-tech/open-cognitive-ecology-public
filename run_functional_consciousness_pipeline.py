#!/usr/bin/env python3

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load_benchmark_module():
    module_path = (
        ROOT
        / "ontology"
        / "functional_consciousness_behavioral_benchmark.py"
    )

    spec = importlib.util.spec_from_file_location(
        "functional_consciousness_behavioral_benchmark",
        module_path,
    )

    module = importlib.util.module_from_spec(spec)

    if spec.loader is None:
        raise RuntimeError("Unable to load benchmark module.")

    spec.loader.exec_module(module)
    return module


DEFAULT_STATE = {
    "self_model": 0.95,
    "autobiographical_memory": 0.90,
    "temporal_self_continuity": 0.92,
    "introspective_reporting": 0.89,
    "uncertainty_awareness": 0.88,
    "internal_conflict_monitoring": 0.87,
    "reflective_goal_revision": 0.91,
    "conscious_decision_trace": 0.90,
    "consciousness_readiness_index": 0.93,
}


def main():
    module = load_benchmark_module()
    results = module.evaluate(DEFAULT_STATE)

    print()
    print("=== Functional Consciousness Benchmark ===")
    print(
        "Score:",
        results["functional_consciousness_benchmark_score"],
    )
    print(
        "Classification:",
        results["classification"],
    )

    return results


if __name__ == "__main__":
    main()
