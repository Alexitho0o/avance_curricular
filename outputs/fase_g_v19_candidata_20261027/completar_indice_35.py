"""Construye índice privado aditivo para 218 contextos sin modificar v17."""
from pathlib import Path
from collections import defaultdict,Counter
import json,hashlib,sqlite3,sys,os,re,unicodedata,datetime
import openpyxl
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento,sha256
OUT=Path(__file__).parent;PRIVATE=Path('/Users/alexi/.local/share/ipss/fase_g_v19_candidata_20261027');target=PRIVATE/'INDICE_COMPLEMENTARIO_35.sqlite'
assert not PRIVATE.resolve().is_relative_to(ROOT) and not target.exists();PRIVATE.mkdir(parents=True,exist_ok=True,mode=0o700);PRIVATE.chmod(0o700)
descriptor=ROOT/'data/diccionario_sies_seguimiento/v19_20261027_candidata_fase_g/descriptor.json';svc=DiccionarioSiesSeguimiento(descriptor=descriptor);descriptor_hash=sha256(descriptor);base_hash=svc.descriptor['base_privada']['sha256'];rows=[r for r in svc.db.execute('select id,persona,codcli,plan,anio,periodo,carrera,sede,jornada from observaciones') if r[0]>27148];assert len(rows)==35 and len({r[0] for r in rows})==35
rows_by_context=defaultdict(list);owners=defaultdict(list)
for oid,pe,cli,plan,year,period,car,sede,jor in rows:
 rows_by_context[(pe,cli,plan,car,year,period)].append(oid);owners[(pe,cli)].append(oid)
cat=json.loads((ROOT/'data/catalogo_fuentes/CATALOGO_FUENTES.json').read_text());allcat={e['archivo']:e for e in cat['catalogo'] if e.get('categoria')=='04_UMAS_PROMEDIOSDEALUMNOS'};meta=json.loads((ROOT/svc.descriptor['capa_promedios']['metadata']).read_text())
sources={}
for name in ('PROMEDIOSDEALUMNOS_7804.xlsx','PROMEDIOSDEALUMNOS_12166.xlsx','PROMEDIOSDEALUMNOS_3233.xlsx'):
 entry=allcat[name];p=Path(unicodedata.normalize('NFD',entry['ruta_consolidada']));sources[name]={'ruta':str(p),'sha256':entry['sha256'],'hoja':'Hoja1'}
expanded=meta['fuentes']['respaldo_ampliado'];sources['PROMEDIOS_7804_AMPLIADO']={'ruta':expanded['ruta'],'sha256':expanded['sha256'],'hoja':'Hoja1'}
for name in ('foto_2026_2','foto_2026_3'):sources[name]=meta['fuentes'][name]
def clean(x):
 if x is None:return ''
 if isinstance(x,(float,int)) and int(x)==x:return str(int(x))
 return str(x).strip().upper()
def persona(x,dv):
 b=clean(x).replace('.','').replace(' ','');v=clean(dv)
 if '-' in b:b,v=b.split('-',1)
 return str(int(b))+'-'+v if b.isdigit() and re.fullmatch('[0-9K]',v) else ''
contexts={r[0]:{'observacion_id':r[0],'promedios':{},'estado_extracto_12166':None,'fotos':{},'alertas':[]} for r in rows};history=defaultdict(lambda:defaultdict(set));course=defaultdict(lambda:defaultdict(list));source_qa={}
for name,src in sources.items():
 p=Path(src['ruta']);actual=sha256(p);assert actual==src['sha256'], 'Hash fuente distinto: '+name
 wb=openpyxl.load_workbook(p,read_only=True,data_only=True);ws=wb[src['hoja']];it=ws.iter_rows(values_only=True);heads={clean(v):i for i,v in enumerate(next(it)) if v is not None};total=0;invalid=0
 for lineno,row in enumerate(it,2):
  total+=1
  def v(k):return clean(row[heads[k]]) if k in heads and heads[k]<len(row) else ''
  pe=persona(v('RUT'),v('DIG'));cli=v('CODCLI')
  if (pe,cli) not in owners:continue
  if name.startswith('foto_'):
   for oid in owners[(pe,cli)]:
    yr,per=name[-6:-2],name[-1];obs=next(t for t in rows if t[0]==oid)
    if (obs[4],obs[5])==(yr,per):contexts[oid]['fotos'].setdefault(name,[]).append({'hoja':src['hoja'],'fila':lineno,'estado':v('ESTADOACADEMICO') or None,'tiene_estado':'ESTADOACADEMICO' in heads})
   continue
  year=v('ANO');per=v('PERIODO')
  if not year.isdigit() or not per.isdigit():invalid+=1;continue
  if name=='PROMEDIOSDEALUMNOS_12166.xlsx':history[(pe,cli)][(int(year),int(per))].add(v('ESTADO_ACADEMICO'))
  key=(pe,cli,v('PLAN_DE_ESTUDIO'),v('CODCARR'),year,per)
  for oid in rows_by_context.get(key,[]):
   item={'fila':lineno,'jornada':v('JORNADA'),'asignatura':v('CODRAMO'),'seccion':v('CODSECC'),'nota':v('NOTA_FINAL'),'estado_asignatura':v('ESTADO'),'estado_academico_extracto':v('ESTADO_ACADEMICO')}
   contexts[oid]['promedios'].setdefault(name,[]).append(item);course[(oid,item['asignatura'])][name].append(item)
 wb.close();assert sha256(p)==actual;source_qa[name]={'ruta':str(p),'sha256':actual,'hoja':src['hoja'],'filas_leidas':total,'filas_clave_invalida_en_foco':invalid,'fuente_corte_no_certificado':True}
for oid,pe,cli,plan,year,period,car,sede,jor in rows:
 ctx=contexts[oid];periods=history.get((pe,cli),{})
 if periods:
  latest=max(periods);v=periods[latest];nonempty={z for z in v if z};ctx['estado_extracto_12166']={'ano_ultimo_observado':latest[0],'periodo_ultimo_observado':latest[1],'estado':next(iter(nonempty)) if len(nonempty)==1 and '' not in v else None,'observacion':'Estado del extracto; no acredita estado histórico ni fecha de cierre.'}
 for (id_,subject),sources_ in course.items():
  if id_!=oid or not subject or len(sources_)<2:continue
  signatures={name:{(v['seccion'],v['nota'],v['estado_asignatura'],v['estado_academico_extracto']) for v in items} for name,items in sources_.items()}
  if len({str(sorted(x)) for x in signatures.values()})>1:ctx['alertas'].append({'tipo':'DIFERENCIA_EXTRACTOS_ASIGNATURA','asignatura':subject,'fuentes':sorted(signatures),'detalle':{k:sorted(v) for k,v in signatures.items()}})
 for name in ('foto_2026_2','foto_2026_3'):
  if name not in ctx['fotos']:ctx['fotos'][name]=[]
 ctx['limite_fotos']='Solo se compara mismo año/período; sin coincidencia no implica abandono.'
svc.close()
fd=os.open(target,os.O_CREAT|os.O_EXCL|os.O_RDWR,0o600);os.close(fd);db=sqlite3.connect(target);db.execute('CREATE TABLE indice (observacion_id INTEGER PRIMARY KEY, payload TEXT NOT NULL)')
for oid in sorted(contexts):db.execute('INSERT INTO indice VALUES (?,?)',(oid,json.dumps(contexts[oid],ensure_ascii=False)))
db.commit();assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok';assert db.execute('SELECT COUNT(*),COUNT(DISTINCT observacion_id) FROM indice').fetchone()==(35,35);db.close()
coverage={name:sum(bool(c['promedios'].get(name)) for c in contexts.values()) for name in sources if name.startswith('PROMEDIOS')};photos={name:sum(bool(c['fotos'][name]) for c in contexts.values()) for name in ('foto_2026_2','foto_2026_3')};stats={'contextos_objetivo':35,'indice_registros':35,'sin_duplicados':True,'cobertura_actividad_por_fuente':coverage,'cobertura_fotos_periodo_coincidente':photos,'con_estado_extracto_12166':sum(c['estado_extracto_12166'] is not None for c in contexts.values()),'con_alertas_de_asignatura':sum(bool(c['alertas']) for c in contexts.values()),'con_al_menos_una_fuente_actividad':sum(bool(c['promedios']) for c in contexts.values()),'sin_fuente_actividad':sum(not c['promedios'] for c in contexts.values()),'fuentes':source_qa,'descriptor_candidata_sha256':descriptor_hash,'base_candidata_sha256':base_hash,'indice_privado':{'ruta':str(target),'sha256':sha256(target)},'clase':'B/C/E','limites':['Índice añadido a la candidata, sin alterar v17.','Estado es del extracto, no histórico; fecha y cobertura no certificadas.','Foto sin correspondencia no indica ausencia o deserción.','Comparación de registros de asignatura no identifica causa de discrepancia.']}
assert sha256(descriptor)==descriptor_hash and sha256(Path(svc.descriptor['base_privada']['ruta']))==base_hash
(OUT/'QA_INDICE_35.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in stats.items() if k not in ('fuentes','indice_privado')},ensure_ascii=False,indent=2))
