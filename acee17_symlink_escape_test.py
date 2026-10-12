from pathlib import Path
from tempfile import TemporaryDirectory

from ontology.acee_dashboard import ACEEDashboard


def main():
    with TemporaryDirectory() as root_tmp:
        with TemporaryDirectory() as outside_tmp:
            root = Path(root_tmp)
            outside = Path(outside_tmp)

            link = root / "escaped_runtime"
            link.symlink_to(outside, target_is_directory=True)

            try:
                ACEEDashboard(
                    root=root,
                    runtime_dir=link,
                )
            except ValueError as exc:
                assert str(exc) == "runtime_dir_outside_root"
            else:
                raise AssertionError(
                    "symlink escape was not rejected"
                )

    print("ACEE17_SYMLINK_ESCAPE_REJECTED")


if __name__ == "__main__":
    main()
