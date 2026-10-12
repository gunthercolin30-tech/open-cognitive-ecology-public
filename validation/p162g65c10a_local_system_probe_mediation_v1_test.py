from pathlib import Path
import pytest
ROOT = Path(__file__).resolve().parents[1]
FILES = [
    "autonomous_hardware_health_monitor.py",
    "civilizational_runtime_governance_console.py",
    "embodied_world_interface.py",
    "physical_infrastructure_registry.py",
]

def test_no_standard_subprocess_in_migrated_modules():
    for name in FILES:
        text = (ROOT / "ontology" / name).read_text()
        assert "import subprocess" not in text
        assert "subprocess.run" not in text

def test_unregistered_command_rejected():
    from ontology.governed_local_system_probe import run_local_system_probe
    with pytest.raises(PermissionError):
        run_local_system_probe("sh", "-c", "id")

def test_unregistered_args_rejected():
    from ontology.governed_local_system_probe import run_local_system_probe
    with pytest.raises(PermissionError):
        run_local_system_probe("launchctl", "unload", "x")

def test_timeout_expansion_rejected():
    from ontology.governed_local_system_probe import run_local_system_probe
    with pytest.raises(PermissionError):
        run_local_system_probe("launchctl", "list", timeout_seconds=11)

def test_read_only_no_descendants_contract():
    text = (ROOT / "ontology" / "governed_local_system_probe.py").read_text()
    assert '"READ_ONLY_OBSERVATION"' in text
    assert '"NO_DESCENDANTS"' in text

def test_backups_exist():
    for name in FILES:
        assert (ROOT / "ontology" / (name + ".bak.p162g65c10a")).is_file()
