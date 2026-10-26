from pathlib import Path
import json,openpyxl,collections,hashlib
P=Path(__file__).resolve().parent
pre=(P/'reconstruir_pasos.py').read_text().split('ct=collections.Counter();')[0]
exec(compile(pre,'preparar_controles_solo_memoria','exec'))
P=Path(__file__).resolve().parent
meta=json.loads((P/'RESPALDOS_XLSX_INSPECCION.json').read_text());sp=next(x for x in meta if Path(x['ruta']).name=='2 y 3er Intake.xlsx')
w=openpyxl.load_workbook(sp['ruta'],read_only=True,data_only=True);it=w['Detalle1'].iter_rows(values_only=True)
for nr,row in enumerate(it,1):
 h=[txt(x)for x in row]
 if 'RUT'in h and 'ANOINGRESO'in h:break
idx={n:i for i,n in enumerate(h)if n};found=set();origins=collections.Counter()
for row in it:
 k=key(row[idx['RUT']])
 if k in persons:
  found.add(k);origins[(txt(row[idx['ANOINGRESO']]),txt(row[idx['PERIODOINGRESO']]))]+=1
corr={k for k in persons if stages['Final a carga'][k]['ARREGLO']=='CORRECCIÓN'}
assert len(corr)==30 and corr==found
r={'control_30_correccion':{'personas':30,'coinciden_exactamente_con_Detalle1':True,'ano_periodo_Detalle1':[{'ano':a,'periodo':p,'filas':n}for(a,p),n in origins.items()]},'workbooks_inspeccionados':len(meta),'workbooks_con_errores_lectura':sum('error'in x for x in meta),'con_query_connections_vba':[{'archivo':x['ruta'],'objetos':[n for n in x.get('objetos_codigo',[])if any(v in n.lower() for v in ['querytable','connections','customxml','vbaproject'])]}for x in meta if any(any(v in n.lower()for v in ['querytable','connections','customxml','vbaproject'])for n in x.get('objetos_codigo',[]))]}
(P/'CONTROLES_AGREGADOS.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
# Keep row references as aggregate spans, and drop free notes; no individual extracts are delivered.
f=P/'CRUCE_RESPALDOS_AGREGADO.json';data=json.loads(f.read_text())
for x in data:
 rr=x.pop('filas_objetivo_por_periodo',{})
 x['rango_abarcador_por_periodo']={k:{'fila_minima':min(v),'fila_maxima':max(v),'numero_filas':len(v)}for k,v in rr.items() if v}
 for z in x['distribucion']:
  z['campos']={k:v for k,v in z['campos'].items()if k in ['ANOINGRESO','PERIODOINGRESO','ANIO_ING_ACT','SEM_ING_ACT','ANIO_ING_ORI','SEM_ING_ORI','FOR_ING_ACT','NIVEL2','NIVEL_2']}
f.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(r,ensure_ascii=False))
wb.close();w.close()
