"""Generate docs/primitives_by_level.md."""

from collections import defaultdict
from pathlib import Path

from ontology.hierarchical_registry import HIERARCHICAL_LEVELS


def main():
    grouped = defaultdict(list)

    for name, level in HIERARCHICAL_LEVELS.items():
        grouped[level].append(name)

    lines = ["# Primitives by Hierarchical Level", ""]

    for level in sorted(grouped):
        lines.append(f"## Level {level}")
        lines.append("")
        for name in sorted(grouped[level]):
            lines.append(f"- `{name}`")
        lines.append("")

    Path("docs/primitives_by_level.md").write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    print("Generated docs/primitives_by_level.md")


if __name__ == "__main__":
    main()
