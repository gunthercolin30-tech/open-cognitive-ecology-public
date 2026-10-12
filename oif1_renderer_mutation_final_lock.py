from __future__ import annotations

import hashlib
from pathlib import Path

from oif1_renderer_call_policy import renderer_policy_findings_from_source

LOCK_VERSION = "oif1-renderer-mutation-final-lock-v1"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    root = Path.home() / "open-cognitive-ecology"
    renderer = root / "oif/ui/review_app.py"
    before = renderer.read_bytes()
    source = before.decode("utf-8")
    assert not renderer_policy_findings_from_source(source, str(renderer))

    mutations = {
        "pathlib_write": "\nfrom pathlib import Path\nPath('/tmp/oif-mutation').write_text('x')\n",
        "open_write": "\nopen('/tmp/oif-mutation', 'w').write('x')\n",
        "os_replace": "\nimport os\nos.replace('a', 'b')\n",
        "subprocess_run": "\nimport subprocess\nsubprocess.run(['true'])\n",
        "dynamic_eval": "\neval('1 + 1')\n",
    }
    for name, payload in mutations.items():
        findings = renderer_policy_findings_from_source(source + payload, f"{renderer}:{name}")
        assert findings, name

    assert renderer.read_bytes() == before
    print("OIF1_RENDERER_REAL_SOURCE_ALLOWED_OK")
    print("OIF1_RENDERER_MUTATION_DETECTION_RATE_OK")
    print("OIF1_RENDERER_REAL_FILE_IMMUTABILITY_OK")
    print("OIF1_RENDERER_MUTATION_FINAL_LOCK_OK")
    print({"lock_version": LOCK_VERSION, "mutation_count": len(mutations), "renderer_sha256": sha256_bytes(before)})


if __name__ == "__main__":
    main()
