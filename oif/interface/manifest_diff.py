"""Deterministic, renderer-independent semantic diff for OIF manifests.

OIF-2H compares validated declarative interface specifications.  It performs no
provider resolution, rendering, persistence, dynamic import, execution, or
governance action.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping, Optional, Sequence, Tuple, Union

from .manifest_validator import ManifestValidator
from .serialization import SerializationViolation
from .specification import InterfaceSpecification

MAX_DIFF_ENTRIES = 10000
IDENTITY_KEYS = (
    "zone_id", "layout_id", "region_id", "provider_id", "component_id",
    "operation_id", "permission_id", "preference_id", "tab_id",
)
NON_SEMANTIC_ENTITY_LIST_SUFFIXES = (
    "/navigation/zones", "/layout", "/regions", "/data_sources",
    "/components", "/operations", "/permissions", "/preferences",
)


class ManifestDiffViolation(ValueError):
    """Raised when a safe, validated declarative diff cannot be produced."""


def _escape(value: str) -> str:
    return value.replace("~", "~0").replace("/", "~1")


def _plain(value: Any, depth: int = 0) -> Any:
    if depth > 32:
        raise ManifestDiffViolation("maximum declarative nesting depth exceeded")
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        if value != value or value in (float("inf"), float("-inf")):
            raise ManifestDiffViolation("non-finite numbers are forbidden")
        return value
    if isinstance(value, Mapping):
        result = {}
        for key in sorted(value):
            if not isinstance(key, str):
                raise ManifestDiffViolation("mapping keys must be strings")
            result[key] = _plain(value[key], depth + 1)
        return result
    if isinstance(value, (list, tuple)):
        return [_plain(item, depth + 1) for item in value]
    raise ManifestDiffViolation("unsupported declarative value type: %s" % type(value).__name__)


def _validated_mapping(
    source: Union[InterfaceSpecification, Mapping[str, Any], str, Path],
    source_format: Optional[str],
) -> Mapping[str, Any]:
    if isinstance(source, InterfaceSpecification):
        return _plain(source.as_dict())
    report = ManifestValidator().validate(source, source_format)
    if not report.valid or report.manifest is None:
        codes = ",".join(error.code for error in report.errors[:8]) or "unknown"
        raise ManifestDiffViolation("manifest validation failed: %s" % codes)
    return _plain(report.manifest.as_dict())


def _identity_key(items: Sequence[Any]) -> Optional[str]:
    if not items or not all(isinstance(item, Mapping) for item in items):
        return None
    for key in IDENTITY_KEYS:
        values = [item.get(key) for item in items]
        if all(isinstance(value, str) and value for value in values) and len(values) == len(set(values)):
            return key
    return None


def _common_identity_key(before: Sequence[Any], after: Sequence[Any]) -> Optional[str]:
    if not before and not after:
        return None
    if not all(isinstance(item, Mapping) for item in list(before) + list(after)):
        return None
    for key in IDENTITY_KEYS:
        left = [item.get(key) for item in before]
        right = [item.get(key) for item in after]
        if (all(isinstance(value, str) and value for value in left + right)
                and len(left) == len(set(left)) and len(right) == len(set(right))):
            return key
    return None


def _list_is_non_semantic(path: str, identity_key: Optional[str]) -> bool:
    if identity_key is None:
        return False
    return any(path.endswith(suffix) for suffix in NON_SEMANTIC_ENTITY_LIST_SUFFIXES)


@dataclass(frozen=True)
class DiffEntry:
    change: str
    path: str
    before: Any = None
    after: Any = None
    from_path: Optional[str] = None
    to_path: Optional[str] = None
    domain: str = "manifest"

    def as_dict(self) -> Mapping[str, Any]:
        result = {
            "change": self.change,
            "path": self.path,
            "domain": self.domain,
        }
        if self.change in {"removed", "modified"}:
            result["before"] = _plain(self.before)
        if self.change in {"added", "modified"}:
            result["after"] = _plain(self.after)
        if self.change == "moved":
            result["from_path"] = self.from_path
            result["to_path"] = self.to_path
        return MappingProxyType(result)


@dataclass(frozen=True)
class ManifestDiffReport:
    before_sha256: str
    after_sha256: str
    entries: Tuple[DiffEntry, ...]

    @property
    def changed(self) -> bool:
        return bool(self.entries)

    @property
    def counts(self) -> Mapping[str, int]:
        result = {name: 0 for name in ("added", "removed", "modified", "moved")}
        for entry in self.entries:
            result[entry.change] += 1
        return MappingProxyType(result)

    def as_dict(self) -> Mapping[str, Any]:
        return MappingProxyType({
            "schema": "oif.manifest.diff.v1",
            "changed": self.changed,
            "before_sha256": self.before_sha256,
            "after_sha256": self.after_sha256,
            "counts": dict(self.counts),
            "entries": [dict(entry.as_dict()) for entry in self.entries],
        })

    def canonical_json(self) -> str:
        return json.dumps(_plain(self.as_dict()), ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)

    def sha256(self) -> str:
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()

    def human_text(self) -> str:
        lines = [
            "OIF declarative manifest diff",
            "changed: %s" % ("yes" if self.changed else "no"),
            "added: {added} | removed: {removed} | modified: {modified} | moved: {moved}".format(**self.counts),
        ]
        for entry in self.entries:
            if entry.change == "moved":
                lines.append("MOVED %s -> %s" % (entry.from_path, entry.to_path))
            elif entry.change == "added":
                lines.append("ADDED %s = %s" % (entry.path, _short(entry.after)))
            elif entry.change == "removed":
                lines.append("REMOVED %s = %s" % (entry.path, _short(entry.before)))
            else:
                lines.append("MODIFIED %s: %s -> %s" % (entry.path, _short(entry.before), _short(entry.after)))
        return "\n".join(lines) + "\n"


def _short(value: Any) -> str:
    text = json.dumps(_plain(value), ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return text if len(text) <= 160 else text[:157] + "..."


def _domain(path: str) -> str:
    if path.startswith("/data_sources"):
        return "providers"
    if path.startswith("/operations"):
        return "operations"
    if path.startswith("/permissions"):
        return "permissions"
    if path.startswith("/layout"):
        return "layouts"
    if path.startswith("/components"):
        return "components"
    if path.startswith("/navigation"):
        return "navigation"
    if path.startswith("/preferences"):
        return "preferences"
    return "manifest"


def _append(entries: list[DiffEntry], entry: DiffEntry) -> None:
    entries.append(entry)
    if len(entries) > MAX_DIFF_ENTRIES:
        raise ManifestDiffViolation("maximum diff entry count exceeded")


def _diff(before: Any, after: Any, path: str, entries: list[DiffEntry]) -> None:
    if type(before) is not type(after):
        _append(entries, DiffEntry("modified", path or "/", before, after, domain=_domain(path)))
        return
    if isinstance(before, Mapping):
        before_keys, after_keys = set(before), set(after)
        for key in sorted(before_keys - after_keys):
            child = (path + "/" + _escape(key)) or "/"
            _append(entries, DiffEntry("removed", child, before=before[key], domain=_domain(child)))
        for key in sorted(after_keys - before_keys):
            child = (path + "/" + _escape(key)) or "/"
            _append(entries, DiffEntry("added", child, after=after[key], domain=_domain(child)))
        for key in sorted(before_keys & after_keys):
            _diff(before[key], after[key], path + "/" + _escape(key), entries)
        return
    if isinstance(before, list):
        identity = _common_identity_key(before, after)
        if identity:
            before_map = {item[identity]: item for item in before}
            after_map = {item[identity]: item for item in after}
            before_pos = {item[identity]: index for index, item in enumerate(before)}
            after_pos = {item[identity]: index for index, item in enumerate(after)}
            for item_id in sorted(set(before_map) - set(after_map)):
                child = path + "/@" + _escape(item_id)
                _append(entries, DiffEntry("removed", child, before=before_map[item_id], domain=_domain(path)))
            for item_id in sorted(set(after_map) - set(before_map)):
                child = path + "/@" + _escape(item_id)
                _append(entries, DiffEntry("added", child, after=after_map[item_id], domain=_domain(path)))
            for item_id in sorted(set(before_map) & set(after_map)):
                child = path + "/@" + _escape(item_id)
                _diff(before_map[item_id], after_map[item_id], child, entries)
                if not _list_is_non_semantic(path, identity) and before_pos[item_id] != after_pos[item_id]:
                    _append(entries, DiffEntry(
                        "moved", child,
                        from_path=path + "/" + str(before_pos[item_id]),
                        to_path=path + "/" + str(after_pos[item_id]),
                        domain=_domain(path),
                    ))
            return
        if before == after:
            return
        # Identifier reference lists have meaningful order and support readable moves.
        if all(isinstance(item, str) for item in before + after) and len(before) == len(set(before)) and len(after) == len(set(after)):
            common = set(before) & set(after)
            for item in sorted(set(before) - set(after)):
                _append(entries, DiffEntry("removed", path + "/" + str(before.index(item)), before=item, domain=_domain(path)))
            for item in sorted(set(after) - set(before)):
                _append(entries, DiffEntry("added", path + "/" + str(after.index(item)), after=item, domain=_domain(path)))
            for item in sorted(common):
                old, new = before.index(item), after.index(item)
                if old != new:
                    _append(entries, DiffEntry("moved", path + "/@" + _escape(item), from_path=path + "/" + str(old), to_path=path + "/" + str(new), domain=_domain(path)))
            return
        if len(before) != len(after):
            _append(entries, DiffEntry("modified", path or "/", before, after, domain=_domain(path)))
            return
        for index, (left, right) in enumerate(zip(before, after)):
            _diff(left, right, path + "/" + str(index), entries)
        return
    if before != after:
        _append(entries, DiffEntry("modified", path or "/", before, after, domain=_domain(path)))


def compare_manifests(
    before: Union[InterfaceSpecification, Mapping[str, Any], str, Path],
    after: Union[InterfaceSpecification, Mapping[str, Any], str, Path],
    before_format: Optional[str] = None,
    after_format: Optional[str] = None,
) -> ManifestDiffReport:
    """Validate and compare two OIF manifests without mutating either input."""
    left = _validated_mapping(before, before_format)
    right = _validated_mapping(after, after_format)
    left_json = json.dumps(left, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    right_json = json.dumps(right, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    entries: list[DiffEntry] = []
    _diff(left, right, "", entries)
    ordered = tuple(sorted(entries, key=lambda e: (e.path, e.change, e.from_path or "", e.to_path or "")))
    return ManifestDiffReport(
        hashlib.sha256(left_json.encode("utf-8")).hexdigest(),
        hashlib.sha256(right_json.encode("utf-8")).hexdigest(),
        ordered,
    )
