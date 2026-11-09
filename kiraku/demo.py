"""Prepare fictional demo history through the same checked API as the game."""
from threading import Lock
from .cases.templates import display

_lock=Lock()


def prepare(app, target=8):
    with _lock, app.test_client() as client:
        def post(path, body):
            response=client.post(path,json=body)
            if response.status_code!=200:raise ValueError('Demo preparation could not complete. Saved progress is safe.')
            return response.get_json()
        post('/api/session/start',{'pupil_id':'pupil-a'})
        snapshot=client.get('/api/pupil/pupil-a/state').get_json()
        completed=snapshot['completed_cases'];created=0
        while completed<target:
            public=post('/api/case/next',{})['case'];cid=public['id']
            store=app.extensions['state']
            with store.transaction() as db:case=store.case(db,cid)
            accepted={a['step_index'] for a in case['attempts'] if a['correct']}
            if completed==0 and not case['attempts']:
                post('/api/case/step',{'case_id':cid,'step_index':0,'value':display(case['data']['steps'][0]['trap']),'submission_id':'demo-first-try'})
                post('/api/case/hint',{'case_id':cid,'step_index':0,'level':1})
            for i,step in enumerate(case['data']['steps']):
                if i in accepted:continue
                post('/api/case/step',{'case_id':cid,'step_index':i,'value':display(step['expected']),'submission_id':f'demo-verified-{i}'})
            post('/api/case/finish',{'case_id':cid});completed+=1;created+=1
        if created:post('/api/teacher/report',{'pupil_id':'pupil-a'})
        return dict(pupil_id='pupil-a',completed=completed,created=created,fictional=True)
