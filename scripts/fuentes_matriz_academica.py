#!/usr/bin/env python3
"""Reproduce evidencia demográfica en memoria sin modificar entregas previas."""
import json,sys
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.fuentes_capa_demografica import cargar_presencia
from scripts.fuentes_ensayo_enlace_conjunto import doc,token,year,sha
from scripts.diagnosticar_enlace_conjunto import build_graphs
from common.capa_demografica import nacimiento,sexo,comparar,puerta
from common.enlace_conjunto import solve
OUT=ROOT/'data/capa_demografica/20261016'


def cargar_evidencia():
    ctx=cargar_presencia();d=ctx['d'];sources=ctx['sources']
    up=defaultdict(lambda:{'birth':set(),'sex':set(),'bad':False})
    mp=defaultdict(lambda:{'birth':set(),'sex':set(),'bad':False})
    rp=defaultdict(lambda:{'birth':set(),'sex':set()})
    raw_quality=defaultdict(Counter)
    for r in d['da']:
        p=doc(r['RUT'])
        b,bs=nacimiento(r['FECHANACIMIENTO']);s,ss=sexo(r['SEXO'],'UMAS')
        raw_quality['UMAS_nacimiento'][bs]+=1;raw_quality['UMAS_sexo'][ss]+=1
        if not p:continue
        up[p]['birth'].add(b);up[p]['sex'].add(s);up[p]['bad'] |= bs!='VALIDO' or ss!='VALIDO'
    # Auditoría longitudinal MRUN: no ligar MRUN distintos por sus atributos.
    for r in d['rawmr']:
        m=token(r['mrun'])
        b,bs=nacimiento(r['fec_nac_alu']);s,ss=sexo(r['gen_alu'],'MRUN')
        raw_quality['MRUN_nacimiento'][bs]+=1;raw_quality['MRUN_sexo'][ss]+=1
        if not m:continue
        mp[m]['birth'].add(b);mp[m]['sex'].add(s);mp[m]['bad'] |= bs!='VALIDO' or ss!='VALIDO'
    for r in d['references']:
        if not r['person']:continue
        key=r['year'],r['person']
        rp[key]['birth'].add(r['birth']);rp[key]['sex'].add({'M':'HOMBRE','F':'MUJER'}.get(r['sex']))
    def clean_ok(v):
        return not v['bad'] and len(v['birth'])==1 and len(v['sex'])==1
    comparisons={};counts=Counter();byyear=Counter();incidences=[]
    for (y,p),v in rp.items():
        if p not in up:
            counts['PERSONA_AUSENTE_UMAS']+=1
            continue
        states={f:comparar(up[p][f],v[f]) for f in ('birth','sex')}
        comparisons[y,p]=states
        for f,s in states.items():byyear[y,f,s]+=1
        label='COINCIDE_AMBOS' if all(s=='COINCIDE' for s in states.values()) else 'REQUIERE_REVISION'
        counts[label]+=1
        if label!='COINCIDE_AMBOS':
            incidences.append({'anio':y,'nacimiento':states['birth'],'sexo':states['sex']})
    graphs,_,_,_=build_graphs(ctx['expanded'],d['mr'],d['groups'])
    sol={}
    for y,g in graphs['cohorte_original'].items():
        forced,_=solve(g);sol.update({(y,p):m for p,m in forced.items()})
    return locals()
