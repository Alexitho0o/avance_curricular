"""Propuestas Fase F: compara evidencia sin modificar el diccionario."""
from pathlib import Path
from collections import defaultdict,Counter
from datetime import datetime
import json,os,re,subprocess,sys,unicodedata,hashlib,openpyxl
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R));from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento,sha256
O=Path(__file__).parent;P=Path.home()/'.local/share/ipss/fase_f_hito2_20261027';os.umask(0o077);P.mkdir(parents=True,exist_ok=True);assert subprocess.run(['git','-C',str(P.parent),'rev-parse','--show-toplevel'],capture_output=True).returncode!=0
active=R/'data/diccionario_sies_seguimiento/activo.json';activebytes=active.read_bytes();head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip();assert head=='1383d5c2449b710328c7b56dbbefe72f9f7530ed';svc=DiccionarioSiesSeguimiento();assert svc.edicion=='v17_20261027_candidata_promedios';beforebase=sha256(svc.descriptor['base_privada']['ruta'])
fm=R/'outputs/fase_f_hito1_clasificacion_20261027/MANIFEST.json';m=json.loads(fm.read_text());pin=Path(m['detalle_privado']['ruta']);assert sha256(pin)==m['detalle_privado']['sha256'];allitems=json.loads(pin.read_text());items=[x for x in allitems if x['mu']=='FAMILIA_PENDIENTE_CANDIDATA'];assert len(items)==263 and Counter(x['alcance'] for x in items)=={'NUCLEO_45':242,'RESTO_FOCO':21}
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
agg=defaultdict(lambda:{'contextos':0,'expedientes':set(),'personas':set()});out=[];counts=Counter();reasons=Counter();ing_counts=Counter()
for x in items:
 pe=x['persona'];cli=x['codcli'];car=x['carrera'];plan=x['plan'];year=str(x['anio']);per=str(x['periodo']);ann=annual.get((pe,year),[]);codes={z['codigo'] for z in ann};match={c for c in codes if family(c) in x['familias_candidatas']};unique=len(codes)==1 and len(match)==1;cd=next(iter(match)) if len(match)==1 else None;rows=[z for z in ann if z['codigo']==cd];years={int(float(z['ANIO_ING_ACT'])) for z in rows if re.fullmatch(r'\d{4}(?:\.0)?',z['ANIO_ING_ACT'])};sem={z['SEM_ING_ACT'] for z in rows if z['SEM_ING_ACT']};ori={z['ANIO_ING_ORI'] for z in rows if z['ANIO_ING_ORI']};ing_counts['ANIO_ING_ACT']+=bool(years);ing_counts['SEM_ING_ACT']+=bool(sem);ing_counts['ANIO_ING_ORI']+=bool(ori)
 ingok=len(years)==1 and next(iter(years))<=int(year);da_rows=da.get((pe,cli,car),[]);sites={r['sede'] for r in da_rows if r['sede']};jours={r['jornada'] for r in da_rows if r['jornada']};m=re.fullmatch(r'I162S(\d+)C\d+J(\d+)V\d+',cd or '');expj={'D':'1','V':'2','O':'4'}.get(x['jornada']);site_ok=bool(m and len(sites)==1 and {'RE':'2','CO':'3'}.get(next(iter(sites)))==m[1]);jour_ok=bool(m and expj and m[2]==expj and (not jours or x['jornada'] in jours));activity=actrows.get((pe,cli,car,plan,year,per),[]);others=activities.get((pe,car,year,per),set())-{cli,''};otherexp=x['otros_expedientes_foco'];othercareer=all(e[1]!=car for e in otherexp);off=offer.get((year,cd),[]) if cd else []
 cont=x['relacion']=='CONTINUIDAD_MISMA_AREA';tecnico=[]
 if cont and len(years)==1:
  expected={area(n) for n in x['nombres_plan'] if flat(n).startswith('CONTINUIDAD INGENIERIA ')}
  for yr,pl,ref in prior.get(pe,[]):
   if yr>=next(iter(years)):continue
   names=plans.get(pl,{}).get('nombres_carrera',[])
   if any(flat(n).startswith('TECNICO ') and area(n) in expected for n in names):tecnico.append(ref)
 failures=[]
 if not unique:failures.append('CODIGO_MU_NO_UNICO_O_DISTINTA_FAMILIA')
 if not site_ok:failures.append('SEDE_NO_CONFIRMADA')
 if not jour_ok:failures.append('JORNADA_NO_CONFIRMADA')
 if not ingok:failures.append('INGRESO_FALTANTE_CONFLICTIVO_O_POSTERIOR')
 if not activity:failures.append('ACTIVIDAD_PERIODO_NO_OBSERVADA')
 if others:failures.append('OTRO_CODCLI_MISMA_CARRERA_PERIODO')
 if not othercareer:failures.append('OTRO_EXPEDIENTE_MISMA_CARRERA')
 optional=[]
 if not off:optional.append('OFERTA_NO_ENCONTRADA')
 if cont and not tecnico:optional.append('TECNICO_PREVIO_NO_ACREDITADO')
 level='E' if failures or len(optional)>1 else 'D2_PROPUESTA' if optional else 'D1_PROPUESTA';counts[level]+=1;reasons.update(failures+optional);detail={'persona':pe,'codcli':cli,'plan':plan,'carrera':car,'anio':year,'periodo':per,'alcance':x['alcance'],'relacion':x['relacion'],'nivel':level,'codigo_candidato':cd,'mu_original':ann,'ingresos_actuales':sorted(years),'semestres':sorted(sem),'ingresos_origen':sorted(ori),'datos_alumnos':da_rows,'actividad':activity,'otros_codcli':sorted(others),'oferta':off,'tecnico_previo':tecnico,'faltantes':failures+optional,'riesgos':['Ausencia de otro CODCLI limitada a extractos revisados; cobertura completa no acreditada.','Sede de Datos Alumnos no necesariamente acredita fecha histórica.','Correspondencia interna propuesta; atribución documental por período no acreditada.']};out.append(detail);g=agg[(x['alcance'],level,x['relacion'],car,year)];g['contextos']+=1;g['personas'].add(pe);g['expedientes'].add((pe,cli,car))
priv=P/'DETALLE_PRIVADO.json';assert not priv.exists();priv.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');os.chmod(priv,0o600)
rows=[{'alcance':k[0],'nivel':k[1],'relacion':k[2],'carrera':k[3],'anio':k[4],'contextos':v['contextos'],'expedientes':len(v['expedientes']),'personas':len(v['personas'])} for k,v in sorted(agg.items())];nucD1={x['persona'] for x in out if x['alcance']=='NUCLEO_45' and x['nivel']=='D1_PROPUESTA'};nucD2={x['persona'] for x in out if x['alcance']=='NUCLEO_45' and x['nivel']=='D2_PROPUESTA'};res={'contextos':263,'por_alcance':dict(Counter(x['alcance'] for x in out)),'niveles':dict(counts),'faltantes_no_exclusivos':dict(reasons),'ingreso_campos_recuperados':dict(ing_counts),'personas_nucleo_45_con_al_menos_una_D1':len(nucD1),'personas_nucleo_45_con_al_menos_una_D1_o_D2':len(nucD1|nucD2),'conteos_sin_suma_entre_filas':True,'tabla':rows};assert sum(counts.values())==263 and sum(x['contextos'] for x in rows)==263
(O/'RESULTADOS_AGREGADOS.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n');lines=['# Fase F · Hito 2: propuestas no aplicadas','',f"[C] Foco: 263 contextos; propuestas {dict(counts)}. Personas del núcleo con al menos una D1: {len(nucD1)}; con D1 o D2: {len(nucD1|nucD2)}. Son escenarios, no cierres adoptados.",'','[E] Ausencia de otro CODCLI se limita a tres extractos de cobertura no acreditada. Sede en Datos Alumnos no demuestra fecha histórica; MU se vincula por persona/año/código y no por sí sola al plan o CODCLI. Continuidad solo se respalda por actividad técnica en año anterior, no por fecha exacta ni por título no revisado. D1/D2 no acreditan envío SIES ni asignación documental al período.','', '| Alcance | Nivel | Relación | Carrera | Año | Contextos | Expedientes | Personas | Clase |','|---|---|---|---|---:|---:|---:|---:|---|']
for x in rows:lines.append('| '+' | '.join(str(x[k]) for k in ['alcance','nivel','relacion','carrera','anio','contextos','expedientes','personas'])+' | C/E |')
lines+=['','[C] No sumar personas ni expedientes entre filas; los motivos pueden solaparse. Los contextos excluidos por diplomados no se incorporan. Sin modificación de diccionario, bases ni denominadores.'];(O/'INFORME.md').write_text('\n'.join(lines)+'\n');svc.close();assert active.read_bytes()==activebytes and sha256(json.loads(activebytes)['descriptor'] if False else R/json.loads(activebytes)['descriptor'])==json.loads(activebytes)['sha256'];assert sha256(json.loads((R/json.loads(activebytes)['descriptor']).read_text())['base_privada']['ruta'])==beforebase
manifest={'fecha':datetime.now().astimezone().isoformat(),'head':head,'descriptor_sha256':json.loads(activebytes)['sha256'],'fuente_foco':{'ruta':str(pin),'sha256':sha256(pin)},'fuentes':sources,'salidas':{z:sha256(O/z) for z in ['evaluar.py','INFORME.md','RESULTADOS_AGREGADOS.json']},'detalle_privado':{'ruta':str(priv),'sha256':sha256(priv)},'qa':{'contextos':263,'particion':True,'exclusion_diplomados_hito1':True,'sin_edicion_commit_push':True}};(O/'MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in res.items() if k!='tabla'},ensure_ascii=False,indent=2));print('manifest',sha256(O/'MANIFEST.json'))
