import {language,t} from './i18n.js';
export const $ = (selector, root = document) => root.querySelector(selector);
export function esc(value) { return String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
export async function api(path, body) {
  const response = await fetch(path, body === undefined ? {cache:'no-store',headers:{'X-Kiraku-Language':language}} : {method:'POST',headers:{'Content-Type':'application/json','X-Kiraku-Language':language},body:JSON.stringify(body)});
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || `Request failed (${response.status})`);
  return data;
}
let toastTimer;
export function toast(message) { const el=$('#toast');el.textContent=message;el.hidden=false;clearTimeout(toastTimer);toastTimer=setTimeout(()=>el.hidden=true,4500); }
export const time = timestamp => new Date(timestamp).toLocaleTimeString([], {hour:'2-digit',minute:'2-digit',second:'2-digit'});
export const kinds = {shops:t('Shops','Kedai'),stalls:t('Stalls','Gerai'),parks:t('Parks','Taman'),stands:t('Taxis','Teksi'),homes:t('Homes','Rumah'),offices:t('Offices','Pejabat'),civic:t('Community','Komuniti')};
const representative={shops:'com_1x1_LisieuxPlantCare',stalls:'com_1x1_CompactFastshop_MS',parks:'park_2x2_RusticPark',stands:'com_1x1_BikeShop',homes:'res_1x1_ClassicHouse_MS',offices:'com_2x2_TanTower_kt',civic:'park_1x1_Garden'};
export const art = (kind,asset) => `/static/assets/cytopia/previews/${asset||representative[kind]}.png`;
