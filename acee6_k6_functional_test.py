from acee6_k6_longitudinal_runner import run_reduced
o=run_reduced(False);assert o['verification']['valid'],o['verification'];r=o['report'];assert r['transaction_count']==20;assert r['segment_count']==2;assert r['committed_count']==10;print('ACEE6_K6_FUNCTIONAL_OK')
