import os
import re


def safe_line(text, seen=(), max_length=360):
    if not isinstance(text,str) or not 1<=len(text)<=max_length: return False
    # Conservative: narrator prose never contains numerals, even previously seen ones.
    return not re.search(r'\d',text) and not re.search(r'https?://|<|>',text)


def narrate(case, logger, review=False):
    text=('Bandar Kiraku is counting on your ideas. Read the givens, then take one step at a time.' if not review
          else 'You checked each calculation before making a town decision. Keep the same care in the next case.')
    source='template'
    if os.getenv('GEMINI_API_KEY'):
        try:
            import google.generativeai as genai
            genai.configure(api_key=os.environ['GEMINI_API_KEY'])
            model=genai.GenerativeModel(os.getenv('GEMINI_MODEL','gemini-2.0-flash'))
            response=model.generate_content('Rewrite the following encouragement in under 240 characters. No numbers, calculations, answers, markup, or additional facts. Text: '+text,request_options={'timeout':5})
            if safe_line(response.text): text=response.text;source='Gemini'
        except Exception:
            pass
    if not safe_line(text): text='Read the givens and check each operation before continuing.';source='template'
    logger.action('Pelita','Review' if review else 'Case brief',text,dict(source=source))
    if not review: return dict(text=text,source=source)
    wrong=sorted({a['step_index'] for a in case['attempts'] if not a['correct']})
    return dict(text=text,source=source,strongest='You verified '+case['data']['steps'][-1]['label']+'.',
                revisit=('Revisit '+case['data']['steps'][wrong[0]]['label']+'.' if wrong else 'Keep explaining why each operation fits the brief.'),
                news='Town news: a plan is ready for its next chapter.')
