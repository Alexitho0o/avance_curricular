"""Índice privado de actividad por expediente y período; no asigna vigencia ni códigos."""
import collections, hashlib, json, os, re, sqlite3
from pathlib import Path
import openpyxl

ROOT=Path(__file__).resolve().parents[2]
PRIVATE=Path('/Users/alexi/.local/share/ipss/v11_fase2_20261026')
BASES=Path('/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/IPSS_CONCILIACION_UMAS_SIES_BASES')
PROM=[BASES/'04_UMAS_PROMEDIOSDEALUMNOS'/f'PROMEDIOSDEALUMNOS_{x}.xlsx' for x in (7804,12166,3233)]
DA=BASES/'03_UMAS_DATOSDEALUMNOS/DATOSDEALUMNOS_12159.xlsx'
VISTA=Path('/Users/alexi/.local/share/ipss/trazabilidad_integral_fase3_20261025/VISTA_T1_T2_T3.json')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def clean(x):
 if x is None:return ''
 s=str(x).strip().upper();return '' if s in ('NONE','NULL','NAN') else s
def norm(n,d=None):
 s=clean(n).replace('.','').replace(' ','')
 if d is None:
  if '-' not in s:return None
  s,d=s.split('-',1)
 v=clean(d)
 if not re.fullmatch(r'\d+',s) or not re.fullmatch(r'[0-9K]',v):return None
 return str(int(s))+'-'+v
def rows(path):
 w=openpyxl.load_workbook(path,read_only=True,data_only=True); s=w['Hoja1']; it=s.iter_rows(values_only=True); h={clean(v):i for i,v in enumerate(next(it))}
 for i,row in enumerate(it,2):yield s.title,i,h,row
 w.close()
def get(r,h,k):
 i=h.get(k);return clean(r[i]) if i is not None and i<len(r) else ''

if PRIVATE.exists():raise SystemExit('El directorio privado ya existe: preservar la ejecución anterior')
if ROOT.resolve() in PRIVATE.resolve().parents:raise SystemExit('Destino privado dentro del repositorio')
PRIVATE.mkdir(mode=0o700); os.chmod(PRIVATE,0o700)
vista=json.loads(VISTA.read_text()); pending=[x for x in vista if not x['contextos']]
assert len(pending)==3520
people={x['persona'] for x in pending if x.get('tipo_doc')=='R'}
by_person=collections.defaultdict(list)
for i,x in enumerate(pending):
 if x.get('tipo_doc')=='R':by_person[(x['persona'],str(x['anio_observado']),str(x['periodo_nativo']))].append(i)
mapping={}
review=json.loads((ROOT/'outputs/v11_fase1_cobertura_20261026/COBERTURA_COMBINACIONES.json').read_text())
for x in review['tabla']:
 if x['estado']=='FAMILIA_RESPALDADA':mapping[(x['carrera'],x['sede_UMAS'],x['jornada_UMAS'])]=(x['jornada_SIES'],x['familias_grupo'])
assert len(mapping)==32
for c,code in [('COTEIQ','I162S3C114J2'),('COTENS','I162S3C91J2'),('COTFAR','I162S3C115J2')]:mapping[(c,'CO','V')]=('2',[code])
owners=collections.defaultdict(set); sites=collections.defaultdict(set)
for sheet,i,h,r in rows(DA):
 cli=get(r,h,'CODCLI'); pe=norm(get(r,h,'RUT'));site=get(r,h,'SEDE')
 if cli and pe:owners[cli].add(pe);sites[(cli,pe)].add(site)
acc=collections.defaultdict(lambda:{'fuentes':collections.defaultdict(list),'familias':set(),'sede':set()})
activity=collections.defaultdict(set); invalid=collections.Counter(); total=collections.Counter()
for path in PROM:
 for sheet,i,h,r in rows(path):
  pe=norm(get(r,h,'RUT'),get(r,h,'DIG')); year=get(r,h,'ANO');period=get(r,h,'PERIODO')
  positions=by_person.get((pe,year,period))
  if not positions:continue
  for pos in positions:activity[pos].add(path.name)
  cli=get(r,h,'CODCLI');career=get(r,h,'CODCARR');plan=get(r,h,'PLAN_DE_ESTUDIO');journey=get(r,h,'JORNADA')
  if not cli or not plan or not career or not journey:invalid['llave_incompleta']+=1;continue
  if owners.get(cli) and owners[cli]!={pe}:invalid['codcli_identidad_ambigua']+=1;continue
  ss=sites.get((cli,pe),set()); candidates=[(site,mapping[(career,site,journey)]) for site in ss if (career,site,journey) in mapping]
  if len(candidates)!=1:invalid['sede_no_unica_o_fuera_alcance']+=1;continue
  site,(jour_sies,families)=candidates[0]
  if site=='CO' and year!='2026':invalid['co_fuera_de_2026']+=1;continue
  key=(pe,cli,plan,year,period,career,site,jour_sies)
  a=acc[key];a['familias'].update(families);a['sede'].add(site);a['fuentes'][path.name].append(i)
  total[path.name]+=1
contexts=[]; by_key={}
for key,a in acc.items():
 pe,cli,plan,year,period,career,site,jour=key
 obj={'persona':pe,'CODCLI':cli,'plan':plan,'anio':year,'periodo':period,'carrera':career,'sede_umas_actual':site,'jornada_sies':jour,'familias_candidatas':sorted(a['familias']),'fuentes_filas':dict(a['fuentes']),'estado':'E_PENDIENTE_CODIGO_Y_SEDE_HISTORICA','nota':'SEDE de DATOSDEALUMNOS es actual, no acredita sede histórica; actividad no acredita vigencia.'}
 by_key[key]=len(contexts);contexts.append(obj)
affected=set()
for key in acc:
 for pos in by_person.get((key[0],key[3],key[4]),[]):affected.add(pos)
doc={'posiciones':len(pending),'actividad_cualquier_fuente':len(activity),'contexto_candidato':len(affected),'sin_contexto_candidato':len(pending)-len(affected),'tipo_P_sin_cruce':sum(x.get('tipo_doc')!='R' for x in pending),'contextos_unicos':len(contexts),'personas_contexto_candidato':len({k[0] for k in acc}),'filas_por_fuente':dict(total),'advertencias_filas':dict(invalid),'fuentes_sha256':{p.name:sha(p) for p in PROM+[DA]},'vista_sha256':sha(VISTA),'familias_32_y_3':'candidatas aprobadas, no atribución individual','nota':'Las posiciones pueden tener múltiples contextos; conteos no son retención.'}
(PRIVATE/'CONTEXTOS_CANDIDATOS.json').write_text(json.dumps(contexts,ensure_ascii=False));os.chmod(PRIVATE/'CONTEXTOS_CANDIDATOS.json',0o600)
(PRIVATE/'POSICIONES_CON_CONTEXTO_INDICES.json').write_text(json.dumps(sorted(affected)));os.chmod(PRIVATE/'POSICIONES_CON_CONTEXTO_INDICES.json',0o600)
out=ROOT/'outputs/v11_fase2_20261026/RESULTADOS_INDICE.json';out.write_text(json.dumps(doc,ensure_ascii=False,indent=2));print(json.dumps(doc,ensure_ascii=False))
