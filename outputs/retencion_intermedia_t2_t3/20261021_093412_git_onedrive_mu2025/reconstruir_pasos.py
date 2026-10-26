from pathlib import Path
import json,openpyxl,collections,hashlib
P=Path(__file__).resolve().parent
pre=Path('/Users/alexi/Documents/GitHub/avance_curricular/outputs/retencion_intermedia_t2_t3/20261021_092604_codcli_mu2025/auditar_codcli.py').read_text().split('trace=[]')[0]
exec(compile(pre,'seleccion83_solo_memoria','exec'));P=Path(__file__).resolve().parent
persons={k:{'term':term,'ss':ss,'dest':dest} for term,k,ss,dest in targets}
spec=next(s for s in json.loads((P/'RESPALDOS_XLSX_INSPECCION.json').read_text()) if Path(s['ruta']).name=='IPSS_Procesamiento.xlsx')
wb=openpyxl.load_workbook(spec['ruta'],read_only=True,data_only=True)
stages={}
for name in ['Carga_Completa','Carga_Completa (2)','Carga_Completa (3)','Final a carga']:
 it=wb[name].iter_rows(values_only=True)
 for no,row in enumerate(it,1):
  h=[txt(x)for x in row]
  if 'N_DOC'in h and 'ANIO_ING_ORI'in h:break
 idx={n:i for i,n in enumerate(h) if n};stage=collections.defaultdict(list)
 for row in it:
  k=key(row[idx['N_DOC']],row[idx['DV']])
  if k not in persons:continue
  if txt(row[idx['COD_CAR']])not in {txt(r['COD_CAR'])for r in persons[k]['dest']}:continue
  stage[k].append({n:txt(row[idx[n]])for n in ['ANIO_ING_ACT','SEM_ING_ACT','ANIO_ING_ORI','SEM_ING_ORI','NIVEL','ARREGLO','FOR_ING_ACT']if n in idx})
 assert len(stage)==83 and all(len(v)==1 for v in stage.values())
 stages[name]={k:v[0]for k,v in stage.items()}
ct=collections.Counter();source30=collections.Counter()
for k,p in persons.items():
 origcli={txt(r['CODCLI'])for r in p['ss']};src_car={txt(r['CODCARPR'])for r in p['ss']}
 new=[r for r in ui[k] if txt(r['CODCARPR'])in src_car and txt(r['ANOINGRESO'])=='2025' and txt(r['CODCLI'])not in origcli]
 before=stages['Carga_Completa (2)'][k];after=stages['Carga_Completa (3)'][k];final=stages['Final a carga'][k]
 tup=(p['term'],final['ARREGLO']or'SIN MARCA',before['ANIO_ING_ACT'],before['ANIO_ING_ORI'],after['ANIO_ING_ACT'],after['ANIO_ING_ORI'],before.get('NIVEL'),after.get('NIVEL'),bool(new))
 ct[tup]+=1
rows=[{'periodo_ingreso2024':t,'marca_ARREGLO':m,'ANIO_ING_ACT_hoja2':act0,'ANIO_ING_ORI_hoja2':ori0,'ANIO_ING_ACT_hoja3':act1,'ANIO_ING_ORI_hoja3':ori1,'NIVEL_hoja2':niv0,'NIVEL_hoja3':niv1,'otro_CODCLI_ingreso2025_misma_carrera':new,'personas':n}for(t,m,act0,ori0,act1,ori1,niv0,niv1,new),n in sorted(ct.items())]
assert sum(r['personas']for r in rows)==83
assert sum(r['personas']for r in rows if r['marca_ARREGLO']=='2+3 INGRESO')==50
assert sum(r['personas']for r in rows if r['marca_ARREGLO']=='CORRECCIÓN')==30
assert sum(r['personas']for r in rows if r['otro_CODCLI_ingreso2025_misma_carrera'])==3
assert all(not r['otro_CODCLI_ingreso2025_misma_carrera']for r in rows if r['marca_ARREGLO']!='SIN MARCA')
result={'archivo':spec['ruta'],'sha256':spec['sha256'],'hojas_comparadas':['Carga_Completa (2)','Carga_Completa (3)','Final a carga'],'llave_control':'N_DOC+DV+COD_CAR, relación única validada para estas 83 personas; CODCLI fuente UMAS mantenido en memoria','resultados':rows,'control':{'personas':83,'registros_unicos_por_persona_y_hoja':True,'con_cambio_origen_2024_a_2025_entre_hojas':50,'ya_origen2025_marca_correccion':30,'sin_marca_con_otro_CODCLI_ingreso2025':3},'clasificacion':'B/C; motivo y autorización no acreditados E'}
(P/'PASOS_RECONSTRUIDOS_AGREGADOS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False,indent=2))
wb.close()
