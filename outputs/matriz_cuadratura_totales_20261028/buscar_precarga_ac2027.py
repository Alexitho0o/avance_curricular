"""Búsqueda de nombres y metadatos AC2027; no lee nóminas ni altera fuentes."""
import hashlib,json,os,unicodedata
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
ROTULO='No existe aún (D, Alexi): el proceso AC 2027 ocurre después de MU 2027 (abril–mayo 2027); su precarga contendrá la matrícula 2026 registrada por SIES'
def norm(s):
    return ''.join(c for c in unicodedata.normalize('NFD',str(s).lower()) if not unicodedata.combining(c))
def sha(p):
    with open(p,'rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def candidate(s):
    n=norm(s)
    return '2027' in n and ('5809' in n or 'precarga' in n or 'avance curricular' in n or 'avance_curricular' in n)
def catalog_paths(x):
    if isinstance(x,dict):
        for k,v in x.items():
            if k in ('ruta','ruta_consolidada','origen') and isinstance(v,str):yield v
            elif isinstance(v,(dict,list)):yield from catalog_paths(v)
    elif isinstance(x,list):
        for v in x:yield from catalog_paths(v)
cats=[]
for rel in ('data/catalogo_fuentes/CATALOGO_FUENTES.json','data/catalogo_datos/CATALOGO_DATOS_IPSS.json'):
    p=ROOT/rel;paths=list(catalog_paths(json.loads(p.read_text())))
    cats.append({'ruta':str(p),'sha256':sha(p),'coincidencias':[s for s in paths if candidate(Path(s).name)]})
od=[p for p in Path('/Users/alexi/Library/CloudStorage').glob('OneDrive-*') if 'institutoprofesional' in norm(p.name)]
assert len(od)==1
ac=[p for p in od[0].glob('Datos DAI*/1.2.1 Datos Institucionales/1.2.1.1 SIES/Enviados/*') if norm(p.name)=='avance curricular']
assert len(ac)==1
scans=[]
for base in (ac[0],Path('/Users/alexi/Downloads'),Path('/Users/alexi/Desktop')):
    item={'raiz':str(base),'existe':base.exists(),'archivos':0,'directorios':0,'errores':[],'coincidencias':[]}
    for here,dirs,files in os.walk(base,onerror=lambda e:item['errores'].append(type(e).__name__)):
        dirs[:]=[d for d in dirs if d not in ('.git','node_modules','__pycache__')]
        item['directorios']+=1
        for name in files:
            item['archivos']+=1
            if candidate(name):item['coincidencias'].append(str(Path(here)/name))
    scans.append(item)
years=sorted(p.name for p in ac[0].iterdir() if p.is_dir())
result={'fecha':'2026-10-28','proceso':'Avance Curricular 2027','referencia_matricula_esperada':2026,'resultado_observado':'B: no localizada en los ámbitos revisados','rotulo_vigente':ROTULO,'clase_rotulo':'D decisión de Alexi; no fecha oficial A','calendario_oficial_2027_verificado':False,'catalogos':cats,'ambitos':scans,'carpetas_enviados_avance_curricular':years,'existe_carpeta_2027':'2027' in years,'metodo_mu2026_ejecutado':False,'fuentes_copiadas':False,'limite':'Búsqueda de nombres y metadatos locales; no acredita ausencia universal ni calendario oficial.'}
assert not any(x['coincidencias'] for x in cats+scans)
assert not result['existe_carpeta_2027']
(OUT/'BUSQUEDA_PRECARGA_AC2027.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
lines=['# Búsqueda de precarga Avance Curricular 2027','','**'+ROTULO+'.**','','D: indicación explícita de Alexi. No se presenta como calendario oficial A.','', 'B/C: no localizada al 28-10-2026 en los dos catálogos, Enviados/Avance Curricular, Descargas ni Escritorio. Carpetas observadas en Enviados: '+', '.join(years)+'. No hay carpeta 2027.','','| Ámbito | Archivos enumerados | Coincidencias | Errores |','|---|---:|---:|---:|']
for x in scans:lines.append(f"| {x['raiz']} | {x['archivos']} | {len(x['coincidencias'])} | {len(x['errores'])} |")
lines+=['','Rutas y hashes de catálogos: JSON adjunto. No se copió ninguna fuente ni se ejecutó el método MU2026. La fecha oficial del proceso permanece sin verificar.']
(OUT/'BUSQUEDA_PRECARGA_AC2027.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({'resultado':result['resultado_observado'],'carpetas':years,'coincidencias':0},ensure_ascii=False))
