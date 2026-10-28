# Retención de 1er año · indicador interno H001

**Indicador interno alineado con la definición oficial SIES; no es la tasa oficial.** Activación interna aprobada por Alexi el 28-10-2026. La regla solo activa el componente 1; el subproyecto conserva los estados de sus demás componentes.

| Cohorte | Casos H001 | Retenidos H001 | Tasa H001 | Tasa SIES publicada | Brecha H001 − SIES |
|---:|---:|---:|---:|---:|---:|
| 2022 | 305 | 224 | 73,44% | 68,95% | +4,49 pp |
| 2023 | 366 | 258 | 70,49% | 70,57% | −0,08 pp |
| 2024 | 558 | 326 | 58,42% | 67,50% | −9,08 pp |
| 2025 | 1.150 | 668 | 58,09% | 58,21% | −0,12 pp |

Las brechas de 2022 y 2024 mantienen causa E y sus escenarios constan en `outputs/retencion_vig_por_proceso_20261028/INFORME.md`. Las cifras 2023 y 2025 son cercanas, no idénticas. En 2025 H001 tiene 13 casos y nueve retenidos menos que los 1.163 casos y 677 retenidos del correo SIES; H001 distribuye esas diferencias entre nueve códigos. La causa individual sigue E. Los 92 no considerados de SIES no forman parte de los 1.163 casos. No se igualan denominadores.

## Salidas y método

`RETENCION_PRIMER_ANIO_AGREGADO.json` contiene datos por cohorte institucional, sector y carrera: personas, retenidos y tasa = retenidos / casos. La unidad es persona por cohorte, comprobada para las cuatro cohortes. En las agrupaciones con menos de diez casos, los tres valores se suprimen (null); no se convierten a cero. La suma de grupos antes de suprimir coincide con el total de cada cohorte. El mapeo de 17 códigos de carrera a sector corresponde a `analisis_desercion_ipss/reglas/MAPEO_SECTOR_IPSS_H001.json`, verificado contra V24 hoja `8_Mapeo_Sector_IPSS`, B6:D22 y el hash registrado en ese archivo.

El código H001 y los datos del diagnóstico y catálogo congelados están documentados en `analisis_desercion_ipss/reglas/REGLA_RETENCION_PRIMER_ANIO.json`. El prototipo de presencia con cualquier VIG permanece únicamente como función de sensibilidad histórica, fuera del flujo principal.

## Anexo institucional: escenario de nóminas 2026 (E)

Según `data/reglas_negocio/mu2027/estudio/RESULTADOS_AGREGADOS.json`, 291 personas de las nóminas están en la cohorte interna H001 2025 y 276 de ellas tienen una matrícula 2026 de la misma cohorte de origen con VIG=0. Si exclusivamente esas 276 se contaran como retenidas, el escenario sería **944/1.150 = 82,09%**, en lugar de 668/1.150 = 58,09%.

Este ejercicio no modifica VIG ni es tasa oficial. Requiere el fundamento académico y temporal de quien preparó la carga; no se dispone de un enlace demostrado para atribuir a esas personas el numerador o denominador oficial de SIES. Las 960 filas VIG=0 del envío no equivalen a 960 personas de esta cohorte.

## QA

Se compararon los cuatro pares H001 con los controles de la auditoría, se verificó una persona por cohorte y se conciliaron sumas por sector y carrera antes de la supresión. Mapeo sectorial: 17/17 filas iguales a V24 con su hash; clasificación ausente produce error. Se comprobó que un grupo por carrera quedó bajo el umbral y suprimido, que las tasas publicables son cociente de conteos y que la lógica del prototipo no forma parte del flujo principal. El detalle individual no se incorpora en estas salidas.
