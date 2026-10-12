from acee6_k7_longitudinal_runner import run_reduced
o=run_reduced(False);assert o['verification']['valid'],o;assert o['report']['comparison']['valid'];print('ACEE6_K7_FUNCTIONAL_OK')
