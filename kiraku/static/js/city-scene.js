// Kiraku renderer; original Cytopia sheets retain GPL-3.0 and author credits.
import {emit,on} from './bus.js';
import {t,plotName} from './i18n.js';
import {buildingDesign} from './building-designs.js';
import {makeSky,updateSky,drawLandscape,drawNature,routeOnRoads} from './landscape-scene.js';
const project=(x,y)=>({x:(x-y)*32,y:(x+y)*16});
const inverse=(x,y)=>({x:(x/32+y/16)/2,y:(y/16-x/32)/2});
const AMBER=0xffb23f;
let scene,creating=false;
export async function createTown(){
  if(scene||creating)return;creating=true;
  if(!window.Phaser){creating=false;emit('town:error',t('The town engine could not load. Refresh to try again.','Bandar tidak dapat dimuatkan. Muat semula untuk mencuba lagi.'));return;}
  let catalog;
  try{const r=await fetch('/static/assets/cytopia/manifest.json');if(!r.ok)throw Error();catalog=await r.json();}
  catch{creating=false;emit('town:error',t('The city artwork could not load. Refresh to try again.','Seni bandar tidak dapat dimuatkan. Muat semula untuk mencuba lagi.'));return;}
  // Phaser measures a font once. Wait for the local font copies before it caches
  // fallback metrics, which otherwise clip pixel labels after a state refresh.
  if(document.fonts)await Promise.all([document.fonts.load('14px "Press Start 2P"'),document.fonts.load('17px Inter')]).catch(()=>{});
  const art=new Map(catalog.assets.map(a=>[a.id,a]));
  class City extends Phaser.Scene{
    constructor(){super('BandarKiraku');this.people=[];this.cars=[];this.buildings=new Map();this.labels=[];this.scenery=[];this.paused=matchMedia('(prefers-reduced-motion:reduce)').matches;this.zoomFactor=1;this.focus={x:18,y:18};this.zoom=1;this.drag=null;this.lastMini=0;this.city=null;this.cameraGoal=null;this.velocity={x:0,y:0};this.lastLabels=0;this.lastSort=0;this.lastCull=0;this.avatarPosition={x:18,y:16};this.avatarRoute=[];}
    preload(){
      this.load.image('pelita','/static/assets/pelita.png');
      for(const a of catalog.assets)this.load.spritesheet(a.id,`/static/assets/cytopia/${a.file}`,{frameWidth:a.tiles.clip_width,frameHeight:a.id.startsWith('terrain_')?23:a.tiles.clip_height});
      for(const a of ['car-a','car-b','npc-0','npc-1','npc-2','npc-3','npc-0b','npc-1b','npc-2b','npc-3b'])this.load.image(a,`/static/assets/pixel/${a}.png`);
    }
    create(){
      scene=this;makeSky(this);this.root=this.add.container(0,0);this.objects=this.add.container(0,0);this.labelLayer=this.add.container(0,0);this.root.add([this.objects,this.labelLayer]);this.makeTraffic();this.makeAvatar();this.makeMinimap();
      this.hud=window.__kirakuHUD;this.scale.on('resize',()=>this.layout());
      this.input.on('pointerdown',p=>{if(p.event?.target!==this.game.canvas)return;if(this.overMinimap(p)){this.minimapFocus(p);return;}this.velocity={x:0,y:0};this.tweens.killTweensOf(this.root);this.cameraGoal={x:this.root.x,y:this.root.y,zoom:this.zoom};this.drag={x:p.x,y:p.y,rx:this.root.x,ry:this.root.y,moved:false,lastX:p.x,lastY:p.y,lastTime:performance.now()};});
      this.input.on('pointermove',p=>{if(!this.drag||!p.isDown)return;const dx=p.x-this.drag.x,dy=p.y-this.drag.y;if(Math.abs(dx)+Math.abs(dy)>7)this.drag.moved=true;if(this.drag.moved){const now=performance.now(),dt=Math.max(8,now-this.drag.lastTime);this.velocity={x:Phaser.Math.Clamp((p.x-this.drag.lastX)/dt,-2,2),y:Phaser.Math.Clamp((p.y-this.drag.lastY)/dt,-2,2)};this.drag.lastX=p.x;this.drag.lastY=p.y;this.drag.lastTime=now;this.cameraGoal={x:this.drag.rx+dx,y:this.drag.ry+dy,zoom:this.zoom};}});
      this.input.on('pointerup',()=>{if(!this.drag?.moved||performance.now()-(this.drag?.lastTime||0)>90||this.paused)this.velocity={x:0,y:0};setTimeout(()=>this.drag=null,0);});
      this.game.canvas.addEventListener('pointercancel',()=>{this.drag=null;this.velocity={x:0,y:0};});
      this.input.on('wheel',(p,objects,dx,dy)=>this.zoomAt(Math.exp(-Phaser.Math.Clamp(dy,-120,120)*.0015),p));this.game.canvas.addEventListener('wheel',e=>e.preventDefault(),{passive:false});
      this.keys=this.input.keyboard.addKeys({up:'UP',down:'DOWN',left:'LEFT',right:'RIGHT',w:'W',a:'A',s:'S',d:'D'},false);
      on('town:state',s=>this.renderState(s));
      on('town:case',data=>{this.activePlot=data?.plot_id;this.inCase=!!data;this.layout();if(data){const p=this.state?.town.find(p=>p.id===data.plot_id);if(p){const height=p.appearance?.height||art.get(p.asset)?.tiles.clip_height||30;this.focusAt(p.x,p.y,false,height*.55);}}this.refreshLabels();});
      on('town:district',id=>{const d=this.city?.districts.find(d=>d.id===id);if(d){this.activePlot=null;this.focusAt(d.x,d.y,true);emit('town:district-selected',d);}});
      on('town:lake',()=>{const lake=this.city?.landscape.lake;if(lake){this.zoomFactor=.8;this.zoom=this.baseScale*this.zoomFactor;this.root.setScale(this.zoom);this.focusAt(lake.x,lake.y,true);}});
      on('town:pulse',id=>this.pulse(id));on('town:rejected',id=>this.reject(id));on('town:grow',id=>this.grow(id));
      on('town:zoom',f=>this.zoomAt(f));on('town:reset',()=>{this.zoomFactor=1;this.zoom=this.baseScale;this.cameraGoal=null;this.root.setScale(this.zoom);const d=this.city?.districts[0];this.focusAt(d?.x??18,d?.y??18,true);if(d)emit('town:district-selected',d);});on('town:overview',()=>this.overview());
      on('town:hud',data=>{this.hud=data;this.mini.setPosition(data.mini.x,data.mini.y).setVisible(data.mini.visible);this.refreshLabels();});
      on('town:agent-action',event=>this.agentAction(event));on('town:find-pelita',()=>{this.focusAt(this.avatarPosition.x,this.avatarPosition.y,true);this.showAvatarSpeech();});
      on('town:motion',p=>{this.paused=p||matchMedia('(prefers-reduced-motion:reduce)').matches;if(this.paused)this.tweens.getTweens().forEach(t=>t.complete());});
      matchMedia('(prefers-reduced-motion:reduce)').addEventListener('change',e=>{this.paused=e.matches;emit('town:motion-state',this.paused);});
      window.__kirakuTown={ready:true,source:'Cytopia',commit:catalog.commit,snapshot:()=>this.game.canvas.toDataURL('image/png'),scene:this};emit('town:ready');
    }
    drawGround(){drawLandscape(this);}
    drawScenery(){drawNature(this,art);}
    labelTexture(text,color){
      // Share immutable label bitmaps. Recreating pooled live Text canvases on
      // every API update can temporarily corrupt glyphs in the canvas renderer.
      const key=`kiraku-label:${color}:${text}`;if(this.textures.exists(key))return key;
      const canvas=document.createElement('canvas'),ctx=canvas.getContext('2d'),lines=text.split('\n');ctx.font='14px "Press Start 2P",monospace';
      canvas.width=Math.ceil(Math.max(...lines.map(line=>ctx.measureText(line).width)))+24;canvas.height=lines.length*24+16;
      ctx.imageSmoothingEnabled=false;ctx.font='14px "Press Start 2P",monospace';ctx.textAlign='center';ctx.textBaseline='alphabetic';ctx.lineJoin='round';ctx.lineWidth=4;ctx.strokeStyle='#162334';ctx.fillStyle=color;
      lines.forEach((line,i)=>{ctx.strokeText(line,canvas.width/2,26+i*24);ctx.fillText(line,canvas.width/2,26+i*24);});this.textures.addCanvas(key,canvas);return key;
    }
    pixelLabel(x,y,text,color){
      const label=this.add.image(x,y,this.labelTexture(text,color)).setOrigin(.5,1);label.style={fontSize:'14px'};label.text=text;
      label.setText=value=>{label.text=value;label.setTexture(this.labelTexture(value,color));return label;};return label;
    }
    uiLabel(x,y,text,size,bold=false){
      const key=`ui:${size}:${bold}:${text}`;
      if(!this.textures.exists(key)){
        const canvas=document.createElement('canvas'),ctx=canvas.getContext('2d'),font=`${bold?'700':'400'} ${size}px Inter`;
        ctx.font=font;canvas.width=Math.ceil(ctx.measureText(text).width)+4;canvas.height=size+8;
        ctx.font=font;ctx.fillStyle=bold?'#f4f1ea':'#b5c0d0';ctx.textBaseline='top';ctx.fillText(text,1,2);this.textures.addCanvas(key,canvas);
      }
      return this.add.image(x,y,key).setOrigin(0);
    }
    renderState(state){
      const first=!this.city;this.state=state;this.city=state.city;if(first)this.drawGround();
      for(const [id,g] of this.buildings){if(!state.town.some(p=>p.id===id)){g.destroy(true);this.buildings.delete(id);this.labels=this.labels.filter(i=>{if(i.plot.id===id)i.label.destroy();return i.plot.id!==id;});}}
      for(const plot of state.town){
        const fingerprint=JSON.stringify(plot),existing=this.buildings.get(plot.id);if(existing?.getData('fingerprint')===fingerprint)continue;if(existing){existing.destroy(true);this.labels=this.labels.filter(i=>{if(i.plot.id===plot.id)i.label.destroy();return i.plot.id!==plot.id;});}
        const p=project(plot.x,plot.y),size=plot.footprint||1,g=this.add.container(p.x,p.y);g.setDepth(p.y+size*16);g.setData('plot',plot);g.setData('fingerprint',fingerprint);this.objects.add(g);let hot;
        if(plot.status==='built'){
          const design=buildingDesign(this,plot);const image=this.add.image(0,size*16,design.key,design.frame).setOrigin(.5,1).setScale(2).setInteractive({useHandCursor:true});g.add(image);g.setData('image',image);g.setData('design',design);hot=image;
          image.on('pointerup',pointer=>{if(pointer.event?.target===this.game.canvas&&!this.drag?.moved){this.selectedPlot=plot.id;this.refreshLabels();emit('town:building',plot);}});
          if(plot.kind==='shops'&&plot.landmark){const sign=this.add.rectangle(-8,-12,10,4,0xffd783);g.add(sign);g.setData('sign',sign);}
        }else{
          const line=this.add.graphics();line.lineStyle(2,plot.waiting?AMBER:0xe4dba7,.95);const pts=[{x:0,y:-16*size},{x:32*size,y:0},{x:0,y:16*size},{x:-32*size,y:0}];
          for(let i=0;i<4;i++){const a=pts[i],b=pts[(i+1)%4];for(let t=0;t<1;t+=.25){line.beginPath();line.moveTo(a.x+(b.x-a.x)*t,a.y+(b.y-a.y)*t);line.lineTo(a.x+(b.x-a.x)*(t+.14),a.y+(b.y-a.y)*(t+.14));line.strokePath();}}
          g.add(line);g.add([this.add.rectangle(0,-11,2,23,0xd5b986),this.add.rectangle(0,-25,28,17,0xf3d49a).setStrokeStyle(2,0x695b3d),this.add.text(0,-26,plot.waiting?'!':'+',{fontFamily:'Inter',fontSize:'17px',fontStyle:'bold',color:'#293e32'}).setOrigin(.5)]);
          g.setSize(size*64,size*48).setInteractive({useHandCursor:true});g.on('pointerup',pointer=>{if(pointer.event?.target===this.game.canvas&&!this.drag?.moved){this.selectedPlot=plot.id;this.refreshLabels();emit('town:building',plot);}});hot=g;
        }
        if(plot.waiting)g.add(this.add.triangle(13,-42,0,0,18,5,0,11,AMBER).setOrigin(0));
        const a=art.get(plot.asset),top=plot.status==='built'?size*16-(g.getData('design')?.height||a?.tiles.clip_height||30)*2-8:size*16+19;
        const label=this.pixelLabel(p.x,p.y+top,this.labelText(plot),plot.waiting?'#ffb23f':'#f4f1ea');this.labelLayer.add(label);
        const item={label,plot,x:p.x,y:p.y+top,hover:false};this.labels.push(item);
        hot.on('pointerover',pointer=>{if(pointer.event?.target===this.game.canvas&&!this.drag?.moved){item.hover=true;label.setText(plotName(plot));this.refreshLabels();}});
        hot.on('pointerout',()=>{item.hover=false;label.setText(this.labelText(plot));this.refreshLabels();});this.buildings.set(plot.id,g);
      }
      if(first){this.drawScenery();this.layout();}this.objects.sort('depth');this.refreshLabels();this.drawMinimap();
    }
    labelText(p){return plotName(p)+(p.status==='built'&&p.template_id?` · ${t('Lv','T')} ${p.level}`:'');}
    viewport(){const w=this.scale.width,h=this.scale.height,mobile=w<=760,panel=this.inCase&&!mobile?(w<=1100?410:440):0;return {w,h,mobile,width:w-panel,height:mobile&&this.inCase?h*.46:h};}
    focalPoint(){const v=this.viewport();if(this.hud&&!this.inCase){const r=this.hud.free;return {x:(r.left+r.right)/2,y:Math.max(r.top+40,(r.top+r.bottom)/2)};}return {x:v.width/2,y:this.inCase?v.height*.38:v.height*.46};}
    layout(){const v=this.viewport();this.mobile=v.mobile;this.baseScale=v.mobile?(this.inCase?1.05:1.12):(v.width<800?1.12:1.34);this.zoom=this.baseScale*this.zoomFactor;this.root.setScale(this.zoom);this.positionFocus();this.mini.setVisible(this.hud?.mini.visible??false);if(this.hud)this.mini.setPosition(this.hud.mini.x,this.hud.mini.y);this.refreshLabels();this.drawMinimap();}
    positionFocus(){const p=project(this.focus.x,this.focus.y),f=this.focalPoint();this.root.setPosition(f.x-p.x*this.zoom,f.y-p.y*this.zoom);this.cameraGoal={x:this.root.x,y:this.root.y,zoom:this.zoom};this.velocity={x:0,y:0};}
    captureFocus(){const f=this.focalPoint();this.focus=inverse((f.x-this.root.x)/this.zoom,(f.y-this.root.y)/this.zoom);}
    focusAt(x,y,animate=true,elevation=0){this.focus={x:Phaser.Math.Clamp(x,0,39),y:Phaser.Math.Clamp(y,0,39)};const p=project(this.focus.x,this.focus.y),f=this.focalPoint();this.velocity={x:0,y:0};this.cameraGoal={x:f.x-p.x*this.zoom,y:f.y-p.y*this.zoom+elevation*this.zoom,zoom:this.zoom};if(!animate||this.paused){this.root.setPosition(this.cameraGoal.x,this.cameraGoal.y);this.refreshLabels();this.drawMinimap();}}
    zoomAt(factor,pointer){if(!this.city)return;const goal=this.cameraGoal||{x:this.root.x,y:this.root.y,zoom:this.zoom},f=pointer||this.focalPoint(),wx=(f.x-goal.x)/goal.zoom,wy=(f.y-goal.y)/goal.zoom;this.zoomFactor=Phaser.Math.Clamp(this.zoomFactor*factor,.25,2);const zoom=this.baseScale*this.zoomFactor;this.velocity={x:0,y:0};this.cameraGoal={x:f.x-wx*zoom,y:f.y-wy*zoom,zoom};if(this.paused){this.zoom=zoom;this.root.setScale(zoom).setPosition(this.cameraGoal.x,this.cameraGoal.y);}}
    overview(){if(!this.city)return;const v=this.viewport();this.zoomFactor=Math.max(.2,Math.min((v.width-80)/(this.city.size*64),(v.height-220)/(this.city.size*32))/this.baseScale);this.zoom=this.baseScale*this.zoomFactor;this.root.setScale(this.zoom);this.focusAt(19.5,19.5,false);this.refreshLabels();}

    refreshLabels(){
      if(!this.state||!this.zoom)return;const v=this.viewport(),used=[this.avatarTag,this.avatarSpeech].filter(o=>o?.visible).map(o=>o.getBounds());const rank=i=>i.plot.id===this.activePlot||i.plot.id===this.selectedPlot?-2:i.hover?-1:0;const list=[...this.labels].sort((a,b)=>rank(a)-rank(b));
      const navigation=document.querySelector('.district-navigation');const safeTop=this.inCase?58:(this.hud?.free.top??58);const obstacles=this.hud?.obstacles||[];
      for(const i of list){const {label,plot}=i,focused=plot.id===this.activePlot||plot.id===this.selectedPlot;label.setScale(1/this.zoom);label.setPosition(i.x,i.y);const sx=this.root.x+i.x*this.zoom,sy=this.root.y+i.y*this.zoom,regular=plot.landmark&&plot.district==='market'&&this.zoom>.82&&(!this.mobile||(!this.inCase&&plot.asset==='com_1x1_LisieuxPlantCare'));label.setVisible((i.hover||focused||regular)&&sx>65&&sx<v.width-65&&sy>58&&sy<v.height-65);if(!label.visible)continue;
        const bounds=label.getBounds();if(bounds.y<safeTop)label.y+=(safeTop-bounds.y)/this.zoom;if(bounds.x<8)label.x+=(8-bounds.x)/this.zoom;else if(bounds.right>v.width-8)label.x-=(bounds.right-v.width+8)/this.zoom;
        for(let n=0;n<3;n++){const r=label.getBounds(),p=new Phaser.Geom.Rectangle(r.x-6,r.y-4,r.width+12,r.height+8);if(!used.some(o=>Phaser.Geom.Intersects.RectangleToRectangle(p,o))&&!obstacles.some(o=>p.x<o.x+o.width&&p.right>o.x&&p.y<o.y+o.height&&p.bottom>o.y)){used.push(p);break;}label.y+=(plot.status==='built'?-1:1)*20/this.zoom;if(n===2)label.setVisible(false);}
      }
    }
    makeTraffic(){this.roadPath=[[12,16],[23,16],[23,23],[12,23],[12,16]];const paths=[this.roadPath,[[7,12],[12,12],[12,28],[7,28],[7,12]],[[33,7],[37,7],[37,20],[33,20],[33,7]]];for(let i=0;i<7;i++){const sprite=this.add.image(0,0,`npc-${i%4}`).setOrigin(.5,1).setScale(.48);this.objects.add(sprite);this.people.push({sprite,t:i/7,phase:i,path:paths[i<5?0:i-4]});}for(let i=0;i<3;i++){const sprite=this.add.image(0,0,i%2?'car-b':'car-a').setOrigin(.5,.8).setScale(.46);this.objects.add(sprite);this.cars.push({sprite,t:i/3,path:paths[i===2?2:0]});}}
    roadPosition(t,path,offset=0){t=((t%1)+1)%1*(path.length-1);const i=Math.floor(t),f=t-i,a=path[i],b=path[i+1];return {...project(a[0]+(b[0]-a[0])*f+offset,a[1]+(b[1]-a[1])*f+offset),flip:b[0]<a[0]||b[1]>a[1]};}
    makeAvatar(){
      this.pelita=this.add.image(0,0,'pelita').setOrigin(.5,1).setScale(.48).setInteractive({useHandCursor:true});this.objects.add(this.pelita);
      this.pelita.on('pointerup',p=>{if(p.event?.target===this.game.canvas&&!this.drag?.moved)emit('town:avatar');});
      this.avatarTag=this.pixelLabel(0,0,'Pelita','#ffcf81');this.labelLayer.add(this.avatarTag);
      this.avatarSpeech=this.add.text(0,0,'',{fontFamily:'Inter',fontSize:'14px',color:'#f4f1ea',backgroundColor:'#1b2433',padding:{x:12,y:8},wordWrap:{width:220},lineSpacing:3}).setOrigin(.5,1).setVisible(false);this.labelLayer.add(this.avatarSpeech);
    }
    agentAction(event){
      if(!event||this.lastAgentEvent?.id===event.id)return;this.lastAgentEvent=event;
      const plot=this.state?.town.find(p=>p.id===event.plot_id)||this.state?.town.find(p=>p.funded_case_id===event.case_id);
      if(plot){this.avatarRoute=routeOnRoads(this.city,this.avatarPosition,plot);if(this.paused){this.avatarPosition=this.avatarRoute.at(-1)||this.avatarPosition;this.avatarRoute=[];}}
      this.showAvatarSpeech();
    }
    showAvatarSpeech(){this.avatarSpeech.setText(this.scale.height<450?t('Click me for saved agent activity.','Klik saya untuk aktiviti ejen tersimpan.'):(this.lastAgentEvent?.avatar_text||t('Click me to see saved agent activity.','Klik saya untuk melihat aktiviti ejen tersimpan.'))).setVisible(true);this.speechUntil=this.time.now+7500;}
    placeAvatarLabels(time,p){
      const sx=this.root.x+p.x*this.zoom,sy=this.root.y+p.y*this.zoom,v=this.viewport(),obstacles=this.hud?.obstacles||[];
      const hits=r=>obstacles.some(o=>r.x<o.x+o.width+6&&r.x+r.width>o.x-6&&r.y<o.y+o.height+6&&r.y+r.height>o.y-6);
      this.avatarTag.setScale(1/this.zoom).setPosition(p.x,p.y+36/this.zoom);
      const tag=this.avatarTag.getBounds();this.avatarTag.setVisible(!hits(tag)&&tag.x>0&&tag.right<v.width&&tag.y>0&&tag.bottom<v.height);
      const speech=this.avatarSpeech,w=speech.width,h=speech.height,cx=Phaser.Math.Clamp(sx,w/2+12,v.width-w/2-12);
      const above={x:cx,y:sy-this.pelita.height*.48*this.zoom-18},below={x:cx,y:sy+46+h};
      const choices=v.mobile?[below,above]:[above,below,{x:sx+w/2+50,y:sy},{x:sx-w/2-50,y:sy}];
      const spot=choices.find(c=>{const r={x:c.x-w/2,y:c.y-h,width:w,height:h};return r.x>=8&&r.x+w<=v.width-8&&r.y>=8&&r.y+h<=v.height-8&&!hits(r);});
      speech.setScale(1/this.zoom).setVisible(time<this.speechUntil&&!!spot);
      if(spot)speech.setPosition((spot.x-this.root.x)/this.zoom,(spot.y-this.root.y)/this.zoom);
    }
    update(time,delta){
      const dt=Math.min(delta,40);updateSky(this,dt);
      for(const a of this.people){if(!this.paused)a.t+=dt/105000;const p=this.roadPosition(a.t,a.path,.3);a.sprite.setPosition(p.x,p.y).setDepth(p.y+8).setFlipX(p.flip);if(!this.paused)a.sprite.setTexture(`npc-${a.phase%4}${Math.floor(time/330+a.phase)%2?'b':''}`);}
      for(const a of this.cars){if(!this.paused)a.t+=dt/50000;const p=this.roadPosition(a.t,a.path,-.1);a.sprite.setPosition(p.x,p.y).setDepth(p.y+6).setFlipX(p.flip);}
      if(!this.city)return;
      const tag=document.activeElement?.tagName;
      if(!['INPUT','TEXTAREA','SELECT'].includes(tag)&&!document.querySelector('dialog[open]')){const dx=(this.keys.left.isDown||this.keys.a.isDown?1:0)-(this.keys.right.isDown||this.keys.d.isDown?1:0),dy=(this.keys.up.isDown||this.keys.w.isDown?1:0)-(this.keys.down.isDown||this.keys.s.isDown?1:0);if(dx||dy){this.velocity={x:0,y:0};this.cameraGoal.x+=dx*dt*.6;this.cameraGoal.y+=dy*dt*.6;}}
      if(this.cameraGoal){
        if(!this.drag&&!this.paused){const decay=Math.exp(-dt/150);this.cameraGoal.x+=this.velocity.x*dt;this.cameraGoal.y+=this.velocity.y*dt;this.velocity.x*=decay;this.velocity.y*=decay;if(Math.abs(this.velocity.x)+Math.abs(this.velocity.y)<.01)this.velocity={x:0,y:0};}
        const alpha=this.paused?1:1-Math.exp(-dt/(this.drag?28:85)),g=this.cameraGoal;
        this.zoom+=(g.zoom-this.zoom)*alpha;this.root.setScale(this.zoom);this.root.x+=(g.x-this.root.x)*alpha;this.root.y+=(g.y-this.root.y)*alpha;this.captureFocus();
      }
      if(!this.paused&&this.avatarRoute.length){const goal=this.avatarRoute[0],p=this.avatarPosition,dx=goal.x-p.x,dy=goal.y-p.y,d=Math.hypot(dx,dy),step=dt*.004;if(d<step){this.avatarPosition={...goal};this.avatarRoute.shift();}else{p.x+=dx/d*step;p.y+=dy/d*step;}}
      const p=project(this.avatarPosition.x,this.avatarPosition.y);this.pelita.setPosition(p.x,p.y-2+(this.paused?0:Math.sin(time/260)*1.5)).setDepth(p.y+18);
      this.placeAvatarLabels(time,p);
      if(time-this.lastLabels>90){this.lastLabels=time;this.refreshLabels();}
      if(time-this.lastSort>120){this.lastSort=time;this.objects.sort('depth');}
      if(time-this.lastCull>180){this.lastCull=time;const w=this.scale.width,h=this.scale.height,chosen=this.buildings.get(this.activePlot||this.selectedPlot),chosenBounds=chosen?.getData('image')?.getBounds();for(const obj of [...this.scenery,...this.buildings.values()]){const x=this.root.x+obj.x*this.zoom,y=this.root.y+obj.y*this.zoom;obj.setVisible(x>-250&&x<w+250&&y>-100&&y<h+400);if(this.buildings.has(obj.getData('plot')?.id)){const occludes=chosenBounds&&obj!==chosen&&obj.depth>chosen.depth&&Phaser.Geom.Intersects.RectangleToRectangle(obj.getBounds(),chosenBounds);obj.setAlpha(occludes ? .3 : 1);}}}
      if(time-this.lastMini>180){this.lastMini=time;this.drawMinimap();}
    }

    makeMinimap(){this.mini=this.add.container(0,0).setDepth(100000);this.miniGraphic=this.add.graphics();this.mini.add(this.miniGraphic);this.mini.add([this.uiLabel(14,11,t('Town map','Peta bandar'),13,true),this.uiLabel(14,132,t('Click to travel · Scroll to zoom','Klik untuk bergerak · Tatal untuk zum'),10)]);}
    drawMinimap(){
      if(!this.city||!this.mini?.visible)return;const g=this.miniGraphic;g.clear();g.fillStyle(0x26324a);g.fillRoundedRect(0,0,196,155,8);g.lineStyle(1,0x52614f);g.strokeRoundedRect(0,0,196,155,8);const f=164/(this.city.size*64);this.miniScale=f;const cx=98,top=37;
      const env=this.city.landscape;g.fillStyle(0x91ce67);g.fillPoints(env.coast.map(([x,y])=>{const p=project(x,y);return {x:cx+p.x*f,y:top+p.y*f};}),true);
      g.fillStyle(0x405b4a);for(const [x,y] of env.road_tiles){const p=project(x,y);g.fillRect(cx+p.x*f,top+p.y*f,1,1);}
      g.fillStyle(0x67d3e9);g.fillPoints(env.lake.outline.map(([x,y])=>{const p=project(x,y);return {x:cx+p.x*f,y:top+p.y*f};}),true);
      for(const plot of this.state.town){const p=project(plot.x,plot.y);g.fillStyle(plot.status==='empty'?AMBER:plot.kind==='homes'?0xc5bc96:plot.kind==='offices'?0xf0dec1:plot.kind==='civic'?0x9cb86c:0xe29562);g.fillRect(cx+p.x*f-1,top+p.y*f-1,2,2);}
      const owl=project(this.avatarPosition.x,this.avatarPosition.y);g.fillStyle(0xffdc84);g.fillCircle(cx+owl.x*f,top+owl.y*f,3);
      const v=this.viewport(),a={x:-this.root.x/this.zoom,y:(68-this.root.y)/this.zoom},b={x:(v.width-this.root.x)/this.zoom,y:(v.height-100-this.root.y)/this.zoom};const x1=Phaser.Math.Clamp(cx+a.x*f,12,184),y1=Phaser.Math.Clamp(top+a.y*f,33,123),x2=Phaser.Math.Clamp(cx+b.x*f,12,184),y2=Phaser.Math.Clamp(top+b.y*f,33,123);g.lineStyle(1,0xffdc84);g.strokeRect(x1,y1,Math.max(0,x2-x1),Math.max(0,y2-y1));
    }
    overMinimap(p){return this.mini.visible&&p.x>=this.mini.x&&p.x<=this.mini.x+196&&p.y>=this.mini.y+30&&p.y<=this.mini.y+128;}
    minimapFocus(p){if(this.miniScale){const q=inverse((p.x-this.mini.x-98)/this.miniScale,(p.y-this.mini.y-37)/this.miniScale);this.focusAt(q.x,q.y,true);}}
    pulse(id){const plot=this.state?.town.find(p=>p.id===id);if(!plot)return;const end=project(plot.x,plot.y);if(this.paused){this.activePlot=id;this.refreshLabels();return;}const v=this.viewport(),pulse=this.add.rectangle((32-this.root.x)/this.zoom,((v.mobile?v.height-50:v.height-200)-this.root.y)/this.zoom,7/this.zoom,7/this.zoom,AMBER);this.labelLayer.add(pulse);this.tweens.add({targets:pulse,x:end.x,y:end.y-18,duration:850,ease:'Sine.easeOut',onComplete:()=>{pulse.destroy();this.reject(id,true);}});}
    reject(id){const g=this.buildings.get(id);if(!g)return;const s=g.getData('plot').footprint||1,flash=this.add.graphics();flash.fillStyle(AMBER,.6);flash.fillPoints([{x:0,y:-16*s},{x:32*s,y:0},{x:0,y:16*s},{x:-32*s,y:0}],true);g.addAt(flash,0);if(this.paused){flash.destroy();return;}this.tweens.add({targets:flash,alpha:0,duration:430,onComplete:()=>flash.destroy()});}
    grow(id){const g=this.buildings.get(id),image=g?.getData('image');if(!image)return;this.selectedPlot=id;this.speechUntil=0;const plot=g.getData('plot');this.focusAt(plot.x,plot.y,true,image.height*.55);this.refreshLabels();emit('town:animation-start',id);if(this.paused){emit('town:animation-end',id);return;}const target=image.scaleY;image.scaleY=.02;const sign=g.getData('sign');sign?.setFillStyle(0x5b5e49);this.tweens.add({targets:image,scaleY:target,duration:600,ease:'Back.easeOut',onComplete:()=>{sign?.setFillStyle(0xffd783);emit('town:animation-end',id);}});for(let i=0;i<7;i++){const dust=this.add.rectangle((i-3)*7,8,5,4,0xe5d5ac,.9);g.add(dust);this.tweens.add({targets:dust,x:dust.x+(i-3)*4,y:-12-(i%3)*7,alpha:0,duration:550,onComplete:()=>dust.destroy()});}}
  }
  const el=document.querySelector('#town-canvas');new Phaser.Game({type:Phaser.CANVAS,parent:el,backgroundColor:'#a8dcf1',pixelArt:true,roundPixels:true,antialias:false,fps:{target:60,forceSetTimeOut:true},scale:{mode:Phaser.Scale.RESIZE,width:el.clientWidth,height:el.clientHeight},scene:City,audio:{noAudio:true},banner:false});
}
