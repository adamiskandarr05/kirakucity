import pytest
from kiraku.app import create_app


@pytest.fixture
def app(tmp_path,monkeypatch):
    monkeypatch.delenv('GEMINI_API_KEY',raising=False)
    return create_app(dict(TESTING=True,DATABASE=tmp_path/'test.sqlite',SECRET_KEY='tests-only'))


@pytest.fixture
def client(app):
    c=app.test_client()
    c.post('/api/session/start',json=dict(pupil_id='pupil-a'))
    return c


@pytest.fixture
def case(client):
    return client.post('/api/case/next',json={}).get_json()['case']


def solve(client,case,app):
    store=app.extensions['state']
    with store.transaction() as db: raw=store.case(db,case['id'])
    from kiraku.cases.templates import display
    for i,s in enumerate(raw['data']['steps']):
        response=client.post('/api/case/step',json=dict(case_id=case['id'],step_index=i,value=display(s['expected'])))
        assert response.status_code==200 and response.get_json()['correct']
    return client.post('/api/case/finish',json=dict(case_id=case['id']))
