def report(snapshot, logger):
    pupil=snapshot['pupil'];mastery=pupil['mastery']
    strong=max(mastery,key=lambda m:m['score']);weak=min(mastery,key=lambda m:m['score'])
    sections=[
        dict(title='Kemajuan / Progress',text=f"{pupil['id']} is strongest in {strong['title_en']} ({strong['score']}% mastery). Current practice level: {pupil['level']}."),
        dict(title='Perhatian / Attention',text=f"{len(snapshot['open_issues'])} open issue(s). Prioritise {weak['title_en']}; inspect the logged misconception before giving a worked answer."),
        dict(title='Langkah seterusnya / Next steps',text='Ask the pupil to explain each operation aloud. Revisit due issues after two completed cases, then compare the new working with the original attempt.'),
    ]
    sections_ms=[
        dict(title='Kemajuan',text=f"{pupil['id']} paling menguasai {strong['title_ms']} ({strong['score']}% penguasaan). Tahap latihan semasa: {pupil['level']}."),
        dict(title='Perhatian',text=f"{len(snapshot['open_issues'])} isu terbuka. Utamakan {weak['title_ms']}; semak salah faham yang direkodkan sebelum memberi penyelesaian."),
        dict(title='Langkah seterusnya',text='Minta murid menerangkan setiap operasi secara lisan. Ulang kaji isu selepas dua kes selesai, kemudian bandingkan pengiraan baharu dengan cubaan asal.'),
    ]
    logger.action('Teacher',f"{pupil['id']}; mastery and open issues",'Prepared a three-section practice report.',dict(sections=sections,sections_ms=sections_ms))
    return dict(pupil_id=pupil['id'],sections=sections,sections_ms=sections_ms)
