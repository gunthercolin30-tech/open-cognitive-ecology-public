import hashlib, tempfile
from pathlib import Path
from ontology.acee_installation_executor import AceeInstallationExecutor

def tree_hash(root):
    h=hashlib.sha256()
    for p in sorted(root.rglob("*"),key=lambda x:str(x)):
        if p.is_file(): h.update(str(p.relative_to(root)).encode()); h.update(p.read_bytes())
    return h.hexdigest()
with tempfile.TemporaryDirectory() as temp:
    root=Path(temp); (root/"ontology").mkdir(); (root/"ontology"/"sentinel.txt").write_text("stable",encoding="utf-8")
    before=tree_hash(root)
    result=AceeInstallationExecutor(root=root).step(inputs={"admission_context":{"requested_stage":"ACEE6-B1"}},persist=False)
    assert isinstance(result,dict); assert tree_hash(root)==before
print("ACEE6_K1_PERSIST_FALSE_IMMUTABILITY_OK")
