import os
from kiraku.agents.narration import narrate,safe_line


class Log:
    def action(self,*args):pass


def test_no_unseen_answer_in_narration():
    result=narrate({},Log())
    assert safe_line(result['text'])
    assert not safe_line('The answer is 110.00.')
    assert not safe_line('x'*400)
    assert not safe_line('<script>bad</script>')


def test_optional_gemini_failure_falls_back(monkeypatch):
    monkeypatch.setenv('GEMINI_API_KEY','fake-test-key')
    import sys,types
    fake=types.SimpleNamespace(configure=lambda **kw:None,GenerativeModel=lambda *a: (_ for _ in ()).throw(RuntimeError('offline')))
    monkeypatch.setitem(sys.modules,'google.generativeai',fake)
    assert narrate({},Log())['source']=='template'
