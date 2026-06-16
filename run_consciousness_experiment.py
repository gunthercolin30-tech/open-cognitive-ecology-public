#!/usr/bin/env python3
'''
Standalone experimental runner for the consciousness experiment.
This script does not modify main.py.
'''

from pprint import pprint

from ontology.consciousness_experiment_runner import (
    ConsciousnessExperimentRunner,
)


def main():
    runner = ConsciousnessExperimentRunner()

    report = runner.run(
        scores=[0.92, 0.87, 0.78, 0.84, 0.91]
    )

    print("\n=== Consciousness Experiment Report ===")
    pprint(report)


if __name__ == "__main__":
    main()
