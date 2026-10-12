import pytest
from ontology.fly_cli_exact_command_contract import *
def test_ops(): assert ALLOWED_OPERATIONS==frozenset({OP_AUTH_WHOAMI,OP_STATUS,OP_APPS_LIST,OP_SSH_IDENTITY_PROBE})
def test_no_app():
 assert compile_fly_argv(FlyCommandSpec(OP_AUTH_WHOAMI))==("fly","auth","whoami")
 assert compile_fly_argv(FlyCommandSpec(OP_APPS_LIST))==("fly","apps","list")
def test_app():
 assert compile_fly_argv(FlyCommandSpec(OP_STATUS,"oce-node-1"))==("fly","status","--app","oce-node-1")
 assert compile_fly_argv(FlyCommandSpec(OP_SSH_IDENTITY_PROBE,"oce-node-1"))==("fly","ssh","console","--app","oce-node-1","-C","hostname && uname -a")
@pytest.mark.parametrize("bad",["","-x","A","a_b","a/b","a;rm","a b","a"*64])
def test_bad_app(bad):
 with pytest.raises(ValueError): compile_fly_argv(FlyCommandSpec(OP_STATUS,bad))
def test_unknown():
 with pytest.raises(PermissionError): compile_fly_argv(FlyCommandSpec("FLY_DEPLOY","oce"))
def test_unused_app():
 with pytest.raises(ValueError): compile_fly_argv(FlyCommandSpec(OP_APPS_LIST,"oce"))
def test_raw(): assert raw_argv_is_authority(["fly","deploy"]) is False
def test_nonexecuting():
 import inspect,ontology.fly_cli_exact_command_contract as m
 s=inspect.getsource(m); assert "subprocess" not in s and "os.system" not in s and "Popen" not in s
