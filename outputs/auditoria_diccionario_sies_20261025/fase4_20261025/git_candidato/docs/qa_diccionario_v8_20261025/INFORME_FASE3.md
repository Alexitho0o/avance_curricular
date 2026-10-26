# Fase 3 — candidata consolidada y verificada

**B/C — Resultado:** ocho atribuciones anuales incorporadas exclusivamente a la edición candidata v8. Se conservó v7 activa. Cinco afectan a los contextos T2/T3 del Excel y tres corresponden a T1 de 2025. No se adoptaron las 16 propuestas internas ni los 12 criterios T2 pendientes.

| Alcance (B/C) | Antes | Candidata | Denominador fijo |
|---|---:|---:|---:|
| Histórico con código | 21.725 | 21.733 | 24.774 observaciones |
| Histórico pendiente | 3.049 | 3.041 | 24.774 observaciones |
| Contextos V17/V18 con código | 2.750 | 2.755 | 2.854 observaciones |
| Contextos V17/V18 pendientes | 104 | 99 | 2.854 observaciones |
| Pendientes del foco multiversión del Excel | 24 | 24 | 1.077 observaciones |

**E — No se alcanzó el 100%.** Las ocho recuperaciones reparan atribuciones documentales, no distinguen las versiones de los 24 contextos del foco multiversión. No confundir este avance con una reducción de ese foco.

**C — Hito1:** copia privada de SQLite, ocho estados previos exactos y cambios limitados a atribución/evidencia. Cuatro enlaces anuales explícitos añadidos al índice MU; no son cuatro matrículas nuevas. Los enlaces existentes permanecen iguales. Descriptor candidato separado, sin cambiar el puntero común.

**C — Hito2:** 24.774 consultas verificadas; ocho diferencias previstas y 24.766 respuestas conservadas salvo nombre de edición. Tres consumidores dan las mismas respuestas en un proceso aislado con descriptor candidato; los consumidores productivos siguen leyendo v7. Pasaron las 12 pruebas existentes y se rechazó un hash alterado.

**C — Hito3:** copia V18_CANDIDATA en Escritorio, con actualización de hojas52/54. Las 53 hojas restantes, 13 gráficos y 35 tablas conservan sus partes originales byte a byte. Se conserva el texto de todas las fórmulas; solo se actualizan seis caches dependientes y notas correspondientes. 28 controles aritméticos correctos; sin errores en hojas afectadas. Fuentes, cohortes, denominadores y tasas conservados.

**C/E — Límites de QA:** recálculo de dependencias agregadas mediante Artifact Tool y cotejo independiente; no recálculo global ni apertura en Excel nativo. Se revisaron visualmente las vistas de las hojas afectadas generadas por Artifact Tool; la copia final conserva estilos originales. Esta revisión no vuelve a certificar las tasas históricas de hojas inalteradas.

**C — Privacidad:** SQLite, operaciones individuales y copia completa del Excel fuera de Git. El Excel hereda las hojas individuales de V17 y no se publica en el repositorio. Código, descriptor sin identificadores, manifiesto y agregados se conservan localmente en el proyecto. Ningún dato subido a servicios externos.

**C — Reproducción:** consolidar.py → qa_consumidores.py; ejecutar las 12 pruebas del servicio; build.mjs con Artifact Tool → ensamblar.py → finalizar.py. Los scripts de construcción se detienen ante salidas ya existentes; no sobrescribir una edición congelada. Ensamblar usa el Python del runtime incluido con lxml. Fuentes y rutas fijadas mediante hashes en los manifiestos de fases1/2 y descriptor previo; detalle individual sólo en la ruta privada. La promoción, actualización de consumidores remotos y publicación quedan para la fase4 con autorización aplicable.

**B/C — Git:** rama feature/ire-2026; HEAD antes/después 55e3b709afb9483f0ecdd2d166f67229a454a5ef. Tres modificaciones previas conservadas por hash. Sin commit, push ni cambios al canon.
