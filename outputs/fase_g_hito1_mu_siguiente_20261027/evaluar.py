"""Propuestas Fase F: compara evidencia sin modificar el diccionario."""
from pathlib import Path
from collections import defaultdict,Counter
from datetime import datetime
import json,os,re,subprocess,sys,unicodedata,hashlib,openpyxl
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R));from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento,sha256
O=Path(__file__).parent;P=Path.home()/'.local/share/ipss/fase_g_hito1_20261027';os.umask(0o077);P.mkdir(parents=True,exist_ok=True);assert subprocess.run(['git','-C',str(P.parent),'rev-parse','--show-toplevel'],capture_output=True).returncode!=0
active=R/'data/diccionario_sies_seguimiento/activo.json';activebytes=active.read_bytes();head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip();assert head=='190ca4c979c8cb38d672ac26832c330d1b883593';svc=DiccionarioSiesSeguimiento();assert svc.edicion=='v18_20261027_candidata_fase_f';beforebase=sha256(svc.descriptor['base_privada']['ruta'])
fm=R/'outputs/fase_f_hito1_clasificacion_20261027/MANIFEST.json';m=json.loads(fm.read_text());pin=Path(m['detalle_privado']['ruta']);assert sha256(pin)==m['detalle_privado']['sha256'];allitems=json.loads(pin.read_text());items=[x for x in allitems if x['mu']=='SIN_MU_PERSONA_ANIO_EN_INDICE_Y_RESPALDOS_REVISADOS'];assert len(items)==430
cat=json.loads((R/'data/catalogo_fuentes/CATALOGO_FUENTES.json').read_text())['catalogo'];sources={}
for token,key in [('MATRICULA_UNIFICADA_INFORMADA','mu'),('IPSS_Procesamiento.xlsx','carga'),('PROMEDIOSDEALUMNOS_7804.xlsx','p7804'),('PROMEDIOSDEALUMNOS_12166.xlsx','p12166'),('PROMEDIOSDEALUMNOS_3233.xlsx','p3233'),('DATOSDEALUMNOS_12159.xlsx','da12159'),('DATOSDEALUMNOS_11248.xlsx','da11248'),('Oferta_Academica_2010_al_2026_SIES_05_06_2026_WEB_E.xlsx','oferta')]:
 entries=[e for e in cat if token in e['archivo']];assert len(entries)==1,(key,len(entries));e=entries[0];p=Path(unicodedata.normalize('NFD',e['ruta_consolidada']));assert sha256(p)==e['sha256'];sources[key]={'ruta':str(p),'sha256':e['sha256']}
def val(x):return '' if x is None else str(int(x)) if isinstance(x,float) and x.is_integer() else str(x).strip().upper()
def identity(b,d):
 b=val(b).replace('.','').strip();d=val(d).upper().strip();return str(int(b))+'-'+d if re.fullmatch(r'\d+',b) and re.fullmatch(r'[0-9K]',d) else None
def rut(x):
 x=re.sub(r'[.\s]','',val(x));m=re.fullmatch(r'(\d+)-([0-9K])',x);return str(int(m[1]))+'-'+m[2] if m else None
def code(s,c,j,v):
 vv=[val(x) for x in (s,c,j,v)];return 'I162S'+str(int(float(vv[0])))+'C'+str(int(float(vv[1])))+'J'+str(int(float(vv[2])))+'V'+str(int(float(vv[3]))) if all(re.fullmatch(r'\d+(?:\.0)?',x) for x in vv) else None
def family(x):return re.sub(r'V\d+$','',x) if x else None
def flat(x):return re.sub(r'\s+',' ',''.join(c for c in unicodedata.normalize('NFKD',str(x).upper()) if not unicodedata.combining(c))).strip()
def area(x):return re.sub(r'^(?:CONTINUIDAD\s+)?(?:INGENIERIA|TECNICO)(?:\s+EN)?\s+','',flat(x)).strip()
plans={x['CODPESTUD']:x for x in json.loads((R/'data/versiones_historicas_sies_umas/fase_4_20261015/catalogo_planes.json').read_text())};subjects={x['persona'] for x in items};annual=defaultdict(list)
for key,sheet in [('mu','BASE_RETENCION_MU'),('carga','2025_carga')]:
 w=openpyxl.load_workbook(sources[key]['ruta'],read_only=True,data_only=True);ws=w[sheet];it=ws.iter_rows(values_only=True);hdr=next(it)
 if key=='mu':idx={str(v):i for i,v in enumerate(hdr)};pos=[idx[x] for x in ['N_DOC','DV','COD_SED','COD_CAR','JOR','VERSION','ANIO_ING_ACT','SEM_ING_ACT','ANIO_ING_ORI','ANIO_INFORMADO','TIPO_DOC']]
 else:pos=[72,73,82,83,85,86,88,89,90,None,None]
 for rn,row in enumerate(it,2):
  get=lambda i:row[i] if i is not None and i<len(row) else None
  b,d,sed,car,jor,ver,ing,sem,ori,year,typ=[get(i) for i in pos];pe=identity(b,d);year='2025' if key=='carga' else val(year)
  if pe not in subjects or (key=='mu' and val(typ) not in ('R','1')):continue
  cd=code(sed,car,jor,ver)
  if cd:annual[(pe,year)].append({'codigo':cd,'ANIO_ING_ACT':val(ing),'SEM_ING_ACT':val(sem),'ANIO_ING_ORI':val(ori),'fuente':sources[key]['ruta'],'sha256':sources[key]['sha256'],'hoja':sheet,'fila':rn})
 w.close()
activities=defaultdict(set);actrows=defaultdict(list);prior=defaultdict(list)
for key in ['p7804','p12166','p3233']:
 w=openpyxl.load_workbook(sources[key]['ruta'],read_only=True,data_only=True);ws=w['Hoja1'];it=ws.iter_rows(values_only=True);hd={val(x):i for i,x in enumerate(next(it))};assert all(k in hd for k in ['RUT','DIG','CODCLI','CODCARR','ANO','PERIODO','PLAN_DE_ESTUDIO'])
 for rn,row in enumerate(it,2):
  get=lambda k:row[hd[k]] if hd[k]<len(row) else None
  pe=identity(get('RUT'),get('DIG'))
  if pe not in subjects:continue
  cli,car,year,per,plan=[val(get(k)) for k in ['CODCLI','CODCARR','ANO','PERIODO','PLAN_DE_ESTUDIO']];k=(pe,car,year,per);activities[k].add(cli);ref={'fuente':sources[key]['ruta'],'sha256':sources[key]['sha256'],'hoja':'Hoja1','fila':rn,'plan':plan,'anio':year,'periodo':per};actrows[(pe,cli,car,plan,year,per)].append(ref)
  if year.isdigit():prior[pe].append((int(year),plan,ref))
 w.close()
da=defaultdict(list)
for key in ['da12159','da11248']:
 w=openpyxl.load_workbook(sources[key]['ruta'],read_only=True,data_only=True);ws=w['Hoja1'];it=ws.iter_rows(values_only=True);hd={val(x):i for i,x in enumerate(next(it))};assert all(k in hd for k in ['RUT','CODCLI','CODCARPR','SEDE','JORNADA'])
 for rn,row in enumerate(it,2):
  get=lambda k:row[hd[k]] if hd[k]<len(row) else None
  pe=rut(get('RUT'))
  if pe in subjects:da[(pe,val(get('CODCLI')),val(get('CODCARPR')))].append({'sede':val(get('SEDE')),'jornada':val(get('JORNADA')),'fuente':sources[key]['ruta'],'sha256':sources[key]['sha256'],'hoja':'Hoja1','fila':rn})
 w.close()
w=openpyxl.load_workbook(sources['oferta']['ruta'],read_only=True,data_only=True);ws=w['in'];it=ws.iter_rows(values_only=True);hdr=next(it);assert val(hdr[0])=='AÑO' and val(hdr[1])=='CÓDIGO ÚNICO';offer=defaultdict(list)
for rn,row in enumerate(it,2):
 y=val(row[0]);c=val(row[1]);y=y[4:] if re.fullmatch(r'OFE_\d{4}',y) else y
 if c.startswith('I162'):offer[(y,c)].append({'fuente':sources['oferta']['ruta'],'sha256':sources['oferta']['sha256'],'hoja':'in','fila':rn,'vigencia':val(row[68]) if len(row)>68 else ''})
w.close();print('Fuentes verificadas; resultados individuales solo en carpeta privada',flush=True)
agg=defaultdict(lambda:{'contextos':0,'expedientes':set(),'personas':set()});out=[];counts=Counter();reasons=Counter();yearstats=Counter();codclistats=Counter()
for x in items:
 pe=x['persona'];cli=x['codcli'];car=x['carrera'];plan=x['plan'];year=str(x['anio']);per=str(x['periodo']);nextyear=str(int(year)+1);ann=annual.get((pe,nextyear),[]);codes={z['codigo'] for z in ann};match={c for c in codes if family(c) in x['familias_candidatas']};cd=next(iter(match)) if len(match)==1 else None;unique=len(codes)==1 and len(match)==1;rr=[z for z in ann if z['codigo']==cd];years={int(float(z['ANIO_ING_ACT'])) for z in rr if re.fullmatch(r'\d{4}(?:\.0)?',z['ANIO_ING_ACT'])};all_ing=bool(rr) and all(re.fullmatch(r'\d{4}(?:\.0)?',z['ANIO_ING_ACT']) and int(float(z['ANIO_ING_ACT']))<=int(year) for z in rr);yearstats['con_ano_ing_act']+=bool(years);yearstats['con_sem_ing_act']+=any(z['SEM_ING_ACT'] for z in rr);yearstats['con_ano_ing_ori']+=any(z['ANIO_ING_ORI'] for z in rr)
 dr=da.get((pe,cli,car),[]);sites={z['sede'] for z in dr if z['sede']};jours={z['jornada'] for z in dr if z['jornada']};m=re.fullmatch(r'I162S(\d+)C\d+J(\d+)V\d+',cd or '');sj={'D':'1','V':'2','O':'4'}.get(x['jornada']);site_ok=bool(m and len(sites)==1 and {'RE':'2','CO':'3'}.get(next(iter(sites)))==m[1]);jour_ok=bool(m and sj and m[2]==sj and (not jours or x['jornada'] in jours));activity=actrows.get((pe,cli,car,plan,year,per),[]);others=activities.get((pe,car,year,per),set())-{cli,''};off=offer.get((year,cd),[]) if cd else []
 docs=[]
 for oid,payload in svc.db.execute('select id,payload from observaciones where persona=? and codcli=? and anio=?',(pe,cli,nextyear)):
  z=json.loads(payload);doc=z.get('codigo_documental_atribuible');
  if doc:docs.append({'observacion_id':oid,'codigo':doc,'plan':z.get('plan'),'carrera':z.get('carrera'),'sede':z.get('sede_dimension'),'jornada':z.get('jornada_sies')})
 same=bool(cd and any(z['codigo']==cd and z['plan']==plan and z['carrera']==car for z in docs));codclistats['mismo_codcli_codigo_plan_carrera']+=same
 failures=[]
 if not ann:failures.append('SIN_MU_ANIO_SIGUIENTE_EN_FUENTES_REVISADAS')
 elif not unique:failures.append('CODIGO_MU_NO_UNICO_O_DISTINTA_FAMILIA')
 if not site_ok:failures.append('SEDE_NO_CONFIRMADA')
 if not jour_ok:failures.append('JORNADA_NO_CONFIRMADA')
 if not all_ing:failures.append('INGRESO_FALTANTE_CONFLICTIVO_O_POSTERIOR')
 if not activity:failures.append('ACTIVIDAD_PERIODO_NO_OBSERVADA')
 if others:failures.append('OTRO_CODCLI_MISMA_CARRERA_PERIODO')
 optional=[]
 if not off:optional.append('OFERTA_ANIO_NO_ENCONTRADA')
 if not same:optional.append('MISMO_CODCLI_CODIGO_DOCUMENTAL_ANIO_SIGUIENTE_NO_ACREDITADO')
 # D2: únicamente un control opcional sin comprobar; ausencia de evidencia nunca demuestra inexistencia.
 level='E' if failures or len(optional)>1 else 'D2_PROPUESTA' if optional else 'D1_PROPUESTA';counts[level]+=1;reasons.update(failures+optional)
 record={'persona':pe,'codcli':cli,'plan':plan,'carrera':car,'anio':year,'periodo':per,'alcance':x['alcance'],'relacion':x['relacion'],'nivel':level,'codigo_candidato':cd,'mu_anio_siguiente':ann,'ingresos_actuales':sorted(years),'mu_documental_codcli':docs,'datos_alumnos':dr,'actividad':activity,'otros_codcli':sorted(others),'oferta':off,'faltantes':failures+optional,'riesgos':['Extracciones revisadas de cobertura y fecha no certificadas.','La sede actual no acredita por sí sola su estado histórico.','No prueba envío ni aceptación SIES para el período.']};out.append(record);g=agg[(level,x['relacion'],car,year)];g['contextos']+=1;g['expedientes'].add((pe,cli,car));g['personas'].add(pe)
priv=P/'DETALLE_PRIVADO.json';assert not priv.exists();priv.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');os.chmod(priv,0o600)
rows=[{'nivel':k[0],'relacion':k[1],'carrera':k[2],'anio':k[3],'contextos':v['contextos'],'expedientes':len(v['expedientes']),'personas':len(v['personas'])} for k,v in sorted(agg.items())];summary={'contextos':len(out),'personas_distintas':len({x['persona'] for x in out}),'expedientes_distintos':len({(x['persona'],x['codcli'],x['carrera']) for x in out}),'niveles':dict(counts),'campos_recuperados':dict(yearstats),'documental_mismo_codcli':dict(codclistats),'motivos_no_excluyentes':dict(reasons),'tabla':rows};assert sum(counts.values())==430 and sum(r['contextos'] for r in rows)==430
(O/'RESULTADOS_AGREGADOS.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');lines=['# Fase G · Hito 1: MU del año siguiente','',f'[C/E] Se revisaron 430 contextos; propuestas {dict(counts)}. Ninguna propuesta está aplicada; no prueban atribución documental del período ni aceptación SIES.','[E] La ausencia de matrícula, actividad o CODCLI se limita a los respaldos consultados; la sede de Datos Alumnos no acredita fecha histórica. La oferta observada no demuestra vigencia administrativa.','', '| Nivel | Relación | Carrera | Año | Contextos | Expedientes | Personas | Clase |','|---|---|---|---:|---:|---:|---:|---|']
for r in rows:lines.append('| '+' | '.join(str(r[k]) for k in ['nivel','relacion','carrera','anio','contextos','expedientes','personas'])+' | C/E |')
lines.append('\n[C] Personas y expedientes pueden repetirse entre filas y no se suman. Motivos no excluyentes. Sin cambios de bases, denominadores ni diccionario.');(O/'INFORME.md').write_text('\n'.join(lines)+'\n');svc.close();assert active.read_bytes()==activebytes and sha256(R/json.loads(activebytes)['descriptor'])==json.loads(activebytes)['sha256'];assert sha256(json.loads((R/json.loads(activebytes)['descriptor']).read_text())['base_privada']['ruta'])==beforebase
manifest={'fecha':datetime.now().astimezone().isoformat(),'head':head,'descriptor_sha256':json.loads(activebytes)['sha256'],'fuente_foco':{'ruta':str(pin),'sha256':sha256(pin)},'fuentes':sources,'salidas':{z:sha256(O/z) for z in ['evaluar.py','INFORME.md','RESULTADOS_AGREGADOS.json']},'detalle_privado':{'ruta':str(priv),'sha256':sha256(priv)},'qa':{'contextos':430,'particion':True,'sin_edicion_commit_push':True}};(O/'MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in summary.items() if k!='tabla'},ensure_ascii=False,indent=2));print('manifest',sha256(O/'MANIFEST.json'))
