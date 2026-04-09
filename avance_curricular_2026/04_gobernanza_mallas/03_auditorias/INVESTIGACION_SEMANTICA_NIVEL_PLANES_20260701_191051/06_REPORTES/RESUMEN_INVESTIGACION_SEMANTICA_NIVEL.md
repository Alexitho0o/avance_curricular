# Resumen investigacion semantica de NIVEL

## Resultado

Conclusion global: **NIVEL_CURRICULAR_SIN_EQUIVALENCIA**.  
Estado para recalculo: **NO_APTO_PARA_RECALCULO**.

La columna `NIVEL` del Excel institucional se observa como atributo curricular de asignatura por `CODPESTUD`, relacionado con `CODRAMO`, `CREDITO` y la estructura de la malla. No se encontro definicion explicita en el libro, ni formulas, comentarios, nombres definidos u hojas auxiliares que establezcan que `NIVEL` sea semestre o anio.

## Evidencia principal

- Libro revisado: `/Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/01_fuentes_institucionales/planes_estudio/Listado_Planes_estudio_Sedes_RE_CO_20260701.xlsx`.
- Hojas revisadas: 1.
- Hoja principal: `BBDD Bruta`.
- Columnas: 29.
- Posicion de `NIVEL`: 12.
- Planes funcionales analizados: 16.
- Codigos bloqueados por niveles analizados: 33.

## Conclusion operativa

No corresponde aplicar aun la conversion `1-2 -> anio 1`, `3-4 -> anio 2`, etc. La equivalencia temporal de `NIVEL` no esta demostrada para los planes afectados. Los 33 casos bloqueados deben seguir bloqueados hasta contar con una fuente institucional que defina `NIVEL` y su conversion a anio/semestre para la carga de Carreras.

## Control

No se modificaron fuentes, matrices funcionales ni auditorias previas. No se genero archivo de carga.
