from __future__ import annotations

PRIMITIVE = "corpus_simulation_engine"
DESCRIPTION = "Corpus simulation engine."
DEPENDENCIES = []

"""
corpus_simulation_engine.py

Moteur central de simulation permettant de charger automatiquement
l'ensemble des primitives du package ``ontology`` et d'orchestrer
leur exécution itérative.

Ce module transforme le corpus ontologique formalisé en un système
dynamique exécutable.

Compatible Python 3.11+.
Bibliothèque standard uniquement.
"""


import importlib
import inspect
import json
import pkgutil
import traceback
from pathlib import Path
from types import ModuleType
from typing import Any


class CorpusSimulationEngine:
    """
    Moteur de simulation du corpus ontologique.

    Fonctionnalités :
    - découverte automatique des modules du package ontology ;
    - importation robuste des modules ;
    - détection des classes définies localement ;
    - instanciation automatique des classes sans arguments obligatoires ;
    - sélection des objets disposant d'une méthode step() ;
    - exécution itérative ;
    - capture des résultats et des erreurs ;
    - calcul de diagnostics globaux ;
    - sauvegarde de l'historique et d'un rapport final.
    """

    def __init__(
        self,
        ontology_package: str = "ontology",
        max_steps: int = 100,
        stop_on_error: bool = False,
    ) -> None:
        """
        Initialise le moteur de simulation.

        Parameters
        ----------
        ontology_package:
            Nom du package contenant les primitives.
        max_steps:
            Nombre maximal d'itérations.
        stop_on_error:
            Si True, arrête immédiatement la simulation en cas d'erreur.
        """
        self.ontology_package = ontology_package
        self.max_steps = int(max_steps)
        self.stop_on_error = bool(stop_on_error)

        self.modules: list[ModuleType] = []
        self.instances: list[Any] = []
        self.active_primitives: list[Any] = []
        self.history: list[dict[str, Any]] = []
        self.errors: list[dict[str, Any]] = []
        self.diagnostics: dict[str, Any] = {}

    # ------------------------------------------------------------------
    # Découverte et chargement
    # ------------------------------------------------------------------

    def discover_modules(self) -> list[str]:
        """
        Découvre tous les modules du package ontology.

        Returns
        -------
        list[str]
            Liste des noms complets des modules.
        """
        module_names: list[str] = []

        try:
            package = importlib.import_module(self.ontology_package)
        except Exception as exc:
            self._record_error(
                stage="discover_modules",
                source=self.ontology_package,
                exception=exc,
            )
            if self.stop_on_error:
                raise
            return []

        package_path = getattr(package, "__path__", None)
        if package_path is None:
            return []

        for module_info in pkgutil.iter_modules(package_path):
            name = module_info.name

            # Exclure les modules privés
            if name.startswith("_"):
                continue

            # Éviter l'auto-import du présent module
            if name == Path(__file__).stem:
                continue

            full_name = f"{self.ontology_package}.{name}"
            module_names.append(full_name)

        module_names.sort()
        return module_names

    def import_module(self, module_name: str):
        """
        Importe un module de manière robuste.

        Parameters
        ----------
        module_name:
            Nom complet du module.

        Returns
        -------
        ModuleType | None
        """
        try:
            return importlib.import_module(module_name)
        except Exception as exc:
            self._record_error(
                stage="import_module",
                source=module_name,
                exception=exc,
            )
            if self.stop_on_error:
                raise
            return None

    def discover_classes(self, module) -> list[type]:
        """
        Identifie les classes définies localement dans un module.

        Parameters
        ----------
        module:
            Module Python.

        Returns
        -------
        list[type]
        """
        classes: list[type] = []

        for _, obj in inspect.getmembers(module, inspect.isclass):
            if obj.__module__ == module.__name__:
                classes.append(obj)

        return classes

    def can_instantiate(self, cls: type) -> bool:
        """
        Détermine si une classe peut être instanciée sans arguments obligatoires.

        Parameters
        ----------
        cls:
            Classe à tester.

        Returns
        -------
        bool
        """
        # Ignorer les classes abstraites
        if inspect.isabstract(cls):
            return False

        try:
            signature = inspect.signature(cls)
        except (TypeError, ValueError):
            return False

        for param in signature.parameters.values():
            if param.name == "self":
                continue

            if param.kind in (
                inspect.Parameter.VAR_POSITIONAL,
                inspect.Parameter.VAR_KEYWORD,
            ):
                continue

            if param.default is inspect.Parameter.empty:
                return False

        return True

    def instantiate_class(self, cls: type):
        """
        Instancie une classe de manière robuste.

        Parameters
        ----------
        cls:
            Classe à instancier.

        Returns
        -------
        object | None
        """
        try:
            return cls()
        except Exception as exc:
            self._record_error(
                stage="instantiate_class",
                source=f"{cls.__module__}.{cls.__name__}",
                exception=exc,
            )
            if self.stop_on_error:
                raise
            return None

    def load_corpus(self) -> None:
        """
        Charge l'ensemble du corpus.

        Étapes :
        - découverte des modules ;
        - importation ;
        - découverte des classes ;
        - instanciation ;
        - sélection des primitives disposant d'une méthode step().
        """
        module_names = self.discover_modules()

        for module_name in module_names:
            module = self.import_module(module_name)
            if module is None:
                continue

            self.modules.append(module)

            for cls in self.discover_classes(module):
                if not self.can_instantiate(cls):
                    continue

                instance = self.instantiate_class(cls)
                if instance is None:
                    continue

                self.instances.append(instance)

                if callable(getattr(instance, "step", None)):
                    self.active_primitives.append(instance)

    # ------------------------------------------------------------------
    # Exécution
    # ------------------------------------------------------------------

    def step(self, step_index: int = 0):
        """
        Exécute une itération de simulation.

        Parameters
        ----------
        step_index:
            Index de l'itération.

        Returns
        -------
        dict
            Résumé de l'itération.
        """
        calls: list[dict[str, Any]] = []
        successful_calls = 0
        failed_calls = 0

        for primitive in self.active_primitives:
            primitive_name = (
                f"{primitive.__class__.__module__}."
                f"{primitive.__class__.__name__}"
            )

            try:
                result = primitive.step()

                calls.append(
                    {
                        "primitive": primitive_name,
                        "status": "success",
                        "result": self._make_json_serializable(result),
                    }
                )

                successful_calls += 1

            except Exception as exc:
                failed_calls += 1

                error_record = self._record_error(
                    stage="step",
                    source=primitive_name,
                    exception=exc,
                    step_index=step_index,
                )

                calls.append(
                    {
                        "primitive": primitive_name,
                        "status": "error",
                        "error": error_record["message"],
                    }
                )

                if self.stop_on_error:
                    raise

        summary = {
            "step_index": step_index,
            "successful_calls": successful_calls,
            "failed_calls": failed_calls,
            "calls": calls,
        }

        return summary

    # ------------------------------------------------------------------
    # Boucle de simulation
    # ------------------------------------------------------------------

    def run(self) -> list[dict]:
        """
        Exécute la simulation complète.

        Returns
        -------
        list[dict]
            Historique complet.
        """
        # Réinitialisation
        self.modules = []
        self.instances = []
        self.active_primitives = []
        self.history = []
        self.errors = []
        self.diagnostics = {}

        # Chargement du corpus
        self.load_corpus()

        # Si aucune primitive active, calculer tout de même les diagnostics
        if not self.active_primitives:
            self.diagnostics = self.compute_diagnostics()
            return self.history

        # Exécution
        for step_index in range(self.max_steps):
            iteration_summary = self.step(step_index)
            self.history.append(iteration_summary)

        # Diagnostics finaux
        self.diagnostics = self.compute_diagnostics()

        return self.history

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def compute_diagnostics(self) -> dict:
        """
        Calcule les diagnostics globaux.

        Returns
        -------
        dict
        """
        successful_calls = sum(
            entry.get("successful_calls", 0)
            for entry in self.history
        )

        failed_calls = sum(
            entry.get("failed_calls", 0)
            for entry in self.history
        )

        diagnostics = {
            "modules_discovered": len(self.modules),
            "instances_created": len(self.instances),
            "active_primitives": len(self.active_primitives),
            "steps_executed": len(self.history),
            "successful_calls": successful_calls,
            "failed_calls": failed_calls,
            "error_count": len(self.errors),
        }

        return diagnostics

    # ------------------------------------------------------------------
    # Sauvegarde
    # ------------------------------------------------------------------

    def save_history(
        self,
        filename: str = "corpus_simulation_history.json",
    ) -> None:
        """
        Sauvegarde l'historique de simulation au format JSON.

        Parameters
        ----------
        filename:
            Nom du fichier de sortie.
        """
        path = Path(filename)

        data = {
            "diagnostics": self.diagnostics,
            "history": self.history,
            "errors": self.errors,
        }

        with path.open("w", encoding="utf-8") as f:
            json.dump(
                data,
                f,
                indent=2,
                ensure_ascii=False,
            )

    def save_report(
        self,
        filename: str = "corpus_simulation_report.txt",
    ) -> None:
        """
        Génère un rapport textuel de synthèse.

        Parameters
        ----------
        filename:
            Nom du fichier de sortie.
        """
        path = Path(filename)

        lines: list[str] = []

        lines.append("CORPUS SIMULATION REPORT")
        lines.append("=" * 80)
        lines.append("")

        lines.append("CONFIGURATION")
        lines.append("-" * 80)
        lines.append(f"Ontology package : {self.ontology_package}")
        lines.append(f"Max steps        : {self.max_steps}")
        lines.append(f"Stop on error    : {self.stop_on_error}")
        lines.append("")

        lines.append("DIAGNOSTICS")
        lines.append("-" * 80)
        for key, value in self.diagnostics.items():
            lines.append(f"{key}: {value}")
        lines.append("")

        lines.append("ACTIVE PRIMITIVES")
        lines.append("-" * 80)
        if self.active_primitives:
            for primitive in self.active_primitives:
                name = (
                    f"{primitive.__class__.__module__}."
                    f"{primitive.__class__.__name__}"
                )
                lines.append(name)
        else:
            lines.append("None")
        lines.append("")

        lines.append("ERRORS")
        lines.append("-" * 80)
        if self.errors:
            for error in self.errors:
                lines.append(
                    f"[{error.get('stage')}] "
                    f"{error.get('source')} : "
                    f"{error.get('message')}"
                )
        else:
            lines.append("None")
        lines.append("")

        path.write_text("\n".join(lines), encoding="utf-8")

    # ------------------------------------------------------------------
    # Utilitaires internes
    # ------------------------------------------------------------------

    def _record_error(
        self,
        stage: str,
        source: str,
        exception: Exception,
        step_index: int | None = None,
    ) -> dict[str, Any]:
        """
        Enregistre une erreur.

        Returns
        -------
        dict
            Enregistrement d'erreur.
        """
        record = {
            "stage": stage,
            "source": source,
            "step_index": step_index,
            "exception_type": type(exception).__name__,
            "message": str(exception),
            "traceback": traceback.format_exc(),
        }

        self.errors.append(record)
        return record

    def _make_json_serializable(self, obj: Any) -> Any:
        """
        Convertit un objet en structure sérialisable JSON.
        """
        try:
            json.dumps(obj)
            return obj
        except (TypeError, OverflowError):
            pass

        if isinstance(obj, dict):
            return {
                str(k): self._make_json_serializable(v)
                for k, v in obj.items()
            }

        if isinstance(obj, (list, tuple, set)):
            return [
                self._make_json_serializable(item)
                for item in obj
            ]

        if hasattr(obj, "__dict__"):
            try:
                return self._make_json_serializable(vars(obj))
            except Exception:
                pass

        return repr(obj)


def main() -> None:
    """
    Point d'entrée principal.
    """
    engine = CorpusSimulationEngine(max_steps=10)
    engine.run()
    engine.save_history()
    engine.save_report()

    print("Simulation terminée.")
    print(engine.diagnostics)


if __name__ == "__main__":
    main()
