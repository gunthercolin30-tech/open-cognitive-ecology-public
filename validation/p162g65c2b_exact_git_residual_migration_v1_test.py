from pathlib import Path
import json,pytest
ROOT=Path(__file__).resolve().parents[1]
R=ROOT/"validation_artifacts/p162/p162g/g65c2b/residual_git_migration.json"
def d(): return json.loads(R.read_text())
def test_all_residual_git_modules_mediated():
 for rel in d()["modules"]:
  s=(ROOT/rel).read_text()
  # Git mediation is the c2b invariant. An explicitly aliased non-Git
  # stdlib subprocess may remain visible for later G6.5c4 governance.
  assert "governed_git_exact_process" in s
  assert "import subprocess\n" not in s
  assert "import subprocess as subprocess" not in s
def test_backups_exist():
 for rel in d()["modules"]:
  p=ROOT/rel
  assert p.with_name(p.name+".bak.p162g65c2b").is_file()
def test_grammar_rejects_git_write_and_config_injection():
 from ontology.governed_git_exact_process import _bounded
 for a in [["git","push"],["git","commit"],["git","checkout"],["git","remote","add","x","y"],["git","tag","v1"],["git","rev-parse","--verify","HEAD"],["git","log","--exec=x"]]:
  with pytest.raises(PermissionError): _bounded(a)
def test_observed_bounded_forms_are_accepted():
 from ontology.governed_git_exact_process import _bounded
 for a in [["git","remote","-v"],["git","tag","-l"],["git","rev-parse","HEAD"],["git","rev-parse","--abbrev-ref","HEAD"],["git","log","-80","--decorate","--oneline"]]:
  assert _bounded(a)==a
def test_no_premature_zero():
 x=d()
 assert x["process_bypass_zero_claimed"] is False
 assert x["process_migration_complete"] is False
 assert x["p162g_closure_not_claimed"] is True
