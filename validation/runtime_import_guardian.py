from pathlib import Path
import ast
import json

ROOT = Path(__file__).resolve().parent.parent

ONTOLOGY = ROOT / "ontology"

RUNTIME_PREFIXES = [
    "run_",
    "runtime_",
    "continuous_",
    "experiment_",
]

REFINE_PREFIXES = [
    "refine_",
]

HISTORICAL_TOKENS = [
    "_FIXED",
    "_patch",
    "_backup",
    "_old",
    "_legacy",
]


def classify_module(module_name):

    if any(
        module_name.startswith(prefix)
        for prefix in RUNTIME_PREFIXES
    ):
        return "runtime"

    if any(
        module_name.startswith(prefix)
        for prefix in REFINE_PREFIXES
    ):
        return "refinement"

    if any(
        token in module_name
        for token in HISTORICAL_TOKENS
    ):
        return "historical_artifact"

    return "ontology"


def detect_side_effects(tree):

    findings = []

    for node in ast.walk(tree):

        if isinstance(node, ast.Call):

            func = node.func

            if isinstance(func, ast.Attribute):

                name = func.attr

            elif isinstance(func, ast.Name):

                name = func.id

            else:

                continue

            if name in [
                "sleep",
                "run",
                "start",
                "launch",
                "execute",
                "main",
            ]:
                findings.append(name)

    return sorted(set(findings))


def analyze_module(path):

    content = path.read_text(
        encoding="utf-8",
        errors="ignore",
    )

    module_name = path.stem

    classification = classify_module(
        module_name
    )

    result = {
        "module": module_name,
        "classification": classification,
        "unsafe_import_side_effects": [],
        "safe_import": True,
    }

    try:

        tree = ast.parse(content)

        side_effects = detect_side_effects(tree)

        result[
            "unsafe_import_side_effects"
        ] = side_effects

        if side_effects and (
            classification == "runtime"
        ):
            result["safe_import"] = False

    except Exception as e:

        result["parse_error"] = str(e)

    return result


def main():

    modules = sorted(
        ONTOLOGY.glob("*.py")
    )

    report = []

    for module in modules:

        report.append(
            analyze_module(module)
        )

    unsafe = [
        r for r in report
        if not r["safe_import"]
    ]

    summary = {
        "modules_analyzed":
            len(report),

        "unsafe_runtime_modules":
            len(unsafe),

        "runtime_modules":
            len(
                [
                    r for r in report
                    if r["classification"]
                    == "runtime"
                ]
            ),

        "refinement_modules":
            len(
                [
                    r for r in report
                    if r["classification"]
                    == "refinement"
                ]
            ),

        "historical_artifacts":
            len(
                [
                    r for r in report
                    if r["classification"]
                    == "historical_artifact"
                ]
            ),
    }

    print(json.dumps(
        summary,
        indent=2,
    ))

    print(
        "\nPotential unsafe runtime imports:\n"
    )

    for item in unsafe[:100]:

        print(
            f"{item['module']} -> "
            f"{item['unsafe_import_side_effects']}"
        )

    return summary


if __name__ == "__main__":
    main()
