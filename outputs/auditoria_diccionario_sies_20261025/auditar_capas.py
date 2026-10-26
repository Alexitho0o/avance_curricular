from pathlib import Path
import json,hashlib,collections,openpyxl
import sys
R=Path('/Users/alexi/Documents/GitHub/avance_curricular')
P=Path('/Users/alexi/Desktop/RETENCION_IPSS_SEGUIMIENTO_T1_T2_T3_20261024_V17.xlsx')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads((R/p).read_text())
out={'clasificacion':'B observado; C recálculo agregado; D decisiones conservadas; E pendientes','fuentes':{}}
paths=['data/diccionario_sies_seguimiento/activo.json','data/diccionario_sies_seguimiento/v7_20261023_inf35_03_t3/descriptor.json','data/diccionario_sies_seguimiento/v7_20261023_inf35_03_t3/RESUMEN.json','data/consumo_comun_c2/20261016/descriptor.json','data/reglas_historicas_b5/20261016/reglas_observadas.json','data/diccionario_c1/20261016/entrega.json','data/versiones_por_cohorte/20261016/resumen.json','outputs/seguimiento_t1_hasta_2026_20261023_v13/MANIFEST_SEGUIMIENTO.json','outputs/seguimiento_t1_hasta_2026_20261023_v13/TABLAS_SEGUIMIENTO.json','outputs/seguimiento_t1_hasta_2026_20261023_v13/FOCO_MULTIVERSION.json','outputs/pendientes_entrega_20261024_v17/QA_Y_MANIFEST.json']
out['fuentes']={str(R/p):sha(R/p) for p in paths};out['fuentes'][str(P)]=sha(P)
rules=read(paths[4]);out['c2']={'reglas':len(rules),'habilitadas':sum(bool(x['habilitada_para_resolver']) for x in rules),'estados':dict(collections.Counter(x['estado'] for x in rules)),'asignacion_productiva':False,'edicion':'C2_20261016'}
out['cohorte_oferta_20261016']=read(paths[6])
tb=read(paths[8]); f=read(paths[9]); w=openpyxl.load_workbook(P,read_only=True,data_only=True)
actual=[list(row) for row in w['54_Contextos_y_Pendientes'].iter_rows(min_row=6,values_only=True) if len(row)>=14 and isinstance(row[13],(int,float))]
out['v17']={'sha256':sha(P),'hojas':len(w.sheetnames),'contextos_filas_agregadas':len(actual),'tabla54_identica_a_tablas_v13':actual==tb['contextos'],'diccionario_origen':read(paths[7])['diccionario'],'contextos':sum(r[13] for r in actual),'estados':dict(collections.Counter())}
for k in set(r[8] for r in actual):out['v17']['estados'][k]=sum(r[13] for r in actual if r[8]==k)
out['v17']['foco_multiversion']=f
pending=[r for r in actual if r[8].startswith('E')]
key_defs={'carrera_umas_plan':lambda r:(r[4],r[5]),'carrera_umas_plan_ano_periodo':lambda r:(r[4],r[5],r[1],r[2]),'codigo_origen_plan_ano_periodo':lambda r:(r[6],r[5],r[1],r[2])}
out['v17']['combinaciones']={name:{'total':len({fn(r) for r in actual}),'con_pendientes':len({fn(r) for r in pending})} for name,fn in key_defs.items()}
by=collections.defaultdict(lambda:collections.Counter())
for r in actual:
 k=(r[4],r[5]);by[k]['observaciones']+=r[13];by[k]['pendientes']+=r[13] if r[8].startswith('E') else 0
out['v17']['planes_con_pendientes']=[{'carrera_umas':k[0],'plan':k[1],**dict(v),'razones':sorted(set(r[9] for r in pending if (r[4],r[5])==k))} for k,v in sorted(by.items()) if v['pendientes']]
private=Path('/Users/alexi/.local/share/ipss/destinos_calendario_v7_20261023/CONTEXTOS_POR_ORIGEN_PERIODO.json')
pr=json.loads(private.read_text());out['fuentes'][str(private)]=sha(private)
sys.path.insert(0,str(R))
from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento
service=DiccionarioSiesSeguimiento()
qdiff=0
for row in pr:
 response=service.consultar(persona=row['persona'],codcli=row['codcli'],plan=row['plan'],anio=row['anio_observado'],periodo=row['periodo_nativo'],carrera=row['carrera_umas'],sede=row['sede_observada'],jornada=row['jornada_observada'])
 qdiff+= (response['codigo_sies'] or '')!=(row['codigo_destino'] or '') or response['nivel_respaldo']!=row['estado_destino']
service.close()
mf={r['familia_origen'] for r in f['por_familia']}
po=[r for r in pr if r['estado_destino']=='E_PENDIENTE'];pm=[r for r in po if r['codigo_origen_T1'].rsplit('V',1)[0] in mf]
out['v17']['qa_reconsulta_actual']={'consultas':len(pr),'diferencias':qdiff,'observaciones_id_distintas':len({r['observacion_id'] for r in pr}),'personas_distintas':len({r['persona'] for r in pr}),'pendientes_observaciones':len(po),'pendientes_personas_distintas':len({r['persona'] for r in po}),'pendientes_multiversion_observaciones':len(pm),'pendientes_multiversion_personas_distintas':len({r['persona'] for r in pm})}
groups=collections.defaultdict(list)
for r in pr:groups[(r['carrera_umas'],r['sede_observada'],r['jornada_observada'],r['plan'],r['anio_observado'],r['periodo_nativo'])].append(r)
grows=[]
for k,rs in sorted(groups.items()):
 ps=[r for r in rs if r['estado_destino']=='E_PENDIENTE']
 grows.append(dict(zip(['carrera_umas','sede_observada','jornada_sies_observada','plan','anio_observado','periodo_nativo'],k))|{'observaciones':len(rs),'documentales':sum(bool(r['codigo_documental']) for r in rs),'internos':sum(bool(r['codigo_interno']) and not r['codigo_documental'] for r in rs),'pendientes':len(ps),'pendientes_multiversion':sum(r['codigo_origen_T1'].rsplit('V',1)[0] in mf for r in ps),'codigos_origen':sorted({r['codigo_origen_T1'] for r in rs}),'codigos_destino':sorted({r['codigo_destino'] for r in rs if r['codigo_destino']}),'motivos_pendientes':sorted({r['tipo_pendiente'] or r['relacion_codigo'] for r in ps}),'requisito_pendiente':sorted({r['pendiente'] for r in ps})})
out['v17']['combinaciones_contextuales']=grows
out['v17']['resumen_combinaciones_contextuales']={'definicion':'carrera UMAS+sede observada+jornada SIES observada+plan+año observado+período nativo','total':len(grows),'con_pendientes':sum(r['pendientes']>0 for r in grows),'con_pendientes_multiversion':sum(r['pendientes_multiversion']>0 for r in grows),'carreras_con_pendiente':len({r['carrera_umas'] for r in grows if r['pendientes']>0})}
compact=collections.defaultdict(list)
for r in pr:compact[(r['carrera_umas'],r['sede_observada'],r['jornada_observada'],r['plan'])].append(r)
out['v17']['combinaciones_sin_periodo']=[dict(zip(['carrera_umas','sede_observada','jornada_sies_observada','plan'],k))|{'observaciones':len(rs),'pendientes':sum(r['estado_destino']=='E_PENDIENTE' for r in rs),'pendientes_multiversion':sum(r['estado_destino']=='E_PENDIENTE' and r['codigo_origen_T1'].rsplit('V',1)[0] in mf for r in rs)} for k,rs in sorted(compact.items())]
out['v17']['resumen_combinaciones_sin_periodo']={'definicion':'carrera UMAS+sede observada+jornada SIES observada+plan','total':len(compact),'con_pendientes':sum(r['pendientes']>0 for r in out['v17']['combinaciones_sin_periodo']),'con_pendientes_multiversion':sum(r['pendientes_multiversion']>0 for r in out['v17']['combinaciones_sin_periodo'])}
bc=collections.defaultdict(collections.Counter)
for r in grows:
 for key in ['observaciones','documentales','internos','pendientes','pendientes_multiversion']:bc[r['carrera_umas']][key]+=r[key]
out['v17']['por_carrera']=[{'carrera_umas':k,**dict(v)} for k,v in sorted(bc.items())]
out['v17']['pendientes_por_motivo']=dict(collections.Counter(r['tipo_pendiente'] or r['relacion_codigo'] for r in po))
out['v17']['limites']=['Hojas30–51 preservan cifras históricas; no equivalen al estado actual v7.','Codigo T1 conocido no acredita automáticamente el código del contexto destino.','Sin contexto no equivale a pendiente de código ni a deserción.','V17 preserva los denominadores 558/1150/1471 de T1; tasa T3-2026 utiliza1467 según regla heredada.']
out['v17']['historico_63']={'filas':len([r for r in w['39_Dimensiones_Contraste'].iter_rows(min_row=5,values_only=True) if r and r[0]]),'alcance':'Inventario original carrera UMAS+sede+jornada; cifras V6 preservadas como historia, no cierres actuales.'}
(Path(__file__).resolve().parent/'insumos/capas.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
print(json.dumps({'v17':{k:v for k,v in out['v17'].items() if k not in ['planes_con_pendientes','foco_multiversion','combinaciones_contextuales','combinaciones_sin_periodo','por_carrera']},'c2':out['c2'],'salida':'/tmp/auditoria_diccionario_20261025_capas.json'},ensure_ascii=False,indent=2))
