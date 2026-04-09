# Confirmación de gobernanza PROMEDIOSDEALUMNOS

Fuente vigente identificada: `/Users/alexi/Downloads/PROMEDIOSDEALUMNOS_7804.xlsx`  
SHA-256: `7911e0de3b9ec5df70b6667161e94a2f6751bc5f3c24ba55cce5dbcea35ef19d`

La copia congelada de Avance Curricular en `00_fuentes_congeladas` es físicamente idéntica a la fuente vigente. Las copias `PROMEDIOSDEALUMNOS_7804.xlsx` en raíz e `input/` tienen la misma estructura pero otro hash, por lo que quedan como evidencia histórica/no vigente, no como versión operativa paralela.

## Funcionamiento actual confirmado

### Matrícula Unificada
El flujo vigente opera principalmente mediante catálogo CODCLI y consolidación controlada por CODCLI/oferta. Conserva archivo, hoja, fila y columna de evidencia para CODCLI; controla hash de catálogo, hashes de archivos operativos, conflictos, múltiples CODCLI y vigencia. Brecha real acotada: documentar de forma explícita el vínculo con la fuente PROMEDIOS vigente de Descargas o copia congelada cuando corresponda.

### Estudiantes Extranjeros
El flujo vigente conserva base académica normalizada, cruce Hoja1/DatosAlumnos, línea de tiempo por CODCLI, MULTICODCLI, vigencia, nacionalidad/residencia, validación end-to-end, regresión y manifiestos PES. Brecha real acotada: el cierre final no deja explícito el hash de PROMEDIOS Descargas como origen de los normalizados.

### Avance Curricular
El flujo vigente congela PROMEDIOS con hash idéntico a Descargas, genera derivados TSV, separa 5809/5810, valida la cadena 5809.RUT+DV -> DatosAlumnos.RUT -> CODCLI -> Hoja1.CODCLI -> CODCARR/PLAN/asignaturas. El caso CIIND y el cierre corregido 41/2 documentan controles y pendientes. Brechas reales: completar pendientes documentados y generalizar controles multicodcli/multiplan a todos los casos complejos, sin rediseñar lo ya gobernado.

## Cierre
No existe evidencia de una razón técnica general para detener la conciliación actual. Sí existen brechas reales acotadas y documentales/puntuales que deben resolverse antes de cerrar los casos pendientes específicos.
