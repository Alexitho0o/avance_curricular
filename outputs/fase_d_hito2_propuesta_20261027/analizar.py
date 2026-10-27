"""Contraste conservador: solo propuestas, identificadores fuera del repo."""
from pathlib import Path
from collections import defaultdict,Counter
import json,hashlib,unicodedata,os,subprocess,re,openpyxl,sys
from datetime import datetime
R=Path(__file__).resolve().parents[2];O=Path(__file__).parent;P=Path.home()/'.local/share/ipss/fase_d_hito2_20261027';os.umask(0o077);P.mkdir(parents=True,exist_ok=True)
assert subprocess.run(['git','-C',str(P.parent),'rev-parse','--show-toplevel'],capture_output=True).returncode!=0
h=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
active=R/'data/diccionario_sies_seguimiento/activo.json';head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip();assert head=='567795c77eed72d92f4ba6879960ecf9d56e9909';ah=h(active)
pin=Path.home()/'.local/share/ipss/fase_d_hito1b_20261027/DETALLE_PRIVADO.json';prev=json.loads((R/'outputs/fase_d_hito1b_20261027/MANIFEST.json').read_text());assert h(pin)==prev['detalle_privado']['sha256']; items=json.loads(pin.read_text());assert len(items)==736
focus=[x for x in items if x['clasificacion_mu']=='FAMILIA_PENDIENTE'];assert len(focus)==312
catalog=json.loads((R/'data/catalogo_fuentes/CATALOGO_FUENTES.json').read_text())['catalogo']; sources={}
for token,key in [('MATRICULA_UNIFICADA_INFORMADA','mu'),('IPSS_Procesamiento.xlsx','carga'),('PROMEDIOSDEALUMNOS_7804.xlsx','p7804'),('PROMEDIOSDEALUMNOS_12166.xlsx','p12166'),('PROMEDIOSDEALUMNOS_3233.xlsx','p3233')]:
 entries=[e for e in catalog if token in e['archivo']];assert len(entries)==1,(key,len(entries));e=entries[0];path=Path(unicodedata.normalize('NFD',e['ruta_consolidada']));assert h(path)==e['sha256'];sources[key]={'path':path,'sha256':e['sha256']}
def val(x):return '' if x is None else str(int(x)) if isinstance(x,float) and x.is_integer() else str(x).strip()
def identity(b,d):
 b=val(b).replace('.','').strip();d=val(d).upper().strip()
 if not re.fullmatch(r'\d+',b) or not re.fullmatch(r'[0-9K]',d):return None
 return str(int(b))+'-'+d
def code(s,c,j,v):
 if not all(val(x) and re.fullmatch(r'\d+(?:\.0)?',val(x)) for x in [s,c,j,v]):return None
 return 'I162S'+str(int(float(val(s))))+'C'+str(int(float(val(c))))+'J'+str(int(float(val(j))))+'V'+str(int(float(val(v))))
def fam(c):return re.sub(r'V\d+$','',c) if c else None
wanted={x['persona'] for x in items}; annual=defaultdict(list)
for key,sheet in [('mu','BASE_RETENCION_MU'),('carga','2025_carga')]:
 w=openpyxl.load_workbook(sources[key]['path'],read_only=True,data_only=True);s=w[sheet]; it=s.iter_rows(values_only=True);headers=next(it)
 if key=='mu':ix={str(x):i for i,x in enumerate(headers)}; positions=[ix[x] for x in ['N_DOC','DV','COD_SED','COD_CAR','JOR','VERSION','ANIO_ING_ACT','SEM_ING_ACT','ANIO_ING_ORI','ANIO_INFORMADO']]
 else:positions=[72,73,82,83,85,86,88,89,90,None]
 for rn,row in enumerate(it,2):
  get=lambda i:row[i] if i is not None and i<len(row) else None
  b,d,sed,car,jor,ver,ing,sem,ori,year=(get(i) for i in positions);pe=identity(b,d);year=2025 if key=='carga' else val(year)
  if pe not in wanted:continue
  cd=code(sed,car,jor,ver)
  if not cd:continue
  annual[(pe,str(year))].append({'codigo':cd,'ingreso':val(ing),'semestre':val(sem),'origen':val(ori),'fuente':str(sources[key]['path']),'sha256':sources[key]['sha256'],'hoja':sheet,'fila':rn})
 w.close()
activity=defaultdict(set); actrows=defaultdict(list)
for key in ['p7804','p12166','p3233']:
 w=openpyxl.load_workbook(sources[key]['path'],read_only=True,data_only=True);s=w['Hoja1'];it=s.iter_rows(values_only=True);hd={val(x).upper():i for i,x in enumerate(next(it))};req=['RUT','DIG','CODCLI','CODCARR','ANO','PERIODO'];assert all(k in hd for k in req),(key,hd.keys())
 for rn,row in enumerate(it,2):
  at=lambda n:row[hd[n]] if hd[n]<len(row) else None
  pe=identity(at('RUT'),at('DIG'))
  if pe not in wanted:continue
  cli,car,year,period=(val(at(x)).upper() for x in ['CODCLI','CODCARR','ANO','PERIODO']);k=(pe,car,year,period);activity[k].add(cli);actrows[(pe,cli,car,year,period)].append({'fuente':str(sources[key]['path']),'sha256':sources[key]['sha256'],'hoja':'Hoja1','fila':rn})
 w.close()
print('Fuentes MU y PROMEDIOS contrastadas, detalle solo privado',flush=True)
sys.path.insert(0,str(R))
from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento
svc=DiccionarioSiesSeguimiento()
results=[];resultsagg=defaultdict(lambda:{'contextos':0,'personas':set(),'expedientes':set()})
for x in items:
 pe=x['persona'];cli=x['codcli'];car=x['carrera'];year=str(x['anio']);period=str(x['periodo']);mu=annual.get((pe,year),[]);candidates=set(x['familias_pendientes_candidatas']);matching=[a for a in mu if fam(a['codigo']) in candidates];codes={a['codigo'] for a in matching};nonmatching={a['codigo'] for a in mu if fam(a['codigo']) not in candidates}
 # Candidate groups are keyed by career and UMAS jornada but need unambiguous sede mapping.
 groups=x['grupos_oferta_candidatos'];groupcodes={q for g in groups for q in g['codigos_base']};possible=codes & groupcodes
 sede_jornada=len(possible)==1 and len(codes)==1 and all(c in groupcodes for c in codes) and len({g['sede'] for g in groups if next(iter(possible),None) in g['codigos_base']})==1
 unique=len(codes)==1 and not nonmatching
 # Conservative: reported annual offer is observed, not official plan validity across full year.
 years=[a['ingreso'] for a in matching if re.fullmatch(r'\d{4}(?:\.0)?',a['ingreso'])];sem=[a['semestre'] for a in matching if a['semestre']];ori=[a['origen'] for a in matching if a['origen']]
 ingok=len(set(years))==1 and int(float(years[0]))<=int(year)
 offer=any(z['codigo'] in possible for z in x['oferta_anual_candidata']);acts=actrows.get((pe,cli,car,year,period),[]);other=activity.get((pe,car,year,period),set())-{cli,''};coverage_unknown=True
 cont=x['relacion_1b']=='CONTINUIDAD_TECNICO_INGENIERIA_MISMA_AREA'; prior=False
 if cont and ingok:
  plans=json.loads((R/'data/versiones_historicas_sies_umas/fase_4_20261015/catalogo_planes.json').read_text());pm={p['CODPESTUD']:p for p in plans}
  for e in x['expedientes_con_codigo']:
   for z in e['contextos']:
    names=pm.get(z['plan'],{}).get('nombres_carrera',[])
    if any('TECNICO' in n.upper() for n in names) and str(z['anio']).isdigit() and int(z['anio'])<int(float(years[0])):prior=True
 linked_rows=svc.db.execute('SELECT payload FROM observaciones WHERE persona=? AND codcli=? AND carrera=? AND plan=? AND anio=? AND periodo=?',(pe,cli,car,x['plan'],year,period)).fetchall()
 linked_payload=[json.loads(z[0]) for z in linked_rows]
 linked=any(v.get('codigo_documental_atribuible') in possible and v.get('codigo_documental_atribuible') for v in linked_payload)
 checks={'codigo_anual_unico_persona_y_candidato':unique,'sede_jornada_candidatas_sin_ancla_expediente':sede_jornada,'oferta_observada_anio':offer,'actividad_promedios':bool(acts),'ingreso_actual_le_anio':ingok,'otro_codcli_detectado':bool(other),'cobertura_promedios_completa_acreditada':False,'continuidad_tecnico_anterior':prior if cont else None,'vinculo_individual_codigo_plan_y_sede_acreditado':bool(linked)}
 failures=[]
 if x['clasificacion_mu']!='FAMILIA_PENDIENTE':failures.append('GRUPO_MU_EXCLUIDO_DEL_CRITERIO')
 if not unique:failures.append('CODIGO_MU_NO_UNICO_O_VARIAS_FAMILIAS')
 if not sede_jornada:failures.append('SEDE_JORNADA_NO_CONCORDANCIA_UNICA')
 if not offer:failures.append('OFERTA_ANUAL_NO_OBSERVADA')
 if not acts:failures.append('ACTIVIDAD_NO_ENCONTRADA')
 if not ingok:failures.append('INGRESO_A_CARRERA_NO_ACREDITADO_O_POSTERIOR')
 if other:failures.append('OTRO_CODCLI_MISMA_CARRERA_PERIODO_DETECTADO')
 if cont and not prior:failures.append('TECNICO_ANTERIOR_AL_INGRESO_NO_ACREDITADO')
 # These are independent evidence gaps and cannot be inferred from aggregate mapping.
 failures.append('COBERTURA_COMPLETA_PROMEDIOS_NO_ACREDITADA')
 if not linked:failures.append('CODIGO_MU_NO_VINCULADO_INEQUIVOCAMENTE_AL_PLAN_CODCLI')
 level='D1_PROPUESTA' if not failures else 'D2_PROPUESTA' if len(failures)==1 else 'E_PENDIENTE'
 res={'persona':pe,'codcli':cli,'carrera':car,'plan':x['plan'],'jornada':x['jornada'],'anio':year,'periodo':period,'relacion':x['relacion_1b'],'mu_clase_anterior':x['clasificacion_mu'],'nivel':level,'controles':checks,'motivos':failures,'mu_original_filas':mu,'ingreso_valores':years,'semestre_valores':sem,'origen_valores':ori,'actividad_fuentes':acts,'otros_codcli_observados':sorted(other)};results.append(res)
 k=(level,x['relacion_1b'],car,year);g=resultsagg[k];g['contextos']+=1;g['personas'].add(pe);g['expedientes'].add((pe,cli,car))
priv=P/'RESULTADOS_PRIVADOS.json';priv.write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n');os.chmod(priv,0o600)
rows=[{'nivel':k[0],'relacion':k[1],'carrera':k[2],'anio':k[3],'contextos':v['contextos'],'expedientes':len(v['expedientes']),'personas':len(v['personas'])} for k,v in sorted(resultsagg.items())]
fr=[r for r in results if r['mu_clase_anterior']=='FAMILIA_PENDIENTE'];assert len(fr)==312 and len(results)==736
summary={'contextos_total':len(results),'contextos_foco':len(fr),'con_ingreso_actual':sum(bool(r['ingreso_valores']) for r in fr),'con_sem_ing_act':sum(bool(r['semestre_valores']) for r in fr),'con_anio_ing_ori':sum(bool(r['origen_valores']) for r in fr),'ingreso_le_anio':sum(r['controles']['ingreso_actual_le_anio'] for r in fr),'niveles_foco':dict(Counter(r['nivel'] for r in fr)),'niveles_total':dict(Counter(r['nivel'] for r in results)),'motivos_foco':dict(Counter(m for r in fr for m in r['motivos'])),'tabla':rows}
(O/'RESULTADOS_AGREGADOS.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
lines=['# Fase D · Hito 2: propuesta sin activación','',f"[C] De 312 contextos, {summary['con_ingreso_actual']} tienen año de ingreso actual recuperado, {summary['con_sem_ing_act']} semestre y {summary['con_anio_ing_ori']} año de origen; {summary['ingreso_le_anio']} cumplen el control de año en los registros coincidentes.",'','[E] La cobertura total de PROMEDIOS no está certificada. Una coincidencia de familia y año en MU no vincula por sí misma el código al CODCLI ni al plan; oferta anual observada tampoco demuestra vigencia administrativa durante todo el año. No se crea edición ni se aplica propuesta. Las categorías D1/D2 son propuestas y no decisiones D aprobadas.','', '| Nivel | Relación | Carrera | Año | Contextos | Expedientes | Personas | Clase |','|---|---|---|---:|---:|---:|---:|---|']
for x in rows:lines.append('| '+' | '.join(str(x[k]) for k in ['nivel','relacion','carrera','anio','contextos','expedientes','personas'])+' | C/E |')
lines+=['','[C] Las personas y expedientes pueden aparecer en más de una fila. Los motivos no son mutuamente excluyentes. Las fuentes, filas y valores originales se encuentran en el detalle privado.']
(O/'INFORME.md').write_text('\n'.join(lines)+'\n')
svc.close()
assert h(active)==ah and subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()==head
manifest={'fecha':datetime.now().isoformat(),'head':head,'puntero_sha256':ah,'fuentes':{k:{'ruta':str(v['path']),'sha256':v['sha256']} for k,v in sources.items()},'detalle_hito1b_sha256':h(pin),'salidas':{x:h(O/x) for x in ['analizar.py','RESULTADOS_AGREGADOS.json','INFORME.md']},'detalle_privado':{'ruta':str(priv),'sha256':h(priv)},'qa':{'foco':len(fr),'total':len(results),'particion_tabla':sum(r['contextos'] for r in rows)==736,'no_modifica_bases_ni_denominadores':True,'puntero_y_head_intactos':True,'commit_push':False}}
(O/'MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in summary.items() if k!='tabla'},ensure_ascii=False,indent=2));print('MANIFEST',h(O/'MANIFEST.json'))
