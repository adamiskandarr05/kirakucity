"""Seeded landscape and safe lot placement, shared by saved towns and the map."""
import math
import random
from functools import lru_cache

SEED=42173
LAKE=dict(x=26,y=10,rx=5.7,ry=4.2,name='Tasik Awan',english='Cloud Lake')


def on_land(x,y,margin=0):
    dx,dy=x-19.5,y-19.5
    angle=math.atan2(dy,dx)
    radius=19.7/(abs(math.cos(angle))**4+abs(math.sin(angle))**4)**.25+0.6*math.sin(angle*3)+0.4*math.cos(angle*7)
    return math.hypot(dx,dy)+margin<radius


def near_water(x,y,margin=0):
    return ((x-LAKE['x'])/(LAKE['rx']+margin))**2+((y-LAKE['y'])/(LAKE['ry']+margin))**2<1


def environment(roads):
    return _environment(tuple(roads))


@lru_cache(maxsize=4)
def _environment(roads):
    coast=[];water=[]
    for i in range(64):
        a=math.tau*i/64;r=19.7/(abs(math.cos(a))**4+abs(math.sin(a))**4)**.25+.6*math.sin(a*3)+.4*math.cos(a*7)
        coast.append([round(19.5+math.cos(a)*r,3),round(19.5+math.sin(a)*r,3)])
    for i in range(40):
        a=math.tau*i/40;r=1+.065*math.sin(a*5)+.035*math.cos(a*9)
        water.append([round(LAKE['x']+math.cos(a)*LAKE['rx']*r,3),round(LAKE['y']+math.sin(a)*LAKE['ry']*r,3)])
    land=[[x,y] for y in range(40) for x in range(40) if on_land(x,y)]
    road_tiles={(x,y) for x,y in land if (x in roads or y in roads) and not near_water(x,y,.65)}
    # Uneven blocks and quiet green lanes replace the repeated full-road lattice.
    protected=set()
    for path in [[(12,16),(23,16),(23,23),(12,23),(12,16)],[(7,12),(12,12),(12,28),(7,28),(7,12)],[(33,7),(37,7),(37,20),(33,20),(33,7)]]:
        for (ax,ay),(bx,by) in zip(path,path[1:]):
            protected.update((x,y) for x in range(min(ax,bx),max(ax,bx)+1) for y in range(min(ay,by),max(ay,by)+1))
    rng=random.Random(SEED+31)
    for fixed in roads:
        for a,b in zip(roads,roads[1:]):
            for vertical in [False,True]:
                cells={(fixed,n) if vertical else (n,fixed) for n in range(a+1,b)}
                if rng.random()<.32 and not cells&protected:road_tiles.difference_update(cells)
    # Keep the one connected network used by traffic and Pelita.
    seen={(18,16)};queue=[(18,16)]
    for x,y in queue:
        for node in [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]:
            if node in road_tiles and node not in seen:seen.add(node);queue.append(node)
    road_tiles=[list(p) for p in sorted(road_tiles&seen,key=lambda p:(p[1],p[0]))]
    return dict(seed=SEED,coast=coast,land_tiles=land,road_tiles=road_tiles,lake={**LAKE,'outline':water})


def valid_lot(x,y,size,placed,roads):
    if not _terrain_clear(x,y,size,tuple(roads)):return False
    return all(abs(x-p['x'])>=(size+p['footprint'])/2 or abs(y-p['y'])>=(size+p['footprint'])/2 for p in placed)


@lru_cache(maxsize=12000)
def _terrain_clear(x,y,size,roads):
    if not on_land(x,y,size*.75) or near_water(x,y,size*.7+.55):return False
    half=(size+1)/2
    return not any(abs(x-rx)<half and abs(y-ry)<half for rx,ry in environment(roads)['road_tiles'])


def arrange(plots,roads):
    fields=('x','y','footprint','landmark','district')
    key=tuple(tuple(p[k] for k in fields)+(bool(p.get('funded_case_id')),) for p in plots)
    coordinates=_arranged(key,tuple(roads))
    return {p['id']:coordinates[i] for i,p in enumerate(plots)}


@lru_cache(maxsize=64)
def _arranged(key,roads):
    fields=('x','y','footprint','landmark','district','funded_case_id')
    plots=[dict(zip(fields,row),id=i,name=f'lot {i}') for i,row in enumerate(key)]
    positions=_arrange(plots,roads)
    return tuple(positions[i] for i in range(len(plots)))


def _arrange(plots,roads):
    """Retain core/funded lots when safe; scatter other lots without losing IDs."""
    rng=random.Random(SEED);placed=[];result={}
    zones={'homes':(3,23,9,36),'market':(8,27,9,30),'skyline':(15,37,3,22),'gardens':(3,37,23,37)}
    ordered=sorted(plots,key=lambda p:(not bool(p.get('funded_case_id')),not (p['landmark'] and p['district']=='market'),-p['footprint'],p['y'],p['x']))
    for p in ordered:
        fixed=p.get('funded_case_id') or (p['landmark'] and p['district']=='market')
        if fixed and valid_lot(p['x'],p['y'],p['footprint'],placed,roads):x,y=p['x'],p['y']
        else:
            x1,x2,y1,y2=zones.get(p['district'],zones['homes'])
            candidates=[(x,y) for y in range(y1,y2+1) for x in range(x1,x2+1) if valid_lot(x,y,p['footprint'],placed,roads)]
            if not candidates:candidates=[(x,y) for y in range(3,37) for x in range(3,37) if valid_lot(x,y,p['footprint'],placed,roads)]
            if not candidates:raise ValueError(f"No safe place for {p['name']} (footprint {p['footprint']}); {len(placed)} placed")
            rng.shuffle(candidates)
            x,y=min(candidates,key=lambda q:math.hypot(q[0]-p['x'],q[1]-p['y'])+rng.random()*8)
        result[p['id']]=(x,y);placed.append(dict(x=x,y=y,footprint=p['footprint']))
    return result
