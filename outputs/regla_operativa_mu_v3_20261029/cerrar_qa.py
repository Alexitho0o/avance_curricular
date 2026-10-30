#!/usr/bin/env python3
"""QA de entrega H002m: pruebas, preservación, privacidad y reproducción."""
import csv, hashlib, json, os, re, subprocess, sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
DATA=ROOT/'data/paridad_codigo_sies/regla_operativa_mu_v3'
PRIVATE=Path.home()/'.local/share/ipss/h002m_20261029'
PREFIXES=[str(p.relative_to(ROOT))+'/' for p in (DATA,OUT)]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
def main():
 initial=json.loads((PRIVATE/'ESTADO_INICIAL.json').read_text())
 changed=[p for p,h in initial['hashes'].items() if not (ROOT/p).is_file() or sha(ROOT/p)!=h]
 assert not changed,'Archivos protegidos cambiaron: '+str(changed)
 status=subprocess.check_output(['git','status','--short'],cwd=ROOT,text=True).splitlines()
 unrelated=[s for s in status if not any(s[3:].startswith(p) for p in PREFIXES)]
 assert unrelated==initial['status'],'Cambió el estado ajeno'
 suites=['outputs/regla_operativa_mu_v3_20261029/test_v3.py','outputs/regla_operativa_mu_v2_20261029/test_regla_v2.py','outputs/depuracion_codigo_mu2027_20261029/test_h002l.py']
 tests=[];env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
 for rel in suites:
  r=subprocess.run([sys.executable,rel],cwd=ROOT,env=env,capture_output=True,text=True)
  log=r.stdout+r.stderr;(PRIVATE/(Path(rel).stem+'_final.log')).write_text(log)
  assert r.returncode==0,'Prueba falla: '+rel
  count=int(re.search(r'Ran (\d+) tests?',log)[1]);tests.append({'ruta':rel,'sha256':sha(ROOT/rel),'pruebas':count,'estado':'PASS'})
 r=subprocess.run([sys.executable,str(OUT/'construir_v3.py'),'--check'],cwd=ROOT,env=env,capture_output=True,text=True)
 (PRIVATE/'REPRODUCCION_FINAL.log').write_text(r.stdout+r.stderr)
 assert r.returncode==0,'Reproducción falla; ver registro privado'
 sources=json.loads((OUT/'FUENTES.json').read_text());tokens=set()
 for s in sources:
  assert sha(s['ruta'])==s['sha256'],'Fuente alterada: '+s['id']
  if s['id'] in ('sies_individual','sies_individual_2026'):
   with Path(s['ruta']).open(encoding='utf-8-sig') as f:
    for row in csv.DictReader(f):tokens.add(row['mrun'])
  if s['id']=='enlaces_H002g':
   for row in json.loads(Path(s['ruta']).read_text()):
    if row['identidad']:tokens.update(str(v) for v in row['identidad'] if v is not None)
    if row['seleccion']:tokens.add(str(row['seleccion'][0]))
 tokens={x for x in tokens if re.fullmatch(r'\d{6,12}[Kk]?',x)}
 patterns={
  'documento':r'(?<![\w])(?:\d{1,2}\.\d{3}\.\d{3}|\d{7,8})-[0-9Kk](?![\w])',
  'correo':r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
  'telefono':r'(?<!\w)\+56[ -]?[2-9](?:[ -]?\d){8}(?!\d)',
  'expediente':r'(?<!\w)(?:19|20)\d{2}[1-5][A-Z]{2,12}\d{3,}(?!\w)',
  'credencial':r'\b(?:gh[pousr]_[A-Za-z0-9]{15,}|github_pat_[A-Za-z0-9_]{15,})\b'}
 files=sorted(p for folder in (DATA,OUT) for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name not in ('QA_FINAL.json','MANIFEST_ENTREGA.json'))
 findings=[]
 for p in files:
  assert p.suffix in ('.json','.csv','.md','.py'),'Formato no autorizado'
  raw=p.read_text();plain=re.sub(r'\b[a-fA-F0-9]{40,64}\b',' HASH ',raw)
  kinds=[k for k,pattern in patterns.items() if re.search(pattern,plain)]
  if set(re.findall(r'(?<![A-Za-z0-9])\d{6,12}[Kk]?(?![A-Za-z0-9])',plain))&tokens:kinds.append('token_individual_exacto')
  if kinds:findings.append({'archivo':str(p.relative_to(ROOT)),'tipos':kinds})
 assert not findings,'Revisar privacidad (sin valores): '+str(findings)
 assert all(sha(ROOT/p)==h for p,h in initial['hashes'].items())
 qa={'estado':'PASS','clase':'C','ejecucion':'2026-10-30','archivos_protegidos_intactos':len(initial['hashes']),'cambios_ajenos_intactos':len(unrelated),'pruebas':tests,'total_pruebas':sum(t['pruebas'] for t in tests),'reproduccion_por_hash':'IDENTICA','fuentes_hash_verificadas':len(sources),'privacidad':{'archivos_escaneados':len(files),'hallazgos':findings,'metodo':'Patrones documento/contacto/expediente/credencial + tokens exactos de fuentes sólo en memoria; salidas de esquema agregado sin campos nominales'},'limites':['Candidata; no cambia regla activa','Patrones SIES agregados no certifican errores individuales','Microdatos con matrícula no equivalen a oferta completa']}
 save(OUT/'QA_FINAL.json',qa)
 files.append(OUT/'QA_FINAL.json')
 save(OUT/'MANIFEST_ENTREGA.json',{'hito':'H002m','commit_base':initial['head'],'estado':'CANDIDATO_NO_ACTIVO','archivos':[{'ruta':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(files)]})
 print(json.dumps(qa,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
