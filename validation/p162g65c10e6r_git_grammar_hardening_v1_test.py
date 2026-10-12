import pytest
def test_exact_historical_forms():
 from ontology.governed_git_exact_process import _bounded
 for a in [["git","remote","-v"],["git","tag","-l"],["git","rev-parse","HEAD"],["git","branch","--show-current"],["git","ls-files","--others","--exclude-standard"],["git","diff","--cached","--name-only"],["git","log","-80","--decorate","--oneline"]]: assert _bounded(a)==a
def test_delegation_denied_exact():
 from ontology.governed_git_exact_process import _bounded
 for x in ["--ext-diff","--textconv","-c","-c=x=y","--config-env","--config-env=x=y"]:
  with pytest.raises(PermissionError): _bounded(["git","diff",x])
def test_delegation_denied_readonly():
 from ontology.governed_git_readonly_process import governed_git_subprocess as g
 for x in ["--ext-diff","--textconv","-c","-c=x=y","--config-env","--config-env=x=y"]:
  with pytest.raises(PermissionError): g._check(["git","diff",x])
def test_effect_argv():
 from ontology.governed_git_exact_process import _effect_argv
 assert _effect_argv(["git","diff","--name-only"])==["git","diff","--no-ext-diff","--name-only"]
 assert _effect_argv(["git","show","HEAD"])==["git","show","--no-ext-diff","HEAD"]
def test_env_neutralized():
 from ontology.governed_git_exact_process import _safe_env
 e=_safe_env({"PATH":"/bin","GIT_EXTERNAL_DIFF":"evil","GIT_CONFIG_COUNT":"1","GIT_SSH_COMMAND":"evil","GIT_ASKPASS":"evil","GIT_PAGER":"evil"})
 assert e["PATH"]=="/bin" and e["GIT_PAGER"]=="cat" and e["PAGER"]=="cat"
 for k in ["GIT_EXTERNAL_DIFF","GIT_CONFIG_COUNT","GIT_SSH_COMMAND","GIT_ASKPASS"]: assert k not in e
