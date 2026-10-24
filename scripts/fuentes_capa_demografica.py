#!/usr/bin/env python3
"""Reproduce carga de presencia anual sin escribir ni alterar el ensayo anterior."""
import json,sys
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.fuentes_ensayo_enlace_conjunto import cargar_ensayo,doc,token,year,sha,YEARS
from scripts.reconstruir_planes_umas import read_sheet
from scripts.diagnosticar_enlace_conjunto import build_graphs
from common.versiones_por_cohorte import clave_grupo
from common.presencia_anual import evaluar_nota
from common.enlace_conjunto import solve
OUT=ROOT/'data/presencia_anual/20261016'


def cargar_presencia():
    d=cargar_ensayo(); sources=dict(d['sources'])
    sm=json.loads((ROOT/'data/continuidad_trayectoria/20261016/fuentes.json').read_text())['umas']['promedios']
    assert sha(sm['path'])==sm['sha256']
    base=d['base']/'2025/SIES/AVANCE CURRICULAR/original'
    paths=[Path(sm['path'])]+[base/f'{y}.xlsx' for y in (2020,2021,2022)]
    index=defaultdict(list)
    for r in d['da']:index[token(r['CODCLI']),token(r['CODCARPR'])].append(r)
    evidence=defaultdict(set); academic=defaultdict(set); source_stats=[]
    for r in d['da']:
        y=year(r['ANOMATRICULA'])
        if y and doc(r['RUT']):evidence[r['_fila'],y].add('ANOMATRICULA')
    for p in paths:
        sources[str(p)]=sha(p)
        fields=('CODCLI','RUT','DIG','CODCARR','ANO','DESCRIPCION_ESTADO','CONVALIDADO')
        rows,meta=read_sheet(p,'Hoja1',fields)
        quality=Counter();years=Counter();states=Counter()
        for r in rows:
            candidates=index[token(r['CODCLI']),token(r['CODCARR'])]
            status,y=evaluar_nota(r,candidates);quality[status]+=1;years[token(r['ANO'])]+=1
            states[token(r['DESCRIPCION_ESTADO'])]+=1
            if status=='ACTIVIDAD_VERIFICADA':
                for a in candidates:
                    evidence[a['_fila'],y].add('ACTIVIDAD_ACADEMICA')
                    academic[a['_fila'],y].add(str(p))
        source_stats.append({'path':str(p),'lectura':meta,'filas':len(rows),'anios_reales':dict(years),'estados':dict(states),'clasificacion':dict(quality)})
    byrow={r['_fila']:r for r in d['da']}
    expanded=[]; annual=defaultdict(lambda:defaultdict(set)); career=defaultdict(set)
    byperson=defaultdict(list)
    for r in d['da']:
        if doc(r['RUT']):byperson[doc(r['RUT'])].append(r)
    for (row,y),flags in evidence.items():
        r=byrow[row];p=doc(r['RUT'])
        expanded.append(dict(r,ANOMATRICULA=str(y)))
        annual[y]['union'].add(p)
        for flag in flags:annual[y][flag].add(p)
        career[y,token(r['CODCARPR']),token(r['SEDE']),token(r['JORNADA']),'+'.join(sorted(flags))].add(p)
    return locals()
