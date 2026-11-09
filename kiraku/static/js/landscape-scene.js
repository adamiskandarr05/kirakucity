const iso=(x,y)=>({x:(x-y)*32,y:(x+y)*16});
export const noise=(x,y,s=0)=>{let n=Math.imul((x*173+y*7919+s*104729)|0,1597334677);n=Math.imul(n^(n>>>16),2246822519);return ((n^(n>>>13))>>>0)/4294967296;};
const water=(lake,x,y,margin=0)=>((x-lake.x)/(lake.rx+margin))**2+((y-lake.y)/(lake.ry+margin))**2<1;

export function makeSky(scene){
  if(!scene.textures.exists('kiraku-cloud')){
    const texture=scene.textures.createCanvas('kiraku-cloud',106,46),c=texture.context;
    c.fillStyle='#d9edf6';for(const [x,y,rx,ry] of [[24,30,23,12],[53,26,32,17],[81,31,23,11]]){c.beginPath();c.ellipse(x,y,rx,ry,0,0,Math.PI*2);c.fill();}
    c.fillStyle='#f6fcff';for(const [x,y,rx,ry] of [[22,25,20,10],[43,19,21,17],[65,21,22,16],[83,27,19,10]]){c.beginPath();c.ellipse(x,y,rx,ry,0,0,Math.PI*2);c.fill();}texture.refresh();
  }
  scene.sky=scene.add.container(0,0).setDepth(-10000);scene.clouds=[];
  for(let i=0;i<9;i++){const sprite=scene.add.image(0,0,'kiraku-cloud').setScale(1.7+noise(i,4)*2.6).setAlpha(.65+noise(i,7)*.3);scene.sky.add(sprite);scene.clouds.push({sprite,x:noise(i,1),y:noise(i,2),speed:.000002+noise(i,3)*.000003});}
}

export function updateSky(scene,delta){
  const w=scene.scale.width,h=scene.scale.height;
  for(const c of scene.clouds){if(!scene.paused)c.x=(c.x+delta*c.speed)%1;c.sprite.setPosition(c.x*(w+500)-250+(scene.root?.x||0)*.008,c.y*h+(scene.root?.y||0)*.004);}
}

export function drawLandscape(scene){
  const env=scene.city.landscape,size=scene.city.size,w=size*64+128,h=size*32+160,ox=w/2,oy=64;
  const texture=scene.textures.createCanvas('kiraku-city-ground',w,h),ctx=texture.context;ctx.imageSmoothingEnabled=false;
  const point=(x,y)=>{const p=iso(x,y);return {x:p.x+ox,y:p.y+oy};};
  const poly=(pairs,color,offset=0)=>{ctx.fillStyle=color;ctx.beginPath();pairs.forEach(([x,y],i)=>{const p=point(x,y);i?ctx.lineTo(p.x,p.y+offset):ctx.moveTo(p.x,p.y+offset);});ctx.closePath();ctx.fill();};
  poly(env.coast,'#947954',18);poly(env.coast,'#b2935e',10);poly(env.coast,'#8acb66');
  const grass=scene.textures.get('terrain_grass').getSourceImage(),road=scene.textures.get('road_paved').getSourceImage(),roads=new Set(env.road_tiles.map(([x,y])=>`${x},${y}`));scene.roadTiles=roads;
  ctx.save();ctx.beginPath();env.coast.forEach(([x,y],i)=>{const p=point(x,y);i?ctx.lineTo(p.x,p.y):ctx.moveTo(p.x,p.y);});ctx.closePath();ctx.clip();
  for(const [x,y] of env.land_tiles){const p=point(x,y);ctx.filter='brightness(1.48) saturate(1.6)';ctx.drawImage(grass,(13+Math.floor(noise(x,y)*3))*32,0,32,23,p.x-32,p.y-30,64,46);ctx.filter='none';
    if(roads.has(`${x},${y}`)){const vertical=roads.has(`${x},${y+1}`)||roads.has(`${x},${y-1}`),horizontal=roads.has(`${x+1},${y}`)||roads.has(`${x-1},${y}`);ctx.drawImage(road,(vertical&&horizontal?0:vertical?10:5)*32,0,32,23,p.x-32,p.y-30,64,46);}
    else if(!water(env.lake,x,y,1)&&noise(x,y,5)>.62){ctx.fillStyle=noise(x,y,7)>.5?'#c9e782':'#74b854';for(let i=0;i<4;i++)ctx.fillRect(p.x-18+noise(x+i,y,6)*36,p.y-9+noise(x,y+i,8)*14,2,1);}
  }
  ctx.restore();
  // Flat bands and irregular banks retain the pixel-art look without a gradient.
  poly(env.lake.outline,'#e7d69d');
  const lakeOutline=env.lake.outline.map(([x,y])=>[env.lake.x+(x-env.lake.x)*.96,env.lake.y+(y-env.lake.y)*.94]);poly(lakeOutline,'#6dd9e8');
  poly(lakeOutline.map(([x,y])=>[env.lake.x+(x-env.lake.x)*.77,env.lake.y+(y-env.lake.y)*.72]),'#47badb');
  for(let i=0;i<65;i++){const x=env.lake.x+(noise(i,12)-.5)*env.lake.rx*1.65,y=env.lake.y+(noise(i,18)-.5)*env.lake.ry*1.65;if(!water(env.lake,x,y,-.5))continue;const p=point(x,y);ctx.fillStyle=i%3?'#a4e5eb':'#c8f4f0';ctx.fillRect(p.x,p.y,5+noise(i,21)*13,1);}
  // A timber jetty and lily pads give the water an identifiable destination.
  poly([[25.6,14.5],[26.3,14.5],[26.3,12.4],[25.6,12.4]],'#a67e4f');
  for(let i=0;i<12;i++){const a=point(25.6,12.4+i*.18),b=point(26.3,12.4+i*.18);ctx.strokeStyle='#d2b47d';ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke();}
  for(let i=0;i<8;i++){const p=point(22.4+noise(i,32)*1.3,9+noise(i,42)*1.6);ctx.fillStyle='#68a867';ctx.fillRect(p.x,p.y,7,3);if(i%3===0){ctx.fillStyle='#f7d7cf';ctx.fillRect(p.x+2,p.y-2,3,2);}}
  texture.refresh();scene.floor=scene.add.image(-ox,-oy,'kiraku-city-ground').setOrigin(0);scene.root.addAt(scene.floor,0);
}

export function drawNature(scene,art){
  const env=scene.city.landscape,plots=scene.state.town;
  for(const [x,y] of env.land_tiles){
    if(scene.roadTiles.has(`${x},${y}`)||water(env.lake,x,y,1.1))continue;
    const clustered=(Math.sin(x*.57)+Math.cos(y*.69)+Math.sin((x+y)*.28))*.12;
    if(noise(x,y,11)<.76-clustered)continue;
    if(plots.some(p=>Math.abs(p.x-x)<(p.footprint||1)/2+1&&Math.abs(p.y-y)<(p.footprint||1)/2+1))continue;
    const p=iso(x+(noise(x,y,2)-.5)*.5,y+(noise(x,y,3)-.5)*.5),key=['tree_Oak_light','tree_Willow_light','tree_birch_light'][Math.floor(noise(x,y,17)*3)],a=art.get(key);
    const tree=scene.add.image(p.x,p.y+14,key,Math.floor(noise(x,y,19)*a.tiles.count)).setOrigin(.5,1).setScale(1.65+noise(x,y,9)*.65).setDepth(p.y+10);scene.objects.add(tree);scene.scenery.push(tree);
    if(noise(x,y,22)>.6){const flowers=scene.add.graphics().setPosition(p.x+13,p.y+14).setDepth(p.y+11);for(let i=0;i<4;i++){flowers.fillStyle([0xffd68a,0xf6d3bc,0xfff4cf][i%3]);flowers.fillRect(i*3,Math.sin(i)*3,2,2);}scene.objects.add(flowers);scene.scenery.push(flowers);}
  }
  for(const [x,y] of env.road_tiles){if(noise(x,y,27)<.96||water(env.lake,x,y,1))continue;const p=iso(x+.38,y+.38),lamp=scene.add.image(p.x,p.y+16,'BD_1x1_LightPole_kt',Math.floor(noise(x,y,29)*4)).setOrigin(.5,1).setScale(2).setDepth(p.y+10);scene.objects.add(lamp);scene.scenery.push(lamp);}
}

export function routeOnRoads(city,start,plot){
  const tiles=city.landscape.road_tiles,key=([x,y])=>`${x},${y}`,all=new Set(tiles.map(key));
  const nearest=point=>tiles.reduce((a,b)=>Math.hypot(a[0]-point.x,a[1]-point.y)<Math.hypot(b[0]-point.x,b[1]-point.y)?a:b);
  const from=nearest(start),to=nearest(plot),queue=[from],parents=new Map([[key(from),null]]);let best=from;
  for(let i=0;i<queue.length;i++){const node=queue[i];if(Math.hypot(node[0]-plot.x,node[1]-plot.y)<Math.hypot(best[0]-plot.x,best[1]-plot.y))best=node;if(key(node)===key(to)){best=node;break;}for(const next of [[node[0]+1,node[1]],[node[0]-1,node[1]],[node[0],node[1]+1],[node[0],node[1]-1]]){const k=key(next);if(all.has(k)&&!parents.has(k)){parents.set(k,node);queue.push(next);}}}
  const path=[];for(let node=best;node;node=parents.get(key(node)))path.push({x:node[0],y:node[1]});return path.reverse();
}
