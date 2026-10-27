from pathlib import Path
import json,sys,collections,pandas as pd,re,hashlib,openpyxl
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento,sha256
p=Path('/Users/alexi/.local/share/ipss/revision_42_20261027/REVISION_42.json');props=json.loads(p.read_text())['propuestas'];assert len(props)==42
svc=DiccionarioSiesSeguimiento();assert svc.edicion=='v14_20261027_contextos_42';remaining=[]
for p in props:
 x=p['contexto'];v=svc.consultar(persona=x['persona'],codcli=x['CODCLI'],plan=x['plan'],anio=x['ano'],periodo=x['periodo_UMAS'],carrera=x['carrera']);
 if not v.get('codigo_sies'):remaining.append(p)
assert len(remaining)==7
man=json.loads((ROOT/'outputs/avance_historico_origen_h113_20261027/MANIFEST_ORIGEN_H113.json').read_text());source=Path(man['fuentes']['promedios']['ruta']);assert sha256(source)==man['fuentes']['promedios']['sha256'];cols=['RUT','DIG','CODCLI','CODCARR','JORNADA','PLAN_DE_ESTUDIO','ANO','PERIODO','ESTADO'];df=pd.read_excel(source,sheet_name='Hoja1',dtype=str,keep_default_na=False,usecols=cols)
def norm(x):return str(x).strip().upper()
def bod(x):return re.sub(r'[.\s]','',norm(x))
def num(x):
 try:return str(int(float(x)))
 except:return ''
df['_id']=df['RUT'].map(bod)+'-'+df['DIG'].map(bod)
p=next(Path('/Users/alexi/Library/CloudStorage').glob('OneDrive*/RESPALDO SIES ENVIADO POR CARLOS ARAVENA EL 24-9/2025/Matricula/SIES/06-05-2025/IPSS_Procesamiento.xlsx'));assert sha256(p)=='e2984ccdf22ecf35c46e1f77275fdd12cda47bd2d77a523860e2cd2cf90127f4'
w=openpyxl.load_workbook(p,read_only=True,data_only=True);it=w['2025_carga'].iter_rows(values_only=True);next(it);idx=collections.defaultdict(list)
for row in it:
 row=tuple(row)+(None,)*115;doc=bod(row[72])+'-'+bod(row[73]);idx[doc].append({'carrera':norm(row[1]),'jornada':norm(row[8])})
w.close();profiles=[];private=[]
for i,p in enumerate(remaining,1):
 x=p['contexto'];pe=x['persona'];cli=x['CODCLI'];year=x['ano'];same=df[(df['_id']==pe)&(df['ANO'].map(num)==year)];student=same[same['CODCLI'].map(norm)==cli];other=same[same['CODCLI'].map(norm)!=cli];own=collections.Counter((norm(a),norm(b),norm(c),num(d)) for a,b,c,d in zip(student['CODCARR'],student['PLAN_DE_ESTUDIO'],student['JORNADA'],student['PERIODO']));alternatives=collections.Counter((norm(a),norm(b),norm(c),num(d)) for a,b,c,d in zip(other['CODCARR'],other['PLAN_DE_ESTUDIO'],other['JORNADA'],other['PERIODO']));annual=svc.codigos_mu(persona=pe,anio=year);assert annual['codigos']==[p['codigo']]
 records=svc.db.execute('SELECT codcli,payload FROM observaciones WHERE persona=? AND anio=?',(pe,year)).fetchall();othercode=collections.Counter()
 for c,v in records:
  r=json.loads(v);code=r.get('codigo_documental_atribuible') or r.get('codigo_interno_adoptado');
  if c!=cli and code==p['codigo']:othercode[(r.get('carrera'),r.get('plan'),str(r.get('periodo')),r.get('clasificacion'))]+=1
 profile={'estados_ramo':dict(collections.Counter(norm(y) for y in student['ESTADO'])),'caso':'P%02d'%i,'motivo_previo':p['motivo'],'anio':year,'periodo':x['periodo_UMAS'],'carrera':x['carrera'],'plan':x['plan'],'jornada':x['jornada_UMAS'],'codigo':p['codigo'],'actividad_expediente':[{'carrera':k[0],'plan':k[1],'jornada':k[2],'periodo':k[3],'filas':v} for k,v in sorted(own.items())],'actividad_otros_expedientes':[{'carrera':k[0],'plan':k[1],'jornada':k[2],'periodo':k[3],'filas':v} for k,v in sorted(alternatives.items())],'otros_codcli_con_codigo':[{'carrera':k[0],'plan':k[1],'periodo':k[2],'clasificacion':k[3],'observaciones':v} for k,v in sorted(othercode.items())],'preparacion_2025':idx.get(pe,[]) if year=='2025' else [],'estado':'PENDIENTE'}
 profiles.append(profile);private.append({'alias':profile['caso'],'propuesta':p})
svc.close();out=Path('/Users/alexi/.local/share/ipss/revision_siete_20261027');(out/'PERFILES_PRIVADOS.json').write_text(json.dumps(profiles,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'casos':len(profiles),'personas':len({p['contexto']['persona'] for p in remaining}),'expedientes':len({(p['contexto']['persona'],p['contexto']['CODCLI']) for p in remaining}),'estados_ramo':dict(collections.Counter(s for x in profiles for s in x['estados_ramo']))},ensure_ascii=False))
