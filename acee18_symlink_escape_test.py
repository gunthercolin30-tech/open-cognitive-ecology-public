from pathlib import Path
from tempfile import TemporaryDirectory

from ontology.acee_prediction_engine import (
    ACEEPredictionEngine,
)


def main():
    with TemporaryDirectory() as root_tmp:
        with TemporaryDirectory() as outside_tmp:
            root = Path(root_tmp)
            outside = Path(outside_tmp)

            link = root / "prediction_runtime"
            link.symlink_to(
                outside,
                target_is_directory=True,
            )

            try:
                ACEEPredictionEngine(
                    root=root,
                    runtime_dir=link,
                )
            except ValueError as exc:
                assert str(exc) == (
                    "runtime_dir_outside_root"
                )
            else:
                raise AssertionError(
                    "symlink escape accepted"
                )

    print(
        "ACEE18_SYMLINK_ESCAPE_REJECTED"
    )


if __name__ == "__main__":
    main()
