"""QA y lista exacta H010/H010b; no publica ni abre Excel."""
import argparse,ast,json,re,sqlite3,subprocess,sys,os
from pathlib import Path
from construir import sha,dump

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--privado',type=Path,required=True);a=ap.parse_args();R=a.repo.resolve();P=a.privado.resolve();O=R/'outputs/regla_t1_h010_20261030';load=lambda p:json.loads(Path(p).read_text());g=lambda *x:subprocess.check_output(['git','-C',str(R),*x],text=True).strip()
 init=load(P/'ESTADO_INICIAL.json');baseline=load(P/'MAPA_H010_ANTES.json');now=load(R/'docs/MAPA_RESULTADOS_GOBERNADOS.json');before=load(P/'ASIGNACIONES_PRIVADAS.json');after=load(P/'ASIGNACIONES_H010B_PRIVADAS.json');q=load(O/'QA_RESOLUCION_H010B.json')
 env=os.environ|{'PYTHONDONTWRITEBYTECODE':'1'};tests=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(O),'-p','test_*.py'],env=env,capture_output=True,text=True);assert tests.returncode==0,tests.stderr
 repro=load(P/'HASHES_H010B_REPRO_ANTES.json');repro_ok={str(Path(p).name):sha(p)==h for p,h in repro.items()};assert all(repro_ok.values()),repro_ok
 dump(O/'REPRODUCCION_H010B.json',{'estado':'PASS','archivos':len(repro),'hashes_identicos':repro_ok,'hashes':repro,'metodo':'Dos ejecuciones desde H010 congelado; no reclasifica asignaciones anteriores.'})
 oldhash=load(P/'HASHES_REPRODUCCION_ANTES.json');original_ok=all(sha(p)==h for p,h in oldhash.items() if Path(p).name!='descriptor.json')
 # Mantener los cierres originales como evidencia histórica, no sustituir por un PASS nuevo.
 assert sha(O/'DESCRIPTOR_H010_ANTES.json')==next(h for p,h in oldhash.items() if Path(p).name=='descriptor.json')
 active=load(R/'data/diccionario_sies_seguimiento/activo.json');desc=load(R/active['descriptor']);base=Path(desc['base_privada']['ruta']);db=sqlite3.connect(base.as_uri()+'?mode=ro',uri=True);known={str(v) for row in db.execute('select persona,codcli from observaciones') for v in row if v is not None};known|={v.split('-')[0] for v in known if '-'in v};db.close()
 patterns=[re.compile(r'(?<!\w)(?:'+'|'.join(re.escape(v) for v in sorted(known) if len(v)>=6)+r')(?!\w)'),re.compile(r'(?<!\w)\d{7,8}-[0-9Kk](?!\w)'),re.compile(r'\b\d{1,2}\.\d{3}\.\d{3}-[0-9Kk]\b'),re.compile(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}'),re.compile(r'(?<!\w)(?:\+56\s*[29]\s*\d{4}\s*\d{4}|[29]\d{8})(?!\w)'),re.compile(r'(?i)"(?:mrun|rut|CODCLI|N_DOC|nombre_alumno|telefono|correo)"\s*:\s*"?\d+')]
 initial_paths=load(O/'LISTA_PUBLICACION_H010_ANTES.json')['rutas'];paths=set(initial_paths);paths.update(str(f.relative_to(R)) for f in O.iterdir() if f.is_file());paths.update('outputs/regla_t1_h010_20261030/'+n for n in ['QA_H010B.json','REPRODUCCION_H010B.json']);paths=sorted(paths)
 allowed_prefix='outputs/regla_t1_h010_20261030/';assert all(p in initial_paths or p.startswith(allowed_prefix) for p in paths)
 findings=[]
 def scan():
  for rp in paths:
   f=R/rp
   if not f.exists():continue
   assert f.suffix in {'.md','.json','.py'} and f.stat().st_size<20*1024*1024,rp
   s=f.read_text()
   if f.suffix=='.py':ast.parse(s)
   if f.suffix=='.json':json.loads(s)
   for ln,line in enumerate(s.splitlines(),1):
    for n,rx in enumerate(patterns):
     if rx.search(line):findings.append({'ruta':rp,'linea':ln,'patron':n})
 scan();assert not findings,findings
 source_ok=True
 for fn in ['FUENTES.json','FUENTES_H010B.json']:
  for f in load(O/fn)['fuentes']:
   if Path(f['ruta'])==R/'docs/MAPA_RESULTADOS_GOBERNADOS.json':continue
   source_ok &= sha(f['ruta'])==f['sha256']
 for f in load(O/'PERIODOS45_H010B.json')['fuentes']:
  p=Path(f['ruta']);p=p if p.is_absolute() else R/p;source_ok &= sha(p)==f['sha256']
 oldmap={r['id']:r for r in baseline['resultados']};newmap={r['id']:r for r in now['resultados']}
 sourcecodes_ok=all(re.fullmatch(r'I162S'+re.escape(z['sede'])+r'C\d+J'+re.escape(z['jornada'])+r'V\d+',z['codigo_candidato']) for b,z in zip(before,after) if b['nivel_asignacion']=='E' and z['nivel_asignacion']!='E')
 books={Path.home()/'Desktop/RETENCION_IPSS_SEGUIMIENTO_T1_T2_T3_20261030_V25.xlsx':'63b55351334616833a2e687fbeb36314a0cbb1538c10b6a891c99f94475adc0a',Path.home()/'Desktop/RETENCION_IPSS_SEGUIMIENTO_T1_T2_T3_20261030_V26.xlsx':'d7e68859cdba52a636e562a9cd287f8114afbc0fb97f0840dfc9284fb2a43a51'}
 checks={'19_pruebas':tests.returncode==0 and 'Ran 19 tests' in tests.stderr,'reproduccion_hash':all(repro_ok.values()),'H010_resultados_previos_intactos':original_ok,'asignaciones_previas_intactas':all(b==z for b,z in zip(before,after) if b['nivel_asignacion']!='E'),'4_5_intactos':all(b==z for b,z in zip(before,after) if b['periodo'] in ['4','5']),'resolucion_pass':q['estado']=='PASS' and all(q['controles'].values()),'nuevas_sede_jornada_codigo_coherentes':sourcecodes_ok,'fuentes_intactas':source_ok,'v20_hash_intacto':sha(base)==desc['base_privada']['sha256'],'activo_descriptor_intacto':sha(R/active['descriptor'])==active['sha256'],'R01_R28_intactos':all(oldmap[k]==newmap[k] for k in oldmap if k!='R29'),'R29_CANDIDATA':'CANDIDATA' in newmap['R29']['resultado_clave'],'HEAD_6505cae':g('rev-parse','HEAD')==init['head'],'stage_vacio':not g('diff','--cached','--name-only'),'25_ajenos_hash_intacto':all(sha(R/p)==h for p,h in init['ajenos'].items()),'25_ajenos_status_intacto':all(s in g('status','--porcelain').splitlines() for s in init['status_ajenos'].splitlines()),'V25_V26_hash_intacto':all(sha(p)==h for p,h in books.items()),'privacidad_sin_hallazgos':not findings,'ningun_xlsx_publicado':all(not p.endswith('.xlsx') for p in paths)}
 assert all(checks.values()),{k:v for k,v in checks.items() if not v}
 dump(O/'QA_H010B.json',{'estado':'PASS_CANDIDATA_CON_RESIDUALES_E','controles':checks,'pruebas':19,'tasas_delta_pp':{'R01_R04':0.0,'R19':0.0},'metodo_tasas':'Conservación por hash, no recálculo ni integración','hallazgos_privacidad':findings,'alcance_privacidad':'Patrones, cotejo con identificadores privados y revisión de esquemas agregados; ningún registro individual publicado. No certificación universal de cualquier dato personal.','sin_activar':True,'sin_abrir_Excel':True})
 dump(O/'LISTA_PUBLICACION.json',{'estado':'QA_PASS_AUTORIZADO_H010_H010B','rutas':paths,'mensaje':'H010 asigna código de contexto por primer T1 informado; H010b aplica D1–D3 y documenta períodos 4/5','excluye':'Libros, bases privadas, detalle nominal y 25 cambios ajenos','autoriza':'D Alexi 30-10-2026, prompt H010b'})
 dump(O/'MANIFEST.json',{'hito':'H010_H010B','base_commit':init['head'],'estado':'CANDIDATA_NO_ACTIVA','fuentes':['FUENTES.json','FUENTES_H010B.json','PERIODOS45_H010B.json'],'salidas':{p:{'sha256':sha(R/p),'bytes':(R/p).stat().st_size} for p in paths if p!=str((O/'MANIFEST.json').relative_to(R))},'sin_hash_propio':'Evita autorreferencia'})
 findings.clear();scan();assert not findings,findings
 print(json.dumps({'estado':'PASS','controles':len(checks),'pruebas':19,'rutas':len(paths),'identificadores':len(findings)},ensure_ascii=False))
if __name__=='__main__':main()
