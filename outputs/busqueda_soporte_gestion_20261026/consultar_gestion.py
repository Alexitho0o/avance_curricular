"""Exploración de reportes institucionales por cuerpo de RUT; solo conteos."""
import collections,hashlib,json,sqlite3,unicodedata
from pathlib import Path
import openpyxl
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
private=Path('/Users/alexi/.local/share/ipss/revision_21_ramos_4_expedientes_20261026/DETALLE_CUATRO_CASOS_V2.json')
source=Path('/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/IPSS_CONCILIACION_UMAS_SIES_BASES/06_INDICADORES_ACADEMICOS_VRA/GESTIONSGE_1703.xlsx')
db=Path('/Users/alexi/.local/share/ipss/v11_fase2_20261026/DICCIONARIO_SIES_CANDIDATO_V11_86_Y_AMBIGUEDAD.sqlite')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
cases=json.loads(private.read_text());persons={x['RUT'] for x in cases};assert len(persons)==4
codclis={c['CODCLI'] for x in cases for c in x['contextos_v11']}
plan_codes={'IINF20241','IECIREOL20211','TCRE20241','TTMRE20211'}
course_codes={x['ramo'] for x in json.loads((ROOT/'outputs/busqueda_respaldo_titulos_homologaciones_20261026/RESULTADO_AGREGADO.json').read_text())['ramos']}
con=sqlite3.connect(db.as_uri()+'?mode=ro',uri=True);assert sha(db)=='1dafb1486f3ebd080ad4435a3af80b65a1a7016ba47b51f30d91b9a050985141'
bodies={x.split('-')[0]:x for x in persons};ambiguous=set()
for body in bodies:
 matches={x[0] for x in con.execute('select distinct persona from observaciones where persona like ?', (body+'-%',))}
 if matches!={bodies[body]}:ambiguous.add(body)
con.close();digest=sha(source);w=openpyxl.load_workbook(source,read_only=True,data_only=True);it=w['Hoja1'].iter_rows(values_only=True);head=[str(x or '').strip().upper() for x in next(it)];ids=[i for i,x in enumerate(head) if x=='RUT_ALUMNO'];assert len(ids)==2
textcols=[head.index(x) for x in ('ASUNTO','OBSERVACION')];hits=collections.defaultdict(list);excluded=0
for row in it:
 vals=[str(row[i] or '').strip().replace('.','').replace(' ','') for i in ids]
 valid={str(int(v)) for v in vals if v.isdigit()}
 if not valid.intersection(bodies):continue
 if len(valid)!=1 or valid.intersection(ambiguous):excluded+=1;continue
 body=next(iter(valid));text=' '.join(str(row[i] or '') for i in textcols).upper();text=''.join(c for c in unicodedata.normalize('NFKD',text) if not unicodedata.combining(c))
 flags={name for name,patterns in {'plan':('PLAN DE ESTUDIO','CAMBIO DE PLAN','ACTUALIZACION DE PLAN'),'titulacion':('TITULACION','TITULADO','TITULO'),'homologacion':('HOMOLOG','CONVALID')}.items() if any(p in text for p in patterns)}
 if any(x in text for x in codclis):flags.add('codcli_explicito')
 if any(x in text for x in plan_codes):flags.add('codigo_plan_explicito')
 if any(x in text for x in course_codes):flags.add('codigo_ramo_explicito')
 if any(x in text for x in ('SOLICIT','CONSULT')):flags.add('solicitud_o_consulta')
 if any(x in text for x in ('APROBAD','RESOLUCION','DECRETO')):flags.add('palabra_decision_busqueda_limitada')
 hits[body].append(flags)
w.close();assert sha(source)==digest
result={'clasificacion':'B fuente; C búsqueda literal; E identidad y hechos','fuente':{'ruta':str(source),'hoja':'Hoja1','sha256':digest},'metodo':'Búsqueda por cuerpo de RUT en dos columnas RUT_ALUMNO, sin DV en fuente; se excluyen cuerpos ambiguos en v11 y columnas discordantes. Búsqueda literal en ASUNTO y OBSERVACION; no se exporta texto.','personas_buscadas':len(persons),'personas_con_registros':len(hits),'registros_coincidentes':sum(map(len,hits.values())),'personas_con_palabras_por_tema':{k:sum(any(k in flags for flags in rows) for rows in hits.values()) for k in ('plan','titulacion','homologacion')},'registros_con_patron_literal':{k:sum(k in flags for rows in hits.values() for flags in rows) for k in ('codcli_explicito','codigo_plan_explicito','codigo_ramo_explicito','solicitud_o_consulta','palabra_decision_busqueda_limitada')},'registros_excluidos_ambiguos':excluded,'limites':'El cuerpo de RUT no acredita DV; la búsqueda literal puede omitir sinónimos, archivos y eventos. Una mención no es documento de titulación ni acredita migración o equivalencia.'}
(OUT/'RESULTADO_AGREGADO.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:result[k] for k in ('personas_con_registros','registros_coincidentes','personas_con_palabras_por_tema','registros_excluidos_ambiguos')},ensure_ascii=False))
