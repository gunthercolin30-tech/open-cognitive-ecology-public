from pathlib import Path
import shutil

ROOT = Path.home() / "open-cognitive-ecology"

TARGET = ROOT / "ontology" / "external_compute_expansion_manager.py"

BACKUP = TARGET.with_suffix(".syntax_fix.py.bak")


def main():

    if not TARGET.exists():
        raise FileNotFoundError(
            f"Target file not found: {TARGET}"
        )

    shutil.copy2(TARGET, BACKUP)

    content = TARGET.read_text(
        encoding="utf-8"
    )

    fixed = content.replace(
        "\\n\\n",
        "\n\n",
    )

    TARGET.write_text(
        fixed,
        encoding="utf-8",
    )

    print(
        "Syntax repair completed."
    )

    print(
        f"Backup created: {BACKUP}"
    )


if __name__ == "__main__":
    main()
