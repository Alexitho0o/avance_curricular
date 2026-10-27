"""Clasifica foco v17 sin asignar códigos ni publicar identificadores."""
from pathlib import Path
from collections import defaultdict,Counter
from datetime import datetime
import json,sys,hashlib,os,subprocess,re,unicodedata
import openpyxl
R=Path(__file__).resolve().parents[2];O=Path(__file__).parent;P=Path.home()/'.local/share/ipss/fase_f_hito1_20261027';os.umask(0o077);P.mkdir(parents=True,exist_ok=True);assert subprocess.run(['git','-C',str(P.parent),'rev-parse','--show-toplevel'],capture_output=True).returncode!=0
sys.path.insert(0,str(R));from common.diccionario_sies_seguimiento import sha256
active=R/'data/diccionario_sies_seguimiento/activo.json';start=active.read_bytes();head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip();assert head=='1383d5c2449b710328c7b56dbbefe72f9f7530ed';p=R/'outputs/avance_historico_atribucion_20261027/auditar_atribucion.py';n={'__file__':str(p)};exec(compile(p.read_text().split("with (OUT/'PARTICION_POR_CODIGO.csv')")[0],str(p),'exec'),n)
cache=n['cache'];svc=n['service'];assert svc.edicion=='v17_20261027_candidata_promedios' and len(cache)==5144
by_person=defaultdict(list);by_exp=defaultdict(list)
for k,v in cache.items():
 pe,cli,plan,car,jor,ano,per=k;by_person[pe].append((k,v));by_exp[(pe,cli,car)].append((k,v))
nucleus={p for p,rs in by_person.items() if all(not v.get('codigo_sies') for k,v in rs)};nuc_exp={e for e in by_exp if e[0] in nucleus};assert len(nucleus)==45 and len(nuc_exp)==87
pending=[(k,v) for k,v in cache.items() if not v.get('codigo_sies')];assert len(pending)==990
catalog=R/'data/versiones_historicas_sies_umas/fase_4_20261015/catalogo_planes.json';plans={x['CODPESTUD']:x for x in json.loads(catalog.read_text())};groups_path=R/'data/versiones_por_cohorte/20261016/grupos_existentes.json';groups=defaultdict(list)
for g in json.loads(groups_path.read_text()):groups[(g['codcarpr'],g['jornada'])].append(g)
def names(plan):return plans.get(plan,{}).get('nombres_carrera',[])
def flat(t):return re.sub(r'\s+',' ',''.join(c for c in unicodedata.normalize('NFKD',str(t).upper()) if not unicodedata.combining(c))).strip()
def area(t):return re.sub(r'^(?:CONTINUIDAD\s+)?(?:INGENIERIA|TECNICO)(?:\s+EN)?\s+','',flat(t)).strip()
def family(code):
 m=re.fullmatch(r'(I\d+S\d+C\d+J\d+)V\d+',str(code or ''));return m.group(1) if m else None
# Reuse validated row-by-row MU extraction from Hito 2 when available; its original rows carry provenance.
h2=Path.home()/'.local/share/ipss/fase_d_hito2_20261027/RESULTADOS_PRIVADOS.json';mh=json.loads((R/'outputs/fase_d_hito2_propuesta_20261027/MANIFEST.json').read_text());assert sha256(h2)==mh['detalle_privado']['sha256'];h2data=json.loads(h2.read_text());annual=defaultdict(dict)
for x in h2data:
 for row in x['mu_original_filas']:
  annual[(x['persona'],str(x['anio']))][(row['fuente'],row['hoja'],row['fila'])]=row
# Fallback to active annual documentary index for all remaining persons/years.
def mu_rows(pe,year):
 saved=list(annual.get((pe,year),{}).values()); seen={(r['fuente'],r['hoja'],r['fila']) for r in saved}
 for p in svc.db.execute('select payload from mu_anual where persona=? and anio=?',(pe,year)):
  z=json.loads(p[0]);key=(z['fuente'],z['hoja'],z['fila'])
  if key not in seen:saved.append({'codigo':z['codigo'],'ingreso':z.get('ingreso_actual'),'origen':z.get('ingreso_origen'),'fuente':z['fuente'],'hoja':z['hoja'],'fila':z['fila']})
 return saved
out=[];excluded=[];unknown_names=0;agg=defaultdict(lambda:{'contextos':0,'personas':set(),'expedientes':set()})
for k,v in pending:
 pe,cli,plan,car,jor,year,period=k; nm=[flat(x) for x in names(plan)];is_dip=car in ('DACD','ECCURYDP') or any('DIPLOMADO' in x for x in nm)
 if is_dip:excluded.append((k,v));continue
 if not nm:unknown_names+=1
 other=[(ok,ov) for ok,ov in by_person[pe] if (ok[1],ok[3])!=(cli,car)];samecli=any(ok[1]==cli and ok[3]!=car for ok,ov in other)
 cont=False
 for nm1 in nm:
  if not nm1.startswith('CONTINUIDAD INGENIERIA '):continue
  if any(flat(nm2).startswith('TECNICO ') and area(nm2)==area(nm1) for ok,ov in other for nm2 in names(ok[2])):cont=True
 if samecli:rel='CODCLI_POR_REVISAR'
 elif not other:rel='NINGUNO_EN_FOCO'
 elif cont:rel='CONTINUIDAD_MISMA_AREA'
 elif any(ok[3]==car and ok[4]!=jor for ok,ov in other):rel='MISMA_CARRERA_OTRA_JORNADA'
 elif any(ok[3]!=car for ok,ov in other):rel='OTRA_CARRERA_CAMBIO_NO_ACREDITADO'
 else:rel='OTRO'
 gs=groups.get((car,jor),[]);pf={family(cd) for g in gs for cd in g['codigos_base']};pf.discard(None);of={family(ov.get('codigo_sies')) for ok,ov in other if ov.get('codigo_sies')};of.discard(None);ann=mu_rows(pe,year);mf={family(z.get('codigo')) for z in ann};mf.discard(None)
 if not ann:mu='SIN_MU_PERSONA_ANIO_EN_INDICE_Y_RESPALDOS_REVISADOS'
 elif not pf:mu='FAMILIA_PENDIENTE_NO_DISPONIBLE'
 elif pf&of&mf:mu='COMPARTIDAS_SIN_DESAMBIGUAR'
 elif mf&pf and mf&of:mu='AMBAS_FAMILIAS'
 elif mf&pf:mu='FAMILIA_PENDIENTE_CANDIDATA'
 elif mf&of:mu='SOLO_OTRO_EXPEDIENTE'
 else:mu='OTRA_FAMILIA_O_NO_COMPARABLE'
 yrs=[]
 for z in ann:
  if family(z.get('codigo')) not in pf:continue
  val=str(z.get('ingreso') if z.get('ingreso') is not None else '').strip()
  if re.fullmatch(r'\d{4}(?:\.0)?',val):yrs.append(int(float(val)))
 if not yrs:ing='SIN_DATO_COMPARABLE'
 elif len(set(yrs))>1:ing='VARIOS_ANIOS'
 elif yrs[0]<=int(year):ing='INGRESO_MENOR_IGUAL_CONTEXTO'
 else:ing='INGRESO_POSTERIOR_CONTEXTO'
 scope='NUCLEO_45' if pe in nucleus else 'RESTO_FOCO';row={'persona':pe,'codcli':cli,'plan':plan,'carrera':car,'jornada':jor,'anio':year,'periodo':period,'alcance':scope,'relacion':rel,'mu':mu,'ingreso':ing,'fuentes_mu':ann,'familias_candidatas':sorted(pf),'familias_otro_expediente':sorted(of),'nombres_plan':nm,'otros_expedientes_foco':sorted({(ok[1],ok[3]) for ok,ov in other}),'motivo_diccionario':v.get('motivo')};out.append(row);a=agg[(scope,rel,mu,ing)];a['contextos']+=1;a['personas'].add(pe);a['expedientes'].add((pe,cli,car))
priv=P/'DETALLE_PRIVADO.json';assert not priv.exists();priv.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');os.chmod(priv,0o600)
rows=[{'alcance':k[0],'relacion':k[1],'mu':k[2],'ingreso':k[3],'contextos':v['contextos'],'expedientes':len(v['expedientes']),'personas':len(v['personas'])} for k,v in sorted(agg.items())];res={'foco_total_contextos':5144,'pendientes_originales':990,'excluidos_diplomados_contextos':len(excluded),'contextos_analizados':len(out),'nucleo_pre_exclusion':{'personas':len(nucleus),'expedientes':len(nuc_exp)},'planes_sin_nombre_catalogo_contextos':unknown_names,'tabla':rows,'relacion_contextos':dict(Counter(x['relacion'] for x in out)),'mu_contextos':dict(Counter(x['mu'] for x in out)),'ingreso_contextos':dict(Counter(x['ingreso'] for x in out)),'nucleo_post_exclusion':{'contextos':sum(x['alcance']=='NUCLEO_45' for x in out),'personas':len({x['persona'] for x in out if x['alcance']=='NUCLEO_45'}),'expedientes':len({(x['persona'],x['codcli'],x['carrera']) for x in out if x['alcance']=='NUCLEO_45'})}}
assert len(out)+len(excluded)==990 and sum(x['contextos'] for x in rows)==len(out)
(O/'RESULTADOS_AGREGADOS.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n');lines=['# Fase F · Hito 1','',f"[C] Foco: 5.144 contextos; {len(pending)} pendientes. Excluidos por diplomados: {len(excluded)} contextos; {len(out)} clasificados. Núcleo previo: 45 personas y 87 expedientes. Personas/expedientes no sumables entre filas.",'','[B/C/E] Relaciones se buscan en el foco; ninguno no acredita ausencia en la institución. Continuidad se identifica por nombres de planes con mismo área, sin probar migración. Familia pendiente es candidata por carrera/jornada, sin validar automáticamente sede ni asignación. Sin MU es ausencia en índice y respaldos revisados, no ausencia universal. Ingreso se evalúa solo en filas MU con familia candidata; faltas o conflictos permanecen visibles. Planes sin nombre de catálogo requieren revisión de exclusión.','', '| Alcance | Relación | MU | Ingreso | Contextos | Expedientes | Personas | Clase |','|---|---|---|---|---:|---:|---:|---|']
for r in rows:lines.append('| '+' | '.join(str(r[x]) for x in ['alcance','relacion','mu','ingreso','contextos','expedientes','personas'])+' | B/C/E |')
(O/'INFORME.md').write_text('\n'.join(lines)+'\n');svc.close();assert active.read_bytes()==start
m={'fecha':datetime.now().astimezone().isoformat(),'head':head,'descriptor_sha256':json.loads(start)['sha256'],'fuentes':{'script_foco':{'ruta':str(p),'sha256':sha256(p)},'catalogo_planes':{'ruta':str(catalog),'sha256':sha256(catalog)},'grupos':{'ruta':str(groups_path),'sha256':sha256(groups_path)},'detalle_hito2':{'ruta':str(h2),'sha256':sha256(h2)},'fuentes_foco':n['manifest']['fuentes']},'salidas':{x:sha256(O/x) for x in ['clasificar.py','RESULTADOS_AGREGADOS.json','INFORME.md']},'detalle_privado':{'ruta':str(priv),'sha256':sha256(priv)},'qa':{'foco_5144':True,'pendientes_990':True,'nucleo_45_87':True,'particion':True,'sin_cambios_fuentes_ni_denominadores':True,'commit_push':False}};(O/'MANIFEST.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in res.items() if k!='tabla'},ensure_ascii=False,indent=2));print('manifest',sha256(O/'MANIFEST.json'))
