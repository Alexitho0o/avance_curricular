"""Audita excepciones v11 por contexto; exporta detalle solo en ruta privada."""
import collections, datetime, hashlib, json, os, re, sqlite3
from pathlib import Path
import openpyxl
ROOT=Path(__file__).resolve().parents[2]; OUT=Path(__file__).parent
PRIVATE=Path('/Users/alexi/.local/share/ipss/v11_fase2_20261026')
BASES=Path('/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/IPSS_CONCILIACION_UMAS_SIES_BASES')
SRC=[BASES/'04_UMAS_PROMEDIOSDEALUMNOS'/f'PROMEDIOSDEALUMNOS_{n}.xlsx' for n in (7804,12166,3233)]
DA=BASES/'03_UMAS_DATOSDEALUMNOS/DATOSDEALUMNOS_12159.xlsx'
VISTA=Path('/Users/alexi/.local/share/ipss/trazabilidad_integral_fase3_20261025/VISTA_T1_T2_T3.json')
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def txt(v):
 if v is None:return ''
 s=str(v).strip().upper();return '' if s in ('NULL','NONE','NAN') else s
def norm(v,d=None):
 s=txt(v).replace('.','').replace(' ','')
 if d is None:
  if '-' not in s:return None
  s,d=s.split('-',1)
 d=txt(d);return str(int(s))+'-'+d if re.fullmatch(r'\d+',s) and re.fullmatch(r'[0-9K]',d) else None
def parts(v):
 m=re.fullmatch(r'I(\d+)S(\d+)C(\d+)J(\d+)V(\d+)',str(v or ''));return m.groups() if m else None
def rows(p):
 w=openpyxl.load_workbook(p,read_only=True,data_only=True);s=w['Hoja1'];it=s.iter_rows(values_only=True);h={txt(v):i for i,v in enumerate(next(it))}
 for n,row in enumerate(it,2):yield n,h,row
 w.close()
def get(row,h,k):
 n=h.get(k);return txt(row[n]) if n is not None and n<len(row) else ''
summary=json.loads((OUT/'QA_ATRIBUCION_T1_AGREGADO_V3.json').read_text()); descriptor=json.loads((OUT/'DESCRIPTOR_CANDIDATA.json').read_text()); active=json.loads((ROOT/'data/diccionario_sies_seguimiento/activo.json').read_text());old=json.loads((ROOT/active['descriptor']).read_text());v10=Path(old['base_privada']['ruta']);v11=Path(descriptor['base_privada']['ruta'])
for p in SRC+[DA]:
 if sha(p)!=summary['fuentes_sha256'][p.name]:raise ValueError('Cambió fuente '+p.name)
assert sha(VISTA)==summary['vista_sha256'] and sha(v10)==summary['base_v10_sha256'] and sha(v11)==summary['base_v11_sha256']
view=[x for x in json.loads(VISTA.read_text()) if not x['contextos']]; detail=json.loads((PRIVATE/'QA_ATRIBUCION_T1_DETALLE_V3.json').read_text());db=sqlite3.connect(v11.as_uri()+'?mode=ro',uri=True)
obs={x['observacion_id']:x for (p,) in db.execute('select payload from observaciones where id>24774') for x in [json.loads(p)]}; targets=[]
for d in detail:
 x=obs[d['observacion_id']];v=view[d['posicion_indice']];p=parts(v['codigo_origen_T1']);fam=v['codigo_origen_T1'].rsplit('V',1)[0]
 diff=fam not in x['familias_candidatas'];missing=d['estado_analisis_T1']=='SIN_CODCLI_T1_EN_FUENTES_REVISADAS';co=x['sede_dimension']=='CO'
 if diff or missing or co:targets.append({'pos':d['posicion_indice'],'persona':x['persona'],'codcli':x['CODCLI'],'carrera':x['carrera'],'plan':x['plan'],'anio':str(x['ano']),'periodo':str(x['periodo']),'sede_actual':x['sede_dimension'],'jornada':str(x['jornada_sies']),'codigo_T1':v['codigo_origen_T1'],'anio_T1':str(v['anio_origen']),'familias_destino':x['familias_candidatas'],'diferencia_familia':diff,'sin_t1':missing,'co':co,'tipo_cambio':'SIN_DIFERENCIA' if not diff else ('SEDE' if p and p[1]!=('3' if co else '2') else 'CARRERA' if p and all('C'+p[2]+'J' not in f for f in x['familias_candidatas']) else 'JORNADA'),'mu':[],'da':[],'promedios':collections.defaultdict(lambda:collections.Counter())})
assert len(targets)==100 and sum(x['diferencia_familia'] for x in targets)==25 and sum(x['sin_t1'] for x in targets)==8 and sum(x['co'] for x in targets)==73
by_person=collections.defaultdict(list);by_cli=collections.defaultdict(list)
for t in targets:by_person[t['persona']].append(t);by_cli[t['codcli']].append(t)
for pe,an,cod,p in db.execute('select persona,anio,codigo,payload from mu_anual'):
 for t in by_person.get(pe,[]):
  o=json.loads(p);t['mu'].append({'anio':str(an),'codigo':cod,'fuente':o.get('fuente'),'hoja':o.get('hoja'),'fila':o.get('fila'),'ingreso_actual':o.get('ingreso_actual'),'ingreso_origen':o.get('ingreso_origen')})
db.close()
for n,h,r in rows(DA):
 cli=get(r,h,'CODCLI'); pe=norm(get(r,h,'RUT'))
 for t in by_cli.get(cli,[]):
  if pe==t['persona']:t['da'].append({'fuente':DA.name,'hoja':'Hoja1','fila':n,'sede':get(r,h,'SEDE'),'carrera':get(r,h,'CODCARPR'),'jornada':get(r,h,'JORNADA'),'ano_ingreso':get(r,h,'ANOINGRESO'),'periodo_ingreso':get(r,h,'PERIODOINGRESO'),'ano_matricula':get(r,h,'ANOMATRICULA'),'periodo_matricula':get(r,h,'PERIODOMATRICULA'),'fecha_matricula':get(r,h,'FECHAMATRICULA')})
for path in SRC:
 for n,h,r in rows(path):
  cli=get(r,h,'CODCLI'); tt=by_cli.get(cli)
  if not tt:continue
  pe=norm(get(r,h,'RUT'),get(r,h,'DIG'));an=get(r,h,'ANO');per=get(r,h,'PERIODO');pl=get(r,h,'PLAN_DE_ESTUDIO');ca=get(r,h,'CODCARR');jo=get(r,h,'JORNADA')
  for t in tt:
   if pe==t['persona'] and an in {t['anio_T1'],t['anio']}:
    k='|'.join([path.name,an,per,pl,ca,jo]);t['promedios'][k]['filas']+=1
    if 'primera_fila' not in t['promedios'][k]:t['promedios'][k]['primera_fila']=n
for t in targets:t['promedios']=dict(t['promedios'])
def classification(t):
 codes={m['codigo'] for m in t['mu'] if m['anio']==t['anio_T1']}; matching={c for c in codes if c.rsplit('V',1)[0] in t['familias_destino']}; alternate=codes-{t['codigo_T1']}
 if not codes:return 'SIN_MU_ANUAL_ORIGEN'
 if matching and alternate:return 'MU_PERSONA_TIENE_DESTINO_Y_OTRO_CODIGO'
 if matching:return 'MU_PERSONA_TIENE_FAMILIA_DESTINO'
 return 'MU_PERSONA_NO_TIENE_FAMILIA_DESTINO_EN_ANIO_ORIGEN'
def destino_alguna_mu(t):
 return any(m['codigo'].rsplit('V',1)[0] in t['familias_destino'] for m in t['mu'])
def destino_mu_siguiente(t):
 return any(m['anio'].isdigit() and int(m['anio'])>int(t['anio_T1']) and m['codigo'].rsplit('V',1)[0] in t['familias_destino'] for m in t['mu'])
for t in targets:t['clasificacion_mu_persona']=classification(t)
report={'fecha_hora':datetime.datetime.now().astimezone().isoformat(),'estado':'REVISADO_CON_PENDIENTES','contextos_unicos_union':len(targets),'grupos_superpuestos':dict(collections.Counter('diferencia='+str(t['diferencia_familia'])+'|sin_t1='+str(t['sin_t1'])+'|co='+str(t['co']) for t in targets)),'diferencias_25':{'por_tipo':dict(collections.Counter(t['tipo_cambio'] for t in targets if t['diferencia_familia'])),'por_carrera':dict(collections.Counter(t['carrera'] for t in targets if t['diferencia_familia'])),'mu_persona':dict(collections.Counter(t['clasificacion_mu_persona'] for t in targets if t['diferencia_familia'])),'familia_destino_en_mu_otro_ano_persona':sum(destino_alguna_mu(t) for t in targets if t['diferencia_familia']),'familia_destino_en_mu_posterior_persona':sum(destino_mu_siguiente(t) for t in targets if t['diferencia_familia']),'personas':len({t['persona'] for t in targets if t['diferencia_familia']})},'sin_coincidencia_8':{'por_carrera':dict(collections.Counter(t['carrera'] for t in targets if t['sin_t1'])),'por_tipo':dict(collections.Counter(t['tipo_cambio'] for t in targets if t['sin_t1'])),'origen_ano_ingreso_coincide_da':sum(any(d['ano_ingreso']==t['anio_T1'] for d in t['da']) for t in targets if t['sin_t1']),'mu_persona':dict(collections.Counter(t['clasificacion_mu_persona'] for t in targets if t['sin_t1'])),'personas':len({t['persona'] for t in targets if t['sin_t1']})},'sede_CO_73':{'por_carrera':dict(collections.Counter(t['carrera'] for t in targets if t['co'])),'mu_persona':dict(collections.Counter(t['clasificacion_mu_persona'] for t in targets if t['co'])),'da_misma_persona_codcli_CO':sum(any(d['sede']=='CO' for d in t['da']) for t in targets if t['co']),'mu_codigos_distintos_en_mismo_ano':sum(len({m['codigo'] for m in t['mu'] if m['anio']==t['anio_T1']})>1 for t in targets if t['co']),'personas':len({t['persona'] for t in targets if t['co']}),'expedientes_persona_codcli':len({(t['persona'],t['codcli']) for t in targets if t['co']})},'fuentes_sha256':summary['fuentes_sha256'],'base_v10_sha256':sha(v10),'base_v11_sha256':sha(v11),'vista_sha256':sha(VISTA),'restricciones':'Datos de MU por persona y año no atribuyen automáticamente CODCLI, plan, sede histórica o fecha de cambio; estado DA es actual; sin modificación de código ni denominadores.'}
p=PRIVATE/'QA_EXCEPCIONES_T1_DETALLE_20261026_V2.json';fd=os.open(p,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
with os.fdopen(fd,'w') as f:json.dump(targets,f,ensure_ascii=False,default=str)
(OUT/'QA_EXCEPCIONES_T1_AGREGADO_20261026_V2.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False))
