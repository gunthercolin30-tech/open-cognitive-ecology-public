\
#!/usr/bin/env python3
"""Governed installer for the AY1-D1 PDF backend."""
from __future__ import annotations

import importlib
import importlib.metadata
import subprocess
import sys

PIN = "pypdf==5.9.0"


def main():
    try:
        importlib.import_module("pypdf")
        version = importlib.metadata.version("pypdf")
        print(f"AY1_D1_PDF_BACKEND_READY pypdf={version}")
        return
    except (ImportError, importlib.metadata.PackageNotFoundError):
        pass
    command = [sys.executable, "-m", "pip", "install", "--user", "--disable-pip-version-check", PIN]
    print("AY1-D1 backend installation")
    print("- package:", PIN)
    subprocess.run(command, check=True, timeout=300, shell=False)
    importlib.invalidate_caches()
    module = importlib.import_module("pypdf")
    version = importlib.metadata.version("pypdf")
    if version != PIN.split("==", 1)[1]:
        raise SystemExit(f"Unexpected pypdf version: {version}")
    print(f"AY1_D1_PDF_BACKEND_READY pypdf={version}")


if __name__ == "__main__": main()
