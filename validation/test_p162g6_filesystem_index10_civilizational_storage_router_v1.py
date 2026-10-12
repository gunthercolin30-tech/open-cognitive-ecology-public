from pathlib import Path
import ast
import shutil
import pytest

import ontology.civilizational_storage_router as m
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
from ontology.governed_filesystem_effector import GovernedFilesystemEffector
from ontology.scoped_handle_broker import ScopedEffectHandle

class Broker:
    def __init__(self, handles):
        self.known = {h.handle_id for h in handles}
        self.used = set()
    def consume_once(self, handle_id):
        if handle_id not in self.known or handle_id in self.used:
            return False
        self.used.add(handle_id)
        return True

def handle(i, rel):
    return ScopedEffectHandle(
        i, "lease", "reservation", "claim", "adapter", "filesystem",
        "FS_CREATE_DIR", "filesystem://r1/" + rel, "scope", "adapter",
        "2999-01-01T00:00:00Z"
    )

def context(root, rels):
    hs = [handle("h%d" % i, rel) for i, rel in enumerate(rels)]
    return GovernedFilesystemEffectContext(
        slots={"storage_route_parent_create": hs},
        effector=GovernedFilesystemEffector(
            root_registry={"r1": str(root)},
            handle_broker=Broker(hs),
        ),
        root_id="r1",
        root_path=root,
        adapter_id="adapter",
        effector_id="filesystem",
    )

def router(root):
    return m.CivilizationalStorageRouter(
        root=root,
        ssd_root=root / "absent_ssd",
        fallback_root=root / "fallback",
    )

def expected_parent_rels():
    return ["fallback", "fallback/archive", "fallback/archive/x"]

def test_create_parent_false_is_pure_routing(tmp_path):
    r = router(tmp_path)
    p = r.route_path("x/y.json", category="archive", create_parent=False)
    assert p == tmp_path / "fallback" / "archive" / "x" / "y.json"
    assert list(tmp_path.iterdir()) == []

def test_existing_parent_needs_no_context_and_has_no_effect(tmp_path):
    parent = tmp_path / "fallback" / "archive" / "x"
    parent.mkdir(parents=True)
    before = sorted(str(p.relative_to(tmp_path)) for p in tmp_path.rglob("*"))
    p = router(tmp_path).route_path("x/y.json", category="archive")
    after = sorted(str(p.relative_to(tmp_path)) for p in tmp_path.rglob("*"))
    assert p.parent == parent
    assert before == after

def test_missing_parent_without_context_fails_closed(tmp_path):
    with pytest.raises(PermissionError, match="filesystem_effect_context_required"):
        router(tmp_path).route_path("x/y.json", category="archive")
    assert list(tmp_path.iterdir()) == []

def test_missing_parent_chain_real_tcb(tmp_path):
    c = context(tmp_path, expected_parent_rels())
    p = router(tmp_path).route_path(
        "x/y.json", category="archive", filesystem_context=c
    )
    assert p.parent.is_dir()
    assert c.remaining()["storage_route_parent_create"] == 0
    assert c.authority_minting is False

def test_exact_cardinality_checked_before_any_effect(tmp_path):
    c = context(tmp_path, expected_parent_rels()[:-1])
    with pytest.raises(RuntimeError, match="cardinality_mismatch"):
        router(tmp_path).route_path(
            "x/y.json", category="archive", filesystem_context=c
        )
    assert list(tmp_path.iterdir()) == []

def test_target_binding_fails_closed(tmp_path):
    rels = ["wrong", "wrong/a", "wrong/a/b"]
    c = context(tmp_path, rels)
    with pytest.raises(RuntimeError, match="target_mismatch"):
        router(tmp_path).route_path(
            "x/y.json", category="archive", filesystem_context=c
        )
    assert not (tmp_path / "fallback").exists()

def test_context_replay_fails_closed(tmp_path):
    c = context(tmp_path, expected_parent_rels())
    router(tmp_path).route_path(
        "x/y.json", category="archive", filesystem_context=c
    )
    shutil.rmtree(tmp_path / "fallback")
    with pytest.raises(RuntimeError, match="context replay"):
        router(tmp_path).route_path(
            "x/y.json", category="archive", filesystem_context=c
        )
    assert not (tmp_path / "fallback").exists()

def test_outside_root_fails_closed(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    outside = tmp_path / "outside"
    r = m.CivilizationalStorageRouter(
        root=root, ssd_root=root / "absent_ssd", fallback_root=outside
    )
    missing = r._missing_parent_chain(outside / "archive" / "x")
    c = context(root, ["placeholder%d" % i for i in range(len(missing))])
    with pytest.raises(RuntimeError, match="outside governed root"):
        r.route_path("x/y.json", category="archive", filesystem_context=c)
    assert not outside.exists()

def test_route_directory_transports_context(tmp_path):
    rels = ["fallback", "fallback/memory", "fallback/memory/external_memory"]
    c = context(tmp_path, rels)
    p = router(tmp_path).route_directory(
        "external_memory", category="memory", filesystem_context=c
    )
    assert p == tmp_path / "fallback" / "memory" / "external_memory"
    assert p.is_dir()
    assert c.remaining()["storage_route_parent_create"] == 0

def test_route_path_contains_no_ambient_mutator():
    src = Path(m.__file__).read_text(encoding="utf-8")
    tree = ast.parse(src)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "CivilizationalStorageRouter")
    fn = next(n for n in cls.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == "route_path")
    forbidden = []
    for n in ast.walk(fn):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute):
            if n.func.attr in {"mkdir", "write_text", "write_bytes", "open", "unlink", "rename"}:
                forbidden.append((n.func.attr, n.lineno))
    assert forbidden == []

def write_handle(i, rel):
    return ScopedEffectHandle(
        i, "lease", "reservation", "claim", "adapter", "filesystem",
        "FS_WRITE_REPLACE_BYTES", "filesystem://r1/" + rel, "scope", "adapter",
        "2999-01-01T00:00:00Z"
    )

def write_context(root, parent_rels, target_rel):
    parents = [handle("p%d" % i, rel) for i, rel in enumerate(parent_rels)]
    writer = write_handle("w0", target_rel)
    hs = parents + [writer]
    return GovernedFilesystemEffectContext(
        slots={"storage_route_parent_create": parents, "storage_route_write_replace": [writer]},
        effector=GovernedFilesystemEffector(root_registry={"r1": str(root)}, handle_broker=Broker(hs)),
        root_id="r1", root_path=root, adapter_id="adapter", effector_id="filesystem",
    )

def test_write_text_real_tcb_creates_parents_and_file(tmp_path):
    c = write_context(tmp_path, expected_parent_rels(), "fallback/archive/x/y.txt")
    p = router(tmp_path).write_text("x/y.txt", "hello", category="archive", filesystem_context=c)
    assert p.read_text(encoding="utf-8") == "hello"
    assert c.remaining()["storage_route_parent_create"] == 0
    assert c.remaining()["storage_route_write_replace"] == 0
    assert c.authority_minting is False

def test_write_text_real_tcb_replaces_existing_file(tmp_path):
    parent = tmp_path / "fallback" / "archive" / "x"
    parent.mkdir(parents=True)
    target = parent / "y.txt"
    target.write_text("old", encoding="utf-8")
    c = write_context(tmp_path, [], "fallback/archive/x/y.txt")
    p = router(tmp_path).write_text("x/y.txt", "new", category="archive", filesystem_context=c)
    assert p == target
    assert target.read_text(encoding="utf-8") == "new"

def test_write_text_without_context_fails_closed_before_effect(tmp_path):
    with pytest.raises(PermissionError, match="filesystem_effect_context_required_for_storage_write"):
        router(tmp_path).write_text("x/y.txt", "hello", category="archive")
    assert list(tmp_path.iterdir()) == []

def test_write_text_missing_write_authority_fails_before_parent_effect(tmp_path):
    parents = [handle("p%d" % i, rel) for i, rel in enumerate(expected_parent_rels())]
    c = GovernedFilesystemEffectContext(
        slots={"storage_route_parent_create": parents},
        effector=GovernedFilesystemEffector(root_registry={"r1": str(tmp_path)}, handle_broker=Broker(parents)),
        root_id="r1", root_path=tmp_path, adapter_id="adapter", effector_id="filesystem",
    )
    with pytest.raises(RuntimeError, match="storage_route_write_replace_cardinality_mismatch"):
        router(tmp_path).write_text("x/y.txt", "hello", category="archive", filesystem_context=c)
    assert list(tmp_path.iterdir()) == []

def test_write_text_wrong_target_fails_closed(tmp_path):
    c = write_context(tmp_path, expected_parent_rels(), "fallback/archive/x/wrong.txt")
    with pytest.raises(RuntimeError, match="target_mismatch"):
        router(tmp_path).write_text("x/y.txt", "hello", category="archive", filesystem_context=c)
    assert not (tmp_path / "fallback" / "archive" / "x" / "y.txt").exists()

def test_write_text_encoding_failure_has_no_effect(tmp_path):
    c = write_context(tmp_path, expected_parent_rels(), "fallback/archive/x/y.txt")
    with pytest.raises(UnicodeEncodeError):
        router(tmp_path).write_text("x/y.txt", "é", category="archive", encoding="ascii", filesystem_context=c)
    assert list(tmp_path.iterdir()) == []

def test_write_text_contains_no_ambient_mutator():
    src = Path(m.__file__).read_text(encoding="utf-8")
    tree = ast.parse(src)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "CivilizationalStorageRouter")
    fn = next(n for n in cls.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == "write_text")
    forbidden = []
    for n in ast.walk(fn):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute):
            if n.func.attr in {"mkdir", "write_text", "write_bytes", "open", "unlink", "rename", "replace"}:
                forbidden.append((n.func.attr, n.lineno))
    assert forbidden == []
