from __future__ import annotations

from oif1_renderer_call_policy import renderer_policy_findings_from_source


def assert_allowed(source: str) -> None:
    findings = renderer_policy_findings_from_source(source)
    assert not findings, (source, findings)


def assert_blocked(source: str, marker: str) -> None:
    findings = renderer_policy_findings_from_source(source)
    assert findings, source
    assert any(marker in finding for finding in findings), (marker, findings)


def main() -> None:
    allowed = [
        "from nicegui import ui\nui.run(reload=False)\n",
        "from nicegui import ui\nui.button('Save')\nui.notify('ok')\n",
        "service.load()\nservice.save_decision('x')\n",
        "model.write_text_preview()\n",
        "open('resource.txt', 'r').read()\n",
        "open('resource.bin', 'rb').read()\n",
    ]
    for source in allowed:
        assert_allowed(source)
    print("OIF1_RENDERER_POLICY_ALLOWED_CASES_OK")

    blocked = [
        ("from pathlib import Path\nPath('x').write_text('x')\n", "write_text"),
        ("from pathlib import Path\nPath('x').write_bytes(b'x')\n", "write_bytes"),
        ("import pathlib\npathlib.Path('x').unlink()\n", "unlink"),
        ("import pathlib as pl\npl.Path('x').touch()\n", "touch"),
        ("from pathlib import Path as P\nP('x').mkdir()\n", "mkdir"),
        ("from pathlib import Path\np = Path('x')\np.write_text('x')\n", "write_text"),
        ("open('x', 'w')\n", "direct-open-write"),
        ("open('x', mode='ab')\n", "direct-open-write"),
        ("writer = open\nwriter('x', 'x')\n", "direct-open-write"),
        ("import os\nos.replace('a', 'b')\n", "os.replace"),
        ("import shutil as sh\nsh.rmtree('x')\n", "shutil.rmtree"),
        ("import subprocess as sp\nsp.run(['true'])\n", "subprocess.run"),
        ("from subprocess import run as process_run\nprocess_run(['true'])\n", "subprocess.run"),
        ("eval('1+1')\n", "eval"),
        ("exec('x=1')\n", "exec"),
        ("import runpy\nrunpy.run_path('x.py')\n", "runpy.run_path"),
    ]
    for source, marker in blocked:
        assert_blocked(source, marker)
    print("OIF1_RENDERER_POLICY_MUTATION_CASES_OK")
    print("OIF1_RENDERER_CALL_POLICY_TEST_OK")


if __name__ == "__main__":
    main()
