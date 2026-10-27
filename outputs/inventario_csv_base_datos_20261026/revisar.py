"""Inspecciona solo la primera línea de CSV/GZ locales, sin exportar contenido."""
import concurrent.futures
import csv
import gzip
import hashlib
import json
import subprocess
import sys
import unicodedata
from pathlib import Path

OUT = Path(__file__).resolve().parent
BASE = next(p for p in Path('/Users/alexi/Library/CloudStorage').iterdir() if unicodedata.normalize('NFC', p.name) == 'OneDrive-InstitutoProfesionalSanSebastián') / '0 BASES DE DATOS'

def read_one(path):
    opener = gzip.open if path.suffix.lower() == '.gz' else open
    with opener(path, 'rb') as f: line = f.readline(65536)
    for encoding in ['utf-8-sig','cp1252']:
        try: text = line.decode(encoding); break
        except UnicodeDecodeError: continue
    separator = max([',',';','\t'], key=text.count)
    cells = [x.strip().upper() for x in next(csv.reader([text], delimiter=separator))]
    coding = any(x in {'CODCLI','COD_CLI'} for x in cells)
    plan = any(x in {'PLAN_DE_ESTUDIO','PLAN_ESTUDIOS','PLAN_ESTUDIO'} for x in cells)
    title = any(x in {'TITULO','NOMBRE_TITULO','FECHA_TITULACION','FECHA_OBT_TIT_GRA','FECHA_OBTENCION_TITULO'} for x in cells)
    has_header = any(x in {'RUT','MRUN','CODCLI','COD_CLI','NUM_DOCUMENTO','N_DOC','CODCARPR','COD_CARRERA','AÑO','ANO','CAT_PERIODO','PERIODO','TIPO_REGISTRO','TOTAL TITULACIONES'} for x in cells)
    trace = any(any(t in x for t in ['TRACE_SCORE_CANDIDATO','TRACE_REASONS_CANDIDATO','RES_TIT_UNIFICADA']) for x in cells)
    return {'cabecera_reconocida':has_header,'codcli':coding,'plan':plan,'titulo':title,'traza':trace,'sha256_primera_linea':hashlib.sha256(line).hexdigest()}

if len(sys.argv) == 3 and sys.argv[1] == '--solo-archivo':
    try:
        print(json.dumps(read_one(Path(sys.argv[2])), ensure_ascii=False))
    except Exception as exc:
        print(json.dumps({'error':type(exc).__name__}))
    sys.exit(0)

files = sorted(p for p in BASE.rglob('*') if p.is_file() and p.suffix.lower() in {'.csv','.gz'})
def inspect(path):
    try:
        p = subprocess.run([sys.executable, __file__, '--solo-archivo', str(path)], capture_output=True, text=True, timeout=5)
        r = json.loads(p.stdout) if p.returncode == 0 else {'error':'ErrorSubproceso'}
    except subprocess.TimeoutExpired: r = {'error':'Timeout'}
    except (ValueError, OSError): r = {'error':'RespuestaInvalida'}
    return {'ruta':str(path), **r}

with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
    results = list(pool.map(inspect, files))
summary = {'archivos':len(files),'inspeccionados':sum('error' not in x for x in results),
           'con_error':sum('error' in x for x in results),'cabecera_no_reconocida':sum(not x.get('cabecera_reconocida') for x in results if 'error' not in x),
           'codcli_y_plan_y_titulo':sum(x.get('codcli',False) and x.get('plan',False) and x.get('titulo',False) for x in results),
           'traza_en_cabecera':sum(x.get('traza',False) for x in results)}
out={'clasificacion':'B estructura; C inspección; E contenido no examinado', 'raiz':str(BASE),
     'resumen':summary,'archivos':results,
     'limites':'Solo primera línea, máximo 65536 bytes por archivo; algunos CSV no tienen encabezados y algunos GZ pueden no ser CSV. No se leen registros ni se reconstruye RUT–MRUN. Un hash de primera línea no es hash del archivo.'}
(OUT/'RESULTADO_AGREGADO.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(summary,ensure_ascii=False))
