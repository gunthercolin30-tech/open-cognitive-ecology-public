
# -*- coding: utf-8 -*-
"""
F2 — Node Capability Registry.

This primitive measures and persists the local capabilities of a distributed
civilizational node. It complements distributed_civilizational_node: F1 proves
that a persistent node exists; F2 describes what that node can contribute to a
multi-machine ecology.

The validation target is functional and measurable: CPU, RAM, storage,
platform, Python runtime, available ontology modules, optional GPU signal,
capability completeness, and a bounded global capability index.
"""


from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, List
import hashlib
import importlib.util
import json
import os
import platform
import shutil
import socket
import sys

PRIMITIVE = 'node_capability_registry'

DEPENDENCIES = [
    'distributed_civilizational_node',
    'autonomous_resource_manager',
    'external_compute_expansion_manager',
    'autonomous_storage_discovery_engine',
    'autonomous_storage_provider_evaluation_engine',
    'metrics_history_recorder',
    'distributed_runtime_coordination',
    'distributed_runtime_coordinator',
]

CAPABILITY_KEYS = [
    'cpu',
    'ram',
    'storage',
    'platform',
    'python_runtime',
    'ontology_modules',
    'node_identity',
]


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def _bounded(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except Exception:
        number = default
    if number != number or number in (float('inf'), float('-inf')):
        return default
    return max(0.0, min(1.0, number))


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _safe_text(value: Any, default: str = 'unknown') -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _read_meminfo_linux() -> Dict[str, int]:
    result = {'total_bytes': 0, 'available_bytes': 0}
    path = Path('/proc/meminfo')
    if not path.exists():
        return result
    try:
        values: Dict[str, int] = {}
        for line in path.read_text(encoding='utf-8', errors='ignore').splitlines():
            if ':' not in line:
                continue
            key, raw = line.split(':', 1)
            parts = raw.strip().split()
            if parts and parts[0].isdigit():
                values[key] = int(parts[0]) * 1024
        result['total_bytes'] = values.get('MemTotal', 0)
        result['available_bytes'] = values.get('MemAvailable', values.get('MemFree', 0))
    except Exception:
        pass
    return result


def _memory_snapshot() -> Dict[str, Any]:
    # Prefer psutil when available, but do not require it.
    try:
        import psutil  # type: ignore
        vm = psutil.virtual_memory()
        return {
            'total_bytes': int(vm.total),
            'available_bytes': int(vm.available),
            'availability_ratio': _bounded(vm.available / vm.total if vm.total else 0.0),
            'source': 'psutil',
        }
    except Exception:
        pass

    linux = _read_meminfo_linux()
    if linux['total_bytes'] > 0:
        return {
            'total_bytes': linux['total_bytes'],
            'available_bytes': linux['available_bytes'],
            'availability_ratio': _bounded(linux['available_bytes'] / linux['total_bytes']),
            'source': 'proc_meminfo',
        }

    # Portable fallback: exact total RAM is unavailable from stdlib on macOS.
    # The capability remains present but low-confidence rather than failing.
    return {
        'total_bytes': 0,
        'available_bytes': 0,
        'availability_ratio': 0.5,
        'source': 'portable_fallback',
    }


def _gpu_snapshot() -> Dict[str, Any]:
    # Intentionally conservative and offline: detect likely local GPU signal.
    machine = platform.machine().lower()
    system = platform.system().lower()
    if system == 'darwin' and ('arm' in machine or 'aarch64' in machine):
        return {'gpu_available': True, 'gpu_type': 'apple_silicon_integrated', 'confidence': 0.7}
    if shutil.which('nvidia-smi'):
        return {'gpu_available': True, 'gpu_type': 'nvidia_smi_detected', 'confidence': 0.8}
    return {'gpu_available': False, 'gpu_type': 'not_detected', 'confidence': 0.5}


@dataclass
class CapabilitySnapshot:
    primitive: str
    node_id: str
    node_name: str
    timestamp_utc: str
    cpu_count: int
    cpu_capability_score: float
    ram_total_bytes: int
    ram_available_bytes: int
    ram_availability_ratio: float
    storage_total_bytes: int
    storage_free_bytes: int
    storage_availability_ratio: float
    gpu_available: bool
    gpu_type: str
    platform_name: str
    python_version: str
    ontology_module_count: int
    available_dependency_count: int
    missing_dependency_count: int
    available_capability_count: int
    global_capability_index: float
    capability_registry_ready: bool


class NodeCapabilityRegistry:
    """Local capability registry for distributed civilizational nodes."""

    primitive = PRIMITIVE

    def __init__(self, root: str | Path | None = None, node_id: str | None = None) -> None:
        self.root = Path(root) if root else Path.home() / 'open-cognitive-ecology'
        self.ontology_dir = self.root / 'ontology'
        self.node_dir = self.root / 'distributed_nodes'
        self.node_dir.mkdir(parents=True, exist_ok=True)
        self.node_identity_path = self.node_dir / 'local_node_identity.json'
        self.registry_path = self.node_dir / 'node_capability_registry.json'
        self.history_path = self.node_dir / 'node_capability_history.jsonl'
        self.node_id = node_id or os.environ.get('OCE_NODE_ID') or self._load_node_id()

    def _load_node_id(self) -> str:
        if self.node_identity_path.exists():
            try:
                data = json.loads(self.node_identity_path.read_text(encoding='utf-8'))
                candidate = _safe_text(data.get('node_id'), '')
                if candidate:
                    return candidate
            except Exception:
                pass
        seed = '|'.join([socket.gethostname(), platform.platform(), str(self.root)])
        return 'oce-node-' + hashlib.sha256(seed.encode('utf-8')).hexdigest()[:16]

    def _node_name(self) -> str:
        return socket.gethostname() or self.node_id

    def _ontology_module_count(self) -> int:
        if not self.ontology_dir.exists():
            return 0
        try:
            return len([p for p in self.ontology_dir.glob('*.py') if p.name != '__init__.py'])
        except Exception:
            return 0

    def _dependency_availability(self) -> Dict[str, Any]:
        available: List[str] = []
        missing: List[str] = []
        for dependency in DEPENDENCIES:
            module_path = self.ontology_dir / f'{dependency}.py'
            if module_path.exists() or importlib.util.find_spec(f'ontology.{dependency}') is not None:
                available.append(dependency)
            else:
                missing.append(dependency)
        return {'available': available, 'missing': missing}

    def _write_json(self, path: Path, payload: Dict[str, Any]) -> bool:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding='utf-8')
            return True
        except Exception:
            return False

    def _append_history(self, payload: Dict[str, Any]) -> bool:
        try:
            self.history_path.parent.mkdir(parents=True, exist_ok=True)
            with self.history_path.open('a', encoding='utf-8') as handle:
                handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + '\n')
            return True
        except Exception:
            return False

    def _storage_snapshot(self) -> Dict[str, Any]:
        try:
            usage = shutil.disk_usage(self.root if self.root.exists() else Path.home())
            total = int(usage.total)
            free = int(usage.free)
            return {
                'total_bytes': total,
                'free_bytes': free,
                'availability_ratio': _bounded(free / total if total else 0.0),
            }
        except Exception:
            return {'total_bytes': 0, 'free_bytes': 0, 'availability_ratio': 0.0}

    def _cpu_score(self, cpu_count: int) -> float:
        # 8 cores or more is treated as full local CPU capability; bounded for comparability.
        return _bounded(cpu_count / 8.0 if cpu_count else 0.0)

    def step(self, inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        inputs = inputs or {}

        cpu_count = _safe_int(inputs.get('cpu_count', os.cpu_count() or 0), 0)
        memory = _memory_snapshot()
        storage = self._storage_snapshot()
        gpu = _gpu_snapshot()
        deps = self._dependency_availability()
        module_count = self._ontology_module_count()

        # Test hooks allow degradation simulation without corrupting host measurement.
        if 'ram_availability_ratio' in inputs:
            memory['availability_ratio'] = _bounded(inputs.get('ram_availability_ratio'))
        if 'storage_availability_ratio' in inputs:
            storage['availability_ratio'] = _bounded(inputs.get('storage_availability_ratio'))
        if 'ontology_module_count' in inputs:
            module_count = max(0, _safe_int(inputs.get('ontology_module_count'), module_count))
        if 'dependency_missing_override' in inputs:
            missing_count = max(0, _safe_int(inputs.get('dependency_missing_override'), 0))
            available_dependency_count = max(0, len(DEPENDENCIES) - missing_count)
            missing_dependency_count = missing_count
        else:
            available_dependency_count = len(deps['available'])
            missing_dependency_count = len(deps['missing'])

        cpu_score = self._cpu_score(cpu_count)
        ram_score = _bounded(memory.get('availability_ratio'), 0.5)
        storage_score = _bounded(storage.get('availability_ratio'), 0.0)
        dependency_score = _bounded(available_dependency_count / len(DEPENDENCIES) if DEPENDENCIES else 1.0)
        module_score = _bounded(module_count / 600.0 if module_count else 0.0)
        platform_score = 1.0 if platform.system() else 0.0
        python_score = 1.0 if sys.version_info >= (3, 9) else 0.7
        gpu_score = 0.15 if gpu.get('gpu_available') else 0.0

        capability_flags = {
            'cpu': cpu_score > 0.0,
            'ram': ram_score > 0.0,
            'storage': storage_score > 0.0,
            'platform': platform_score > 0.0,
            'python_runtime': python_score > 0.0,
            'ontology_modules': module_count > 0,
            'node_identity': bool(self.node_id),
        }
        available_capability_count = sum(1 for value in capability_flags.values() if value)

        global_capability_index = _bounded(
            (0.18 * cpu_score)
            + (0.18 * ram_score)
            + (0.18 * storage_score)
            + (0.16 * dependency_score)
            + (0.12 * module_score)
            + (0.08 * platform_score)
            + (0.07 * python_score)
            + (0.03 * gpu_score)
        )

        registry_ready = (
            available_capability_count >= 6
            and dependency_score >= 0.75
            and storage_score >= 0.02
            and global_capability_index >= 0.35
        )

        snapshot = CapabilitySnapshot(
            primitive=PRIMITIVE,
            node_id=self.node_id,
            node_name=self._node_name(),
            timestamp_utc=_now(),
            cpu_count=cpu_count,
            cpu_capability_score=round(cpu_score, 4),
            ram_total_bytes=int(memory.get('total_bytes', 0)),
            ram_available_bytes=int(memory.get('available_bytes', 0)),
            ram_availability_ratio=round(ram_score, 4),
            storage_total_bytes=int(storage.get('total_bytes', 0)),
            storage_free_bytes=int(storage.get('free_bytes', 0)),
            storage_availability_ratio=round(storage_score, 4),
            gpu_available=bool(gpu.get('gpu_available', False)),
            gpu_type=_safe_text(gpu.get('gpu_type'), 'not_detected'),
            platform_name=platform.platform(),
            python_version=sys.version.split()[0],
            ontology_module_count=module_count,
            available_dependency_count=available_dependency_count,
            missing_dependency_count=missing_dependency_count,
            available_capability_count=available_capability_count,
            global_capability_index=round(global_capability_index, 4),
            capability_registry_ready=registry_ready,
        )

        payload = asdict(snapshot)
        payload['capability_flags'] = capability_flags
        payload['dependencies'] = DEPENDENCIES
        payload['available_dependencies'] = deps['available'] if 'dependency_missing_override' not in inputs else []
        payload['missing_dependencies'] = deps['missing'] if 'dependency_missing_override' not in inputs else ['simulated_missing'] * missing_dependency_count
        payload['memory_source'] = memory.get('source', 'unknown')
        payload['gpu_detection_confidence'] = gpu.get('confidence', 0.0)
        payload['registry_path'] = str(self.registry_path)
        payload['history_path'] = str(self.history_path)
        payload['registry_written'] = self._write_json(self.registry_path, payload)
        payload['history_written'] = self._append_history(payload)
        payload['diagnostics'] = {
            'primitive': PRIMITIVE,
            'non_redundant_role': 'local_node_capability_inventory',
            'supports_future_phases': ['F3', 'F5', 'F7', 'F10', 'F11', 'F12'],
            'closure_pressure_added': 0.0,
            'capability_keys': CAPABILITY_KEYS,
            'scoring_model': 'bounded_weighted_local_capability_index_v1',
        }
        return payload
