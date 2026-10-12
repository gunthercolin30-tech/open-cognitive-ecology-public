from copy import deepcopy
from oif.interface.manifest_diff import compare_manifests
from oif2h_test_support import base_mapping
b=base_mapping(); a=deepcopy(b)
a['interface']['title']='Portail pilote révisé'
a['permissions'].append({'permission_id':'audit.read','description':'Lecture des audits'})
a['components'][0]['properties']['text']='Portail fonctionnel révisé'
a['layout'][0]['regions'][0]['component_ids'][0],a['layout'][0]['regions'][0]['component_ids'][1]=a['layout'][0]['regions'][0]['component_ids'][1],a['layout'][0]['regions'][0]['component_ids'][0]
r=compare_manifests(b,a)
assert r.changed
assert r.counts['added']>=1 and r.counts['modified']>=2 and r.counts['moved']>=2, r.as_dict()
assert 'ADDED' in r.human_text() and 'MODIFIED' in r.human_text() and 'MOVED' in r.human_text()
assert r.as_dict()['schema']=='oif.manifest.diff.v1'
print('OIF2H_MANIFEST_DIFF_FUNCTIONAL_OK')
