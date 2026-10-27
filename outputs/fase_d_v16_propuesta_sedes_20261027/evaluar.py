from pathlib import Path
from collections import Counter,defaultdict
import sys,json,sqlite3,hashlib,csv,unicodedata
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R));from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento,sha256
O=Path(__file__).parent;old=DiccionarioSiesSeguimiento();rr=old.db.execute('select * from observaciones order by id').fetchall();targets=[r for r in rr if 24775<=r[0]<=25902];assert len(targets)==1128
mapping={'RE':'2','CO':'3'}; assert Counter(r[7] for r in targets)=={'RE':1055,'CO':73}
counts=Counter(tuple(r[1:9]) for r in rr); transformed=[]
for r in rr:
 a=list(r)
 if 24775<=r[0]<=25902:a[7]=mapping[a[7]]
 transformed.append(a)
counts2=Counter(tuple(r[1:9]) for r in transformed);collisions={k:v for k,v in counts2.items() if v>1 and v>counts.get(k,0)}
# Consulta en memoria: sin escritura en base privada ni construcción v16.
db=sqlite3.connect(':memory:');old.db.backup(db);db.executemany('update observaciones set sede=? where id=?',[(mapping[r[7]],r[0]) for r in targets]);service=DiccionarioSiesSeguimiento.__new__(DiccionarioSiesSeguimiento);service.db=db;service.edicion='SIMULACION_NO_ACTIVADA'
res=Counter()
for r in targets:
 x=json.loads(r[9]);code=x.get('codigo_interno_adoptado');
 if not code:continue
 args={'persona':r[1],'codcli':r[2],'plan':r[3],'anio':r[4],'periodo':r[5],'carrera':r[6],'sede':mapping[r[7]],'jornada':r[8]};a=old.consultar(**args);b=service.consultar(**args)
 res['aprobadas']+=1;res['no_localizadas_antes']+=a.get('motivo')=='CONTEXTO_NO_LOCALIZADO';res['mismo_codigo_despues']+=b.get('codigo_sies')==code;res['ambiguas_despues']+=b.get('motivo')=='CONTEXTO_MULTIPLE'
assert res['aprobadas']==86
six=json.loads((Path.home()/'.local/share/ipss/fase_d_v15_candidata_20261027/ADJUDICACIONES_PRIVADAS.json').read_text());assert len(six)==6
ids={r[0] for r in targets};six_in=sum(o['observacion_id'] in ids for o in six)
result={'filas':len(targets),'sede_umas':dict(Counter(r[7] for r in targets)),'colisiones_nuevas':len(collisions),'respuestas_86':dict(res),'seis_en_intervalo':six_in,'aclaracion':'Simulación en memoria; no altera v14 ni genera v16. Contenido y clave sede deben tratarse en conjunto; regla puntual para las seis requiere aprobación.','catalogo_sedes_sha256':sha256(R/'gobernanza_sede.tsv')}
(O/'RESULTADOS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');old.close();db.close();print(json.dumps(result,ensure_ascii=False,indent=2))
