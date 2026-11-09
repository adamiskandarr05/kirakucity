import {$,api,esc,toast,time,kinds,art} from './api.js';
import {emit,on} from './bus.js';
import {createTown} from './city-scene.js';
import {language,t,pair,pupilName,plotName} from './i18n.js';
import {layoutHUD} from './hud-layout.js';

let pid=null, state=null, currentCase=null, view='brief', events=[],cursor=0, ready=false,busy=false;
const hintLevels=new Map(), hintTexts=new Map();
const panel=$('#case-panel'), town=$('#town-screen');

function profileCard(p,index){
  return `<article class="pupil-card"><div class="pupil-card-head"><span class="avatar">${esc(p.name.slice(-1))}</span><div><h2>${esc(pupilName(p.name))}</h2><span class="profile-kind">${[t('A fresh perspective','Pandangan baharu'),t('A head for patterns','Cekap mengenal pola'),t('A growing curiosity','Rasa ingin tahu')][index]}</span></div></div><p class="profile-description">${esc(pair(p.description))}</p><div class="mastery-mini">${p.mastery.map(m=>`<div class="mastery-row"><div class="mastery-label"><span>${esc(m[language==='ms'?'title_ms':'title_en'])}</span><span>${m.score}%</span></div><div class="mastery-bar" role="meter" aria-label="${esc(m[language==='ms'?'title_ms':'title_en'])} mastery" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${m.score}"><i style="width:${m.score}%"></i></div></div>`).join('')}</div><button class="btn secondary" data-pupil="${esc(p.id)}">${t('Choose','Pilih')} ${esc(pupilName(p.name))} <span aria-hidden="true">→</span></button></article>`;
}
async function loadPupils(){try{const data=await api('/api/pupils');$('#pupil-cards').innerHTML=data.pupils.map(profileCard).join('');}catch(error){toast(error.message);$('#pupil-cards').innerHTML=`<p>${t('Planner profiles could not load. Refresh to try again.','Profil perancang tidak dapat dimuatkan. Muat semula untuk mencuba lagi.')}</p>`;}}
async function start(pidValue){
  if(busy)return;busy=true;
  try{await window.kirakuEngineReady;const data=await api('/api/session/start',{pupil_id:pidValue});pid=pidValue;state=data.state;events=[];cursor=0;currentCase=null;localStorage.setItem('kiraku-pupil',pid);$('#pupil-select').hidden=true;town.hidden=false;$('#switch-pupil').hidden=false;$('#header-avatar').textContent=state.pupil.name.slice(-1);$('#header-pupil').textContent=pupilName(state.pupil.name);createTown();renderState();await refreshState();await refreshEvents();const savedView=JSON.parse(sessionStorage.getItem('kiraku-case-view')||'null');if(!state.active_case&&savedView?.pid===pid&&savedView.view==='result'&&savedView.id){try{state.active_case=(await api(`/api/case/${savedView.id}/why`)).case;}catch{}}if(state.active_case){currentCase=state.active_case;view=currentCase.steps.some(s=>s.last_result)?'working':'brief';const previousOpen=restoreDrafts();if(previousOpen===false||new URLSearchParams(location.search).get('city')==='1')closePanel();else openPanel();}else{closePanel();}}
  catch(error){toast(error.message);}finally{busy=false;}
}
function renderState(){
  if(!state)return;
  $('#town-stats').innerHTML=Object.entries(state.counts).map(([kind,count])=>`<div class="town-stat"><img class="stat-sprite" src="${art(kind)}" alt=""><div><strong>${count}</strong><span>${kinds[kind]}</span></div></div>`).join('');
  $('#town-subtitle').textContent=`${state.city_summary.buildings} ${t('buildings','bangunan')} · ${state.completed_cases} ${t('cases completed','kes selesai')} · ${state.city_summary.districts} ${t('districts','kawasan')}`;
  $('#district-nav').innerHTML=state.city.districts.map((d,i)=>`<button data-district="${d.id}" aria-pressed="${i===0}"><span class="district-icon" aria-hidden="true">${['▦','⌂','▥','♧'][i]}</span><span>${esc(language==='ms'?d.name:d.english)}</span><span aria-hidden="true">↗</span></button>`).join('');
  $('#building-list').innerHTML=[...state.town].sort((a,b)=>b.landmark-a.landmark).map(p=>`<button data-building="${p.id}">${esc(plotName(p))}<span>${p.waiting?t('Waiting','Menunggu'):p.status==='built'?t('Open','Dibuka'):t('Empty','Kosong')}</span></button>`).join('');
  if(ready)emit('town:state',state);
  $('#pelita-town').textContent=state.completed_cases?t('Your town has saved progress. Click me in town to see the agents at work.','Bandar anda mempunyai kemajuan tersimpan. Klik saya di bandar untuk melihat aktiviti ejen.'):t('A new plan is waiting. Find me in town to see the agents at work.','Pelan baharu menanti. Cari saya di bandar untuk melihat aktiviti ejen.');
}
async function refreshState(){if(!pid)return;state=await api(`/api/pupil/${pid}/state`);renderState();}
async function refreshEvents(){
  if(!pid)return;
  const data=await api(`/api/events?since=${cursor}`);
  const initial=cursor===0;const known=new Set(events.map(e=>e.id));
  const fresh=data.events.filter(e=>!known.has(e.id));events.push(...fresh);events.sort((a,b)=>b.id-a.id);cursor=Math.max(cursor,...fresh.map(e=>e.id));renderTrace();renderActivity();if(ready&&fresh.length){const action=initial?fresh.sort((a,b)=>b.id-a.id)[0]:fresh.sort((a,b)=>a.id-b.id).at(-1);emit('town:agent-action',{...action,plot_id:currentCase?.plot_id||state.town.find(p=>p.funded_case_id===action.case_id)?.id});}
}
function renderTrace(){
  const list=events.filter(e=>e.case_id===currentCase?.id);
  $('#trace-count').textContent=`${list.length} ${t('decisions','keputusan')}`;
  $('#trace-list').innerHTML=list.map(e=>`<details class="trace-entry ${e.agent==='Feedback'&&!e.raw.correct?'rejected':''}" data-event-id="${e.id}"><summary><div class="trace-meta"><strong>${esc(e.display_agent||e.agent)}</strong><time datetime="${esc(e.timestamp)}">${esc(time(e.timestamp))}</time></div><p class="trace-decision">${esc(e.display_decision||e.decision)}</p><p class="trace-inputs">${esc(e.display_inputs||e.input_summary)}</p></summary><pre>${t('Saved evidence','Bukti tersimpan')}
${esc(JSON.stringify(e.raw,null,2))}</pre></details>`).join('');
}
function openPanel(){panel.hidden=false;town.classList.add('in-case');$('#trace-panel').hidden=false;$('#building-detail').hidden=true;emit('town:case',currentCase);renderCase();renderTrace();}
function closePanel(){panel.hidden=true;town.classList.remove('in-case');$('#trace-panel').hidden=true;emit('town:case',null);$('#next-case').innerHTML=`${currentCase?t('Continue case','Sambung kes'):t('Next case','Kes seterusnya')} <span>→</span>`;}
const heading=()=>`<header class="case-head"><span><i class="status-dot"></i><span class="case-kind">${esc(kinds[currentCase.kind])}</span> · ${esc(currentCase.street)}</span><button id="close-case" aria-label="${t('Minimise case','Kecilkan kes')}">×</button></header>`;
const givens=()=>`<table class="givens"><thead><tr><th>${t('Given','Diberi')}</th><th>${t('Value','Nilai')}</th><th>Unit</th></tr></thead><tbody>${currentCase.given_rows.map(([label,value,unit])=>`<tr><td>${esc(label)}</td><td>${esc(value)}</td><td>${esc(unit)}</td></tr>`).join('')}</tbody></table>`;
function renderCase(){
  const c=currentCase;if(!c)return;
  const scrolled=$('.case-scroll',panel)?.scrollTop||0;
  if(view==='brief'){
    panel.innerHTML=heading()+`<div class="case-scroll"><div class="case-kicker"><i></i> ${t('Town case · Level','Kes bandar · Tahap')} ${c.level}</div><h2>${esc(c.title)}</h2><p class="case-brief">${esc(c.brief)}</p>${givens()}<p class="rounding">${esc(c.rounding)}</p><div class="case-pelita"><img src="/static/assets/pelita.png" alt="Pelita"><p>${esc(c.narration.text)}</p></div></div><footer class="case-footer"><button class="btn primary" id="start-working">${t('Start calculating','Mula kira')}<span>→</span></button><p>${c.steps.length} ${t('linked steps · Take your time','langkah berangkai · Ikut rentak anda')}</p></footer>`;
  }else if(view==='working'){
    const done=c.steps.filter(s=>s.verified).length;
    panel.innerHTML=heading()+`<div class="case-scroll"><div class="progress-strip" aria-label="${done}/${c.steps.length} ${t('steps verified','langkah disahkan')}">${c.steps.map(s=>`<i class="${s.verified?'done':''}"></i>`).join('')}</div><div class="case-kicker"><i></i> ${t('Your working','Pengiraan anda')}</div><h2>${esc(c.title)}</h2><details class="brief-disclosure"><summary>${t('View brief & givens','Lihat butiran kes')}</summary><p class="case-brief">${esc(c.brief)}</p>${givens()}<p class="rounding">${esc(c.rounding)}</p></details><ol class="step-list">${c.steps.map((s,i)=>{
      const locked=c.steps.slice(0,i).some(p=>!p.verified),result=s.last_result;
      const labels=[s.label];
      return `<li class="working-step ${s.verified?'verified':locked?'locked':''}" data-step="${i}"><span class="step-number">${s.verified?'✓':i+1}</span><h3><label for="answer-${i}">${esc(labels[0])}<span>${esc(labels[1]||'')}</span></label></h3>${locked?`<p class="locked-label"><span aria-hidden="true">▣</span> ${t('Verify the previous step to continue.','Sahkan langkah sebelumnya untuk meneruskan.')}</p>`:s.verified?`<p class="step-verified-value">${esc(result.value.includes('/')?Number(result.value.split('/')[0])/Number(result.value.split('/')[1]):result.value)} <small>${esc(s.unit)}</small></p><p class="step-feedback good">✓ ${esc(result.solution)}</p>`:`<form class="answer-form" data-index="${i}"><div class="answer-row"><div class="input-wrap"><input id="answer-${i}" name="value" type="text" inputmode="decimal" autocomplete="off" required aria-describedby="step-help-${i}" ${result&&!result.correct?'aria-invalid="true"':''} value="${esc(s.draft??'')}"><span>${esc(s.unit)}</span></div><button class="check-btn" type="submit">${t('Check','Semak')}</button></div><p id="step-help-${i}" class="rounding">${t('2 decimal places','2 tempat perpuluhan')} · ${esc(s.unit)}</p>${result?`<p class="step-feedback" role="status">${esc(result.message)}</p>`:''}<button class="hint-btn" type="button" data-hint="${i}">✧ ${t('Hint','Petunjuk')} ${Math.min(3,(hintLevels.get(i)||0)+1)} ${t('of','daripada')} 3</button>${hintTexts.has(i)?`<p class="hint-text">${esc(hintTexts.get(i))}</p>`:''}</form>`}</li>`;
    }).join('')}</ol></div><footer class="case-footer"><button class="btn ${done===c.steps.length?'primary':'secondary'}" id="finish-case" ${done<c.steps.length?'disabled':''}>${t('Finish case','Siapkan kes')}<span>✓</span></button><p>${done}/${c.steps.length} ${t('steps verified','langkah disahkan')} · ${done===c.steps.length?t('Your plan is ready','Pelan anda sedia'):t('Each step opens the next','Selesaikan mengikut urutan')}</p></footer>`;
  }else if(view==='result'){
    const r=c.result;
    panel.innerHTML=heading()+`<div class="case-scroll"><div class="result-seal ${r.branch==='held'?'held':''}">${r.effect?'✓':'◇'}</div><div class="case-kicker">${t('Case complete','Kes selesai')}</div><h2>${r.effect?t('A new beginning.','Satu lagi permulaan.'):t('Calculations verified.','Pengiraan disahkan.')}</h2><p class="result-outcome">${esc(r.outcome)}</p>${r.effect?`<div class="result-effect">+1 ${esc(kinds[r.effect.kind])} · ${t('Ready to open','Sedia dibuka')}</div>`:''}<ul class="result-marks">${r.marks.map(m=>`<li>✓ ${esc(m.label)}</li>`).join('')}</ul><div class="result-review"><h3><img src="/static/assets/pelita.png" alt="">${t('Pelita’s review','Ulasan Pelita')}</h3><p>${esc(r.review.text)}</p><div class="review-line"><strong>${t('Strongest step','Langkah terkuat')}</strong>${esc(r.review.strongest)}</div><div class="review-line"><strong>${t('To revisit','Untuk diingati')}</strong>${esc(r.review.revisit)}</div><div class="review-line"><strong>${t('Town news','Berita bandar')}</strong>${esc(r.review.news)}</div></div></div><footer class="case-footer"><button class="btn primary" id="return-town">${t('Return to town','Kembali ke bandar')}<span>↗</span></button><p>${r.effect?t('Watch your plan become part of the town.','Lihat pelan anda menjadi sebahagian bandar.'):t('The town is ready for your next plan.','Bandar sedia untuk pelan seterusnya.')}</p></footer>`;
  }
  if(view==='working')$('.case-scroll',panel).scrollTop=scrolled;
}
async function nextCase(){
  if(currentCase){openPanel();return;}if(busy)return;busy=true;$('#next-case').disabled=true;
  try{const data=await api('/api/case/next',{});currentCase=data.case;hintLevels.clear();hintTexts.clear();view=currentCase.steps.some(s=>s.last_result)?'working':'brief';openPanel();await refreshEvents();emit('town:pulse',currentCase.plot_id);}
  catch(error){toast(error.message);}finally{busy=false;$('#next-case').disabled=false;}
}
panel.addEventListener('input',event=>{if(event.target.name==='value'){const index=Number(event.target.closest('form').dataset.index);currentCase.steps[index].draft=event.target.value;}});
panel.addEventListener('submit',async event=>{
  if(!event.target.matches('.answer-form'))return;event.preventDefault();if(busy)return;
  const form=event.target,index=Number(form.dataset.index),input=$('input',form);busy=true;$('button[type=submit]',form).disabled=true;
  try{const result=await api('/api/case/step',{case_id:currentCase.id,step_index:index,value:input.value,submission_id:crypto.randomUUID()});const step=currentCase.steps[index];step.last_result=result;step.verified=result.correct;renderCase();await refreshState();await refreshEvents();if(!result.correct)emit('town:rejected',currentCase.plot_id);const next=$(`#answer-${result.correct?index+1:index}`);if(next){next.focus({preventScroll:true});if(result.correct)next.closest('.working-step').scrollIntoView({block:'nearest',behavior:'instant'});}}
  catch(error){toast(error.message);}finally{busy=false;const button=$(`.answer-form[data-index="${index}"] button[type=submit]`);if(button)button.disabled=false;}
});
panel.addEventListener('click',async event=>{
  const button=event.target.closest('button');if(!button)return;
  if(button.id==='close-case'){if(view==='result'){await returnTown();}else closePanel();return;}
  if(button.id==='start-working'){view='working';renderCase();$('#answer-0')?.focus({preventScroll:true});return;}
  if(button.dataset.hint!==undefined){if(busy)return;busy=true;const index=Number(button.dataset.hint),level=Math.min(3,(hintLevels.get(index)||0)+1);try{const result=await api('/api/case/hint',{case_id:currentCase.id,step_index:index,level});hintLevels.set(index,level);hintTexts.set(index,result.text);renderCase();await refreshEvents();}catch(error){toast(error.message);}finally{busy=false;}return;}
  if(button.id==='finish-case'){if(busy)return;busy=true;button.disabled=true;try{currentCase.result=await api('/api/case/finish',{case_id:currentCase.id});view='result';renderCase();await refreshEvents();}catch(error){toast(error.message);button.disabled=false;}finally{busy=false;}return;}
  if(button.id==='return-town')await returnTown();
});
async function returnTown(){
  if(busy)return;busy=true;try{const effect=currentCase?.result?.effect;currentCase=null;closePanel();await refreshState();if(effect){emit('town:grow',effect.plot_id);toast(`+1 ${kinds[effect.kind]} · ${t('Your town has a new beginning.','Permulaan baharu untuk bandar anda.')}`);}else toast(t('Your calculations are saved. The project is waiting for its target.','Pengiraan anda disimpan. Projek menunggu sasarannya.'));}catch(error){toast(error.message);}finally{busy=false;}
}
async function buildingDetail(plot){
  $('#building-list').hidden=true;$('#building-list-toggle').setAttribute('aria-expanded','false');
  if(currentCase&&plot.id===currentCase.plot_id){openPanel();return;}
  const box=$('#building-detail');box.innerHTML=`<button class="detail-close" aria-label="${t('Close building details','Tutup butiran bangunan')}">×</button><img src="${art(plot.kind,plot.asset)}" alt=""><h2>${esc(plotName(plot))}</h2><p>${esc(plot.street)}</p><p>${plot.status==='built'?t('Open','Dibuka'):plot.waiting?t('Waiting for a calculation to be revisited.','Menunggu pengiraan disemak semula.'):t('Empty · A new plan can bring this plot to life.','Kosong · Pelan baharu boleh menghidupkan lot ini.')}</p><div id="funding-details"></div>`;box.hidden=false;
  $('.detail-close',box).onclick=()=>box.hidden=true;
  if(plot.funded_case_id){try{const data=await api(`/api/case/${plot.funded_case_id}/why`);if(!box.hidden)$('#funding-details').innerHTML=data.case.steps.filter(s=>s.verified).map(s=>`<p class="calculation">✓ ${esc(s.solution)}</p>`).join('');}catch(error){toast(error.message);}}
  else if(plot.status==='built')$('#funding-details').innerHTML=`<p>${t('This building belongs to the starting town. No pupil calculation has funded an upgrade yet.','Bangunan ini sebahagian bandar asal. Belum ada naik taraf yang dibiayai pengiraan murid.')}</p>`;
}
$('#pupil-cards').addEventListener('click',event=>{const button=event.target.closest('[data-pupil]');if(button)start(button.dataset.pupil);});
$('#switch-pupil').onclick=()=>{currentCase=null;pid=null;localStorage.removeItem('kiraku-pupil');town.hidden=true;$('#pupil-select').hidden=false;$('#switch-pupil').hidden=true;};
$('#next-case').onclick=nextCase;
$('#zoom-in').onclick=()=>emit('town:zoom',1.15);$('#zoom-out').onclick=()=>emit('town:zoom',1/1.15);$('#reset-map').onclick=()=>emit('town:reset');
$('#city-overview').onclick=()=>emit('town:overview');
$('#district-nav').onclick=event=>{const button=event.target.closest('[data-district]');if(button){emit('town:district',button.dataset.district);$('#toggle-districts').setAttribute('aria-expanded','false');layoutHUD();}};
on('town:district-selected',district=>{$('#district-nav').querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.district===district.id)));});
let motionPaused=localStorage.getItem('kiraku-motion')==='paused'||matchMedia('(prefers-reduced-motion:reduce)').matches;
function setMotion(){const button=$('#toggle-motion');button.setAttribute('aria-pressed',String(motionPaused));button.setAttribute('aria-label',motionPaused?t('Resume town motion','Sambung animasi bandar'):t('Pause town motion','Jeda animasi bandar'));button.textContent=motionPaused?'▷':'Ⅱ';emit('town:motion',motionPaused);}
$('#toggle-motion').onclick=()=>{motionPaused=!motionPaused;localStorage.setItem('kiraku-motion',motionPaused?'paused':'playing');setMotion();emit('town:motion-state',motionPaused);};on('town:motion-state',paused=>{motionPaused=paused;setMotion();});
$('#building-list-toggle').onclick=()=>{const list=$('#building-list');list.hidden=!list.hidden;$('#building-list-toggle').setAttribute('aria-expanded',String(!list.hidden));};
$('#building-list').onclick=event=>{const button=event.target.closest('[data-building]');if(button)buildingDetail(state.town.find(p=>p.id===Number(button.dataset.building)));};
on('town:building',buildingDetail);on('town:error',toast);on('town:ready',()=>{ready=true;renderState();setMotion();layoutHUD();if(events.length)emit('town:agent-action',events[0]);if(currentCase&&!panel.hidden)emit('town:case',currentCase);});
window.addEventListener('error',event=>{console.error(event.error||event.message);});
loadPupils();
const saved=new URLSearchParams(location.search).get('pupil')||localStorage.getItem('kiraku-pupil');if(['pupil-a','pupil-b','pupil-c'].includes(saved))start(saved);
setInterval(()=>{if(pid&&document.visibilityState==='visible')refreshEvents().catch(()=>{});},3000);

function renderActivity(){
  $('#agent-activity').innerHTML=events.slice(0,5).map(e=>`<article class="agent-action" data-event-id="${e.id}"><div><strong>${esc(e.display_agent||e.agent)}</strong><time>${esc(time(e.timestamp))}</time></div><p>${esc(e.avatar_text||e.display_decision||e.decision)}</p><small>${t('Saved decision','Keputusan disimpan')} #${e.id}</small></article>`).join('')||`<p>${t('Start a case to see the agents at work.','Mulakan kes untuk melihat aktiviti ejen.')}</p>`;
}
on('town:avatar',()=>{$('#agent-dialog').showModal();renderActivity();});
$('#find-pelita').onclick=()=>emit('town:find-pelita');
$('.pelita-card').onclick=()=>emit('town:find-pelita');
$('.pelita-card').tabIndex=0;$('.pelita-card').setAttribute('role','button');$('.pelita-card').onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();emit('town:find-pelita');}};
$('#toggle-districts').onclick=()=>{const b=$('#toggle-districts');b.setAttribute('aria-expanded',String(b.getAttribute('aria-expanded')!=='true'));layoutHUD();};
on('town:motion-setting',value=>{motionPaused=value;setMotion();});
window.addEventListener('kiraku:language-change',()=>{sessionStorage.setItem('kiraku-case-view',JSON.stringify({pid,id:currentCase?.id,view,open:!panel.hidden,drafts:currentCase?.steps.map(s=>s.draft)}));});
function restoreDrafts(){try{const saved=JSON.parse(sessionStorage.getItem('kiraku-case-view'));sessionStorage.removeItem('kiraku-case-view');if(saved?.id===currentCase.id){view=saved.view;currentCase.steps.forEach((s,i)=>s.draft=saved.drafts?.[i]);if(saved.open){const url=new URL(location);url.searchParams.delete('city');history.replaceState(null,'',url);}return saved.open;}}catch{}}
window.addEventListener('kiraku:demo-ready',async()=>{if(pid==='pupil-a'){currentCase=null;closePanel();await refreshState();await refreshEvents();}});
