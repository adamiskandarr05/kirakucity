from ..cases.templates import TEMPLATES


def evaluate(case, all_correct, logger):
    data=case['data'];template=TEMPLATES[data['template_id']]
    funded=all_correct and template.outcome([s['expected'] for s in data['steps']],data)
    branch='built' if funded else ('held' if all_correct else 'rejected')
    if branch=='built':
        ms=f"{data['name']} dibuka. Pengiraan anda menghidupkan bandar."
        en=f"{data['name']} is open. Your verified calculations funded a town improvement."
    elif branch=='held':
        ms='Pengiraan betul. Projek menunggu bajet atau sasaran yang mencukupi.'
        en='Your calculations are correct. The project is waiting for enough budget or a viable target.'
    else:
        ms='Semak semula pengiraan sebelum projek boleh diteruskan.'
        en='Review the calculations before this project can go ahead.'
    effect=dict(kind=data['kind'],amount=1,plot_id=case['plot_id']) if funded else None
    result=dict(branch=branch,outcome_ms=ms,outcome_en=en,effect=effect,all_correct=all_correct)
    logger.action('Outcome',f"{data['template_id']}; all steps verified: {all_correct}",en,dict(branch=branch,effect=effect))
    return result
