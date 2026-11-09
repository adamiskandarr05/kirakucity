"""The only SQL boundary. A request holds an immediate transaction for mutations.

This makes a repeated submission or finish atomic, including across processes.
"""
import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from .cases.templates import TOPICS
from .city import CITY,CORE_ART,extended_lots
from .landscape import arrange
from .progression import appearance


def now():
    return datetime.now(timezone.utc).isoformat(timespec='milliseconds')


class State:
    def __init__(self, path):
        self.path = str(path)
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self.transaction() as db:
            db.executescript('''
            CREATE TABLE IF NOT EXISTS pupils(id TEXT PRIMARY KEY, profile TEXT NOT NULL, level INTEGER DEFAULT 3,
                correct_streak INTEGER DEFAULT 0, wrong_streak INTEGER DEFAULT 0);
            CREATE TABLE IF NOT EXISTS mastery(pupil_id TEXT, topic TEXT, score INTEGER, attempts INTEGER DEFAULT 0,
                PRIMARY KEY(pupil_id,topic));
            CREATE TABLE IF NOT EXISTS sessions(id TEXT PRIMARY KEY,pupil_id TEXT,completed INTEGER DEFAULT 0,created_at TEXT);
            CREATE TABLE IF NOT EXISTS cases(id TEXT PRIMARY KEY,session_id TEXT,pupil_id TEXT,data TEXT,
                status TEXT DEFAULT 'active',result TEXT,plot_id INTEGER,created_at TEXT);
            CREATE TABLE IF NOT EXISTS steps(case_id TEXT,step_index INTEGER,submission_id TEXT,value TEXT,
                correct INTEGER,response TEXT,created_at TEXT,PRIMARY KEY(case_id,step_index,submission_id));
            CREATE TABLE IF NOT EXISTS open_issues(id INTEGER PRIMARY KEY AUTOINCREMENT,pupil_id TEXT,template_id TEXT,
                step_index INTEGER,reason TEXT,due_after INTEGER,status TEXT DEFAULT 'open',case_id TEXT,
                UNIQUE(pupil_id,case_id,step_index));
            CREATE TABLE IF NOT EXISTS town(id INTEGER PRIMARY KEY AUTOINCREMENT,pupil_id TEXT,kind TEXT,name TEXT,
                english TEXT,x INTEGER,y INTEGER,status TEXT,level INTEGER DEFAULT 1,template_id TEXT,
                funded_case_id TEXT,street TEXT);
            CREATE TABLE IF NOT EXISTS decision_log(id INTEGER PRIMARY KEY AUTOINCREMENT,pupil_id TEXT,case_id TEXT,
                agent TEXT,input_summary TEXT,decision TEXT,raw TEXT,timestamp TEXT);
            CREATE INDEX IF NOT EXISTS log_pupil ON decision_log(pupil_id,id);
            ''')
            if not db.execute('SELECT 1 FROM pupils LIMIT 1').fetchone():
                self.seed(db)
            self.migrate_city(db)
            self.migrate_landscape(db)

    def migrate_landscape(self,db):
        if db.execute('PRAGMA user_version').fetchone()[0]>=3:return
        # The legacy fixture intentionally defers all city migrations.
        if 'footprint' not in {r['name'] for r in db.execute('PRAGMA table_info(town)')}:return
        for pupil in db.execute('SELECT id FROM pupils').fetchall():
            plots=[dict(r) for r in db.execute('SELECT * FROM town WHERE pupil_id=?',(pupil['id'],))]
            for plot_id,(x,y) in arrange(plots,CITY['roads']).items():db.execute('UPDATE town SET x=?,y=? WHERE id=?',(x,y,plot_id))
        db.execute('PRAGMA user_version=3')

    def migrate_city(self,db):
        """Expand older towns in place, preserving all case and funding links."""
        if db.execute('PRAGMA user_version').fetchone()[0]>=2:return
        present={r['name'] for r in db.execute('PRAGMA table_info(town)')}
        for name,definition in [('asset','TEXT'),('frame','INTEGER DEFAULT 0'),('footprint','INTEGER DEFAULT 1'),
                                ('landmark','INTEGER DEFAULT 1'),('district',"TEXT DEFAULT 'market'")]:
            if name not in present:db.execute(f'ALTER TABLE town ADD COLUMN {name} {definition}')
        for p in db.execute('SELECT id,x,y,kind FROM town').fetchall():
            asset=CORE_ART.get((p['x'],p['y']),'com_1x1_CafeApartment_kt')
            db.execute('UPDATE town SET x=x+12,y=y+12,asset=?,footprint=? WHERE id=?',(asset,2 if p['kind']=='parks' else 1,p['id']))
        for pupil in db.execute('SELECT id FROM pupils').fetchall():
            for lot in extended_lots():
                db.execute('INSERT INTO town(pupil_id,kind,name,english,x,y,status,template_id,street,asset,frame,footprint,landmark,district) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                    (pupil['id'],lot['kind'],lot['name'],lot['english'],lot['x'],lot['y'],lot['status'],lot['template_id'],lot['street'],lot['asset'],lot['frame'],lot['footprint'],lot['landmark'],lot['district']))
        db.execute('PRAGMA user_version=2')

    @contextmanager
    def transaction(self):
        db = sqlite3.connect(self.path, timeout=15)
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA foreign_keys=ON')
        db.execute('BEGIN IMMEDIATE')
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def seed(self, db):
        profiles = [
            ('pupil-a', 'Pupil A', 'Selesa dengan persamaan; mahu berlatih peratus berturutan. / Confident with equations. Practising successive percentages.', [25, 68, 52, 45]),
            ('pupil-b', 'Pupil B', 'Suka melihat pola data; mahu berlatih persamaan. / Enjoys data patterns. Practising equations.', [65, 28, 74, 46]),
            ('pupil-c', 'Pupil C', 'Selesa dengan peratus; mahu berlatih masalah taman. / Confident with percentages. Practising two unknowns.', [72, 64, 55, 24]),
        ]
        plots = [
            ('shops','Kedai Roti','Bakery',2,2,'built','kedai_bunga_melur'),
            ('shops','Kedai Buku','Bookshop',6,2,'built','kedai_bunga_melur'),
            ('stalls','Gerai Daun','Leaf stall',9,5,'built','gerai_taman'),
            ('parks','Taman Rimba','Grove park',2,6,'built','taman_kiraku'),
            ('shops','Kedai Kopi','Coffee shop',6,9,'built','kedai_bunga_melur'),
            ('stands','Hentian Teksi','Taxi stand',9,9,'built','teksi_kiraku'),
            ('shops','Kedai Bunga Melur','Flower shop',5,5,'empty','kedai_bunga_melur'),
            ('stands','Teksi Kiraku','Taxi stand',9,2,'empty','teksi_kiraku'),
            ('stalls','Gerai Taman','Garden stall',6,6,'empty','gerai_taman'),
            ('parks','Taman Kiraku','Neighbourhood park',2,9,'empty','taman_kiraku'),
        ]
        for pid, name, description, scores in profiles:
            db.execute('INSERT INTO pupils(id,profile) VALUES (?,?)',(pid,json.dumps(dict(name=name,description=description))))
            db.executemany('INSERT INTO mastery(pupil_id,topic,score) VALUES (?,?,?)',[(pid,t,s) for t,s in zip(TOPICS,scores)])
            for kind,name,en,x,y,status,template in plots:
                db.execute('INSERT INTO town(pupil_id,kind,name,english,x,y,status,template_id,street) VALUES (?,?,?,?,?,?,?,?,?)',
                           (pid,kind,name,en,x,y,status,template,'Jalan Pelangi' if x < 5 else 'Jalan Daun'))

    def pupil(self, db, pid):
        row = db.execute('SELECT * FROM pupils WHERE id=?',(pid,)).fetchone()
        if not row:
            raise LookupError('Pupil not found')
        p = dict(row); p.update(json.loads(p.pop('profile')))
        p['mastery'] = [dict(r, title_ms=TOPICS[r['topic']][0], title_en=TOPICS[r['topic']][1]) for r in db.execute('SELECT * FROM mastery WHERE pupil_id=?',(pid,))]
        return p

    def pupils(self, db):
        return [self.pupil(db,r['id']) for r in db.execute('SELECT id FROM pupils ORDER BY id')]

    def start(self, db, pid):
        self.pupil(db,pid)
        sid = uuid.uuid4().hex
        db.execute('INSERT INTO sessions(id,pupil_id,created_at) VALUES (?,?,?)',(sid,pid,now()))
        return self.session(db,sid)

    def session(self, db, sid):
        row = db.execute('SELECT * FROM sessions WHERE id=?',(sid,)).fetchone()
        if not row:
            raise LookupError('Start a pupil session first')
        result = dict(row)
        # Issue deadlines count completed cases across sessions, so restarting cannot defer them.
        result['completed'] = db.execute('SELECT COUNT(*) FROM cases WHERE pupil_id=? AND status=?',(row['pupil_id'],'finished')).fetchone()[0]
        return result

    def snapshot(self, db, pid):
        self.pupil(db,pid)
        plots = [dict(r) for r in db.execute('SELECT * FROM town WHERE pupil_id=? ORDER BY y,x',(pid,))]
        issues = self.issues(db,pid)
        for p in plots:
            p['waiting'] = any(i['plot_id']==p['id'] for i in issues)
            p['appearance']=appearance(p)
        counts = {k:sum(1 for p in plots if p['kind']==k and p['status']=='built') for k in ['shops','stalls','parks','stands']}
        completed=db.execute("SELECT COUNT(*) FROM cases WHERE pupil_id=? AND status='finished'",(pid,)).fetchone()[0]
        return dict(pupil=self.pupil(db,pid), town=plots, counts=counts, open_issues=issues,city=CITY,completed_cases=completed,
                    city_summary=dict(buildings=sum(p['status']=='built' for p in plots),plots=sum(p['status']=='empty' for p in plots),districts=len(CITY['districts'])))

    def issues(self, db, pid):
        return [dict(r) for r in db.execute("SELECT i.*,c.plot_id FROM open_issues i JOIN cases c ON c.id=i.case_id WHERE i.pupil_id=? AND i.status='open' ORDER BY i.due_after,i.id",(pid,))]

    def choose_plot(self, db, pid, template_id):
        return dict(db.execute("SELECT * FROM town WHERE pupil_id=? AND template_id=? ORDER BY (status='empty') DESC,level,id LIMIT 1",(pid,template_id)).fetchone())

    def town_plot(self,db,pid,plot_id):
        row=db.execute('SELECT * FROM town WHERE pupil_id=? AND id=?',(pid,plot_id)).fetchone()
        if not row:raise LookupError('Building not found for this pupil')
        return dict(row)

    def active_case(self, db, pid):
        r = db.execute("SELECT id FROM cases WHERE pupil_id=? AND status='active' ORDER BY created_at DESC LIMIT 1",(pid,)).fetchone()
        return self.case(db,r['id']) if r else None

    def add_case(self, db, session, data, plot_id):
        cid = uuid.uuid4().hex
        db.execute('INSERT INTO cases(id,session_id,pupil_id,data,plot_id,created_at) VALUES (?,?,?,?,?,?)',
                   (cid,session['id'],session['pupil_id'],json.dumps(data),plot_id,now()))
        return self.case(db,cid)

    def case(self, db, cid):
        row = db.execute('SELECT * FROM cases WHERE id=?',(cid,)).fetchone()
        if not row:
            raise LookupError('Case not found')
        r=dict(row); r['data']=json.loads(r['data']);r['result']=json.loads(r['result']) if r['result'] else None
        r['attempts']=[dict(x,response=json.loads(x['response'])) for x in db.execute('SELECT * FROM steps WHERE case_id=? ORDER BY created_at,rowid',(cid,))]
        return r

    def previous_submission(self, db, cid, index, submission_id):
        row=db.execute('SELECT response FROM steps WHERE case_id=? AND step_index=? AND submission_id=?',(cid,index,submission_id)).fetchone()
        return json.loads(row['response']) if row else None

    def add_step(self, db, case, index, submission_id, value, result):
        db.execute('INSERT INTO steps VALUES (?,?,?,?,?,?,?)',(case['id'],index,submission_id,str(value),int(result['correct']),json.dumps(result),now()))

    def record_skill(self, db, pid, topic, correct):
        p=self.pupil(db,pid)
        cs=p['correct_streak']+1 if correct else 0
        ws=0 if correct else p['wrong_streak']+1
        level=p['level']
        if cs==3: level=min(5,level+1);cs=0
        if ws==2: level=max(1,level-1);ws=0
        db.execute('UPDATE pupils SET level=?,correct_streak=?,wrong_streak=? WHERE id=?',(level,cs,ws,pid))
        db.execute('UPDATE mastery SET score=MAX(0,MIN(100,score+?)),attempts=attempts+1 WHERE pupil_id=? AND topic=?',(8 if correct else -6,pid,topic))
        return level

    def add_issue(self, db, case, index, reason, completed):
        db.execute('INSERT OR IGNORE INTO open_issues(pupil_id,template_id,step_index,reason,due_after,case_id) VALUES (?,?,?,?,?,?)',
                   (case['pupil_id'],case['data']['template_id'],index,reason,completed+2,case['id']))

    def resolve_issues(self, db, case):
        # An issue is rehearsed in a later case, not erased by immediately correcting the same case.
        db.execute("UPDATE open_issues SET status='resolved' WHERE pupil_id=? AND template_id=? AND case_id<>?",
                   (case['pupil_id'],case['data']['template_id'],case['id']))

    def finish(self, db, case, result):
        db.execute("UPDATE cases SET status='finished',result=? WHERE id=?",(json.dumps(result),case['id']))
        db.execute('UPDATE sessions SET completed=completed+1 WHERE id=?',(case['session_id'],))
        if result['effect']:
            db.execute("UPDATE town SET status='built',level=CASE WHEN status='built' THEN level+1 ELSE 1 END,funded_case_id=?,name=?,street=? WHERE id=?",
                       (case['id'],case['data']['name'],case['data']['street'],case['plot_id']))

    def log(self, db, pid, cid, agent, inputs, decision, raw=None):
        cur=db.execute('INSERT INTO decision_log(pupil_id,case_id,agent,input_summary,decision,raw,timestamp) VALUES (?,?,?,?,?,?,?)',
                       (pid,cid,agent,inputs,decision,json.dumps(raw or {}),now()))
        return cur.lastrowid

    def events(self, db, pid=None, since=0, cid=None, limit=300):
        clauses=['id>?']; args=[since]
        if pid: clauses.append('pupil_id=?');args.append(pid)
        if cid: clauses.append('case_id=?');args.append(cid)
        rows=db.execute('SELECT * FROM decision_log WHERE '+' AND '.join(clauses)+' ORDER BY id DESC LIMIT ?',(*args,limit))
        return [dict(r,raw=json.loads(r['raw'])) for r in rows]

    def attach_actions(self, db, pid, after, cid):
        db.execute('UPDATE decision_log SET case_id=? WHERE pupil_id=? AND id>? AND case_id IS NULL',(cid,pid,after))

    def teacher(self, db):
        pupils=self.pupils(db)
        return dict(pupils=pupils,open_issues=[i for p in pupils for i in self.issues(db,p['id'])],
                    reports=[e for e in self.events(db,limit=1000) if e['agent']=='Teacher'][:3],decision_log=self.events(db,limit=500))
