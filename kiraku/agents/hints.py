def hint(step, level, logger):
    key=['approach','method','worked'][level-1]
    text=step['solution'][key]
    logger.action('Hint',f'Level {level}; {step["label"]}',text,dict(level=level))
    return dict(level=level,text=text,reveals_answer=level==3)
