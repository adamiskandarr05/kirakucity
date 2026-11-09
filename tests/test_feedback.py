from kiraku.cases.templates import display


def test_trap_opens_one_issue_and_retries_are_atomic(client,app,case):
    s=app.extensions['state']
    with s.transaction() as db:raw=s.case(db,case['id']);trap=display(raw['data']['steps'][0]['trap'])
    body=dict(case_id=case['id'],step_index=0,value=trap,submission_id='same-click')
    first=client.post('/api/case/step',json=body).get_json()
    assert not first['correct'] and 'Adding successive percentages' in first['trap']
    assert client.post('/api/case/step',json=body).get_json()==first
    client.post('/api/case/step',json={**body,'submission_id':'second-try'})
    snapshot=client.get('/api/pupil/pupil-a/state').get_json()
    assert len(snapshot['open_issues'])==1
    with s.transaction() as db:
        feedback=[e for e in s.events(db,'pupil-a') if e['agent']=='Feedback']
        assert len(feedback)==2
