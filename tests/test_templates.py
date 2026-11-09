import random
from fractions import Fraction as F
import pytest
from kiraku.cases.templates import TEMPLATES,display
from kiraku.agents.verifier import verify_case,verify_answer


@pytest.mark.parametrize('template',TEMPLATES.values(),ids=TEMPLATES)
def test_200_seeds(template):
    for seed in range(200):
        case=template.generate(random.Random(seed))
        assert verify_case(case)==dict(ok=True,reasons=[]),(seed,case,verify_case(case))
        for step in case['steps']:
            assert verify_answer(step,display(step['expected']))['ok']
            assert not verify_answer(step,display(step['trap']))['ok']
            assert isinstance(F(step['expected']),F)


def test_fixed_defaults():
    expected={'kedai_bunga_melur':['110','169/5'],'teksi_kiraku':['10','23'],
              'gerai_taman':['241','61','40'],'taman_kiraku':['20','25','1000','100']}
    for name,values in expected.items():
        case=TEMPLATES[name].generate(random.Random(0),default=True)
        assert [s['expected'] for s in case['steps']]==values
