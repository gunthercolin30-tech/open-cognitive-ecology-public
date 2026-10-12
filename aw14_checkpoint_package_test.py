import hashlib
import json
import tempfile
from pathlib import Path
from aw14_context import build_context
from ontology.ecological_certifier import EcologicalCertifier

with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    result = EcologicalCertifier(root).step(inputs=build_context(), persist=True)
    checkpoint = root / "validation_evidence" / "aw14_final_checkpoint"
    checkpoint.mkdir(parents=True)
    files = {
        "ecological_certification.json": result,
        "module_statuses.json": result["module_statuses"],
        "evidence_manifest.json": result["evidence_manifest"],
        "test_manifest.json": result["test_manifest"],
    }
    for name, value in files.items():
        (checkpoint / name).write_text(
            json.dumps(value, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
    lines = []
    for path in sorted(checkpoint.glob("*.json")):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {path.name}")
    (checkpoint / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    assert len(lines) == 4
    assert all(len(line.split()[0]) == 64 for line in lines)
print("AW14_CHECKPOINT_PACKAGE_OK")
