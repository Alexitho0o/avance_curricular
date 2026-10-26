"""Cobertura del libro V12 y consulta v7; lectura, sin modificar artefactos."""
from pathlib import Path
import json,sys,collections,openpyxl
R=Path('/Users/alexi/Documents/GitHub/avance_curricular');sys.path.insert(0,str(R))
from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento,sha256
MP=R/'outputs/aplicacion_diccionario_intertrimestral_20261023_125556/MANIFEST_APLICACION.json';M=json.loads(MP.read_text());P=Path(M['privado']);V=Path(M['salida']);assert sha256(V)==M['salida_sha256']
for name in ['ORIGENES_T1.json','CONSULTAS_EXACTAS.json','SIN_CONTEXTO.json']:assert sha256(P/name)==M['auditoria_privada_hashes'][name]
origins=json.loads((P/'ORIGENES_T1.json').read_text());follow=json.loads((P/'CONSULTAS_EXACTAS.json').read_text());missing=json.loads((P/'SIN_CONTEXTO.json').read_text());s=DiccionarioSiesSeguimiento();rs={r['observacion_id']:r for x in s.db.execute('select payload from observaciones') for r in [json.loads(x[0])]}
assert s.edicion=='v7_20261023_inf35_03_t3';assert len({x['observacion_id'] for x in follow})==len(follow)==5320;assert len({(x['persona'],x['anio']) for x in origins})==len(origins)==3179
current=[]
for f in follow:
 r=rs[f['observacion_id']];q=s.consultar(persona=r['persona'],codcli=r['CODCLI'],plan=r['plan'],anio=r['ano'],periodo=r['periodo'],carrera=r['carrera'],sede=r['sede_dimension'],jornada=r['jornada_sies'])
 status='B/C Documental' if q['nivel_respaldo'].startswith('B/C') else 'D Interno aprobado' if q['nivel_respaldo'].startswith('D_') else 'E Pendiente'
 relation=f['relacion_familia']
 if q['codigo_sies'] and q['codigo_sies'].rsplit('V',1)[0]!=f['familia']:relation='Otra familia'
 current.append(dict(f,estado=status,relacion_familia=relation,codigo_contexto=q['codigo_sies']))
statuses=['B/C Documental','D Interno aprobado','E Pendiente']
def stat(fs):
 c=collections.Counter(f['estado'] for f in fs);out={'observaciones':len(fs),'personas_sin_duplicar':len({f['persona'] for f in fs}),'persona_anio':len({(f['persona'],f['anio']) for f in fs}),'expedientes_persona_CODCLI':len({(f['persona'],f['codcli']) for f in fs}),**{k:c[k] for k in statuses}};out['con_codigo_pct']=100*(c[statuses[0]]+c[statuses[1]])/len(fs) if fs else None;return out
def yearper(fs):
 return [{'anio':y,'periodo_nativo':p,**stat([f for f in fs if int(f['anio'])==y and int(f['periodo_nativo'])==p])} for y,p in sorted({(int(f['anio']),int(f['periodo_nativo'])) for f in fs})]
def origins_summary(fs):
 idx=collections.defaultdict(list)
 for f in fs:idx[f['persona'],f['anio']].append(f)
 out=[]
 for y in sorted({x['anio'] for x in origins}):
  os=[x for x in origins if x['anio']==y];c=collections.Counter()
  for o in os:
   ff=idx[o['persona'],y];npend=sum(f['estado']=='E Pendiente' for f in ff);ndoc=sum(f['estado']=='B/C Documental' for f in ff)
   if not ff:c['sin_contexto_localizado']+=1
   elif npend==0:c['todos_contextos_con_codigo']+=1
   elif npend==len(ff):c['todos_contextos_pendientes']+=1
   else:c['contextos_parcialmente_resueltos']+=1
  assert sum(c.values())==len(os)
  out.append({'anio':y,'origenes_T1':len(os),'codigo_origen_documentado':len(os),**dict(c),'personas_con_algun_contexto':sum(bool(idx[o['persona'],y]) for o in os),'cobertura_contexto_pct':100*sum(bool(idx[o['persona'],y]) for o in os)/len(os)})
 return out
w=openpyxl.load_workbook(V,read_only=True,data_only=True)
photo20=list(w['20_Foto_BBDD'].iter_rows(min_row=5,values_only=True));groups=collections.Counter()
for r in photo20:
 if r[0]:groups[(int(r[0]),int(r[1]))]+=int(r[5])
# Only aggregate sheets are printed; no identifiers.
cellrefs={}
for tab in ['18_Foto_Intertrimestral','52_Codigos_SIES_Revision','53_Codigos_T1_Confirmados','54_Contextos_y_Pendientes']:
 ws=w[tab];sample=[]
 if tab in ['18_Foto_Intertrimestral','52_Codigos_SIES_Revision']:
  for row in ws.iter_rows():
   nonempty=[{'celda':c.coordinate,'valor':c.value} for c in row if c.value is not None]
   if nonempty:sample.append(nonempty)
 else:sample=[{'fila':i,'valores':list(r)} for i,r in enumerate(ws.iter_rows(min_row=1,max_row=5,values_only=True),1)]
 cellrefs[tab]={'dimensiones':[ws.max_row,ws.max_column],'muestra_agregada':sample}
res={'clasificacion':'B observado/C recuento; D cierres internos ya autorizados; E pendientes','excel':{'ruta':str(V),'sha256':sha256(V),'edicion_diccionario_incorporada':M['diccionario']},'diccionario_consultado_actual':{'edicion':s.edicion,'ruta':s.descriptor['base_privada']['ruta'],'sha256':s.descriptor['base_privada']['sha256']},'origenes_T1':{'total':3179,'todos_codigo_origen_documentado':3179,'por_anio_v1':origins_summary(follow),'por_anio_v7':origins_summary(current)},'cobertura_v1_en_excel':{'total':stat(follow),'por_anio_periodo':yearper(follow),'varias_versiones':stat([f for f in follow if f['multiple']])},'cobertura_consulta_actual_v7':{'total':stat(current),'por_anio_periodo':yearper(current),'varias_versiones':stat([f for f in current if f['multiple']]),'varias_versiones_por_anio_periodo':yearper([f for f in current if f['multiple']]),'relaciones':{k:stat([f for f in current if f['relacion_familia']==k]) for k in sorted({f['relacion_familia'] for f in current})}},'universo_completo_foto_hoja20':[{'anio':k[0],'grupo_ingreso':k[1],'filas_persona':n,'aplicado_diccionario':k[1]==1} for k,n in sorted(groups.items())],'nuevos_grupos_T2_T3_preservados_no_reclasificados':sum(n for k,n in groups.items() if k[1]!=1),'no_incluye_2027':not any(k[0]==2027 for k in groups),'celdas':cellrefs,'fuentes':{'manifest':{'ruta':str(MP),'sha256':sha256(MP)},'privados_hashes':M['auditoria_privada_hashes'],'script_aplicacion':{'ruta':str(R/'scripts/aplicar_diccionario_excel_intertrimestral_20261023.py'),'sha256':sha256(R/'scripts/aplicar_diccionario_excel_intertrimestral_20261023.py')}},'limites':['La asignación documental es anual y no prueba aceptación SIES ni fecha exacta de cambio.','Los períodos reportados son nativos de PROMEDIOS, no se declaran trimestres equivalentes.','El código de origen sigue respaldado para personas sin contexto localizado.','Los grupos de ingreso2/3 no fueron reclasificados en V12; no se les asigna el porcentaje de cobertura de T1.','No se alteraron bases, denominadores, Excel ni diccionario.','La consulta v7 no actualiza las hojas52-54 del Excel V12, que contienen v1.']}
p=Path('/tmp/cobertura_excel_alcance_20261023.json');t=json.dumps(res,ensure_ascii=False,indent=2,default=str);assert not any(str(r['CODCLI']) in t or str(r['persona']) in t for r in rs.values());p.write_text(t+'\n');w.close();s.close();print(json.dumps({k:v for k,v in res.items() if k not in ('celdas','fuentes')},ensure_ascii=False,indent=2))
