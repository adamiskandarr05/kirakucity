import random
from .verifier import verify_case


def make_problem(template, seed, logger, default=False):
    rng=random.Random(seed)
    case=None
    for attempt in range(3):
        candidate=template.generate(rng,default=default)
        result=verify_case(candidate)
        logger.action('Verifier',f'{template.id}; attempt {attempt+1}',
                      'All exact values and step relationships verified.' if result['ok'] else 'Rejected generator: '+ '; '.join(result['reasons']),result)
        if result['ok']:
            case=candidate;break
    if case is None:
        case=template.generate(random.Random(0),default=True)
        result=verify_case(case)
        logger.action('Verifier','Fixed default fallback','Verified default case.' if result['ok'] else 'Default invalid.',result)
        if not result['ok']: raise ValueError('Default case failed verification')
    logger.action('Problem',f"{template.id}; seed {seed}",f"Computed {len(case['steps'])} answers and misconception values using exact fractions.",dict(seed=seed,template_id=template.id,rounding=case['rounding']))
    return case
