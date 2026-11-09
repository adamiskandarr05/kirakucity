from kiraku.agents.quest import choose
from kiraku.agents.logger import Logger


def test_due_issue_first(app):
    s=app.extensions['state']
    with s.transaction() as db:
        p=s.pupil(db,'pupil-a');log=Logger(s,db,p['id'])
        assert choose(p,[],0,log).id=='kedai_bunga_melur'
        issue=dict(id=1,template_id='taman_kiraku',due_after=2,reason='Perimeter misconception')
        assert choose(p,[issue],2,log).id=='taman_kiraku'


def test_level_streaks(app):
    s=app.extensions['state']
    with s.transaction() as db:
        assert s.pupil(db,'pupil-a')['level']==3
        for _ in range(3): s.record_skill(db,'pupil-a','ratio_percent',True)
        assert s.pupil(db,'pupil-a')['level']==4
        for _ in range(2): s.record_skill(db,'pupil-a','ratio_percent',False)
        assert s.pupil(db,'pupil-a')['level']==3


def test_deterministic(app):
    s=app.extensions['state']
    with s.transaction() as db:
        p=s.pupil(db,'pupil-a');log=Logger(s,db,p['id'])
        assert choose(p,[],0,log)==choose(p,[],0,log)
