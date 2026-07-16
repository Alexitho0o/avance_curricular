# Diagnóstico gobernado Carreras Avance Curricular 2026 / ID 16769

## Dictamen

Estado final: **BLOQUEADO**.

Declaración de carga: **NO_LISTO_PARA_CARGA**.

No se modificaron fuentes originales, no se corrigieron datos, no se generó CSV final y no se generó SIES_READY.

## A. Regla oficial

El instructivo oficial indica que la carga Carreras Avance Curricular 2026 corresponde al ID 16769, se realiza antes de Matrícula, usa la estructura del Anexo I, requiere eliminar la primera columna de institución y los encabezados para el CSV, y define DURACION_ESTUDIOS en semestres. También define TOTAL_UNIDADES_MEDIDA y UNIDADES_1ER_ANIO a UNIDADES_7MO_ANIO como enteros asociados a la distribución formal del plan.

El Anexo IV contiene el error de plataforma: “Distribución de unidades de medida no coincide con duración de la carrera”, además de la validación de suma total contra años.

## B. Dato observado

La precarga 5810 contiene 43 filas y 22 columnas. La estructura física de carga queda en 21 columnas al excluir CODIGO_IES_NUM, consistente con la indicación del manual y con la validación previa de plataforma.

El H106 tiene 43 filas y 21 columnas, pero al reproducir la validación por duración presenta 42 filas con unidades fuera de duración y 83 celdas con UNIDADES_N_ANIO en años mayores al techo(DURACION_ESTUDIOS/2).

La fuente de detalle candidata seleccionada es:

`/Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/04_gobernanza_mallas/03_auditorias/CANONICO_TODOS_PLANES_ESTUDIO_20260701_140528/02_RESULTADOS/01_CANONICO_TODOS_PLANES.tsv`

El cruce hacia las 43 carreras se obtiene mediante:

`/Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/04_gobernanza_mallas/03_auditorias/CIERRE_FINAL_43_RESUELTAS_0_PENDIENTES_20260701_171409/02_RESULTADOS/01_CONCILIACION_FINAL_43.tsv`

## C. Implementación técnica

Se reconstruyó una distribución diagnóstica desde detalle de asignaturas/planes usando CODPESTUD como puente trazable hacia CODIGO_UNICO. La unidad estable usada fue: CODRAMO usado porque RAMOEQUIV no está completo..

La conversión NIVEL -> año SIES se calculó solo como escenario técnico candidato para auditar duración. No fue aplicada como regla final.

## D. Decisión interna

El procedimiento penaliza hojas de Matrícula 5809 y PROMEDIOS para el ranking de Carreras. PROMEDIOS no se usa como fuente normativa ni como fuente de estructura de Carreras.

## E. Pendiente

NIVEL no queda gobernado como semestre ni como año formal por el manual. Hay 43 carreras bloqueadas en el diagnóstico por semántica de NIVEL, duración o necesidad de revisión. Por tanto no corresponde generar CSV final todavía.

## Conclusión

El diagnóstico corrige el rumbo de H108A: prioriza detalle de mallas/planes/asignaturas y deja fuera las hojas de matrícula 5809 como fuente de estructura de Carreras. Sin embargo, la evidencia local disponible no permite cerrar de forma automática la conversión de NIVEL a distribución anual SIES ni redistribuir unidades fuera de duración.

No se propone comando de generación de CSV final mientras el estado sea BLOQUEADO.
