"""Evalúa el alcance del criterio D1 sin ampliar la decisión ni asignar códigos."""
import collections, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; OUT=Path(__file__).parent
P=Path('/Users/alexi/.local/share/ipss/v11_fase2_20261026/EVALUACION_CIERRE_CO_V1_DETALLE_V2.json')
EXP=Path('/Users/alexi/.local/share/ipss/v11_fase2_20261026/REVISION_TRECE_EXPEDIENTES_DETALLE.json')
hist=json.loads((ROOT/'data/versiones_por_cohorte/20261016/historias_oferta.json').read_text()); rows=json.loads(P.read_text()); exps={x['contexto']:x for x in json.loads(EXP.read_text())}
targets=[t for t in rows if t['diferencia_familia'] and t['anio']=='2025' and any(m['anio']=='2026' and m.get('codigo','').rsplit('V',1)[0] in t['familias_destino'] for m in t['mu_fuente_primaria'])];assert len(targets)==13
stats=collections.Counter(); gr=collections.Counter()
for t in targets:
 mu=[m for m in t['mu_fuente_primaria'] if m['anio']=='2026'];codes={m['codigo'] for m in mu}; assert len(codes)==1;code=next(iter(codes)); family=code.rsplit('V',1)[0]
 oferta={r['codigo_unico'] for r in hist if r['familia']==family and any(str(a['anio'])=='2025' for a in r['anual'])}
 checks={'sede_RE_actual':t['sede_actual']=='RE','jornada_codigo':family.endswith('J'+t['jornada']),'oferta_2025_candidato_unico':oferta=={code},'mu_2026_unico':len(codes)==1,'ingreso_actual_hasta_2025':all(str(m['ingreso_actual']).isdigit() and int(m['ingreso_actual'])<=2025 for m in mu),'plan_unico_fuentes_revisadas':{k.split('|')[3] for k in t['promedios']}=={t['plan']},'actividad_mismo_plan_periodo':any((v:=k.split('|'))[1:3]==['2025',t['periodo']] and v[3:6]==[t['plan'],t['carrera'],{'1':'D','2':'V','4':'O'}[t['jornada']]] for k in t['promedios'])}
 e=exps[t['pos']]; checks['codcli_misma_carrera_jornada_en_dos_fotos_2026']=all(any(r['codcli']==t['codcli'] and r['carrera']==t['carrera'] and r['jornada']=={'1':'D','2':'V','4':'O'}[t['jornada']] for r in e['respaldos'][p]) for p in ['DA_P2_2026','DA_P3_2026'])
 for k,v in checks.items():stats[k+'_cumple' if v else k+'_no_acreditado']+=1
 gr[(t['carrera'],t['periodo'],code)]+=1
assert all(v==13 for v in stats.values())
out={'clasificacion':'B observacion; C contraste; E atribucion y autorizacion','contextos':13,'personas':len({t['persona'] for t in targets}),'expedientes':len({(t['persona'],t['codcli']) for t in targets}),'controles':dict(stats),'grupos':[{'carrera':a,'periodo':b,'codigo_candidato':c,'contextos':v} for (a,b,c),v in sorted(gr.items())],'fuentes_detalle_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'respaldos_privados_sha256':hashlib.sha256(EXP.read_bytes()).hexdigest(),'reserva':'El índice acredita presencia y unicidad en oferta 2025, no estado de vigencia ni aceptación; RUT de MU2026 no contiene CODCLI. Las dos fotos corroboran vínculo, pero no identifican código documental del expediente en 2025. La decisión D1 aprobó 27 observaciones concretas, no estos 13.'}
(OUT/'QA_TRECE_CRITERIO_V10.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False))
