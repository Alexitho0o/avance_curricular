"""Diagnóstico agregado sin conservar identidades ni escribir las fuentes."""
import collections, datetime, hashlib, json, unicodedata
from pathlib import Path
import openpyxl
OUT=Path(__file__).parent
BASE=Path('/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/IPSS_CONCILIACION_UMAS_SIES_BASES/04_UMAS_PROMEDIOSDEALUMNOS')
FILES={'v11_12166':BASE/'PROMEDIOSDEALUMNOS_12166.xlsx','respaldo_ampliado':Path('/Users/alexi/Documents/GitHub/CARACTERIZACIÓN/.local/analisis_anual/2026/20261016_002933_892820/entrega/03_RESPALDOS/P3/01_ENTRADAS/PROMEDIOSDEALUMNOS_7804.xlsx')}
expected={'v11_12166':'aad1a71d166bdfb839049a5db534a21d050df1ed4e9251ad9982245896429015','respaldo_ampliado':'78491c4cd66978b16b1236fbc8fc9d01a9c99246c3ba4d33e20b7f32f2959a71'}
prior=json.loads((OUT/'RESULTADOS_AGREGADOS.json').read_text());assert all(not prior['fuentes'][x]['filas_por_periodo_2026'].get(p,0) for x in ('v11_7804','v11_3233') for p in ('2026-2','2026-3'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
for label in ('v11_7804','v11_3233'):
 assert sha(Path(prior['fuentes'][label]['ruta']))==prior['fuentes'][label]['sha256']
def clean(x):
 if x is None:return ''
 if isinstance(x,(int,float)) and x==int(x):return str(int(x))
 return str(x).strip().upper()
sets={}; counts={}; info={}
for label,path in FILES.items():
 assert sha(path)==expected[label]
 w=openpyxl.load_workbook(path,read_only=True,data_only=True);it=w['Hoja1'].iter_rows(values_only=True);h={clean(v):i for i,v in enumerate(next(it)) if v is not None}
 req=('ANO','PERIODO','RUT','DIG','CODCLI','CODCARR','PLAN_DE_ESTUDIO','CODRAMO','CODSECC','RAMOEQUIV','ASIGNATURA','JORNADA','ESTADO','NOTA_FINAL','CONVALIDADO','NIVEL','ESTADO_ACADEMICO')
 assert set(req).issubset(h)
 records=collections.defaultdict(lambda:collections.defaultdict(list)); ct=collections.Counter()
 for row in it:
  def get(k):return clean(row[h[k]]) if h[k]<len(row) else ''
  if get('ANO')!='2026' or get('PERIODO') not in ('2','3'):continue
  period='2026-'+get('PERIODO');key=(get('RUT').replace('.','').replace(' ','').lstrip('0') or '0',get('DIG'),get('CODCLI'),get('CODCARR'),get('PLAN_DE_ESTUDIO'),get('CODRAMO'),get('CODSECC'))
  if not all(key):ct[period+'_incompleta']+=1;continue
  attrs={k:get(k) for k in req if k not in ('ANO','PERIODO','RUT','DIG','CODCLI','CODCARR','PLAN_DE_ESTUDIO','CODRAMO','CODSECC')}
  records[period][key].append(attrs);ct[period+'_filas']+=1
 w.close();assert sha(path)==expected[label];sets[label]=records;counts[label]=ct;info[label]={'ruta':str(path),'hoja':'Hoja1','sha256':expected[label]}
def keysub(k,mask):return tuple(k[i] for i in mask)
def classified(exclusive,other):
 # Clases disjuntas y jerárquicas; coincidencia aproximada no prueba causa.
 masks=[('misma_asignatura_otra_seccion',(0,1,2,3,4,5)),('misma_asignatura_otro_plan',(0,1,2,3,5)),('misma_asignatura_otra_carrera',(0,1,2,5)),('mismo_expediente_otras_asignaturas',(0,1,2,3,4)),('mismo_codcli_otro_contexto',(0,1,2)),('misma_persona_otro_codcli',(0,1))]
 indexes={label:{keysub(k,m) for k in other} for label,m in masks};result=collections.Counter()
 for k in exclusive:
  found=next((label for label,mask in masks if keysub(k,mask) in indexes[label]),'sin_persona_en_otra_fuente')
  result[found]+=1
 return dict(result)
def equivalente(exclusive,own,other):
 def txt(x):return ''.join(c for c in unicodedata.normalize('NFKD',x) if not unicodedata.combining(c)).strip()
 indices={n:set() for n in ('RAMOEQUIV','ASIGNATURA')}
 for k,recs in other.items():
  for rec in recs:
   for n in indices:
    v=txt(rec[n]);
    if v:indices[n].add((k[:5],v))
 out=collections.Counter()
 for k in exclusive:
  recs=own[k];eq=any((k[:5],txt(rec['RAMOEQUIV'])) in indices['RAMOEQUIV'] for rec in recs if rec['RAMOEQUIV']);name=any((k[:5],txt(rec['ASIGNATURA'])) in indices['ASIGNATURA'] for rec in recs if rec['ASIGNATURA'])
  out['misma_equivalencia_y_nombre' if eq and name else 'solo_equivalencia' if eq else 'solo_nombre' if name else 'sin_coincidencia_equivalencia_o_nombre']+=1
 return dict(out)
def grade_class(v):
 if not v:return 'vacia'
 try:return 'cero' if float(v.replace(',','.'))==0 else 'distinta_de_cero'
 except ValueError:return 'no_numerica'
out={'clasificacion':'B datos; C comparaciones; E causa','fecha':datetime.datetime.now().astimezone().isoformat(),'fuentes':info,'metodo':'Llave RUT+DV+CODCLI+carrera+plan+CODRAMO+CODSECC por año/período. Llaves únicas, no filas ni personas. Clases de exclusivas disjuntas por coincidencia jerárquica; no demuestran causa.','periodos':{},'limites':'Las diferencias detectadas no demuestran corrección, traslado o fecha del cambio; no se infiere vigencia, deserción ni completitud.'}
fields=('RAMOEQUIV','ASIGNATURA','JORNADA','ESTADO','NOTA_FINAL','CONVALIDADO','NIVEL','ESTADO_ACADEMICO')
for period in ('2026-2','2026-3'):
 a=sets['respaldo_ampliado'][period];b=sets['v11_12166'][period];ak=set(a);bk=set(b);common=ak&bk;only_a=ak-bk;only_b=bk-ak
 priorc=prior['comparaciones'][period]['respaldo_anual_7804'];assert (len(common),len(only_a),len(only_b))==(priorc['llaves_comunes'],priorc['llaves_solo_fuente'],priorc['llaves_solo_v11'])
 differences=collections.Counter();ambiguous=0;grade_patterns=collections.Counter();state_patterns=collections.Counter();grade_people=set();state_people=set()
 for k in common:
  if len(a[k])!=1 or len(b[k])!=1:ambiguous+=1;continue
  for f in fields:
   if a[k][0][f]!=b[k][0][f]:differences[f]+=1
  if a[k][0]['NOTA_FINAL']!=b[k][0]['NOTA_FINAL']:grade_patterns[(grade_class(a[k][0]['NOTA_FINAL']),grade_class(b[k][0]['NOTA_FINAL']))]+=1;grade_people.add((k[0],k[1]))
  if a[k][0]['ESTADO_ACADEMICO']!=b[k][0]['ESTADO_ACADEMICO']:state_patterns[(a[k][0]['ESTADO_ACADEMICO'],b[k][0]['ESTADO_ACADEMICO'])]+=1;state_people.add((k[0],k[1]))
 person_a={(k[0],k[1]) for k in ak}; person_b={(k[0],k[1]) for k in bk};cli_a={k[2] for k in ak};cli_b={k[2] for k in bk}
 grp_a=collections.Counter(k[:6] for k in only_a);grp_b=collections.Counter(k[:6] for k in only_b);inter=set(grp_a)&set(grp_b)
 out['periodos'][period]={'filas_respaldo':counts['respaldo_ampliado'][period+'_filas'],'filas_v11':counts['v11_12166'][period+'_filas'],'llaves_comunes':len(common),'solo_respaldo':len(only_a),'solo_v11':len(only_b),'personas_afectadas_exclusivas_respaldo':len({k[:2] for k in only_a}),'personas_afectadas_exclusivas_v11':len({k[:2] for k in only_b}),'clasificacion_exclusivas_respaldo':classified(only_a,bk),'clasificacion_exclusivas_v11':classified(only_b,ak),'grupos_asignatura_con_seccion_diferente':len(inter),'grupos_uno_a_uno':sum(grp_a[g]==grp_b[g]==1 for g in inter),'equivalencia_exclusivas_respaldo':equivalente(only_a,a,b),'equivalencia_exclusivas_v11':equivalente(only_b,b,a),'llaves_comunes_con_multiplicidad':ambiguous,'diferencias_valores_llave_comun':dict(differences),'personas_diferencia_nota':len(grade_people),'personas_diferencia_estado':len(state_people),'patron_nota_respaldo_vs_v11':[{'respaldo':x,'v11':y,'llaves':n} for (x,y),n in grade_patterns.items()],'patron_estado_respaldo_vs_v11':[{'respaldo':x,'v11':y,'llaves':n} for (x,y),n in state_patterns.items()],'personas_distintas_respaldo':len(person_a),'personas_distintas_v11':len(person_b),'personas_solo_respaldo':len(person_a-person_b),'personas_solo_v11':len(person_b-person_a),'codcli_solo_respaldo':len(cli_a-cli_b),'codcli_solo_v11':len(cli_b-cli_a),'filas_llave_incompleta_respaldo':counts['respaldo_ampliado'][period+'_incompleta'],'filas_llave_incompleta_v11':counts['v11_12166'][period+'_incompleta']}
(OUT/'DIFERENCIAS_ASIGNATURA_AGREGADO.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False))
