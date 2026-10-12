from acee6_k7_longitudinal_runner import run_reduced
out=run_reduced(False);report=out['report'];assert out['verification']['valid'],out
raw=[report['campaigns'][name]['raw_hashes'] for name in ('A','B','C')]
normalized=[report['campaigns'][name]['normalized_hashes'] for name in ('A','B','C')]
assert normalized[0]==normalized[1]==normalized[2],normalized
assert all(set(item)=={'transaction_chain_hash','segment_chain_hash','campaign_hash','report_hash'} for item in raw),raw
assert report['public_schema_version']=='1.1.0'
print('ACEE6_K7_HASH_VIEWS_OK')
