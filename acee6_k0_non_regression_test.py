from acee6_k0_support import MODULE_PATH, file_sha, run_orchestrator

def main():
    before=file_sha(MODULE_PATH)
    result=run_orchestrator(persist=False)
    after=file_sha(MODULE_PATH)
    assert before == after
    assert result['report']['heavy_campaigns_executed'] is False
    assert result['verification']['valid'] is True
    print('ACEE6_K0_NON_REGRESSION_OK')
if __name__=='__main__': main()
