import random,re
from fractions import Fraction as F
from kiraku.cases.templates import TEMPLATES,display
from kiraku.agents.hints import hint


class Log:
    def action(self,*args):pass


def test_no_answer_in_first_two_hints():
    for template in TEMPLATES.values():
        for seed in range(200):
            case=template.generate(random.Random(seed))
            for step in case['steps']:
                for level in [1,2]:
                    text=hint(step,level,Log())['text']
                    assert not re.search(r'\d',text)
                    assert display(step['expected']) not in text
                assert hint(step,3,Log())['text']==step['solution']['worked']
