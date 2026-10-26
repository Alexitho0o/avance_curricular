"""Separa etiquetas observadas de actos efectivos de migración; no adopta candidatos."""
import json,csv,sys,hashlib
from pathlib import Path
from collections import defaultdict,Counter
import openpyxl
O=Path(sys.argv[1]);P=Path(json.load(open(O/'MANIFEST.json'))['privado']);R=Path(__file__).resolve().parents[1]
rr=json.load(open(P/'OBSERVACIONES_PRIVADAS.json'))
G=json.load(open(R/'data/versiones_por_cohorte/20261016/grupos_existentes.json'))
rev={'1':'D','2':'V','4':'O'};families={(g['codcarpr'],g['jornada']):g['familias'] for g in G}
by=defaultdict(list)
for x in rr:
 for f in families.get((x['carrera'],rev.get(x['jornada_sies'])),[]):by[x['persona'],f].append(x)
multiple=[];summary=Counter()
for (person,fam),xs in by.items():
 plans={(x['CODCLI'],x['carrera'],x['plan']) for x in xs}
 if len(plans)<2:continue
 multiple.append({'persona':person,'familia':fam,'expedientes_planes':[{'CODCLI':c,'carrera':ca,'plan':p,'primer_periodo_observado':min((x['ano'],x['periodo']) for x in xs if (x['CODCLI'],x['carrera'],x['plan'])==(c,ca,p)),
  'ultimo_periodo_observado':max((x['ano'],x['periodo']) for x in xs if (x['CODCLI'],x['carrera'],x['plan'])==(c,ca,p))} for c,ca,p in sorted(plans)],
  'clasificacion':'B etiquetas observadas; E migración/continuidad administrativa no acreditada'})
 summary[fam]+=1
headers={}
for path in ['/Users/alexi/Downloads/DATOSDEALUMNOS_12159.xlsx','/Users/alexi/Downloads/2025/DATOSDEALUMNOS_11248.xlsx']:
 w=openpyxl.load_workbook(path,read_only=True);h=list(next(w['Hoja1'].values));w.close()
 headers[path]={'sha256':hashlib.sha256(Path(path).read_bytes()).hexdigest(),'hoja':'Hoja1','encabezados_plan':[v for v in h if v and ('PLAN' in str(v).upper() or 'PESTUD' in str(v).upper())],
 'fechas_disponibles':[v for v in h if v and any(z in str(v).upper() for z in ['FECHA','INGRESO']) and v!='FECHANACIMIENTO'],
 'corte_efectivo':'No acreditado; docProps no lo sustituye'}
focus=[x for x in rr if x['codigo_documental_atribuible']=='I162S2C3J4V2' and x['fechas_declaradas']['MU_INGRESO_ACTUAL']==2022]
counts=Counter((x['carrera'],x['plan'],x['ano'],str(x['fechas_declaradas']['DA_ANOINGRESO']),str(x['fechas_declaradas']['MU_INGRESO_ORIGEN'])) for x in focus)
result={'estado':'OK_CON_PENDIENTES_SEMANTICOS','fuentes_DA':headers,'caso_C3J4':{'observaciones':len(focus),'personas':len({x['persona'] for x in focus}),
 'codigo_observado':'I162S2C3J4V2','ingreso_actual_MU':2022,'desglose':[dict(zip(['carrera','plan','ano_observado','DA_ANOINGRESO','MU_ANIO_ORIGEN','observaciones'],[*k,v])) for k,v in sorted(counts.items())]},
 'personas_familia_con_varios_expedientes_planes':len(multiple),'personas_unicas_no_sumar_familias':len({x['persona'] for x in multiple}),
 'por_familia':dict(sorted(summary.items())),
 'conclusion':'Una etiqueta de plan por expediente no descarta varios expedientes/planes de la persona dentro de una familia. Coexistencia o secuencia observada no acredita fecha efectiva de migración, reingreso ni equivalencia retrospectiva.'}
(O/'QA_CRONOLOGIA.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
(P/'TRAYECTORIAS_MULTIPLES_PERSONA_FAMILIA.json').write_text(json.dumps(multiple,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in result.items() if k not in ['fuentes_DA','caso_C3J4','por_familia']},ensure_ascii=False))
