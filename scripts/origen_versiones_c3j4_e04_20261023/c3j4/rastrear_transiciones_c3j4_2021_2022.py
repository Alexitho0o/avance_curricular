"""Solo lectura de fuentes; salidas agregadas persistentes. DB v7 fijada."""
from pathlib import Path
import json,sys,collections,hashlib
OUTPUT_ROOT=Path('/Users/alexi/Documents/GitHub/avance_curricular/outputs/origen_versiones_c3j4_e04_20261023_163300/c3j4')
OUTPUT_ROOT.mkdir(parents=True,exist_ok=True)
R=Path('/Users/alexi/Documents/GitHub/avance_curricular');sys.path.insert(0,str(R))
from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento
import sqlite3
DB=Path('/Users/alexi/.local/share/ipss/cierre_inf35_03_t3_20261023_154224/DICCIONARIO_SIES.sqlite')
s=sqlite3.connect('file:'+str(DB)+'?mode=ro',uri=True);rs=[json.loads(x[0]) for x in s.execute('select payload from observaciones')];s.close()
ctx=collections.defaultdict(lambda:collections.defaultdict(list))
for r in rs:
 if r['codigo_documental_atribuible'] and r['carrera']=='IETMREOL' and r['plan']=='IETMREOL20211' and str(r['sede_dimension'])=='2' and str(r['jornada_sies'])=='4':ctx[r['persona'],r['CODCLI'],r['plan']][int(r['ano'])].append(r)
focus=[]
for key,years in ctx.items():
 if {r['codigo_documental_atribuible'] for r in years.get(2021,[])}=={'I162S2C3J4V1'} and {r['codigo_documental_atribuible'] for r in years.get(2022,[])}=={'I162S2C3J4V2'}:focus.append((key,years))
assert len(focus)==50
sources=collections.defaultdict(lambda:collections.defaultdict(set));allfields=collections.Counter()
for key,ys in focus:
 for y in (2021,2022):
  for r in ys[y]:
   for e in r['evidencias_matricula']:
    sources[e['fuente']][e['hoja']].add(e['fila']);allfields.update(e.keys())

"""Rastreo de 50 transiciones anuales C3/J4; no modifica fuentes."""
from pathlib import Path


import csv,io,openpyxl
people={key[0] for key,ys in focus};allcontexts=ctx
norm=lambda v:str(v).replace('.0','').strip() if v is not None else ''
from common.diccionario_sies_seguimiento import rut_normalizado,sha256
base=Path('/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián');headers=[{'ruta': '/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/RESPALDO SIES ENVIADO POR CARLOS ARAVENA EL 24-9/Matricula/2022.xlsx', 'sha256': 'ed4e2552e791848d4392066edd54de7ef2ab7d4603957d62ada5aa5174797038', 'hojas': [{'hoja': '2022', 'rows': 1039, 'cols': 33, 'header': ['COD_NIV_GLO', 'TIPO_DOC', 'N_DOC', 'DV', 'A_PAT', 'A_MAT', 'NOMBRE', 'SEXO', 'FECH_NAC', 'NAC', 'PAIS_EST_SEC', 'COD_IES', 'COD_SED', 'COD_CAR', 'MODALIDAD', 'JOR', 'VERSION', 'FOR_ING_ACT', 'ANIO_ING_ACT', 'SEM_ING_ACT', 'ANIO_ING_ORI', 'SEM_ING_ORI', 'ASI_INS_ANT', 'ASI_APR_ANT', 'PROM_PRI_SEM', 'PROM_SEG_SEM', 'ASI_INS_HIS', 'ASI_APR_HIS', 'NIV_ACA', 'SIT_FON_SOL', 'SUS_PRE', 'VIG', 'FECH_CAR']}]}, {'ruta': '/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/Datos DAI (RAW) - 1.1 Datos crudos/1.2.1 Datos Institucionales/1.2.1.1 SIES/Publicados/Matrícula Unificada/MAT_IP_CIISA_2021.xlsx', 'sha256': '8f14b670f00f725412d9dadffea5db9ad2de97b536c88dad992d4370252c401e', 'hojas': [{'hoja': 'MAT_2021', 'rows': 1106, 'cols': 38, 'header': ['MC_CAT_PERIODO', 'MM_N_DOCUMENTO', 'MM_DV', 'MM_APE_PATERNO', 'MM_APE_MATERNO', 'MM_NOMBRES', 'MM_SEXO', 'MM_FECHA_NACIMIENTO', 'MM_NACIONALIDAD', 'MM_N_PASAPORTE', 'MM_TIPO_ESTUDIANTE', 'MM_TIPO_RESIDENCIA', 'MM_PAIS_EST_PREVIOS', 'MM_ANIO_ORIGEN', 'MM_SEM_ORIGEN', 'MM_ANIO_ACTUAL', 'MM_SEM_ACTUAL', 'MM_SEM_SUSPENSION', 'MM_EST_PROC_TER_TIT', 'MM_ANIO_EGRESO', 'MM_SEM_EGRESO', 'MC_COD_INST', 'MC_NOMB_INST', 'MC_CODIGO_UNICO', 'MC_NOMB_CARRERA', 'MC_MODALIDAD', 'MC_JORNADA', 'MC_NOMB_SEDE', 'MC_TIPO_PLAN_CARR', 'MC_CARAC_PLAN_ESP', 'MC_DUR_ESTUDIO_CARR', 'MC_DUR_PROCESO_TIT', 'MC_DUR_TOTAL_CARR', 'MC_COMUNA_SEDE', 'MC_PROVINCIA_SEDE', 'MC_REGION_NOMBRE_SEDE', 'MC_NIVEL_GLOBAL', 'MC_NIVEL_CARRERA_1']}]}, {'ruta': '/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/Datos DAI (RAW) - 1.1 Datos crudos/1.2.1 Datos Institucionales/1.2.1.1 SIES/Publicados/Matrícula Unificada/2022 - 1098/MAT_IP_CIISA_2022.xlsx', 'sha256': '28c826e409e50c482749c1e6cbb6426da86acbbd27e758d80355356a3367fb71', 'hojas': [{'hoja': 'MAT_2022', 'rows': 1034, 'cols': 38, 'header': ['MC_CAT_PERIODO', 'MM_N_DOCUMENTO', 'MM_DV', 'MM_APE_PATERNO', 'MM_APE_MATERNO', 'MM_NOMBRES', 'MM_SEXO', 'MM_FECHA_NACIMIENTO', 'MM_NACIONALIDAD', 'MM_N_PASAPORTE', 'MM_TIPO_ESTUDIANTE', 'MM_TIPO_RESIDENCIA', 'MM_PAIS_EST_PREVIOS', 'MM_ANIO_ORIGEN', 'MM_SEM_ORIGEN', 'MM_ANIO_ACTUAL', 'MM_SEM_ACTUAL', 'MM_SEM_SUSPENSION', 'MM_EST_PROC_TER_TIT', 'MM_ANIO_EGRESO', 'MM_SEM_EGRESO', 'MC_COD_INST', 'MC_NOMB_INST', 'MC_CODIGO_UNICO', 'MC_NOMB_CARRERA', 'MC_MODALIDAD', 'MC_JORNADA', 'MC_NOMB_SEDE', 'MC_TIPO_PLAN_CARR', 'MC_CARAC_PLAN_ESP', 'MC_DUR_ESTUDIO_CARR', 'MC_DUR_PROCESO_TIT', 'MC_DUR_TOTAL_CARR', 'MC_COMUNA_SEDE', 'MC_PROVINCIA_SEDE', 'MC_REGION_NOMBRE_SEDE', 'MC_NIVEL_GLOBAL', 'MC_NIVEL_CARRERA_1']}]}, {'ruta': '/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/Datos DAI (RAW) - 1.1 Datos crudos/1.2.1 Datos Institucionales/1.2.1.5 Otros/Matrícula 1er y 2do semestre/MAT_IP_CIISA_2021_1er y2do semestre.xlsx', 'sha256': '21174b560957fcc94f00459f8f4c0c44cbaf0beab548aab570f078ee01dbd36b', 'hojas': [{'hoja': 'Hoja1', 'rows': 42, 'cols': 4, 'header': ['MC_NIVEL_GLOBAL', 'Pregrado', None, None]}, {'hoja': 'MAT_2021', 'rows': 1206, 'cols': 40, 'header': ['MC_CAT_PERIODO', 'MM_N_DOCUMENTO', 'MM_DV', 'MM_APE_PATERNO', 'MM_APE_MATERNO', 'MM_NOMBRES', 'MM_SEXO', 'MM_FECHA_NACIMIENTO', 'MM_NACIONALIDAD', 'MM_N_PASAPORTE', 'MM_TIPO_ESTUDIANTE', 'MM_TIPO_RESIDENCIA', 'MM_PAIS_EST_PREVIOS', 'MM_ANIO_ORIGEN', 'MM_SEM_ORIGEN', 'MM_ANIO_ACTUAL', 'MM_SEM_ACTUAL', 'MM_SEM_SUSPENSION', 'MM_EST_PROC_TER_TIT', 'MM_ANIO_EGRESO', 'MM_SEM_EGRESO', 'MC_COD_INST', 'MC_NOMB_INST', 'MC_CODIGO_UNICO', 'MC_NOMB_CARRERA', 'MC_MODALIDAD', 'MC_JORNADA', 'MC_NOMB_SEDE', 'MC_TIPO_PLAN_CARR', 'MC_CARAC_PLAN_ESP', 'MC_DUR_ESTUDIO_CARR', 'MC_DUR_PROCESO_TIT', 'MC_DUR_TOTAL_CARR', 'MC_COMUNA_SEDE', 'MC_PROVINCIA_SEDE', 'MC_REGION_NOMBRE_SEDE', 'MC_NIVEL_GLOBAL', 'MC_NIVEL_CARRERA_1', 'U+ 2021', 'NIVEL']}]}, {'ruta': '/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/Datos DAI (RAW) - 1.1 Datos crudos/1.2.1 Datos Institucionales/1.2.1.5 Otros/Matrícula 1er y 2do semestre/MAT_IP_CIISA_2022_1ro y 2do semestre.xlsx', 'sha256': 'b1297a66881d5f3f8fb2bd7bda90ccad03144a350dcd1fcbd5152b1554e4ac25', 'hojas': [{'hoja': 'Hoja1', 'rows': 37, 'cols': 4, 'header': ['1er año', 'Nuevo', None, None]}, {'hoja': 'MAT_2022', 'rows': 1163, 'cols': 39, 'header': ['MC_CAT_PERIODO', 'MM_N_DOCUMENTO', 'MM_DV', 'MM_APE_PATERNO', 'MM_APE_MATERNO', 'MM_NOMBRES', 'MM_SEXO', 'MM_FECHA_NACIMIENTO', 'MM_NACIONALIDAD', 'MM_N_PASAPORTE', 'MM_TIPO_ESTUDIANTE', 'MM_TIPO_RESIDENCIA', 'MM_PAIS_EST_PREVIOS', 'MM_ANIO_ORIGEN', 'MM_SEM_ORIGEN', 'MM_ANIO_ACTUAL', 'MM_SEM_ACTUAL', 'MM_SEM_SUSPENSION', 'MM_EST_PROC_TER_TIT', 'MM_ANIO_EGRESO', 'MM_SEM_EGRESO', 'MC_COD_INST', 'MC_NOMB_INST', 'MC_CODIGO_UNICO', 'MC_NOMB_CARRERA', 'MC_MODALIDAD', 'MC_JORNADA', 'MC_NOMB_SEDE', 'MC_TIPO_PLAN_CARR', 'MC_CARAC_PLAN_ESP', 'MC_DUR_ESTUDIO_CARR', 'MC_DUR_PROCESO_TIT', 'MC_DUR_TOTAL_CARR', 'MC_COMUNA_SEDE', 'MC_PROVINCIA_SEDE', 'MC_REGION_NOMBRE_SEDE', 'MC_NIVEL_GLOBAL', 'MC_NIVEL_CARRERA_1', '1er año']}]}, {'ruta': '/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/2025/SIES/AVANCE CURRICULAR/original/2022.xlsx', 'sha256': 'e2354cde89552049bbc1f565399789499978a647e9380bde5f40e90eaba2a669', 'hojas': [{'hoja': 'Hoja1', 'rows': 68465, 'cols': 25, 'header': ['Número', 'CODCLI', 'RUT', 'DIG', 'NOMBRE', 'PATERNO', 'MATERNO', 'CODCARR', 'CARRERA', 'JORNADA', 'REGIMEN', 'RAMOEQUIV', 'CODRAMO', 'CODSECC', 'ASIGNATURA', 'EXAMEN', 'NOTA_FINAL', 'ANO', 'PERIODO', 'ESTADO', 'DESCRIPCION_ESTADO', 'CONVALIDADO', 'NIVEL', 'ESTADO_ACADEMICO', 'PLAN_DE_ESTUDIO']}]}, {'ruta': '/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/2025/SIES/AVANCE CURRICULAR/original/2021.xlsx', 'sha256': '55659dbbbca0d3111fe48486b13b08f6347ccc77b4f9556d100a946dfc854bc0', 'hojas': [{'hoja': 'Hoja1', 'rows': 70001, 'cols': 25, 'header': ['Número', 'CODCLI', 'RUT', 'DIG', 'NOMBRE', 'PATERNO', 'MATERNO', 'CODCARR', 'CARRERA', 'JORNADA', 'REGIMEN', 'RAMOEQUIV', 'CODRAMO', 'CODSECC', 'ASIGNATURA', 'EXAMEN', 'NOTA_FINAL', 'ANO', 'PERIODO', 'ESTADO', 'DESCRIPCION_ESTADO', 'CONVALIDADO', 'NIVEL', 'ESTADO_ACADEMICO', 'PLAN_DE_ESTUDIO']}]}];results=[];local={};individual=[]
for meta in headers[:5]:
 p=Path(meta['ruta']);wb=openpyxl.load_workbook(p,read_only=True,data_only=False)
 tab=next(t['hoja'] for t in meta['hojas'] if t['hoja'].startswith('MAT_') or t['hoja']=='2022');ws=wb[tab];rows=list(ws.iter_rows());hd=[c.value for c in rows[0]];out=[];fam=[];fc=0;indexes=[]
 for row in rows[1:]:
  z=dict(zip(hd,[c.value for c in row]));code=z.get('MC_CODIGO_UNICO')
  if code is None:code='I'+norm(z.get('COD_IES'))+'S'+norm(z.get('COD_SED'))+'C'+norm(z.get('COD_CAR'))+'J'+norm(z.get('JOR'))+'V'+norm(z.get('VERSION'))
  try:person=rut_normalizado(norm(z.get('MM_N_DOCUMENTO',z.get('N_DOC')))+'-'+norm(z.get('MM_DV',z.get('DV'))))
  except ValueError:continue
  if code.startswith('I162S2C3J4V'):
   fam.append((person,code,z))
   if person in people:
    out.append((person,code,z));indexes.append(row[0].row)
    col=hd.index('MC_CODIGO_UNICO') if 'MC_CODIGO_UNICO' in hd else hd.index('VERSION');fc+=row[col].data_type=='f'
  if person in people:individual.append({'persona':person,'fuente':str(p),'hoja':tab,'fila':row[0].row,'codigo':code,'ingreso_actual':z.get('MM_ANIO_ACTUAL',z.get('ANIO_ING_ACT')),'ingreso_origen':z.get('MM_ANIO_ORIGEN',z.get('ANIO_ING_ORI'))})
 local[p.name]=(out,fam)
 results.append({'archivo':str(p),'sha256':sha256(p),'hoja':tab,'n_datos':len(rows)-1,'foco_personas_en_familia':len({q[0] for q in out}),'foco_filas':len(out),'foco_codigos':dict(collections.Counter(q[1] for q in out)),'foco_ingreso_actual':dict(collections.Counter(norm(q[2].get('MM_ANIO_ACTUAL',q[2].get('ANIO_ING_ACT'))) for q in out)),'foco_ingreso_origen':dict(collections.Counter(norm(q[2].get('MM_ANIO_ORIGEN',q[2].get('ANIO_ING_ORI'))) for q in out)),'filas_foco':indexes,'formulas_codigo_foco':fc,'familia_total_filas':len(fam),'familia_codigos':dict(collections.Counter(q[1] for q in fam))});wb.close()
# Fuente RAW CSV 2022 anterior a la consolidación.
p=base/'Datos DAI (RAW) - 1.1 Datos crudos/1.2.1 Datos Institucionales/1.2.1.1 SIES/Enviados/Matrícula Unificada/2022/2022.csv';raw=list(csv.DictReader(io.StringIO(p.read_text(encoding='utf-8-sig')),delimiter=';'));rawfocus=[];rawfam=[]
for i,z in enumerate(raw,2):
 code='I'+norm(z.get('COD_IES'))+'S'+norm(z.get('COD_SED'))+'C'+norm(z.get('COD_CAR'))+'J'+norm(z.get('JOR'))+'V'+norm(z.get('VERSION'))
 try:person=rut_normalizado(norm(z.get('N_DOC'))+'-'+norm(z.get('DV')))
 except ValueError:continue
 if code.startswith('I162S2C3J4V'):
  rawfam.append((person,code,z))
  if person in people:rawfocus.append((person,code,i,z));individual.append({'persona':person,'fuente':str(p),'hoja':'CSV','fila':i,'codigo':code,'ingreso_actual':z['ANIO_ING_ACT'],'ingreso_origen':z['ANIO_ING_ORI']})
assert len(rawfocus)==50 and {v[1] for v in rawfocus}=={'I162S2C3J4V2'}
results.append({'archivo':str(p),'sha256':sha256(p),'hoja':'CSV con encabezados','n_datos':len(raw),'foco_personas_en_familia':len({q[0] for q in rawfocus}),'foco_filas':len(rawfocus),'foco_codigos':dict(collections.Counter(q[1] for q in rawfocus)),'filas_foco':[q[2] for q in rawfocus],'familia_total_filas':len(rawfam),'familia_codigos':dict(collections.Counter(q[1] for q in rawfam)),'foco_fech_car':dict(collections.Counter(q[3]['FECH_CAR'] for q in rawfocus))})
# Relación de transición sobre todos los sujetos presentes en ambas fuentes, no sólo50.
a={p:c for p,c,z in local['MAT_IP_CIISA_2021.xlsx'][1]};b=collections.defaultdict(set)
for p,c,z in rawfam:b[p].add(c)
trans=collections.Counter((a[p],next(iter(cs))) for p,cs in b.items() if p in a and len(cs)==1)
res={'universo_foco':50,'codigo_2021':'I162S2C3J4V1','codigo_2022':'I162S2C3J4V2','mismo_contexto_actual':{'carrera':'IETMREOL','plan':'IETMREOL20211','sede':'2','jornada':'4'},'fuentes':results,'familia_interseccion_fuentes_2021_2022':{'personas_codigo_2022_unico':sum(trans.values()),'transiciones':[{'codigo_2021':k[0],'codigo_2022':k[1],'personas':n} for k,n in trans.items()]},'clasificacion':'B/C observado; no se atribuye regla causal','nota':'El código ya es valor literal en las fuentes de entrada; no fue asignado por la consolidación2026.'}

q21=collections.defaultdict(list)
for qp,qc,qz in local['MAT_IP_CIISA_2021.xlsx'][1]:q21[qp].append((qc,qz))
q22=collections.defaultdict(list)
for qp,qc,qz in rawfam:q22[qp].append((qc,qz))
common_people=set(q21)&set(q22)
res['qa_cardinalidad_identidad']={
 'personas_foco':len(people),'contextos_foco':len(focus),'CODCLI_distintos_foco':len({key[1] for key,ys in focus}),
 'personas_comunes_familia':len(common_people),
 'max_filas_2021_por_persona_comun':max(len(q21[qp]) for qp in common_people),
 'max_codigos_2021_por_persona_comun':max(len({qc for qc,qz in q21[qp]}) for qp in common_people),
 'max_filas_2022_por_persona_comun':max(len(q22[qp]) for qp in common_people),
 'max_codigos_2022_por_persona_comun':max(len({qc for qc,qz in q22[qp]}) for qp in common_people),
 'max_filas_2021_por_persona_foco':max(len(q21[qp]) for qp in people),
 'max_filas_2022_por_persona_foco':max(len(q22[qp]) for qp in people),
 'TIPO_DOC_RAW2022_foco':dict(collections.Counter(norm(qz.get('TIPO_DOC')) for qp,qc,qi,qz in rawfocus)),
 'TIPO_DOC_RAW2022_comunes':dict(collections.Counter(norm(qz.get('TIPO_DOC')) for qp in common_people for qc,qz in q22[qp])),
 'pasaporte_no_vacio_2021_foco':sum(bool(norm(qz.get('MM_N_PASAPORTE'))) for qp in people for qc,qz in q21[qp]),
 'nota_tipo_documento_2021':'MAT_2021 no contiene TIPO_DOC: cruce por MM_N_DOCUMENTO + MM_DV; comprobar pasaporte explícito, sin inventar tipo.'
}
assert res['qa_cardinalidad_identidad']['max_filas_2021_por_persona_comun']==1
assert res['qa_cardinalidad_identidad']['max_filas_2022_por_persona_comun']==1
assert res['qa_cardinalidad_identidad']['CODCLI_distintos_foco']==50

(OUTPUT_ROOT/'PRIMARY.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n')
# Evidencia individual no se emite: sólo localizadores agregados en salida.


f21=local['MAT_IP_CIISA_2021.xlsx'][1];f22=local['MAT_IP_CIISA_2022.xlsx'][1]
b21=collections.defaultdict(list);b22=collections.defaultdict(list)
for p,c,z in f21:b21[p].append((c,z))
for p,c,z in f22:b22[p].append((c,z))
fields=['MM_ANIO_ACTUAL','MM_SEM_ACTUAL','MM_ANIO_ORIGEN','MM_SEM_ORIGEN','MC_TIPO_PLAN_CARR','MC_CARAC_PLAN_ESP','MC_DUR_ESTUDIO_CARR','MC_DUR_PROCESO_TIT','MC_DUR_TOTAL_CARR','MM_VIGENCIA','MM_VIGENTE','MC_NOMBRE_CARRERA']
groups=collections.defaultdict(list)
for p,aa in b21.items():
 bb=b22.get(p,[])
 if len(aa)==len(bb)==1:groups[(aa[0][0],bb[0][0])].append((p,aa[0][1],bb[0][1]))
out={'clasificacion':'B/C; patrones observados, no regla causal','fuentes':'rutas/hash en regla_c3j4_primary.json','cardinalidad':{'filas_2021':len(f21),'personas_2021':len(b21),'filas_2022':len(f22),'personas_2022':len(b22),'comunes':len(set(b21)&set(b22))},'transiciones':[]}
for k,gg in groups.items():
 z={'2021':k[0],'2022':k[1],'personas':len(gg),'campos':{}}
 for field in fields:
  if any(field in q[1] or field in q[2] for q in gg):z['campos'][field]=dict(collections.Counter(str(q[1].get(field))+' → '+str(q[2].get(field)) for q in gg))
 out['transiciones'].append(z)
# literal source links/document metadata, no identity fields.
import zipfile,xml.etree.ElementTree as ET
out['paquetes_fuentes']=[]
for m in headers[:5]:
 p=Path(m['ruta'])
 with zipfile.ZipFile(p) as z:
  entries=z.namelist();root=ET.fromstring(z.read('docProps/core.xml'))
  out['paquetes_fuentes'].append({'archivo':str(p),'core':{n.tag.split('}')[-1]:n.text for n in root},'connections':[n for n in entries if any(q in n for q in ['connections','queryTables','externalLinks','vbaProject'])]})
(OUTPUT_ROOT/'PATRONES.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')


rby={p:z for p,c,z in rawfam};out=[]
fields=['FOR_ING_ACT','ANIO_ING_ACT','SEM_ING_ACT','ANIO_ING_ORI','SEM_ING_ORI','VIG','FECH_CAR','NIV_ACA','ASI_INS_ANT','ASI_APR_ANT','ASI_INS_HIS','ASI_APR_HIS','MODALIDAD']
for k,gg in groups.items():
 pp={q[0] for q in gg};record={'codigos':list(k),'personas':len(pp),'campos_raw2022':{}}
 for f in fields:record['campos_raw2022'][f]=dict(collections.Counter(norm(rby[p].get(f)) for p in pp))
 # Personas y contextos en diccionario (resumen sin identificadores).
 rr=[r for r in rs if r['persona'] in pp]
 record['contextos_en_diccionario']=[{'carrera':k1[0],'plan':k1[1],'sede':k1[2],'jornada':k1[3],'personas':len(v)} for k1,v in ((k1,{r['persona'] for r in vals}) for k1,vals in __import__('itertools').groupby(sorted(rr,key=lambda r:(str(r['carrera']),str(r['plan']),str(r['sede_dimension']),str(r['jornada_sies']))),key=lambda r:(str(r['carrera']),str(r['plan']),str(r['sede_dimension']),str(r['jornada_sies']))))]
 out.append(record)
(OUTPUT_ROOT/'SEPARACION.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')


all_lots=collections.Counter((code,norm(z.get('FECH_CAR'))) for person,code,z in rawfam)
full_lots={'clasificacion':'B/C','filas_total_familia':len(rawfam),'codigo_lote':[{'codigo':k[0],'FECH_CAR':k[1],'filas':n} for k,n in sorted(all_lots.items())]}
(OUTPUT_ROOT/'LOTES.json').write_text(json.dumps(full_lots,ensure_ascii=False,indent=2)+'\n')
assert len(focus)==50
assert len(people)==50
assert all(z['foco_filas']==50 and z['foco_personas_en_familia']==50 for z in results)
assert all(z.get('formulas_codigo_foco',0)==0 for z in results)
print(json.dumps({'qa':'PASS','personas':50,'expedientes':50,'fuentes_contrastadas':len(results),'lotes':full_lots},ensure_ascii=False))
