"""Browser acceptance checks and real screenshots. Uses a disposable database.

Run: python tools/visual_qa.py [--chrome "C:/.../chrome.exe"]
No external requests or API key are needed. The pinned local Phaser fallback and
Google Fonts copies are intentionally exercised by blocking external requests.
"""
import argparse
import base64
import json
import os
import sys
import tempfile
import threading
import time
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from werkzeug.serving import make_server, WSGIRequestHandler
from playwright.sync_api import sync_playwright
from kiraku.app import create_app

ROOT=Path(__file__).resolve().parents[1]
SHOTS=ROOT/'docs'/'screenshots'
SHOTS.mkdir(parents=True,exist_ok=True)
REPORT={'screens':[],'checks':[],'errors':[],'external_network':'blocked; bundled fallback tested'}


class QuietHandler(WSGIRequestHandler):
    def log(self,*args,**kwargs): pass


def check(condition, message):
    REPORT['checks'].append(dict(ok=bool(condition),description=message))
    if not condition: raise AssertionError(message)


def shot(page,name,width,full=False):
    page.wait_for_timeout(100)
    overflow=page.evaluate('document.documentElement.scrollWidth > innerWidth')
    check(not overflow,f'{name} at {width}px: no horizontal overflow')
    path=SHOTS/f'{name}-{width}.png'
    page.screenshot(path=str(path),full_page=full,animations='disabled')
    REPORT['screens'].append(path.name)


def route_offline(route):
    if route.request.url.startswith('http://127.0.0.1:'):route.continue_()
    else:route.abort()


def contrast(a,b):
    def luminance(color):
        values=[int(color[i:i+2],16)/255 for i in [1,3,5]]
        values=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in values]
        return sum(x*w for x,w in zip(values,[.2126,.7152,.0722]))
    la,lb=sorted([luminance(a),luminance(b)])
    return (lb+.05)/(la+.05)


def run_width(browser,width,height,base_url):
    ctx=browser.new_context(viewport={'width':width,'height':height},device_scale_factor=1)
    ctx.route('**/*',route_offline)
    page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(base_url+'/play');page.wait_for_selector('[data-pupil="pupil-a"]')
    shot(page,'02-pupil-select',width,full=True)
    page.locator('[data-pupil="pupil-a"]').click()
    page.wait_for_function('window.__kirakuTown?.ready')
    page.wait_for_timeout(300)
    check(page.locator('canvas').count()==1,f'{width}px: Phaser town renders')
    before=page.evaluate('window.__kirakuTown.scene.people.map(p=>[p.sprite.x,p.sprite.y])')
    page.wait_for_timeout(250)
    after=page.evaluate('window.__kirakuTown.scene.people.map(p=>[p.sprite.x,p.sprite.y])')
    check(before!=after,f'{width}px: seven walking NPCs move along roads')
    check(page.evaluate('window.__kirakuTown.scene.cars.length')==3,f'{width}px: three cars on road loop')
    labels=page.evaluate('''() => { const s=window.__kirakuTown.scene; return s.labels.filter(l=>l.label.visible).map(l=>({name:l.plot.name,size:parseFloat(l.label.style.fontSize)*l.label.scaleX*s.root.scaleX,rect:l.label.getBounds()})); }''')
    check(all(l['size']>=13.999 for l in labels),f'{width}px: all visible map labels are at least 14 rendered pixels')
    collisions=[]
    for i,a in enumerate(labels):
        for b in labels[i+1:]:
            ra,rb=a['rect'],b['rect']
            if ra['x']<rb['x']+rb['width'] and rb['x']<ra['x']+ra['width'] and ra['y']<rb['y']+rb['height'] and rb['y']<ra['y']+ra['height']:
                collisions.append([a['name'],b['name']])
    check(not collisions,f'{width}px: no overlapping town labels ({collisions})')
    shot(page,'03-town',width)
    check(page.evaluate('window.__kirakuTown.source')=='Cytopia',f'{width}px: original Cytopia artwork is loaded')
    check(page.evaluate('window.__kirakuTown.scene.buildings.size')==118,f'{width}px: all 118 saved city lots are rendered')
    for district in ['skyline','homes','gardens','market']:

        if width<=760:page.locator('#toggle-districts').click()
        page.locator(f'[data-district="{district}"]').click();page.wait_for_timeout(650)
        check(page.locator('#building-detail').is_hidden(),f'{width}px: district control does not click a building behind it ({district})')
        if district=='skyline':shot(page,'17-cytopia-skyline',width)
    old_zoom=page.evaluate('window.__kirakuTown.scene.zoom')
    page.locator('#zoom-in').click();page.wait_for_timeout(450);check(page.evaluate('window.__kirakuTown.scene.zoom')>old_zoom,f'{width}px: zoom control works')
    page.locator('#city-overview').click();shot(page,'18-city-overview',width)
    page.locator('#reset-map').click();page.wait_for_timeout(650)
    if width==1440:
        # A real screenshot of this state-driven Phaser town, used by the landing page.
        image=page.evaluate('''async () => {const s=window.__kirakuTown.scene;s.mini.setVisible(false);await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));const image=await new Promise(resolve=>s.game.renderer.snapshotArea(190,90,1060,600,img=>resolve(img.src)));s.mini.setVisible(true);return image;}''')
        (ROOT/'kiraku/static/assets/town-preview.png').write_bytes(base64.b64decode(image.split(',',1)[1]))
    page.locator('#next-case').click();page.wait_for_selector('#start-working');page.wait_for_timeout(300)
    shot(page,'04-case-brief',width)
    check(page.locator('#case-panel h2').inner_text()=='The flower shop',f'{width}px: Pupil A starts with reverse percentages')
    case=(ctx.request.get(base_url+'/api/pupil/pupil-a/state').json())['active_case']
    page.locator('#start-working').click();shot(page,'05-working',width)
    check(page.locator('#answer-1').count()==0,f'{width}px: later steps locked')
    page.locator('#answer-0').fill('108');page.locator('.answer-form button[type="submit"]').click()
    page.wait_for_selector('.step-feedback:not(.good)')
    page.wait_for_timeout(150)
    check('Adding successive percentages' in page.locator('.step-feedback').inner_text(),f'{width}px: trap feedback names the mistake')
    snapshot=ctx.request.get(base_url+'/api/pupil/pupil-a/state').json()
    check(len(snapshot['open_issues'])==1,f'{width}px: rejected step creates one open issue')
    shot(page,'06-rejected',width)
    for level in [1,2,3]:
        page.locator('[data-hint="0"]').click();page.wait_for_function(f"document.querySelector('.hint-btn').textContent.includes('{min(3,level+1)} of 3')")
        page.wait_for_timeout(100)
        text=page.locator('.hint-text').inner_text()
        check(('110.00' not in text) if level<3 else ('110.00' in text),f'{width}px: hint level {level} answer policy')
        shot(page,f'07-hint-{level}',width)
    page.locator('#trace-list details').first.locator('summary').click();shot(page,'08-trace-raw',width)
    page.locator('#answer-0').fill('110.00');page.locator('.answer-form button[type="submit"]').click()
    page.wait_for_selector('#answer-1');page.locator('#answer-1').fill('33.80');page.locator('.answer-form button[type="submit"]').click()
    page.wait_for_function("!document.querySelector('#finish-case').disabled")
    shot(page,'09-verified',width)
    page.locator('#finish-case').click();page.wait_for_selector('#return-town');shot(page,'10-result',width)
    ids=page.locator('#trace-list details').evaluate_all('(els)=>els.map(e=>Number(e.dataset.eventId))')
    saved=ctx.request.get(base_url+'/api/events').json()['events']
    check(set(ids)=={e['id'] for e in saved if e['case_id']==case['id']},f'{width}px: every displayed trace entry matches decision_log exactly')
    # Freeze at 220ms of the real 600ms tween to capture the building mid-growth.
    page.evaluate('''async () => {const {on}=await import('/static/js/bus.js');on('town:animation-start',id=>{window.__qaPlot=id;setTimeout(()=>{window.__kirakuTown.scene.tweens.pauseAll();window.__qaFrozen=true},220)});}''')
    page.locator('#return-town').click();page.wait_for_function('window.__qaFrozen===true')
    scale=page.evaluate('window.__kirakuTown.scene.buildings.get(window.__qaPlot).getData("image").scaleY')
    check(scale>0 and abs(scale-2)>.001,f'{width}px: real building growth captured mid-animation')
    shot(page,'11-building-animation',width)
    page.evaluate('window.__kirakuTown.scene.tweens.resumeAll()');page.wait_for_timeout(700)
    shot(page,'12-town-grown',width)
    post_collisions=page.evaluate('''()=>{const items=window.__kirakuTown.scene.labels.filter(l=>l.label.visible).map(l=>({name:l.plot.name,r:l.label.getBounds()}));return items.flatMap((a,i)=>items.slice(i+1).filter(b=>a.r.x<b.r.x+b.r.width&&b.r.x<a.r.x+a.r.width&&a.r.y<b.r.y+b.r.height&&b.r.y<a.r.y+a.r.height).map(b=>[a.name,b.name]));}''')
    check(not post_collisions,f'{width}px: labels remain separated after construction ({post_collisions})')
    if width<=760:page.locator('#toggle-districts').click()
    page.locator('#building-list-toggle').click();page.locator(f'[data-building="{case["plot_id"]}"]').click()
    page.wait_for_selector('.calculation');shot(page,'13-building-funding',width)
    check('110.00' in page.locator('#building-detail').inner_text(),f'{width}px: funded building exposes verified calculation')
    page.goto(base_url+'/teacher');page.wait_for_selector('.data-table')
    page.locator('#report-form button').click();page.wait_for_selector('.report-section')
    check(page.locator('.report-section').count()==3,f'{width}px: teacher report has three sections')
    shot(page,'14-teacher',width,full=True)
    page.goto(base_url+'/');page.wait_for_selector('#town-preview');page.wait_for_timeout(200)
    check(page.locator('#town-preview').evaluate('(img)=>img.complete&&img.naturalWidth>0'),f'{width}px: landing uses real town screenshot')
    shot(page,'01-landing',width,full=True)
    check(not errors,f'{width}px: no browser script errors ({errors})')
    ctx.close()


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--chrome');args=parser.parse_args()
    os.environ.pop('GEMINI_API_KEY',None)
    # Store disposable QA state inside the project and leave the user's town untouched.
    scratch=ROOT/'.qa';scratch.mkdir(exist_ok=True)
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,**({'executable_path':args.chrome} if args.chrome else {}))
        try:
            for width,height in [(1440,900),(390,844)]:
                with tempfile.TemporaryDirectory(dir=scratch) as tmp:
                    app=create_app(dict(DATABASE=str(Path(tmp)/'qa.sqlite'),SECRET_KEY='temporary-browser-qa'))
                    server=make_server('127.0.0.1',0,app,threaded=True,request_handler=QuietHandler)
                    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
                    try:run_width(browser,width,height,f'http://127.0.0.1:{server.server_port}')
                    finally:server.shutdown();thread.join()
            # Reduced motion: the same map state, no traffic movement or growth tween.
            with tempfile.TemporaryDirectory(dir=scratch) as tmp:
                app=create_app(dict(DATABASE=str(Path(tmp)/'qa.sqlite'),SECRET_KEY='reduced-motion-qa'))
                server=make_server('127.0.0.1',0,app,threaded=True,request_handler=QuietHandler)
                thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
                try:
                    ctx=browser.new_context(viewport={'width':1440,'height':900},reduced_motion='reduce');ctx.route('**/*',route_offline)
                    page=ctx.new_page();base=f'http://127.0.0.1:{server.server_port}'
                    page.goto(base+'/play');page.locator('[data-pupil="pupil-a"]').click();page.wait_for_function('window.__kirakuTown?.ready')
                    before=page.evaluate('window.__kirakuTown.scene.people.map(p=>[p.sprite.x,p.sprite.y])');cars_before=page.evaluate('window.__kirakuTown.scene.cars.map(p=>[p.sprite.x,p.sprite.y])');page.wait_for_timeout(300)
                    after=page.evaluate('window.__kirakuTown.scene.people.map(p=>[p.sprite.x,p.sprite.y])')
                    check(before==after,'Reduced motion stops NPC traffic')
                    check(cars_before==page.evaluate('window.__kirakuTown.scene.cars.map(p=>[p.sprite.x,p.sprite.y])'),'Reduced motion stops car traffic')
                    check(page.locator('#toggle-motion').get_attribute('aria-pressed')=='true','Reduced motion is reflected in motion control')
                    shot(page,'15-reduced-motion',1440)
                    for width,height in [(1024,768),(768,1024),(320,844)]:
                        page.set_viewport_size({'width':width,'height':height});page.wait_for_timeout(200);shot(page,'16-responsive-town',width)
                    ctx.close()
                finally:server.shutdown();thread.join()
            for foreground,background,name in [('#F4F1EA','#26324A','panel text'),('#B5C0D0','#26324A','muted text'),('#1B2433','#FFB23F','action text'),('#4CC38A','#26324A','verified text'),('#FF6B5A','#26324A','rejected text'),('#7CC4FF','#202C40','trace information')]:
                value=contrast(foreground,background);check(value>=4.5,f'WCAG AA: {name} contrast {value:.2f}:1')
        except Exception as error:
            REPORT['errors'].append(str(error));raise
        finally:
            browser.close();(ROOT/'docs/visual-qa.json').write_text(json.dumps(REPORT,indent=2))
    print(f"Visual QA: {len(REPORT['screens'])} screenshots; {len(REPORT['checks'])} checks passed; no failures.")


if __name__=='__main__':main()
