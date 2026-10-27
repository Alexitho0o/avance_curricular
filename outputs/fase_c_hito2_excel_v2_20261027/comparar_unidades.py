from pathlib import Path
from collections import defaultdict,Counter
import json,sqlite3
r=Path(__file__).resolve().parents[2];p=r/'outputs/avance_historico_atribucion_20261027/auditar_atribucion.py';n={'__file__':str(p)};exec(compile(p.read_text().split("with (OUT/'PARTICION_POR_CODIGO.csv')")[0],str(p),'exec'),n);cache=n['cache'];assert len(cache)==5144
base=json.loads((r/'data/diccionario_sies_seguimiento/v12_20261027_644_internos/descriptor.json').read_text());db=sqlite3.connect(Path(base['base_privada']['ruta']).as_uri()+'?mode=ro',uri=True);last=db.execute('select max(id) from observaciones').fetchone()[0];db.close()
def coverage(before,dim):
 groups=defaultdict(list)
 for k,v in cache.items():
  pe,cli,plan,car,jor,year,per=k;entity=pe if dim=='personas' else (pe,cli,car) if dim=='expedientes' else k
  attributed=bool(v.get('codigo_sies'))
  if before and v.get('observacion_id',0)>last:attributed=False
  groups[entity].append(attributed)
 return dict(Counter('sin_pendientes' if all(values) else 'parcial' if any(values) else 'sin_codigo' for values in groups.values()))
a={d:coverage(True,d) for d in ['contextos','personas','expedientes']};b={d:coverage(False,d) for d in ['contextos','personas','expedientes']}
assert a['contextos'].get('sin_codigo')==1374 and b['contextos'].get('sin_codigo')==1292
result={'universo':'foco fijo H113','antes_v12':a,'despues_v14':b,'advertencia':'Las categorías de personas y expedientes se aplican solo a los contextos de este foco; no son cobertura institucional.'};(Path(__file__).parent/'COMPARACION_UNIDADES.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False,indent=2));n['service'].close()
