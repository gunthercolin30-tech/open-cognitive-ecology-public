from __future__ import annotations
import json
from pathlib import Path
from acee6_k8_certification_support import REPORT_PATH,BUNDLE_PATH,MANIFEST_PATH,file_sha
from acee6_k8_global_certifier import verify_bundle,verify_report
def verify_persisted()->dict:
 reasons=[]
 if not REPORT_PATH.is_file():reasons.append('missing_report')
 if not MANIFEST_PATH.is_file():reasons.append('missing_manifest')
 if not BUNDLE_PATH.is_file():reasons.append('missing_bundle')
 if reasons:return {'valid':False,'reasons':reasons}
 report=json.loads(REPORT_PATH.read_text(encoding='utf-8'))
 rv=verify_report(report);bv=verify_bundle(BUNDLE_PATH)
 reasons.extend(rv['reasons']);reasons.extend(bv['reasons'])
 return {'valid':not reasons,'reasons':reasons,'report':rv,'bundle':bv}
