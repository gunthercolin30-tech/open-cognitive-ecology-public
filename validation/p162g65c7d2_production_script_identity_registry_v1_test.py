from hashlib import sha256
from pathlib import Path
import pytest
from ontology.production_script_identity_registry import (
    PRODUCTION_SCRIPT_REGISTRY, ProductionScriptIdentity,
    resolve_registered_script, validate_registry,
)

def test_canonical_registry_is_minimal_and_empty():
    assert PRODUCTION_SCRIPT_REGISTRY == {}

def test_unknown_identity_fails_closed(tmp_path):
    with pytest.raises(ValueError, match="unresolved_registered_script"):
        resolve_registered_script(tmp_path, "unknown", {})

def test_valid_identity_requires_exact_hash(tmp_path):
    p=tmp_path/"probe.py"; p.write_text("print('ok')\n")
    h=sha256(p.read_bytes()).hexdigest()
    reg={"probe":ProductionScriptIdentity("probe","probe.py",h)}
    assert resolve_registered_script(tmp_path,"probe",reg)==p.resolve()

def test_hash_drift_is_rejected(tmp_path):
    p=tmp_path/"probe.py"; p.write_text("a=1\n")
    h=sha256(p.read_bytes()).hexdigest()
    reg={"probe":ProductionScriptIdentity("probe","probe.py",h)}
    p.write_text("a=2\n")
    with pytest.raises(ValueError, match="hash_drift"):
        resolve_registered_script(tmp_path,"probe",reg)

def test_symlink_is_rejected(tmp_path):
    target=tmp_path/"real.py"; target.write_text("a=1\n")
    link=tmp_path/"link.py"
    try: link.symlink_to(target)
    except OSError: pytest.skip("symlink unavailable")
    h=sha256(target.read_bytes()).hexdigest()
    reg={"probe":ProductionScriptIdentity("probe","link.py",h)}
    with pytest.raises(ValueError, match="symlink"):
        resolve_registered_script(tmp_path,"probe",reg)

def test_path_like_identity_is_rejected():
    h="0"*64
    with pytest.raises(ValueError, match="opaque_script_id"):
        validate_registry({"x.py":ProductionScriptIdentity("x.py","x.py",h)})

def test_parent_traversal_is_rejected():
    h="0"*64
    with pytest.raises(ValueError, match="canonical_relative"):
        validate_registry({"x":ProductionScriptIdentity("x","../x.py",h)})
