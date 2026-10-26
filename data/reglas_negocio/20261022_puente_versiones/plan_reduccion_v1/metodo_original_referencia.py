import pandas as pd,re,hashlib,json,os
root='/Users/alexi/Documents/GitHub/avance_curricular'; out=root+'/data/reglas_negocio/20261022_puente_versiones'
mu=pd.read_excel(root+'/outputs/base_retencion_matricula_unificada_2022_2026/20260901_142342/BASE_RETENCION_MATRICULA_UNIFICADA_INFORMADA_SIES_2022_2026_20260901_142342.xlsx',sheet_name='BASE_RETENCION_MU',usecols=['N_DOC','DV','COD_SED','COD_CAR','JOR','VERSION'])
pr=pd.read_excel('/Users/alexi/Downloads/PROMEDIOSDEALUMNOS_12166.xlsx',usecols=['RUT','DIG','CODCARR','PLAN_DE_ESTUDIO'])
def key(r,d):
 s=re.sub(r'\D','',str(r)); return s+'-'+str(d).strip().upper() if s else ''
mu['rutkey']=[key(a,b) for a,b in zip(mu.N_DOC,mu.DV)]; pr['rutkey']=[key(a,b) for a,b in zip(pr.RUT,pr.DIG)]
mu['codigo_unico']='I162S'+mu.COD_SED.astype(str)+'C'+mu.COD_CAR.astype(str)+'J'+mu.JOR.astype(str)+'V'+mu.VERSION.astype(str)
cat=pd.read_csv(out+'/PUENTE_VERSIONES_PLAN_UMAS_SIES_20261022.csv')
rows=[]
for dim,g in cat.groupby(['codcarpr_interno','sede','jornada_catalogo']):
 sub=pr[pr.CODCARR.astype(str).str.upper()==dim[0]]; j=sub.merge(mu[['rutkey','codigo_unico']],on='rutkey',how='inner'); j=j[j.codigo_unico.isin(g.codigo_unico_sies_candidato)]
 cc=j.drop_duplicates(['rutkey','PLAN_DE_ESTUDIO','codigo_unico']).groupby('codigo_unico').size().sort_values(ascending=False)
 total=int(cc.sum()); top=int(cc.iloc[0]) if total else 0; proposed=cc.index[0] if total and top/total>=0.9 and top>=3 else ''
 state='PROPUESTA_INTERNA_PREDOMINANTE' if proposed else ('PENDIENTE_MULTIPLE_O_BAJA_COBERTURA' if total else 'PENDIENTE_SIN_MATCH')
 rows.append({'codcarpr_interno':dim[0],'sede':dim[1],'jornada_catalogo':dim[2],'personas_matched':total,'distribucion_versiones':';'.join(f'{k}:{int(v)}' for k,v in cc.items()),'version_propuesta':proposed,'proporcion_predominante':round(top/total,4) if total else None,'estado':state,'clasificacion':'C/D' if proposed else 'E'})
df=pd.DataFrame(rows); path=out+'/DICCIONARIO_VERSIONES_UMAS_SIES_PROPUESTO_20261022.csv'; df.to_csv(path,index=False,encoding='utf-8-sig'); sha=hashlib.sha256(open(path,'rb').read()).hexdigest()
manifest={'recurso':'DICCIONARIO_VERSIONES_UMAS_SIES_PROPUESTO','archivo':os.path.basename(path),'sha256':sha,'fecha':'2026-10-22','fuentes':['PROMEDIOSDEALUMNOS_12166.xlsx','BASE_RETENCION_MU_2022_2026','oferta historica SIES','catalogo 2027'],'regla_propuesta':'Proponer la versión con >=90% de las personas coincidentes y al menos 3 personas; mantener pendientes los demás casos. Regla no aprobada oficialmente.','privacidad':'Agregado sin RUT, nombre ni CODCLI.','estado':'PENDIENTE_APROBACION_GOBERNANZA'}
json.dump(manifest,open(out+'/DICCIONARIO_VERSIONES_UMAS_SIES_PROPUESTO_20261022.manifest.json','w'),ensure_ascii=False,indent=2)
print(df.estado.value_counts().to_dict(),sha)
