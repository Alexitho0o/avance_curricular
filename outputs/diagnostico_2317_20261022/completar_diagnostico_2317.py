import json,csv
from pathlib import Path
from collections import Counter,defaultdict
R=Path.cwd();O=R/'outputs/diagnostico_2317_20261022';q=json.load(open(O/'DIAGNOSTICO.json'));x=json.load(open('/tmp/ipss_revision_63_20261022/payload.json'));u=next(s['rows'] for s in x if s['name']=='CONTRASTE_63');e=[r for r in u if r[10]=='DIFIERE_CODIGO_PROPUESTO_OBSERVADO'];cand=defaultdict(set)
for r in csv.DictReader(open(R/'data/reglas_negocio/20261022_puente_versiones/PUENTE_VERSIONES_PLAN_UMAS_SIES_20261022.csv',encoding='utf-8-sig')):cand[r['codcarpr_interno'],r['sede'],r['jornada_catalogo']].add(r['codigo_unico_sies_candidato'])
groups=defaultdict(list)
for r in e:groups['OBSERVADO_FUERA_CANDIDATOS_ORIGINALES' if r[9] not in cand[r[2],r[3],r[4]] else 'OBSERVADO_ENTRE_CANDIDATOS_NO_PREDOMINANTE'].append(r)
q['diferencias_causa_comprobable']={k:{'observaciones':len(v),'personas':len({r[0] for r in v}),'por_ano':dict(Counter(r[6] for r in v))} for k,v in groups.items()}
labels={'CONTRADICCION_O_ATRIBUCION_MULTIPLE':'ATRIBUCION_MULTIPLE_CON_CODIGO_UNICO','SIN_EVIDENCIA_ANUAL_APLICABLE':'SIN_ANUAL','CODIGO_ANUAL_SIN_CONTEXTO_DA_EXACTO':'SIN_DA','DIFIERE_CODIGO_PROPUESTO_OBSERVADO':'DIFIERE_PROPUESTA'};gg=defaultdict(list)
for r in u:
 if r[10] in labels:gg[r[2],r[6],r[4],labels[r[10]]].append(r)
with open(O/'CAUSA_CARRERA_ANO_JORNADA.csv','w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['carrera','ano','jornada','causa','personas','expedientes','observaciones'])
 for k,v in sorted(gg.items()):w.writerow([*k,len({r[0] for r in v}),len({(r[2],r[1]) for r in v}),len(v)])
q['carreras_distintas_foco']=len({r[2] for r in u if r[10] in labels});q['jornadas_distintas']=3
# Auditoría: n3, mayoría, tipo/duración, plan literal y VIG no fueron filtros de código anual V6.
q['auditoria_reglas']={'lector_multiproceso':'mismo inventario38 y lector de V2; universo ampliado','recuperacion_historica':'identidad exacta, documentos R/1/RUT o campo tipo ausente; código completo; sin filtro previo año/familia','etapa_anual_adicional':'solo proceso MATRICULA con MC_CAT_PERIODO o ANIO_INFORMADO explícito igual a año PR, familia SIES y DA del corte','plan_literal_filtra':False,'vig_filtra':False,'minimo3_filtra':False,'predominancia90_filtra':False,'tipo_duracion_filtran':False,'DA_y_atribucion':'controles de vinculación del expediente; no implican que código no exista','temporalidad_respaldo':'docs/fase_4_planes_asignaciones_umas.md puntos4–7','fuente_primaria':'etiquetas de Publicados/Enviados no certifican aceptación; MU consolidada derivada admitida como base gobernada; retención derivada no añade evidencia anual independiente'}
(O/'DIAGNOSTICO.json').write_text(json.dumps(q,ensure_ascii=False,indent=2));print(json.dumps({'carreras':q['carreras_distintas_foco'],'diferencias':q['diferencias_causa_comprobable']},ensure_ascii=False))
