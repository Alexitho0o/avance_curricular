# Preparación de reconstrucción acumulativa MU2026

Estado: PREPARADO_NO_EJECUTADO. C/E: las llaves candidatas no están acreditadas como llave normativa PES.

## Base oficial [A]

Manual MU2026 p.15, líneas 468–478: cargas acumulativas, actualización al cargarse correctamente y resultado Finalizado. P.16, líneas 483–498: Historial de Carga ordenado por fecha y acción ver el archivo cargado.

Manual: /Users/alexi/Documents/GitHub/avance_curricular/manual_matrícula_unificada.txt. SHA-256: `ce2dda6e32df94012679718e6e20f58a97fcf4ddf7038be5046d5d17238a67c9`.

## Lo que descargará Alexi

1. Export o captura del Historial de Carga MU2026, con fechas, resultados y evidencia disponible de reinicios/eliminaciones.
2. El archivo cargado de cada fila Finalizado, vinculado a esa fila y conservado con SHA-256 en privado.

No se reconstruirá con nuestros envíos locales, archivos orig.zip, PARA_SUBIR ni reportes de errores.

## Antecedente: las formulaciones originales eran equivalentes [C]

Con institución I162 fija, código completo coherente y componentes normalizados, las dos formulaciones originales son equivalentes. La segunda se reemplaza por documento + COD_CAR para ofrecer una sensibilidad distinta.

## Dos llaves vigentes de sensibilidad [C/E]

| Llave | Campos |
|---|---|
| L1 | Tipo documental + número + DV + código único |
| L2, gruesa | Tipo documental + número + DV + COD_CAR; sin sede, jornada ni versión |

L1 conserva sede, jornada y versión dentro del código único; L2 agrupa por documento + COD_CAR y puede unir contextos distintos. Ambas son sensibilidad C/E, no llave normativa PES acreditada.

## Hipótesis que se evaluará, sin ejecutar [C/E]

Si L1 reproduce la publicación mejor que L2, y el linaje identifica registros antiguos no sobrescritos bajo L1 que L2 sustituye.
Los registros antiguos no sobrescritos son una explicación candidata, no aceptación SIES ni demostración causal.
Comparar discrepancia absoluta total por código y cantidad de códigos coincidentes, en el mismo universo pregrado; mostrar también el neto y el foco de 48 códigos, sin elegir por compensación de diferencias. Si las métricas discrepan, informar el resultado mixto.

## Procedimiento futuro, no ejecutado

1. Verificar hashes y relación archivo recibido ↔ fila del historial. Admitir sólo Finalizado; documentar errores y faltantes sin aplicarlos.
2. Acreditar el orden de aplicación y cualquier eliminación/reinicio antes de acumular; no asumir que no existieron.
3. Mantener dos estados en paralelo, indexados por L1 documento + código único y L2 documento + COD_CAR. Una llave repetida reemplaza el registro completo con el de la carga posterior; VIG 0 actualiza, no elimina físicamente.
4. Duplicados incompatibles dentro de una carga o sin orden acreditado bloquean el grupo; no elegir primera ni última fila por conveniencia.
5. Conservar linaje de cada llave: primera carga, última carga, cambios VIG, y si una llave antigua nunca volvió a ser sobrescrita.
6. Conciliar ambos estados en privado y producir sólo agregados VIG1/VIG0 por código, incluidas altas antiguas no sobrescritas; separar registros de L1 que la llave gruesa L2 sustituye.
7. Comparar con 3.371 pregrado publicados y 3.145 VIG1 nuestras, más los 48 códigos con diferencia; no ajustar bases ni tasas.

Fuentes faltantes y controles se detallan en el JSON. No se informa aún VIG1 reconstruida ni número de llaves antiguas.
