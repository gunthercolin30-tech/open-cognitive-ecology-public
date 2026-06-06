"""
AUTONOMOUS_STORAGE_DISCOVERY_ENGINE
"""

from pathlib import Path
import shutil


class AutonomousStorageDiscoveryEngine:
    DEFAULT_CANDIDATES = [
        str(Path.home()),
        "/Volumes",
        "/mnt",
        "/media",
    ]

    def __init__(self):
        self.name = "AUTONOMOUS_STORAGE_DISCOVERY_ENGINE"

    def _iter_candidate_paths(self, state):
        candidates = state.get("candidate_paths", self.DEFAULT_CANDIDATES)
        results = []

        for item in candidates:
            p = Path(item).expanduser()
            if not p.exists():
                continue

            if p.name in {"Volumes", "mnt", "media"} and p.is_dir():
                try:
                    for child in p.iterdir():
                        if child.exists():
                            results.append(child)
                except Exception:
                    pass
            else:
                results.append(p)

        unique = []
        seen = set()
        for p in results:
            key = str(p)
            if key not in seen:
                seen.add(key)
                unique.append(p)

        return unique

    def _describe_path(self, path):
        usage = shutil.disk_usage(path)
        is_external = str(path).startswith(("/Volumes/", "/mnt/", "/media/"))

        return {
            "path": str(path),
            "total_bytes": int(usage.total),
            "used_bytes": int(usage.used),
            "free_bytes": int(usage.free),
            "is_external": bool(is_external),
        }

    def step(self, state=None):
        if state is None:
            state = {}

        local_quota_bytes = int(
            state.get("local_quota_bytes", 500 * 1024 * 1024)
        )
        simulate_no_external = bool(
            state.get("simulate_no_external_storage", False)
        )

        locations = []

        for path in self._iter_candidate_paths(state):
            try:
                info = self._describe_path(path)
                if simulate_no_external:
                    info["is_external"] = False
                locations.append(info)
            except Exception:
                continue

        locations.sort(
            key=lambda x: (x["is_external"], x["free_bytes"]),
            reverse=True,
        )

        recommended = locations[0] if locations else None

        try:
            home_free = self._describe_path(Path.home())["free_bytes"]
        except Exception:
            home_free = 0

        quota_respected = home_free <= local_quota_bytes
        external_storage_detected = any(
            item["is_external"] for item in locations
        )

        return {
            "available_storage_locations": locations,
            "recommended_location": recommended,
            "quota_respected": quota_respected,
            "external_storage_detected": external_storage_detected,
            "storage_account_creation_required": (
                not external_storage_detected
            ),
        }


__all__ = ["AutonomousStorageDiscoveryEngine"]
