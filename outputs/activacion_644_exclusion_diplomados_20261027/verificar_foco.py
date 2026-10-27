"""Reejecuta lector/cálculo previo sin sobrescribir auditorías anteriores."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).parent
p=ROOT/'outputs/avance_historico_atribucion_20261027/auditar_atribucion.py'
ns={'__file__':str(p)}
exec(compile(p.read_text().split("with (OUT/'PARTICION_POR_CODIGO.csv')")[0],str(p),'exec'),ns)
r=ns['result'];prior=json.load(open(ROOT/'outputs/avance_historico_fase2_candidata_644_20261027/RESULTADOS.json'))
assert r['particion_unidades_por_atribucion']==prior['unidades_simuladas']
assert r['estados_anuales_filas']==prior['anual_simulado']
assert r['estados_acumulados_filas']==prior['acumulado_simulado']
assert sum(not v.get('codigo_sies') for v in ns['cache'].values())==1374
r['escenario_adoptado']=True;r['pendientes_contextos']=1374;r['coincide_con_simulacion_aprobada']=True
(OUT/'RESULTADO_FOCO_ACTIVADO.json').write_text(json.dumps(r,ensure_ascii=False,indent=2))
ns['service'].close();print('PASS: foco 5144, pendientes 1374, particiones iguales al escenario aprobado')
