import {emit} from './bus.js';
let scheduled=false,last='';
export function layoutHUD(){
  if(scheduled)return;scheduled=true;
  requestAnimationFrame(()=>{
    scheduled=false;const stage=document.querySelector('#town-screen');if(!stage||stage.hidden)return;
    const bounds=stage.getBoundingClientRect(),mobile=bounds.width<=760,incase=stage.classList.contains('in-case');
    const rect=selector=>{const el=stage.querySelector(selector);if(!el||!el.getClientRects().length)return null;const r=el.getBoundingClientRect();return {x:r.left-bounds.left,y:r.top-bounds.top,width:r.width,height:r.height,right:r.right-bounds.left,bottom:r.bottom-bounds.top};};
    const heading=rect('.town-heading'),bottom=rect('.town-bottom');
    stage.style.setProperty('--hud-top',`${Math.ceil(heading.bottom+12)}px`);
    const dockTop=bottom?.y??bounds.height-16;
    stage.style.setProperty('--legend-bottom',`${Math.ceil(bounds.height-dockTop+10)}px`);
    stage.style.setProperty('--district-height',`${Math.max(44,dockTop-80-heading.bottom)}px`);
    const tools=rect('.map-tools'),nav=rect('.district-navigation'),legend=rect('.map-legend');
    const mini={x:bounds.width-220,y:tools.bottom+12,width:196,height:155};
    mini.visible=!mobile&&!incase&&mini.y+mini.height<dockTop-12;
    const obstacles=['.town-heading>div:first-child','.town-stats','.district-navigation','.map-tools','.town-bottom','.map-legend','.trace-panel'].map(rect).filter(Boolean);
    if(mini.visible)obstacles.push(mini);
    const free={left:mobile?12:(nav?.right??12)+16,right:mobile?bounds.width-12:Math.max(bounds.width-400,(tools?.x??bounds.width)-16),top:heading.bottom+16,bottom:incase&&mobile?bounds.height*.46-128:dockTop-40};
    const data={mini,obstacles,free};window.__kirakuHUD=data;const key=JSON.stringify(data);if(key!==last){last=key;emit('town:hud',data);}
  });
}
const observer=new ResizeObserver(layoutHUD);
for(const selector of ['#town-screen','.town-heading','.town-bottom','.district-navigation','.map-tools']){const el=document.querySelector(selector);if(el)observer.observe(el);}
new MutationObserver(layoutHUD).observe(document.querySelector('#town-screen'),{attributes:true,attributeFilter:['class','hidden']});
window.addEventListener('resize',layoutHUD);

