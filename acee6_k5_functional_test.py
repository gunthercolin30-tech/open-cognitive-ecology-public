from acee6_k5_transaction_runner import run
o=run(False);assert o['verification']['valid'],o;assert o['report']['transaction_count']==100;assert o['report']['committed_count']==50;print('ACEE6_K5_FUNCTIONAL_OK')
