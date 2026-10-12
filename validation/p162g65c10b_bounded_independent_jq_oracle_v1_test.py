from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_target_no_direct_subprocess():
 s=(ROOT/"ontology/occ1h_a070_parser_differential_semantics.py").read_text()
 assert "import subprocess" not in s and "subprocess.run" not in s
def test_oracle_fixed():
 s=(ROOT/"ontology/governed_independent_jq_oracle.py").read_text()
 assert 'ARGV=("-cS",".")' in s and 'TIMEOUT_SECONDS=5.0' in s
 assert 'MAX_STDIN_BYTES=1_048_576' in s and 'shell=False' in s and 'start_new_session=True' in s
def test_oversize_fails_closed():
 from ontology.governed_independent_jq_oracle import jq_canonicalize,MAX_STDIN_BYTES
 assert jq_canonicalize("x"*(MAX_STDIN_BYTES+1))["status"]=="EXECUTION_BLOCKED_AT_FINAL_RECHECK"
def test_semantics():
 from ontology.occ1h_a070_parser_differential_semantics import evaluate_serialized_json
 assert evaluate_serialized_json('{"b":2,"a":1}')["verdict"] in {"ADMISSIBLE_CONTROL","UNRESOLVED"}
 assert evaluate_serialized_json('{"a":')["verdict"] in {"INVALID_INPUT_CONTROL","UNRESOLVED"}
def test_backup():
 assert (ROOT/"ontology/occ1h_a070_parser_differential_semantics.py.bak.p162g65c10b").is_file()
