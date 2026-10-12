import ast, os
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"ontology/autonomous_external_collaboration_runner.py"
def runner(tmp_path):
 from ontology.autonomous_external_collaboration_runner import AutonomousExternalCollaborationRunner
 return AutonomousExternalCollaborationRunner(root=tmp_path)
def test_no_direct_process():
 t=P.read_text(); ast.parse(t); assert "import subprocess" not in t and "subprocess.run(" not in t and "command.split()" not in t
def test_payload_command_blocked(tmp_path):
 with patch.dict(os.environ,{"OCE_EXTERNAL_COLLABORATION_RESPONSE":"","OCE_EXTERNAL_COLLABORATION_COMMAND":""},clear=False):
  x=runner(tmp_path)._execute_provider("p","q","autonomous_local_adapter",{"command":"python -c pass"})
 assert x["success"] is False and x["adapter_mode"]=="legacy_process_adapter_blocked"
def test_env_command_blocked(tmp_path):
 with patch.dict(os.environ,{"OCE_EXTERNAL_COLLABORATION_COMMAND":"/bin/echo unsafe","OCE_EXTERNAL_COLLABORATION_RESPONSE":""},clear=False):
  x=runner(tmp_path)._execute_provider("p","q","autonomous_local_adapter",{})
 assert x["success"] is False and x["failure_reason"]=="arbitrary_external_collaboration_command_space_closed"
def test_environment_response_preserved(tmp_path):
 with patch.dict(os.environ,{"OCE_EXTERNAL_COLLABORATION_COMMAND":"/bin/echo unsafe","OCE_EXTERNAL_COLLABORATION_RESPONSE":"bounded response"},clear=False):
  x=runner(tmp_path)._execute_provider("p","q","autonomous_local_adapter",{})
 assert x["success"] is True and x["adapter_mode"]=="environment_response_adapter" and x["response_text"]=="bounded response"
def test_file_response_preserved(tmp_path):
 f=tmp_path/"r.txt"; f.write_text("file response")
 x=runner(tmp_path)._execute_provider("p","q","autonomous_local_adapter",{"response_file":str(f)})
 assert x["success"] is True and x["adapter_mode"]=="file_adapter"
def test_local_synthetic_preserved(tmp_path):
 with patch.dict(os.environ,{"OCE_EXTERNAL_COLLABORATION_RESPONSE":"","OCE_EXTERNAL_COLLABORATION_COMMAND":""},clear=False):
  x=runner(tmp_path)._execute_provider("p","q","autonomous_local_adapter",{"unique_token":"C10E1"})
 assert x["success"] is True and x["adapter_mode"]=="local_safe_synthetic_adapter" and "C10E1" in x["response_text"]
