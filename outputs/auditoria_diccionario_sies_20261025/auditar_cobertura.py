import collections, json, sys, hashlib
from pathlib import Path
R=Path('/Users/alexi/Documents/GitHub/avance_curricular')
sys.path.insert(0,str(R))
from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento, sha256
O=Path(__file__).resolve().parent/'insumos'; O.mkdir(exist_ok=True)
s=DiccionarioSiesSeguimiento()
rows=[json.loads(x[0]) for x in s.db.execute('SELECT payload FROM observaciones ORDER BY id')]
families=collections.defaultdict(set)
for code, in s.db.execute('SELECT DISTINCT codigo FROM mu_anual'):
    families[code.rsplit('V',1)[0]].add(code)
multi={f for f,c in families.items() if len(c)>1}
is_multi=lambda r:any(c.rsplit('V',1)[0] in multi for c in r['codigos_anuales_documentados']+r['candidatos_calculados'] if isinstance(c,str))
def status_group(rs,field):
    n=sum(bool(r[field]) for r in rs)
    return 'Completa' if n==len(rs) else 'Parcial' if n else 'Sin resolver'
def groups(keys,rs):
    g=collections.defaultdict(list)
    for r in rs:g[tuple(r[k] for k in keys)].append(r)
    return g
def coverage(rs):
    return {'observaciones':len(rs),'documentadas':sum(bool(r['codigo_documental_atribuible']) for r in rs),
            'solo_internas':sum(bool(r['codigo_interno_adoptado']) and not r['codigo_documental_atribuible'] for r in rs),
            'pendientes':sum(not r['codigo_interno_adoptado'] for r in rs),
            'personas':len({r['persona'] for r in rs}),
            'personas_con_pendiente':len({r['persona'] for r in rs if not r['codigo_interno_adoptado']}),
            'estados_pendientes':dict(collections.Counter(r['estado_interno'] for r in rs if not r['codigo_interno_adoptado']))}
def combination_records(keys,rs):
    out=[]
    for key,gr in sorted(groups(keys,rs).items()):
        codes=sorted({r['codigo_interno_adoptado'] for r in gr if r['codigo_interno_adoptado']})
        fs={c.rsplit('V',1)[0] for c in codes}
        o={**dict(zip(keys,key)),**coverage(gr),'estado':status_group(gr,'codigo_interno_adoptado'),
           'estado_documental':status_group(gr,'codigo_documental_atribuible'),
           'codigos_respaldados':codes,'familias_respaldadas':sorted(fs),
           'varias_versiones_en_familia':any(len({c for c in codes if c.rsplit('V',1)[0]==f})>1 for f in fs),
           'en_foco_multiversion':any(is_multi(r) for r in gr),
           'anios':sorted({r['ano'] for r in gr}), 'periodos':sorted({r['periodo'] for r in gr})}
        out.append(o)
    return out
def distribution(keys,field):
    return dict(collections.Counter(status_group(rs,field) for rs in groups(keys,rows).values()))
base_keys=['carrera','plan','sede_dimension','jornada_sies']
comb=combination_records(base_keys,rows)
timecomb=combination_records(base_keys+['ano','periodo'],rows)
for c in comb:
    child=[t for t in timecomb if all(t[k]==c[k] for k in base_keys)]
    c['periodos_con_mas_un_codigo']=sum(len(t['codigos_respaldados'])>1 for t in child)
    c['periodos_con_varias_versiones_misma_familia']=sum(t['varias_versiones_en_familia'] for t in child)
    c['necesita_contexto_personal']=bool(c['periodos_con_mas_un_codigo'])
    c['pendiente_concreto']=' | '.join({
      'SIN_EVIDENCIA_ANUAL_APLICABLE':'Vincular el código al expediente y período; no basta un código de otro año ni la coincidencia de totales.',
      'CODIGO_ANUAL_SIN_CONTEXTO_DA_EXACTO':'Recuperar el contexto DatosAlumnos concordante (carrera, plan, sede y jornada).',
      'CONTRADICCION_O_ATRIBUCION_MULTIPLE':'Atribuir la matrícula anual al expediente/plan correcto y ubicar los cambios de contexto.',
      'HOMOLOGACION_EN_PLAN_RECHAZADO_SIN_VERSION':'Acreditar plan realmente cursado; la homologación en un plan rechazado no confirma versión.'
      }[k] for k in c['estados_pendientes']) or 'Sin excepciones en las observaciones revisadas; no autoriza extrapolar a otra persona o período.'
focus=[r for r in rows if is_multi(r)]
queries=collections.Counter(); mismatches=0; conflicts=0
for r in rows:
    q=s.consultar(persona=r['persona'],codcli=r['CODCLI'],plan=r['plan'],anio=r['ano'],periodo=r['periodo'],carrera=r['carrera'],sede=r['sede_dimension'],jornada=r['jornada_sies'])
    queries[q['nivel_respaldo']]+=1
    mismatches+=(q['codigo_sies'] or '') != r['codigo_interno_adoptado']
    conflicts+=bool(r['codigo_documental_atribuible'] and r['codigo_interno_adoptado'] and r['codigo_documental_atribuible']!=r['codigo_interno_adoptado'])
summary={'clasificacion':'B/C observado y recalculado; D cierres internos autorizados; E pendientes',
    'edicion':s.edicion,'descriptor':str(R/json.loads((R/'data/diccionario_sies_seguimiento/activo.json').read_text())['descriptor']),
    'base_privada_sha256':s.descriptor['base_privada']['sha256'],
    'universo':coverage(rows),'personas_estado_interno':distribution(['persona'],'codigo_interno_adoptado'),
    'personas_estado_documental':distribution(['persona'],'codigo_documental_atribuible'),
    'expedientes_estado_interno':distribution(['carrera','CODCLI'],'codigo_interno_adoptado'),
    'combinacion_definicion':base_keys,'combinaciones':len(comb),
    'combinaciones_estado':dict(collections.Counter(x['estado'] for x in comb)),
    'combinaciones_estado_documental':dict(collections.Counter(x['estado_documental'] for x in comb)),
    'combinaciones_varias_versiones_respaldadas':sum(x['varias_versiones_en_familia'] for x in comb),
    'combinaciones_con_mas_un_codigo':sum(len(x['codigos_respaldados'])>1 for x in comb),
    'combinaciones_con_mas_un_codigo_mismo_periodo':sum(x['necesita_contexto_personal'] for x in comb),
    'combinaciones_completas_con_mas_un_codigo_mismo_periodo':sum(x['estado']=='Completa' and x['necesita_contexto_personal'] for x in comb),
    'combinaciones_completas_con_mas_un_codigo_historia':sum(x['estado']=='Completa' and len(x['codigos_respaldados'])>1 for x in comb),
    'combinaciones_periodo':len(timecomb),'combinaciones_periodo_estado':dict(collections.Counter(x['estado'] for x in timecomb)),
    'combinaciones_periodo_con_mas_un_codigo':sum(len(x['codigos_respaldados'])>1 for x in timecomb),
    'combinaciones_periodo_varias_versiones_respaldadas':sum(x['varias_versiones_en_familia'] for x in timecomb),
    'codigos_carrera_umas':len({r['carrera'] for r in rows}),
    'carreras_con_pendientes':len({r['carrera'] for r in rows if not r['codigo_interno_adoptado']}),
    'planes_distintos':len({r['plan'] for r in rows}),
    'anios':sorted({r['ano'] for r in rows}),'periodos_nativos':sorted({r['periodo'] for r in rows}),
    'familias_multiversion_en_evidencia':len(multi),'foco_multiversion':coverage(focus),
    'foco_multiversion_combinaciones':len([c for c in comb if c['en_foco_multiversion']]),
    'foco_multiversion_combinaciones_con_pendientes':sum(c['en_foco_multiversion'] and c['pendientes']>0 for c in comb),
    'indice_mu_filas':s.db.execute('select count(*) from mu_anual').fetchone()[0],
    'qa_consultas':{'total':len(rows),'respuestas':dict(queries),'diferencias':mismatches,'conflictos_doc_interno':conflicts,
                    'integridad_sqlite':s.db.execute('pragma integrity_check').fetchone()[0],
                    'identificadores_observacion_unicos':len({r['observacion_id'] for r in rows})==len(rows),
                    'contextos_unicos':len(groups(['persona','CODCLI','plan','ano','periodo','carrera','sede_dimension','jornada_sies'],rows))==len(rows)},
    'campos_respaldo':{k:dict(collections.Counter(str(r[k]) for r in rows)) for k in ['aceptacion_SIES','fecha_efectiva_plan','cambio_plan_efectivo_acreditado','estado_documental','estado_interno']}}
career=combination_records(['carrera'],rows)
year=combination_records(['ano'],rows)
reasons=[]
for reason,gr in sorted(groups(['estado_interno'],[r for r in rows if not r['codigo_interno_adoptado']]).items()):
    reasons.append({'motivo':reason[0],**coverage(gr),'combinaciones_afectadas':len(groups(base_keys,gr)),
        'carreras_afectadas':len({r['carrera'] for r in gr})})
requirements=[]
for requirement,gr in sorted(groups(['requisito_pendiente'],[r for r in rows if not r['codigo_interno_adoptado']]).items()):
    requirements.append({'requisito_pendiente':requirement[0],**coverage(gr),
        'combinaciones_afectadas':len(groups(base_keys,gr))})
summary['pendientes_por_estado_propuesta']=dict(collections.Counter(r['estado_propuesta'] for r in rows if not r['codigo_interno_adoptado']))
maestro_path=R/'data/versiones_historicas_sies_umas/fase_5_20261015/maestro.json'
maestro=json.loads(maestro_path.read_text())
names=collections.defaultdict(set)
for e in maestro['equivalencias_programa_2026']:
    if e.get('nombre_interno'):names[e['codcarpr']].add(e['nombre_interno'])
names_report={'fuente':str(maestro_path),'sha256':sha256(maestro_path),'alcance':'Etiquetas de equivalencias_programa_2026 por CODCARPR exacto; no equivalencia nueva ni acreditación del nombre histórico; vacíos sin etiqueta localizada en esta tabla','nombres_por_codigo':{ca:sorted(names[ca]) for ca in sorted({r['carrera'] for r in rows})}}
secrets={r['persona'] for r in rows}|{r['CODCLI'] for r in rows}
for name,obj in [('resumen.json',summary),('combinaciones.json',comb),('combinaciones_periodo.json',timecomb),('carreras.json',career),('anios.json',year),('motivos.json',reasons),('requisitos.json',requirements),('nombres_catalogo.json',names_report)]:
    t=json.dumps(obj,ensure_ascii=False,indent=2)+'\n'
    assert not any(v and v in t for v in secrets),'Privacidad: identificador inesperado'
    (O/name).write_text(t)
s.close()
print(json.dumps(summary,ensure_ascii=False,indent=2))
