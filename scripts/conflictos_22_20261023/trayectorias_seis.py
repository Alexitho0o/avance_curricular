"""Reproduce trayectorias anuales de los seis controles; no modifica fuentes."""
import sqlite3,json,collections
from pathlib import Path
E=json.load(open('/Users/alexi/.local/share/ipss/analisis_conflictos_22_20261023/ERRORES6_DETALLE.json'))
c=sqlite3.connect('file:/Users/alexi/.local/share/ipss/cierre_inf35_03_t3_20261023_154224/DICCIONARIO_SIES.sqlite?mode=ro',uri=True)
rs=[json.loads(x[0]) for x in c.execute('select payload from observaciones')]
out=[]
for e in E:
 rows=[r for r in rs if r['persona']==e['persona']]
 by=collections.defaultdict(lambda:{'codigos_doc':set(),'codigos_internos':set(),'periodos':set(),'estados':set(),'n':0})
 for r in rows:
  k=(r['ano'],r['carrera'],r['plan'],r['jornada_sies'],r['CODCLI']==e['CODCLI']);d=by[k];d['codigos_doc'].add(r['codigo_documental_atribuible']);d['codigos_internos'].add(r['codigo_interno_adoptado']);d['periodos'].add(r['periodo']);d['estados'].add(r['estado_interno']);d['n']+=1
 trajectory=[]
 for k,v in sorted(by.items()):trajectory.append(dict(zip(['anio','carrera','plan','jornada','mismo_codcli'],k),**{f:sorted(z) if isinstance(z,set) else z for f,z in v.items()}))
 out.append({'id':e['id'],'trayectoria':trajectory})
text=json.dumps(out,ensure_ascii=False,indent=2)
for e in E:assert e['persona'] not in text and e['CODCLI'] not in text
Path('/tmp/errores6_trayectorias_agregadas.json').write_text(text)
c.close()
print('OK: seis trayectorias agregadas, sin identificadores personales.')
