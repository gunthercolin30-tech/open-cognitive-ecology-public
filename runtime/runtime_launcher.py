import importlib

from runtime.runtime_activation_registry import (
    RUNTIME_REGISTRY,
)


class RuntimeLauncher:

    def list_runtimes(self):

        return sorted(
            RUNTIME_REGISTRY.keys()
        )

    def get_runtime_info(
        self,
        runtime_name,
    ):

        return RUNTIME_REGISTRY.get(
            runtime_name,
            {},
        )

    def activate(
        self,
        runtime_name,
    ):

        if runtime_name not in RUNTIME_REGISTRY:

            raise ValueError(
                f"Unknown runtime: {runtime_name}"
            )

        info = RUNTIME_REGISTRY[
            runtime_name
        ]

        if (
            info.get(
                "activation_mode"
            ) != "manual"
        ):

            raise RuntimeError(
                "Runtime activation mode unsafe."
            )

        module = importlib.import_module(
            f"ontology.{runtime_name}"
        )

        return {
            "runtime":
                runtime_name,

            "category":
                info.get(
                    "category"
                ),

            "safe_import":
                info.get(
                    "safe_import"
                ),

            "module_loaded":
                True,
        }


if __name__ == "__main__":

    launcher = RuntimeLauncher()

    print(
        launcher.list_runtimes()
    )
