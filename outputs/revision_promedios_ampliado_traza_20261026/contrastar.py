"""Comparación de 21 ramos y trazas por llave; sin salida individual."""
import collections,hashlib,json,re,unicodedata
from pathlib import Path
import openpyxl
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
target=ROOT/'outputs/busqueda_respaldo_titulos_homologaciones_20261026/RESULTADO_AGREGADO.json'
private=Path('/Users/alexi/.local/share/ipss/revision_21_ramos_4_expedientes_20261026/DETALLE_CUATRO_CASOS_V2.json')
sources={
 '7804_previo':(Path('/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/IPSS_CONCILIACION_UMAS_SIES_BASES/04_UMAS_PROMEDIOSDEALUMNOS/PROMEDIOSDEALUMNOS_7804.xlsx'),'83a0ba72b21d25dd0d151b75fb0182a1f55bbe3f5efba06d088c994067262fca'),
 '7804_ampliado':(Path('/Users/alexi/Documents/GitHub/CARACTERIZACIÓN/.local/analisis_anual/2026/20261016_002933_892820/entrega/03_RESPALDOS/P3/01_ENTRADAS/PROMEDIOSDEALUMNOS_7804.xlsx'),'78491c4cd66978b16b1236fbc8fc9d01a9c99246c3ba4d33e20b7f32f2959a71')}
targets={(x['carrera'],x['plan_revisado'],x['ramo']) for x in json.loads(target.read_text())['ramos']};assert len(targets)==21
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def s(v):
 if v is None:return ''
 if isinstance(v,(float,int)) and v==int(v):return str(int(v))
 return str(v).strip().upper()
sets={};metadata=[];counts=[]
for label,(p,expected) in sources.items():
 assert sha(p)==expected
 w=openpyxl.load_workbook(p,read_only=True,data_only=True);it=w['Hoja1'].iter_rows(values_only=True);h={s(v):i for i,v in enumerate(next(it)) if v is not None}
 fields=('RUT','DIG','CODCLI','CODCARR','PLAN_DE_ESTUDIO','ANO','PERIODO','CODRAMO','CODSECC','ESTADO','DESCRIPCION_ESTADO','CONVALIDADO','RAMOEQUIV');assert set(fields).issubset(h)
 entries=collections.defaultdict(list);n=0;bad=0
 for row in it:
  def v(k):return s(row[h[k]]) if h[k]<len(row) else ''
  career,plan,course=(v(k) for k in ('CODCARR','PLAN_DE_ESTUDIO','CODRAMO'))
  if (career,plan,course) not in targets:continue
  n+=1;body=v('RUT').replace('.','').replace(' ','');dv=v('DIG')
  if not body.isdigit() or not re.fullmatch('[0-9K]',dv) or not v('CODCLI') or not v('ANO') or not v('PERIODO'):bad+=1;continue
  key=(str(int(body)),dv,v('CODCLI'),career,plan,v('ANO'),v('PERIODO'),course,v('CODSECC'))
  entries[key].append(tuple(v(k) for k in ('ESTADO','DESCRIPCION_ESTADO','CONVALIDADO','RAMOEQUIV')))
 w.close();assert sha(p)==expected;sets[label]=entries
 st=collections.Counter((k[3],k[4],k[7],a[0],a[1]) for k,vals in entries.items() for a in vals)
 counts.extend({'fuente':label,'carrera':ca,'plan':pl,'ramo':co,'estado':e,'descripcion':desc,'filas':n} for (ca,pl,co,e,desc),n in sorted(st.items()))
 metadata.append({'etiqueta':label,'ruta':str(p),'hoja':'Hoja1','sha256':expected,'filas_objetivo':n,'llaves_distintas':len(entries),'llaves_incompletas':bad,'llaves_multiples':sum(len(x)>1 for x in entries.values()),'ramos_encontrados':len({(k[3],k[4],k[7]) for k in entries})})
a=sets['7804_previo'];b=sets['7804_ampliado'];common=set(a)&set(b);only_a=set(a)-set(b);only_b=set(b)-set(a)
different=sum(1 for k in common if sorted(a[k])!=sorted(b[k]));extra=collections.Counter((k[3],k[4],k[7]) for k in only_b)
attribute_changes=collections.Counter();patterns=collections.Counter()
for k in common:
 if len(a[k])!=1 or len(b[k])!=1:continue
 for name,old,new in zip(('ESTADO','DESCRIPCION_ESTADO','CONVALIDADO','RAMOEQUIV'),a[k][0],b[k][0]):
  if old!=new:
   attribute_changes[name]+=1
   patterns[(name,'NULL' if old=='NULL' else 'VACIO' if old=='' else 'OTRO','NULL' if new=='NULL' else 'VACIO' if new=='' else 'OTRO')]+=1
cases=json.loads(private.read_text());topics=collections.Counter();scores=collections.Counter();traces=0
for c in cases:
 for x in c['trazas_calculadas']:
  traces+=1;scores[s(x['puntaje'])]+=1;text=''.join(c for c in unicodedata.normalize('NFKD',s(x['razones'])) if not unicodedata.combining(c))
  for word in ('RUT','PLAN','CARRERA','FAMILIA','JORNADA','ANO','INGRESO','NOMBRE','EXACTO'):
   if word in text:topics[word]+=1
assert len(cases)==4
out={'clasificacion':'B fuentes; C cruce y traza; E regla de puntuación y homologación','fuentes':metadata,'llave':'RUT cuerpo+DV+CODCLI+carrera+plan+año+período+CODRAMO+CODSECC; datos personales solo en memoria','comparacion':{'llaves_comunes':len(common),'solo_previo':len(only_a),'solo_ampliado':len(only_b),'llaves_comunes_con_atributos_distintos':different,'cambios_por_campo':dict(attribute_changes),'patrones_valor_sin_contenido':[{'campo':field,'previo':old,'ampliado':new,'llaves':n} for (field,old,new),n in sorted(patterns.items())],'ramos_con_llaves_extra_ampliado':len(extra),'detalle_llaves_extra':[{'carrera':ca,'plan':pl,'ramo':co,'llaves':n} for (ca,pl,co),n in sorted(extra.items())]},'estados_por_fuente':counts,'traza':{'personas':4,'filas_traza':traces,'puntajes':dict(scores),'temas_literales':dict(topics),'advertencia':'Los temas muestran términos de TRACE_REASONS, no la fórmula o su peso. La traza elige candidato, no acredita plan formal ni aceptación.'},'limitaciones':'No sumar extracciones, no inferir vigencia o aprobación de malla. Estado de asignatura no reemplaza resolución. No se modifica base o denominadores.'}
(OUT/'RESULTADO_AGREGADO.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'fuentes':metadata,'comparacion':out['comparacion'],'traza':out['traza']},ensure_ascii=False))
