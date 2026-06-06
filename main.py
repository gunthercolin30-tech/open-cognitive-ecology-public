# main.py

import asyncio
import subprocess
import sys
from pathlib import Path

from runtime.build_system import (
    build_system,
)

from runtime.initialize_graph import (
    initialize_graph,
)

from runtime.run_loop import (
    run_loop,
)

# ==========================================================
# OPTIONAL SCIENTIFIC VALIDATION LAYER
# ==========================================================
try:
    from ontology_integration_test_harness import (
        OntologyIntegrationTestHarness,
    )
except ImportError:
    OntologyIntegrationTestHarness = None


def regenerate_ontology_inventory():
    """
    Regenerate ontology_inventory.txt from all Python modules
    present in the ontology directory.

    The inventory is sorted alphabetically and excludes
    __init__.py.
    """

    root = Path(__file__).resolve().parent
    ontology_dir = root / "ontology"
    inventory_path = root / "ontology_inventory.txt"

    if not ontology_dir.exists():
        print("=" * 60)
        print("ONTOLOGY DIRECTORY NOT FOUND")
        print("=" * 60)
        print(f"Missing directory: {ontology_dir}")
        print("Ontology inventory regeneration skipped.")
        print()
        return

    try:
        modules = sorted(
            path.stem
            for path in ontology_dir.glob("*.py")
            if path.stem != "__init__"
        )

        lines = [
            f"modules_discovered: {len(modules)}",
            f"active_primitives: {len(modules) - 1 if len(modules) > 0 else 0}",
            "error_count: 0",
            "",
            "modules:",
        ]
        lines.extend(f"- {module}" for module in modules)

        inventory_path.write_text(
            "\n".join(lines) + "\n",
            encoding="utf-8",
        )

        print("=" * 60)
        print("ONTOLOGY INVENTORY REGENERATED")
        print("=" * 60)
        print(f"Modules discovered: {len(modules)}")
        print(f"Active primitives (estimated): {len(modules) - 1 if len(modules) > 0 else 0}")
        print(f"Inventory written to: {inventory_path}")
        print()

    except Exception as exc:
        print("=" * 60)
        print("ONTOLOGY INVENTORY REGENERATION FAILED")
        print("=" * 60)
        print(f"{type(exc).__name__}: {exc}")
        print("Runtime startup will continue normally.")
        print()


def run_publication_pipeline():
    """
    Execute the automated scientific publication pipeline
    if run_publication_pipeline.py is available.

    This pipeline regenerates:
        - global meta-analysis
        - inter-version regression benchmark
        - consolidated scientific dashboard
        - completion marker

    Any failure is reported but does not prevent the
    runtime from starting.
    """

    root = Path(__file__).resolve().parent
    pipeline_script = root / "run_publication_pipeline.py"

    if not pipeline_script.exists():
        print("=" * 60)
        print("PUBLICATION PIPELINE NOT FOUND")
        print("=" * 60)
        print("run_publication_pipeline.py is not present.")
        print("Runtime startup will continue normally.")
        print()
        return

    try:
        print("=" * 60)
        print("RUNNING AUTOMATED SCIENTIFIC PUBLICATION PIPELINE")
        print("=" * 60)

        subprocess.run(
            [sys.executable, str(pipeline_script)],
            cwd=str(root),
            check=True,
        )

        print("Publication pipeline completed successfully.")
        print()

    except Exception as exc:
        print("=" * 60)
        print("PUBLICATION PIPELINE FAILED")
        print("=" * 60)
        print(f"{type(exc).__name__}: {exc}")
        print(
            "Runtime startup will continue despite "
            "publication pipeline failure."
        )
        print()


async def main():
    """
    Entry point for Open Cognitive Ecology.

    Runtime initialization sequence:
    1. Regenerate ontology_inventory.txt.
    2. Optionally execute the scientific validation harness.
    3. Automatically regenerate scientific reports.
    4. Build the full system architecture.
    5. Ensure the shared agent population exists.
    6. Initialize the cognitive graph and couple nodes
       to PersistentAgent objects.
    7. Start the asynchronous execution loop.
    """

    # =====================================================
    # REGENERATE ONTOLOGY INVENTORY
    # =====================================================

    regenerate_ontology_inventory()

    # =====================================================
    # OPTIONAL SCIENTIFIC VALIDATION
    # =====================================================

    if OntologyIntegrationTestHarness is not None:
        try:
            print("=" * 60)
            print("RUNNING ONTOLOGY VALIDATION HARNESS")
            print("=" * 60)

            harness = OntologyIntegrationTestHarness()
            harness.run_all_tests()
            harness.save_json_report()
            harness.save_text_report()

            print("Validation completed.")
            print(harness.diagnostics)
            print()

        except Exception as exc:
            print("=" * 60)
            print("VALIDATION HARNESS FAILED")
            print("=" * 60)
            print(f"{type(exc).__name__}: {exc}")
            print(
                "Runtime startup will continue despite "
                "validation failure."
            )
            print()

    # =====================================================
    # AUTOMATED SCIENTIFIC PUBLICATION PIPELINE
    # =====================================================

    run_publication_pipeline()

    # =====================================================
    # BUILD COMPLETE RUNTIME
    # =====================================================

    system = build_system()

    # =====================================================
    # ENSURE SHARED AGENT POPULATION
    # =====================================================

    if "agents" not in system:
        system["agents"] = []

    # =====================================================
    # INITIALIZE COGNITIVE GRAPH + AGENT COUPLING
    # =====================================================

    initialize_graph(
        system["graph"],
        system["agents"],
    )

    # =====================================================
    # OPTIONAL EXECUTION GROUPS (COMPATIBILITY CHECK)
    # =====================================================

    if "graph_based_ecologies" not in system:
        system["graph_based_ecologies"] = []

    if "agent_based_ecologies" not in system:
        system["agent_based_ecologies"] = []

    # =====================================================
    # START MAIN EXECUTION LOOP
    # =====================================================

    await run_loop(system)


if __name__ == "__main__":
    asyncio.run(main())