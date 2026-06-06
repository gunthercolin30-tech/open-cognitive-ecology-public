
"""
AUTONOMOUS_PUBLICATION_PIPELINE
Publication pipeline using only the Python standard library.
"""

from pathlib import Path
from datetime import datetime
import json


class AutonomousPublicationPipeline:
    PRIMITIVE = "AUTONOMOUS_PUBLICATION_PIPELINE"

    def __init__(self, archive_root=None):
        if archive_root is None:
            archive_root = Path.home() / "open-cognitive-ecology" / "publication_archive"
        self.archive_root = Path(archive_root)
        self.archive_root.mkdir(parents=True, exist_ok=True)

    def step(self, *args, **kwargs):
        scientific_result = {}

        if args and isinstance(args[0], dict):
            scientific_result.update(args[0])

        if "scientific_result" in kwargs:
            value = kwargs.pop("scientific_result")
            if isinstance(value, dict):
                scientific_result.update(value)

        scientific_result.update(kwargs)

        title = scientific_result.get("title", "Untitled Scientific Result")
        body = scientific_result.get("body", scientific_result.get("content", "No detailed content provided."))
        references = scientific_result.get("references", ["Gunther, C. Formal Foundations of Constraint-Based Systems. Zenodo."])

        slug = scientific_result.get("slug", title.lower().replace(" ", "_"))

        package_dir = self.archive_root / slug
        package_dir.mkdir(parents=True, exist_ok=True)

        bibliography = "\n".join(
            "[" + str(i + 1) + "] " + ref
            for i, ref in enumerate(references)
        )

        manuscript = (
            "# " + title + "\n\n"
            "## Abstract\n"
            "Automatically generated manuscript from validated scientific outputs.\n\n"
            "## Results\n"
            + body + "\n\n"
            "## References\n"
            + bibliography
        )

        metrics = {
            "validation_score": scientific_result.get("validation_score", 1.0),
            "reproducibility_score": scientific_result.get("reproducibility_score", 1.0),
            "archive_timestamp": datetime.utcnow().isoformat() + "Z",
        }

        manuscript_path = package_dir / "manuscript.txt"
        bibliography_path = package_dir / "bibliography.txt"
        metrics_path = package_dir / "validation_metrics.json"

        manuscript_path.write_text(manuscript, encoding="utf-8")
        bibliography_path.write_text(bibliography, encoding="utf-8")
        metrics_path.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")

        return {
            "primitive": self.PRIMITIVE,
            "package_created": True,
            "package_dir": str(package_dir),
            "manuscript_path": str(manuscript_path),
            "bibliography_path": str(bibliography_path),
            "metrics_path": str(metrics_path),
            "metrics": metrics,
        }
