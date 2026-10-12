from pathlib import Path
import tempfile
from acee6_k0_support import run_orchestrator

def main():
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp)
        (root/'ontology').mkdir()
        (root/'ontology'/'acee_installation_executor.py').write_text('class AceeInstallationExecutor:\n    def __init__(self, root=None): self.root=root\n    def step(self, inputs=None, persist=False): return {}\n', encoding='utf-8')
        dry=run_orchestrator(root=root,persist=False)
        assert dry['dry_run'] is True
        assert dry['persistence_performed'] is False
        assert not (root/'acee6_k_evidence').exists()
        assert dry['verification']['valid'] is True, dry
        persisted=run_orchestrator(root=root,persist=True)
        assert persisted['persistence_performed'] is True
        assert Path(persisted['report_path']).is_file()
    print('ACEE6_K0_ORCHESTRATOR_OK')
if __name__=='__main__': main()
