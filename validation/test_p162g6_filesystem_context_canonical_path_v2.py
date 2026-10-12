from pathlib import Path
from tempfile import TemporaryDirectory
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext

with TemporaryDirectory() as td:
    lexical_root=Path(td)
    canonical_root=lexical_root.resolve()
    target=lexical_root/"future.html"
    ctx=GovernedFilesystemEffectContext(slots={"unused":[]},root_path=lexical_root)
    assert ctx.root_path==canonical_root
    assert ctx._relative(target)=="future.html"
    nested=lexical_root/"a"/"b"/"future.html"
    assert ctx._relative(nested)=="a/b/future.html"
    outside=lexical_root.parent/"outside-governed-root.txt"
    try:
        ctx._relative(outside)
        raise AssertionError("outside_target_not_rejected")
    except RuntimeError as exc:
        assert "outside governed root" in str(exc)
print("P162G6_FILESYSTEM_CONTEXT_CANONICAL_PATH_OK")
print("MACOS_VAR_PRIVATE_VAR_ALIAS_OK")
print("NONEXISTENT_IN_ROOT_TARGET_OK")
print("OUTSIDE_ROOT_FAIL_CLOSED_OK")
