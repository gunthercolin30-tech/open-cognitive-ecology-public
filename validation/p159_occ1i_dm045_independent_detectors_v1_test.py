from pathlib import Path
import ast, hashlib, importlib.util, shutil, sys, tempfile

ROOT=Path.home()/"open-cognitive-ecology"
VER=ROOT/"ontology/occ_independent_constitutional_verifier.py"
EXPECTED_VER="dfd4aa673abb58a08d9970a9d320f5efee7d4409173f985a1f1cce1af87f90f0"

def _source():
    return VER.read_text(encoding="utf-8")

def test_dm045_detector_1_ast_fail_closed_aggregation():
    tree=ast.parse(_source())
    found=False
    for node in ast.walk(tree):
        if isinstance(node,ast.If) and ast.unparse(node.test)=="inconclusive":
            body=ast.unparse(ast.Module(body=node.body,type_ignores=[]))
            if "INDETERMINATE" in body and "VERIFIED" not in body:
                found=True
    assert found, "DM045_AST_FAIL_CLOSED_AGGREGATION_MISSING"

def test_dm045_detector_2_behavioral_inconclusive_injection():
    src=_source()
    anchor='add("IVI-9", "PASS", "verdict aggregation is fail-closed: any inconclusive check blocks VERIFIED")'
    replacement='add("IVI-9", "INCONCLUSIVE", "controlled defensive fixture: aggregation must remain fail-closed")'
    assert src.count(anchor)==1

    with tempfile.TemporaryDirectory(prefix="oce_dm045_detector_v2_") as td:
        ws=Path(td)
        # Preserve relative paths expected by P159 verifier while using the
        # canonical P159 evidence set as immutable fixture input.
        shutil.copytree(ROOT/"ontology",ws/"ontology",
                        ignore=shutil.ignore_patterns("__pycache__","*.pyc","*.bak*"))
        shutil.copytree(ROOT/"validation_artifacts"/"p159",ws/"validation_artifacts"/"p159",
                        ignore=shutil.ignore_patterns("__pycache__","*.pyc","*.bak*"))
        for d in ("normative","constitutional","governance"):
            if (ROOT/d).is_dir():
                shutil.copytree(ROOT/d,ws/d,
                                ignore=shutil.ignore_patterns("__pycache__","*.pyc","*.bak*"))

        vp=ws/"ontology/occ_independent_constitutional_verifier.py"
        vp.write_text(vp.read_text(encoding="utf-8").replace(anchor,replacement,1),encoding="utf-8")

        # Load the isolated verifier while making all workspace modules resolve
        # against the workspace, never against canonical Python module objects.
        saved={k:v for k,v in sys.modules.items() if k=="ontology" or k.startswith("ontology.")}
        for k in list(saved): sys.modules.pop(k,None)
        sys.path.insert(0,str(ws))
        try:
            spec=importlib.util.spec_from_file_location("dm045_fixture_verifier_v2",vp)
            mod=importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            result=mod.verify(ws)
        finally:
            sys.path.pop(0)
            for k in list(sys.modules):
                if k=="dm045_fixture_verifier_v2" or k=="ontology" or k.startswith("ontology."):
                    sys.modules.pop(k,None)
            sys.modules.update(saved)

        # INPUTS must no longer be the reason the fixture is inconclusive.
        assert "INPUTS" not in result.get("inconclusive_check_ids",[]), result
        assert "IVI-9" in result.get("inconclusive_check_ids",[]), result
        assert result["checks_inconclusive"]>=1
        assert result["verdict"]=="INDETERMINATE", result
        assert result["verdict"]!="VERIFIED"

def test_dm045_canonical_verifier_unchanged():
    assert hashlib.sha256(VER.read_bytes()).hexdigest()==EXPECTED_VER
