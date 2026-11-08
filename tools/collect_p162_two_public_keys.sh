#!/bin/bash
set -euo pipefail
umask 077
root="${1:-$HOME/open-cognitive-ecology}"
downloads="${2:-$HOME/Downloads}"
command -v python3 >/dev/null 2>&1 || { printf 'python3 introuvable.\n' >&2; exit 1; }
workdir=$(mktemp -d "${TMPDIR:-/tmp}/oce-two-public-keys.XXXXXXXX")
trap 'rm -rf -- "$workdir"' EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
cat > "$workdir/collect_two_public_keys.py" <<'OCE_TWO_KEYS_PY'
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, stat, sys, zipfile

EXPECTED = {
    "governance_public.pem": "c624fa20f52f6aeda325b150234390e3acc1769731c5c299a212e89386301399",
    "witness_public.pem": "fe7722c74ab1390b54e2f3d77baddf90646e8017951cf840baf1fc2a26a06ffe",
}
LIMIT = 8192
SKIP = {".git", ".venv", "venv", "node_modules", "__pycache__"}


def accept(name, data):
    if not data.startswith(b"-----BEGIN PUBLIC KEY-----"):
        return False
    if b"PRIVATE KEY" in data or len(data) > LIMIT:
        return False
    return hashlib.sha256(data).hexdigest() == EXPECTED[name]


def main():
    root = Path(sys.argv[1]).expanduser().resolve(strict=True)
    downloads = Path(sys.argv[2]).expanduser().resolve(strict=True)
    if not root.is_dir() or not downloads.is_dir() or downloads == root or root in downloads.parents:
        raise ValueError("project and separate Downloads directory required")
    found = {}
    locations = {}
    failures = []
    checked_archives = 0
    def save(name, data, location):
        if name not in found and accept(name, data):
            found[name] = data
            locations[name] = location
    for base in dict.fromkeys((root, downloads)):
        for directory, dirs, files in os.walk(base, followlinks=False):
            dirs[:] = sorted(d for d in dirs if d not in SKIP and
                             not (Path(directory) / d).is_symlink())
            for filename in sorted(files):
                path = Path(directory) / filename
                is_archive = path.suffix.lower() == ".zip"
                if filename not in EXPECTED and not is_archive:
                    continue
                if path.is_symlink():
                    continue
                try:
                    fd = os.open(str(path), os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) |
                                 getattr(os, "O_NONBLOCK", 0))
                    try:
                        if not stat.S_ISREG(os.fstat(fd).st_mode):
                            continue
                        with os.fdopen(fd, "rb", closefd=False) as stream:
                            if not is_archive:
                                save(filename, stream.read(LIMIT+1), str(path))
                            else:
                                checked_archives += 1
                                with zipfile.ZipFile(stream) as archive:
                                    for entry in archive.infolist():
                                        name = entry.filename.rsplit("/", 1)[-1]
                                        if (name not in EXPECTED or name in found or entry.is_dir()
                                                or entry.file_size > LIMIT):
                                            continue
                                        # Never extract an archive path; bounded read into memory.
                                        with archive.open(entry) as member:
                                            data = member.read(LIMIT+1)
                                        save(name, data, str(path)+" :: "+entry.filename)
                    finally:
                        os.close(fd)
                except (OSError, ValueError, RuntimeError, zipfile.BadZipFile, NotImplementedError) as exc:
                    failures.append({"path":str(path), "error_type":type(exc).__name__})
                if len(found) == len(EXPECTED):
                    break
            if len(found) == len(EXPECTED):
                break
        if len(found) == len(EXPECTED):
            break
    report = {
        "schema":"oce.p162.two-existing-public-keys.v1",
        "expected_sha256":EXPECTED, "locations":locations,
        "found":sorted(found), "missing":sorted(set(EXPECTED)-set(found)),
        "archive_read_errors":failures, "archives_checked":checked_archives,
        "private_keys_collected":False, "signature_verification_performed":False,
        "constitutional_authority_established":False, "project_modified":False,
    }
    output = downloads / ("OCE_P162_TWO_PUBLIC_KEYS_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + str(os.getpid()) + ".zip")
    created = False
    try:
        with output.open("xb") as stream:
            created = True
            with zipfile.ZipFile(stream,"w",compression=zipfile.ZIP_DEFLATED) as archive:
                for name, data in sorted(found.items()):
                    archive.writestr(name, data)
                archive.writestr("COLLECTION_MANIFEST.json",json.dumps(report,indent=2)+"\n")
            stream.flush()
            os.fsync(stream.fileno())
        with zipfile.ZipFile(output) as archive:
            if archive.testzip() is not None:
                raise ValueError("ZIP integrity failure")
    except BaseException:
        if created:
            output.unlink(missing_ok=True)
        raise
    print("ZIP : " + str(output))
    print("SHA256 : " + hashlib.sha256(output.read_bytes()).hexdigest())
    print("Clés publiques retrouvées : " + str(len(found)) + "/2")
    for name in report["missing"]:
        print("ABSENTE : " + name)
    print("Aucune clé privée collectée ; aucun fichier du projet modifié.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        raise SystemExit("COLLECTION_FAILED: " + str(exc))
OCE_TWO_KEYS_PY
python3 "$workdir/collect_two_public_keys.py" "$root" "$downloads"
