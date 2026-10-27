"""Contrasta cobertura observada de TITULADOS y fecha del caso, sin alterar fuentes."""
import hashlib, io, json
from datetime import datetime
from pathlib import Path
import openpyxl

OUT=Path(__file__).resolve().parent
ROOT=next(Path('/Users/alexi/Library/CloudStorage').glob('OneDrive-InstitutoProfesionalSanSebasti*'))
CASES=Path('/Users/alexi/.local/share/ipss/revision_21_ramos_4_expedientes_20261026/DETALLE_CUATRO_CASOS_V2.json')
cases=json.loads(CASES.read_text())
case=next(c for c in cases if any(x['carrera']=='TCRE' for x in c['contextos_v11']))
body,dv=case['RUT'].split('-')
def norm(v):
    if isinstance(v,float) and v.is_integer():v=int(v)
    return str(v or '').strip().upper()
def read(p):
    blob=p.read_bytes()
    return openpyxl.load_workbook(io.BytesIO(blob),read_only=True,data_only=True),hashlib.sha256(blob).hexdigest()
def check(p,h):assert hashlib.sha256(p.read_bytes()).hexdigest()==h

raw=ROOT/'Datos DAI (RAW) - 1.1 Datos crudos'/'1.2.1 Datos Institucionales'
doc=next(raw.rglob('Informe de Titulados 2025_vf.xlsx'))
w,h=read(doc);s=w['Hoja1'];it=s.values;headers=[norm(v) for v in next(it)];hits=[]
for rn,row in enumerate(it,2):
    if norm(row[headers.index('NUM_DOCUMENTO')])==body and norm(row[headers.index('DV')])==dv:
        hits.append((rn,row[headers.index('FECHA_OBT_TIT_GRA')]))
w.close();check(doc,h);assert len(hits)==1 and isinstance(hits[0][1],datetime)
result={'docencia':{'archivo':doc.name,'hoja':'Hoja1','fila':hits[0][0],'sha256':h,'campo':'FECHA_OBT_TIT_GRA','fecha_observada':hits[0][1].date().isoformat()},'respaldos':[]}
for name in ['TITULADOS_3280.xlsx','TITULADOS_3280 (1).xlsx','TITULADOS_3280 1.xlsx']:
    p=ROOT/'Archivos de chat de Microsoft Teams'/name
    w,h=read(p);s=w.worksheets[0];it=s.values;headers=[norm(v) for v in next(it)];dates=[];errors=0;count=0;matches=0
    for row in it:
        if not any(v is not None for v in row):continue
        count+=1;value=row[headers.index('FECHA')]
        if isinstance(value,datetime):dates.append(value)
        if isinstance(value,str) and value.startswith('#'):errors+=1
        if norm(row[headers.index('RUT')])==body and norm(row[headers.index('DIG')])==dv:matches+=1
    assert dates
    result['respaldos'].append({'archivo':name,'sha256':h,'hoja':s.title,'filas_no_vacias':count,
        'fecha_maxima_observada':max(dates).date().isoformat(),'fecha_caso_posterior':hits[0][1]>max(dates),
        'coincidencias_rut_dv':matches,'codcli_en_cabecera':'CODCLI' in headers,
        'plan_en_cabecera':any(x in headers for x in ('PLAN','PLAN_DE_ESTUDIO','PLAN_ESTUDIOS','CODPESTUD')),
        'errores_cacheados_campo_fecha':errors,'hash_conservado':True})
    w.close();check(p,h)
result['limite']='Máximo de FECHA observado, no fecha de exportación ni prueba de cobertura exhaustiva. Ausencia del caso no prueba causa del faltante.'
payload=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
for c in cases:
    assert c['RUT'].split('-')[0] not in payload
    for d in c['datosalumnos']:
        if d['CODCLI']:assert norm(d['CODCLI']) not in payload
(OUT/'COMPARACION_REPORTES.json').write_text(payload)
print(payload)
