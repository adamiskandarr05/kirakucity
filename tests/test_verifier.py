import copy,random
import pytest
from kiraku.cases.templates import TEMPLATES,display,rounded
from kiraku.agents.verifier import verify_case,verify_answer


def base(): return TEMPLATES['kedai_bunga_melur'].generate(random.Random(0),default=True)


@pytest.mark.parametrize('value',['-1','nan','inf','NaN','1/0','110.001','1e10000','',None,True])
def test_invalid_and_wrong_values(value):
    assert not verify_answer(base()['steps'][0],value)['ok']


def test_correct_and_trap():
    s=base()['steps'][0]
    assert verify_answer(s,'110.00')['ok']
    result=verify_answer(s,display(s['trap']))
    assert not result['ok'] and result['trap']
    case=base();case['givens'].update(P='100',C='50')
    case['steps']=TEMPLATES[case['template_id']].solve(case)
    assert verify_case(case)['ok']


@pytest.mark.parametrize('change',['wrong','trap','negative','range','rounding','step_rounding'])
def test_case_rejections(change):
    case=base()
    if change=='wrong':case['steps'][0]['expected']='111'
    if change=='trap':case['steps'][0]['trap']=case['steps'][0]['expected']
    if change=='negative':case['givens']['C']='-5'
    if change=='range':case['givens']['P']='101'
    if change=='rounding':case['rounding']=''
    if change=='step_rounding':case['steps'][0]['places']=0
    assert not verify_case(case)['ok']


def test_non_unique_mode():
    case=TEMPLATES['gerai_taman'].generate(random.Random(0),default=True)
    case['givens'].update(known=['40','40','50','50'],M='48')
    assert not verify_case(case)['ok']


def test_round_half_up_exact():
    assert display('1.005')=='1.01'
    assert display('2.675')=='2.68'
    assert display('-1.005')=='-1.01'
