from conftest import solve


def test_step_order_and_double_submission(client,case,app):
    late=client.post('/api/case/step',json=dict(case_id=case['id'],step_index=1,value='33.80'))
    assert late.status_code==409
    body=dict(case_id=case['id'],step_index=0,value='110',submission_id='one')
    first=client.post('/api/case/step',json=body).get_json()
    before=client.get('/api/pupil/pupil-a/state').get_json()
    assert client.post('/api/case/step',json=body).get_json()==first
    assert client.post('/api/case/step',json={**body,'value':'1','submission_id':'another'}).get_json()==first
    assert client.get('/api/pupil/pupil-a/state').get_json()==before


def test_repeated_next_resumes(client,case):
    before=client.get('/api/events').get_json()
    assert client.post('/api/case/next',json={}).get_json()['case']['id']==case['id']
    assert client.get('/api/events').get_json()==before


def test_hidden_answers_not_sent(client,case):
    assert all('expected' not in s and 'trap' not in s and 'solution' not in s for s in case['steps'])
    assert '110.00' not in str(case)
    why=client.get('/api/case/'+case['id']+'/why').get_json()
    assert '110.00' not in str(why)


def test_wrong_pupil_cannot_submit(client,case):
    client.post('/api/session/start',json=dict(pupil_id='pupil-b'))
    assert client.post('/api/case/step',json=dict(case_id=case['id'],step_index=0,value='110')).status_code==404


def test_unknown_pupil_and_invalid_inputs(client,case):
    assert client.get('/api/pupil/unknown/state').status_code==404
    assert client.post('/api/session/start',json=dict(pupil_id='unknown')).status_code==404
    for index in [True,'0',-1,999]:
        assert client.post('/api/case/step',json=dict(case_id=case['id'],step_index=index,value='1')).status_code==400
    assert client.post('/api/case/hint',json=dict(case_id=case['id'],step_index=1,level=3)).status_code==409
    assert client.post('/api/case/hint',json=dict(case_id=case['id'],step_index=0,level=4)).status_code==400
    assert client.get('/api/events?since=no').status_code==400


def test_routes_and_teacher_report(client):
    for path in ['/','/play','/teacher','/api/pupils','/api/teacher/state']:
        assert client.get(path).status_code==200
    report=client.post('/api/teacher/report',json=dict(pupil_id='pupil-a')).get_json()
    assert len(report['sections'])==3
    assert report['pupil_id']=='pupil-a'


def test_session_restart_preserves_issue_deadline(client,case,app):
    client.post('/api/case/step',json=dict(case_id=case['id'],step_index=0,value='1'))
    solve(client,case,app)
    restarted=client.post('/api/session/start',json=dict(pupil_id='pupil-a')).get_json()
    assert restarted['session']['completed']==1
    assert restarted['state']['open_issues'][0]['due_after']==2
