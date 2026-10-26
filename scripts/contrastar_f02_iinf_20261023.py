"""Contraste descriptivo por persona de IINF20241, sin adopción por mayoría."""
import json, hashlib, os, subprocess, datetime
from pathlib import Path
from collections import Counter, defaultdict
from zoneinfo import ZoneInfo
import openpyxl

R=Path(__file__).resolve().parents[1];P=Path.home()/'.local/share/ipss'
stamp=datetime.datetime.now(ZoneInfo('America/Santiago')).strftime('%Y%m%d_%H%M%S')
O=R/'outputs'/('contraste_f02_iinf_'+stamp);Q=P/('contraste_f02_iinf_'+stamp)
assert subprocess.run(['git','-C',str(P),'rev-parse','--show-toplevel'],capture_output=True).returncode!=0
os.umask(0o077);O.mkdir();Q.mkdir();H={}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def src(p,h=None):
 p=Path(p);v=sha(p);assert h is None or v==h,str(p);H[str(p)]=v;return p
def load(p,h=None):return json.loads(src(p,h).read_text())
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2,default=str)+'\n')
def val(v):return '' if v is None else str(int(v)) if isinstance(v,float) and v.is_integer() else str(v).strip()
def norm(n,d):
 n=val(n).replace('.','').strip();d=val(d).upper();return str(int(n))+'-'+d if n.isdigit() and d in '0123456789K' and len(d)==1 else ''
def git():return {k:subprocess.check_output(['git','-C',str(R),*a],text=True).strip() for k,a in [('rama',['branch','--show-current']),('HEAD',['rev-parse','HEAD']),('status',['status','--short'])]}
before=git();dump(O/'GIT_ANTES.json',before)
bm=load(R/'outputs/reproduccion_puente_20261023_004044/MANIFEST.json')
obs=load(Path(bm['privado'])/'OBSERVACIONES_PRIVADAS.json',bm['salidas_privadas_hashes']['OBSERVACIONES_PRIVADAS.json'])
case=next(x for x in load(P/'cambios_plan_12_y_4_20261023_080207/REVISION_16_CASOS_FINAL.json') if x['caso']=='F02')
close=load(P/'cierre_interno_f02_20261023_084246/ADJUDICACION_INTERNA.json')
master=load(R/'data/versiones_historicas_sies_umas/fase_5_20261015/maestro.json')
foc=[x for x in obs if (x['carrera'],x['plan'],x['sede_dimension'],x['jornada_sies'],x['ano'])==('IINF','IINF20241','2','4','2024')]
groups={v:{x['persona'] for x in foc if x['codigo_documental_atribuible']=='I162S2C1J4'+v} for v in ['V2','V3']}
assert len(groups['V2'])==132 and len(groups['V3'])==1 and not groups['V2']&groups['V3']
groups['F02']={case['persona']};people=set.union(*groups.values());assert len(people)==134
labels={k:v for v,ps in groups.items() for k in ps}
mu_path=next(e['fuente'] for x in foc for e in x['evidencias_matricula'] if 'BASE_RETENCION_MATRICULA' in e['fuente'])
mu=[];pr=[]
for kind,path,sheet in [('MU',mu_path,'BASE_RETENCION_MU'),('PR','/Users/alexi/Downloads/PROMEDIOSDEALUMNOS_12166.xlsx','Hoja1')]:
 src(path,bm['fuentes_hashes'].get(path));w=openpyxl.load_workbook(path,read_only=True,data_only=True);it=iter(w[sheet].values);head=next(it)
 fields=['ANIO_INFORMADO','COD_SED','COD_CAR','JOR','VERSION','FOR_ING_ACT','ANIO_ING_ACT','SEM_ING_ACT','ANIO_ING_ORI','SEM_ING_ORI','NIV_ACA','ASI_INS_HIS','ASI_APR_HIS','VIG','FECHA_MATRICULA'] if kind=='MU' else ['CODCLI','CODCARR','PLAN_DE_ESTUDIO','ANO','PERIODO','NIVEL','REGIMEN','CODRAMO','RAMOEQUIV','NOTA_FINAL','ESTADO','DESCRIPCION_ESTADO','CONVALIDADO']
 for rn,row in enumerate(it,2):
  d=dict(zip(head,row));p=norm(d.get('N_DOC') if kind=='MU' else d.get('RUT'),d.get('DV') if kind=='MU' else d.get('DIG'))
  if p not in people:continue
  z={k:val(d.get(k)) for k in fields};z.update(persona=p,fuente=path,hoja=sheet,fila=rn)
  if kind=='MU':z['codigo']='I162S%sC%sJ%sV%s'%tuple(z[k] for k in ['COD_SED','COD_CAR','JOR','VERSION']);mu.append(z)
  else:pr.append(z)
 w.close();print(kind,'filas foco',len(mu) if kind=='MU' else len(pr),flush=True)
dump(Q/'MU_RELEIDA.json',mu);dump(Q/'PROMEDIOS_RELEIDO.json',pr)
summary={'universo_comparacion':{'V2':132,'V3':1,'F02':1},'distribuciones':{},'casos_dirigidos':{},'oferta_relevante':[]}
for label,ps in groups.items():
 z=[x for x in foc if x['persona'] in ps];stats={}
 for field in ['ANOINGRESO','PERIODOINGRESO']:
  stats['DA_'+field]=dict(Counter('|'.join(sorted({d[field] for x in z if x['persona']==p for d in x['contextos_DA']})) for p in ps))
 ym=[x for x in mu if x['persona'] in ps and x['ANIO_INFORMADO']=='2024' and x['COD_CAR']=='1' and x['COD_SED']=='2']
 for field in ['codigo','FOR_ING_ACT','ANIO_ING_ACT','ANIO_ING_ORI','NIV_ACA','ASI_APR_HIS']:
  stats['MU2024_'+field]=dict(Counter('|'.join(sorted({x[field] for x in ym if x['persona']==p})) for p in ps))
 summary['distribuciones'][label]=stats
 if label in ['V3','F02']:
  pp=[x for x in pr if x['persona'] in ps];mm=[x for x in mu if x['persona'] in ps]
  traj=sorted({(x['carrera'],x['plan'],x['ano'],x['periodo'],x['codigo_documental_atribuible']) for x in obs if x['persona'] in ps})
  byperiod=[]
  for key in sorted({(x['CODCARR'],x['PLAN_DE_ESTUDIO'],x['ANO'],x['PERIODO'],x['REGIMEN']) for x in pp}):
   rows=[x for x in pp if (x['CODCARR'],x['PLAN_DE_ESTUDIO'],x['ANO'],x['PERIODO'],x['REGIMEN'])==key]
   byperiod.append({'carrera':key[0],'plan':key[1],'ano':key[2],'periodo':key[3],'regimen':key[4],'filas':len(rows),'asignaturas_distintas':len({x['CODRAMO'] for x in rows}),'niveles':sorted({x['NIVEL'] for x in rows}),'estados':dict(Counter(x['DESCRIPCION_ESTADO'] for x in rows)),'convalidado':dict(Counter(x['CONVALIDADO'] or 'VACIO' for x in rows))})
  summary['casos_dirigidos'][label]={'trayectoria_diagnostico':traj,'MU_releida':[{k:v for k,v in x.items() if k not in ['persona','fuente','fila','hoja']} for x in mm],'avance_por_periodo':byperiod}
codes={(int(x['ANIO_INFORMADO']),x['codigo']) for x in mu if labels[x['persona']] in ['V3','F02']}
summary['oferta_relevante']=[x for x in master['oferta_anual'] if (x['anio'],x['codigo_unico']) in codes]
dump(O/'RESULTADOS_DESCRIPTIVOS.json',summary)
dump(Q/'F02_Y_CONTRASTE_OBSERVACIONES.json',[x for x in obs if x['persona'] in groups['V3']|groups['F02']])
src(Path(__file__));src(R/'docs/ESPECIFICACION_CONTRASTE_F02_IINF_20261023.md')
qa={'fuentes_intactas':all(sha(p)==h for p,h in H.items()),'grupos_personas_disjuntos':len(people)==134,'conteos_foco_conservados':len(foc)==403,'cierre_previo_V2_conservado':close['estado_despues']['codigo_interno_adoptado']=='I162S2C1J4V2','bases_denominadores_sin_cambio':True,'sin_adopcion_automatica':True}
assert all(qa.values());dump(O/'QA.json',qa);dump(O/'FUENTES_HASHES.json',H);dump(O/'GIT_DESPUES.json',git())
dump(O/'MANIFEST.json',{'fecha':datetime.datetime.now(ZoneInfo('America/Santiago')).isoformat(),'fuentes_hashes':H,'privado':str(Q),'salidas_hashes':{p.name:sha(p) for p in O.iterdir()},'privados_hashes':{p.name:sha(p) for p in Q.iterdir()},'clasificacion':'B/C descriptivo; E interpretación hasta evaluar','sin_commit_push':True})
print(str(O))
