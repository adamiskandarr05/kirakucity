NAMES={
    'shops':['Kedai Bunga Melur','Kedai Bunga Daun','Kedai Bunga Awan'],
    'stands':['Teksi Kiraku','Hentian Daun','Hentian Pelangi'],
    'stalls':['Gerai Taman','Gerai Rimba','Gerai Melur'],
    'parks':['Taman Kiraku','Taman Daun','Taman Pelangi'],
}
STREETS=['Jalan Pelangi','Jalan Daun','Jalan Awan']


def fill(case, completed, logger, location=None):
    case['name']=location['name'] if location else NAMES[case['kind']][completed%3]
    case['street']=location['street'] if location else STREETS[completed%3]
    logger.action('Scenario',f"{case['template_id']}; fictional names only",f"Assigned {case['name']} to {case['street']}.",dict(name=case['name'],street=case['street']))
    return case
