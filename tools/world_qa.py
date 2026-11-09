"""Real UI upgrades and landscape checks in a disposable fictional town."""
import argparse,json,sys,tempfile,threading
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from kiraku.app import create_app
from kiraku.cases.templates import display
from werkzeug.serving import make_server
from playwright.sync_api import sync_playwright
from visual_qa import QuietHandler,route_offline
ROOT=Path(__file__).resolve().parents[1]
report={'checks':[],'screens':[],'errors':[]}
def check(ok,message):
    report['checks'].append({'ok':bool(ok),'description':message})
    if not ok:raise AssertionError(message)
def shot(page,name):
    page.screenshot(path=str(ROOT/'docs/screenshots'/name));report['screens'].append(name)
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--chrome');args=parser.parse_args()
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,**({'executable_path':args.chrome} if args.chrome else {}))
        try:
            for width,height in [(1440,900),(390,844)]:
                with tempfile.TemporaryDirectory(dir=ROOT/'.qa') as tmp:
                    app=create_app(dict(DATABASE=str(Path(tmp)/'world.sqlite'),SECRET_KEY='world-qa'));store=app.extensions['state']
                    server=make_server('127.0.0.1',0,app,threaded=True,request_handler=QuietHandler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}'
                    ctx=browser.new_context(viewport={'width':width,'height':height});ctx.route('**/*',route_offline);page=ctx.new_page();page.on('pageerror',lambda e:report['errors'].append(str(e)))
                    try:
                        page.goto(base+'/play?pupil=pupil-a&city=1');page.wait_for_function('window.__kirakuTown?.scene.state');page.wait_for_timeout(300)
                        check(page.evaluate('window.__kirakuTown.scene.clouds.length')==9,f'{width}: sky has nine cloud sprites')
                        page.locator('#city-overview').click();page.wait_for_timeout(400);shot(page,f'22-lake-island-{width}.png')
                        check(page.evaluate('window.__kirakuTown.scene.city.landscape.lake.outline.length')==40,f'{width}: irregular lake is present')
                        check(page.evaluate("window.__kirakuTown.scene.game.config.backgroundColor.color===0xa8dcf1"),f'{width}: sky replaces the green backdrop')
                        brightness=page.evaluate('''()=>{const s=window.__kirakuTown.scene,src=s.textures.get('terrain_grass').getSourceImage(),a=document.createElement('canvas');a.width=32;a.height=23;const c=a.getContext('2d');c.drawImage(src,13*32,0,32,23,0,0,32,23);const raw=c.getImageData(0,0,32,23).data;const mean=data=>{let n=0,t=0;for(let i=0;i<data.length;i+=4){if(data[i+3]>200){n++;t+=(data[i]+data[i+1]+data[i+2])/3}}return t/n};const ground=s.textures.get('kiraku-city-ground'),tile=s.city.landscape.land_tiles.find(([x,y])=>!s.roadTiles.has(`${x},${y}`)&&Math.abs(x-26)>8&&Math.abs(y-10)>6),[x,y]=tile,p={x:(x-y)*32+ground.width/2,y:(x+y)*16+64};return {source:mean(raw),bright:mean(ground.context.getImageData(p.x-12,p.y-12,24,12).data)}}''')
                        check(brightness['bright']>brightness['source']*1.15,f'{width}: grass is measurably brighter ({brightness})')
                        if width<=760:page.locator('#toggle-districts').click()
                        page.locator('#lake-view').click();page.wait_for_timeout(650);shot(page,f'23-lakeside-{width}.png')
                        check(page.evaluate('Math.abs(window.__kirakuTown.scene.focus.x-26)<.1'),f'{width}: lake navigation focuses the water')
                        if width<=760:page.locator('#toggle-districts').click()
                        page.locator('#building-list-toggle').click()
                        with store.transaction() as db:plot=max((p for p in store.snapshot(db,'pupil-a')['town'] if p['template_id']=='teksi_kiraku' and p['status']=='empty'),key=lambda p:p['y'])
                        dimensions=[]
                        for level in range(1,5):
                            if level>1:
                                if width<=760:page.locator('#toggle-districts').click()
                                page.locator('#building-list-toggle').click()
                            page.locator(f'[data-building="{plot["id"]}"]').click();page.locator('#upgrade-building').click();page.wait_for_selector('#start-working')
                            check(f'{level-1} → {level}' in page.locator('.upgrade-target').inner_text(),f'{width}: case describes target level {level}')
                            c=ctx.request.get(base+'/api/pupil/pupil-a/state').json()['active_case']
                            with store.transaction() as db:raw=store.case(db,c['id'])
                            page.locator('#start-working').click()
                            for i,step in enumerate(raw['data']['steps']):
                                page.locator(f'#answer-{i}').fill(display(step['expected']));page.locator('.answer-form button[type=submit]').click();page.wait_for_function(f"document.querySelectorAll('.working-step.verified').length==={i+1}")
                            page.locator('#finish-case').click();page.wait_for_selector('#return-town');check(f'{level}' in page.locator('.result-effect').inner_text(),f'{width}: result confirms level {level}');page.locator('#return-town').click();page.wait_for_timeout(800)
                            box=page.evaluate(f'''()=>{{const s=window.__kirakuTown.scene,g=s.buildings.get({plot['id']}),p=g.getData('plot'),image=g.getData('image');s.focusAt(p.x,p.y,false,image.height*.55);return {{level:p.level,height:image.height,key:image.texture.key,width:image.width}};}}''');dimensions.append(box);shot(page,f'24-building-level-{level}-{width}.png')
                            check(box['level']==level,f'{width}: saved building renders level {level}')
                            if level>1:check(box['height']>dimensions[-2]['height'] and box['key']!=dimensions[-2]['key'],f'{width}: level {level} has a new taller design')
                        check(len({d['key'] for d in dimensions})==4,f'{width}: four visibly distinct building stages')
                        route=page.evaluate('''async()=>{const s=window.__kirakuTown.scene,{routeOnRoads}=await import('/static/js/landscape-scene.js'),plot=s.state.town.find(p=>p.district==='skyline');const route=routeOnRoads(s.city,{x:18,y:16},plot);return route.length>0&&route.every(p=>s.roadTiles.has(`${p.x},${p.y}`));}''');check(route,f'{width}: Pelita paths stay on roads around water')
                        check(not report['errors'],f'{width}: no browser errors')
                    finally:ctx.close();server.shutdown();thread.join()
        except Exception as e:report['errors'].append(str(e));raise
        finally:browser.close();(ROOT/'docs/world-qa.json').write_text(json.dumps(report,indent=2))
    print(f"World QA: {len(report['checks'])} checks; {len(report['screens'])} screenshots; {len(report['errors'])} errors")
if __name__=='__main__':main()
