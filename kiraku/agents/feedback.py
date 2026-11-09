from .verifier import verify_answer


def check(state, db, case, index, value, completed, logger):
    step=case['data']['steps'][index]
    verified=verify_answer(step,value)
    correct=verified['ok']
    mistake=step['mistake'] if verified['trap'] else None
    message='Disahkan / Verified. '+step['solution']['worked'] if correct else (
        'Ditolak / Rejected. '+mistake if mistake else 'Belum tepat / Not yet. Check the operation and try again.')
    if verified['value'] is None: message=verified['reasons'][0]
    result=dict(correct=correct,step_index=index,message=message,trap=mistake,value=verified['value'])
    if correct: result['solution']=step['solution']['worked']
    state.record_skill(db,case['pupil_id'],case['data']['topic'],correct)
    if not correct:
        state.add_issue(db,case,index,mistake or 'Revisit '+step['label'],completed)
    logger.action('Feedback',f"Step {index+1}; submitted {str(value)[:40]}",message,
                  dict(step_index=index,submitted=str(value)[:40],correct=correct,trap=mistake))
    return result
