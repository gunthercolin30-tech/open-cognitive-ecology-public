from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
D=lambda: json.loads((ROOT/"validation_artifacts/p162/p162g/g65c1/git_readonly_migration.json").read_text())
def test_modules_mediated():
    # Progression-aware: c1 readonly may later become stricter c2b exact mediation.
    for rel in D()["modules"]:
        s=(ROOT/rel).read_text()
        assert "import subprocess" not in s
        assert ("governed_git_readonly_process" in s or "governed_git_exact_process" in s)
def test_backups():
    for rel in D()["modules"]:
        p=ROOT/rel
        assert p.with_name(p.name+".bak.p162g65c1").is_file()
def test_facade_narrow():
    s=(ROOT/"ontology/governed_git_readonly_process.py").read_text()
    assert 'a[1]=="remote" and a[2:]!=["-v"]' in s
    assert 'a[1]=="tag" and a[2:]!=["-l"]' in s
    assert "shell=False" in s
def test_no_premature_closure():
    d=D()
    assert d["process_bypass_zero_claimed"] is False
    assert d["process_migration_complete"] is False
    assert d["p162g_closure_not_claimed"] is True
