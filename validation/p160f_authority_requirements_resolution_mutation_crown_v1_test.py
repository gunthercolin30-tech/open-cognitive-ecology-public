from pathlib import Path
import hashlib
from ontology import p160_authority_requirements_resolution as m
EXPECTED="6c9959a1e413af550e61b82e71e16cb684bf92a07f5b6fe784e3579beb86c60c"
def sh(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def test_exact_hash(): assert sh(m.__file__)==EXPECTED
def test_boundaries():
    b=m.manifest()["boundaries"]
    assert all(b[k] is False for k in ("authority_created","authorization_created","execution_performed","p160g_opened","p161_opened"))
