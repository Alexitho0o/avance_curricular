"""Prueba wrappers contra candidata en un entorno aislado y privado."""
import json, os, shutil, sqlite3, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PRIVATE=Path('/Users/alexi/.local/share/ipss/v11_fase2_20261026')
descriptor=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else ROOT/'outputs/v11_fase2_20261026/DESCRIPTOR_CANDIDATA.json'
d=json.loads(descriptor.read_text());base=Path(d['base_privada']['ruta'])
with tempfile.TemporaryDirectory(prefix='qa_',dir=PRIVATE) as tmp:
 scratch=Path(tmp);os.chmod(scratch,0o700);t=scratch/'repositorio_aislado';t.mkdir()
 files=list(d['componentes_sha256'])
 for f in files:
  dst=t/f;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/f,dst)
 (t/'descriptor.json').write_text(descriptor.read_text());(t/'activo.json').write_text(json.dumps({'descriptor':'descriptor.json','sha256':__import__('hashlib').sha256(descriptor.read_bytes()).hexdigest()}))
 (t/'PROYECTO_IPSS.json').write_text(json.dumps({'recursos_comunes':{'diccionario_sies_seguimiento':'activo.json'}}))
 db=sqlite3.connect(base.as_uri()+'?mode=ro',uri=True)
 rows=db.execute('SELECT persona,codcli,plan,anio,periodo,carrera,sede,jornada FROM observaciones WHERE id IN (SELECT min(id) FROM observaciones UNION SELECT max(id) FROM observaciones UNION SELECT min(id) FROM observaciones WHERE payload LIKE ? UNION SELECT min(id) FROM observaciones WHERE payload LIKE ?)',('%CO_V1_T1_PLAN_JORNADA_73_APROBADO%','%MU2026_CAMBIO_JORNADA_13_2025_APROBADO%')).fetchall()
 amb=db.execute('SELECT persona,codcli,plan,anio,periodo FROM observaciones WHERE payload LIKE ? LIMIT 1',('%ALTERNATIVA_JORNADA_AMBIGUA_SIN_ADJUDICAR%',)).fetchone();db.close()
 request=[{'metodo':'consultar','entrada':dict(zip(('persona','codcli','plan','anio','periodo','carrera','sede','jornada'),r))} for r in rows]
 if amb:request.append({'metodo':'consultar','entrada':dict(zip(('persona','codcli','plan','anio','periodo'),amb))})
 scripts=['scripts/consultar_diccionario_sies_seguimiento.py','scripts/retencion_intermedia_t2_t3/consultar_codigos_sies.py','procesos/caracterizacion/scripts/consultar_diccionario_sies_seguimiento.py']
 results=[]
 for i,s in enumerate(scripts):
  path=scratch/('respuesta_'+str(i)+'.json');run=subprocess.run([sys.executable,str(t/s),'--salida-privada',str(path)],input=json.dumps(request),text=True,capture_output=True)
  if run.returncode:raise RuntimeError('Fallo del consumidor '+s+': '+run.stderr.splitlines()[-1])
  results.append(json.loads(path.read_text()))
 assert results[0]==results[1]==results[2]
 print(json.dumps({'consumidores':3,'consultas_por_consumidor':len(request),'respuestas_coinciden':True,'candidata_edicion':d['edicion'],'prueba':'entorno aislado privado; incluye una consulta antigua y una nueva'}))
