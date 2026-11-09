"""Presentation translations. Stored calculations and audit records stay intact."""
from copy import deepcopy
import re
from flask import request
from .cases.templates import display


def language():
    return 'ms' if request.headers.get('X-Kiraku-Language', request.cookies.get('kiraku-language', 'en')) == 'ms' else 'en'


def text(en, ms):
    return ms if language() == 'ms' else en


def pair(value):
    if not isinstance(value, str): return value
    parts=value.split(' / ', 1)
    return parts[0 if language()=='ms' else 1] if len(parts)==2 else translate(value)


MS = {
    'Undo the discount first, then undo the price increase.':'Batalkan diskaun dahulu, kemudian batalkan kenaikan harga.',
    'Divide the final price by the discount multiplier, then by the increase multiplier.':'Bahagikan harga akhir dengan pengganda diskaun, kemudian dengan pengganda kenaikan.',
    'Profit compares what the shop receives with what it paid.':'Untung membandingkan hasil jualan dengan kos yang dibayar.',
    'Subtract the cost from the final selling price.':'Tolak kos daripada harga jualan akhir.',
    'The trip total includes a fixed fee and a distance charge.':'Jumlah tambang merangkumi tambang mula dan caj jarak.',
    'Subtract the fixed fee before dividing by the rate per kilometre.':'Tolak tambang mula sebelum membahagi dengan kadar setiap kilometer.',
    'The new trip also starts with the fixed fee.':'Perjalanan baharu juga bermula dengan tambang mula.',
    'Multiply the new distance by the rate, then add the fixed fee.':'Darab jarak baharu dengan kadar, kemudian tambah tambang mula.',
    'The mean spreads the total evenly across the days.':'Min membahagikan jumlah secara sama rata antara hari.',
    'Multiply the mean by the number of days.':'Darab min dengan bilangan hari.',
    'Compare the full total with the known sales.':'Bandingkan jumlah keseluruhan dengan jualan yang diketahui.',
    'Subtract the sum of the known sales from the total.':'Tolak jumlah jualan yang diketahui daripada jumlah keseluruhan.',
    'The mode is the value that occurs most often.':'Mod ialah nilai yang paling kerap muncul.',
    'Count each value across all the daily sales and choose the most frequent.':'Kira kekerapan setiap nilai jualan harian dan pilih yang paling kerap.',
    'A rectangle has a pair of long sides and a pair of short sides.':'Segi empat tepat mempunyai sepasang sisi panjang dan sepasang sisi pendek.',
    'Halve the perimeter, subtract the length difference, then halve again.':'Bahagi perimeter dengan dua, tolak beza panjang, kemudian bahagi dengan dua lagi.',
    'The length is greater than the width.':'Panjang melebihi lebar.',
    'Add the stated difference to the width.':'Tambah beza yang diberi kepada lebar.',
    'The budget covers a fence on one long side only.':'Bajet meliputi pagar pada satu sisi panjang sahaja.',
    'Multiply the length by the cost per metre.':'Darab panjang dengan kos setiap meter.',
    'A shortfall is the amount still needed after using the budget.':'Kekurangan ialah jumlah yang masih diperlukan selepas menggunakan bajet.',
    'Subtract the budget from the fence cost; use zero if the budget is sufficient.':'Tolak bajet daripada kos pagar; gunakan sifar jika bajet mencukupi.',
    'Bandar Kiraku is counting on your ideas. Read the givens, then take one step at a time.':'Bandar Kiraku menantikan idea anda. Baca maklumat diberi, kemudian selesaikan satu langkah pada satu masa.',
    'You checked each calculation before making a town decision. Keep the same care in the next case.':'Anda menyemak setiap pengiraan sebelum membuat keputusan bandar. Teruskan ketelitian ini dalam kes seterusnya.',
    'Read the givens and check each operation before continuing.':'Baca maklumat diberi dan semak setiap operasi sebelum meneruskan.',
    'Keep explaining why each operation fits the brief.':'Teruskan menerangkan sebab setiap operasi sesuai dengan soalan.',
    'Town news: a plan is ready for its next chapter.':'Berita bandar: pelan sedia untuk langkah seterusnya.',
    'Enter a decimal number.':'Masukkan nombor perpuluhan.',
    'Enter a decimal number':'Masukkan nombor perpuluhan',
    'Use at most 2 decimal places.':'Gunakan maksimum 2 tempat perpuluhan.',
}


def translate(value):
    if not isinstance(value,str) or language()!='ms': return value
    if value in MS: return MS[value]
    value=re.sub(r' occurs twice; every other value occurs once\.', ' muncul dua kali; nilai lain muncul sekali.', value)
    return value.replace('days','hari')


def feedback(result):
    if not result: return result
    r=deepcopy(result)
    if r.get('correct'):
        r['solution']=translate(r['solution'])
        r['message']=text('Verified. ','Disahkan. ')+r['solution']
    elif r.get('trap'):
        r['trap']=pair(r['trap']);r['message']=text('Not yet. ','Belum tepat. ')+r['trap']
    elif r.get('value') is not None:
        r['message']=text('Not yet. Check the operation and try again.','Belum tepat. Semak operasi dan cuba lagi.')
    else:
        r['message']=text(r['message'],'Masukkan nombor perpuluhan yang sah dengan maksimum 2 tempat perpuluhan.')
    return r


def case_view(case):
    c=deepcopy(case);g=c['givens'];m=lambda k:display(g[k]);ms=language()=='ms'
    c['title']=c['title_ms' if ms else 'title_en']
    c['rounding']=text('Round to 2 decimal places (half up).','Bulatkan kepada 2 tempat perpuluhan (separuh ke atas).')
    if c['kind']=='shops':
        c['brief']=text(f"A flower shop increases its vase price by {m('P')}%, then gives a {m('Q')}% discount. The final price is RM {m('F')} and the cost is RM {m('C')}. Find the original price and profit. A profit of at least RM {m('T')} reopens the shop.",f"Kedai bunga menaikkan harga pasu sebanyak {m('P')}%, kemudian memberi diskaun {m('Q')}%. Harga akhir ialah RM {m('F')} dan kos ialah RM {m('C')}. Cari harga asal dan untung. Untung sekurang-kurangnya RM {m('T')} membuka semula kedai.")
    elif c['kind']=='stands':
        c['brief']=text(f"The taxi charges a fixed fee of RM {m('A')} plus RM {m('R')} per kilometre. The first trip costs RM {m('F')}. Find its distance, then the fare for a {m('D')} km trip to open the taxi stand.",f"Teksi mengenakan tambang mula RM {m('A')} serta RM {m('R')} setiap kilometer. Perjalanan pertama berharga RM {m('F')}. Cari jaraknya, kemudian tambang perjalanan {m('D')} km untuk membuka hentian teksi.")
    elif c['kind']=='stalls':
        known=', '.join(display(v) for v in g['known'])
        c['brief']=text(f"Five days of sales have a mean of RM {m('M')}. Four daily sales are known: {known}. Find the total, missing sales and mode. A mode of at least RM {m('T')} opens the stall.",f"Jualan lima hari mempunyai min RM {m('M')}. Empat jualan harian diketahui: {known}. Cari jumlah, jualan yang hilang dan mod. Mod sekurang-kurangnya RM {m('T')} membuka gerai.")
    else:
        c['brief']=text(f"The park is 5 m longer than it is wide, with perimeter {m('P')} m. The budget is RM {m('B')} and fencing costs RM {m('R')} per metre. Find both dimensions, the fence cost for one long side and the shortfall. Zero shortfall funds the park.",f"Panjang taman ialah 5 m lebih daripada lebarnya, dengan perimeter {m('P')} m. Bajet ialah RM {m('B')} dan pagar berharga RM {m('R')} setiap meter. Cari panjang, lebar, kos pagar satu sisi panjang dan kekurangan bajet. Kekurangan sifar membiayai taman.")
    c['given_rows']=[[pair(label),value,translate(unit)] for label,value,unit in c['given_rows']]
    for s in c['steps']:
        s['label']=pair(s['label']);s['last_result']=feedback(s.get('last_result'))
        if 'solution' in s:s['solution']=translate(s['solution'])
    if c.get('narration'):
        original=c['narration']['text']
        c['narration']['text']=MS.get(original,MS['Bandar Kiraku is counting on your ideas. Read the givens, then take one step at a time.']) if ms else original
    if c.get('result'):c['result']=result_view(c['result'])
    return c


def result_view(result):
    r=deepcopy(result);r['outcome']=r['outcome_ms' if language()=='ms' else 'outcome_en']
    for m in r.get('marks',[]):m['label']=pair(m['label']);m['solution']=translate(m['solution'])
    review=r.get('review',{})
    for key in ['text','news','revisit','strongest']:
        if key not in review:continue
        v=review[key]
        if v.startswith('You verified '):v=text('You verified ','Anda mengesahkan ')+pair(v[13:].rstrip('.'))+'.'
        elif v.startswith('Revisit '):v=text('Revisit ','Ulang kaji ')+pair(v[8:].rstrip('.'))+'.'
        else:
            v=translate(v)
            if key=='text' and language()=='ms' and review.get('source')=='Gemini':v=MS['You checked each calculation before making a town decision. Keep the same care in the next case.']
        review[key]=v
    return r


AGENTS={'Quest':('Planner','Perancang'),'Problem':('Problem maker','Pembina soalan'),'Verifier':('Verifier','Pengesah'),'Scenario':('Town storyteller','Pencerita bandar'),'Feedback':('Answer checker','Penyemak jawapan'),'Hint':('Hint guide','Pembimbing petunjuk'),'Outcome':('Town builder','Pembina bandar'),'Teacher':('Teacher','Guru'),'Pelita':('Pelita','Pelita')}


def event_view(event):
    e=deepcopy(event);a=e['agent'];raw=e['raw'];en,ms=AGENTS.get(a,(a,a));e['display_agent']=text(en,ms)
    if a=='Feedback':
        decision=text('Calculation verified.','Pengiraan disahkan.') if raw.get('correct') else text('This step needs another look.','Langkah ini perlu disemak semula.')
        if raw.get('trap'):decision+=' '+pair(raw['trap'])+'.'
    elif a=='Quest':decision=text('Returning to a due practice issue.','Mengulang kaji isu latihan yang telah tiba masanya.') if raw.get('issue_id') else text('Choosing practice from this pupil’s saved mastery.','Memilih latihan berdasarkan penguasaan murid yang disimpan.')
    elif a=='Hint':decision=translate(e['decision'])
    elif a=='Outcome':decision=text('The checked plan can improve the town.','Pelan yang disahkan boleh membangunkan bandar.') if raw.get('effect') else text('Calculations saved; this project is waiting for its target.','Pengiraan disimpan; projek ini menunggu sasarannya.')
    elif a=='Pelita':decision=MS.get(e['decision'],'Pelita menyediakan panduan untuk kes ini.') if language()=='ms' else e['decision']
    elif a=='Scenario':decision=text('Preparing the people and place for this case.','Menyediakan watak dan tempat untuk kes ini.')
    elif a=='Verifier':decision=text('Checking the generated maths before it reaches the pupil.','Menyemak matematik yang dijana sebelum dipaparkan kepada murid.')
    elif a=='Problem':decision=text('Preparing a linked maths case.','Menyediakan kes matematik berangkai.')
    else:decision=text('Prepared a practice report from saved progress.','Laporan latihan disediakan daripada kemajuan yang disimpan.')
    # English retains the full original reasoning; Malay has a readable localized
    # summary. Original database fields and raw evidence remain available below.
    e['display_decision']=e['decision'] if language()=='en' and a not in ['Feedback','Hint'] and not (a=='Quest' and raw.get('issue_id')) else decision
    e['avatar_text']=decision
    e['display_inputs']=text('Saved decision','Keputusan disimpan')+f" #{e['id']}"
    if a=='Feedback':e['display_inputs']+=text(' · Step ',' · Langkah ')+str(raw['step_index']+1)
    if a=='Hint':e['display_inputs']+=text(' · Hint level ',' · Tahap petunjuk ')+str(raw['level'])
    return e


def report_view(report):
    r=deepcopy(report)
    if language()=='ms' and 'sections_ms' in r:r['sections']=r['sections_ms']
    else:
        for s in r.get('sections',[]):
            s['title']=pair(s['title'])
            if language()=='ms':
                v=s['text']
                replacements={' is strongest in ':' paling menguasai ','% mastery':'% penguasaan','Current practice level:':'Tahap latihan semasa:',' open issue(s). Prioritise ':' isu terbuka. Utamakan ','; inspect the logged misconception before giving a worked answer.':'; semak salah faham yang direkodkan sebelum memberi penyelesaian.','Ratio & percentage':'Nisbah dan peratus','Linear equations':'Persamaan linear','Statistics':'Statistik','Two unknowns':'Dua pembolehubah','Ask the pupil to explain each operation aloud. Revisit due issues after two completed cases, then compare the new working with the original attempt.':'Minta murid menerangkan setiap operasi secara lisan. Ulang kaji isu selepas dua kes selesai, kemudian bandingkan pengiraan baharu dengan cubaan asal.'}
                for en,ms in replacements.items():v=v.replace(en,ms)
                s['text']=v
    return r


def response_view(data, path):
    d=deepcopy(data)
    if d.get('error') and language()=='ms':
        errors={'Start a pupil session first':'Mulakan sesi murid dahulu.','Case not found for this pupil':'Kes tidak ditemui untuk murid ini.','This case is already finished.':'Kes ini telah selesai.','Verify the previous step first.':'Sahkan langkah sebelumnya dahulu.','This step is locked.':'Langkah ini dikunci.','Verify every step before finishing. The town has not changed.':'Sahkan setiap langkah sebelum menyiapkan kes. Bandar belum berubah.','Invalid step index':'Langkah tidak sah.','Invalid hint request':'Permintaan petunjuk tidak sah.','Demo preparation could not complete. Saved progress is safe.':'Persediaan demo tidak dapat diselesaikan. Kemajuan tersimpan selamat.'}
        d['error']=errors.get(d['error'],'Permintaan tidak dapat diselesaikan. Sila cuba lagi.')
    if 'case' in d:d['case']=case_view(d['case'])
    if d.get('active_case'):d['active_case']=case_view(d['active_case'])
    if 'correct' in d:d=feedback(d)
    if path.endswith('/hint') and 'text' in d:d['text']=translate(d['text'])
    if path.endswith('/finish') and 'branch' in d:d=result_view(d)
    if 'events' in d:d['events']=[event_view(e) for e in d['events']]
    if 'decision_log' in d:d['decision_log']=[event_view(e) for e in d['decision_log']]
    if 'reports' in d:
        for r in d['reports']:r['raw']=report_view(r['raw'])
    if 'sections' in d:d=report_view(d)
    if 'open_issues' in d:
        for issue in d['open_issues']:
            reason=issue['reason'];issue['display_reason']=pair(reason.removeprefix('Revisit '))
    return d
