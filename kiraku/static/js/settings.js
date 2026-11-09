import {t} from './i18n.js';
import {api,toast} from './api.js';
import {emit,on} from './bus.js';
const dialog=document.querySelector('#settings-dialog');
document.querySelector('#open-settings').onclick=()=>dialog.showModal();
document.querySelectorAll('[data-close-dialog]').forEach(b=>b.onclick=()=>b.closest('dialog').close());
dialog.addEventListener('click',e=>{if(e.target===dialog)dialog.close();});
document.querySelectorAll('[name=language]').forEach(input=>input.onchange=()=>{
  window.dispatchEvent(new Event('kiraku:language-change'));
  document.cookie=`kiraku-language=${input.value};path=/;max-age=31536000;SameSite=Strict`;
  localStorage.setItem('kiraku-language',input.value);location.reload();
});
const motion=document.querySelector('#settings-motion');motion.checked=localStorage.getItem('kiraku-motion')==='paused'||matchMedia('(prefers-reduced-motion:reduce)').matches;
motion.onchange=()=>{localStorage.setItem('kiraku-motion',motion.checked?'paused':'playing');emit('town:motion-setting',motion.checked);};
on('town:motion-state',value=>motion.checked=value);
document.querySelector('#prepare-demo').onclick=async e=>{
  const b=e.currentTarget;b.disabled=true;b.textContent=t('Preparing saved cases…','Menyediakan kes tersimpan…');
  try{const result=await api('/api/demo/prepare',{});toast(t(`${result.completed} completed demo cases are ready for Pupil A.`,`${result.completed} kes demo selesai disediakan untuk Murid A.`));window.dispatchEvent(new Event('kiraku:demo-ready'));}
  catch(error){toast(error.message);}finally{b.disabled=false;b.textContent=t('Prepare demo progress','Sediakan kemajuan demo');}
};
