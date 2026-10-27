"""Relaciona expedientes del foco v14, sin asignar códigos ni modificar fuentes."""
from pathlib import Path
from collections import defaultdict,Counter
from datetime import datetime
import hashlib,json,os,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]; OUT=Path(__file__).parent
PRIVATE=Path.home()/'.local/share/ipss/fase_d_hito1_20261027'
assert subprocess.run(['git','-C',str(PRIVATE.parent),'rev-parse','--show-toplevel'],capture_output=True).returncode!=0
os.umask(0o077);PRIVATE.mkdir(parents=True,exist_ok=True)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def git(*x):return subprocess.check_output(['git',*x],cwd=ROOT,text=True).strip()
head=git('rev-parse','HEAD'); assert head=='567795c77eed72d92f4ba6879960ecf9d56e9909'; assert git('branch','--show-current')=='feature/ire-2026'
active=ROOT/'data/diccionario_sies_seguimiento/activo.json'; oldactive=sha(active)
p=ROOT/'outputs/avance_historico_atribucion_20261027/auditar_atribucion.py';n={'__file__':str(p)}
exec(compile(p.read_text().split("with (OUT/'PARTICION_POR_CODIGO.csv')")[0],str(p),'exec'),n)
cache=n['cache'];svc=n['service'];byexp=defaultdict(list);byperson=defaultdict(list)
for k,v in cache.items():
 pe,cli,plan,career,jour,year,period=k;byexp[(pe,cli,career)].append((k,v));byperson[pe].append((k,v))
target=[e for e,rs in byexp.items() if all(not v.get('codigo_sies') for _,v in rs) and any(v.get('codigo_sies') for _,v in byperson[e[0]])]
assert len(target)==209 and len(cache)==5144
by_group=defaultdict(list)
for g in json.loads((ROOT/'data/versiones_por_cohorte/20261016/grupos_existentes.json').read_text()):by_group[(g['codcarpr'],g['jornada'])].append(g)
history={x['codigo_unico']:x for x in json.loads((ROOT/'data/versiones_por_cohorte/20261016/historias_oferta.json').read_text())}
counts=Counter();agg=defaultdict(lambda:{'contexts':0,'people':set(),'exp':set()}); detail=[]
for ek in sorted(target):
 pe,cli,career=ek; pending=byexp[ek]; resolved=[(k,v) for k,v in byperson[pe] if v.get('codigo_sies')]; related=defaultdict(list)
 for k,v in resolved: related[(k[1],k[3])].append((k,v))
 samecli=any(x[0]==cli for x in related); samecareer=[rs for (c,car),rs in related.items() if car==career]; othercareer=any(car!=career for c,car in related)
 pendingj={k[4] for k,v in pending}; resolvedj={k[4] for rs in samecareer for k,v in rs}
 if samecareer and pendingj.isdisjoint(resolvedj):rel='MISMA_CARRERA_OTRA_JORNADA'
 elif samecareer:rel='MISMA_CARRERA_JORNADA_COMPARTIDA'
 elif othercareer:rel='OTRA_CARRERA_CONTINUIDAD_POR_VERIFICAR'
 else:rel='OTRO_O_MULTIPLE'
 if samecli and othercareer:dup='MISMO_CODCLI_CON_CARRERAS_DISTINTAS_REVISAR'
 elif samecli:dup='MISMO_CODCLI_OTRO_CONTEXTO'
 else:dup='CODCLI_DISTINTO_NO_ES_DUPLICADO_POR_SI_SOLO'
 counts[rel]+=1
 for k,v in pending:
  _,_,plan,car,jour,year,period=k
  ann=[]
  for row in svc.db.execute('select anio,codigo,fuente,hoja,fila,payload from mu_anual where persona=? and anio=?',(pe,str(year))):
   payload=json.loads(row[5]);ann.append({'anio':row[0],'codigo':row[1],'fuente':row[2],'hoja':row[3],'fila':row[4],'ingreso_actual':payload.get('ingreso_actual'),'ingreso_origen':payload.get('ingreso_origen')})
  gs=by_group.get((car,jour),[]);possible={code for g in gs for code in g['codigos_base']};offer=[{'codigo':code,'anual':h} for code in possible if code in history for h in history[code]['anual'] if str(h['anio'])==str(year)]
  entry={'persona':pe,'codcli':cli,'carrera':car,'plan':plan,'jornada':jour,'anio':year,'periodo':period,'relacion':rel,'alerta_codcli':dup,'expedientes_con_codigo':[{'codcli':rcli,'carrera':rcar,'contextos':[{'plan':z[0][2],'jornada':z[0][4],'anio':z[0][5],'periodo':z[0][6],'codigo':z[1].get('codigo_sies'),'nivel_respaldo':z[1].get('nivel_respaldo')} for z in rr]} for (rcli,rcar),rr in related.items()],'mu_anual_misma_persona_y_anio':ann,'grupos_oferta_candidatos':gs,'oferta_anual_candidata':offer,'actividad_promedios':'Registro exacto en el foco procedente de PROMEDIOS 7804, Hoja1; no prueba vigencia ni version','estado':'E_SIN_ATRIBUCION_AL_EXPEDIENTE'}
  detail.append(entry); key=(car,year,rel,dup,'MU_PERSONA_ANIO' if ann else 'SIN_MU_PERSONA_ANIO','OFERTA_CANDIDATA_ANIO' if offer else 'SIN_OFERTA_CANDIDATA_ANIO'); a=agg[key];a['contexts']+=1;a['people'].add(pe);a['exp'].add(ek)
private=PRIVATE/'DETALLE_PRIVADO.json';private.write_text(json.dumps(detail,ensure_ascii=False,indent=2)+'\n');os.chmod(private,0o600)
rows=[{'carrera':k[0],'anio':k[1],'relacion':k[2],'alerta_codcli':k[3],'mu':k[4],'oferta':k[5],'contextos':v['contexts'],'personas':len(v['people']),'expedientes':len(v['exp'])} for k,v in sorted(agg.items())]
res={'clasificacion':'B/C/E','foco_contextos':len(cache),'expedientes':len(target),'personas':len({e[0] for e in target}),'contextos':len(detail),'relacion_expedientes':dict(counts),'grupos':len(rows),'detalle_grupos':rows,'limites':['Las relaciones y la oferta son evidencia a nivel contextual; no atribuyen automaticamente version o plan.','Las filas MU son de la persona y año, no implican el mismo CODCLI ni plan.','Año de ingreso se conserva en detalle, no se infiere si falta o si su alcance no está demostrado.','Continuidad y duplicado real no se afirman sin respaldo.','Conteos de personas y expedientes por grupo pueden solaparse entre años.']}
(OUT/'RESULTADOS_AGREGADOS.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n')
lines=['# Fase D · Hito 1','',f"[C] Foco: {len(cache)} contextos. Subconjunto: {len(target)} expedientes sin código, pertenecientes a {res['personas']} personas con otro expediente con código; {len(detail)} contextos.",'','[B/C/E] PROMEDIOS acredita actividad observada en el foco; MU anual está vinculada a persona/año, no necesariamente al expediente. La oferta ofrece candidatos, no prueba asignación personal. El ingreso actual/origen está en detalle privado y requiere interpretación de fuente. Continuidad técnica–ingeniería y duplicados reales quedan pendientes cuando no están acreditados.','', '| Carrera | Año | Relación | Control CODCLI | MU persona/año | Oferta candidata/año | Contextos | Personas | Expedientes | Clase |','|---|---:|---|---|---|---|---:|---:|---:|---|']
for x in rows:lines.append('| '+' | '.join(str(x[t]) for t in ['carrera','anio','relacion','alerta_codcli','mu','oferta','contextos','personas','expedientes'])+' | B/C/E |')
lines+=['','[C] Las personas y expedientes por fila pueden repetirse entre años y grupos; no sumarlos. No se cambian bases, denominadores ni edición del diccionario.','']
(OUT/'INFORME.md').write_text('\n'.join(lines))
svc.close(); assert sha(active)==oldactive and git('rev-parse','HEAD')==head
out=['RESULTADOS_AGREGADOS.json','INFORME.md','analizar.py'];manifest={'fecha':datetime.now().isoformat(),'head':head,'diccionario_puntero_sha256':oldactive,'descriptor_sha256':'8d9390f3552c5dc076562c2c137ca9159ba939800fa8fff4ab7b90d4e079a6c3','fuentes':{'foco_script':{'ruta':str(p),'sha256':sha(p)},'grupos':{'ruta':'data/versiones_por_cohorte/20261016/grupos_existentes.json','sha256':sha(ROOT/'data/versiones_por_cohorte/20261016/grupos_existentes.json')},'oferta':{'ruta':'data/versiones_por_cohorte/20261016/historias_oferta.json','sha256':sha(ROOT/'data/versiones_por_cohorte/20261016/historias_oferta.json')},'foco_fuentes':n['manifest']['fuentes']},'salidas':{x:sha(OUT/x) for x in out},'detalle_privado':{'ruta':str(private),'sha256':sha(private)},'qa':{'expedientes':len(target),'contextos':len(detail),'particion_relaciones':sum(counts.values())==209,'v14_intacta':True,'head_intacto':True,'base_denominadores_modificados':False}}
(OUT/'MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:res[k] for k in ['expedientes','personas','contextos','relacion_expedientes','grupos']},ensure_ascii=False));print('MANIFEST_SHA256',sha(OUT/'MANIFEST.json'))
