# Retención de 1er año · indicador interno H001

**Indicador interno alineado con la definición oficial SIES; no es la tasa oficial.** Activación interna aprobada por Alexi el 28-10-2026. La regla solo activa el componente 1; el subproyecto conserva los estados de sus demás componentes.

| Cohorte | Casos H001 | Retenidos H001 | Tasa H001 | Tasa SIES publicada | Brecha H001 − SIES |
|---:|---:|---:|---:|---:|---:|
| 2022 | 305 | 224 | 73,44% | 68,95% | +4,49 pp |
| 2023 | 366 | 258 | 70,49% | 70,57% | −0,08 pp |
| 2024 | 558 | 326 | 58,42% | 67,50% | −9,08 pp |
| 2025 | 1.150 | 668 | 58,09% | 58,21% | −0,12 pp |

Las brechas de 2022 y 2024 mantienen causa E, documentada en `manifests/milestones/H001-RETENCION-IPSS162/README.md`. Las cifras 2023 y 2025 son cercanas, no idénticas. En 2025 H001 tiene 13 casos y nueve retenidos menos que los 1.163 casos y 677 retenidos del correo SIES; H001 distribuye esas diferencias entre nueve códigos. La causa individual sigue E. Los 92 no considerados de SIES no forman parte de los 1.163 casos. No se igualan denominadores.

## Salidas y método

`RETENCION_PRIMER_ANIO_AGREGADO.json` contiene datos por cohorte institucional, sector y carrera: personas, retenidos y tasa = retenidos / casos. La unidad es persona por cohorte, comprobada para las cuatro cohortes. En las agrupaciones con menos de diez casos, los tres valores se suprimen (null); no se convierten a cero. La suma de grupos antes de suprimir coincide con el total de cada cohorte. El mapeo de 17 códigos de carrera a sector corresponde a `analisis_desercion_ipss/reglas/MAPEO_SECTOR_IPSS_H001.json`, verificado contra V24 hoja `8_Mapeo_Sector_IPSS`, B6:D22 y el hash registrado en ese archivo.

El código H001 y los datos del diagnóstico y catálogo congelados están documentados en `analisis_desercion_ipss/reglas/REGLA_RETENCION_PRIMER_ANIO.json`. El prototipo de presencia con cualquier VIG está descartado para el cálculo: no acredita la misma cohorte de origen ni la condición de matrícula vigente.

## Documentación de generación MU 2026

Para la generación y cierre MU 2026, consultar `control/reportes/decision_operativa_mu_2026.md`, `control/reportes/ejecucion_oficial_mu_2026.md`, `control/gate/gate_final_mu_2026.md` y `CIERRE_PES_READY_MU2026.md`.

## QA

Se compararon los cuatro pares H001 con los controles de la auditoría, se verificó una persona por cohorte y se conciliaron sumas por sector y carrera antes de la supresión. Mapeo sectorial: 17/17 filas iguales a V24 con su hash; clasificación ausente produce error. Se comprobó que un grupo por carrera quedó bajo el umbral y suprimido, que las tasas publicables son cociente de conteos y que la lógica del prototipo no forma parte del flujo principal. El detalle individual no se incorpora en estas salidas.
