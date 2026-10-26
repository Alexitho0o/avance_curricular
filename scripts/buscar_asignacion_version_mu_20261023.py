"""Busca evidencia de implementación; no ejecuta motores ni modifica las fuentes."""
from pathlib import Path
import subprocess, json, re, hashlib, signal

R = Path('/Users/alexi/Documents/GitHub/avance_curricular')
O = R/'outputs/origen_versiones_c3j4_e04_20261023_163300'
EXT = {'.py','.sql','.ipynb','.r','.vba','.m','.ps1','.sh'}
PAT = re.compile(r'IETMREOL|IINF20241|I162S2C3J4|Fallback VERSION|VERSION.{0,100}(?:max|map|apply|astype)|(?:max|map|apply).{0,100}VERSION', re.I)

def relevant(text):
    lines=text.splitlines()
    found=[i for i,l in enumerate(lines,1) if PAT.search(l)]
    years=sorted(set(re.findall(r'(?<!\d)202[1256](?!\d)',text)))
    return {'lineas_candidatas':found,'anos_mencionados':years,
            'cadenas_foco':{s:text.count(s) for s in ['IETMREOL','IINF20241','I162S2C3J4','Fallback VERSION']}}

results=[]
for repo in [R,R.parent/'CARACTERIZACIÓN',R.parent/'IPSS_Procesos_SIES']:
    obj=subprocess.check_output(['git','-C',str(repo),'rev-list','--objects','--all'],text=True)
    entries={}
    for line in obj.splitlines():
        if ' ' not in line: continue
        sha,path=line.split(' ',1)
        if Path(path).suffix.lower() in EXT: entries.setdefault(sha,path)
    proc=subprocess.Popen(['git','-C',str(repo),'cat-file','--batch'],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
    hits=[]; errors=[]
    for sha,path in entries.items():
        proc.stdin.write((sha+'\n').encode());proc.stdin.flush()
        header=proc.stdout.readline().decode().strip().split()
        if len(header)!=3 or header[1]!='blob':
            errors.append({'objeto':sha,'ruta':path,'cabecera':header});continue
        data=proc.stdout.read(int(header[2]));proc.stdout.read(1)
        info=relevant(data.decode('utf-8',errors='replace'))
        if info['lineas_candidatas']:
            hits.append({'objeto_git':sha,'ruta':path,'sha256':hashlib.sha256(data).hexdigest(),**info})
    proc.stdin.close();proc.wait()
    results.append({'repositorio':str(repo),'objetos_codigo_leidos':len(entries),'hallazgos_para_inspeccion':hits,'errores':errors})
    print(repo.name,len(entries),len(hits),flush=True)

inv=json.loads((R/'outputs/retencion_intermedia_t2_t3/20261021_093412_git_onedrive_mu2025/INVENTARIO_ONEDRIVE.json').read_text())
disk=[]
def timeout_handler(*args): raise TimeoutError('Lectura OneDrive excede 5 segundos; pendiente de disponibilidad')
signal.signal(signal.SIGALRM,timeout_handler)
for entry in inv['scripts_consultas']:
    p=Path(entry['ruta'])
    if '/Enviados/FCU/2026/' in str(p):
        disk.append({'ruta':str(p),'estado':'No releído: respaldo FCU2026 fuera del proceso/períodos investigados; inventariado previamente.'})
        continue
    try:
        signal.alarm(5)
        data=p.read_bytes(); info=relevant(data.decode('utf-8',errors='replace'))
        disk.append({'ruta':str(p),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),**info})
    except Exception as exc: disk.append({'ruta':str(p),'error':str(exc)})
    finally: signal.alarm(0)

code=R/'codigo_gobernanza_v2.py'
history=subprocess.check_output(['git','-C',str(R),'log','--all','--reverse','--format=%H %aI %s','-S','Fallback VERSION','--','codigo_gobernanza_v2.py'],text=True)
output={'clasificacion':'C','metodo':'Inspección estática de todos los blobs locales de extensiones de código; clasificación de 150 rutas del inventario OneDrive previo y relectura de las ajenas a FCU2026. No ejecución del motor ni acceso remoto.',
        'git':results,'onedrive':disk,
        'fallback_actual':{'ruta':str(code),'sha256':hashlib.sha256(code.read_bytes()).hexdigest(),'lineas':[3763,3766,3781],'alcance_observado':'Generador MU2026; primero parsea código final; solo con VERSION ausente toma máximo por COD_CAR+JOR del catálogo. No prueba de su uso en MU2021/2022/2025.','historial_introduccion':history},
        'limite':'No localizar una regla en esta cobertura no demuestra inexistencia universal. Las fechas Git describen versiones de código, no ejecución ni asignación académica.'}
(O/'BUSQUEDA_IMPLEMENTACIONES.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
print('Terminado',len(disk),'respaldos',flush=True)
