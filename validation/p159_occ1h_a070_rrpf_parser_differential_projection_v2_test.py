from pathlib import Path
import importlib.util,json
R=Path(__file__).resolve().parents[1];M=R/"ontology/occ1h_a070_parser_differential_semantics.py";A=R/"validation_artifacts/p159/occ1h/a070/a070_rrpf_parser_differential_projection_v2.json"
def mod():
 s=importlib.util.spec_from_file_location("a070m",M);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def test_agreement_controls():
 m=mod();assert m.evaluate_serialized_json('{"b":2,"a":1}')["verdict"]=="ADMISSIBLE_CONTROL";assert m.evaluate_serialized_json('{"x":[1,true,null]}')["verdict"]=="ADMISSIBLE_CONTROL"
def test_differential_degradation():
 r=mod().evaluate_serialized_json('{"n":NaN}');assert r["verdict"]=="RESISTED";assert r["reason"]=="PARSER_SEMANTIC_DIVERGENCE"
def test_invalid_and_no_authority():
 m=mod();assert m.evaluate_serialized_json('{"a":1,}')["verdict"]=="INVALID_INPUT_CONTROL";assert m.RUNTIME_AUTHORITY_GRANTED is False;assert m.FUNCTIONAL_ONLY is True
def test_artifact_boundaries():
 x=json.loads(A.read_text());assert x["RRP21"]["status"]=="COMPLETE";assert x["RRP21"]["candidate_verdict"]=="RESISTED";assert x["RRP22"]["status"]=="INDEPENDENT_REQUALIFICATION_REQUIRED";assert x["v1_failed_attempt"]["status"]=="FAILED_PRE_ARTIFACT";assert x["boundaries"]=={"occ1h_closed":False,"p159_final_lock":False,"p160_opened":False}
