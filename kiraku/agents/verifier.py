from collections import Counter
from fractions import Fraction as F
import re
from ..cases.templates import TEMPLATES, rounded


def verify_case(case):
    reasons=[]
    try:
        template=TEMPLATES[case['template_id']]
        expected=template.solve(case)
        if not case.get('rounding') or '2 decimal' not in case['rounding']:
            reasons.append('Rounding must state two decimal places.')
        for key,value in case['givens'].items():
            numbers=value if isinstance(value,list) else [value]
            if any(F(v)<=0 for v in numbers): reasons.append(f'{key} must be positive.')
            if key in ['P','Q'] and template.kind=='shops' and not 0<=F(value)<=100:
                reasons.append('Percentage outside valid range.')
        if len(case['steps'])!=len(expected): reasons.append('Step count differs.')
        for actual,solution in zip(case['steps'],expected):
            answer=F(actual['expected']);trap=F(actual['trap'])
            if answer<0: reasons.append('Negative answer.')
            if answer!=F(solution['expected']): reasons.append('Inconsistent step value.')
            if trap!=F(solution['trap']): reasons.append('Inconsistent trap value.')
            if rounded(answer)==rounded(trap): reasons.append('Trap and answer are not distinct at display precision.')
            if actual.get('places')!=2: reasons.append('Step rounding differs from brief.')
        if template.kind=='stalls':
            known=[F(x) for x in case['givens']['known']]
            if len(known)!=4: reasons.append('Four known sales required.')
            missing=F(expected[1]['expected']);counts=Counter(known+[missing])
            if missing in known: reasons.append('Missing sales must differ from known sales.')
            if sum(v==max(counts.values()) for v in counts.values())!=1:
                reasons.append('Mode is not unique.')
    except (ValueError,KeyError,TypeError,ZeroDivisionError,OverflowError):
        reasons.append('Invalid case structure or arithmetic.')
    return dict(ok=not reasons,reasons=reasons)


def verify_answer(step, value):
    try:
        s=str(value)
        if not re.fullmatch(r'\+?\d{1,12}(?:\.\d{1,8})?',s): raise ValueError()
        value=F(s)
        if value<0 or value>10**9: raise ValueError()
        # Answers are compared to the explicitly stated rounded value, not a tolerance band.
        correct=value==rounded(step['expected'],step['places'])
        trap=value==rounded(step['trap'],step['places'])
        return dict(ok=correct,reasons=[] if correct else ['Answer does not match the verified rounded result.'],trap=trap,value=str(value))
    except (ValueError,ZeroDivisionError,OverflowError):
        return dict(ok=False,reasons=['Enter a finite, non-negative decimal number.'],trap=False,value=None)
