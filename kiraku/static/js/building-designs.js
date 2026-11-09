// Original code-drawn Kiraku upgrade designs. The plot footprint never expands.
const palettes={shops:['#f0dbab','#c3a777','#2b897c','#ce7656'],stands:['#d1e4e8','#96b8c6','#35628d','#f2bc4e'],stalls:['#efc299','#bf9270','#c86548','#f8d272'],parks:['#e7d6ac','#b6bb8b','#4c8c66','#f3da8c']};
export function buildingDesign(scene,plot){
  const a=plot.appearance;if(!a||a.style!=='kiraku-upgrade')return {key:plot.asset,frame:plot.frame||0,height:null};
  if(scene.textures.exists(a.key))return {key:a.key,frame:0,height:a.height};
  const size=plot.footprint||1,w=size*32+8,h=a.height,cx=w/2,base=h-5,depth=size===2?11:7,half=size===2?21:14,body=a.floors*8;
  const texture=scene.textures.createCanvas(a.key,w,h),ctx=texture.context;ctx.imageSmoothingEnabled=false;
  const [light,dark,roof,accent]=palettes[plot.kind]||palettes.shops;
  const poly=(points,color)=>{ctx.fillStyle=color;ctx.beginPath();points.forEach(([x,y],i)=>i?ctx.lineTo(x,y):ctx.moveTo(x,y));ctx.closePath();ctx.fill();};
  poly([[cx,base],[4,base-size*8],[cx,base-size*16],[w-4,base-size*8]],plot.kind==='parks'?'#a5cf6b':'#d9d6bd');
  // Pavement edging and terrace planting make later stages read as new designs.
  poly([[cx-half,base-depth],[cx,base],[cx,base-body],[cx-half,base-depth-body]],light);
  poly([[cx,base],[cx+half,base-depth],[cx+half,base-depth-body],[cx,base-body]],dark);
  for(let floor=0;floor<a.floors;floor++){
    const y=base-floor*8;
    poly([[cx-half,y-depth],[cx,y],[cx,y-1],[cx-half,y-depth-1]],'#998968');
    poly([[cx,y],[cx+half,y-depth],[cx+half,y-depth-1],[cx,y-1]],'#7c816e');
    for(let col=0;col<3;col++){
      const x=cx-half+3+col*(half-4)/3,wy=y-depth+(x-(cx-half))*depth/half-6;
      poly([[x,wy],[x+3,wy+1.5],[x+3,wy+5],[x,wy+3.5]],floor===0?accent:'#4a7779');
      const rx=cx+3+col*(half-4)/3,ry=y-(rx-cx)*depth/half-6;
      poly([[rx,ry],[rx+3,ry-1.5],[rx+3,ry+2],[rx,ry+3.5]],floor===0?accent:'#355966');
      ctx.fillStyle='#c6e6d0';ctx.fillRect(Math.round(x),Math.round(wy),1,2);
    }
  }
  const top=base-body;
  poly([[cx-half,top-depth],[cx,top-depth*2],[cx+half,top-depth],[cx,top]],roof);
  poly([[cx-half,top-depth],[cx,top],[cx,top+2],[cx-half,top-depth+2]],'#f1e5bc');
  poly([[cx,top],[cx+half,top-depth],[cx+half,top-depth+2],[cx,top+2]],'#b1bc9a');
  // Category-specific frontage: shop awning, taxi canopy, market stripes, park vines.
  if(plot.kind==='shops'||plot.kind==='stalls'){
    const y=base-8;poly([[cx-half-1,y-depth],[cx,y+1],[cx+1,y-3],[cx-half,y-depth-4]],accent);
    for(let n=0;n<4;n++)ctx.fillStyle=n%2?'#f7edce':roof,ctx.fillRect(cx-half+n*3,Math.round(y-depth+n*1.5-2),2,3);
  }else if(plot.kind==='stands'){
    poly([[cx-half-2,base-depth-8],[cx-1,base-8],[cx+2,base-13],[cx-half,base-depth-13]],'#efbd50');
    ctx.fillStyle='#273e53';ctx.fillRect(cx-8,base-17,9,3);
  }else{
    for(let floor=1;floor<a.floors;floor++){ctx.fillStyle=floor%2?'#5b9f56':'#6dbd66';ctx.fillRect(cx-half+1,base-depth-floor*8-2,4,3);ctx.fillRect(cx+half-5,base-depth-floor*8-2,4,3);}
  }
  if(a.level>=2){ctx.fillStyle='#735c3c';ctx.fillRect(cx-7,top-depth-4,5,3);ctx.fillStyle='#8ec26b';ctx.fillRect(cx-7,top-depth-7,5,4);}
  if(a.level>=3){poly([[cx+1,top-depth-5],[cx+7,top-depth-8],[cx+10,top-depth-5],[cx+4,top-depth-2]],'#547f99');ctx.fillStyle='#a6d3dc';ctx.fillRect(cx+4,top-depth-6,3,1);}
  if(a.level>=4){ctx.fillStyle='#e8dcb8';ctx.fillRect(cx-1,top-depth*2-8,2,9);ctx.fillStyle=accent;ctx.fillRect(cx+1,top-depth*2-8,6,3);}
  if(a.level>=5){ctx.fillStyle='#f2ce68';ctx.fillRect(cx-3,top-depth-11,3,3);ctx.fillRect(cx+1,top-depth-12,3,3);}
  texture.refresh();return {key:a.key,frame:0,height:h};
}
