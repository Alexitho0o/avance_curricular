# Contraste por CODCLI, RUT y DV en respaldos SIES · 26-10-2026

**[C] Alcance:** carpeta `SIES/Enviados` indicada por Alexi; caso de Titulación Unificada 2026 con título observado en 2025. Las búsquedas se realizaron en el orden CODCLI exacto, RUT con DV y cuerpo de RUT, sin exportar identificadores personales. No se modificaron fuentes, bases o denominadores.

## Cobertura de la búsqueda

**[C/E]** De 389 archivos `.xlsx`, `.xlsm`, `.csv` o `.tsv` inventariados, se leyeron 377 tras un reintento; ocho agotaron el tiempo y cuatro no pudieron interpretarse como archivos Excel. El barrido literal identificó 47 archivos candidatos, que se volvieron a leer por filas y cabeceras. En esa verificación:

| Llave [C] | Archivos con al menos una fila encontrada [B/C] |
|---|---:|
| CODCLI exacto | 19 |
| RUT y DV en el mismo registro | 37 |
| Cuerpo de RUT sin DV acreditado en alguna fila | 2 |

**[C/E]** Los grupos se superponen: no se suman, no son número de personas y pueden incluir copias o extractos relacionados. Las cabeceras se detectaron en las primeras 15 filas; documentos con otra estructura, valores calculados sin caché u otros formatos podrían no identificarse. Los ocho archivos con timeout y cuatro no interpretables siguen pendientes; el detalle de rutas y resultados se conserva en el inventario privado.

## Evidencia por CODCLI

**[B/C]** `Promedio-notas-Alexi.xlsx`, hoja `Hoja1`, SHA-256 `1037f4492d7215350c8deb7ad7c827804a934f61feb3205c088b9f94d61a7d88`, tiene 62 filas de asignaturas con alguno de los tres CODCLI del caso; las 62 también coinciden en RUT y DV. Son filas, no personas. Se observa:

- Expediente `TTMRE` / plan `TTMRE20211`: actividad en 2022 y 2023.
- Expediente `TCRE` / plan `TCRE20241`: actividad en 2024 y dos filas en 2025, período nativo 1.
- Un tercer expediente `IECIRE` / plan `IECIRE20151`: actividad en 2019 y 2020, de otra carrera.

**[E]** Los períodos de actividad no establecen por sí solos fecha efectiva de migración, ni que un título se haya asignado formalmente al plan. Las filas de diversas extracciones pueden coincidir; no se suman como evidencias independientes.

## Evidencia por RUT y DV

**[B/C]** `matricula_avance_curricular_2025_control.csv`, SHA-256 `9e4cdaf0f3fbd900d67a5d5b3d1d519c82f654359794203241ea1346d8852774`, contiene una fila del mismo documento y DV con `PLAN_ESTUDIOS=TCRE20241`. El archivo no incluye CODCLI ni campo de título; refuerza la observación del plan posterior en Avance Curricular, sin ser el registro que vincula formalmente título y expediente **[E]**. No se interpreta el campo de vigencia de este proceso como vigencia de otro.

**[B/C]** `Informe de Titulados 2025_vf.xlsx`, hoja `Hoja1`, SHA-256 `676e6451eed59dae08d4cbcf99188932e0a2b586f9c3eb46f4b597721743f236`, contiene el título por documento y DV, pero no declara CODCLI ni plan, como ya se documentó. Las dos copias de `Res_Tit_Unificada` incluyen un CODCLI calculado y razones; no acreditan el plan formal del título.

## Pendientes y control

**[E]** La relación actividad CODCLI–plan está observada; falta el acto o registro que vincule el título con uno de esos expedientes y planes. Tampoco se recuperó la fórmula o regla de desempate del puntaje 2130. No se asignó ni cambió ningún plan automáticamente.

**[C]** Los procedimientos `buscar.py`, `reintentar.py`, `validar.py` y `revisar.py` registran el método; los inventarios con rutas de coincidencias se conservan bajo `~/.local/share/ipss/busqueda_tres_llaves_sies_20261026/` con permisos 0600. La segunda lectura comprueba los hashes de cada candidato antes y después; las dos fuentes de este contraste también se verificaron antes y después. Sin cambios a bases, diccionario o denominadores; sin commit ni push.
