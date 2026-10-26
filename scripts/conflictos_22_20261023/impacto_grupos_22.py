"""Auditoría de solo lectura del impacto de los grupos K2 en el Excel V12."""
from pathlib import Path
import sys,json,collections,hashlib,re,unicodedata,openpyxl
R=Path('/Users/alexi/Documents/GitHub/avance_curricular');sys.path.insert(0,str(R))
from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento,rut_normalizado,sha256
O=Path('/tmp/impacto_grupos_22');O.mkdir(exist_ok=True)
M=json.loads((R/'outputs/aplicacion_diccionario_intertrimestral_20261023_125556/MANIFEST_APLICACION.json').read_text());src=Path('/Users/alexi/Downloads/RETENCION_IPSS_FINAL_con_Foto_Intertrimestral_20261022_AUDITADO_ENTREGA.xlsx');v12=Path(M['salida']);assert sha256(v12)==M['salida_sha256'];assert sha256(src)==M['fuentes'][str(src)]
P=Path(M['privado']);originpath=P/'ORIGENES_T1.json';followpath=P/'CONSULTAS_EXACTAS.json'
for p in (originpath,followpath):assert sha256(p)==M['auditoria_privada_hashes'][p.name]
origins=json.loads(originpath.read_text());oldfollow=json.loads(followpath.read_text());originindex={(x['persona'],str(x['anio'])):x for x in origins};assert len(originindex)==3179
s=DiccionarioSiesSeguimiento();rs=[json.loads(x[0]) for x in s.db.execute('select payload from observaciones')];assert s.edicion=='v7_20261023_inf35_03_t3'
assert sha256(s.descriptor['base_privada']['ruta'])==s.descriptor['base_privada']['sha256']
GG=[g for g in json.loads((R/'outputs/auditoria_metodos_puente_20261023_155309/GRUPOS_MULTICODIGO.json').read_text()) if g['llave']=='K2_mas_plan'];assert len(GG)==22
k=lambda r:tuple(str(r.get(c,'')) for c in ['carrera','sede_dimension','jornada_sies','ano','plan'])
gk=lambda v:tuple(str(v[c]) for c in ['carrera','sede','jornada','ano','plan'])
groups={gk(g['variables']):('G%02d'%(i+1),g) for i,g in enumerate(GG)}
w=openpyxl.load_workbook(src,read_only=True,data_only=True);x20=[(i,r) for i,r in enumerate(w['20_Foto_BBDD'].iter_rows(min_row=6,values_only=True),6) if r[1]]
# Valida el agregado idéntico de la población mediante los cinco campos de linaje.
v=openpyxl.load_workbook(v12,read_only=True,data_only=True)
a=collections.Counter(tuple(r[j] for j in [1,2,9,10,11]) for i,r in x20);b={tuple(r[:5]):r[5] for r in v['20_Foto_BBDD'].iter_rows(min_row=5,values_only=True) if r[0]};assert a==b
# Fuentes de los grupos de ingreso T2/T3: usa fila literal de la fuente, no nombre como llave.
paths={unicodedata.normalize('NFC',p.name):p for p in Path('/Users/alexi/Downloads').glob('*.xlsx')};loaded={};source_meta={}
for name,tab in [('Matrícula T2_2025 2.xlsx','Hoja1'),('Matrícula T_2_13_07_2026.xlsx','Hoja1'),('Matrícula_T3_02_10_2026.xlsx','Base')]:
 p=paths[name];sw=openpyxl.load_workbook(p,read_only=True,data_only=True);allrows=list(sw[tab].iter_rows(values_only=True));heads=allrows[0];loaded[name]={j+1:dict(zip(heads,r)) for j,r in enumerate(allrows)};source_meta[name]={'ruta':str(p),'hoja':tab,'sha256':sha256(p)};sw.close()
newmembership=collections.defaultdict(list);checks=collections.Counter();unresolved=[]
for i,r in x20:
 if r[2] not in (2,3):continue
 name='Matrícula T2_2025 2.xlsx' if r[1]==2025 else 'Matrícula T_2_13_07_2026.xlsx' if r[2]==2 else 'Matrícula_T3_02_10_2026.xlsx';sr=int(re.search(r'fila (\d+)',r[3]).group(1));z=loaded[name][sr]
 try:person=rut_normalizado(r[4]);rawperson=rut_normalizado(z['RUT'])
 except ValueError:checks['sin_llave_rut']+=1;unresolved.append((i,name));continue
 assert person==rawperson
 checks['ingreso_literal_coincide_grupo' if str(z['ANOINGRESO'])==str(r[1]) and str(z['PERIODOINGRESO'])==str(r[2]) else 'ingreso_literal_distinto_grupo']+=1
 key=(person,str(z['CODCLI']),str(z['CODCARPR']),str(r[1]))
 newmembership[key].append({'fila_20':i,'grupo':r[2],'anio':r[1]});checks['filas_fuente_coinciden']+=1
annual9=collections.defaultdict(list)
for rr in w['9_Base_Analitica_Detalle'].iter_rows(min_row=6,values_only=True):
 if str(rr[1]) not in ['2022','2023','2024','2025']:continue
 try:rp=rut_normalizado(str(rr[7])+'-'+str(rr[8]))
 except ValueError:continue
 annual9[(rp,str(rr[1]))].append(str(rr[23]))
for ori in origins:
 if int(ori['anio']) in (2024,2025) and ori['persona']:annual9[(ori['persona'],str(ori['anio']))].append(ori['codigo_origen'])
# Grupo exacto: no confunde misma persona en otra carrera/familia.
def matching(r):
 ori=originindex.get((r['persona'],str(r['ano'])));relation='sin_origen_T1'
 if ori:
  cand=set(r['codigos_anuales_documentados'])|set(r['candidatos_calculados']);cand|={str(r.get(c) or '') for c in ['codigo_documental_atribuible','codigo_interno_adoptado','codigo_propuesto','codigo_propuesto_inicial']}
  fam={c.rsplit('V',1)[0] for c in cand if re.fullmatch(r'I162S\d+C\d+J\d+V\d+',c)}
  relation='misma_familia' if ori['familia'] in fam else 'otra_familia' if fam else 'sin_familia'
  chosen=r['codigo_interno_adoptado']
  if chosen and chosen.rsplit('V',1)[0]!=ori['familia']:relation='otra_familia'
 nw=newmembership.get((r['persona'],str(r['CODCLI']),r['carrera'],str(r['ano'])),[])
 return ori,relation,nw
def amatch(r):
 codes=annual9.get((r['persona'],str(r['ano'])),[]); fams={c.rsplit('V',1)[0] for c in codes};sel=r['codigo_interno_adoptado']
 if sel:return sel.rsplit('V',1)[0] in fams
 cand=set(r['codigos_anuales_documentados'])|set(r['candidatos_calculados']);cand|={str(r.get(c) or '') for c in ['codigo_propuesto','codigo_propuesto_inicial']}
 return bool(fams & {c.rsplit('V',1)[0] for c in cand if re.fullmatch(r'I162S\d+C\d+J\d+V\d+',c)})
out=[];focus_by_gid={};hit_observation_ids=set();hit_people=set()
for key,(gid,g) in groups.items():
 gr=[r for r in rs if k(r)==key];focus_by_gid[gid]=gr
 ann={tuple(str(r[c]) for c in ['persona','CODCLI','plan','carrera','sede_dimension','jornada_sies','ano']) for r in gr if r['codigo_documental_atribuible']}
 matched=[];new=[];pres_person=set();t1origin=set();t1exact=set();status=collections.Counter();per=collections.Counter()
 for r in gr:
  ori,relation,nw=matching(r)
  if ori:
   pres_person.add(r['persona']);status[relation]+=1
   if relation=='misma_familia':
    matched.append(r);t1origin.add((r['persona'],str(r['ano'])));t1exact.add((r['persona'],r['CODCLI'],str(r['ano'])));per[str(r['periodo'])]+=1;hit_observation_ids.add(r['observacion_id']);hit_people.add(r['persona'])
  if nw:new.append((r,nw))
 out.append({'grupo':gid,'variables':g['variables'],'codigos_documentados':g['codigos_y_personas'],'contextos_anuales_documentados':len(ann),'observaciones_todos_estados_grupo':len(gr),'personas_todos_estados_grupo':len({r['persona'] for r in gr}),'pendientes_actuales_grupo':sum(not r['codigo_interno_adoptado'] for r in gr),'T1_personas_mismo_anio_cualquier_familia':len(pres_person),'T1_origenes_misma_familia':len(t1origin),'T1_expedientes_misma_familia':len(t1exact),'T1_observaciones_misma_familia':len(matched),'T1_observaciones_pendientes_misma_familia':sum(not r['codigo_interno_adoptado'] for r in matched),'T1_relacion_familia':dict(status),'T1_periodos_nativos':dict(per),'ingresos_T2_T3_exactos_por_grupo':{str(group):{'personas':len({r['persona'] for r,nw in new if any(z['grupo']==group for z in nw)}),'expedientes':len({(r['persona'],r['CODCLI']) for r,nw in new if any(z['grupo']==group for z in nw)}),'observaciones':len({r['observacion_id'] for r,nw in new if any(z['grupo']==group for z in nw)})} for group in (2,3)},'hoja9_cohorte_anual_todos_estados':{'personas':len({r['persona'] for r in gr if amatch(r)}),'observaciones':sum(amatch(r) for r in gr),'pendientes':sum(amatch(r) and not r['codigo_interno_adoptado'] for r in gr)},'hoja9_cohorte_anual_misma_familia_personas':len({r['persona'] for r in gr if any(c.rsplit('V',1)[0]==r['codigo_documental_atribuible'].rsplit('V',1)[0] for c in annual9.get((r['persona'],str(r['ano'])),[])) and r['codigo_documental_atribuible']}),'clasificacion':'B/C observado, no modifica datos o tasas'})
# Reproduce los seis errores K3 y determina si la persona/contexto entra al año del libro.
ag=collections.defaultdict(list)
for r in rs:
 if r['codigo_documental_atribuible']:ag[tuple(str(r[c]) for c in ['persona','CODCLI','plan','carrera','sede_dimension','jornada_sies','ano'])].append(r)
annual=[]
for key,gr in ag.items():
 codes={r['codigo_documental_atribuible'] for r in gr};assert len(codes)==1;r=gr[0];incomes={str(x['fechas_declaradas'].get('DA_ANOINGRESO') or '') for x in gr};assert len(incomes)==1
 annual.append(dict(r,ingreso=next(iter(incomes)),code=next(iter(codes)),fold=int(hashlib.sha256(r['persona'].encode()).hexdigest()[:16],16)%5))
fs=['carrera','sede_dimension','jornada_sies','ano','plan','ingreso'];ck=lambda r:tuple(str(r.get(f) or '') for f in fs);errors=[]
for fold in range(5):
 model=collections.defaultdict(lambda:collections.defaultdict(set))
 for r in annual:
  if r['fold']!=fold and '' not in ck(r):model[ck(r)][r['code']].add(r['persona'])
 for r in annual:
  if r['fold']!=fold:continue
  z=model.get(ck(r),{});pred=next(iter(z)) if len(z)==1 and len(next(iter(z.values())))>=3 else None
  if pred and pred!=r['code']:errors.append(r|{'pred':pred})
assert len(errors)==6
errs=[]
for i,r in enumerate(errors,1):
 ori,relation,nw=matching(r);gid=groups.get(k(r),('',{}))[0]
 errs.append({'error':i,'grupo':gid,'variables':{c:str(r[c]) for c in ['carrera','sede_dimension','jornada_sies','ano','plan','ingreso']},'documentado':r['code'],'predicho_no_aplicado':r['pred'],'T1_mismo_anio_persona':bool(ori),'T1_relacion':relation,'T1_codigo_origen':ori['codigo_origen'] if ori else None,'cohorte_anual_hoja9_codigos':sorted(set(annual9.get((r['persona'],str(r['ano'])),[]))),'hoja9_todas_cohortes_persona':[{'cohorte':y,'codigos_origen':sorted(set(cs)),'rol_anio_error':'origen' if y==str(r['ano']) else 'seguimiento_anual_siguiente' if int(y)+1==int(r['ano']) else 'otro_anio'} for (p,y),cs in annual9.items() if p==r['persona']],'hoja20_T1_todos_anios_persona':[{'anio':ori2['anio'],'codigo_origen':ori2['codigo_origen'],'rol_anio_error':'origen' if str(ori2['anio'])==str(r['ano']) else 'seguimiento_anual_siguiente' if int(ori2['anio'])+1==int(r['ano']) else 'otro_anio'} for ori2 in origins if ori2['persona']==r['persona']],'ingresos_T2_T3':sorted({z['grupo'] for z in nw}),'clasificacion':'B/C error experimental no aplicado'})
# Verifica fórmula/valor en libro y fuente; solo reporte de estructura y referencias.
formula={}
for p,label in [(v12,'V12'),(src,'original')]:
 fw=openpyxl.load_workbook(p,read_only=True,data_only=False);tabs={}
 for tab in ['18_Foto_Intertrimestral','19_Foto_Carrera','20_Foto_BBDD','26_Avance_Curricular_Resumen']:
  cells=[(c.coordinate,c.value) for row in fw[tab].iter_rows() for c in row if c.data_type=='f'];tabs[tab]={'formulas':len(cells),'referencias_a_diccionario_52_54':sum(any(x in f for x in ['52_','53_','54_']) for cell,f in cells),'referencias_VERSION_o_CODIGO_SIES':sum(any(x in f.upper() for x in ['VERSION','CODIGO_SIES']) for cell,f in cells)}
 formula[label]=tabs;fw.close()
res={'excel':{'ruta':str(v12),'sha256':sha256(v12),'hojas':len(v.sheetnames),'diccionario_integrado_en_version_excel':M['diccionario'],'diccionario_consultado_hoy':s.edicion},'linaje_original':{'ruta':str(src),'sha256':sha256(src),'hoja':'20_Foto_BBDD','filas':len(x20),'agrupacion_reproducida':len(a),'grupos_denominadores':{str(k):n for k,n in collections.Counter((r[1],r[2]) for _,r in x20).items()}},'fuentes_nuevos_ingresos':source_meta,'QA_fuentes_nuevos_ingresos':dict(checks),'grupos':out,'errores':errs,'estructura_formulas':formula,'resumen':{'grupos_revisados':22,'grupos_con_T1_misma_familia':sum(x['T1_origenes_misma_familia']>0 for x in out),'personas_T1_misma_familia_sin_duplicar_entre_grupos':len(hit_people),'observaciones_T1_misma_familia_sin_duplicar':len(hit_observation_ids),'errores_con_T1_misma_familia':sum(x['T1_relacion']=='misma_familia' for x in errs),'errores_con_ingreso_T2_T3_exacto':sum(bool(x['ingresos_T2_T3']) for x in errs)},'limites':['Períodos PROMEDIOS nativos no se igualan a cierre T2/T3.','Presencia de persona en otra familia no atribuye su contexto al origen T1.','Códigos documentados anuales no son hechos trimestrales independientes.','V12 18/19 son valores agregados; asignaciones del diccionario no actualizan esas tasas.','No se cambiaron bases, denominadores, Excel o diccionario.']}
# Privacidad: no emite llaves individuales, ni hash personal.
t=json.dumps(res,ensure_ascii=False,indent=2);assert not any(r['CODCLI'] in t or r['persona'] in t for r in rs)
(O/'IMPACTO_EXCEL_22.json').write_text(t+'\n');print(json.dumps({'ruta':str(O/'IMPACTO_EXCEL_22.json'),'resumen':res['resumen'],'grupos_afectan':[{k:v for k,v in x.items() if k in ('grupo','variables','T1_origenes_misma_familia','T1_observaciones_misma_familia','T1_observaciones_pendientes_misma_familia','ingresos_T2_T3_exactos_por_grupo')} for x in out if x['T1_origenes_misma_familia'] or any(z['personas'] for z in x['ingresos_T2_T3_exactos_por_grupo'].values())],'errores':errs,'formulas':formula},ensure_ascii=False,indent=2));s.close();w.close();v.close()
