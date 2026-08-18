# Conciliacion Etapa 2 vs Reporte 5912 (Oferta Vigente Validada Etapa 1)

Registros institucionales evaluados (filas reales 2-51 del archivo recibido): 50
Registros del reporte 5912 (Etapa 1 validada) usados como referencia: 103

## Resumen por clasificacion

- NUEVO_NO_PRESENTE_EN_ETAPA1: 22
- POSIBLE_DUPLICADO_ETAPA1: 18
- REQUIERE_REVISION_MANUAL: 4
- NUEVA_SEDE: 4
- NUEVA_JORNADA: 1
- NUEVO_TIPO_PLAN: 1

## Hallazgo principal

**18 de 50 registros (36%)** del archivo institucional coinciden EXACTAMENTE (sede, carrera, modalidad, jornada, tipo de plan, nivel y titulo) con un registro ya presente en la Oferta Vigente Validada (reporte 5912). El instructivo indica textualmente (Anexo 4, pag. 63): 'La Carrera o Programa que esta ingresando como nueva, ya existe en la Oferta Vigente Validada.' Estos registros NO deben cargarse como oferta nueva sin antes confirmar con Docencia si corresponden a un error de la planilla de trabajo o si la intencion es otra (por ejemplo, dar de baja o corregir vigencia de un programa ya vigente, lo cual es un proceso distinto a Etapa 2 Oferta Nueva).

Ningun registro se declaro identico solo por coincidencia de nombre: la clasificacion exige coincidencia en las 7 dimensiones de la llave diagnostica (sede + nombre de carrera + modalidad + jornada + tipo de plan + nivel + titulo), y los casos de similitud textual sin coincidencia exacta se marcaron como REQUIERE_REVISION_MANUAL, no como duplicado.

## Limitacion metodologica registrada

No se pudo evaluar la categoria FALTANTE_ETAPA1 (programas que debieron incluirse en la Etapa 1 y no lo fueron) porque el repositorio no contiene el archivo de la carga original de Etapa 1 previa a validacion, solo el reporte 5912 ya validado. Determinar 'faltantes' respecto de una carga que no esta disponible como fuente requeriria informacion adicional de Docencia.

## Archivos de esta fase

- TSV detalle (ambos lados de la comparacion): 06_validaciones/CONCILIACION_ETAPA2_VS_REPORTE_5912_20260827.tsv
- JSON completo: 06_validaciones/CONCILIACION_ETAPA2_VS_REPORTE_5912_20260827.json
- Markdown ejecutivo: 06_validaciones/CONCILIACION_ETAPA2_VS_REPORTE_5912_20260827.md (este archivo)