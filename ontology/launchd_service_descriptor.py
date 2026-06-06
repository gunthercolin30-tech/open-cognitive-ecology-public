
"""
LAUNCHD_SERVICE_DESCRIPTOR
"""

from pathlib import Path
from datetime import datetime
import plistlib

PRIMITIVE = "LAUNCHD_SERVICE_DESCRIPTOR"


class LaunchdServiceDescriptor:
    primitive = PRIMITIVE

    def __init__(self, root=None):
        self.root = Path(root) if root else Path.home() / "open-cognitive-ecology"
        self.launch_agents_dir = Path.home() / "Library" / "LaunchAgents"
        self.launch_agents_dir.mkdir(parents=True, exist_ok=True)
        self.label = "org.opencognitiveecology.runtime"
        self.plist_path = self.launch_agents_dir / f"{self.label}.plist"
        self.log_dir = self.root / "runtime_service"
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def step(
        self,
        interval_seconds=3600,
        max_cycles=10,
        sleep_seconds=1.0,
        viability_threshold=0.90,
        autonomy_threshold=0.90,
    ):
        python_path = "/usr/bin/python3"
        command = (
            "from ontology.autonomous_runtime_service import AutonomousRuntimeService; "
            "AutonomousRuntimeService().run_forever("
            f"interval_seconds={float(interval_seconds)}, "
            f"max_cycles={int(max_cycles)}, "
            f"sleep_seconds={float(sleep_seconds)}, "
            f"viability_threshold={float(viability_threshold)}, "
            f"autonomy_threshold={float(autonomy_threshold)})"
        )

        plist = {
            "Label": self.label,
            "ProgramArguments": [python_path, "-c", command],
            "WorkingDirectory": str(self.root),
            "RunAtLoad": True,
            "KeepAlive": True,
            "StandardOutPath": str(self.log_dir / "launchd_stdout.log"),
            "StandardErrorPath": str(self.log_dir / "launchd_stderr.log"),
        }

        with self.plist_path.open("wb") as handle:
            plistlib.dump(plist, handle)

        return {
            "primitive": self.primitive,
            "timestamp": datetime.utcnow().strftime("%Y%m%dT%H%M%SZ"),
            "plist_path": str(self.plist_path),
            "label": self.label,
            "load_command": f"launchctl load {self.plist_path}",
            "unload_command": f"launchctl unload {self.plist_path}",
            "status": "completed",
        }
