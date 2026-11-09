from fractions import Fraction as F
from ..cases.templates import TEMPLATES


def choose(pupil, issues, completed, logger, requested=None):
    if requested:
        template=TEMPLATES[requested['template_id']]
        logger.action('Quest',f"{pupil['id']}; requested building {requested['id']}",
                      f"The pupil chose to improve {requested['name']} from level {requested['level']}.",
                      dict(requested_plot_id=requested['id'],level=requested['level'],completed=completed))
        return template
    due=[i for i in issues if i['due_after']<=completed]
    if due:
        issue=min(due,key=lambda i:(i['due_after'],i['id']))
        template=TEMPLATES[issue['template_id']]
        reason=f"Revisit an open issue after two completed cases: {issue['reason']}."
        raw=dict(issue_id=issue['id'],due_after=issue['due_after'],completed=completed)
    else:
        # Small deterministic exploration bonus for less-practised topics.
        scores={m['topic']:F(100-m['score'])+F(4,1+m['attempts']) for m in pupil['mastery']}
        # While an issue is cooling down, practise a different topic.
        cooling={i['template_id'] for i in issues if i['due_after']>completed}
        pool=[t for t in TEMPLATES.values() if t.id not in cooling] or list(TEMPLATES.values())
        template=max(pool,key=lambda t:(scores[t.topic],-abs(t.level-pupil['level']),t.id))
        m=next(m for m in pupil['mastery'] if m['topic']==template.topic)
        reason=f"{m['title_en']} needs practice ({m['score']}% mastery). Added a small exploration bonus for less-practised topics; current level {pupil['level']}."
        raw=dict(scores={k:str(v) for k,v in scores.items()},level=pupil['level'],completed=completed,cooling=sorted(cooling))
    logger.action('Quest',f"{pupil['id']}; {completed} cases completed",reason,raw)
    return template
