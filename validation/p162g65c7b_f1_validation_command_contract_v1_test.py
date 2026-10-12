import pytest
from ontology.f1_validation_command_contract import *
def good():
 return [{"role":r,"kind":"VALIDATION_MAIN"} for r in REQUIRED_ROLES]
def test_exact_seven_roles_and_order():
 assert len(validate_f1_contract(good()))==7
 x=good(); x[0],x[1]=x[1],x[0]
 with pytest.raises(ValueError): validate_f1_contract(x)
def test_opaque_argv_rejected():
 x=good(); x[0]={"role":"functional","kind":"PYTHON_ARGV","args":["x.py"]}
 with pytest.raises(ValueError): validate_f1_contract(x)
def test_registered_script_requires_id_not_path():
 x=good(); x[0]={"role":"functional","kind":"REGISTERED_SCRIPT","script_id":"foo.py"}
 with pytest.raises(ValueError): validate_f1_contract(x)
def test_unresolved_script_never_compiles():
 d=validate_descriptor({"role":"functional","kind":"REGISTERED_SCRIPT","script_id":"functional_probe"})
 with pytest.raises(ValueError): compile_descriptor(d,{})
def test_validation_main_has_closed_grammar():
 d=validate_descriptor({"role":"functional","kind":"VALIDATION_MAIN"})
 assert compile_descriptor(d,{})==("PYTHON_MODULE","validation.main")
 with pytest.raises(ValueError): validate_descriptor({"role":"functional","kind":"VALIDATION_MAIN","args":["x"]})
