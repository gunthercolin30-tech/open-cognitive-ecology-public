from pathlib import Path
import importlib
import traceback

ROOT = Path(__file__).resolve().parent.parent
ONTOLOGY = ROOT / "ontology"


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

    results = [
        test_module(module)
        for module in modules
    ]

    errors = [
        r for r in results
        if r["status"] != "ok"
    ]

    summary = {
        "modules_discovered": len(modules),
        "successful_calls":
            len(results) - len(errors),
        "failed_calls": len(errors),
        "error_count": len(errors),
    }

    print(summary)

    if errors:

        print("\nERRORS:\n")

        for error in errors[:20]:

            print(
                f"{error['module']} -> "
                f"{error['error']}"
            )

    return summary


if __name__ == "__main__":
    main()
