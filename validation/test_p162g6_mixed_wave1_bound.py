import pytest
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext
class H:
    def __init__(self,n): self.n=n
def test_fifo_cardinality():
    a,b=H(1),H(2); c=GovernedFilesystemEffectContext({"write":[a,b]}); c.begin(); assert c.take("write") is a; assert c.take("write") is b; assert c.remaining()=={"write":0}
def test_replay_fails():
    c=GovernedFilesystemEffectContext({"write":[]}); c.begin()
    with pytest.raises(RuntimeError): c.begin()
def test_missing_slot_fails():
    c=GovernedFilesystemEffectContext({"write":[]}); c.begin()
    with pytest.raises(KeyError): c.take("other")
def test_empty_slot_fails():
    c=GovernedFilesystemEffectContext({"write":[]}); c.begin()
    with pytest.raises(RuntimeError): c.take("write")
def test_take_before_begin_fails():
    c=GovernedFilesystemEffectContext({"write":[H(1)]})
    with pytest.raises(RuntimeError): c.take("write")
def test_no_minting_api():
    c=GovernedFilesystemEffectContext({}); assert c.authority_minting is False; assert not ({"issue","mint","claim","reserve","lease","authorize"} & set(dir(c)))
