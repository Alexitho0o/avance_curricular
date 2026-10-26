from pathlib import Path
from collections import Counter,defaultdict
import json,contextlib,io,re,openpyxl,hashlib
P=Path(__file__).resolve().parent
# Reuse the exact, already audited population selection; no prior output is rewritten.
pre=Path('/Users/alexi/Documents/GitHub/avance_curricular/outputs/retencion_intermedia_t2_t3/20261021_092604_codcli_mu2025/auditar_codcli.py').read_text().split('trace=[]')[0]
exec(compile(pre,'seleccion83_solo_memoria','exec'))
P=Path(__file__).resolve().parent
targets83={k:{'periodo':term,'codcarpr':{txt(r['CODCARPR']) for r in ss},'codigos':{txt(r['COD_CAR']) for r in dest}} for term,k,ss,dest in targets}
inv=json.loads((P/'RESPALDOS_XLSX_INSPECCION.json').read_text())
names=['2 y 3er Intake.xlsx','IPSS_Procesamiento.xlsx','DATOSDEALUMNOS_1758_CRUDO_10_04_2025_FINAL_SIES.xlsx','Descarga de lo cargado_08-05-2025_22-26-22_Matrícula_Pregrado_2025.xlsx','Formati_SIES_2025.xlsx','Matricula 2 y 3er 2024.xlsx']
results=[]
for spec in inv:
 if Path(spec['ruta']).name not in names or 'error' in spec:continue
 p=Path(spec['ruta']);assert hashlib.sha256(p.read_bytes()).hexdigest()==spec['sha256']
 wb=openpyxl.load_workbook(p,read_only=True,data_only=True);wf=openpyxl.load_workbook(p,read_only=True,data_only=False)
 for sheet in wb:
  # Only grain-bearing sheets, no pivot summaries.
  h=None;hrow=None;it=sheet.iter_rows(values_only=True)
  for nr,row in enumerate(it,1):
   vals=[txt(x) for x in row]
   if ('RUT'in vals and ('ANOINGRESO'in vals or 'CODCARPR'in vals)) or ('N_DOC'in vals and 'ANIO_ING_ORI'in vals):h=vals;hrow=nr;break
   if nr>=8:break
  if not h:continue
  idx={n:i for i,n in enumerate(h) if n};cts=Counter();counts=Counter();seen=set();seen_same=set();formula_counts=Counter();formulas=[];rowranges=defaultdict(list)
  for nr,row in enumerate(it,hrow+1):
   def val(n):return row[idx[n]] if n in idx and idx[n]<len(row) else None
   if 'N_DOC'in idx:k=key(val('N_DOC'),val('DV'))
   else:k=key(val('RUT'))
   if k not in targets83:continue
   seen.add(k)
   candidate=targets83[k]
   if 'CODCARPR'in idx:same=txt(val('CODCARPR')) in candidate['codcarpr']
   elif 'COD_CAR'in idx:same=txt(val('COD_CAR')) in candidate['codigos']
   else:same=None
   if same:seen_same.add(k)
   counts['misma_carrera' if same else 'otra_carrera_o_sin_codigo']+=1
   fields={n:txt(val(n)) for n in ['ANOINGRESO','PERIODOINGRESO','ANIO_ING_ACT','SEM_ING_ACT','ANIO_ING_ORI','SEM_ING_ORI','FOR_ING_ACT','NIVEL2','NIVEL_2','Primer año','CARGA','OBS','OBSERVACION','OBSERVACIONES','Arreglo'] if n in idx}
   cts[(candidate['periodo'],'misma'if same else'otra',tuple(fields.items()))]+=1
   rowranges[candidate['periodo']].append(nr)
  # Aggregate formulas only from origin/ingress columns, never identity values.
  ingress=[n for n in ['ANOINGRESO','PERIODOINGRESO','ANIO_ING_ACT','SEM_ING_ACT','ANIO_ING_ORI','SEM_ING_ORI'] if n in idx]
  for row in wf[sheet.title].iter_rows(min_row=hrow+1):
   for n in ingress:
    cell=row[idx[n]]
    if cell.data_type=='f':
     formula_counts[n]+=1
     if len(formulas)<6 and not re.search(r'\b\d{7,9}\b',str(cell.value)):formulas.append({'campo':n,'celda':cell.coordinate,'formula':cell.value})
  result={'ruta':str(p),'sha256':spec['sha256'],'hoja':sheet.title,'fila_encabezado':hrow,'contiene_CODCLI':'CODCLI'in idx,'personas_objetivo_encontradas':len(seen),'personas_objetivo_misma_carrera':len(seen_same),'filas_clasificacion':dict(counts),'campos_ingreso_formulas':dict(formula_counts),'formulas_ingreso_muestra':formulas,'distribucion':[{'periodo_origen2024':t,'comparacion_carrera':z,'campos':dict(f),'filas':n} for(t,z,f),n in cts.items()],'filas_objetivo_por_periodo':{str(k):v for k,v in rowranges.items()}}
  results.append(result);(P/'CRUCE_RESPALDOS_AGREGADO.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
  print(p.name,sheet.title,'personas',len(seen),'misma_carrera',len(seen_same),'formulas_ingreso',dict(formula_counts),flush=True)
 wb.close();wf.close()
