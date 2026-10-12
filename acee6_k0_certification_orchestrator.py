from __future__ import annotations
import argparse
import json
from pathlib import Path
from acee6_k0_support import ROOT, run_orchestrator

def main() -> int:
    parser = argparse.ArgumentParser(description="ACEE6-K0 certification contract and baseline orchestrator")
    parser.add_argument("--persist", action="store_true", help="Persist the K0 evidence report")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    result = run_orchestrator(root=args.root.resolve(), persist=args.persist, run_heavy=False)
    print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
    print("ACEE6_K0_ORCHESTRATOR_READY")
    return 0 if result["verification"]["valid"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
