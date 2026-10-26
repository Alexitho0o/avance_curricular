"""Controles complementarios de 13 contextos 2025; no adjudica versiones."""
import collections,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).parent
P=Path('/Users/alexi/.local/share/ipss/v11_fase2_20261026/EVALUACION_CIERRE_CO_V1_DETALLE_V2.json')
H=ROOT/'data/versiones_por_cohorte/20261016/historias_oferta.json'
targets=json.loads(P.read_text());hist=json.loads(H.read_text());idx={x['codigo_unico']:{str(a['anio']) for a in x['anual']} for x in hist}
z=collections.Counter(); groups=collections.Counter()
for t in targets:
 if not t['diferencia_familia'] or t['anio']!='2025':continue
 mu=[x for x in t['mu_fuente_primaria'] if x['anio']=='2026'];matched=[x for x in mu if x['codigo'].rsplit('V',1)[0] in t['familias_destino']]
 if not matched:continue
 z['contextos']+=1;z['codigo_mu_2026_unico_total' if len({x['codigo'] for x in mu})==1 else 'multiples_codigos_mu']+=1
 z['ingreso_actual_no_posterior_2025' if all(x['ingreso_actual'].isdigit() and int(x['ingreso_actual'])<=2025 for x in matched) else 'ingreso_no_confirmado']+=1
 z['codcli_mismo_en_ambos_respaldos_2026' if all(t['respaldos'][p] for p in ['DA_P2_2026','DA_P3_2026']) else 'codcli_no_verificado']+=1
 plans={k.split('|')[3] for k in t['promedios']};z['plan_observado_unico' if plans=={t['plan']} else 'plan_no_unico']+=1
 z['codigo_en_oferta_2025' if all('2025' in idx.get(x['codigo'],set()) for x in matched) else 'codigo_no_localizado_oferta_2025']+=1
 groups[t['carrera']+'|'+t['periodo']]+=1
assert z['contextos']==13
out={'clasificacion':'B fuentes; C controles; E atribución al expediente y periodo','controles':dict(z),'grupos':dict(groups),'limite':'MU anual identifica persona y año; los respaldos no demuestran por sí solos atribución documental del código a CODCLI en 2025. Aplicación de decisión previa requiere auditoría individual de alcance.','detalle_privado_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'historias_oferta_sha256':hashlib.sha256(H.read_bytes()).hexdigest()}
(OUT/'EVALUACION_TRECE_MU2026_AGREGADO.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(json.dumps(out,ensure_ascii=False))
