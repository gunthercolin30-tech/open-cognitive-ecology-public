# OCE_QUICK_VALIDATION_PATCH
"""
Infrastructure de génération du rapport d'intégration du package ontology.

Ce module réalise une analyse structurelle complète des modules du package
`ontology` : découverte récursive, import dynamique, identification des
classes définies localement, tentative d'instanciation sans arguments et
exécution optionnelle de la méthode `step()`.

Toutes les structures retournées sont sérialisables en JSON.
"""

from __future__ import annotations

import importlib
import inspect
import pkgutil
import traceback
from pathlib import Path
from types import ModuleType
from typing import Any


ONTOLOGY_PACKAGE = "ontology"
REPORT_FILE = "ontology_integration_report.txt"


def _safe_repr(value: Any, max_length: int = 200) -> str:
    """
    Retourne une représentation robuste et tronquée d'un objet.
    """
    try:
        text = repr(value)
    except Exception:
        text = "<repr-error>"

    if len(text) > max_length:
        return text[: max_length - 3] + "..."

    return text


def discover_modules() -> list[str]:
    """
    Découvre récursivement tous les modules du package ontology.

    Returns:
        Liste triée des noms complets de modules.
    """
    try:
        package = importlib.import_module(ONTOLOGY_PACKAGE)
    except Exception:
        return []

    package_path = getattr(package, "__path__", None)
    if package_path is None:
        return []

    modules: list[str] = []

    for module_info in pkgutil.walk_packages(
        package_path,
        prefix=f"{ONTOLOGY_PACKAGE}.",
    ):
        modules.append(module_info.name)

    return sorted(set(modules))


def import_ontology_module(module_name: str) -> dict[str, Any]:
    """
    Importe dynamiquement un module.

    Args:
        module_name: Nom complet du module.

    Returns:
        Dictionnaire contenant le statut d'import.
    """
    try:
        module = importlib.import_module(module_name)
        return {
            "success": True,
            "module": module,
            "error": None,
            "traceback": None,
        }
    except Exception as exc:
        return {
            "success": False,
            "module": None,
            "error": f"{type(exc).__name__}: {exc}",
            "traceback": traceback.format_exc(),
        }


def discover_classes(module: ModuleType) -> list[type]:
    """
    Retourne les classes définies dans le module lui-même.

    Args:
        module: Module Python importé.

    Returns:
        Liste triée de classes.
    """
    classes: list[type] = []

    try:
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if getattr(obj, "__module__", None) == module.__name__:
                classes.append(obj)
    except Exception:
        return []

    classes.sort(key=lambda cls: cls.__name__)
    return classes


def can_instantiate_without_arguments(cls: type) -> bool:
    """
    Détermine si une classe peut être instanciée sans argument requis.

    Args:
        cls: Classe à analyser.

    Returns:
        True si l'instanciation sans argument est théoriquement possible.
    """
    try:
        signature = inspect.signature(cls)
    except Exception:
        try:
            signature = inspect.signature(cls.__init__)
        except Exception:
            return True

    for parameter in signature.parameters.values():
        if parameter.name in {"self", "cls"}:
            continue

        if parameter.kind in (
            inspect.Parameter.VAR_POSITIONAL,
            inspect.Parameter.VAR_KEYWORD,
        ):
            continue

        if parameter.default is inspect.Parameter.empty:
            return False

    return True


def instantiate_class(cls: type) -> dict[str, Any]:
    """
    Instancie une classe de manière sécurisée.

    Args:
        cls: Classe à instancier.

    Returns:
        Dictionnaire décrivant le résultat.
    """
    if not can_instantiate_without_arguments(cls):
        return {
            "success": False,
            "instance": None,
            "error": "Class requires constructor arguments.",
            "repr": None,
        }

    try:
        instance = cls()
        return {
            "success": True,
            "instance": instance,
            "error": None,
            "repr": _safe_repr(instance),
        }
    except Exception as exc:
        return {
            "success": False,
            "instance": None,
            "error": f"{type(exc).__name__}: {exc}",
            "repr": None,
        }


def analyze_step_method(instance: Any) -> dict[str, Any]:
    """
    Analyse et exécute la méthode step() si disponible.

    Args:
        instance: Instance d'une classe.

    Returns:
        Diagnostic JSON-sérialisable.
    """
    result = {
        "has_step": False,
        "step_callable": False,
        "step_executed": False,
        "step_result_type": None,
        "step_result_repr": None,
        "step_error": None,
    }

    if instance is None:
        return result

    if not hasattr(instance, "step"):
        return result

    result["has_step"] = True

    try:
        step_method = getattr(instance, "step")
    except Exception as exc:
        result["step_error"] = f"{type(exc).__name__}: {exc}"
        return result

    if not callable(step_method):
        return result

    result["step_callable"] = True
    try:
        signature = inspect.signature(step_method)
        required_parameters = []

        for parameter in signature.parameters.values():
            if parameter.kind in (
                inspect.Parameter.VAR_POSITIONAL,
                inspect.Parameter.VAR_KEYWORD,
            ):
                continue

            if parameter.default is inspect.Parameter.empty:
                required_parameters.append(parameter.name)

        if required_parameters:
            result["step_error"] = (
                "step() requires arguments: "
                + ", ".join(required_parameters)
            )
            return result
    except Exception:
        # Si la signature n'est pas inspectable, on tente tout de même.
        pass

    try:
        step_output = step_method()
        result["step_executed"] = True
        result["step_result_type"] = type(step_output).__name__
        result["step_result_repr"] = _safe_repr(step_output)
    except Exception as exc:
        result["step_error"] = f"{type(exc).__name__}: {exc}"

    return result


def test_module(module_name: str) -> dict[str, Any]:
    """
    Réalise l'analyse complète d'un module.

    Args:
        module_name: Nom complet du module.

    Returns:
        Diagnostic complet JSON-sérialisable.
    """
    module_result: dict[str, Any] = {
        "module": module_name,
        "import_success": False,
        "import_error": None,
        "classes": [],
    }

    import_result = import_ontology_module(module_name)
    module_result["import_success"] = import_result["success"]
    module_result["import_error"] = import_result["error"]

    if not import_result["success"]:
        return module_result

    module = import_result["module"]
    assert module is not None

    for cls in discover_classes(module):
        class_result: dict[str, Any] = {
            "class_name": cls.__name__,
            "qualified_name": f"{module_name}.{cls.__name__}",
            "can_instantiate": can_instantiate_without_arguments(cls),
            "instantiated": False,
            "instantiation_error": None,
            "instance_repr": None,
            "step_analysis": {
                "has_step": False,
                "step_callable": False,
                "step_executed": False,
                "step_result_type": None,
                "step_result_repr": None,
                "step_error": None,
            },
        }

        instantiation = instantiate_class(cls)

        if instantiation["success"]:
            class_result["instantiated"] = True
            class_result["instance_repr"] = instantiation["repr"]
            class_result["step_analysis"] = analyze_step_method(
                instantiation["instance"]
            )
        else:
            class_result["instantiation_error"] = instantiation["error"]

        module_result["classes"].append(class_result)

    return module_result


def _compute_statistics(results: list[dict[str, Any]]) -> dict[str, int]:
    """
    Calcule les statistiques globales.
    """
    stats = {
        "modules_discovered": len(results),
        "imports_successful": 0,
        "imports_failed": 0,
        "classes_detected": 0,
        "classes_instantiated": 0,
        "step_methods_executed": 0,
        "errors": 0,
    }

    for module_result in results:
        if module_result.get("import_success"):
            stats["imports_successful"] += 1
        else:
            stats["imports_failed"] += 1
            stats["errors"] += 1

        for class_result in module_result.get("classes", []):
            stats["classes_detected"] += 1

            if class_result.get("instantiated"):
                stats["classes_instantiated"] += 1
            elif class_result.get("instantiation_error"):
                stats["errors"] += 1

            step_analysis = class_result.get("step_analysis", {})

            if step_analysis.get("step_executed"):
                stats["step_methods_executed"] += 1

            if step_analysis.get("step_error"):
                stats["errors"] += 1

    return stats


def build_report(quick_validation=False,) -> str:
    """
    Construit le rapport texte complet.

    Returns:
        Rapport formaté prêt à être sauvegardé.
    """
    module_names = discover_modules()
    
    if quick_validation:

        filtered_modules = []

        for module_name in module_names:

            lowered = module_name.lower()

            blocked = [
                "longitudinal",
                "runtime_experiment",
                "run_a3",
                "continuous",
                "24h",
                "long_horizon",
            ]

            if any(
                token in lowered
                for token in blocked
            ):
                continue

            filtered_modules.append(
                module_name
            )

        module_names = filtered_modules

    results = [
        test_module(module_name)
        for module_name in module_names
    ]

    stats = _compute_statistics(results)

    lines: list[str] = []

    lines.append("ONTOLOGY INTEGRATION REPORT")
    lines.append("=" * 80)
    lines.append("")

    lines.append("GLOBAL STATISTICS")
    lines.append("-" * 80)

    for key, value in stats.items():
        lines.append(f"{key}: {value}")

    lines.append("")
    lines.append("MODULE DETAILS")
    lines.append("-" * 80)
    for module_result in results:
        lines.append("")
        lines.append(f"Module: {module_result['module']}")
        lines.append(f"Import success: {module_result['import_success']}")

        if module_result["import_error"]:
            lines.append(f"Import error: {module_result['import_error']}")
            continue

        classes = module_result.get("classes", [])
        lines.append(f"Classes detected: {len(classes)}")

        for class_result in classes:
            lines.append(f"  Class: {class_result['class_name']}")
            lines.append(
                f"    Can instantiate: {class_result['can_instantiate']}"
            )
            lines.append(
                f"    Instantiated: {class_result['instantiated']}"
            )

            if class_result["instantiation_error"]:
                lines.append(
                    "    Instantiation error: "
                    f"{class_result['instantiation_error']}"
                )

            step_analysis = class_result["step_analysis"]

            lines.append(
                f"    Has step: {step_analysis['has_step']}"
            )
            lines.append(
                f"    Step callable: {step_analysis['step_callable']}"
            )
            lines.append(
                f"    Step executed: {step_analysis['step_executed']}"
            )

            if step_analysis["step_result_type"] is not None:
                lines.append(
                    "    Step result type: "
                    f"{step_analysis['step_result_type']}"
                )

            if step_analysis["step_result_repr"] is not None:
                lines.append(
                    "    Step result repr: "
                    f"{step_analysis['step_result_repr']}"
                )

            if step_analysis["step_error"]:
                lines.append(
                    f"    Step error: {step_analysis['step_error']}"
                )

    lines.append("")
    return "\n".join(lines)


def save_report(
    report: str | None = None,
    filename: str = REPORT_FILE,
) -> Path:
    """
    Sauvegarde le rapport sur disque.

    Args:
        report: Rapport à sauvegarder. Si None, il est généré.
        filename: Nom du fichier de sortie.

    Returns:
        Chemin du fichier créé.
    """
    if report is None:
        report = build_report()

    path = Path(filename)
    path.write_text(report, encoding="utf-8")
    return path


if __name__ == "__main__":
    save_report()        
