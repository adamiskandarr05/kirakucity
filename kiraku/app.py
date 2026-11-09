import hashlib
import os
import secrets
from pathlib import Path

from flask import Flask, jsonify, render_template, request, session

from .state import State
from .agents.logger import Logger
from .agents import quest, scenario, problem, feedback, hints, outcome, narration, teacher
from . import i18n


def public_case(case):
    data=case['data']
    accepted={a['step_index']:a['response'] for a in case['attempts'] if a['correct']}
    latest={a['step_index']:a['response'] for a in case['attempts']}
    steps=[]
    for index,s in enumerate(data['steps']):
        public={k:s[k] for k in ['label','unit','places']}
        public.update(index=index,verified=index in accepted,last_result=latest.get(index))
        if index in accepted: public['solution']=accepted[index]['solution']
        steps.append(public)
    safe={k:v for k,v in data.items() if k!='steps'}
    safe.update(id=case['id'],status=case['status'],plot_id=case['plot_id'],steps=steps,result=case['result'])
    return safe


def create_app(config=None):
    app=Flask(__name__,instance_relative_config=True)
    app.config.update(SECRET_KEY=os.getenv('KIRAKU_SECRET_KEY') or secrets.token_hex(32),
                      DATABASE=os.getenv('KIRAKU_DATABASE') or str(Path(app.instance_path)/'kiraku.sqlite'),
                      MAX_CONTENT_LENGTH=16384,SESSION_COOKIE_HTTPONLY=True,SESSION_COOKIE_SAMESITE='Strict')
    if config: app.config.update(config)
    store=State(app.config['DATABASE']);app.extensions['state']=store

    @app.context_processor
    def common():
        return dict(llm_enabled=bool(os.getenv('GEMINI_API_KEY')),t=i18n.text,language=i18n.language())

    @app.get('/')
    def index(): return render_template('index.html',page='landing')

    @app.get('/play')
    def play(): return render_template('play.html',page='play')

    @app.get('/teacher')
    def teacher_page(): return render_template('teacher.html',page='teacher')

    @app.errorhandler(LookupError)
    def missing(error): return jsonify(error=str(error)),404

    @app.errorhandler(ValueError)
    def invalid(error): return jsonify(error=str(error)),400

    def payload():
        body=request.get_json(silent=True)
        if not isinstance(body,dict): raise ValueError('Send a JSON object.')
        return body

    def current(db):
        return store.session(db,session.get('sid'))

    def owned(db, body):
        active=current(db);case=store.case(db,str(body.get('case_id','')))
        if case['pupil_id']!=active['pupil_id']: raise LookupError('Case not found for this pupil')
        return active,case

    @app.get('/api/pupils')
    def pupils():
        with store.transaction() as db: return jsonify(pupils=store.pupils(db))

    @app.get('/api/pupil/<pid>/state')
    def pupil_state(pid):
        with store.transaction() as db:
            result=store.snapshot(db,pid)
            active=store.active_case(db,pid)
            result['active_case']=public_case(active) if active else None
            return jsonify(result)

    @app.post('/api/session/start')
    def start():
        body=payload()
        with store.transaction() as db:
            active=store.start(db,str(body.get('pupil_id','')))
            session['sid']=active['id']
            return jsonify(session=active,state=store.snapshot(db,active['pupil_id']))

    @app.post('/api/case/next')
    def next_case():
        body=request.get_json(silent=True) or {}
        if not isinstance(body,dict):raise ValueError('Send a JSON object.')
        with store.transaction() as db:
            active=current(db);pid=active['pupil_id']
            requested=None
            if 'plot_id' in body:
                if type(body['plot_id']) is not int:raise ValueError('Invalid building')
                requested=store.town_plot(db,pid,body['plot_id'])
                if not requested['template_id']:raise ValueError('This building does not have a maths case.')
            existing=store.active_case(db,pid)
            if existing: return jsonify(case=public_case(existing),resumed=True)
            before=store.events(db,limit=1);last=before[0]['id'] if before else 0
            logger=Logger(store,db,pid)
            pupil=store.pupil(db,pid)
            template=quest.choose(pupil,store.issues(db,pid),active['completed'],logger,requested=requested)
            seed=int(hashlib.sha256(f"{pid}:{active['completed']}:{template.id}".encode()).hexdigest()[:10],16)
            data=problem.make_problem(template,seed,logger,default=active['completed']==0)
            plot=requested or store.choose_plot(db,pid,template.id)
            data=scenario.fill(data,active['completed'],logger,location=plot if plot['status']=='built' else None)
            data['narration']=narration.narrate(data,logger)
            data['progression']=dict(action='upgrade' if plot['status']=='built' else 'build',current_level=plot['level'] if plot['status']=='built' else 0,next_level=plot['level']+1 if plot['status']=='built' else 1)
            case=store.add_case(db,active,data,plot['id'])
            store.attach_actions(db,pid,last,case['id'])
            return jsonify(case=public_case(case),resumed=False)

    @app.post('/api/case/step')
    def check_step():
        body=payload()
        with store.transaction() as db:
            active,case=owned(db,body)
            index=body.get('step_index')
            if type(index) is not int or not 0<=index<len(case['data']['steps']): raise ValueError('Invalid step index')
            value=body.get('value','')
            if not isinstance(value,(str,int,float)) or isinstance(value,bool): raise ValueError('Enter a decimal number')
            submission=str(body.get('submission_id') or hashlib.sha256(f'{case["id"]}:{index}:{value}'.encode()).hexdigest())[:100]
            old=store.previous_submission(db,case['id'],index,submission)
            if old is not None: return jsonify(old)
            accepted={a['step_index']:a['response'] for a in case['attempts'] if a['correct']}
            if index in accepted: return jsonify(accepted[index])
            if case['status']!='active': return jsonify(error='This case is already finished.'),409
            if any(i not in accepted for i in range(index)): return jsonify(error='Verify the previous step first.'),409
            logger=Logger(store,db,case['pupil_id'],case['id'])
            result=feedback.check(store,db,case,index,value,active['completed'],logger)
            store.add_step(db,case,index,submission,value,result)
            return jsonify(result)

    @app.post('/api/case/hint')
    def get_hint():
        body=payload()
        with store.transaction() as db:
            active,case=owned(db,body)
            index=body.get('step_index');level=body.get('level',1)
            if type(index) is not int or not 0<=index<len(case['data']['steps']) or type(level) is not int or level not in [1,2,3]: raise ValueError('Invalid hint request')
            accepted={a['step_index'] for a in case['attempts'] if a['correct']}
            if case['status']!='active' or any(i not in accepted for i in range(index)): return jsonify(error='This step is locked.'),409
            logger=Logger(store,db,case['pupil_id'],case['id'])
            return jsonify(hints.hint(case['data']['steps'][index],level,logger))

    @app.post('/api/case/finish')
    def finish_case():
        body=payload()
        with store.transaction() as db:
            active,case=owned(db,body)
            if case['result']: return jsonify(case['result'])
            accepted={a['step_index'] for a in case['attempts'] if a['correct']}
            all_correct=len(accepted)==len(case['data']['steps'])
            if not all_correct: return jsonify(error='Verify every step before finishing. The town has not changed.'),409
            logger=Logger(store,db,case['pupil_id'],case['id'])
            result=outcome.evaluate(case,all_correct,logger,plot=store.town_plot(db,case['pupil_id'],case['plot_id']))
            result['review']=narration.narrate(case,logger,review=True)
            result['marks']=[dict(label=s['label'],verified=True,solution=s['solution']['worked']) for s in case['data']['steps']]
            store.resolve_issues(db,case)
            store.finish(db,case,result)
            return jsonify(result)

    @app.get('/api/case/<cid>/why')
    def why(cid):
        with store.transaction() as db:
            active=current(db);case=store.case(db,cid)
            if active['pupil_id']!=case['pupil_id']: raise LookupError('Case not found for this pupil')
            return jsonify(case=public_case(case),events=store.events(db,active['pupil_id'],cid=cid))

    @app.get('/api/events')
    def events():
        with store.transaction() as db:
            active=current(db)
            try: since=int(request.args.get('since','0'))
            except ValueError: raise ValueError('Invalid event cursor')
            return jsonify(events=store.events(db,active['pupil_id'],since=max(0,since)))

    @app.get('/api/teacher/state')
    def teacher_state():
        with store.transaction() as db: return jsonify(store.teacher(db))

    @app.post('/api/teacher/report')
    def teacher_report():
        body=payload()
        with store.transaction() as db:
            pid=str(body.get('pupil_id',''))
            return jsonify(teacher.report(store.snapshot(db,pid),Logger(store,db,pid)))

    @app.after_request
    def headers(response):
        if request.path.startswith('/api/') and response.is_json and (request.headers.get('X-Kiraku-Language') or request.cookies.get('kiraku-language')):
            response.set_data(app.json.dumps(i18n.response_view(response.get_json(),request.path)))
        response.headers['X-Content-Type-Options']='nosniff'
        response.headers['Referrer-Policy']='same-origin'
        if request.path.startswith('/api/'): response.headers['Cache-Control']='no-store'
        return response

    @app.post('/api/demo/prepare')
    def prepare_demo():
        from .demo import prepare
        return jsonify(prepare(app))

    return app
