from conftest import solve


def test_town_changes_only_after_correct_outcome(client,case,app):
    initial=client.get('/api/pupil/pupil-a/state').get_json()
    assert client.post('/api/case/finish',json=dict(case_id=case['id'])).status_code==409
    client.post('/api/case/step',json=dict(case_id=case['id'],step_index=0,value='-1'))
    wrong=client.get('/api/pupil/pupil-a/state').get_json()
    assert wrong['counts']==initial['counts']
    assert [(p['status'],p['level']) for p in wrong['town']]==[(p['status'],p['level']) for p in initial['town']]
    finish=solve(client,case,app)
    assert finish.status_code==200 and finish.get_json()['effect']['kind']=='shops'
    built=client.get('/api/pupil/pupil-a/state').get_json()
    assert built['counts']['shops']==initial['counts']['shops']+1
    assert client.post('/api/case/finish',json=dict(case_id=case['id'])).get_json()==finish.get_json()
    assert client.get('/api/pupil/pupil-a/state').get_json()['counts']==built['counts']


def test_issue_returns_after_two_cases(client,case,app):
    client.post('/api/case/step',json=dict(case_id=case['id'],step_index=0,value='1'))
    solve(client,case,app)
    second=client.post('/api/case/next',json={}).get_json()['case']
    assert second['template_id']!=case['template_id']
    solve(client,second,app)
    third=client.post('/api/case/next',json={}).get_json()['case']
    assert third['template_id']==case['template_id']
    solve(client,third,app)
    assert client.get('/api/pupil/pupil-a/state').get_json()['open_issues']==[]
