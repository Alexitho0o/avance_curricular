from pathlib import Path
import json,hashlib
from collections import Counter,defaultdict
ROOT=Path.cwd();B=ROOT/'data/reglas_negocio/20261022_puente_versiones';OUT=B/'diagnostico_casi_completos_v3'
# Reutilizar únicamente carga e índices privados en memoria, sin ejecutar escrituras V3.
script=(B/'investigacion_contextual_v3/probar_contextos.py').read_text();exec(compile(script.split('result=[];context_rows=[]')[0],'<carga_local_reutilizada>','exec'))
targets=[('NCONRE','2'),('NICCRE','2'),('NINFRE','2'),('TPCRE','1'),('TPCRE','2')];missing={};details=[]
for c,j in targets:
 fam=set(gm[c,'RE',revj[j]]['familias']);units=pr[c,j];bad=[];da_bad=[]
 for k,cli,p,y,t in units:
  if not any(v[0].rsplit('V',1)[0] in fam for v in refs[k,y]):bad.append((k,cli,p,y,t));missing[c,j,k,cli,p,y,t]=True
  if not any(v[0]==k and v[1]=='RE' and v[2]==j for v in da.get((cli,c),set())):da_bad.append((k,cli,p,y,t))
 groups=Counter((p,y,t) for k,cli,p,y,t in bad)
 details.append({'carrera':c,'jornada':j,'faltantes':[{'plan':p,'ano':y,'periodo_PR':t,'observaciones':n} for (p,y,t),n in sorted(groups.items())],'faltantes_DA':[{'plan':p,'ano':y,'periodo_PR':t,'observaciones':n} for (p,y,t),n in sorted(Counter((p,y,t) for k,cli,p,y,t in da_bad).items())],'presencia_misma_identidad_otros_anios':sum(any(kk==k and yy!=y for kk,yy in refs) for k,cli,p,y,t in bad),'coincidencia_cuerpo_otro_DV_mismo_ano':sum(any(kk.split('-')[0]==k.split('-')[0] and kk!=k and yy==y for kk,yy in refs) for k,cli,p,y,t in bad)})
flags=defaultdict(Counter)
for x in xl(PRO):
 c=val(x['CODCARR']);j=jmap.get(val(x['JORNADA']),'');k=doc(x['RUT'],x['DIG']);u=(c,j,k,val(x['CODCLI']),val(x['PLAN_DE_ESTUDIO']),val(x['ANO']),val(x['PERIODO']))
 if u in missing:flags[c,j][('CONVALIDADO',val(x['CONVALIDADO']))]+=1;flags[c,j][('ESTADO_ACADEMICO',val(x['ESTADO_ACADEMICO']))]+=1
# Respaldo ya inventariado 11248: corroboración de expediente, no código SIES.
backup=Path('/Users/alexi/Downloads/2025/DATOSDEALUMNOS_11248.xlsx');bs=defaultdict(set)
if backup.exists():
 for x in xl(backup):bs[val(x['CODCLI']),val(x['CODCARPR'])].add((doc(x['RUT']),val(x['SEDE']),jmap.get(val(x['JORNADA']),'')))
 sources.append({'ruta':str(backup),'sha256':sha(backup),'uso':'corroboracion expediente, no codigo SIES anual'})
for d in details:
 c,j=d['carrera'],d['jornada'];d['atributos_filas_asignaturas_faltantes']=[{'campo':f,'valor':v,'filas':n} for (f,v),n in flags[c,j].items()];d['faltantes_anuales_con_expediente_en_11248']=sum((k,'RE',j) in bs.get((cli,c),set()) for cc,jj,k,cli,p,y,t in missing if (cc,jj)==(c,j))
 d['observaciones_sin_DA12159_recuperadas_11248']=sum((k,'RE',j) in bs.get((cli,c),set()) for k,cli,p,y,t in pr[c,j] if not any(v[0]==k and v[1]=='RE' and v[2]==j for v in da.get((cli,c),set())))
 d['faltante_exacto']='Carga o rectificación MAT_'+','.join(sorted({x['ano'] for x in d['faltantes']}))+' con MM_N_DOCUMENTO, MM_DV, MC_CAT_PERIODO, MC_CODIGO_UNICO; vínculo efectivo CODCLI+PLAN_DE_ESTUDIO y periodo para regla prospectiva.'
rs=load(B/'investigacion_contextual_v3/PRUEBAS_CONTEXTUALES.json');audit=[]
for r in rs:
 if r['completo_con_contexto_DA_y_catalogo'] and r['personas']>=3:
  counts=r['codigos_personas'];prop=max(counts.values())/sum(counts.values());audit.append({'carrera':r['carrera'],'jornada':r['jornada'],'previa':r['estado_previo'].startswith('PROPUESTA'),'personas':r['personas'],'proporcion_persona_codigo':prop,'n3':r['personas']>=3,'predominancia90':prop>=.9,'limite':'proporción en grano persona-código contextual, no réplica del grano original persona-plan-código; tipo de plan individual y control total MU por dimensión no acreditados por cobertura observada','estado':'PROPUESTA_METODOLOGICA_PENDIENTE'})
assert len(audit)==8 and sum(x['previa'] for x in audit)==3 and sum(not x['previa'] for x in audit)==5
assert sum(sum(v['observaciones'] for v in d['faltantes']) for d in details)==7
for s in sources:assert sha(s['ruta'])==s['sha256']
(OUT/'DIAGNOSTICO.json').write_text(json.dumps({'casos':details,'auditoria_ocho_contextuales':audit,'indicador_heterogeneo':{'numerador':44,'denominador':63,'etiqueta':'39 propuestas estadísticas + 5 contextuales, no equivalencias verificadas'},'indicador_homogeneo':{'numerador':8,'denominador':63,'etiqueta':'validación contextual observacional, criterios aplicados a las 63; no certificación plan vigente'},'nueva_resolucion':0},ensure_ascii=False,indent=2));(OUT/'FUENTES.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2));print(json.dumps(details,ensure_ascii=False))
