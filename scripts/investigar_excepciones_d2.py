#!/usr/bin/env python3
"""Investiga contextos D1 con fuentes B5; publica solo evidencia académica agregada."""
import csv,json,sys
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.fuentes_reglas_b5 import cargar_base_b4
from scripts.fuentes_ensayo_enlace_conjunto import doc,token,sha,year
from scripts.reconstruir_planes_umas import read_sheet
from common.continuidad_trayectoria import evaluar_trayectorias
from common.versiones_por_cohorte import clave_grupo
OUT=ROOT/'data/cierre_d2/20261016'
def load(p):return json.loads((ROOT/p).read_text())
def save(n,x):(OUT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
def admision(offer,y,code):
    r=offer.get((y,code)) if y else None
    if not r:return 'SIN_OFERTA_ANUAL'
    v=r['vigencia'].lower()
    return 'SOLO_ANTIGUOS' if 'sin estudiantes nuevos' in v else 'ADMITE_NUEVOS' if 'con estudiantes nuevos' in v else 'VIGENCIA_NO_INTERPRETADA'
def main():
    prior=load('data/reglas_historicas_b5/20261016/manifest.json')
    for path,digest in prior['fuentes_y_codigo_sha256'].items():assert sha(Path(path) if Path(path).is_absolute() else ROOT/path)==digest,path
    print('Fuentes B5 verificadas; reconstruyendo evidencia en memoria.',flush=True)
    b=cargar_base_b4();d=b['d'];ctx=b['ctx'];sources=dict(b['sources'])
    matrix=load('data/matriz_academica_b4/20261016/matriz_contextos.json')
    index={(c['codcarpr'],c['sede_umas'],c['jornada_umas'],c['anio_observado'],c['ingreso_original_declarado'],c['primer_anio_observado_en_carrera'],tuple(c['planes_observados'])):c for c in matrix}
    queue=load('data/cierre_d1/20261016/cola_prioridad_1.json');target={q['expediente'] for q in queue}
    rr=defaultdict(list)
    for r in d['references']:
        if r['person']:rr[r['year'],r['person']].append(r)
    grouped=defaultdict(lambda:defaultdict(set));allpeople=defaultdict(set);linkedpeople=defaultdict(set);rows_context=defaultdict(set)
    for (row,y),flags in ctx['evidence'].items():
        r=ctx['byrow'][row];p=doc(r['RUT']);g=b['rowgroups'][row]
        if not g:continue
        key=(token(r['CODCARPR']),token(r['SEDE']),token(r['JORNADA']),y,token(r['ANOINGRESO']),b['episodes'][p,token(r['CODCARPR'])],tuple(sorted(b['plans'][row,y])))
        c=index[key];cid=c['contexto']
        rows_context[cid].add(row)
        if cid not in target:continue
        allpeople[cid].add(p)
        refs=[x for x in rr[y,p] if x['code'].rsplit('V',1)[0] in g['familias'] and len(b['possible_programs'][p,x['code'].rsplit('V',1)[0]])==1]
        for ref in refs:
            linkedpeople[cid].add(p)
            act=year(ref['act']);ori=year(ref['ori']);code=ref['code']
            sig=(code,ref['ori'],ref['act'],ref['semori'],ref['semact'],admision(b['offer'],y,code),admision(b['offer'],act,code),
                 token(r['ANOMATRICULA']),token(r['ESTADOACADEMICO']),token(r['SITUACION']))
            grouped[cid][sig].add(p)
    dossiers=[]
    for c in matrix:
        cid=c['contexto']
        if cid not in target:continue
        slices=[]
        for k,people in sorted(grouped[cid].items()):
            fields=['codigo','ingreso_original_sies','ingreso_actual_sies','semestre_original_sies','semestre_actual_sies','admision_anio_observado','admision_anio_ingreso_actual','anomatricula_extracto_umas','estado_actual_umas','situacion_actual_umas']
            slices.append(dict(zip(fields,k),personas=len(people)))
        # ¿Los años de ingreso actual/original del reporte separan destinos? Diagnóstico, no regla UMAS.
        partitions={}
        for fields in [('ingreso_actual_sies',),('ingreso_original_sies','ingreso_actual_sies')]:
            parts=defaultdict(set)
            for s in slices:parts[tuple(s[f] for f in fields)].add(s['codigo'])
            partitions['+'.join(fields)]={'grupos':len(parts),'grupos_multicodigo':sum(len(v)>1 for v in parts.values())}
        patterns=sorted({s['admision_anio_observado'] for s in slices})
        admission_conflicts=sum(s['personas'] for s in slices if s['admision_anio_ingreso_actual']=='SOLO_ANTIGUOS')
        dossiers.append({'contexto':cid,'clave_b4':{k:c[k] for k in ('codcarpr','sede_umas','jornada_umas','anio_observado','ingreso_original_declarado','primer_anio_observado_en_carrera','planes_observados')},
            'personas_contexto':len(allpeople[cid]),'personas_con_reporte_atribuible':len(linkedpeople[cid]),'personas_sin_reporte_atribuible':len(allpeople[cid]-linkedpeople[cid]),'detalle_agregado':slices,'particiones_diagnosticas':partitions,
            'oferta_destinos':c['relaciones_sies'],'patrones_admision_en_observacion':patterns,
            'observaciones_persona_estrato_ingreso_en_solo_antiguos':admission_conflicts,
            'conclusion':'COEXISTENCIA_NUEVOS_ANTIGUOS_OBSERVADA_SIN_REGLA_UMAS' if {'ADMITE_NUEVOS','SOLO_ANTIGUOS'}<=set(patterns) else 'MULTIPLICIDAD_NO_EXPLICADA_SOLO_POR_VIGENCIA',
            'estado_cierre_investigacion':'NO_DETERMINABLE_MALLA_CON_FUENTES_ACTUALES',
            'pendiente':'Historial de ingreso/plan/sede/jornada del episodio y contraste del reporte por su corte. Los campos SIES no son entradas UMAS equivalentes acreditadas.',
            'estado_umas_es_actual_no_historico':True,'asignacion_habilitada':False})
    print('16 expedientes contrastados; investigando CILOG.',flush=True)
    # Misma fuente 12023 que B4, sin confundirla con muestra previa 11998.
    levels=defaultdict(set)
    for r in csv.DictReader((ROOT/'DURACION_ESTUDIOS.tsv').open(),delimiter='\t'):levels[r['CODIGO_UNICO']].add(r['NIVEL_CARRERA'])
    observed=defaultdict(set)
    for row,y in ctx['evidence']:observed[row].add(y)
    records=[]
    for r in d['da']:
        g=b['rowgroups'][r['_fila']];types={p[1] for p in g['perfiles_duracion_tipo']} if g else set()
        lev={x for code in (g['codigos_base'] if g else []) for x in levels[code]}
        records.append(dict(indice=r['_fila'],persona=doc(r['RUT']),codcli=token(r['CODCLI']),carrera=token(r['CODCARPR']),continuidad=types=={'3'},tecnico=lev=={'1'},anios_observados=sorted(observed[r['_fila']]),anoingreso=token(r['ANOINGRESO'])))
    evaluated={r['indice']:r for r in evaluar_trayectorias(records)}
    cilog=[r for r in d['da'] if token(r['CODCARPR'])=='CILOG'];sample=[r for r in cilog if year(r['ANOMATRICULA'])]
    counts=Counter();origins=Counter();states=Counter();situations=Counter()
    for r in sample:
        row=r['_fila'];ev=evaluated[row];origins[ev['origen']]+=1;states[token(r['ESTADOACADEMICO'])]+=1;situations[token(r['SITUACION'])]+=1
        academic=sorted(y for (i,y),flags in ctx['evidence'].items() if i==row and 'ACTIVIDAD_ACADEMICA' in flags)
        plans=sorted({p for (i,y),ps in b['plans'].items() if i==row for p in ps})
        k=(token(r['ANOINGRESO']),token(r['ANOMATRICULA']),ev['primer_anio_observado_carrera'],ev['origen'],tuple(academic),tuple(plans),token(r['ESTADOACADEMICO']),token(r['SITUACION']))
        counts[k]+=1
    strata=[dict(zip(['ingreso_original','anomatricula','primera_observacion_carrera','origen','actividad_verificada','planes_observados','estado_actual','situacion_actual'],k),filas=v) for k,v in sorted(counts.items(),key=lambda x:str(x[0]))]
    logistic=[r for r in b['master']['oferta_anual'] if r['codigo_unico'].startswith('I162S2C77')]
    # MRUN agregado independiente 2024–2026: sin enlazarlo a identidad UMAS.
    mr_counts=Counter()
    for r in d['rawmr']:
        if r['codigo_unico'].startswith('I162S2C77'):
            y=year(r['cat_periodo']);code=r['codigo_unico']
            mr_counts[(y,code,r['anio_ing_carr_ori'],r['anio_ing_carr_act'],admision(b['offer'],y,code),admision(b['offer'],year(r['anio_ing_carr_act']),code))]+=1
    mr_strata=[dict(zip(['anio','codigo','ingreso_original','ingreso_actual','admision_anio_observado','admision_ingreso_actual'],k),filas_mrun=v) for k,v in sorted(mr_counts.items(),key=lambda x:str(x[0]))]
    cilog_summary={'fuente':d['sm'],'filas_total_cilog':len(cilog),'filas_hasta_2026':len(sample),'personas_hasta_2026':len({doc(r['RUT']) for r in sample if doc(r['RUT'])}),'expedientes_hasta_2026':len({token(r['CODCLI']) for r in sample}),
        'fuera_ambito_anomatricula':len(cilog)-len(sample),'origen_filas':dict(origins),'estado_actual_filas':dict(states),'situacion_actual_filas':dict(situations),
        'contextos_b4':[c['contexto'] for c in matrix if c['codcarpr']=='CILOG'],'estratos':strata,
        'conclusion':'CILOG_CONTINUIDAD_SEPARADO_DE_ILOG_REGULAR_CON_INCIDENCIAS_TEMPORALES','perfil_cilog':{'duracion_total_semestres':'4','tipo_plan':'3','codigo_perfil':'I162S2C77J4V2'},'perfil_ilog_online':{'duracion_total_semestres':'8','tipo_plan':'1','codigo_perfil':'I162S2C77J4V1'},'inicio_efectivo_confirmado':False,'procedencia_externa_certificada':False,'asignacion_habilitada':False}
    for path,digest in sources.items():assert sha(Path(path) if Path(path).is_absolute() else ROOT/path)==digest,path
    for path,digest in prior['fuentes_y_codigo_sha256'].items():assert sha(Path(path) if Path(path).is_absolute() else ROOT/path)==digest,path
    save('expedientes_16.json',dossiers);save('cilog.json',cilog_summary);save('logistica_oferta_anual.json',logistic);save('logistica_mrun_cohortes.json',mr_strata)
    summary={'hito':'D2','expedientes':len(dossiers),'conclusiones':dict(Counter(x['conclusion'] for x in dossiers)),'expedientes_ingreso_solo_antiguos':[x['contexto'] for x in dossiers if x['observaciones_persona_estrato_ingreso_en_solo_antiguos']],
      'cilog_filas_hasta_2026':len(sample),'cilog_origen':dict(origins),'asignaciones_activadas':0,'identificadores_exportados':False}
    save('resumen_investigacion.json',summary)
    for name in ('data/matriz_academica_b4/20261016/matriz_contextos.json','data/cierre_d1/20261016/cola_prioridad_1.json','DURACION_ESTUDIOS.tsv','scripts/investigar_excepciones_d2.py','common/continuidad_trayectoria.py'):sources[name]=sha(ROOT/name)
    save('manifest_investigacion.json',{'fuentes_sha256':sources,'salidas_sha256':{n:sha(OUT/n) for n in ['expedientes_16.json','cilog.json','logistica_oferta_anual.json','logistica_mrun_cohortes.json','resumen_investigacion.json']}})
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
