from kiraku.cases.templates import TEMPLATES


def test_demo_history_is_checked_and_repeatable(client,app):
    response=client.post('/api/demo/prepare',json={})
    assert response.status_code==200
    assert response.json['completed']==8 and response.json['created']==8
    store=app.extensions['state']
    with store.transaction() as db:
        snapshot=store.snapshot(db,'pupil-a')
        assert snapshot['completed_cases']==8
        funded=[p for p in snapshot['town'] if p['funded_case_id']]
        assert len(funded)>=4
        for p in funded:
            c=store.case(db,p['funded_case_id'])
            assert c['status']=='finished' and c['result']['effect']['plot_id']==p['id']
            assert len({a['step_index'] for a in c['attempts'] if a['correct']})==len(c['data']['steps'])
        before=store.events(db,'pupil-a',limit=1000)
        assert any(e['agent']=='Feedback' and not e['raw']['correct'] for e in before)
        assert any(e['agent']=='Quest' and e['raw'].get('issue_id') for e in before)
    assert client.post('/api/demo/prepare',json={}).json['created']==0
    with store.transaction() as db:assert store.events(db,'pupil-a',limit=1000)==before


def test_switch_language_keeps_saved_case_and_evidence(client,app):
    en={'X-Kiraku-Language':'en'};ms={'X-Kiraku-Language':'ms'}
    a=client.post('/api/case/next',json={},headers=en).json['case']
    b=client.post('/api/case/next',json={},headers=ms).json['case']
    assert a['id']==b['id']
    assert a['title']=='The flower shop' and b['title']=='Kedai Bunga Melur'
    assert a['steps'][0]['label']=='Original price' and b['steps'][0]['label']=='Harga asal'
    assert 'A flower shop' in a['brief'] and 'A flower shop' not in b['brief']
    assert ' / ' not in a['brief']+b['brief']+str(a['given_rows'])+str(b['given_rows'])
    assert all('expected' not in s and 'solution' not in s for s in b['steps'])
    for headers in [en,ms]:
        rows=client.get('/api/events',headers=headers).json['events'];store=app.extensions['state']
        with store.transaction() as db:saved=store.events(db,'pupil-a')
        assert [{k:e[k] for k in saved[0]} for e in rows]==saved
        assert all(e['display_agent'] and e['avatar_text'] for e in rows)


def test_malay_feedback_and_hint_preserve_verifier(client,case):
    ms={'X-Kiraku-Language':'ms'};body={'case_id':case['id'],'step_index':0}
    r=client.post('/api/case/step',json={**body,'value':'108'},headers=ms).json
    assert r['correct'] is False and r['message']=='Belum tepat. Peratus berturutan'
    hint=client.post('/api/case/hint',json={**body,'level':1},headers=ms).json
    assert hint['text'].startswith('Batalkan diskaun') and not any(c.isdigit() for c in hint['text'])
    r=client.post('/api/case/step',json={**body,'value':'110'},headers=ms).json
    assert r['correct'] and r['message'].startswith('Disahkan.')


def test_every_template_has_two_complete_presentations(app):
    import random
    from kiraku.app import public_case
    from kiraku.i18n import case_view
    for template in TEMPLATES.values():
        data=template.generate(random.Random(2),True)
        data.update(name='Demo',street='Jalan Demo')
        c=dict(data=data,id='test',status='active',plot_id=1,result=None,attempts=[])
        for lang in ['en','ms']:
            with app.test_request_context(headers={'X-Kiraku-Language':lang}):
                view=case_view(public_case(c))
                assert ' / ' not in view['brief']+view['rounding']+''.join(s['label'] for s in view['steps'])
                assert len(view['brief'])>100


def test_setting_language_cookie_applies_to_all_pages(client):
    client.set_cookie('kiraku-language','ms')
    for url in ['/','/play','/teacher']:
        html=client.get(url).text
        assert '<html lang="ms"' in html and '>Tetapan</h2>' in html
        assert '>Bahasa</legend>' in html
    client.set_cookie('kiraku-language','en')
    assert '>Settings</h2>' in client.get('/play').text
