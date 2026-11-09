"""Saved city layout and curated original Cytopia sprite assignments.

All occupied lots become town rows. The renderer never invents buildings.
"""
CITY = dict(version=2, size=40, roads=[2,7,12,16,20,23,28,33,37],
    source='Cytopia',source_url='https://github.com/CytopiaTeam/Cytopia',
    districts=[
        dict(id='market',name='Pusat bandar',english='Town centre',x=18,y=18),
        dict(id='homes',name='Kediaman Daun',english='Residential quarter',x=9,y=24),
        dict(id='skyline',name='Dataran Awan',english='Civic skyline',x=26,y=9),
        dict(id='gardens',name='Taman Rimba',english='Garden district',x=26,y=29),
    ])

CORE_ART = {
    (2,2):'com_1x1_JimmysBread', (6,2):'com_1x1_CafeApartment_kt',
    (9,5):'com_1x1_CompactFastshop_MS', (2,6):'park_2x2_RusticPark',
    (6,9):'com_1x1_ClockStore1', (9,9):'com_1x1_BikeShop',
    (5,5):'com_1x1_LisieuxPlantCare', (9,2):'com_1x1_BikeShop',
    (6,6):'com_1x1_CompactFastshop_MS', (2,9):'park_2x2_PicnicArea',
}


def extended_lots():
    """A fixed starting city, with four mission lots reserved in each quarter."""
    lots=[]
    homes=['res_1x1_ClassicHouse_MS','res_1x1_FrenchAbode','res_1x1_SmallRedHouse_RF','res_1x1_GreenHouseHouse','res_1x1_KTHouseNew']
    def add(kind,name,en,x,y,asset,footprint=1,district='homes',frame=0,status='built',template=None,landmark=0):
        lots.append(dict(kind=kind,name=name,english=en,x=x,y=y,asset=asset,footprint=footprint,
                         district=district,frame=frame,status=status,template_id=template,landmark=landmark,
                         street={'market':'Jalan Pelangi','homes':'Jalan Daun','skyline':'Jalan Awan','gardens':'Jalan Rimba'}[district]))
    n=0
    # Low-rise neighbourhoods are grouped into blocks with green courtyards.
    for bx,by in [(8,18),(8,24),(8,29),(3,24),(3,18),(13,24),(17,24),(24,17),(29,17),(29,24),(24,3),(17,8),(8,8),(13,8)]:
        for dx,dy in [(0,0),(1,0),(2,0),(0,2),(2,2)]:
            x,y=bx+dx,by+dy
            if x in CITY['roads'] or y in CITY['roads']:continue
            n+=1;asset=homes[n%len(homes)]
            add('homes',f'Rumah Daun {n:02d}','Neighbourhood home',x,y,asset,frame=(n%4 if asset.endswith('KTHouseNew') else n%2 if 'GreenHouseHouse' in asset else 0))
    # Larger apartment buildings add a second scale to the neighbourhood.
    for i,(x,y) in enumerate([(5,9),(10,14),(5,30),(14,30),(18,30),(25,21),(30,21),(30,30)]):
        add('homes',f'Pangsapuri Daun {i+1}','Neighbourhood apartments',x,y,'res_2x2_BaltVilniusBlock',2)
    for i,(x,y) in enumerate([(5,14),(10,35),(14,35),(18,35),(25,35),(30,35)]):
        add('homes',f'Rumah Rimba {i+1}','Garden home',x,y,'res_2x2_AnnasHouse',2,district='gardens')
    # A stepped skyline. Taller buildings sit behind the main case neighbourhood.
    towers=['com_2x2_TanTower_kt','com_2x2_BaltOffice']
    for i,(x,y) in enumerate([(18,4),(21,4),(25,5),(30,5),(25,10),(30,10),(35,10),(35,5)]):
        add('offices',f'Pejabat Awan {i+1}','Civic office building',x,y,towers[i%2],2,'skyline')
    add('civic','Balai Warga','Community centre',25,14,'com_3x3_CommunityTower',3,'skyline')
    for i,(x,y) in enumerate([(10,4),(14,4),(14,10),(18,10),(26,26),(30,26),(35,25)]):
        add('offices',f'Ruang Niaga {i+1}','Neighbourhood business',x,y,'com_1x1_StairStepShop',2,'market',frame=i%2)
    # Public parks and small gardens, all represented by persistent town rows.
    for i,(x,y) in enumerate([(25,30),(30,30),(35,30),(35,20),(5,35),(10,10)]):
        # Avoid an apartment already occupying the same place.
        if any(p['x']==x and p['y']==y for p in lots):continue
        add('civic',f'Ruang Hijau {i+1}','Public garden',x,y,'park_2x2_RusticPark' if i%2 else 'park_2x2_PicnicArea',2,'gardens')
    for i,(x,y) in enumerate([(9,20),(10,26),(4,26),(14,26),(18,26),(25,19),(30,19),(10,6),(14,6),(18,6),(30,14),(35,15),(26,35),(35,35)]):
        if not any(p['x']==x and p['y']==y for p in lots):add('civic',f'Laman Daun {i+1}','Pocket garden',x,y,'park_1x1_Garden',1,'gardens',frame=i%4)
    # Further maths outcomes open new lots before upgrading an existing building.
    missions=[('shops','Kedai Bunga','Flower shop','kedai_bunga_melur','com_1x1_LisieuxPlantCare',1),
              ('stands','Hentian Teksi','Taxi stand','teksi_kiraku','com_1x1_BikeShop',1),
              ('stalls','Gerai Daun','Market stall','gerai_taman','com_1x1_CompactFastshop_MS',1),
              ('parks','Taman Melur','Neighbourhood park','taman_kiraku','park_2x2_RusticPark',2)]
    for q,(district,points) in enumerate([
        ('homes',[(10,22),(5,22),(10,27),(5,30)]),
        ('skyline',[(26,8),(30,8),(35,8),(35,14)]),
        ('gardens',[(25,32),(30,32),(35,32),(35,35)])]):
        for i,(kind,name,en,template,asset,size) in enumerate(missions):
            x,y=points[i]
            # A mission plot takes priority over a pocket garden at this exact site.
            lots[:]=[p for p in lots if (p['x'],p['y'])!=(x,y)]
            add(kind,f'{name} {q+1}',en,x,y,asset,size,district,status='empty',template=template,landmark=1)
    # Reserve footprints in map coordinates, so tall or multi-tile lots cannot
    # overlap a neighbour or consume a road. Mission lots take priority.
    reserved=[dict(x=x+12,y=y+12,footprint=2 if (x,y) in [(2,6),(2,9)] else 1) for x,y in CORE_ART]
    kept=[]
    for lot in sorted(lots,key=lambda p:(p['status']!='empty',-p['footprint'])):
        half=(lot['footprint']+1)/2
        if any(abs(lot[axis]-r)<half for axis in ['x','y'] for r in CITY['roads']):continue
        if any(abs(lot['x']-p['x'])<(lot['footprint']+p['footprint'])/2 and
               abs(lot['y']-p['y'])<(lot['footprint']+p['footprint'])/2 for p in reserved):continue
        kept.append(lot);reserved.append(lot)
    return kept
