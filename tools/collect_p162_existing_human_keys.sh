#!/bin/bash
set -euo pipefail
umask 077
root="${1:-$HOME/open-cognitive-ecology}"
destination="${2:-$HOME/Downloads}"
if ! command -v python3 >/dev/null 2>&1; then
  printf 'python3 introuvable.\n' >&2
  exit 1
fi
workdir=$(mktemp -d "${TMPDIR:-/tmp}/oce-existing-keys.XXXXXXXX")
trap 'rm -rf -- "$workdir"' EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
cat > "$workdir/collect_existing_human_keys.py" <<'OCE_COLLECTOR_PY'
"""Read only an exact allowlist; write one ZIP outside the project."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, stat, subprocess, sys, zipfile, re, sqlite3, tempfile
from urllib.parse import quote

KNOWN_CODE = {}
PATHS = []
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


# Discovery is limited to governance evidence and named Downloads documents.
NAME = re.compile(r"witness|attest|trust|signature|signed|enroll|public.?key|pc405|p095|p105", re.I)
DB_TABLES = {
    "pc5m3_trusted_keys": ("key_id", "authority_id", "pem", "enrolled_at"),
    "pc5m3_revoked_keys": ("key_id", "revoked_at"),
    "pc5m3_trust_events": ("event_id", "event_sha256", "recorded_at"),
}

def discover(root, downloads):
    found = []
    governance = root / "governance"
    if governance.is_dir() and not governance.is_symlink():
        for directory, dirs, files in os.walk(governance, followlinks=False):
            dirs[:] = sorted(d for d in dirs if not d.startswith(".") and
                             not (Path(directory) / d).is_symlink())
            for name in sorted(files):
                path = Path(directory) / name
                if path.suffix.lower() in (".pem", ".pub", ".sqlite3", ".sqlite", ".db"):
                    found.append((root, path.relative_to(root).as_posix(), "project/"))
                elif path.suffix.lower() == ".json" and NAME.search(name):
                    found.append((root, path.relative_to(root).as_posix(), "project/"))
    if downloads.is_dir():
        for path in sorted(downloads.iterdir()):
            if (path.name.startswith("OCE_") and NAME.search(path.name) and
                    path.suffix.lower() in (".json", ".pem", ".pub")):
                found.append((downloads, path.name, "downloads/"))
    return found

def public_key_file(data):
    text = data.decode("ascii").strip()
    if text.startswith("-----BEGIN PUBLIC KEY-----") and text.endswith("-----END PUBLIC KEY-----"):
        return True
    return text.startswith(("ssh-ed25519 ", "ssh-rsa ", "ecdsa-sha2-"))

def export_trust_tables(root, relative):
    # No raw SQLite file is copied. Read only fixed, public-evidence columns.
    path = root / relative
    cursor = root
    for part in Path(relative).parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise ValueError("symlink_excluded")
    st = path.stat()
    if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1:
        raise ValueError("database_not_regular")
    # SQLite may create shared-memory sidecars even with mode=ro. Work on a
    # stable private copy including WAL; never open the source with SQLite.
    snapshot = tempfile.TemporaryDirectory(prefix="oce-trust-snapshot-")
    copied = Path(snapshot.name) / "trust.sqlite3"
    observed = []
    try:
        for source, target in ((path, copied), (Path(str(path)+"-wal"), Path(str(copied)+"-wal"))):
            try:
                fd = os.open(str(source), os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) |
                             getattr(os, "O_NONBLOCK", 0))
            except FileNotFoundError:
                if source == path:
                    raise
                observed.append((source, None))
                continue
            try:
                a = os.fstat(fd)
                if not stat.S_ISREG(a.st_mode) or a.st_nlink != 1 or a.st_size > 128*1024*1024:
                    raise ValueError("unsafe_or_oversize_database_component")
                with os.fdopen(fd, "rb", closefd=False) as stream:
                    raw = stream.read(128*1024*1024+1)
                b = os.fstat(fd)
                fingerprint = lambda v: (v.st_dev,v.st_ino,v.st_size,v.st_mtime_ns,v.st_ctime_ns)
                if fingerprint(a) != fingerprint(b) or len(raw) > 128*1024*1024:
                    raise ValueError("database_changed_during_copy")
                target.write_bytes(raw)
                observed.append((source, fingerprint(b)))
            finally:
                os.close(fd)
        for source, expected in observed:
            if source.is_symlink():
                raise ValueError("database_component_symlink")
            if expected is None:
                if source.exists(): raise ValueError("database_wal_appeared_during_copy")
            elif fingerprint(source.stat()) != expected:
                raise ValueError("database_changed_during_copy")
        uri = "file:" + quote(str(copied), safe="/") + "?mode=ro"
        con = sqlite3.connect(uri, uri=True, timeout=3, isolation_level=None)
    except BaseException:
        snapshot.cleanup()
        raise
    try:
        con.execute("PRAGMA query_only=ON")
        con.execute("BEGIN")
        present = {x[0] for x in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        result = {}
        for table, columns in DB_TABLES.items():
            if table not in present:
                continue
            # Table and column identifiers are literal constants, never file data.
            query = "SELECT " + ",".join(columns) + " FROM " + table + " ORDER BY " + columns[0]
            rows = con.execute(query).fetchall()
            result[table] = [dict(zip(columns, row)) for row in rows]
        for row in result.get("pc5m3_trusted_keys", []):
            if type(row.get("pem")) is not str or not public_key_file(row["pem"].encode("ascii")):
                raise ValueError("non_public_key_in_trust_table")
        if not result:
            return None
        return (json.dumps({"source": relative, "tables": result}, indent=2,
                           allow_nan=False) + "\n").encode()
    finally:
        con.close()
        snapshot.cleanup()


def main():
    root = Path(sys.argv[1]).expanduser().resolve(strict=True)
    destination = Path(sys.argv[2]).expanduser().resolve(strict=True)
    if not root.is_dir() or not (root / "ontology_inventory.txt").is_file():
        raise ValueError("OCE project and ontology_inventory.txt required")
    if not destination.is_dir() or destination == root or root in destination.parents:
        raise ValueError("output directory must exist outside the project")
    report = {"schema": "oce.p162.pc405.existing-human-keys-collection.v1",
              "read_only_project": True, "authority_created": False,
              "admission_enabled": False,
              "git_branch": git_value(root, ["rev-parse", "--abbrev-ref", "HEAD"]),
              "git_head": git_value(root, ["rev-parse", "HEAD"]), "files": []}
    payloads = []
    candidates = discover(root, destination)
    for source_root, relative, prefix in candidates:
        item = {"path": prefix + relative}
        try:
            if Path(relative).suffix.lower() in (".db", ".sqlite", ".sqlite3"):
                data = export_trust_tables(source_root, relative)
                if data is None:
                    item["status"] = "NO_RELEVANT_PUBLIC_TRUST_TABLES"
                    report["files"].append(item)
                    continue
                relative = relative + ".public-trust.json"
            else:
                data = read_file(source_root, relative)
                if Path(relative).suffix.lower() in (".pem", ".pub") and not public_key_file(data):
                    raise ValueError("not_a_public_key_file")
            if sensitive(json.loads(data)) if relative.endswith(".json") else False:
                raise ValueError("sensitive_json_fields_excluded")
            digest = hashlib.sha256(data).hexdigest()
            item.update(bytes=len(data), sha256=digest)
            if KNOWN_CODE.get(relative) == digest:
                item["status"] = "UNCHANGED_CODE_ALREADY_SUPPLIED"
            else:
                item["status"] = "INCLUDED"
                payloads.append((prefix + relative, data))
        except FileNotFoundError:
            item["status"] = "MISSING"
        except (OSError, ValueError, UnicodeError, RecursionError, sqlite3.Error) as exc:
            item.update(status="EXCLUDED_OR_UNREADABLE", reason=str(exc))
        report["files"].append(item)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output = destination / ("OCE_P162_EXISTING_HUMAN_KEYS_" + stamp + "_" + str(os.getpid()) + ".zip")
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
    print("Included : " + str(len(payloads)) + " / " + str(len(candidates)) + " candidate evidence paths")
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
python3 "$workdir/collect_existing_human_keys.py" "$root" "$destination"
