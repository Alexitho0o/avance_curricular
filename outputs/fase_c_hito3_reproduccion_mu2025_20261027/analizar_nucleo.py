from pathlib import Path
import json,collections,csv
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).parent;p=ROOT/'outputs/avance_historico_atribucion_20261027/auditar_atribucion.py';n={'__file__':str(p)};exec(compile(p.read_text().split("with (OUT/'PARTICION_POR_CODIGO.csv')")[0],str(p),'exec'),n)
cache=n['cache'];assert len(cache)==5144;groupsp=collections.defaultdict(list);groupse=collections.defaultdict(list)
for k,v in cache.items():
 pe,cli,plan,car,jor,ano,per=k;groupsp[pe].append((k,v));groupse[(pe,cli,car)].append((k,v))
people={k for k,rr in groupsp.items() if all(not v.get('codigo_sies') for _,v in rr)};exps={k for k,rr in groupse.items() if all(not v.get('codigo_sies') for _,v in rr)};assert len(people)==45 and len(exps)==296
svc=n['service'];aggregate=collections.defaultdict(lambda:{'contextos':0,'personas':set(),'expedientes':set()});sets=collections.Counter()
for k,v in cache.items():
 pe,cli,plan,car,jor,ano,per=k;ek=(pe,cli,car);isinp=pe in people;isine=ek in exps
 if not inep if False else False:pass
 if not isinp and not isine:continue
 reason=v.get('motivo','SIN_MOTIVO')
 if reason=='CONTEXTO_NO_LOCALIZADO':
  indexed=svc.db.execute('SELECT plan,anio,periodo,carrera FROM observaciones WHERE persona=? AND codcli=?',(pe,cli)).fetchall();sameperiod=[z for z in indexed if z[1]==ano and z[2]==per];sameplan=[z for z in sameperiod if z[0]==plan]
  reason='EXPEDIENTE_NO_INDEXADO' if not indexed else 'PERIODO_NO_INDEXADO' if not sameperiod else 'PLAN_DISTINTO' if not sameplan else 'CARRERA_DISTINTA'
 for scope,on in [('PERSONA_SIN_CODIGO',isinp),('EXPEDIENTE_SIN_CODIGO',isine)]:
  if not on:continue
  g=aggregate[(scope,car,ano,reason)];g['contextos']+=1;g['personas'].add(pe);g['expedientes'].add(ek)
 if isinp:sets['contextos_personas_sin_codigo']+=1
 if isine:sets['contextos_expedientes_sin_codigo']+=1
sets['expedientes_de_45_personas']=sum(e[0] in people for e in exps);sets['personas_con_expediente_sin_codigo']=len({e[0] for e in exps});sets['personas_parciales_con_expediente_sin_codigo']=len({e[0] for e in exps}-people)
with (OUT/'DESGLOSE_NUCLEO_AGREGADO.csv').open('w',encoding='utf8',newline='') as f:
 w=csv.writer(f,delimiter=';');w.writerow(['ALCANCE','CARRERA_UMAS','ANO','CAUSA','CONTEXTOS','PERSONAS_DISTINTAS_EN_GRUPO','EXPEDIENTES_DISTINTOS_EN_GRUPO']);
 for k,g in sorted(aggregate.items()):w.writerow([*k,g['contextos'],len(g['personas']),len(g['expedientes'])])
result={'foco_contextos':5144,'personas_sin_ningun_codigo':len(people),'expedientes_sin_ningun_codigo':len(exps),'detalle_intersecciones':dict(sets),'filas_desglose':len(aggregate),'advertencia':'Personas y expedientes por carrera/año/causa se superponen entre filas; solo contextos son aditivos por alcance. Los 296 expedientes no equivalen automáticamente a los expedientes de las 45 personas.'};(OUT/'NUCLEO_RESUMEN.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False,indent=2));svc.close()
