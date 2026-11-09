"""Visible floor counts are derived from saved building levels, never random."""
def appearance(plot):
    level=max(1,int(plot['level']))
    upgraded=plot['status']=='built' and level>1 and plot['kind'] in ['shops','stalls','parks','stands']
    floors=level+2 if upgraded else 0
    return dict(style='kiraku-upgrade' if upgraded else 'cytopia',level=level,floors=floors,
                height=(36+floors*8) if upgraded else None,
                key=f"upgrade:{plot['kind']}:{plot['footprint']}:{level}" if upgraded else plot.get('asset',''))
