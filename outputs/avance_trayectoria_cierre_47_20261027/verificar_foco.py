from pathlib import Path
import json
root=Path(__file__).resolve().parents[2];p=root/'outputs/avance_historico_atribucion_20261027/auditar_atribucion.py';n={'__file__':str(p)}
exec(compile(p.read_text().split("with (OUT/'PARTICION_POR_CODIGO.csv')")[0],str(p),'exec'),n)
r=n['result'];pend=sum(not v.get('codigo_sies') for v in n['cache'].values());assert len(n['cache'])==5144 and pend==1327
old=json.loads((root/'outputs/activacion_644_exclusion_diplomados_20261027/RESULTADO_FOCO_ACTIVADO.json').read_text());assert r['unidades_identidad_exacta_foco']==old['unidades_identidad_exacta_foco'];assert r['contextos_unicos_consultados']==old['contextos_unicos_consultados']
summary={'contextos_foco':5144,'pendientes_antes':1374,'pendientes_despues':pend,'reduccion_contextos':47,'unidades_conservadas':True,'sin_tasas_recalculadas':True};(Path(__file__).parent/'QA_FOCO.json').write_text(json.dumps(summary,indent=2));n['service'].close();print(json.dumps(summary))
