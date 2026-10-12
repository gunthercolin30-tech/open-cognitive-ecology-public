from pathlib import Path
import tempfile
from acee6_k0_support import build_contract, sha

def main():
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp)
        (root/'ontology').mkdir()
        src='class AceeInstallationExecutor:\n    def step(self, inputs=None, persist=False):\n        return {}\n'
        (root/'ontology'/'acee_installation_executor.py').write_text(src, encoding='utf-8')
        contract=build_contract(root)
        payload=dict(contract); expected=payload.pop('contract_hash')
        assert expected == sha(payload)
        assert contract['heavy_campaigns_default_enabled'] is False
        assert contract['failure_policy']['partial_success_allowed'] is False
        assert contract['retry_policy']['unlimited_retry_allowed'] is False
        assert contract['invariants']['consciousness_proven'] is False
        assert len(contract['campaigns']) == 9
    print('ACEE6_K0_CONTRACT_OK')
if __name__=='__main__': main()
