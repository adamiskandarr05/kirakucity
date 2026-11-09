from kiraku.app import create_app
from kiraku.state import State
from kiraku.city import CITY
from kiraku.landscape import near_water,on_land
from conftest import solve


def test_landscape_keeps_lots_on_safe_ground(app):
    store=app.extensions['state']
    with store.transaction() as db:state=store.snapshot(db,'pupil-a')
    assert len(state['town'])==118 and state['city_summary']['buildings']==102
    assert len(CITY['landscape']['lake']['outline'])==40
    for p in state['town']:
        assert on_land(p['x'],p['y'],p['footprint']*.75)
        assert not near_water(p['x'],p['y'],p['footprint']*.7+.55)
    for x,y in CITY['landscape']['road_tiles']:assert not near_water(x,y,.65)
    # The old repeated five-house arrangement has been broken up.
    assert len({(p['x'],p['y']) for p in state['town']})==118
    assert len({p['x'] for p in state['town'] if p['kind']=='homes'})>10


def test_targeted_upgrade_changes_design_every_level_once(client,app):
    store=app.extensions['state']
    with store.transaction() as db:
        plot=next(p for p in store.snapshot(db,'pupil-a')['town'] if p['template_id']=='teksi_kiraku' and p['status']=='empty')
    last_height=0;built_name=None
    for level in range(1,6):
        c=client.post('/api/case/next',json={'plot_id':plot['id']}).json['case']
        assert c['plot_id']==plot['id'] and c['progression']['next_level']==level
        assert c['progression']['action']==('build' if level==1 else 'upgrade')
        result=solve(client,c,app).json
        assert result['effect']['level']==level
        replay=client.post('/api/case/finish',json={'case_id':c['id']}).json
        assert replay==result
        with store.transaction() as db:
            snapshot=store.snapshot(db,'pupil-a');now=next(p for p in snapshot['town'] if p['id']==plot['id'])
            saved=store.case(db,c['id']);events=store.events(db,'pupil-a',cid=c['id'])
        assert now['level']==level and now['footprint']==plot['footprint']
        if level==1:built_name=now['name']
        assert now['name']==built_name
        assert snapshot['counts']['stands']==2  # Floors do not invent new buildings.
        assert now['funded_case_id']==c['id'] and saved['result']['effect']==result['effect']
        assert next(e for e in events if e['agent']=='Outcome')['raw']['effect']==result['effect']
        assert next(e for e in events if e['agent']=='Quest')['raw']['requested_plot_id']==plot['id']
        if level>1:
            assert now['appearance']['style']=='kiraku-upgrade' and now['appearance']['height']>last_height
            last_height=now['appearance']['height']


def test_upgrade_cannot_skip_verification_or_change_other_pupil(client,app):
    store=app.extensions['state']
    with store.transaction() as db:
        a=next(p for p in store.snapshot(db,'pupil-a')['town'] if p['template_id']=='teksi_kiraku')
        b=next(p for p in store.snapshot(db,'pupil-b')['town'] if p['template_id']=='teksi_kiraku')
    assert client.post('/api/case/next',json={'plot_id':b['id']}).status_code==404
    assert client.post('/api/case/next',json={'plot_id':True}).status_code==400
    c=client.post('/api/case/next',json={'plot_id':a['id']}).json['case']
    assert client.post('/api/case/finish',json={'case_id':c['id']}).status_code==409
    with store.transaction() as db:assert store.town_plot(db,'pupil-a',a['id'])['level']==a['level']


def test_landscape_migrates_history_without_reset(tmp_path,monkeypatch):
    path=tmp_path/'old-world.sqlite'
    with monkeypatch.context() as patch:
        patch.setattr(State,'migrate_landscape',lambda self,db:None)
        old=create_app(dict(TESTING=True,DATABASE=path,SECRET_KEY='old-world'))
        client=old.test_client();client.post('/api/session/start',json={'pupil_id':'pupil-a'})
        c=client.post('/api/case/next',json={}).json['case']
        client.post('/api/case/step',json={'case_id':c['id'],'step_index':0,'value':'108'})
        solve(client,c,old)
        store=old.extensions['state']
        with store.transaction() as db:
            before=store.case(db,c['id']);history=store.events(db,'pupil-a');issues=store.issues(db,'pupil-a');count=len(store.snapshot(db,'pupil-a')['town'])
    new=State(path)
    with new.transaction() as db:
        snapshot=new.snapshot(db,'pupil-a')
        assert new.case(db,c['id'])==before and new.events(db,'pupil-a')==history and new.issues(db,'pupil-a')==issues
        assert len(snapshot['town'])==count and snapshot['completed_cases']==1
        funded=next(p for p in snapshot['town'] if p['funded_case_id']==c['id'])
        assert (funded['x'],funded['y'])==(17,17)
    again=State(path)
    with again.transaction() as db:assert again.snapshot(db,'pupil-a')==snapshot
