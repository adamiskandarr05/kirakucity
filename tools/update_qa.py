"""Acceptance checks for HUD layout, smooth camera, Pelita, demo and language."""
import argparse,json,sys,tempfile,threading
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from kiraku.app import create_app
from kiraku.demo import prepare
from werkzeug.serving import make_server
from playwright.sync_api import sync_playwright
from visual_qa import QuietHandler,route_offline

ROOT=Path(__file__).resolve().parents[1]
report={'checks':[],'screens':[],'errors':[],'frame_samples':[]}
def check(ok,message):
    report['checks'].append({'ok':bool(ok),'description':message})
    if not ok:raise AssertionError(message)

def overlaps(page):
    return page.evaluate('''()=>{const selectors=['.town-heading>div:first-child','.town-stats','.district-navigation','.map-tools','.pelita-card','#next-case','.map-legend','.trace-panel'];const rows=selectors.map(key=>{const e=document.querySelector(key);if(!e.getClientRects().length)return null;const r=e.getBoundingClientRect();return {key,x:r.x,y:r.y,width:r.width,height:r.height}}).filter(Boolean);const s=window.__kirakuTown.scene;if(s.mini.visible){const c=s.game.canvas.getBoundingClientRect();rows.push({key:'minimap',x:c.x+s.mini.x,y:c.y+s.mini.y,width:196,height:155})}return rows.flatMap((a,i)=>rows.slice(i+1).filter(b=>a.x<b.x+b.width-1&&b.x<a.x+a.width-1&&a.y<b.y+b.height-1&&b.y<a.y+a.height-1).map(b=>[a.key,b.key]));}''')

def main():
    args=argparse.ArgumentParser();args.add_argument('--chrome');args=args.parse_args()
    scratch=ROOT/'.qa';scratch.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=scratch) as tmp:
        app=create_app({'DATABASE':str(Path(tmp)/'qa.sqlite'),'SECRET_KEY':'update-qa'})
        check(prepare(app)['completed']==8,'Eight genuinely checked demo cases prepared')
        server=make_server('127.0.0.1',0,app,threaded=True,request_handler=QuietHandler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}'
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True,**({'executable_path':args.chrome} if args.chrome else {}))
            try:
                for width,height in [(1886,782),(1440,900),(1280,720),(1024,768),(768,1024),(812,500),(390,844),(320,844)]:
                    for lang in ['en','ms']:
                        ctx=browser.new_context(viewport={'width':width,'height':height});ctx.route('**/*',route_offline);ctx.add_cookies([{'name':'kiraku-language','value':lang,'url':base}]);page=ctx.new_page();page.on('pageerror',lambda e:report['errors'].append(str(e)))
                        page.goto(base+'/play?pupil=pupil-a&city=1');page.wait_for_function('window.__kirakuTown?.ready&&window.__kirakuTown.scene.state?.town.length>100');page.wait_for_timeout(400)
                        check(not page.evaluate('document.documentElement.scrollWidth>innerWidth'),f'{width}×{height} {lang}: no horizontal overflow')
                        check(page.locator('#town-screen').bounding_box()['y']+page.locator('#town-screen').bounding_box()['height']<=height,f'{width} {lang}: town controls fit the window height')
                        collision=overlaps(page);check(not collision,f'{width}×{height} {lang}: no HUD overlaps {collision}')
                        check(page.evaluate('window.__kirakuTown.scene.pelita.texture.key')=='pelita',f'{width} {lang}: visible Pelita avatar loaded')
                        check('8' in page.locator('#town-subtitle').inner_text(),f'{width} {lang}: demo completion count shown')
                        if width<=760:
                            page.locator('#toggle-districts').click();page.wait_for_timeout(120);collision=overlaps(page);check(not collision,f'{width} {lang}: expanded district list separated {collision}');page.locator('[data-district="gardens"]').click();page.wait_for_timeout(500)
                        page.locator('#find-pelita').click();page.wait_for_timeout(600)
                        check(page.evaluate('window.__kirakuTown.scene.avatarSpeech.visible'),f'{width} {lang}: finding Pelita reveals the guide')
                        avatar_collisions=page.evaluate('''()=>{const s=window.__kirakuTown.scene;return [s.avatarSpeech,s.avatarTag].filter(o=>o.visible).flatMap(o=>{const r=o.getBounds();return (s.hud?.obstacles||[]).filter(b=>r.x<b.x+b.width&&r.right>b.x&&r.y<b.y+b.height&&r.bottom>b.y).map(b=>[r,b]);});}''')
                        check(not avatar_collisions,f'{width} {lang}: avatar labels avoid every HUD panel')
                        if width in [1886,1280,390,320]:
                            name=f'19-town-polished-{width}-{lang}.png';page.screenshot(path=str(ROOT/'docs/screenshots'/name));report['screens'].append(name)
                        if width==1440 and lang=='en':
                            page.evaluate('''()=>{const s=window.__kirakuTown.scene;window.__buildings=[...s.buildings.values()];window.__root=[s.root.x,s.root.y];s.renderState(s.state);window.__sameBuildings=window.__buildings.every(g=>s.buildings.get(g.getData('plot').id)===g);}''')
                            check(page.evaluate('window.__sameBuildings'),'Unchanged state reuses all 118 building objects')
                            box=page.locator('#town-canvas').bounding_box();x=box['x']+box['width']*.55;y=box['y']+box['height']*.5
                            page.mouse.move(x,y);page.mouse.down();page.mouse.move(x+180,y+70,steps=16);page.wait_for_timeout(60);page.mouse.up();page.wait_for_timeout(800)
                            check(page.evaluate('Math.abs(window.__kirakuTown.scene.root.x-window.__root[0])>100'),'Dragging pans the map and settles with inertia')
                            page.locator('#zoom-in').click();check(page.evaluate('Math.abs(window.__kirakuTown.scene.cameraGoal.zoom-window.__kirakuTown.scene.zoom)>.001'),'Zoom interpolates toward its target')
                            page.wait_for_timeout(650);check(page.evaluate('Math.abs(window.__kirakuTown.scene.cameraGoal.zoom-window.__kirakuTown.scene.zoom)<.005'),'Smooth zoom reaches its target')
                            samples=page.evaluate('''()=>new Promise(resolve=>{const d=[];let last=performance.now();function tick(now){d.push(now-last);last=now;if(d.length<90)requestAnimationFrame(tick);else resolve(d.sort((a,b)=>a-b));}requestAnimationFrame(tick);})''')
                            report['frame_samples'].append({'viewport':[width,height],'median_ms':round(samples[45],2),'p95_ms':round(samples[85],2)})
                            page.locator('#open-settings').click();check(page.locator('#settings-dialog').is_visible(),'Settings opens as an accessible dialog');page.locator('#settings-motion').check();page.locator('#settings-dialog [data-close-dialog]').click()
                            before=page.evaluate('window.__kirakuTown.scene.people.map(a=>a.t)');page.wait_for_timeout(200);check(before==page.evaluate('window.__kirakuTown.scene.people.map(a=>a.t)'),'Settings pauses background animation')
                        page.locator('#next-case').click();page.wait_for_selector('#start-working');page.wait_for_timeout(350);collision=overlaps(page);check(not collision,f'{width} {lang}: case HUD separated {collision}')
                        if width==390:
                            page.locator('#start-working').click();page.locator('#answer-0').fill('123.45');page.locator('#open-settings').click();page.locator(f'input[name="language"][value="{"ms" if lang=="en" else "en"}"]').check();page.wait_for_load_state('networkidle');page.wait_for_selector('#answer-0');check(page.locator('#answer-0').input_value()=='123.45',f'{lang}: language switch retains draft and case view')
                            page.locator('#close-case').click();page.wait_for_timeout(150)
                        check(not report['errors'],f'{width} {lang}: no browser errors')
                        ctx.close()
                for lang in ['en','ms']:
                    ctx=browser.new_context(viewport={'width':390,'height':844});ctx.route('**/*',route_offline);ctx.add_cookies([{'name':'kiraku-language','value':lang,'url':base}]);page=ctx.new_page();page.on('pageerror',lambda e:report['errors'].append(str(e)));page.goto(base+'/teacher');page.wait_for_selector('.data-table')
                    page.locator('#report-form button').click();page.wait_for_selector('.report-section');check(page.locator('.report-section').count()==3,f'{lang}: localized teacher report has three sections')
                    check(('penguasaan' in page.locator('#teacher-report').inner_text()) if lang=='ms' else ('mastery' in page.locator('#teacher-report').inner_text()),f'{lang}: teacher report uses selected language')
                    check(page.locator('#toast').is_hidden(),f'{lang}: teacher desk loads without an error')
                    page.locator('#open-settings').click();page.locator('#prepare-demo').click();page.wait_for_function("!document.querySelector('#prepare-demo').disabled");check(page.locator('#toast').is_visible(),f'{lang}: demo preparation can be repeated from Settings')
                    name=f'21-settings-390-{lang}.png';page.screenshot(path=str(ROOT/'docs/screenshots'/name));report['screens'].append(name);ctx.close()
                check(not report['errors'],'Teacher desk has no browser errors in either language')
                # Use the visible owl itself to open the saved activity inspector.
                ctx=browser.new_context(viewport={'width':1440,'height':900});ctx.route('**/*',route_offline);page=ctx.new_page();page.goto(base+'/play?pupil=pupil-a&city=1');page.wait_for_function('window.__kirakuTown?.scene.state');page.locator('#find-pelita').click();page.wait_for_timeout(650)
                position=page.evaluate('''()=>{const s=window.__kirakuTown.scene,r=s.game.canvas.getBoundingClientRect();return {x:r.x+s.root.x+s.pelita.x*s.zoom,y:r.y+s.root.y+(s.pelita.y-15)*s.zoom}}''');page.mouse.click(**position);check(page.locator('#agent-dialog').is_visible(),'Clicking the town avatar opens actual saved agent activity')
                ids=page.locator('#agent-activity [data-event-id]').evaluate_all('(els)=>els.map(e=>Number(e.dataset.eventId))');saved=ctx.request.get(base+'/api/events').json()['events'];check(set(ids).issubset({e['id'] for e in saved}),'Every avatar activity is backed by a saved decision ID');page.screenshot(path=str(ROOT/'docs/screenshots/20-pelita-activity.png'));report['screens'].append('20-pelita-activity.png');ctx.close()
            except Exception as e:report['errors'].append(str(e));raise
            finally:browser.close();server.shutdown();thread.join();(ROOT/'docs/update-qa.json').write_text(json.dumps(report,indent=2))
    print(f"Update QA: {len(report['checks'])} checks, {len(report['screens'])} screenshots, {len(report['errors'])} errors")
if __name__=='__main__':main()
