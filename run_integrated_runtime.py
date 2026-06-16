#!/usr/bin/env python3
"""
run_integrated_runtime.py

Point d'entrée standard pour lancer le runtime civilizational intégré.

Exemples:
    python3 run_integrated_runtime.py
    python3 run_integrated_runtime.py --sleep 2
    python3 run_integrated_runtime.py --sleep 1 --max-cycles 3
"""

import argparse
import sys
import time
from pprint import pprint

from ontology.integrated_civilizational_runtime import IntegratedCivilizationalRuntime


def parse_args():
    parser = argparse.ArgumentParser(
        description="Launch the Integrated Civilizational Runtime."
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=5.0,
        help="Delay in seconds between cycles (default: 5.0).",
    )
    parser.add_argument(
        "--max-cycles",
        type=int,
        default=None,
        help="Maximum number of cycles to execute. If omitted, run forever.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Reduce console output.",
    )
    return parser.parse_args()


def run_bounded(runtime, sleep_seconds, max_cycles, quiet=False):
    cycle = 0
    start = time.time()

    try:
        while cycle < max_cycles:
            result = runtime.step()
            cycle += 1

            if not quiet:
                print(f"=== Cycle {cycle} ===")
                pprint(result)
                print()

            if cycle < max_cycles and sleep_seconds > 0:
                time.sleep(sleep_seconds)

    except KeyboardInterrupt:
        print("\nRuntime interrupted by user.")

    elapsed = time.time() - start

    summary = {
        "status": "completed",
        "cycles_executed": cycle,
        "elapsed_seconds": round(elapsed, 3),
    }

    if not quiet:
        print("=== Summary ===")
        pprint(summary)

    return summary


def main():
    args = parse_args()

    runtime = IntegratedCivilizationalRuntime()

    if args.max_cycles is None:
        if not args.quiet:
            print("Starting integrated runtime in continuous mode.")
            print("Press Ctrl+C to stop.\n")
        return runtime.run_forever(sleep_seconds=args.sleep)

    return run_bounded(
        runtime=runtime,
        sleep_seconds=args.sleep,
        max_cycles=args.max_cycles,
        quiet=args.quiet,
    )


if __name__ == "__main__":
    sys.exit(0 if main() is not None else 0)
