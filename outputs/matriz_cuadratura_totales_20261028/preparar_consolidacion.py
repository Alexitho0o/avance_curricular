"""Plan de copias autorizadas y verificación de extracciones; nunca extrae MRUN."""
import csv, glob, hashlib, json, unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
REF=Path('/Users/alexi/Documents/GitHub/CARACTERIZACIÓN/EXTRACCION_MATRICULA_SIES _2007_2025')
def sha(p):
    with open(p,'rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()
def one(p):
    a=glob.glob(p)
    if len(a)!=1: raise ValueError('Ruta no única: '+p)
    return Path(a[0])
copies=[]
def add(p,category,personal,description,expected=None):
    p=Path(p); h=sha(p)
    if expected and expected!=h: raise ValueError('Hash alterado: '+p.name)
    copies.append({'origen':str(p),'categoria':category,'sha256':h,'datos_personales':personal,'descripcion':description})
mat=REF/'salida/reporte_matricula_ip_san_sebastian.csv'
add(mat,'11_SIES_MRUN_IPSS_162','no; MRUN seudonimizado','Extracción institucional derivada de fuente pública, no archivo oficial de carga SIES')
original=mat.with_name('reporte_matricula_ip_san_sebastian_ORIGINAL.csv')
assert sha(original)==sha(mat)
tit=one('/Users/alexi/Library/CloudStorage/OneDrive-*/0 BASES DE DATOS/TITULACION/Titulados_IPSS_162_Consolidado_2007_2025.csv')
add(tit,'11_SIES_MRUN_IPSS_162','no; MRUN seudonimizado','Consolidado institucional de publicación SIES por cod_inst 162','70758082b7b5ab6363b267f58d334f86349a6c355dc5636cf1654b90dedca229')
add(one('/Users/alexi/Library/CloudStorage/OneDrive-*/0 BASES DE DATOS/TITULACION/GLOSARIO_DE_TITULADO_2007_2025_E.pdf'),'12_TITULACION_UNIFICADA_CARGAS','no','Glosario oficial de la publicación de titulados; evidencia documental','b9be9c46aa1c27452d55fc9efaef87c65624c40d4bc1234d21e87897f89af05f')
parent=one('/Users/alexi/Library/CloudStorage/OneDrive-*/Datos DAI*/1.2.1 Datos Institucionales/1.2.1.1 SIES/Enviados/Titulación Unificada')
for year in (2022,2023,2024,2026):
    for p in sorted((parent/str(year)).iterdir()):
        if not p.is_file() or p.suffix.lower() not in ('.csv','.xlsx','.pdf'): continue
        if p.name.startswith('5319 '): cat='09_TITULACION_DATOS_RESTRINGIDOS'
        else: cat='12_TITULACION_UNIFICADA_CARGAS'
        personal='sí' if p.suffix.lower() in ('.csv','.xlsx') and not p.name.startswith('5320 ') else 'no'
        if year==2024:
            desc='AGREGADO de 470 bytes; no es una nómina individual ni acredita carga final'
            personal='no; agregado por carrera'
        elif p.name.startswith('5319 '): desc='Reporte PES 5319 histórico; contiene nombres y documentos'
        elif p.name.startswith('16683'): desc='Libro PES combinado; contiene datos individuales y reportes 5320/5319'
        else: desc='Carga o documentación de Titulación Unificada '+str(year)
        add(p,cat,personal,desc)
hist=json.loads((ROOT/'outputs/reproduccion_puente_20261023_004044/FUENTES_HASHES.json').read_text())
for suffix,cat,desc in (('/MAT_IP_CIISA_2021.xlsx','02_MATRICULA_UNIFICADA_Y_CARGAS_SIES','Matrícula individual histórica 2021'),('/TIT_IP_CIISA_2024.xlsx','12_TITULACION_UNIFICADA_CARGAS','Respaldo de hoja individual de 346 registros; atribución a carga final 2024 pendiente')):
    p,h=next((p,h) for p,h in hist.items() if p.endswith(suffix)); add(p,cat,'sí',desc,h)
catalog=json.loads((ROOT/'data/catalogo_datos/CATALOGO_DATOS_IPSS.json').read_text()); nationals=[]
def walk(x):
    if isinstance(x,dict):
        if 'ruta' in x and any(s in str(x['ruta']) for s in ('20250729_','20250718_Titulados_')):
            nationals.append({'ruta':x['ruta'],'sha256':x.get('sha256'),'accion':'SOLO_REFERENCIA_SIN_COPIA','clase':'B/C metadato de catálogo'})
        for v in x.values(): walk(v)
    elif isinstance(x,list):
        for v in x: walk(v)
walk(catalog)
unique={n['ruta']:n for n in nationals}; nationals=list(unique.values())
report={'clasificacion':'B/C extracción institucional, no fuente oficial individual de SIES','matricula_sha256':sha(mat),'original_identico':True,'matricula_script':str(REF/'codigo_extraccion_matricula.py'),'matricula_script_filtro':'nombre institucional exacto IP SAN SEBASTIAN; se verifica también cod_inst del resultado, sin reextraer','titulados_consolidado_sha256':sha(tit),'otras_salidas_filtradas_localizadas':[str(p) for p in REF.rglob('titulados_ipss_162_*_filtrado.csv')],'pendientes':['La extracción de matrícula termina en 2025; requiere microdato 2026 para estudiar brecha 226.','El consolidado es derivado institucional de fuentes oficiales; no debe rotularse como archivo oficial de carga.']}
old=Path('/Users/alexi/Documents/GitHub/Titulados_IPSS_162_Consolidado_2007_2025.csv')
if old.exists():
    report['consolidado_anterior_no_usar']={'ruta':str(old),'sha256':sha(old),'filas':sum(1 for _ in csv.DictReader(old.open(encoding='utf-8-sig',newline=''))),'uso':'NO_USAR_VERSION_ANTERIOR'}
for p,key,sep,enc in ((mat,'matricula',';','utf-8-sig'),(tit,'titulados',',','utf-8-sig')):
    with p.open(encoding=enc,newline='') as f:
        sample=f.readline(); f.seek(0); delim=',' if sample.count(',')>sample.count(';') else ';'
        reader=csv.DictReader(f,delimiter=delim); rows=list(reader)
    years=sorted({str(r.get('cat_periodo','')) for r in rows}); institutions=sorted({str(r.get('cod_inst','')) for r in rows})
    report[key]={'filas':len(rows),'periodos':years,'cod_inst':institutions}
(OUT/'PLAN_CONSOLIDACION.json').write_text(json.dumps({'copias':copies,'referencias_nacionales_sin_copia':nationals},ensure_ascii=False,indent=2)+'\n')
(OUT/'ACLARACION_EXTRACCIONES.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'copias_planificadas':len(copies),'referencias_nacionales':len(nationals),'aclaracion':report},ensure_ascii=False))
