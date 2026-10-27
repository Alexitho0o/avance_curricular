from pathlib import Path
import sys,json,re,collections,hashlib,pandas as pd,os
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT));from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento,sha256
props=json.loads(Path('/Users/alexi/.local/share/ipss/revision_42_20261027/REVISION_42.json').read_text())['propuestas'];svc=DiccionarioSiesSeguimiento();assert svc.edicion=='v14_20261027_contextos_42';rem=[]
for p in props:
 x=p['contexto'];v=svc.consultar(persona=x['persona'],codcli=x['CODCLI'],plan=x['plan'],anio=x['ano'],periodo=x['periodo_UMAS'],carrera=x['carrera'])
 if not v.get('codigo_sies'):rem.append(p)
assert len(rem)==7
files=[];frames=[]
for p in Path('/Users/alexi/Library/CloudStorage').glob('OneDrive*/IPSS_CONCILIACION_UMAS_SIES_BASES/03_UMAS_DATOSDEALUMNOS/DATOSDEALUMNOS_*.xlsx'):
 if p.name not in ('DATOSDEALUMNOS_11248.xlsx','DATOSDEALUMNOS_12159.xlsx'):continue
 f=pd.read_excel(p,dtype=str,keep_default_na=False,usecols=['RUT','CODCLI','CODCARPR','JORNADA','SEDE','ANOMATRICULA','PERIODOMATRICULA','ANOINGRESO','PERIODOINGRESO','FECHAMATRICULA','ESTADOACADEMICO','SITUACION']);f['_FUENTE']=p.name;frames.append(f);files.append({'ruta':str(p),'sha256':sha256(p)})
assert len(frames)==2;df=pd.concat(frames,ignore_index=True)
def norm(x):return re.sub('[^0-9K]','',str(x).upper())
def clean(x):return str(x).strip().upper()
def year(x):
 try:return int(float(x))
 except:return None
private=[];stats=collections.Counter();groups=collections.Counter()
for p in rem:
 x=p['contexto'];f=df[df['RUT'].map(norm)==norm(x['persona'])];own=f[f['CODCLI'].map(clean)==x['CODCLI']];other=f[f['CODCLI'].map(clean)!=x['CODCLI']];obs=svc.db.execute('SELECT codcli,payload FROM observaciones WHERE persona=? AND anio=?',(x['persona'],x['ano'])).fetchall();othercode=[]
 for cli,payload in obs:
  row=json.loads(payload);code=row.get('codigo_documental_atribuible') or row.get('codigo_interno_adoptado')
  if cli!=x['CODCLI'] and code==p['codigo']:othercode.append({'CODCLI':cli,'carrera':row['carrera'],'plan':row['plan'],'periodo':row['periodo'],'tipo':row['clasificacion']})
 ownyears=sorted(set(y for y in map(year,own['ANOMATRICULA']) if y));otheryears=sorted(set(y for y in map(year,other['ANOMATRICULA']) if y));ownentry=sorted(set(y for y in map(year,own['ANOINGRESO']) if y));otherentry=sorted(set(y for y in map(year,other['ANOINGRESO']) if y));othercareers=sorted(set(map(clean,other['CODCARPR'])));same=any(y==int(x['ano']) for y in ownyears);stats['propio_mismo_anio_matricula']+=same;stats['anclaje_ambos_expedientes']+=bool(othercode);stats['ambos_expedientes_presentes']+=not own.empty and not other.empty;groups[(x['ano'],x['carrera'],p['motivo'])]+=1
 private.append({'contexto':x,'codigo':p['codigo'],'motivo':p['motivo'],'propio_matricula_anios':ownyears,'otro_matricula_anios':otheryears,'propio_ingreso_anios':ownentry,'otro_ingreso_anios':otherentry,'otras_carreras':othercareers,'otros_exp_codigo':othercode,'filas_datos_alumno_propias':own.to_dict('records'),'filas_datos_alumno_otras':other.to_dict('records')})
svc.close();priv=Path('/Users/alexi/.local/share/ipss/revision_siete_20261027');priv.mkdir(exist_ok=True,parents=True,mode=0o700);target=priv/'RESGUARDO_FECHAS_PLAN.json';assert not target.exists();fd=os.open(target,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
with os.fdopen(fd,'w') as f:json.dump(private,f,ensure_ascii=False,indent=2)
result={'casos':len(rem),'personas':len({p['contexto']['persona'] for p in rem}),'estadisticas':dict(stats),'grupos':[{'anio':k[0],'carrera':k[1],'causa':k[2],'contextos':v} for k,v in groups.items()],'fuentes':files,'limite':'Año de matrícula o ingreso no es fecha efectiva de migración; estados del extracto no son historia. Detalle individual fuera de Git.'};out=Path(__file__).parent;(out/'RESULTADOS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False,indent=2))
