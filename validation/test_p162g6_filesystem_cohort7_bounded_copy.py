from pathlib import Path
import ast, importlib
MODULES=["ontology.occ1h_h7_a075_common_tcb_resolution_probe","ontology.occ1h_h7_a075_defensive_identity_drift_discrimination","ontology.occ1h_h7_a075_independent_anchor_rebinding_probe","ontology.occ1h_h7_a075_relocatable_historical_control","ontology.occ1h_h7_a075_strict_relocatable_preclose_control"]
def test_copy_survivors_zero_and_context_explicit():
    for name in MODULES:
        m=importlib.import_module(name); text=Path(m.__file__).read_text(encoding="utf-8"); tree=ast.parse(text); bad=[]
        for n in ast.walk(tree):
            if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and isinstance(n.func.value,ast.Name):
                if n.func.value.id=="shutil" and n.func.attr in {"copy","copy2","copyfile","copytree"}: bad.append((n.lineno,n.func.attr))
        assert bad==[],(name,bad)
        assert "BoundedFilesystemValidationContext" in text
        assert "filesystem_context.copy2_from" in text
        assert "filesystem_context.remove_tree()" in text
