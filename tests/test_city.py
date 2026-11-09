import hashlib,json
from pathlib import Path
from kiraku.app import create_app
from kiraku.state import State
from conftest import solve


def test_original_cytopia_sheets_are_unchanged():
    root=Path(__file__).parents[1]/'kiraku/static/assets/cytopia'
    manifest=json.loads((root/'manifest.json').read_text())
    assert manifest['commit']=='c70bbce3ba8b0ba23b8dcce9ff8bc8df0af971f8'
    assert len(manifest['assets'])==31
    for asset in manifest['assets']:
        assert hashlib.sha256((root/asset['file']).read_bytes()).hexdigest()==asset['sha256']
        assert (root/'previews'/(asset['id']+'.png')).is_file()
    assert (root/'LICENSE-GPL-3.0.txt').is_file()


def test_city_lots_match_sprite_footprints_and_do_not_overlap(app):
    s=app.extensions['state']
    with s.transaction() as db:state=s.snapshot(db,'pupil-a')
    root=Path(__file__).parents[1]/'kiraku/static/assets/cytopia'
    art={a['id']:a for a in json.loads((root/'manifest.json').read_text())['assets']}
    assert state['city']['size']==40 and len(state['town'])==118
    assert state['city_summary']==dict(buildings=102,plots=16,districts=4)
    for i,plot in enumerate(state['town']):
        assert plot['asset'] in art
        assert plot['footprint']==art[plot['asset']]['footprint']['width']
        assert 0<=plot['frame']<art[plot['asset']]['tiles']['count']
        for other in state['town'][i+1:]:
            distance=(plot['footprint']+other['footprint'])/2
            assert abs(plot['x']-other['x'])>=distance or abs(plot['y']-other['y'])>=distance


def test_reopen_does_not_duplicate_city(app):
    first=app.extensions['state']
    with first.transaction() as db:before=first.snapshot(db,'pupil-a')
    second=State(first.path)
    with second.transaction() as db:assert second.snapshot(db,'pupil-a')==before


def test_legacy_city_expands_without_losing_funded_case(tmp_path,monkeypatch):
    original=State.migrate_city
    with monkeypatch.context() as patch:
        patch.setattr(State,'migrate_city',lambda self,db:None)
        old=create_app(dict(TESTING=True,DATABASE=tmp_path/'legacy.sqlite',SECRET_KEY='legacy-test'))
        client=old.test_client();client.post('/api/session/start',json=dict(pupil_id='pupil-a'))
        case=client.post('/api/case/next',json={}).get_json()['case']
        assert solve(client,case,old).get_json()['effect']['kind']=='shops'
    migrated=State(tmp_path/'legacy.sqlite')
    with migrated.transaction() as db:
        state=migrated.snapshot(db,'pupil-a');funded=next(p for p in state['town'] if p['funded_case_id']==case['id'])
        assert len(state['town'])==118
        assert funded['x']==17 and funded['y']==17 and funded['status']=='built'
        assert state['counts']['shops']==4
        assert migrated.case(db,case['id'])['result']['branch']=='built'
