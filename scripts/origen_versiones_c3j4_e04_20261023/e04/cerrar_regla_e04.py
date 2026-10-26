"""QA de procedencia E04; integra evidencias sin modificar fuentes."""
from pathlib import Path
import json,hashlib,collections
read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
R=Path('/Users/alexi/Documents/GitHub/avance_curricular');P=Path('/Users/alexi/.local/share/ipss/analisis_conflictos_22_20261023/regla_e04');priv=read(P/'PREPARACION_PRIVADA.json');prep=read('/Users/alexi/Documents/GitHub/avance_curricular/outputs/origen_versiones_c3j4_e04_20261023_163300/e04/regla_e04_preparacion.json');inc=read('/Users/alexi/Documents/GitHub/avance_curricular/outputs/origen_versiones_c3j4_e04_20261023_163300/e04/regla_e04_incremental.json');grp=read('/Users/alexi/Documents/GitHub/avance_curricular/outputs/origen_versiones_c3j4_e04_20261023_163300/e04/regla_e04_grupo_precarga.json')
prior=read('/Users/alexi/.local/share/ipss/origen_v1_inf35_03_20261023_150536/EVIDENCIA.json');assert priv['persona']!=prior['objetivos'][0]['persona']
vr=[r for r in prep['registros'] if any(k.endswith(':VERSION') for k in r['valores'])];assert len(vr)==10
assert all(v==1 for r in vr for k,v in r['valores'].items() if k.endswith(':VERSION'))
assert all(not any(k.endswith(':VERSION') for k in r['formulas']) for r in vr)
codcli_refs=[v for r in priv['records'] for k,v in r['valores'].items() if k.endswith(':CODCLI') and v is not None]
assert all(str(v).strip()==priv['CODCLI'] for v in codcli_refs)
assert len(prep['registros'])==32 and len(prep['fuentes'])==17 and grp['filas_precarga_c1j1']==22
sources={**prep['fuentes'],**inc['fuentes_sha256']}
assert all(sha(p)==h for p,h in sources.items())
assert inc['celda_precarga']=={'hoja':'Precarga','celda':'Q1025','valor':1,'tipo':'n','formula':False,'comentario':None,'hipervinculo':None}
qa={'resultado':'OK_LECTURA_REGLA_GENERADORA_PENDIENTE','E04_distinto_INF35_03':True,'libros_preparacion':17,'filas_identidad_exacta':32,'filas_VERSION_literal1':10,'formulas_VERSION_foco':0,'filas_con_CODCLI_cotejadas':len(codcli_refs),'grupo_precarga_c1j1':22,'fuentes_intactas':True,'codigo_actual_diccionario_sha256':sha('/Users/alexi/.local/share/ipss/cierre_inf35_03_t3_20261023_154224/DICCIONARIO_SIES.sqlite'),'adjudicaciones':0,'bases_y_denominadores_modificados':False,'regla_generadora_V1_localizada':False,'limites':['Coincidencia entre hojas no demuestra que unas sean copia directa de otras ni orden exacto de edición.','FECH_CAR es campo observado del lote; no se interpreta como fecha efectiva de cambio de plan.','Las 32 filas incluyen duplicación entre libros/hojas y no son 32 evidencias independientes.','Búsqueda global de scripts/SQL/Git realizada por agente principal; no se presenta aquí como agotada.']}
Path('/Users/alexi/Documents/GitHub/avance_curricular/outputs/origen_versiones_c3j4_e04_20261023_163300/e04/regla_e04_QA.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n')
files=['/Users/alexi/Documents/GitHub/avance_curricular/outputs/origen_versiones_c3j4_e04_20261023_163300/e04/regla_e04_preparacion.json','/Users/alexi/Documents/GitHub/avance_curricular/outputs/origen_versiones_c3j4_e04_20261023_163300/e04/regla_e04_incremental.json','/Users/alexi/Documents/GitHub/avance_curricular/outputs/origen_versiones_c3j4_e04_20261023_163300/e04/regla_e04_grupo_precarga.json','/Users/alexi/Documents/GitHub/avance_curricular/outputs/origen_versiones_c3j4_e04_20261023_163300/e04/regla_e04_conclusion.md','/Users/alexi/Documents/GitHub/avance_curricular/outputs/origen_versiones_c3j4_e04_20261023_163300/e04/regla_e04_QA.json']
for p in files:
 text=Path(p).read_text();assert priv['persona'] not in text and priv['CODCLI'] not in text
scripts=['/Users/alexi/Documents/GitHub/avance_curricular/scripts/origen_versiones_c3j4_e04_20261023/e04/rastrear_regla_e04.py','/Users/alexi/Documents/GitHub/avance_curricular/scripts/origen_versiones_c3j4_e04_20261023/e04/regla_e04_incremental.py','/Users/alexi/Documents/GitHub/avance_curricular/scripts/origen_versiones_c3j4_e04_20261023/e04/regla_e04_grupo_precarga.py','/Users/alexi/Documents/GitHub/avance_curricular/scripts/origen_versiones_c3j4_e04_20261023/e04/cerrar_regla_e04.py']
Path('/Users/alexi/Documents/GitHub/avance_curricular/outputs/origen_versiones_c3j4_e04_20261023_163300/e04/regla_e04_manifest.json').write_text(json.dumps({'fuentes_sha256':sources,'salidas_sha256':{p:sha(p) for p in files},'scripts_sha256':{p:sha(p) for p in scripts},'QA':qa},ensure_ascii=False,indent=2)+'\n')
print(json.dumps(qa,ensure_ascii=False,indent=2))
