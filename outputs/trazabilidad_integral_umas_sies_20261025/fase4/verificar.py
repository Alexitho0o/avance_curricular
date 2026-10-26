"""Verificación de preservación, fórmulas y paquete final V19, sin recálculo nativo."""
from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E
from collections import Counter
import json,hashlib,posixpath,re,subprocess,shutil,os
from datetime import datetime
from zoneinfo import ZoneInfo

OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
P=Path('/Users/alexi/.local/share/ipss/trazabilidad_integral_fase4_20261025')
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def git(*args):return subprocess.check_output(['git','-C',str(ROOT),*args],text=True).strip()
a=load(OUT/'ENSAMBLADO.json');dst=Path(a['salida_privada'])
z=ZipFile(dst);base=ZipFile(a['base']);orig=ZipFile(a['original'])
NS='http://schemas.openxmlformats.org/spreadsheetml/2006/main';n={'s':NS};q=lambda t:'{'+NS+'}'+t
def root(zz,i):return E.fromstring(zz.read(f'xl/worksheets/sheet{i}.xml'))
def cellmap(zz,i):return {c.get('r'):c for c in root(zz,i).findall('.//s:sheetData/s:row/s:c',n)}
def strings(zz):return [''.join(x.itertext()) for x in E.fromstring(zz.read('xl/sharedStrings.xml'))] if 'xl/sharedStrings.xml' in zz.namelist() else []
so=strings(orig)
def val(c,ss=[]):
    if c is None:return None
    v=c.find(q('v'));t=c.find(q('is'))
    if t is not None:return ''.join(t.itertext())
    if v is None:return None
    if c.get('t')=='s':return ss[int(v.text)]
    if c.get('t') not in ['str','e','b']:
        try:return float(v.text)
        except (TypeError,ValueError):pass
    return v.text
checks=[]
def check(label,ok,detail=None):checks.append({'control':label,'resultado':'PASA' if ok else 'FALLIDO','detalle':detail})
check('ZIP íntegro',z.testzip() is None)
for name in z.namelist():
    if name.endswith('.xml') or name.endswith('.rels'):E.fromstring(z.read(name))
check('Todos los XML parseables',True)
check('57 hojas,13 gráficos,37 tablas',a['hojas']==57 and a['graficos']==13 and a['tablas']==37)
graphics=[p for p in base.namelist() if p.startswith(('xl/charts/','xl/drawings/'))]
check('Partes de gráficos y dibujos idénticas a V18',all(z.read(p)==base.read(p) for p in graphics),len(graphics))
sources={10,12,21,25,26}
for i in sources:
    o=cellmap(orig,i);d=cellmap(z,i)
    check(f'Hoja individual original {i}: valores y fórmulas preservados',o.keys()==d.keys() and all(val(o[k],so)==val(d[k]) and E.tostring(o[k].find(q('f')))==E.tostring(d[k].find(q('f'))) if o[k].find(q('f')) is not None else val(o[k],so)==val(d[k]) and d[k].find(q('f')) is None for k in o))
numeric_changes=[];formula_changes=[]
for i in range(1,56):
    if i in sources or i==28:continue
    b=cellmap(base,i);d=cellmap(z,i)
    for ref,c in b.items():
        old=val(c);new=val(d.get(ref))
        if isinstance(old,float) and old!=new:numeric_changes.append([i,ref])
        f=c.find(q('f'))
        if f is not None:
            ff=d.get(ref).find(q('f')) if ref in d else None
            if ff is None or f.text!=ff.text:formula_changes.append([i,ref])
check('Cifras numéricas históricas V18 conservadas',not numeric_changes,numeric_changes)
check('Fórmulas vigentes V18 conservadas',not formula_changes,formula_changes)
restored_missing=[]
for i in range(1,30):
    if i==28:continue
    o=cellmap(orig,i);d=cellmap(z,i)
    for ref,c in o.items():
        if c.find(q('f')) is not None and (ref not in d or d[ref].find(q('f')) is None):restored_missing.append([i,ref])
check('Todas las fórmulas originales recuperadas o sustituidas por corrección vigente',not restored_missing,restored_missing)
orphan_shared=[];errors=[];duplicates=[]
for i in range(1,58):
    rr=root(z,i);cs=rr.findall('.//s:sheetData/s:row/s:c',n);refs=[c.get('r') for c in cs]
    if len(refs)!=len(set(refs)):duplicates.append(i)
    fs=rr.findall('.//s:f',n);masters={f.get('si') for f in fs if f.get('t')=='shared' and f.text}
    for f in fs:
        if f.get('t')=='shared' and f.get('si') not in masters:orphan_shared.append(i)
    for c in cs:
        if c.get('t')=='e':errors.append([i,c.get('r'),val(c)])
check('Sin celdas duplicadas ni fórmulas compartidas huérfanas',not duplicates and not orphan_shared)
new_errors=[e for e in errors if e[0]>=56]
check('Sin errores de fórmula en nuevas hojas',not new_errors,new_errors)
rels_missing=[]
for name in z.namelist():
    if not name.endswith('.rels'):continue
    folder=posixpath.dirname(posixpath.dirname(name))
    for rel in E.fromstring(z.read(name)):
        if rel.get('TargetMode')=='External':continue
        t=rel.get('Target');target=t.lstrip('/') if t.startswith('/') else posixpath.normpath(posixpath.join(folder,t))
        if target not in z.namelist():rels_missing.append([name,target])
check('Relaciones internas con destino existente',not rels_missing,rels_missing)
tableids=[];tablenames=[]
for name in z.namelist():
    if re.fullmatch(r'xl/tables/table\d+.xml',name):
        t=E.fromstring(z.read(name));tableids.append(t.get('id'));tablenames.append(t.get('displayName'));cols=t.find(q('tableColumns'))
        assert len(cols)==int(cols.get('count'))
check('IDs y nombres de tablas únicos',len(tableids)==len(set(tableids)) and len(tablenames)==len(set(tablenames)))
for i in [5,6,13,14,15,16,17,18]:
    orig_dv=root(orig,i).find(q('dataValidations'));new_dv=root(z,i).find(q('dataValidations'))
    check(f'Validaciones/filtros de maqueta hoja {i}',orig_dv is None or (new_dv is not None and len(orig_dv)==len(new_dv)))
protected=load(OUT.parent/'fase1/CADENA_Y_FUENTES.json')['preservacion']
check('13 fuentes protegidas sin modificaciones',all(sha(Path(p))==h for p,h in protected.items()))
check('HEAD y cambio previo preservados',git('rev-parse','HEAD')=='8e2fb85bb8703758d6878681c9e2a29016e60c63' and git('status','--short','--untracked-files=no')=='M PROYECTO_IPSS.json')
check('Sin staging',not git('diff','--cached','--name-only'))
check('Libro individual fuera de Git',subprocess.run(['git','-C',str(dst.parent),'rev-parse','--show-toplevel'],capture_output=True).returncode!=0)
qa={'fecha':datetime.now(ZoneInfo('America/Santiago')).isoformat(),'clasificacion':'C','estado':'PASA_ESTRUCTURAL_CON_RECALCULO_INTEGRAL_PENDIENTE' if all(x['resultado']=='PASA' for x in checks) else 'FALLIDO','controles':checks,'total':len(checks),'errores_cache_existentes':errors,'suplemento':load(P/'QA_SUPLEMENTO.json'),'limites':['Recálculo integral y apertura Excel nativo corresponden a fase5, no ejecutados.','Preservar cachés y fórmulas no certifica todas las funciones en Excel.','Fuentes materializadas permanecen identificadas; no se inventa un dato individual a partir de un conteo.']}
(OUT/'QA_FASE4.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n')
assert qa['estado']!='FALLIDO', 'Revisar QA, no entregar'
desktop=Path('/Users/alexi/Desktop')/dst.name
assert not desktop.exists()
shutil.copy2(dst,desktop);os.chmod(desktop,0o600);assert sha(desktop)==sha(dst)
(OUT/'COPIA_VERIFICADA.json').write_text(json.dumps({'ruta':str(desktop),'sha256':sha(desktop),'original_privado':str(dst),'mismo_hash':True},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'QA':qa['estado'],'controles':len(checks),'errores_cache':len(errors),'salida':str(desktop),'sha256':sha(dst)},ensure_ascii=False))
