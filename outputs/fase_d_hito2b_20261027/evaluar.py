"""Criterio D propuesto por usuario; no adopta correspondencias."""
from pathlib import Path
from collections import defaultdict,Counter
from datetime import datetime
import re,json,hashlib,os,subprocess,unicodedata,openpyxl
R=Path(__file__).resolve().parents[2]; O=Path(__file__).parent;P=Path.home()/'.local/share/ipss/fase_d_hito2b_20261027';os.umask(0o077);P.mkdir(parents=True,exist_ok=True)
assert subprocess.run(['git','-C',str(P.parent),'rev-parse','--show-toplevel'],capture_output=True).returncode!=0
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip();assert head=='567795c77eed72d92f4ba6879960ecf9d56e9909'
active=R/'data/diccionario_sies_seguimiento/activo.json'; ah=sha(active)
old=R/'outputs/fase_d_hito2_propuesta_20261027/MANIFEST.json';m=json.loads(old.read_text());a=Path(m['detalle_privado']['ruta']);assert sha(a)==m['detalle_privado']['sha256'];src=json.loads(a.read_text());src=[x for x in src if x['mu_clase_anterior']=='FAMILIA_PENDIENTE'];assert len(src)==312
prev=R/'outputs/fase_d_hito1b_20261027/MANIFEST.json';mb=json.loads(prev.read_text());bp=Path(mb['detalle_privado']['ruta']);assert sha(bp)==mb['detalle_privado']['sha256'];b=json.loads(bp.read_text());idx={(x['persona'],x['codcli'],x['carrera'],str(x['anio']),str(x['periodo']),x['plan']):x for x in b}
cat=json.loads((R/'data/catalogo_fuentes/CATALOGO_FUENTES.json').read_text())['catalogo']
files={}
for name in ['DATOSDEALUMNOS_12159.xlsx','DATOSDEALUMNOS_11248.xlsx','Oferta_Academica_2010_al_2026_SIES_05_06_2026_WEB_E.xlsx']:
 e=next(x for x in cat if x['archivo']==name);p=Path(unicodedata.normalize('NFD',e['ruta_consolidada']));assert sha(p)==e['sha256'];files[name]={'path':p,'sha256':e['sha256']}
def v(x):return '' if x is None else str(int(x)) if isinstance(x,float) and x.is_integer() else str(x).strip().upper()
def rut(x):
 s=re.sub(r'[.\s]','',v(x));m=re.fullmatch(r'(\d+)-([0-9K])',s)
 return str(int(m[1]))+'-'+m[2] if m else None
def family(x):return re.sub('V[0-9]+$','',x)
def coords(x):
 m=re.fullmatch(r'I162S(\d+)C(\d+)J(\d+)V(\d+)',x or '');return (m[1],m[3]) if m else None
subjects={x['persona'] for x in src};da=defaultdict(list)
for name in ['DATOSDEALUMNOS_12159.xlsx','DATOSDEALUMNOS_11248.xlsx']:
 s=files[name];w=openpyxl.load_workbook(s['path'],read_only=True,data_only=True);ws=w['Hoja1'];it=ws.iter_rows(values_only=True);hd={v(x):i for i,x in enumerate(next(it))};assert all(q in hd for q in ['RUT','CODCLI','CODCARPR','SEDE','JORNADA'])
 for rn,row in enumerate(it,2):
  get=lambda k:row[hd[k]] if hd[k]<len(row) else None
  pe=rut(get('RUT'))
  if pe not in subjects:continue
  da[(pe,v(get('CODCLI')),v(get('CODCARPR')))].append({'sede':v(get('SEDE')),'jornada':v(get('JORNADA')),'fuente':str(s['path']),'sha256':s['sha256'],'hoja':'Hoja1','fila':rn})
 w.close()
s=files['Oferta_Academica_2010_al_2026_SIES_05_06_2026_WEB_E.xlsx'];w=openpyxl.load_workbook(s['path'],read_only=True,data_only=True);ws=w['in'];it=ws.iter_rows(values_only=True);header=[v(x) for x in next(it)];assert header[0]=='AÑO' and header[1]=='CÓDIGO ÚNICO';offer=defaultdict(list)
for rn,row in enumerate(it,2):
 if len(row)<2:continue
 c=v(row[1]);y=v(row[0]);y=y[4:] if re.fullmatch(r'OFE_\d{4}',y) else y;
 if not c.startswith('I162'):continue
 offer[(y,c)].append({'hoja':'in','fila':rn,'vigencia':v(row[68]) if len(row)>68 else '', 'fuente':str(s['path']),'sha256':s['sha256']})
w.close()
# Busca en toda la oferta por año+código completo, sin exigir pertenencia previa del código al grupo UMAS.
def sid(x):return (x['persona'],x['codcli'],x['carrera'],str(x['anio']),str(x['periodo']),x['plan'])
agg=defaultdict(lambda:{'c':0,'p':set(),'e':set()}); details=[];counts=Counter();miss=Counter();hist=Counter()
for x in src:
 y=idx[sid(x)]; allcodes={z['codigo'] for z in x['mu_original_filas']};match={z for z in allcodes if family(z) in y['familias_pendientes_candidatas']};unique=len(allcodes)==1 and len(match)==1
 code=next(iter(match)) if len(match)==1 else None; da_rows=da.get((x['persona'],x['codcli'],x['carrera']),[]); sites={d['sede'] for d in da_rows if d['sede']}; jours={d['jornada'] for d in da_rows if d['jornada']}; expected_j={'D':'1','V':'2','O':'4'}.get(y['jornada']); site_map={'RE':'2','CO':'3'}; pos=coords(code)
 site_ok=bool(pos and len(sites)==1 and site_map.get(next(iter(sites)))==pos[0]);jour_ok=bool(pos and expected_j and pos[1]==expected_j and (not jours or y['jornada'] in jours)); site_conflict=bool(pos and len(sites)==1 and site_map.get(next(iter(sites))) and site_map[next(iter(sites))]!=pos[0]);jour_conflict=bool(pos and expected_j and pos[1]!=expected_j)
 entries=offer.get((x['anio'],code),[]) if code else []; had_old=bool(x['controles']['oferta_observada_anio']);hist['oferta_encontrada_busqueda_directa']+=bool(entries);hist['oferta_recuperada_busqueda_directa']+=bool(entries and not had_old)
 ing=x['controles']['ingreso_actual_le_anio']; acts=x['controles']['actividad_promedios'];other=x['controles']['otro_codcli_detectado'];othercareer=all(e['carrera']!=x['carrera'] for e in y['expedientes_con_codigo']); cont=x['relacion']=='CONTINUIDAD_TECNICO_INGENIERIA_MISMA_AREA';prior=x['controles']['continuidad_tecnico_anterior'] if cont else True
 base=[]
 if not unique:base.append('CODIGO_ANUAL_NO_UNICO_O_NO_FAMILIA')
 if site_conflict or jour_conflict:base.append('SEDE_O_JORNADA_DISTINTA')
 elif not site_ok or not jour_ok:base.append('SEDE_O_JORNADA_NO_ACREDITADA')
 if not ing:base.append('INGRESO_NO_ACREDITADO_O_POSTERIOR')
 if not acts:base.append('ACTIVIDAD_NO_ENCONTRADA')
 if other:base.append('OTRO_CODCLI_DETECTADO')
 if not othercareer:base.append('RELACION_OTRA_CARRERA_NO_CONFIRMADA')
 optional=[]
 if not entries:optional.append('OFERTA_NO_ENCONTRADA')
 if cont and not prior:optional.append('ANTECEDENTE_TECNICO_NO_ACREDITADO')
 if base or len(optional)>1:level='E'
 elif len(optional)==1:level='D2_PROPUESTA'
 else:level='D1_PROPUESTA'
 # Coverage remains disclosed; no claim of universal absence of other CODCLI.
 if level.startswith('D'):risk=['Cobertura de PROMEDIOS no certificada; ausencia de otro CODCLI se limita a extractos revisados.','Correspondencia interna propuesta; atribución documental del contexto no acreditada.']+optional
 else:risk=base+optional
 counts[level]+=1;miss.update(base+optional);g=agg[(level,x['relacion'],x['carrera'],x['anio'])];g['c']+=1;g['p'].add(x['persona']);g['e'].add((x['persona'],x['codcli'],x['carrera']))
 details.append({'persona':x['persona'],'codcli':x['codcli'],'plan':x['plan'],'carrera':x['carrera'],'anio':x['anio'],'periodo':x['periodo'],'jornada':y['jornada'],'codigo_propuesto':code,'nivel':level,'controles':{'codigo_unico':unique,'sede':site_ok,'jornada':jour_ok,'ingreso':ing,'actividad':acts,'otro_codcli':other,'otra_carrera':othercareer,'oferta':bool(entries),'tecnico_previo':prior},'riesgos':risk,'ingreso_fuentes':x['mu_original_filas'],'datos_alumnos':da_rows,'oferta_filas':entries,'promedios_fuentes':x['actividad_fuentes'],'otros_codcli':x['otros_codcli_observados']})
assert len(details)==312
p=P/'DETALLE_PROPUESTAS.json';p.write_text(json.dumps(details,ensure_ascii=False,indent=2)+'\n');os.chmod(p,0o600)
rows=[{'nivel':k[0],'relacion':k[1],'carrera':k[2],'anio':k[3],'contextos':z['c'],'expedientes':len(z['e']),'personas':len(z['p'])} for k,z in sorted(agg.items())]
res={'contextos':312,'niveles':dict(counts),'controles_faltantes':dict(miss),'verificacion_oferta':dict(hist),'tabla':rows,'exclusiones':'No se modifican los otros 424 contextos del núcleo','nota':'Ausencia de otro CODCLI acotada a tres extractos no certificados; D1 y D2 solo propuestas internas, no prueba documental ni aceptación SIES.'}
(O/'RESULTADOS_AGREGADOS.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n')
lines=['# Fase D · Hito 2b','', '[C/E] Se aplica el criterio interno aprobado para propuestas, sin exigir documentación por período. Las propuestas D1/D2 no se adoptan. La ausencia de otro CODCLI se limita a los extractos revisados, sin cobertura completa certificada. Las referencias MU, Datos Alumnos y oferta constan en el detalle privado.','', '[C] La oferta se buscó directamente por año y código completo en la hoja in, incluyendo códigos de continuidad que el filtro previo podía omitir. La existencia de fila es oferta observada; no equivale a aceptación SIES ni prueba vigencia administrativa de una matrícula.','', '| Nivel | Relación | Carrera | Año | Contextos | Expedientes | Personas | Clase |','|---|---|---|---:|---:|---:|---:|---|']
for z in rows:lines.append('| '+' | '.join(str(z[k]) for k in ['nivel','relacion','carrera','anio','contextos','expedientes','personas'])+' | C/E |')
lines+=['','[C] Personas y expedientes pueden repetirse entre filas; no sumarlos. Los demás 424 contextos no se reclasificaron.']
(O/'INFORME.md').write_text('\n'.join(lines)+'\n')
assert sha(active)==ah and subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()==head
manifest={'fecha':datetime.now().isoformat(),'head':head,'puntero_sha256':ah,'detalle_hito2_sha256':sha(a),'detalle_hito1b_sha256':sha(bp),'fuentes':{n:{'ruta':str(q['path']),'sha256':q['sha256']} for n,q in files.items()},'salidas':{n:sha(O/n) for n in ['evaluar.py','INFORME.md','RESULTADOS_AGREGADOS.json']},'detalle_privado':{'ruta':str(p),'sha256':sha(p)},'qa':{'contextos':312,'particion':sum(counts.values())==312,'sin_edicion_diccionario':True,'bases_y_denominadores_modificados':False,'commit_push':False}}
(O/'MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in res.items() if k!='tabla'},ensure_ascii=False,indent=2));print('MANIFEST_SHA256',sha(O/'MANIFEST.json'))
