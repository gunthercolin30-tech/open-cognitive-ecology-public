#!/bin/bash
set -euo pipefail
umask 077
root="${1:-$HOME/open-cognitive-ecology}"
destination="${2:-$HOME/Downloads}"
if ! command -v python3 >/dev/null 2>&1; then
  printf 'python3 introuvable.\n' >&2
  exit 1
fi
workdir=$(mktemp -d "${TMPDIR:-/tmp}/oce-pc405-collect.XXXXXXXX")
trap 'rm -rf -- "$workdir"' EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
cat > "$workdir/collect_pc405_authority_inputs.py" <<'OCE_COLLECTOR_PY'
"""Read only an exact allowlist; write one ZIP outside the project."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, stat, subprocess, sys, zipfile

PATHS = ['oif_review/campaigns/P159-OCC1A/occ1a_governed_institutional_declaration_binding.json', 'oif_review/campaigns/P159-OCC1A/occ1a_initial_development_authority_materialization.json', 'oif_review/campaigns/P159-OCC1A/occ1a_institutional_authority_amendment_dossier.json', 'oif_review/campaigns/P159-OCC1A/occ1a_human_adoption_decisions.json', 'governance/human_decision_records/pc405_institutional_issuer_decision_packet_v1.json', 'governance/human_decision_records/pc405_two_human_development_authority_v1.json', 'governance/human_decision_records/pc405_historical_witness_reconciliation_v1.json', 'ontology/human_reserved_authority_registry.py', 'ontology/occ_independent_institutional_authority_verifier.py', 'runtime/pc405_broker_service.py', 'runtime/pc405_p160_source_contract.py']
KNOWN_CODE = {'ontology/occ_independent_institutional_authority_verifier.py': 'd325e45d8b27a8c14c0988cd69233db2aa0188c552fbe8ba19eb6aac779c8a25', 'runtime/pc405_broker_service.py': '5bdc6c8c3a6c899293a576556950aa5665a0ee2ea9c9b049509747109d044615', 'runtime/pc405_p160_source_contract.py': '1c8c254e323672ddd57aef3f6f259074f755e4f80fe6987e826fc1b767d610b7'}
LIMIT = 16 * 1024 * 1024
SENSITIVE = {"private_key", "secret", "raw_secret", "password", "api_key",
             "access_token", "refresh_token", "client_secret"}


def sensitive(value):
    if isinstance(value, dict):
        return any(str(k).lower() in SENSITIVE or sensitive(v) for k, v in value.items())
    if isinstance(value, list):
        return any(sensitive(v) for v in value)
    return False


def read_file(root, relative):
    path = root / relative
    cursor = root
    for part in Path(relative).parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise ValueError("symlink_excluded")
    fd = os.open(str(path), os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) |
                 getattr(os, "O_NONBLOCK", 0))
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            raise ValueError("not_single_link_regular_file")
        if before.st_size > LIMIT:
            raise ValueError("file_exceeds_16_MiB")
        with os.fdopen(fd, "rb", closefd=False) as stream:
            data = stream.read(LIMIT + 1)
        after = os.fstat(fd)
        signature = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
        if len(data) > LIMIT or signature(before) != signature(after):
            raise ValueError("file_changed_during_read")
        text = data.decode("utf-8")
        if any(marker in text for marker in ("BEGIN PRIVATE KEY", "BEGIN RSA PRIVATE KEY",
                                            "BEGIN EC PRIVATE KEY", "BEGIN OPENSSH PRIVATE KEY")):
            raise ValueError("private_key_material_excluded")
        if relative.endswith(".json"):
            document = json.loads(text)
            if sensitive(document):
                raise ValueError("sensitive_json_fields_excluded")
        return data
    finally:
        os.close(fd)


def git_value(root, args):
    try:
        result = subprocess.run(["git", "-C", str(root)] + args,
                                capture_output=True, text=True, timeout=10)
        return result.stdout.strip() if result.returncode == 0 else "UNAVAILABLE"
    except (OSError, subprocess.TimeoutExpired):
        return "UNAVAILABLE"


def main():
    root = Path(sys.argv[1]).expanduser().resolve(strict=True)
    destination = Path(sys.argv[2]).expanduser().resolve(strict=True)
    if not root.is_dir() or not (root / "ontology_inventory.txt").is_file():
        raise ValueError("OCE project and ontology_inventory.txt required")
    if not destination.is_dir() or destination == root or root in destination.parents:
        raise ValueError("output directory must exist outside the project")
    report = {"schema": "oce.p162.pc405.targeted-authority-collection.v1",
              "read_only_project": True, "authority_created": False,
              "admission_enabled": False,
              "git_branch": git_value(root, ["rev-parse", "--abbrev-ref", "HEAD"]),
              "git_head": git_value(root, ["rev-parse", "HEAD"]), "files": []}
    payloads = []
    for relative in PATHS:
        item = {"path": relative}
        try:
            data = read_file(root, relative)
            digest = hashlib.sha256(data).hexdigest()
            item.update(bytes=len(data), sha256=digest)
            if KNOWN_CODE.get(relative) == digest:
                item["status"] = "UNCHANGED_CODE_ALREADY_SUPPLIED"
            else:
                item["status"] = "INCLUDED"
                payloads.append((relative, data))
        except FileNotFoundError:
            item["status"] = "MISSING"
        except (OSError, ValueError, UnicodeError, RecursionError) as exc:
            item.update(status="EXCLUDED_OR_UNREADABLE", reason=str(exc))
        report["files"].append(item)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output = destination / ("OCE_P162_PC405_AUTHORITY_INPUTS_" + stamp + "_" + str(os.getpid()) + ".zip")
    # Use exclusive creation: never overwrite an earlier collection.
    created = False
    try:
        with output.open("xb") as stream:
            created = True
            with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                for relative, data in payloads:
                    archive.writestr(relative, data)
                archive.writestr("COLLECTION_MANIFEST.json", json.dumps(report, indent=2) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        with zipfile.ZipFile(output) as archive:
            if archive.testzip() is not None:
                raise ValueError("archive_integrity_failure")
    except BaseException:
        # A failed collection is not a deliverable. Never delete another run's file.
        if created:
            output.unlink(missing_ok=True)
        raise
    print("ZIP : " + str(output))
    print("SHA256 : " + hashlib.sha256(output.read_bytes()).hexdigest())
    print("Included : " + str(len(payloads)) + " / " + str(len(PATHS)) + " allowed paths")
    for item in report["files"]:
        if item["status"] in ("MISSING", "EXCLUDED_OR_UNREADABLE"):
            print(item["status"] + " : " + item["path"])
    print("No project file modified; missing evidence is not PASS.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        raise SystemExit("COLLECTION_FAILED: " + str(exc))
OCE_COLLECTOR_PY
python3 "$workdir/collect_pc405_authority_inputs.py" "$root" "$destination"
