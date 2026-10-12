import ast,inspect,textwrap,pytest
from ontology import occ_independent_constitutional_verification_report as r
def test_missing_context_fails_before_output(tmp_path):
    target=tmp_path/r.REPORT_REL
    with pytest.raises(RuntimeError,match="occ1f_report_filesystem_effect_context_required"): r.materialize(tmp_path)
    assert not target.exists()
def test_no_ambient_triad_and_main_transports():
    s=inspect.getsource(r.materialize);t=ast.parse(textwrap.dedent(s));attrs=[n.func.attr for n in ast.walk(t) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)]
    assert not ({"mkdir","replace","unlink","mkstemp"} & set(attrs))
    assert all(x in s for x in ("FS_CREATE_DIRS","FS_WRITE_REPLACE_BYTES","filesystem_effect_context.begin()"))
    assert "materialize(root, filesystem_effect_context)" in inspect.getsource(r.main)
