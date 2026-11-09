export const language=document.documentElement.lang==='ms'?'ms':'en';
export const t=(en,ms)=>language==='ms'?ms:en;
export const pair=value=>{const parts=String(value??'').split(' / ');return parts.length>1?parts[language==='ms'?0:1]:parts[0];};
export const pupilName=name=>String(name).replace('Pupil',t('Pupil','Murid'));
export const plotName=p=>p.status==='built'?(language==='ms'?p.name:(p.funded_case_id?p.name.replace('Kedai Bunga ','Flower shop ').replace('Hentian ','Taxi stand ').replace('Teksi ','Taxi ').replace('Gerai ','Stall ').replace('Taman ','Park '):p.english||p.name)):p.waiting?t('Waiting','Menunggu'):t('Empty plot','Lot kosong');
