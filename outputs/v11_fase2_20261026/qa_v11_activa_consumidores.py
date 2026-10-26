"""Contrasta los tres consumidores con el puntero activo, sin divulgar identidades."""
import json,os,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];PRIVATE=Path('/Users/alexi/.local/share/ipss/v11_fase2_20261026');sys.path.insert(0,str(ROOT))
from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento,sha256
s=DiccionarioSiesSeguimiento();assert s.edicion=='v11_20261026_86_y_ambiguedad'
query='SELECT persona,codcli,plan,anio,periodo,carrera,sede,jornada FROM observaciones WHERE payload LIKE ? LIMIT 1'
co=s.db.execute(query,('%CO_V1_T1_PLAN_JORNADA_73_APROBADO%',)).fetchone();r13=s.db.execute(query,('%MU2026_CAMBIO_JORNADA_13_2025_APROBADO%',)).fetchone();amb=s.db.execute(query,('%ALTERNATIVA_JORNADA_AMBIGUA_SIN_ADJUDICAR%',)).fetchone();assert co and r13 and amb
cols=('persona','codcli','plan','anio','periodo','carrera','sede','jornada');req=[{'metodo':'consultar','entrada':dict(zip(cols,r))} for r in (co,r13,amb)];req.append({'metodo':'consultar','entrada':dict(zip(cols[:5],amb[:5]))});s.close()
scripts=['scripts/consultar_diccionario_sies_seguimiento.py','scripts/retencion_intermedia_t2_t3/consultar_codigos_sies.py','procesos/caracterizacion/scripts/consultar_diccionario_sies_seguimiento.py'];results=[]
with tempfile.TemporaryDirectory(prefix='qa_v11_activa_',dir=PRIVATE) as td:
 os.chmod(td,0o700)
 for i,script in enumerate(scripts):
  path=Path(td)/f'resultado_{i}.json';p=subprocess.run([sys.executable,str(ROOT/script),'--salida-privada',str(path)],input=json.dumps(req),text=True,capture_output=True)
  if p.returncode:raise RuntimeError('Consumidor falló: '+script+'; '+p.stderr.splitlines()[-1])
  results.append(json.loads(path.read_text()))
assert results[0]==results[1]==results[2]
print(json.dumps({'edicion':'v11_20261026_86_y_ambiguedad','consumidores':len(scripts),'consultas_por_consumidor':len(req),'respuestas_coinciden':True,'puntero_sha256':sha256(ROOT/'data/diccionario_sies_seguimiento/activo.json')},ensure_ascii=False))
