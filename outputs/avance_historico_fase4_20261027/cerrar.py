"""Registra la entrega local solo si supera el QA; no publica ni altera fuentes."""
import json,hashlib,shutil,subprocess
from pathlib import Path
from datetime import datetime
O=Path(__file__).parent;R=O.parents[1]
q=json.loads((O/'QA_FINAL.json').read_text());assert q['estado']=='PASS_CON_ALCANCE'
f=O/'AVANCE_ACADEMICO_HISTORICO_IPSS_20261027_V1.xlsx';dest=Path.home()/'Desktop'/f.name
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
if dest.exists():assert sha(dest)==sha(f),'No sobrescribir otra entrega'
else:shutil.copy2(f,dest)
assert sha(dest)==sha(f)
b=json.loads((O/'BASELINE.json').read_text())
report=f'''# Fase 4: entrega local de revisión

[C] Libro: `{f}`. Copia idéntica en `{dest}`. SHA-256: `{sha(f)}`.

[C] Estado: **PASS_CON_ALCANCE**. {len(q['controles'])} controles independientes correctos. La revisión permite entregar el libro provisional; no certifica cobertura total ni vigencia histórica de planes. Apertura y recálculo en Excel nativo: **no verificados**, sin sesión conectada disponible. Recálculo con Artifact Tool.

## Contenido y uso

[C] 15 hojas, tres gráficos editables y tablas con filtros. En 01_Resumen se elige fuente, año observado, período UMAS, carrera y jornada. Los cinco selectores recalculan actividad y desglose; 04_Mallas comparte fuente/carrera/jornada y conserva todo el historial del extracto. 02_Anual_SIES_2025 mantiene el alcance congelado proceso 2026/datos 2025, sin mezclarlo con selección 2026. Para revisar solo coincidencias en las tablas de detalle, filtrar Selección = 1.

[C] Hojas 08–14 contienen las bases pertinentes y derivados de preparación; 06 explica procedencia, fórmulas y alcance. Datos originales son valores B. Conteos distintos y pertenencia a mallas son derivados C preparados por el procedimiento de fase 3, no fórmulas Excel. Resúmenes, búsquedas y cocientes son fórmulas editables. El libro contiene identificadores necesarios para trazabilidad y permanece local, excluido de Git.

## Resultados preservados

| Observación | Resultado | Clase |
|---|---:|---|
| Registros de la carga anual | 2.371 | B |
| Unidades cursadas / aprobadas anuales | 21.389 / 17.628 | B/C |
| Cociente de aprobación anual | 82,4 % | C |
| Denominador de unidades de plan, repetido por registro | 96.104 | C |
| Aprobadas acumuladas H113 / H114B | 41.627 / 38.235 | B |
| Cocientes acumulados H113 / H114B | 43,3 % / 39,8 % | C |
| Filas PROMEDIOS 7804 / 12166 | 129.493 / 70.000 | B |
| Filas del listado curricular | 11.438 | B |

[C/E] H113 y H114B son dos congelados distintos. H114B contiene un ajuste histórico ya documentado; no se ha impuesto un límite universal nuevo ni se ha cambiado el denominador. H113 conserva 247 registros por encima del plan (166 sobre 125 %); H114B no tiene registros sobre el plan. No presentar los cocientes como nuevas tasas oficiales aprobadas.

## QA y reparación durante construcción

[C] Se detectó una discrepancia de búsqueda de unidades de plan en el motor al usar INDEX/MATCH. Se sustituyó por SUMIF con clave única verificada para unidades y VLOOKUP exacto para nombre; el denominador final reproduce 96.104 y los nombres se contrastaron con las 43 claves. Se comparan 43 desgloses anuales, 2.758 contextos de actividad, 565 desgloses de malla, seis selecciones con recálculo, fórmulas exportadas, cachés, tablas y gráficos. Las bases RAW y catálogo incorporados se contrastan íntegramente contra su extracción, sin exponer identificadores en el informe.

[C] La primera exportación agotó el límite de memoria. La construcción final reserva las hojas grandes e incorpora sus valores secuencialmente; conserva las fórmulas y objetos exportados por Artifact Tool. No se usa esa extensión para cambiar indicadores ni fuentes.

## Pendientes que continúan visibles

- [E] 644 contextos propuestos de atribución: no aprobados ni aplicados.
- [E] 21 equivalencias generales de ramos; reconocimientos individuales no las sustituyen.
- [E] 27 filas de atribución H113 y un caso de identidad P permanecen con su alcance documentado.
- [E] Vigencia histórica, obligatoriedad y opciones de malla; los cocientes frente al listado son diagnósticos.
- [E] Cohorte/sede histórica cuando no existe enlace acreditado: no se infieren de año observado ni del prefijo CODCLI.
- [E] Cobertura completa y calendario UMAS: se preservan períodos 4 y 5 y las extracciones separadas.
- [B/E] En 12166 para 2026-3 hay 6.296 filas, cero resultados A/R, 537 E/I y 5.759 otros/sin resultado. La tasa sin resultados A/R figura como Pendiente, no 0 %.

[C] Rama `{q['rama']}`; HEAD antes y después `{q['head']}`. Fuentes, V24, diccionario y cambios previos conservados por hash. Sin commit, push ni publicación. El hash del libro permite verificarlo, pero no significa que el archivo esté publicado en GitHub.
'''
(O/'INFORME.md').write_text(report)
manifest={'clasificacion':'B/C/D/E','fecha':datetime.now().astimezone().isoformat(),'fase':4,'estado':q['estado'],'autorizacion':'Vamos con la fase 4','fuentes':b['sources'],'referencia_visual':b['reference'],'salidas':[{'ruta':str(f),'sha256':sha(f),'privacidad':'individual local; excluido de Git'},{'ruta':str(dest),'sha256':sha(dest),'privacidad':'copia local de entrega'}],'procedimientos':['preparar.py','construir.mjs','incorporar_bases.py','verificar.py','cerrar.py'],'dependencia_previa':str(R/'outputs/avance_historico_fase3_20261027/validar_indicadores.py'),'candidata_644_aplicada':False,'commit':False,'push':False,'rama':q['rama'],'head_antes':b['git_head'],'head_despues':q['head'],'qa':'QA_FINAL.json','excel_nativo':'NO_VERIFICADO'}
manifest['hashes_procedimientos']={n:sha(O/n) for n in manifest['procedimientos']}
(O/'MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
checkpoint={'fase':4,'hitos':{'4.1':'CONSTRUIDO_PROVISIONAL','4.2':'BASES_FORMULAS_GRAFICOS_FILTROS_TRAZABLES','4.3':'PASS_CON_ALCANCE; EXCEL_NATIVO_NO_VERIFICADO'},'libro':str(dest),'sha256':sha(dest),'pendientes':'INFORME.md y hoja 05','siguiente':'Verificar apertura/recalculo nativo; resolver evidencias pendientes sin reabrir conteos ya conciliados. No aprobar automáticamente la candidata 644.','no_modificar':['fuentes','denominadores','diccionario activo'],'sin_commit_push':True}
(O/'CHECKPOINT.json').write_text(json.dumps(checkpoint,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'entrega':str(dest),'sha256':sha(dest),'qa':q['estado']},ensure_ascii=False))
