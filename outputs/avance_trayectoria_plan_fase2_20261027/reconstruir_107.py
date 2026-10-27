from pathlib import Path
import json,collections
root=Path('/Users/alexi/Documents/GitHub/avance_curricular')
p=root/'outputs/avance_historico_periodos_815_20261027/revisar_periodos.py'
s=p.read_text().split('# Solo agregados se exportan.')[0]
s=s.replace("prior.read_text().split('# Query once per exact context.')[0]", "prior.read_text().split('# Query once per exact context.')[0].replace('service=DiccionarioSiesSeguimiento()', \"service=DiccionarioSiesSeguimiento(descriptor=ROOT/'data/diccionario_sies_seguimiento/v11_20261026_promedios_integrada/descriptor.json')\")")
n={'__file__':str(p)}
exec(compile(s,str(p),'exec'),n)
candidates=[x for x in n['candidates'] if x['state']=='MU_ANUAL_UNICA_SIN_CONTEXTO_CONCORDANTE_DEL_ANIO']
print('107_REPRODUCIDOS',len(candidates),flush=True)
out=collections.Counter(); examples=[]
for c in candidates:
 pe,cli,pl,ca,jo,an,period=c['key'];code=c['mu_codes'][0]
 obs=n['byexp'][(pe,cli)]
 same=[x for x in obs if x['plan']==pl and x['carrera']==ca and (x.get('codigo_documental_atribuible') or x.get('codigo_interno_adoptado'))==code]
 yr=[x for x in obs if str(x['ano'])==an and x['plan']==pl and x['carrera']==ca]
 other=[x for x in obs if str(x['ano'])==an and x['carrera']==ca and x['plan']!=pl]
 othercli=[x for (person,cl),rows in n['byexp'].items() if person==pe and cl!=cli for x in rows if str(x['ano'])==an and (x.get('codigo_documental_atribuible') or x.get('codigo_interno_adoptado'))==code]
 status=('ANCLA_MISMO_PLAN_OTRO_ANIO' if same else 'SIN_ANCLA_CODIGO_PLAN');out[status]+=1
 out['CON_OTRO_PLAN_ANIO']+=bool(other);out['OTRO_CODCLI_MISMO_CODIGO']+=bool(othercli);out['CON_CONTEXTO_ANUAL_PLAN_SIN_CODIGO']+=bool(yr)
 if len(examples)<5:examples.append({'plan':pl,'carrera':ca,'jornada':jo,'anio':an,'periodo':period,'codigo_mu_candidato':code,'estado':status,'anclas_anios':sorted({str(x['ano']) for x in same}),'conflicto_otro_plan':bool(other),'conflicto_otro_expediente':bool(othercli)})
print(json.dumps({'totales':out,'ejemplos_sin_identificadores':examples},ensure_ascii=False,indent=2),flush=True)
