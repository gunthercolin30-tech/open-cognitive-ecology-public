from __future__ import annotations

import contextlib
import io
import json
import sys
import traceback
from typing import Any

from validation.integration_report import test_module


def main() -> int:
    if len(sys.argv) != 2:
        print(json.dumps({"success": False, "error": "module name required"}))
        return 2

    module_name = sys.argv[1]
    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()

    try:
        with contextlib.redirect_stdout(stdout_buffer), contextlib.redirect_stderr(stderr_buffer):
            result = test_module(module_name)
        payload: dict[str, Any] = {
            "success": True,
            "module": module_name,
            "result": result,
            "captured_stdout": stdout_buffer.getvalue()[-4000:],
            "captured_stderr": stderr_buffer.getvalue()[-4000:],
        }
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        return 0
    except BaseException as exc:
        payload = {
            "success": False,
            "module": module_name,
            "error": f"{type(exc).__name__}: {exc}",
            "traceback": traceback.format_exc(),
            "captured_stdout": stdout_buffer.getvalue()[-4000:],
            "captured_stderr": stderr_buffer.getvalue()[-4000:],
        }
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
