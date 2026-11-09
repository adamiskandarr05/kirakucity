import random
import pytest
from kiraku.cases.templates import TEMPLATES
from kiraku.agents.outcome import evaluate


class Log:
    def action(self,*args):pass


@pytest.mark.parametrize('template',TEMPLATES.values(),ids=TEMPLATES)
def test_correct_vs_wrong_final(template):
    case=dict(data=template.generate(random.Random(0),default=True),plot_id=7)
    case['data']['name']='Fictional plan'
    good=evaluate(case,True,Log());bad=evaluate(case,False,Log())
    assert good['branch']!=bad['branch']
    assert bad['effect'] is None


def test_park_shortfall_holds():
    data=TEMPLATES['taman_kiraku'].generate(random.Random(0),default=True);data['name']='Taman Kiraku'
    assert evaluate(dict(data=data,plot_id=1),True,Log())['branch']=='held'
