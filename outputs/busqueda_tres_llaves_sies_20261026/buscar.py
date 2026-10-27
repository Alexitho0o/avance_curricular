"""Inventaria candidatos por tres llaves; resultados y nombres permanecen privados."""
import collections
import concurrent.futures
import hashlib
import json
import os
import re
import subprocess
import sys
import unicodedata
import zipfile
from pathlib import Path

PRIVATE = Path('/Users/alexi/.local/share/ipss/revision_21_ramos_4_expedientes_20261026/DETALLE_CUATRO_CASOS_V2.json')
OUT_PRIVATE = Path('/Users/alexi/.local/share/ipss/busqueda_tres_llaves_sies_20261026')
OUT = Path(__file__).resolve().parent
CLOUD = next(p for p in Path('/Users/alexi/Library/CloudStorage').iterdir() if unicodedata.normalize('NFC',p.name)=='OneDrive-InstitutoProfesionalSanSebastián')
BASE = CLOUD/'Datos DAI (RAW) - 1.1 Datos crudos'/'1.2.1 Datos Institucionales'/'1.2.1.1 SIES'/'Enviados'

def targets():
    cases=json.loads(PRIVATE.read_text()); c=next(x for x in cases if any(y['carrera']=='TCRE' for y in x['contextos_v11']))
    codes={str(x['CODCLI']).strip().upper().encode() for x in c['datosalumnos'] if x['CODCLI']}
    assert len(codes)==3
    body,dv=c['RUT'].split('-'); return codes,body,dv

def inspect(path):
    codes,body,dv=targets()
    esc=re.escape(body.encode()); bpat=re.compile(rb'(?<!\d)0*'+esc+rb'(?!\d)')
    decorated=(f'{int(body):,}'.replace(',','.')).encode()
    full=re.compile(rb'(?<!\d)(?:0*'+esc+rb'|'+re.escape(decorated)+rb')[\s.-]*'+re.escape(dv.encode())+rb'(?![\dK])',re.I)
    keypatterns=[re.compile(rb'(?<![A-Z0-9])'+re.escape(c)+rb'(?![A-Z0-9])',re.I) for c in codes]
    status={'codcli':False,'rut_y_dv_juntos':False,'rut_sin_dv':False}
    def scan(stream):
        overlap=b''
        while True:
            b=stream.read(1024*1024)
            if not b:break
            block=overlap+b
            status['codcli']|=any(p.search(block) is not None for p in keypatterns)
            status['rut_y_dv_juntos']|=full.search(block) is not None
            status['rut_sin_dv']|=bpat.search(block) is not None or decorated in block
            overlap=block[-128:]
    if path.suffix.lower() in {'.xlsx','.xlsm'}:
        with zipfile.ZipFile(path) as z:
            for n in z.namelist():
                if n.startswith(('xl/sharedStrings','xl/worksheets/')) and n.endswith('.xml'):
                    with z.open(n) as s:scan(s)
    else:
        with path.open('rb') as s:scan(s)
    # Hash de la fuente completa, sin copiarla ni guardar sus filas.
    h=hashlib.sha256()
    with path.open('rb') as s:
        for b in iter(lambda:s.read(1048576),b''):h.update(b)
    return {'sha256':h.hexdigest(),**status}

if len(sys.argv)==3 and sys.argv[1]=='--uno':
    try:print(json.dumps(inspect(Path(sys.argv[2]))))
    except Exception as e:print(json.dumps({'error':type(e).__name__}))
    sys.exit(0)

OUT_PRIVATE.mkdir(parents=True,mode=0o700,exist_ok=True)
assert subprocess.run(['git','-C',str(OUT_PRIVATE),'rev-parse','--show-toplevel'],capture_output=True).returncode!=0
files=sorted(p for p in BASE.rglob('*') if p.is_file() and p.suffix.lower() in {'.xlsx','.xlsm','.csv','.tsv'})
def one(path):
    try:
        proc=subprocess.run([sys.executable,__file__,'--uno',str(path)],capture_output=True,text=True,timeout=12)
        data=json.loads(proc.stdout) if proc.returncode==0 else {'error':'Subproceso'}
    except subprocess.TimeoutExpired:data={'error':'Timeout'}
    except (OSError,ValueError):data={'error':'RespuestaInvalida'}
    return {'ruta':str(path),**data}
with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool: rows=list(pool.map(one,files))
target=OUT_PRIVATE/'INVENTARIO_PRIVADO.json'
fd=os.open(target,os.O_CREAT|os.O_WRONLY|os.O_TRUNC,0o600)
with os.fdopen(fd,'w') as f:json.dump(rows,f,ensure_ascii=False,indent=2)
counts=collections.Counter()
for r in rows:
    counts['archivos']+=1
    if 'error' in r:counts['error_'+r['error']]+=1
    else:
        counts['leidos']+=1
        for k in ('codcli','rut_y_dv_juntos','rut_sin_dv'):
            if r[k]:counts['archivos_con_'+k]+=1
summary={'clasificacion':'C barrido literal; E no acredita coincidencia en una misma fila','carpeta':str(BASE),
         'extensiones':['xlsx','xlsm','csv','tsv'],'conteos':dict(counts),
         'inventario_privado':str(target),
         'limites':'Barrido de bytes XML o texto: resultados son candidatos de archivo, no coincidencias de fila ni DV en columna aparte. No se revisan ZIP/RAR/PDF ni otros formatos. Un archivo leido puede contener rut y codcli en filas diferentes.'}
(OUT/'RESUMEN_AGREGADO.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(summary,ensure_ascii=False))
