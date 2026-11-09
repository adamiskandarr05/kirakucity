import random
from kiraku.agents.logger import Logger
from kiraku.agents import problem,scenario,quest,narration,hints,outcome,teacher,feedback
from kiraku.cases.templates import TEMPLATES


def test_each_agent_action_writes_exactly_one(app,client,case):
    s=app.extensions['state']
    with s.transaction() as db:
        raw=s.case(db,case['id']);log=Logger(s,db,'pupil-a',case['id'])
        calls=[lambda:quest.choose(s.pupil(db,'pupil-a'),[],0,log),
               lambda:scenario.fill(raw['data'],0,log),
               lambda:narration.narrate(raw,log),
               lambda:hints.hint(raw['data']['steps'][0],1,log),
               lambda:outcome.evaluate(raw,False,log),
               lambda:teacher.report(s.snapshot(db,'pupil-a'),log),
               lambda:feedback.check(s,db,raw,0,'1',0,log)]
        for call in calls:
            before=len(s.events(db,'pupil-a'));call()
            assert len(s.events(db,'pupil-a'))==before+1
        before=s.events(db,'pupil-a')[0]['id']
        problem.make_problem(TEMPLATES['kedai_bunga_melur'],0,log,default=True)
        assert [e['agent'] for e in s.events(db,'pupil-a',since=before)]==['Problem','Verifier']


def test_every_visible_event_is_saved(client,app,case):
    api=client.get('/api/events?since=0').get_json()['events']
    s=app.extensions['state']
    with s.transaction() as db: assert api==s.events(db,'pupil-a')
    assert 'needs practice' in next(e['decision'] for e in api if e['agent']=='Quest')
    assert len({e['id'] for e in api})==len(api)


def test_generation_retries_three_then_default(app,monkeypatch):
    template=TEMPLATES['kedai_bunga_melur'];real=type(template).generate
    def broken(self,rng,default=False):
        result=real(self,rng,default)
        if not default:result['steps'][0]['expected']='-1'
        return result
    monkeypatch.setattr(type(template),'generate',broken)
    s=app.extensions['state']
    with s.transaction() as db:
        result=problem.make_problem(template,0,Logger(s,db,'pupil-a'))
        assert result['steps'][0]['expected']=='110'
        entries=s.events(db,'pupil-a')
        assert len([e for e in entries if e['agent']=='Verifier'])==4
        assert len([e for e in entries if e['decision'].startswith('Rejected generator')])==3
