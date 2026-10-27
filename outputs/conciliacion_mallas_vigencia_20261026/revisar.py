"""Revisa diferencias de ramos y contexto anual SIES; salida agregada únicamente."""
import collections, hashlib, json, sqlite3, unicodedata
from pathlib import Path
import openpyxl

ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
prior=ROOT/'outputs/revision_discrepancias_mallas_20261026/MALLAS_OBSERVADAS_TITULADO_CANDIDATA.json'
compare=ROOT/'outputs/revision_discrepancias_mallas_20261026/CONTRASTE_PLANES_AGREGADO.json'
data=json.loads(prior.read_text()); meta=json.loads(compare.read_text());catalog_path=Path(meta['fuentes']['listado']['ruta'])
db=Path('/Users/alexi/.local/share/ipss/v11_fase2_20261026/DICCIONARIO_SIES_CANDIDATO_V11_86_Y_AMBIGUEDAD.sqlite')
offer=ROOT/'data/diagnostico_vigencia_oferta/20261016/oferta_anual.json'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for x in iter(lambda:f.read(1024*1024),b''):h.update(x)
 return h.hexdigest()
assert sha(catalog_path)==meta['fuentes']['listado']['sha256']
assert sha(db)=='1dafb1486f3ebd080ad4435a3af80b65a1a7016ba47b51f30d91b9a050985141'
def norm(x):
 if x is None:return ''
 if isinstance(x,(float,int)) and x==int(x):return str(int(x))
 return str(x).strip().upper()
def text(x):return ''.join(c for c in unicodedata.normalize('NFKD',norm(x)) if not unicodedata.combining(c))
w=openpyxl.load_workbook(catalog_path,read_only=True,data_only=True);it=w['BBDD Bruta'].iter_rows(values_only=True);h={norm(v):i for i,v in enumerate(next(it)) if v is not None};assert {'CODCARR','CODPESTUD','CODRAMO','NOMBRE','NIVEL'}.issubset(h)
plans=collections.defaultdict(list)
for row in it:
 def g(k):return norm(row[h[k]])
 career,plan,code,name,level=(g(k) for k in ('CODCARR','CODPESTUD','CODRAMO','NOMBRE','NIVEL'))
 if career and plan and code:plans[(career,plan)].append({'codigo':code,'nombre':name,'nivel':level})
w.close();assert sha(catalog_path)==meta['fuentes']['listado']['sha256']
issues=[]
for p in data['planes']:
 k=(p['carrera_umas'],p['plan_de_estudio']);catalog=plans.get(k)
 if catalog is None:continue
 codes={x['codigo'] for x in catalog}
 for c in p['asignaturas']:
  if c['codramo'] in codes:continue
  equivalents=sorted(set(c['ramos_equivalentes_observados'])&codes)
  names={text(n) for n in c['nombres_observados'] if n}
  namesakes=sorted({x['codigo'] for x in catalog if text(x['nombre']) in names and text(x['nombre'])})
  other=sorted({a+'/'+b for (a,b),rows in plans.items() if (a,b)!=k and any(x['codigo']==c['codramo'] for x in rows)})
  issues.append({'carrera':k[0],'plan':k[1],'asignatura':c['codramo'],'nombre_observado':c['nombres_observados'],'nivel_observado':c['niveles_observados'],'equivalente_exacto_en_plan':equivalents,'mismo_nombre_en_plan':namesakes,'mismo_codigo_en_otros_planes':other,'estado':'E: coincidencia exploratoria; equivalencia curricular no acreditada'})
assert len(issues)==22
offer_rows=json.loads(offer.read_text());off=collections.defaultdict(list)
for r in offer_rows:off[r['codigo_unico']].append({'anio':r['anio'],'vigencia':r['vigencia']})
v11=collections.defaultdict(lambda:collections.Counter())
conn=sqlite3.connect(db.as_uri()+'?mode=ro',uri=True)
for career,plan,year,period,sede,jor,payload in conn.execute('select carrera,plan,anio,periodo,sede,jornada,payload from observaciones'):
 p=json.loads(payload);doc=p.get('codigo_documental_atribuible') or '';internal=p.get('codigo_interno_adoptado') or ''
 source='B/C documental' if doc else ('D interno' if internal else 'E pendiente')
 code=doc or internal or ''
 v11[(career,plan)][(str(year),str(period),str(sede),str(jor),source,code)]+=1
conn.close();assert sha(db)=='1dafb1486f3ebd080ad4435a3af80b65a1a7016ba47b51f30d91b9a050985141'
contexts=[]
for p in data['planes']:
 key=(p['carrera_umas'],p['plan_de_estudio']);groups=[]
 for (year,period,sede,jor,source,code),n in sorted(v11.get(key,{}).items()):
  matching=[v for v in off.get(code,[]) if str(v['anio'])==year]
  groups.append({'anio_observacion':year,'periodo_umas':period,'sede':sede,'jornada':jor,'codigo_sies':code or None,'tipo_vinculo':source,'observaciones_v11':n,'oferta_mismo_anio':matching,'limite':'La oferta no prueba vigencia histórica del plan UMAS ni aceptación individual SIES.'})
 contexts.append({'carrera':key[0],'plan':key[1],'contextos':groups,'estado_vigencia_plan':'E: fecha de inicio y término del plan no acreditadas por estos datos'})
out={'clasificacion':'B observación; C cruce; D interno existente; E pendientes','fuentes':{'mallas_observadas_sha256':sha(prior),'listado_planes_sha256':sha(catalog_path),'v11_sha256':sha(db),'oferta_anual_sha256':sha(offer)},'discrepancias':issues,'planes_contextos':contexts,'metodo':'Cruce carrera+plan; código/nombre/ramo equivalente como pistas. Códigos SIES se leen por contexto desde v11, separados documental/interno; oferta solo por código y año. Salida sin identidad.','limitaciones':'Mismo nombre o ramo equivalente no prueba equivalencia. Titulado observado es estado del extracto, no titulación formal. Ausencia en oferta no prueba cierre. No se modifica fuente o denominador.'}
(OUT/'REVISION_AGREGADA.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
stats={'asignaturas_discrepantes':len(issues),'con_ramo_equivalente_en_mismo_plan':sum(bool(x['equivalente_exacto_en_plan']) for x in issues),'con_mismo_nombre_en_mismo_plan':sum(bool(x['mismo_nombre_en_plan']) for x in issues),'con_codigo_en_otro_plan':sum(bool(x['mismo_codigo_en_otros_planes']) for x in issues),'planes_con_contextos_v11':sum(bool(x['contextos']) for x in contexts),'contextos_agregados':sum(len(x['contextos']) for x in contexts),'sin_datos_personales':True}
(OUT/'RESUMEN.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2)+'\n');print(json.dumps(stats,ensure_ascii=False))
