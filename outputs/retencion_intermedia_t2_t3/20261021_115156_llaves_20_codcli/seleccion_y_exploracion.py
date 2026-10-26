from pathlib import Path
from collections import Counter,defaultdict
import json,hashlib,re,openpyxl
R=Path('/Users/alexi/Documents/GitHub/avance_curricular')
pre=(R/'outputs/retencion_intermedia_t2_t3/20261020_215248/profile.py').read_text().split('specs=')[0]
exec(compile(pre,'seleccion_original_solo_lectura','exec'))
assert digest(rawpath)=='19cf33ae4925a7c13ec4745394141a297f4f64be4052a240cb0d2c42ffeb53bd'
assert digest(engpath)=='5f0f7c7f0f238556de374d287bf2931ccc8a93a5489f4c2f2b543befd38c77b3'
targets=[b for b in base if b['engine']['ANIO_INFORMADO']==2025 and b['engine']['ESTADO_FINAL']=='INCLUIDO' and not b['key']]
assert len(targets)==20,len(targets)
assert sum(b['engine']['ANIO_INFORMADO']==2025 and b['engine']['ESTADO_FINAL']=='INCLUIDO' for b in base)==1150
assert sum(b['engine']['ANIO_INFORMADO']==2024 and b['engine']['ESTADO_FINAL']=='INCLUIDO' for b in base)==558
shapes=Counter(('numerico' if txt(b['raw']['N_DOC']).isdigit() else 'alfanumerico',len(txt(b['raw']['N_DOC']))) for b in targets)
print('TARGET_PROFILE',json.dumps({'personas':len(targets),'tipo_doc':dict(Counter(txt(b['raw']['TIPO_DOC']) for b in targets)),'dv':dict(Counter(txt(b['raw']['DV']) for b in targets)),'ndoc_forma':str(dict(shapes)),'carreras':dict(Counter(b['engine']['NOMBRE_CARRERA'] for b in targets))},ensure_ascii=False))
files=[('11998',Path('/Users/alexi/Documents/GitHub/CARACTERIZACIÓN/.local/analisis_anual/2026/20261016_002933_892820/entrega/03_RESPALDOS/P3/01_ENTRADAS/DATOSDEALUMNOS_11998.xlsx'),'5d2df5e7998a4ec903e12d51b25114e8f1ff36da57cecaf623e90398b0828f35'),('10246',Path('/Users/alexi/Documents/GitHub/CARACTERIZACIÓN/.local/fuentes_congeladas/2026/P2/2026_P2_20260721_161905/DATOSDEALUMNOS_10246.xlsx'),'b175d63bd9e3280c5757fb0d7292e45fb594d8f076e277f2e06bad2b15e9d869')]
matches={};ums={}
for sid,p,h in files:
 assert digest(p)==h
 wb=openpyxl.load_workbook(p,read_only=True,data_only=True);rows=records(wb['Hoja1']);wb.close();ums[sid]=rows
 idx=defaultdict(list);bidx=defaultdict(list)
 for r in rows:
  n=txt(r.get('RUT')).replace('.','').replace(' ','');idx[n].append(r)
  if '-'in n:bidx[n.rsplit('-',1)[0]].append(r)
 count=Counter();found=[]
 for t in targets:
  r=t['raw'];n=txt(r['N_DOC']).replace('.','').replace(' ','');d=txt(r['DV'])
  exact_ndoc=idx.get(n,[]);exact_full=idx.get(n+'-'+d,[]);body=bidx.get(n,[])
  variants=Counter({'RUT_igual_N_DOC':len(exact_ndoc),'RUT_igual_N_DOC_DV':len(exact_full),'cuerpo_igual_N_DOC_solo_candidato':len(body)})
  for label,value in variants.items():count[label+'_personas']+=bool(value)
  found.append((t,exact_ndoc,exact_full,body))
 matches[sid]=found
 print('SOURCE',sid,json.dumps(dict(count),ensure_ascii=False))
 print('EXACT_UNIQUE',sid,dict(Counter(len({txt(z['CODCLI']) for z in a+b}) for _,a,b,_ in found)))
 print('BODY_UNIQUE',sid,dict(Counter(len({txt(z['CODCLI']) for z in body}) for _,_,_,body in found)))
 print('BODY_DV_DOMAIN',sid,dict(Counter(txt(z['RUT']).rsplit('-',1)[-1] for _,_,_,body in found for z in body)))
 print('BODY_YEAR_ORIGIN',sid,dict(Counter(txt(z['ANOINGRESO']) for _,_,_,body in found for z in body)))

pp=Path('/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/RESPALDO SIES ENVIADO POR CARLOS ARAVENA EL 24-9/2025/Matricula/SIES/06-05-2025/IPSS_Procesamiento.xlsx')
assert digest(pp)=='e2984ccdf22ecf35c46e1f77275fdd12cda47bd2d77a523860e2cd2cf90127f4'
ww=openpyxl.load_workbook(pp,read_only=True,data_only=True);wf=openpyxl.load_workbook(pp,read_only=True,data_only=False)
prep=records(ww['2025_carga']);numbers={txt(t['raw']['N_DOC']) for t in targets};prepidx=defaultdict(list)
for r in prep:
 if txt(r.get('N_DOC')) in numbers:prepidx[txt(r['N_DOC'])].append(r)
formula_counts=Counter();formula_samples=[]
for row in wf['2025_carga'].iter_rows(min_row=2,min_col=73,max_col=74):
 for cell in row:
  if cell.data_type=='f':
   formula_counts[cell.column_letter]+=1
   if len(formula_samples)<3 and not re.search(r'\b\d{7,}\b',str(cell.value)):formula_samples.append(str(cell.value))
print('PREPARACION_RUT_NDOC',json.dumps({'personas_objetivo':len(prepidx),'RUT_igual_candidato_UMAS':sum(any(txt(r.get('RUT')).replace('.','').replace(' ','') in {txt(z['RUT']).replace('.','').replace(' ','') for sid in matches for t,_,_,bb in matches[sid] if txt(t['raw']['N_DOC'])==n for z in bb} for r in rows) for n,rows in prepidx.items()),'formulas':dict(formula_counts),'muestras_formula':formula_samples},ensure_ascii=False))
