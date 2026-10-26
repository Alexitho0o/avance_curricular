"""Reaplica el método gobernado a pendientes V7; detalle solo local privado."""
import json,hashlib,csv,sys,re
from pathlib import Path
from collections import defaultdict,Counter
import openpyxl
R=Path.cwd();sys.path.insert(0,str(R))
from common.versiones_por_cohorte import resolver_cohorte
from common.continuidad_trayectoria import resolver_version_trayectoria
O=R/'outputs/retencion_puente_provisional_20261023_v8';T=Path('/tmp/ipss_cruce_historico_20261023');load=lambda p:json.load(open(p));sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();hashes={}
def read(p):hashes[str(p)]=sha(p);return load(p)
B=R/'data/versiones_por_cohorte/20261016';manifest=load(B/'manifest.json')
for n in ['grupos_existentes.json','historias_oferta.json']:assert sha(B/n)==manifest['salidas'][n]
groups={(g['codcarpr'],g['sede'],g['jornada']):g for g in read(B/'grupos_existentes.json')};hist=read(B/'historias_oferta.json');master=read(R/'data/versiones_historicas_sies_umas/fase_5_20261015/maestro.json');bycode={h['codigo_unico']:h for h in hist}
rows=[r for r in read('/tmp/ipss_resolucion_2317_20261022/resultados.json') if not r[14]];people={r[1] for r in rows};assert len(rows)==3213 and len(people)==1838
p=read('/tmp/ipss_revision_63_20261022/payload.json');get=lambda n:next(s['rows'] for s in p if s['name']==n)
evidence=defaultdict(list)
for e in get('EVIDENCIAS_SIES'):
 if e[0] in people and e[4]=='COMPLETO':evidence[e[0]].append(e)
da=defaultdict(list);dasheets=[];jm={'1':'D','2':'V','4':'O'};val=lambda v:'' if v is None else str(int(v)) if isinstance(v,float) and v.is_integer() else str(v).strip()
for s in p:
 if not s['name'].startswith('DA_'):continue
 h=s['headers'];filtered=[]
 for r in s['rows']:
  x=dict(zip(h,r));k=x['REV_RUT_DV']
  if k not in people:continue
  filtered.append(r);da[k,val(x['CODCLI']),val(x['CODCARPR']),val(x['JORNADA'])].append(x)
 dasheets.append({**s,'rows':filtered})
# Actividad propia de carrera sin homologaciones: exactamente regla16oct.
needed={(r[1],r[2],r[3]) for r in rows};pr=Path('/Users/alexi/Downloads/PROMEDIOSDEALUMNOS_12166.xlsx');hashes[str(pr)]=sha(pr);academic=defaultdict(set);academic_refs=defaultdict(dict);excluded=Counter();w=openpyxl.load_workbook(pr,read_only=True,data_only=True);ws=w.active;it=iter(ws.values);header=next(it);scanned=0;matched=0
for rn,row in enumerate(it,2):
 scanned+=1;x=dict(zip(header,row));rawrut=val(x.get('RUT')).replace('.','').replace(' ','');dv=val(x.get('DIG')).upper();pk=str(int(rawrut))+'-'+dv if rawrut.isdigit() and re.fullmatch('[0-9K]',dv) else None
 ck=(pk,val(x.get('CODCLI')),val(x.get('CODCARR')))
 if ck not in needed:continue
 matched+=1;state=val(x.get('DESCRIPCION_ESTADO')).upper();con=val(x.get('CONVALIDADO')).upper();year=val(x.get('ANO'))
 if state not in {'APROBADO','REPROBADO'} or con in {'S','SI','SÍ','1','TRUE'}:excluded['estado_o_convalidacion']+=1;continue
 if year.isdigit() and 2007<=int(year)<=2026:academic[ck].add(int(year));academic_refs[ck].setdefault(int(year),[str(pr),ws.title,rn])
w.close();assert sha(pr)==hashes[str(pr)]
# Fecha mínima observada de misma persona/carrera, sin trasladar del técnico.
obs=defaultdict(set);obsrefs=defaultdict(list)
for (k,cli,c,j),ds in da.items():
 for x in ds:
  yy=val(x['ANOMATRICULA'])
  if yy.isdigit() and 2007<=int(yy)<=2026:obs[k,c].add(int(yy));obsrefs[k,c].append([int(yy),x['REV_FUENTE'],x['REV_HOJA'],x['REV_FILA'],'ANOMATRICULA'])
 for yy in academic[k,cli,c]:obs[k,c].add(yy);obsrefs[k,c].append([yy,*academic_refs[k,cli,c][yy],'ACTIVIDAD_NO_CONVALIDADA'])
mrun=defaultdict(set)
for x in master['mrun_anual']:mrun[x['codigo_unico']].add(int(x['cat_periodo']))
result=[];candidates=[];dates=[];fullresults=[];counts=Counter();cross=Counter();agg=defaultdict(lambda:[0,set()])
for r in rows:
 rid,k,cli,c,site,j,plan,y,t=r[:9];g=groups.get((c,'RE',jm.get(j)));ds=da[k,cli,c,jm.get(j)];years=sorted({int(val(d['ANOINGRESO'])) for d in ds if val(d['ANOINGRESO']).isdigit()});types={p[1] for p in g['perfiles_duracion_tipo']} if g else set();continuity=types=={'3'};first=min(obs[k,c]) if obs[k,c] else None
 ingress=years[0] if len(years)==1 else None
 rr=resolver_version_trayectoria(g,hist,anoingreso=ingress,anio_inicio_carrera=first,fecha_confirmada=False)
 if len(years)>1 and not continuity:rr={'estado':'ANOINGRESO_DIVERGENTE_ENTRE_CORTES','codigo_propuesto':None,'habilitada_carga_oficial':False}
 refyear=first if continuity else ingress;code=rr.get('codigo_propuesto') or '';family=set(g['familias']) if g else set();profiles={tuple(p) for p in g['perfiles_duracion_tipo']} if g else set();allh=[h for h in hist if h['familia'] in family];exactref=[];exactobs=[]
 for h in allh:
  for label,yy in [('REFERENCIA',refyear),('OBSERVACION',int(y))]:
   annual=next((a for a in h['anual'] if a['anio']==yy),None);profileok=bool(annual and (annual['duracion_total'],annual['tipo_plan']) in profiles)
   if profileok:(exactref if label=='REFERENCIA' else exactobs).append(h['codigo_unico'])
   candidates.append([rid,h['codigo_unico'],label,yy,h['inicio_oferta'],min(mrun[h['codigo_unico']]) if mrun[h['codigo_unico']] else None,min(z['inicio_oferta'] for z in hist),annual['duracion_total'] if annual else '',annual['tipo_plan'] if annual else '',annual['modalidad'] if annual else '',bool(annual),profileok,annual['registro_csv'] if annual else None,h['codigo_unico']==code,'historias_oferta.json; perfiles_sies_anuales.json'])
 personal=[e for e in evidence[k] if e[1]=='MATRICULA' and e[3]==code] if code else [];annualpersonal=[e for e in personal if e[2] in [y,'MAT_'+y]]
 sameother=[e for e in evidence[k] if e[1]=='MATRICULA' and e[3].rsplit('V',1)[0] in family and e[3]!=code] if code else []
 compatible=code in exactref if code else False
 status=('PROPUESTA_INICIO_COINCIDENTE' if rr['estado']=='COINCIDENCIA_INICIO' else 'PROPUESTA_INTERVALO_NO_ACREDITADO' if rr['estado']=='INTERVALO_PROPUESTO' else 'BLOQUEADO_'+rr['estado'])
 if code and not compatible:status='PROPUESTA_SIN_OFERTA_DEL_ANO_REFERENCIA'
 if not g:missing='Grupo CODCARPR/sede/jornada gobernado'
 elif not profiles:missing='Duración total y tipo de plan propios del programa, con fuente gobernada'
 elif len(exactref)>1:missing='Atributo discriminante entre versiones simultáneas: modalidad/nivel/perfil documentado o código personal contextual; duración/tipo/año no bastan'
 elif continuity:missing='Fecha efectiva de ingreso a continuidad y asignación plan/expediente; mínimo observado no la acredita'
 elif len(years)!=1:missing='Año de ingreso propio del expediente concordante entre cortes'
 elif code:missing='Acreditar relación individual del expediente/plan con candidato; inicio/intervalo de oferta no prueba matrícula personal'
 else:missing='Resolver desfase de cohorte/perfil frente a cobertura de oferta; no renumerar versión ni elegir código por nombre'
 if annualpersonal:missing='Código anual existe; resolver atribución de expediente o contexto DA pendiente V7'
 dates.append([rid,'; '.join(map(str,years)),first,'NO_CONFIRMADA',json.dumps(obsrefs[k,c],ensure_ascii=False),json.dumps([[d['REV_FUENTE'],d['REV_HOJA'],d['REV_FILA'],'ANOINGRESO',val(d['ANOINGRESO'])] for d in ds],ensure_ascii=False)])
 result.append([rid,k,cli,c,site,j,plan,y,t,r[10],g['fuente_perfil'] if g else '',json.dumps(sorted(profiles)),continuity,'; '.join(map(str,years)),first,refyear,'MINIMO_OBSERVADO_CARRERA' if continuity else 'ANOINGRESO_UMAS_CORTE',rr['estado'],status,code,'; '.join(sorted(set(exactref))),'; '.join(sorted(set(exactobs))),bool(personal),bool(annualpersonal),bool(sameother),bool(code and refyear in mrun[code]),'', 'PENDIENTE_DOCUMENTAL_V7',missing,'E propuesta / C cálculo; no código informado individual ni plan acreditado'])
 fullresults.append({'observacion_id':rid,'resolucion':rr,'candidatos_anio_referencia':sorted(set(exactref)),'candidatos_anio_observacion':sorted(set(exactobs))})
 counts[status]+=1;cross['candidato_unico_perfil_en_anio_referencia']+=len(set(exactref))==1;cross['multiples_perfil_en_anio_referencia']+=len(set(exactref))>1;cross['sin_perfil_en_anio_referencia']+=not exactref;cross['propuesta_con_MU_personal_otro_o_mismo_ano']+=bool(personal);cross['propuesta_con_MU_personal_ano_observacion']+=bool(annualpersonal);cross['propuesta_con_MU_agregado_referencia']+=bool(code and refyear in mrun[code]);cross['continuidad_fecha_solo_observada']+=continuity and first is not None;cross['fecha_referencia_posterior_actividad']+=refyear is not None and refyear>int(y)
 a=agg[c,j,y,status];a[0]+=1;a[1].add(k)
assert len(result)==3213 and len({r[1] for r in result})==1838
summary={'observaciones_foco':3213,'personas_foco':1838,'universo_personas':5901,'estados':dict(counts),'controles':dict(cross),'nuevas_conciliaciones_documentales':0,'personas_completamente_resueltas':0,'personas_parcialmente_resueltas':0,'pendiente_observaciones':3213,'pendiente_personas':1838,'pendiente_sobre5901':1838/5901,'nuevas_equivalencias_generales':0,'promedios_filas_leidas':scanned,'promedios_filas_expedientes_foco':matched,'exclusiones_regla_continuidad':dict(excluded),'clasificacion':'C método gobernado; E propuestas no acreditación personal'}
for n,x in [('resultados.json',result),('candidatos.json',candidates),('fechas.json',dates),('metodo_completo.json',fullresults),('DA_foco.json',dasheets)]: (T/n).write_text(json.dumps(x,ensure_ascii=False))
(O/'RESULTADO.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
with open(O/'DESGLOSE.csv','w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['Carrera','Jornada','Ano','Estado','Observaciones','Personas_no_aditivas'])
 for key,(n,pp) in sorted(agg.items()):w.writerow([*key,n,len(pp)])
for pth in ['common/versiones_por_cohorte.py','common/continuidad_trayectoria.py','docs/continuidad_trayectoria_20261016.md']:hashes[str(R/pth)]=sha(R/pth)
assert all(sha(p)==h for p,h in hashes.items());(O/'FUENTES_HASHES.json').write_text(json.dumps(hashes,ensure_ascii=False,indent=2));print(json.dumps(summary,ensure_ascii=False))
