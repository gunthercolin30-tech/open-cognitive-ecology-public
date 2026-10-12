import inspect,pytest
from unittest.mock import patch
import ontology.governed_fly_cli_transport as gt
from ontology.fly_cli_exact_command_contract import *
from ontology.real_cloud_node_deployment_validator import RealCloudNodeDeploymentValidator
def test_target_no_direct_process():
 s=inspect.getsource(__import__("ontology.real_cloud_node_deployment_validator",fromlist=["x"]))
 assert "subprocess.run(" not in s and "import subprocess" not in s
def test_transport_closed_shape():
 s=inspect.getsource(gt)
 assert "compile_fly_argv(spec)" in s and "shell=False" in s and "start_new_session=True" in s and "close_fds=True" in s
 assert "os.environ.copy()" not in s
def test_exact_operation():
 cp=type("CP",(),{"returncode":0,"stdout":"ok","stderr":""})()
 with patch("ontology.governed_fly_cli_transport.subprocess.run",return_value=cp) as run:
  x=gt.run_fly_operation(FlyCommandSpec(OP_STATUS,"oce-node-1"),30)
 assert x["success"] is True and run.call_args.args[0]==["fly","status","--app","oce-node-1"]
 assert run.call_args.kwargs["shell"] is False
def test_unknown_never_reaches_process():
 with patch("ontology.governed_fly_cli_transport.subprocess.run") as run:
  with pytest.raises(PermissionError): gt.run_fly_operation(FlyCommandSpec("FLY_DEPLOY","oce"),30)
 run.assert_not_called()
@pytest.mark.parametrize("timeout",[0,121,-1,True,1.5])
def test_timeout(timeout):
 with patch("ontology.governed_fly_cli_transport.subprocess.run") as run:
  with pytest.raises((TypeError,ValueError)): gt.run_fly_operation(FlyCommandSpec(OP_APPS_LIST),timeout)
 run.assert_not_called()
def test_validator_bridge():
 v=RealCloudNodeDeploymentValidator()
 with patch("ontology.real_cloud_node_deployment_validator.run_fly_operation",return_value={"success":True}) as f:
  x=v._run_fly(OP_AUTH_WHOAMI,30)
 assert x["success"] is True and isinstance(f.call_args.args[0],FlyCommandSpec)
