from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'ontology/autonomous_web_navigation_engine.py'
def src(): return P.read_text(encoding='utf-8')
def test_module_compiles_and_marker_present():
    compile(src(),str(P),'exec'); assert 'P162_G63B3_NETWORK_MEDIATED = True' in src()
def test_future_import_precedes_governance_code():
    lines=src().splitlines(); f=[i for i,x in enumerate(lines) if x.startswith('from __future__ import ')]
    m=next(i for i,x in enumerate(lines) if 'P162_G63B3_NETWORK_MEDIATED = True' in x)
    assert not f or max(f)<m
def test_direct_urlopen_removed():
    assert 'urllib.request.urlopen(' not in src(); assert 'direct_urllib_network_bypass_removed' in src()
def test_single_goto_has_guard():
    lines=src().splitlines(); g=[i for i,x in enumerate(lines) if '.goto(' in x and not x.lstrip().startswith('#')]
    assert len(g)==1; assert '_p162_require_playwright_target' in '\n'.join(lines[max(0,g[0]-3):g[0]])
def test_permission_error_reraised_before_broad_exception():
    lines=src().splitlines(); g=next(i for i,x in enumerate(lines) if '.goto(' in x and not x.lstrip().startswith('#'))
    tail='\n'.join(lines[g:g+30]); assert 'except PermissionError:' in tail and 'except Exception' in tail
    assert tail.index('except PermissionError:') < tail.index('except Exception')
def test_sqlite_remains_for_later_database_migration():
    assert 'sqlite3' in src()
