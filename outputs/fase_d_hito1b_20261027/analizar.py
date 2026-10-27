"""Clasificación descriptiva del foco, sin asignar códigos ni editar fuentes."""
from pathlib import Path
from collections import defaultdict,Counter
import json,re,unicodedata,hashlib,os,subprocess
R=Path(__file__).resolve().parents[2]; O=Path(__file__).parent; P=Path.home()/'.local/share/ipss/fase_d_hito1b_20261027';os.umask(0o077);P.mkdir(parents=True,exist_ok=True)
assert subprocess.run(['git','-C',str(P.parent),'rev-parse','--show-toplevel'],capture_output=True).returncode!=0
h=lambda x:hashlib.sha256(Path(x).read_bytes()).hexdigest()
infile=Path.home()/'.local/share/ipss/fase_d_hito1_20261027/DETALLE_PRIVADO.json'; source=json.loads(infile.read_text()); assert len(source)==737
catalog=R/'data/versiones_historicas_sies_umas/fase_4_20261015/catalogo_planes.json';plans={x['CODPESTUD']:x for x in json.loads(catalog.read_text())}
seen=defaultdict(list)
for x in source: seen[(x['persona'],x['codcli'],x['carrera'])].append(x)
assert len(seen)==209

def names(plan):return sorted(set(plans.get(plan,{}).get('nombres_carrera',[])))
def flat(s):return re.sub(r'\s+',' ',''.join(c for c in unicodedata.normalize('NFKD',s.upper()) if not unicodedata.combining(c))).strip()
def area(s):
 s=flat(s);return re.sub(r'^(?:CONTINUIDAD\s+)?(?:INGENIERIA|TECNICO)(?:\s+EN)?\s+','',s).strip()
def family(code):
 m=re.fullmatch(r'(I\d+S\d+C\d+J\d+)V\d+',str(code or ''));return m.group(1) if m else None
counts=Counter(); grouped=defaultdict(lambda:{'contexts':0,'people':set(),'exp':set()});out=[]; excluded=defaultdict(list)
for exp, contexts in seen.items():
 pending_names={flat(y) for x in contexts for y in names(x['plan'])}
 if exp[2]=='DACD' or any('DIPLOMADO' in z for z in pending_names): excluded[exp]=contexts;continue
 same_cli=any(y['codcli']==exp[1] and y['carrera']!=exp[2] for x in contexts for y in x['expedientes_con_codigo'])
 continuity=False
 for x in contexts:
  for nm in names(x['plan']):
   if not flat(nm).startswith('CONTINUIDAD INGENIERIA '):continue
   for e in x['expedientes_con_codigo']:
    for z in e['contextos']:
     for other in names(z['plan']):
      if flat(other).startswith('TECNICO ') and area(other)==area(nm):continuity=True
 # Categories are exclusive: a potential duplicate is retained as a separate alert if continuity has precedence.
 if same_cli:rel='CODCLI_POSIBLE_DUPLICADO_O_CAMBIO_DE_CARRERA'
 elif continuity:rel='CONTINUIDAD_TECNICO_INGENIERIA_MISMA_AREA'
 elif all(e['carrera']!=exp[2] for x in contexts for e in x['expedientes_con_codigo']):rel='OTRA_CARRERA_CAMBIO_POR_CONFIRMAR'
 elif any(e['carrera']==exp[2] and all(z['jornada']!=x['jornada'] for z in e['contextos']) for x in contexts for e in x['expedientes_con_codigo']):rel='MISMA_CARRERA_OTRA_JORNADA'
 else:rel='OTRO_O_MULTIPLE'
 counts[rel]+=1
 for x in contexts:
  pf={family(z) for g in x['grupos_oferta_candidatos'] for z in g['codigos_base']};pf.discard(None)
  of={family(z['codigo']) for e in x['expedientes_con_codigo'] for z in e['contextos']};of.discard(None)
  ann=x['mu_anual_misma_persona_y_anio']; mf={family(z['codigo']) for z in ann};mf.discard(None)
  if not ann:mu='SIN_MU_ANIO'
  elif not pf:mu='FAMILIA_PENDIENTE_NO_DISPONIBLE'
  elif pf & of & mf:mu='FAMILIAS_COMPARTIDAS_SIN_DESAMBIGUAR'
  elif mf & pf and mf & of:mu='AMBAS_FAMILIAS'
  elif mf & pf:mu='FAMILIA_PENDIENTE'
  elif mf & of:mu='SOLO_OTRO_EXPEDIENTE'
  else:mu='MU_OTRA_FAMILIA_O_NO_COMPARABLE'
  # Use only rows matching the pending family, otherwise no comparable entry-year.
  p_ann=[z for z in ann if family(z['codigo']) in pf]; yrs=[]
  for z in p_ann:
   v=str(z.get('ingreso_actual') or '').strip();
   if re.fullmatch(r'\d{4}(?:\.0)?',v):yrs.append(int(float(v)))
  if not yrs:ing='SIN_DATO_COMPARABLE'
  elif len(set(yrs))>1:ing='VARIOS_ANIOS_EN_MU'
  elif yrs[0]<=int(x['anio']):ing='INGRESO_MENOR_IGUAL_CONTEXTO'
  else:ing='INGRESO_POSTERIOR_CONTEXTO'
  y=dict(x);y.update({'relacion_1b':rel,'nombres_carrera_pendiente':sorted(pending_names),'alerta_codcli':same_cli,'familias_pendientes_candidatas':sorted(pf),'familias_otro_expediente':sorted(of),'clasificacion_mu':mu,'clasificacion_ingreso':ing,'ingreso_comparado_solo_familia_pendiente':True,'continuidad_area_nombre_catalogo':continuity});out.append(y)
  a=grouped[(rel,mu,ing)];a['contexts']+=1;a['people'].add(exp[0]);a['exp'].add(exp)
priv=P/'DETALLE_PRIVADO.json';priv.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');os.chmod(priv,0o600)
rows=[{'tipo':k[0],'MU':k[1],'ingreso':k[2],'contextos':v['contexts'],'expedientes':len(v['exp']),'personas':len(v['people'])} for k,v in sorted(grouped.items())]
res={'expedientes_originales':209,'expedientes_excluidos_diplomado':len(excluded),'contextos_excluidos_diplomado':sum(map(len,excluded.values())),'personas_excluidas_diplomado':len({e[0] for e in excluded}),'carreras_excluidas':dict(Counter(e[2] for e in excluded)),'expedientes_nucleo':sum(counts.values()),'personas_nucleo':len({x['persona'] for x in out}),'contextos_nucleo':len(out),'relaciones_expedientes':dict(counts),'tabla':rows}
assert res['expedientes_nucleo']+len(excluded)==209 and len(out)+res['contextos_excluidos_diplomado']==737 and sum(r['contextos'] for r in rows)==len(out)
(O/'RESULTADOS.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n')
text=['# Fase D · Hito 1b','',f"[C] De 209 expedientes y 737 contextos, se excluyen {len(excluded)} expedientes y {res['contextos_excluidos_diplomado']} contextos por diplomado; quedan {res['expedientes_nucleo']} expedientes, {len(out)} contextos y {res['personas_nucleo']} personas.",'','[C/E] La continuidad se clasifica solo cuando el nombre del plan en el catálogo dice continuidad de ingeniería y el otro plan dice técnico con área idéntica normalizada. Es relación de perfiles observados, no prueba de transición o fecha. CODCLI compartido entre carreras es alerta, no duplicado demostrado. Cambio de carrera describe carreras distintas de una persona, no fecha ni migración.','', '[C/E] Las familias de la carrera pendiente son candidatas del catálogo por carrera y jornada, sin atribución individual ni validación automática de sede. Si se comparten familias, no se fuerza la clasificación. La MU es por persona/año. El año de ingreso se evalúa solo en filas MU de familia candidata pendiente; múltiples valores quedan separados. Sin ese vínculo, es sin dato comparable.','', '| Tipo | MU | Año de ingreso | Contextos | Expedientes | Personas | Clase |','|---|---|---|---:|---:|---:|---|']
for x in rows:text.append('| '+' | '.join(str(x[t]) for t in ['tipo','MU','ingreso','contextos','expedientes','personas'])+' | B/C/E |')
text+=['','[C] Personas y expedientes pueden aparecer en varias filas. No sumarlos. La actividad procede de PROMEDIOS 7804 del foco previo; no acredita vigencia ni versión. No se modifica base, denominador ni diccionario.']
(O/'INFORME.md').write_text('\n'.join(text)+'\n')
manifest={'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'fuentes':{'detalle_hito1':{'ruta':str(infile),'sha256':h(infile)},'catalogo_planes':{'ruta':str(catalog),'sha256':h(catalog)},'manifest_hito1':{'ruta':str(R/'outputs/fase_d_hito1_expedientes_20261027/MANIFEST.json'),'sha256':h(R/'outputs/fase_d_hito1_expedientes_20261027/MANIFEST.json')}},'salidas':{x:h(O/x) for x in ['analizar.py','INFORME.md','RESULTADOS.json']},'detalle_privado':{'ruta':str(priv),'sha256':h(priv)},'qa':{'particion_209':True,'particion_737':True,'no_asignacion_codigo':True,'bases_denominadores_modificados':False,'commit_push':False}}
(O/'MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in res.items() if k!='tabla'},ensure_ascii=False,indent=2)); print('sha_manifest',h(O/'MANIFEST.json'))
