#!/usr/bin/env python3
"""Reconstruye evidencia anual UMAS; contrasta reportes y MRUN sin activar enlaces."""
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


def main():
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
    graphs,_,_,_=build_graphs(expanded,d['mr'],d['groups'])
    solutions={};graph_summary={}
    for v,years in graphs.items():
        solutions[v]={};counts=Counter()
        for y,g in years.items():
            forced,components=solve(g)
            solutions[v].update({(y,p):m for p,m in forced.items()})
            counts.update({'personas_anio':len(g),'sin_candidato':sum(not ids for ids in g.values()),'pares_forzados_condicionales':len(forced),'maximo_pares':sum(c['maximo_pares'] for c in components)})
        graph_summary[v]=dict(counts)
    cases=[];ev={v:Counter() for v in solutions}
    for n,p in enumerate(d['sample'],1):
        a=d['anchors'][p];y=int(a['ANOMATRICULA']);target=d['adjudicated'].get((y,p))
        rr={'caso':f'ENSAYO-{n:03d}','anio':y,'codcarpr':token(a['CODCARPR']),'variantes':{}}
        for v,sol in solutions.items():
            m=sol.get((y,p))
            status='SIN_ENLACE_FORZADO' if not m else 'ENLACE_SIN_REFERENCIA_UNIVOCA' if not target else 'CONCUERDA_CON_REFERENCIA' if target==m else 'CONTRADICE_REFERENCIA'
            ev[v][status]+=1;rr['variantes'][v]={'estado':status,'candidatos':len(graphs[v][y].get(p,set()))}
        cases.append(rr)
    totals=[]
    for y in range(2007,2027):
        mr=[r for r in d['rawmr'] if year(r['cat_periodo'])==y]
        refs=[r for r in d['references'] if r['year']==y]
        rp={r['person'] for r in refs if r['person']}
        persons={token(r['mrun']) for r in mr if token(r['mrun'])}
        totals.append({'anio':y,'umas_anomatricula':len(annual[y]['ANOMATRICULA']),'umas_actividad':len(annual[y]['ACTIVIDAD_ACADEMICA']),
            'umas_union':len(annual[y]['union']),'filas_mrun':len(mr),'personas_mrun':len(persons),
            'filas_reporte_documental':len(refs) if y in YEARS else None,'personas_reporte_documental':len(rp) if y in YEARS else None,
            'filas_reporte_documento_no_normalizable':sum(not r['person'] for r in refs) if y in YEARS else None,
            'personas_reporte_presentes_datosalumnos':len(rp & byperson.keys()) if y in YEARS else None,
            'reporte_con_presencia_anual_umas':len(rp & annual[y]['union']) if y in YEARS else None,
            'reporte_sin_presencia_anual_umas':len(rp-annual[y]['union']) if y in YEARS else None,
            'presencia_umas_fuera_reporte':len(annual[y]['union']-rp) if y in YEARS else None})
    # La carrera del reporte se usa SOLO para auditar cobertura, nunca en el grafo.
    membership=Counter();demographic=Counter()
    from scripts.fuentes_ensayo_enlace_conjunto import dateym
    for r in d['references']:
        p=r['person'];y=r['year'];family=r['code'].rsplit('V',1)[0]
        candidates=[]
        for a in byperson.get(p,[]):
            g=d['groups'].get(clave_grupo(token(a['CODCARPR']),token(a['SEDE']),token(a['JORNADA'])))
            if g and family in g['familias']:candidates.append(a)
        active=[a for a in candidates if (a['_fila'],y) in evidence]
        status='DOCUMENTO_REPORTE_NO_NORMALIZABLE' if not p else 'MISMA_FAMILIA_CON_PRESENCIA_ANUAL' if active else 'MISMA_FAMILIA_SIN_PRESENCIA_ANUAL' if candidates else 'PERSONA_SIN_FAMILIA_COMPATIBLE' if p in byperson else 'PERSONA_AUSENTE_UMAS'
        membership[y,status]+=1
        if candidates:
            matches=[a for a in candidates if dateym(a['FECHANACIMIENTO'])==r['birth'] and token(a['SEXO']).upper()==r['sex'] and r['birth'] and r['sex']]
            demographic['COINCIDE_NACIMIENTO_SEXO' if matches else 'DIFIERE_O_FALTA_NACIMIENTO_SEXO']+=1
    cohort_counts={side:defaultdict(set) for side in ('reporte','mrun')}
    for r in d['references']:
        if r['person']:cohort_counts['reporte'][r['year'],r['code'],r['ori'],r['sex'] or 'NO_COMPARABLE'].add(r['person'])
    for r in d['mr']:
        if r['mrun']:cohort_counts['mrun'][r['year'],r['code'],r['ori'],r['sex'] or 'NO_COMPARABLE'].add(r['mrun'])
    cohort_panels=[dict(zip(('anio','codigo_sies','ingreso_original','sexo'),k), personas_reporte=len(cohort_counts['reporte'][k]), personas_mrun=len(cohort_counts['mrun'][k])) for k in sorted(cohort_counts['reporte'].keys() | cohort_counts['mrun'].keys())]
    summary={'paneles_cohorte_documental_mrun':len(cohort_panels),'paneles_con_totales_iguales':sum(p['personas_reporte']==p['personas_mrun'] for p in cohort_panels),'fuentes_academicas':source_stats,'totales_anuales':totals,'grafo_ampliado':graph_summary,
             'evaluacion_500':{v:dict(c) for v,c in ev.items()},'control_demografico_filas_reporte':dict(demographic),
             'cobertura_carrera_reporte':[{'anio':k[0],'estado':k[1],'filas':v} for k,v in sorted(membership.items())],
             'limites':['Actividad no equivale a matrícula al corte SIES.','No hay actividad 2007–2018 acreditada por estas fuentes.','Atributos de sede/jornada de DatosAlumnos actuales no acreditan invariancia histórica.','Familias compartidas no certifican la versión ni separación regular/continuidad.'],
             'identidades_certificadas':0}
    for p,h in sources.items():assert sha(Path(p) if Path(p).is_absolute() else ROOT/p)==h,p
    protected=json.loads((ROOT/'data/unificacion_proyectos/20261015/control_preservacion_final.json').read_text())['referencias_sha256']
    for p,h in protected.items():assert sha(ROOT/p)==h,p
    x=json.loads((ROOT/'data/versiones_historicas_sies_umas/fase_8_20261015/entrega.json').read_text())['archivo']
    assert sha(x)=='f6431d9bf571a4db0769cf8f4d5b90eee95413477406ddf9a328e657a85298dd'
    assert len(cases)==500
    OUT.mkdir(parents=True,exist_ok=True)
    outputs={'cohortes_reporte_mrun.json':cohort_panels,'resumen.json':summary,'casos_500.json':cases,'presencia_por_carrera.json':[dict(zip(('anio','codcarpr','sede','jornada','evidencia'),k),personas=len(v)) for k,v in sorted(career.items())],
      'qa.json':{'referencias_preservadas':len(protected),'excel_intacto':True,'personas_muestra_distintas':len(set(d['sample'])),'sin_identificadores_exportados':True}}
    for n,v in outputs.items():(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
    for p in ('scripts/reconstruir_presencia_anual.py','common/presencia_anual.py','scripts/fuentes_ensayo_enlace_conjunto.py','scripts/diagnosticar_enlace_conjunto.py','common/enlace_conjunto.py','tests/test_presencia_anual.py'):sources[p]=sha(ROOT/p)
    (OUT/'manifest.json').write_text(json.dumps({'fuentes_y_codigo_sha256':sources,'salidas_sha256':{n:sha(OUT/n) for n in outputs}},ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k!='fuentes_academicas'},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
