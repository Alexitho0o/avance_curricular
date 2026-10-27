from pathlib import Path
import pandas as pd,re,json,collections,hashlib
p=Path(__file__).parent/'reconstruir_107.py';s=p.read_text().split("out=collections.Counter(); examples=[]")[0];n={};exec(compile(s,str(p),'exec'),n)
cs=[c for c in n['candidates'] if any(x['plan']==c['key'][2] and x['carrera']==c['key'][3] and (x.get('codigo_documental_atribuible') or x.get('codigo_interno_adoptado'))==c['mu_codes'][0] for x in n['n']['byexp'][(c['key'][0],c['key'][1])])]
assert len(cs)==89
paths=[]
for p in Path('/Users/alexi/Library/CloudStorage').glob('OneDrive*/IPSS_CONCILIACION_UMAS_SIES_BASES/03_UMAS_DATOSDEALUMNOS/DATOSDEALUMNOS_*.xlsx'):
 if p.name in ('DATOSDEALUMNOS_11248.xlsx','DATOSDEALUMNOS_12159.xlsx'):paths.append(p)
assert len(paths)==2
frames=[];meta=[]
for p in paths:
 f=pd.read_excel(p,dtype=str,keep_default_na=False,usecols=['CODCLI','CODCARPR','JORNADA','RUT','SEDE','ANOMATRICULA','PERIODOMATRICULA']);f['_source']=p.name;frames.append(f);meta.append({'archivo':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'filas':len(f)})
df=pd.concat(frames,ignore_index=True)
def norm(x):return re.sub(r'[^0-9K]','',str(x).upper())
def clean(x):return str(x).strip().upper()
counts=collections.Counter();details=[]; intersection=collections.Counter(); prom=n['n']['h']; body=n['n']['body']; cl=n['n']['clean']; strict=n['n']['strict']
for c in cs:
 pe,cli,pl,ca,jo,an,period=c['key'];code=c['mu_codes'][0];person=norm(pe)
 rows=df[df['CODCLI'].map(clean).eq(cli)];identity=rows[rows['RUT'].map(norm).eq(person)];pair=identity[identity['CODCARPR'].map(clean).eq(ca)&identity['JORNADA'].map(clean).eq(jo)]
 sede=code.split('S',1)[1].split('C',1)[0];paired=pair[pair['SEDE'].map(clean).isin({'2':['RE','2'],'3':['CO','3'],'4':['PTG','4']}.get(sede,[]))]
 sameyear=paired[paired['ANOMATRICULA'].map(clean).eq(an)]
 k='IDENTIDAD_CARRERA_JORNADA_SEDE_ANIO_MATRICULA' if len(sameyear) else ('IDENTIDAD_CARRERA_JORNADA_SEDE_SIN_ANIO_MATRICULA' if len(paired) else ('IDENTIDAD_SIN_COINCIDENCIA_DIMENSIONES' if len(identity) else ('CODCLI_SIN_RUT_DV' if len(rows) else 'CODCLI_NO_LOCALIZADO')))
 counts[k]+=1
 obs=n['n']['byexp'][(pe,cli)];othercli=any(x.get('codigo_documental_atribuible')==code or x.get('codigo_interno_adoptado')==code for (pp,cc),rr in n['n']['byexp'].items() if pp==pe and cc!=cli for x in rr if str(x['ano'])==an)
 if othercli:counts['ALERTA_OTRO_EXPEDIENTE']+=1
 candidates_raw=prom.loc[strict.get(tuple(pe.split('-')),[])]
 same=candidates_raw[(candidates_raw['CODCLI'].map(cl)==cli)&(candidates_raw['_ANO_NUM']==int(an))]
 contexts={(cl(a),cl(b),cl(c)) for a,b,c in zip(same['PLAN_DE_ESTUDIO'],same['CODCARR'],same['JORNADA'])}
 alternatives=contexts-{(pl,ca,jo)}
 if alternatives:counts['ALERTA_OTRO_CONTEXTO_PROMEDIOS_MISMO_ANIO']+=1
 intersection[k+(' / alerta' if othercli or alternatives else ' / sin alerta')]+=1
 if len(details)<5:details.append({'carrera':ca,'plan':pl,'anio':an,'periodo':period,'codigo':code,'estado':k,'otro_expediente':othercli})
result={'contextos':len(cs),'resultados':dict(counts),'particion_alertas':dict(intersection),'fuentes':meta,'ejemplos_sin_identificadores':details,'limite':'Datos Alumnos carece de plan; ancla de otro año no acredita vigencia. No se hicieron atribuciones.'}; (Path(__file__).parent/'RESULTADOS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n'); print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)
