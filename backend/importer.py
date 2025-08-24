import os,re
from typing import Dict,List,Tuple
from models import SessionLocal, Group
from sqlalchemy import delete
HEX=re.compile(r'^[0-9A-Fa-f]{6}$')

def parse_mapping_file(path:str)->Tuple[Dict[str,List[int]],Dict[str,str]]:
    groups={}; colors={}; cur=None
    with open(path,'r',encoding='utf-8',errors='ignore') as f:
        for raw in f:
            line=raw.strip()
            if not line: continue
            if line.startswith('#'):
                cur=line.lstrip('#').strip() or 'Gruppe'
                groups.setdefault(cur,[]); colors.setdefault(cur,'#FFFFFF'); continue
            parts=line.split();
            if not parts or not parts[0].isdigit(): continue
            idx=int(parts[0]);
            if cur is None: cur='Gruppe'; groups.setdefault(cur,[]); colors.setdefault(cur,'#FFFFFF')
            groups[cur].append(idx)
            for p in parts[1:5]:
                if p!='.' and HEX.match(p) and colors.get(cur,'#FFFFFF')=='#FFFFFF':
                    colors[cur]='#'+p.upper(); break
    return groups, colors

def import_mapping(path:str, mode:str='merge'):
    groups,colors=parse_mapping_file(path)
    with SessionLocal() as s:
        if mode=='reset': s.execute(delete(Group))
        existing={g.name:g for g in s.query(Group).all()}
        for name,idxs in groups.items():
            led=','.join(str(i) for i in sorted(set(idxs)))
            if name in existing:
                g=existing[name]; g.led_indices=led; g.color=colors.get(name,g.color or '#FFFFFF')
            else:
                s.add(Group(name=name, led_indices=led, color=colors.get(name,'#FFFFFF')))
        s.commit()
