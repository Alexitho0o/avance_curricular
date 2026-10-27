from pathlib import Path
import json,sys,subprocess,os
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R));from common.diccionario_sies_seguimiento import DiccionarioSiesSeguimiento
O=Path(__file__).parent;P=Path.home()/'.local/share/ipss/fase_d_v15_302_20261027';s=DiccionarioSiesSeguimiento();assert s.edicion=='v15_20261027_candidata_302';v14=DiccionarioSiesSeguimiento(descriptor=R/'data/diccionario_sies_seguimiento/v14_20261027_contextos_42/descriptor.json');new=json.loads((Path.home()/'.local/share/ipss/fase_d_v15_candidata_20261027/NUEVAS_OBSERVACIONES_PRIVADAS.json').read_text())[:30];req=[]
for x in new:req.append({'persona':x['persona'],'codcli':x['CODCLI'],'plan':x['plan'],'anio':x['ano'],'periodo':x['periodo'],'carrera':x['carrera'],'sede':x['sede_dimension'],'jornada':x['jornada_sies']})
for r in v14.db.execute('select persona,codcli,plan,anio,periodo,carrera,sede,jornada from observaciones order by id'):
 q=dict(zip(['persona','codcli','plan','anio','periodo','carrera','sede','jornada'],r));a=v14.consultar(**q);b=s.consultar(**q)
 if a['estado']=='REUTILIZABLE' and a.get('codigo_sies')==b.get('codigo_sies'):req.append(q)
 if len(req)==60:break
assert len(req)==60;payload=json.dumps([{'metodo':'consultar','entrada':x} for x in req]);paths=['scripts/consultar_diccionario_sies_seguimiento.py','scripts/retencion_intermedia_t2_t3/consultar_codigos_sies.py','procesos/caracterizacion/scripts/consultar_diccionario_sies_seguimiento.py'];answers=[]
for i,f in enumerate(paths):
 out=P/('test_activo_60_consumidor_'+str(i)+'.json');assert not out.exists();p=subprocess.run([sys.executable,str(R/f),'--salida-privada',str(out)],input=payload,text=True,capture_output=True,cwd=R);assert p.returncode==0,p.stderr;ans=json.loads(out.read_text());assert len(ans)==60;answers.append(ans)
assert answers[0]==answers[1]==answers[2];assert all(z['nivel_respaldo']=='D_CORRESPONDENCIA_INTERNA_APROBADA' for z in answers[0][:30]);res={'edicion':s.edicion,'puntero_real':True,'nuevos':30,'anteriores':30,'consumidores':3,'consultas_totales':180,'respuestas_iguales':True,'capa_promedios_nuevos_pendiente':sum(z['seguimiento_promedios']['estado']=='PENDIENTE_OBSERVACION_SIN_CAPA' for z in answers[0][:30])};(O/'QA_CONSUMIDORES_ACTIVO.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n');print(json.dumps(res));s.close();v14.close()
