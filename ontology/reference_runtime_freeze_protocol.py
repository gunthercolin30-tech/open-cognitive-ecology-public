"""Reference Runtime Freeze Protocol."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
from typing import Any


@dataclass
class ReferenceRuntimeFreezeProtocol:
    root: Path | None = None

    def __post_init__(self) -> None:
        if self.root is None:
            self.root = Path.home() / "open-cognitive-ecology"

    def _sha256(self, path: Path) -> str:
        if not path.exists():
            return "missing"

        hasher = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(65536), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def _git_metadata(self) -> dict[str, Any]:
        try:
            commit = subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                cwd=self.root,
                text=True,
            ).strip()
            branch = subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=self.root,
                text=True,
            ).strip()
        except Exception:
            commit = "unknown"
            branch = "unknown"

        return {"commit": commit, "branch": branch}

    def freeze(self) -> dict[str, Any]:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

        output_dir = (
            self.root
            / "experimental_reference"
            / f"reference_freeze_{timestamp}"
        )
        output_dir.mkdir(parents=True, exist_ok=True)

        critical_files = [
            self.root / "ontology_inventory.txt",
            self.root / "scientific_validation_report.json",
            self.root / "scientific_validation_report.txt",
            self.root / "civilizational_dashboard.html",
            self.root / "main.py",
            self.root / "validation" / "main.py",
        ]

        artifact_hashes = {}
        for file_path in critical_files:
            if file_path.exists():
                relative_path = str(file_path.relative_to(self.root))
                artifact_hashes[relative_path] = self._sha256(file_path)

        manifest = {
            "timestamp_utc": timestamp,
            "git": self._git_metadata(),
            "artifact_hashes": artifact_hashes,
            "status": "success",
        }

        manifest_path = output_dir / "freeze_manifest.json"
        manifest_path.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        hashes_path = output_dir / "artifact_hashes.json"
        hashes_path.write_text(
            json.dumps(artifact_hashes, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        certificate_path = output_dir / "freeze_certificate.txt"
        certificate_text = "\n".join([
            "REFERENCE RUNTIME FREEZE CERTIFICATE",
            f"Timestamp (UTC): {timestamp}",
            f"Branch: {manifest['git']['branch']}",
            f"Commit: {manifest['git']['commit']}",
            "Status: success",
            "",
        ])
        certificate_path.write_text(
            certificate_text,
            encoding="utf-8",
        )

        self.export_validation_bundle(output_dir)
        self.export_longitudinal_metrics(output_dir)
        self.snapshot_civilizational_memory(output_dir)

        return {
            "status": "success",
            "manifest_path": str(manifest_path),
            "certificate_path": str(certificate_path),
            "hashes_path": str(hashes_path),
        }


    def export_validation_bundle(self, output_dir: Path) -> Path:
        validation_files = [
            self.root / "scientific_validation_report.json",
            self.root / "scientific_validation_report.txt",
            self.root / "ontology_inventory.txt",
        ]

        bundle = {}

        for path in validation_files:
            bundle[str(path.relative_to(self.root))] = {
                "exists": path.exists(),
                "sha256": self._sha256(path),
            }

        output = output_dir / "validation_bundle.json"

        output.write_text(
            json.dumps(bundle, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        return output

    def export_longitudinal_metrics(self, output_dir: Path) -> Path:
        experiments_dir = self.root / "runtime_experiments"

        metrics = {
            "available": experiments_dir.exists(),
            "experiment_files": [],
        }

        if experiments_dir.exists():
            for file in sorted(experiments_dir.glob("experiment_*.json")):
                metrics["experiment_files"].append({
                    "file": file.name,
                    "sha256": self._sha256(file),
                })

        output = output_dir / "longitudinal_metrics.json"

        output.write_text(
            json.dumps(metrics, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        return output

    def snapshot_civilizational_memory(self, output_dir: Path) -> Path:
        snapshot_dir = output_dir / "civilizational_memory_snapshot"

        snapshot_dir.mkdir(parents=True, exist_ok=True)

        memory_candidates = [
            self.root / "memory",
            self.root / "civilizational_memory",
            self.root / "persistent_memory",
        ]

        snapshot_report = {
            "snapshots": [],
        }

        for memory_dir in memory_candidates:
            if memory_dir.exists() and memory_dir.is_dir():

                destination = snapshot_dir / memory_dir.name

                shutil.copytree(
                    memory_dir,
                    destination,
                    dirs_exist_ok=True,
                )

                snapshot_report["snapshots"].append({
                    "source": str(memory_dir),
                    "destination": str(destination),
                })

        report_path = output_dir / "memory_snapshot_report.json"

        report_path.write_text(
            json.dumps(snapshot_report, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        return report_path


if __name__ == "__main__":
    protocol = ReferenceRuntimeFreezeProtocol()
    print(protocol.freeze())
