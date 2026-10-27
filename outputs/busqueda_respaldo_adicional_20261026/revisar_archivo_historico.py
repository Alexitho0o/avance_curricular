"""Contrasta respaldos históricos por CODCLI/ramo sin exportar identificadores."""
import collections,csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
private=Path('/Users/alexi/.local/share/ipss/revision_21_ramos_4_expedientes_20261026/DETALLE_CUATRO_CASOS_V2.json')
base=ROOT/'archive/cleanup/cutoff_2026-04-15/moved 3/resultados'
plans=base/'auditoria_plan_estudios_alumno_completa.tsv'
subjects=base/'run_trace_50_codcli_2026-04-04_18-43-08/audits/03_fuente_Hoja1.csv'
prior=ROOT/'outputs/busqueda_respaldo_titulos_homologaciones_20261026/RESULTADO_AGREGADO.json'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
cases=json.loads(private.read_text());assert len(cases)==4
index={x['CODCLI']:z['caso'] for z in cases for x in z['contextos_v11']}
targets={x['ramo']:x['plan_revisado'] for x in json.loads(prior.read_text())['ramos']}
plan_hash=sha(plans);matches=collections.defaultdict(list);n=0
with plans.open(encoding='utf-8-sig',newline='') as f:
 for r in csv.DictReader(f,delimiter='\t'):
  n+=1
  if r.get('CODCLI') in index:matches[index[r['CODCLI']]].append((r['CODCARPR_NORM'],r['PLAN_DE_ESTUDIO'],r['ANIO_ING_ACT'],r['SIES_MATCH_STATUS']))
assert sha(plans)==plan_hash
counts=collections.Counter(v for rows in matches.values() for v in rows)
subject_hash=sha(subjects);hits=collections.Counter()
with subjects.open(encoding='utf-8-sig',newline='') as f:
 for r in csv.DictReader(f):
  code=r['CODRAMO'].strip().upper();plan=r['PLAN_DE_ESTUDIO'].strip().upper()
  if code in targets:hits[(code,plan,r['RAMOEQUIV'].strip().upper(),r['ESTADO'].strip().upper())]+=1
assert sha(subjects)==subject_hash
out={'clasificacion':'B fuentes; C cruce; E atribución y homologación','fuentes':[{'ruta':str(plans),'sha256':plan_hash,'filas':n},{'ruta':str(subjects),'sha256':subject_hash}],'personas_con_codcli_en_auditoria':len(matches),'personas_buscadas':4,'resultados_por_plan':[{'carrera':c,'plan':p,'anio_ingreso_actual':y,'estado_auditoria_heredado':st,'filas':v} for (c,p,y,st),v in sorted(counts.items())],'ramos_21_localizados':[{'ramo':c,'plan_observado':p,'ramoequiv':e,'estado_ramo':st,'filas':v} for (c,p,e,st),v in sorted(hits.items())],'limites':'El estado de auditoría es resultado heurístico previo, no prueba de aceptación SIES ni vínculo formal título–plan. La actividad en un plan distinto no prueba homologación individual en el plan pendiente.'}
(OUT/'RESULTADO_AGREGADO.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'personas_localizadas':len(matches),'ramos_localizados':len({x[0] for x in hits})},ensure_ascii=False))
