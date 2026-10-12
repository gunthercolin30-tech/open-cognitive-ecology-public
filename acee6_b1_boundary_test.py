import ast
from pathlib import Path

path=Path(__file__).parent/"ontology"/"acee_installation_executor.py"
tree=ast.parse(path.read_text(encoding="utf-8"))
forbidden=("subprocess","py_compile","compileall","shutil","fcntl")
imports=set()
for node in ast.walk(tree):
    if isinstance(node,ast.Import):
        imports.update(alias.name.split(".")[0] for alias in node.names)
    elif isinstance(node,ast.ImportFrom) and node.module:
        imports.add(node.module.split(".")[0])
assert not imports.intersection(forbidden), imports
source=path.read_text(encoding="utf-8")
for token in ("os.replace","write_text(","write_bytes(","mkdir(","unlink(","AceeRollbackEngine","AceeValidationRunner"):
    assert token not in source, token
print("ACEE6_B1_BOUNDARY_OK")
