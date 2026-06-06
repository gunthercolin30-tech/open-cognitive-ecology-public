from pathlib import Path
import importlib
import traceback

ROOT = Path(__file__).resolve().parent.parent

ONTOLOGY = ROOT / "ontology"

SKIP_PREFIXES = [
    "run_",
    "runtime_",
    "continuous_",
    "experiment_",
]

SKIP_CONTAINS = [
    "longitudinal",
    "benchmark",
    "simulation",
    "stress_test",
]


def should_skip(module_name):

    for prefix in SKIP_PREFIXES:

        if module_name.startswith(prefix):
            return True

    for token in SKIP_CONTAINS:

        if token in module_name:
            return True

    return False


def test_module(module_name):

    try:

        importlib.import_module(
            f"ontology.{module_name}"
        )

        return {
            "module": module_name,
            "status": "ok",
        }

    except Exception as e:

        return {
            "module": module_name,
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
        }


def main():

    modules = sorted(
        p.stem
        for p in ONTOLOGY.glob("*.py")
        if not p.stem.startswith("_")
    )

    filtered_modules = [
        m for m in modules
        if not should_skip(m)
    ]

    skipped_modules = [
        m for m in modules
        if should_skip(m)
    ]

    results = [
        test_module(module)
        for module in filtered_modules
    ]

    errors = [
        r for r in results
        if r["status"] != "ok"
    ]

    summary = {
        "modules_discovered":
            len(filtered_modules),

        "skipped_modules":
            len(skipped_modules),

        "successful_calls":
            len(results) - len(errors),

        "failed_calls":
            len(errors),

        "error_count":
            len(errors),
    }

    print(summary)

    if skipped_modules:

        print("\nSkipped runtime-heavy modules:")

        for module in skipped_modules[:50]:

            print(f"- {module}")

    if errors:

        print("\nErrors:")

        for error in errors[:20]:

            print(
                f"{error['module']} -> "
                f"{error['error']}"
            )

    return summary


if __name__ == "__main__":
    main()
