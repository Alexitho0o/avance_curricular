"""Conciliación local acotada; ninguna identidad se exporta al repositorio."""
import json,re,hashlib,datetime,csv
from pathlib import Path
from collections import defaultdict,Counter
import openpyxl
R=Path.cwd();O=R/'outputs/retencion_puente_provisional_20261022_v7';T=Path('/tmp/ipss_resolucion_2317_20261022');T.mkdir(exist_ok=True)
load=lambda p:json.load(open(p));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=load('/tmp/ipss_revision_63_20261022/payload.json');get=lambda n:next(s['rows'] for s in p if s['name']==n)
emb=load('/tmp/ipss_embudo_2317_20261022/embudo_privado.json');foc={r[0] for r in emb};keys={tuple(r[:8]) for r in emb}
u=[r for r in get('CONTRASTE_63') if tuple(r[:8]) in keys];assert len(u)==4973 and len(foc)==2317
old=[e for e in get('EVIDENCIAS_SIES') if e[0] in foc];new=load('/tmp/ipss_embudo_2317_20261022/evidencias_nuevas.json');idx=defaultdict(list)
for e in old:idx[e[0]].append(e)
val=lambda v:'' if v is None else str(int(v)) if isinstance(v,float) and v.is_integer() else str(v).strip()
def key(a,b=None):
 s=val(a).upper().replace('.','').replace(' ','')+('-'+val(b).upper() if b is not None else '')
 return str(int(s.split('-')[0]))+'-'+s.split('-')[1] if re.fullmatch(r'\d+-[0-9K]',s) else None
# Fuente individual 2025 omitida en el inventario de lecturas previo.
inv=load('/tmp/ipss_revision_privada_20261022/inventario_sies.json');tit=next(f for f in inv if 'Informe de Titulados 2025_vf' in f);h0=sha(tit);w=openpyxl.load_workbook(tit,read_only=True,data_only=True);s=w.active;it=iter(s.values);headers=next(it);titrows=[];dates=Counter();allread=0;titmatched=set();titmatchedrows=0
for rn,row in enumerate(it,2):
 allread+=1;x=dict(zip(headers,row));k=key(x.get('NUM_DOCUMENTO'),x.get('DV'));d=x.get('FECHA_OBT_TIT_GRA');year=str(d.year) if hasattr(d,'year') else val(d)[:4];dates[year]+=1
 if k not in foc:continue
 titmatched.add(k);titmatchedrows+=1
 for field in ['COD_SIES_OBT_TIT','COD_SIES_TERMINAL']:
  code=val(x.get(field))
  if re.fullmatch(r'I\d+S\d+C\d+J\d+V\d+',code):titrows.append([k,'TITULADOS',year,code,'COMPLETO',field,'',val(x.get('ANIO_INGRESO_CARRERA_ACTUAL')),tit,s.title,rn,'INFORME_DOCENCIA; no comprobante de aceptación','RUT/DV exacto'])
w.close();assert sha(tit)==h0
beforefound={e[0] for e in old if e[4]=='COMPLETO'}|{e[0] for e in new if e[4]=='COMPLETO'};newfound={e[0] for e in titrows}-beforefound
for e in titrows:idx[e[0]].append(e)
# Contextos DA de cortes existentes, con valores originales y localizadores.
da=defaultdict(list);dasheets=[]
for s in p:
 if s['name'].startswith('DA_'):
  rows=[r for r in s['rows'] if r[s['headers'].index('REV_RUT_DV')] in foc]
  dasheets.append({**s,'rows':rows})
  for r in rows:
   x=dict(zip(s['headers'],r));da[val(x['CODCLI']),val(x['CODCARPR'])].append(x)
# Para 15 excepciones leer solo los expedientes concretos, sin filtrar primero carrera/jornada.
needcli={r[1] for r in u if r[10]=='CODIGO_ANUAL_SIN_CONTEXTO_DA_EXACTO'};daextra=[];dahashes={}
for path in ['/Users/alexi/Downloads/DATOSDEALUMNOS_12159.xlsx','/Users/alexi/Downloads/2025/DATOSDEALUMNOS_11248.xlsx']:
 dahashes[path]=sha(path);w=openpyxl.load_workbook(path,read_only=True,data_only=True);s=w.active;it=iter(s.values);hh=next(it)
 for rn,row in enumerate(it,2):
  x=dict(zip(hh,row))
  if val(x.get('CODCLI')) in needcli:
   x.update(REV_FUENTE=path,REV_HOJA=s.title,REV_FILA=rn,REV_RUT_DV=key(x.get('RUT')));daextra.append(x)
 w.close()
# Localizadores anuales ya acreditados.
links=defaultdict(list)
for e in get('ENLACES_ANUALES'):
 if e[0] in foc:links[tuple(e[:6])].append(e)
newidx=defaultdict(list)
for e in new:
 if e[0] in foc:newidx[e[0]].append(e)
causes={tuple(r[:8]):r[9] for r in emb};results=[];proof=[];cnt=Counter();cohorts=Counter();group=defaultdict(lambda:[0,0,set()]);jm={'D':'1','V':'2','O':'4'}
for i,r in enumerate(u,1):
 k,cli,c,site,j,plan,y,t,previous,observed,state=r[:11];cause=causes[tuple(r[:8])];ev=links[(k,cli,c+'/'+j,plan,y,t)];fam={code.rsplit('V',1)[0] for code in r[12].split('; ') if code};annual={e[6] for e in ev};adopt='';rule='';newstate='BLOQUEADO';reason='';missing='';solution='';evid=[]
 contexts=[x for x in da[cli,c] if x['REV_RUT_DV']==k and val(x['SEDE'])=='RE' and jm.get(val(x['JORNADA']))==j]
 direct=[e for e in newidx[k] if e[4]=='COMPLETO' and e[7]==cli and e[8]==c and e[6]==plan and e[2]==y and e[3].rsplit('V',1)[0] in fam]
 if state=='DIFIERE_CODIGO_PROPUESTO_OBSERVADO' and len(annual)==1 and contexts:
  adopt=next(iter(annual));newstate='CONCILIADO_CODIGO_ANUAL_OBSERVADO';rule='V6_IDENTIDAD_FAMILIA_ANO_DA_SIN_ATRIBUCION_MULTIPLE';reason='Código anual documentado sustituye propuesta estadística SOLO en esta observación';missing='Plan efectivo histórico no acreditado; no impide registrar el código observado';solution='Usar código observado en conciliación; conservar propuesta previa como antecedente, sin modificar canon';evid=ev
 elif direct and len({e[3] for e in direct})==1 and (not annual or annual=={direct[0][3]}):
  adopt=direct[0][3];newstate='CONCILIADO_ENLACE_EXPLICITO';rule='IDENTIDAD_CODCLI_CARRERA_PLAN_ANO_EXPLICITOS';reason='Enlace directo explícito sin alternativas';missing='Aprobación de equivalencia general separada';solution='Registrar vínculo documental de observación';evid=ev
 else:
  if cause=='CODIGO_UNICO_ATRIBUCION_EXPEDIENTE':
   rule='NO_SELECCION_ARBITRARIA_CODCLI';missing=f'Fila de matrícula {y} con CODCLI y periodo {t}, o historial que discrimine expedientes concurrentes';reason='Código anual único; identidad/CODCLI o atribución entre expedientes no discriminada';solution='Relacionar matrícula anual con expediente exacto; no resolver solo por mayoría ni misma cohorte';evid=ev
   admissions={e[7] for e in idx[k] if e[1]=='MATRICULA' and e[2] in [y,'MAT_'+y] and e[3] in annual};dyears={val(x['ANOINGRESO']) for x in contexts};cohorts['cohorte_concordante_no_prueba_expediente']+=bool(admissions&dyears)
  elif cause=='CODIGO_LOCALIZADO_FALTA_CONTEXTO_DA':
   actual=[x for x in daextra if val(x['CODCLI'])==cli];bad=[]
   if not actual:bad=['CODCLI no localizado en DA12159/11248']
   else:
    for field,test in [('RUT/DV',lambda x:x['REV_RUT_DV']==k),('CODCARPR',lambda x:val(x['CODCARPR'])==c),('SEDE',lambda x:val(x['SEDE'])=='RE'),('JORNADA',lambda x:jm.get(val(x['JORNADA']))==j)]:
     if not any(test(x) for x in actual):bad.append(field)
   reason='Contexto DA no acreditado: '+', '.join(bad or ['combinación conjunta']);missing=f'Fila DA concordante por expediente/carrera/sede/jornada para observación {y}/{t}';solution='Recuperar corte DA o historial de cambio con fecha efectiva; preservar códigos anuales';rule='DA_CLAVE_CONJUNTA_EXACTA';evid=ev
  elif cause=='CODIGO_MISMA_FAMILIA_FILTRO_TEMPORAL':
   reason='Código localizado de misma familia fuera de la matrícula anual exigida por V6';missing=f'Matrícula {y} del expediente, o documento que acredite año académico y plan/expediente en la carga de avance';solution='Verificar año representado por proceso de avance; título posterior acredita evento de titulación, no matrícula retrospectiva';rule='SEPARAR_ANO_CARGA_ACTIVIDAD_TITULACION'
  elif cause=='CODIGO_OTRA_CARRERA_SEDE_JORNADA':
   reason='Códigos históricos corresponden solo a otra carrera/sede/jornada';missing=f'Historial de traslado/cambio con fecha efectiva y CODCLI para {c}/J{j}, {y}/{t}';solution='Acreditar transición; mantener todos los códigos con su contexto sin trasladarlos';rule='NO_TRANSFERIR_ENTRE_FAMILIAS'
  else:
   reason='Código no localizado en índices revisados ni informe individual titulados2025';missing=f'Carga o rectificación individual de {c}/J{j}, {y}/{t}, con identidad y código completo';solution='Localizar entrega institucional o comprobante individual del corte indicado; totales agregados no identifican';rule='AUSENCIA_ACOTADA_NO_CERO'
 if not evid:
  evid=[e for e in idx[k] if e[4]=='COMPLETO']
 provenance=[]
 for e in evid:
  if len(e)==13 and e[1] in ['MATRICULA','AVANCE_CURRICULAR','TITULADOS','RETENCION_DERIVADA']:loc=[e[8],e[9],e[10],e[3],e[1],e[2],e[11]]
  else:loc=[e[7],e[8],e[9],e[6],'MATRICULA',y,e[10]]
  provenance.append(loc);proof.append([i,*loc])
 found='; '.join(sorted({e[3] for e in idx[k] if e[4]=='COMPLETO'}|{e[3] for e in newidx[k] if e[4]=='COMPLETO'}))
 results.append([i,k,cli,c,site,j,plan,y,t,state,cause,previous,observed,found,adopt,newstate,rule,reason,missing,solution,'B dato observado; C conciliación; E plan histórico pendiente',len(provenance),'NO_ACREDITADO'])
 cnt[newstate]+=1;g=group[c,y,j];g[0]+=1;g[1]+=newstate.startswith('CONCILIADO');g[2].add(k)
resolved={r[1] for r in results if r[15].startswith('CONCILIADO')};blocked={r[1] for r in results if not r[15].startswith('CONCILIADO')};full=resolved-blocked;partial=resolved&blocked
stats={'universo_personas':5901,'foco_personas':2317,'foco_observaciones':4973,'estados':dict(cnt),'personas_totalmente_conciliadas_en_foco':len(full),'personas_parcialmente_conciliadas':len(partial),'personas_sin_observacion_conciliada':len(foc-resolved),'personas_con_pendiente':len(blocked),'pendiente_antes_sobre5901':2317/5901,'pendiente_ahora_sobre5901':len(blocked)/5901,'resolucion_es_codigo_observado_no_plan':True,'personas_nuevas_codigo_titulados2025':len(newfound),'titulados2025_filas_leidas':allread,'titulados2025_evidencias_foco':len(titrows),'titulados2025_personas_foco':len(titmatched),'titulados2025_filas_foco':titmatchedrows,'titulados2025_campos_codigo_vacios':allread,'titulados2025_anios_evento':dict(dates),'hipotesis_cohorte':dict(cohorts),'equivalencias_generales_aprobadas':0}
assert len(results)==4973 and full|blocked==foc and not full&blocked
(O/'RESULTADO.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2));(T/'resultados.json').write_text(json.dumps(results,ensure_ascii=False));(T/'evidencias.json').write_text(json.dumps(proof,ensure_ascii=False));(T/'titulados2025.json').write_text(json.dumps(titrows,ensure_ascii=False));(T/'DA_foco.json').write_text(json.dumps(dasheets,ensure_ascii=False))
with open(O/'CARRERA_ANO_JORNADA.csv','w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['Carrera','Ano','Jornada','Observaciones','Conciliadas_codigo','Pendientes','Personas_no_aditivas'])
 for (c,y,j),(n,ok,pp) in sorted(group.items()):w.writerow([c,y,j,n,ok,n-ok,len(pp)])
(O/'FUENTES_NUEVAS.json').write_text(json.dumps({'titulados2025':{'ruta':tit,'sha256':h0,'condicion':'Informe docencia, aceptación SIES no acreditada'},'DA_hashes':dahashes},ensure_ascii=False,indent=2));print(json.dumps(stats,ensure_ascii=False))
