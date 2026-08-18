# Perfil tecnico - Entrega Etapa 2 (Oferta Academica Nueva TP Adscritas)

Archivo: Oferta 2027 Etapa2_prueba_1.xlsx
Generado: 2026-08-28T03:36:19.759863
Fuente: copia gobernada en 03_fuentes_institucionales/entregas_docencia/20260827_etapa2_entrega_01/ (no se modifico el original)

## Estructura general

- Hojas: 1 (Hoja4)
- Dimensiones declaradas: A1:AW55 (max_row=55, max_col=49)
- Encabezados en fila 1: 49 encabezados leidos correctamente (posiciones 1 a 49, columnas A a AW)
- Filas de datos con contenido: 50 (de un maximo de 54 filas debajo del encabezado)
- Filas completamente vacias: [52, 53, 54, 55] -> corresponden a las filas 52-55 (cola del archivo, sin datos). Los registros de oferta reales ocupan filas 2 a 51 (50 registros).
- Columnas vacias en todo el rango: ['C', 'AN'] -> C=COD_CARRERA (vacio en 100% de las filas, consistente con la regla del manual de que COD_CARRERA debe quedar vacio) y AN=RECONOCIMIENTOS_APREN_PREVIOS (vacio en 100% de las filas, pendiente de determinar si es obligatorio segun el contrato de Etapa 2).
- Columnas ocultas: ['S'] -> S=ACREDITACION esta oculta en el libro recibido.
- Filas ocultas: ninguna
- Celdas combinadas: ninguna
- Celdas con formula: 0
- Celdas con comentario: 0
- Errores de Excel (#N/A, #REF!, etc.): ninguno detectado
- Numeros almacenados como texto: 0 celdas detectadas en los campos categoricos analizados.
- Espacios invisibles / dobles espacios en texto: 0 celdas detectadas por el patron aplicado (se recomienda una segunda pasada dirigida en Fase 5 sobre NOMBRE_CARRERA y NOMBRE_TITULO).

## Duplicados

- El detector de filas identicas completas marco las filas [52, 53, 54, 55] como "duplicadas". Estas son exactamente las 4 filas completamente vacias (52-55), que coinciden entre si por estar todas en blanco. NO se detectaron filas de datos reales (2-51) identicas entre si en todas sus columnas. La duplicidad real por clave diagnostica (sede + carrera + modalidad + jornada + tipo de plan + nivel + titulo) se evalua en la Fase 4 (conciliacion) y Fase 5 (validacion), no en el perfilamiento.

## Marcas de color observadas (institucionales, sin interpretacion normativa)

- Relleno rojo (FFFF0000) en 69 celdas, distribuidas de forma dispersa, concentradas en columnas de duracion (DURACION_REGIMEN, DURACION_ESTUDIOS, DURACION_TOTAL, DURACION_TITULACION) y en la fila 50, ademas de celdas puntuales en COD_SEDE/NOMBRE_SEDE/COD_CARRERA/NOMBRE_CARRERA en filas 5, 12 y 48. Aparenta ser una marca propia de la institucion (posible senal de dato dudoso o pendiente de revision interna), no una marca de SIES. Se registra como REVISION_MANUAL por fila/columna en la Fase 5, sin asumir su significado.
- Relleno con color de tema (no RGB directo) en la fila 49, aplicado de forma casi transversal a todas las columnas de esa fila. Se interpreta como una marca de atencion sobre el registro completo de la fila 49. Se registra para consulta a la institucion sobre su motivo.

## Tipos de datos observados por columna (resumen)

Ver TSV adjunto (PERFIL_ENTREGA_ETAPA2_20260827_etapa2_entrega01.tsv) para el detalle columna por columna: tipos observados, cantidad de valores unicos, vacios y no vacios.

Columnas con menos de 25 valores distintos (candidatas a campos categoricos/codificados) tienen su catalogo de valores observados almacenado en el JSON completo (PERFIL_ENTREGA_ETAPA2_20260827_etapa2_entrega01.json), campo `valores_unicos_muestra`.

## Hallazgos relevantes para fases siguientes (sin corregir nada en esta fase)

1. COD_CARRERA vacio en el 100% de los registros: consistente con la regla del manual (se asigna despues del cierre). No requiere accion.
2. VERSION tiene valores en 40 de 50 registros reales (1, 2 o 3) y esta vacio en 10. El manual indica que VERSION "no corresponde" en esta etapa; se debe confirmar en la Fase 3 (contrato de columnas) si esto significa que la columna se ignora en la carga o que debe eliminarse/quedar vacia, sin asumir un tratamiento.
3. RECONOCIMIENTOS_APREN_PREVIOS vacio en el 100% de los registros: se debe confirmar en el contrato de columnas si es un campo obligatorio, condicional o si aplica "NO APLICA" segun el manual.
4. La columna ACREDITACION esta oculta en el archivo recibido pero contiene datos (valor unico observado: 2, en 47 de 50 registros; 3 registros sin dato). Ocultar una columna no la excluye de la validacion.
5. La ultima columna del archivo se llama "SECTOR IPSS" (con espacio, no con guion bajo como el resto de los encabezados). Este nombre no aparece en la lista de campos citados por el usuario ni sigue la convencion NOMBRE_CON_GUION_BAJO del resto de la estructura. Se marca como columna a verificar contra la estructura oficial de Etapa 2 en la Fase 3; no se elimina ni se ignora sin confirmacion.
6. La fila 49 tiene una marca de color de tema aplicada a casi todas sus columnas: se registra como revision manual antes de continuar.
7. Los 50 registros reales estan en filas 2-51; las filas 52-55 estan vacias y deben excluirse del conteo de "registros de oferta detectados".

## Archivos generados en esta fase

- JSON completo: 06_validaciones/PERFIL_ENTREGA_ETAPA2_20260827_etapa2_entrega01.json
- TSV resumido: 06_validaciones/PERFIL_ENTREGA_ETAPA2_20260827_etapa2_entrega01.tsv
- Markdown ejecutivo: 06_validaciones/PERFIL_ENTREGA_ETAPA2_20260827_etapa2_entrega01.md (este archivo)
