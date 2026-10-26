"""Diagnóstico aislado de granos y cobertura; no ejecuta el método original que sobrescribe resultados."""
import json,csv,re,hashlib,shutil
from pathlib import Path
from collections import defaultdict,Counter
import openpyxl
R=Path.cwd();B=R/'data/reglas_negocio/20261022_puente_versiones';O=B/'plan_reduccion_v1';A=B/'validacion_local_v1'
def read(p):return list(csv.DictReader(open(p,encoding='utf-8-sig')))
def val(x):return '' if x is None else str(int(x)) if isinstance(x,float) and x.is_integer() else str(x).strip().upper()
def exact(a,b):
 a=val(a).replace('.','').replace(' ','');b=val(b).replace(' ','')
 return str(int(a))+'-'+b if a.isdigit() and re.fullmatch('[0-9K]',b) else None
def legacy(a,b):
 s=re.sub(r'\D','',str(a));return s+'-'+str(b).strip().upper() if s else ''
def xl(p):
 w=openpyxl.load_workbook(p,read_only=True,data_only=True);it=iter(w.active.values);h=next(it)
 for r in it:yield dict(zip(h,r))
 w.close()
old=read(B/'DICCIONARIO_VERSIONES_UMAS_SIES_PROPUESTO_20261022.csv');candidates=defaultdict(set)
for r in read(B/'PUENTE_VERSIONES_PLAN_UMAS_SIES_20261022.csv'):candidates[(r['codcarpr_interno'],r['sede'],r['jornada_catalogo'])].add(r['codigo_unico_sies_candidato'])
mu=R/'outputs/base_retencion_matricula_unificada_2022_2026/20260901_142342/BASE_RETENCION_MATRICULA_UNIFICADA_INFORMADA_SIES_2022_2026_20260901_142342.xlsx';pro=Path('/Users/alexi/Downloads/PROMEDIOSDEALUMNOS_12166.xlsx')
mi=defaultdict(set);my=defaultdict(set);ml=defaultdict(set);normdiff=0
for r in xl(mu):
 code='I162S%sC%sJ%sV%s'%tuple(val(r[k]) for k in ['COD_SED','COD_CAR','JOR','VERSION']);k=exact(r['N_DOC'],r['DV']);lk=legacy(r['N_DOC'],r['DV']);ml[lk].add(code)
 if val(r['TIPO_DOC'])=='R' and k:mi[k].add(code);my[(k,val(r['ANIO_INFORMADO']))].add(code)
bycar=defaultdict(set);byold=defaultdict(set)
for r in xl(pro):
 k=exact(r['RUT'],r['DIG']);lk=legacy(r['RUT'],r['DIG']);normdiff+=k!=lk
 if k:bycar[val(r['CODCARR'])].add((k,val(r['PLAN_DE_ESTUDIO']),val(r['ANO']),val(r['PERIODO'])))
 byold[val(r['CODCARR'])].add((lk,val(r['PLAN_DE_ESTUDIO'])))
groups=json.load(open(R/'data/versiones_por_cohorte/20261016/grupos_existentes.json'));gm={(g['codcarpr'],g['sede'],g['jornada']):g for g in groups};jmap={'1':'D','2':'V','4':'O'}
out=[];reproduced=0;globalpersons=set();globalmatched=set();globalunique=set()
for r in old:
 d=(r['codcarpr_interno'],r['sede'],r['jornada_catalogo']);cs=candidates[d];oldc=Counter(code for k,p in byold[d[0]] for code in ml[k]&cs)
 olddict={v.rsplit(':',1)[0]:int(v.rsplit(':',1)[1]) for v in r['distribucion_versiones'].split(';') if v};reproduced+=dict(oldc)==olddict
 pairs=defaultdict(set);uniq=defaultdict(set);temporal=defaultdict(set)
 for k,p,y,t in bycar[d[0]]:
  globalpersons.add(k)
  for code in mi[k]&cs:pairs[code].add((k,p));uniq[code].add(k)
  for code in my[(k,y)]&cs:temporal[(y,p,code)].add(k)
  matched=my[(k,y)]&cs
  if matched:globalmatched.add(k)
  if len(matched)==1:globalunique.add(k)
 g=gm.get((d[0],'RE' if d[1]=='2' else d[1],jmap.get(d[2],d[2])),{})
 out.append({'dimension':list(d),'estado_anterior':r['estado'],'original_reproducido':dict(oldc),'personas_plan_codigo_exacto':{c:len(s) for c,s in pairs.items()},'personas_codigo_exacto':{c:len(s) for c,s in uniq.items()},'filas_temporales':[{'ano':y,'plan':p,'codigo':c,'personas':len(s)} for (y,p,c),s in sorted(temporal.items())],'perfil_existente':g.get('perfiles_duracion_tipo',[]),'fuente_perfil':g.get('fuente_perfil','GRUPO_NO_LOCALIZADO'),'clasificacion':'C/E'})
result={'dimensiones':len(out),'metodo_original_reproduce':reproduced,'normalizacion_distinta_PROMEDIOS_filas':normdiff,'diferencias_causa':[{k:v for k,v in x.items() if k!='filas_temporales'} for x in out if x['dimension'] in [['IECIRE','2','4'],['IECIREOL','2','4']]],'personas_universo_carreras_63':len(globalpersons),'personas_con_algun_match_candidato_mismo_ano':len(globalmatched),'advertencia_cobertura_persona':'Personas con al menos un match en algún contexto; no acredita todos sus planes, carreras o años. Universo carreras de 63 dimensiones; no es toda MU.','perfiles_univocos_39':sum(x['estado_anterior'].startswith('PROPUESTA') and len(x['perfil_existente'])==1 for x in out),'detalle':out}
(O/'DIAGNOSTICO_GRANOS_Y_TEMPORALIDAD.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
# Respaldo del código original únicamente, sin ejecutarlo ni copiar identificadores.
shutil.copyfile('/tmp/formalize_majority.py',O/'metodo_original_referencia.py')
files=[Path('/tmp/formalize_majority.py'),A/'validar.py',pro,mu,R/'data/versiones_por_cohorte/20261016/grupos_existentes.json']
(O/'FUENTES_DIAGNOSTICO.json').write_text(json.dumps([{'ruta':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files],ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in result.items() if k!='detalle'},ensure_ascii=False))
print('11 pendientes:',json.dumps([{'dimension':x['dimension'],'perfil':x['perfil_existente'],'fuente':x['fuente_perfil'],'contextos_mismo_ano':len(x['filas_temporales'])} for x in out if x['estado_anterior']=='PENDIENTE_MULTIPLE_O_BAJA_COBERTURA'],ensure_ascii=False))
