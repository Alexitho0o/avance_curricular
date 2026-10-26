# Correcciones V14–V18 que deben conservarse

B/C — Registro de evidencias existentes. No restaura ni cambia fórmulas, bases, tasas o denominadores. El original del22-oct no es la referencia numérica vigente.

| Versión | Hoja y celdas | Corrección / resultado vigente | Tipo y estado |
|---|---|---|---|
| V14 | 26_Avance_Curricular_Resumen!D1852,E1852,F1852,H1852; 18_Foto_Intertrimestral!E8,F8; 52_Codigos_SIES_Revision!E8,G8,I8 | Cruce exacto de documentos R y P; puente explícito 2025_carga J/BU/BV. 694 presencias; 611 actividad período2 y estado VIGENTE. E1852 suma grupos de hoja53; hoja18 enlaza E1852. | B/C/D/E · fórmula + agregado + nota. Aprobado/conservado; la exigencia histórica exacta fue sustituida por D de V15. Algoritmo original600 sigue E. |
| V14 | 53_Codigos_T1_Confirmados!G54:G124,I54:I124,J54:J124 SOLO filas pares; 28_QA_Matematica!C11:F12,H11 | 36 grupos actualizados (G numerador; I tasa; J explicación). No cambiar denominadores H. 28!C11:F11 y C12:F12 cotejan611 y611/1150. | B/C · agregados + fórmulas + controles. Conservar. G tiene conteos literales reproducibles por script, no fórmulas individuales. Restaurar fórmulas no convierte estos agregados en prueba personal. |
| V15 | 26_Avance_Curricular_Resumen!D1853,E1853,F1853,H1853,A1857:H1861; 18_Foto_Intertrimestral!B82; 28_QA_Matematica!A18,A19; 52_Codigos_SIES_Revision!A1,A14,A32 | 596 presencias=582R+14P;546 VIGENTE=535R+11P. Fórmulas SUM del bloque1859:1860. Criterio interno aprobado: actividad del período y VIGENTE del extracto sin exigir fecha exacta del estado. La foto de matrícula1023/1150 sigue siendo otro indicador. | B/C/D/E · fórmula + nota. Aprobado/conservado; mecanismo original535 E, sin impedir nuevo cálculo reproducible. |
| V15 | xl/styles.xml (sin cambio de valor en celdas) | Retiro exclusivo de tres extensiones;315 estilos y22dxf conservados. No reintroducir OOXML previo al reparar fórmulas. | B/C · esquema/compatibilidad. QA histórico: apertura Excel nativa sin reparación. Este registro no ejecutó apertura nueva. |
| V16 | 18_Foto_Intertrimestral!H11,H93; D93:G93; B96 | 1360/(1471−4)=1360/1467; cuatro exclusiones internas titulados documentadas. H11 referencia H93; denominador F93 deriva de hoja53. | B/C/D · fórmula + nota. Conservar decisión interna ya documentada; no elevarla a regla oficial SIES. |
| V16 | 18_Foto_Intertrimestral!F12,H94; D94,F94,G94; B97 | 462/528 matrículas; F94=SUM(23_Foto_Renuncias_T2_2026!C6:C24). 527 personas no reemplaza528 matrículas.66 renuncias agregadas sin nómina de origen. | B/C/E · fórmula + nota. Resultado de matrículas conservado; tasa por personas E. |
| V16 | 18_Foto_Intertrimestral!H14,H95; D95:G95; B96 | 2290/(2523−4)=2290/2519; cuatro exclusiones internas documentadas. H14 referencia H95. | B/C/D · fórmula + nota. Conservar; no sustituir población por suma de subgrupos con duplicados. |
| V17 | 55_Pendientes_entrega!A1:D18 (celdas pobladas exactas en JSON) | Hoja informativa:66 renuncias sin respaldo individual; diferencia actividad/matrícula; fotos faltantes; tasa anual tresperíodos pendiente; cuatro exclusiones; promedio ponderado; límites QA. | B/C/D/E · nota/esquema. Conservar; B11=104 pendientes describe V17 y debe armonizarse con99 deV18 en una futura edición, no borrarse silenciosamente. |
| V18 | 52_Codigos_SIES_Revision!F19,H19,F20,H20,F24,H24 (solo cachés); A1,A27,A28,A32,A33 (notas); 54_Contextos_y_Pendientes!A1,A6:O228 | 2742 documentales+13 internos+99 pendientes=2854. Cinco recuperaciones enExcel; foco multiversión1040documentales+13internos+24pendientes=1077. No cambia tasa. Hoja54:221filas en6:226;227:228vacías; tabla conserva228. Fórmulas52 preservadas. | B/C/D/E · caché + agregado + nota. Edición v8 posteriormente promovida en fase4; A32 aún menciona activo v7 y debe actualizarse en edición futura. No cambiar V18 aquí. |

## Límites y pendientes de actualización

- B/C: se cotejaron los hashes reales de V17 y V18 en Escritorio con sus manifiestos. Coinciden.
- C/D: el auxiliar de actividad de2025 usa611/1150 enT2 y546/1150 enT3. La matrículaT3 mantiene1023/1150. Son indicadores distintos; no sustituir uno por otro.
- E: la nómina que origina66 renuncias sigue pendiente.462/528 es tasa de matrículas, no462/527 personas.
- B/E: V18 conserva55!B11 con104 pendientes deV17, aunque52!H24 contiene99;52!A32 aún dice activo v7, aunque el puntero común esv8. Deben corregirse las notas en la próxima edición, conservando el antecedente y sin alterar las tasas.
- C: restaurar fórmulas debe preservar el arreglo OOXML V15 y no reintroducir extensiones huérfanas. Hay conteos agregados legítimamente literales; su reproducción está en scripts y evidencias, no necesariamente en fórmula de celda.
- E: no se vuelve a certificar la apertura nativa, todo el libro ni las fuentes individuales. Los QA V14–V18 se registran como antecedentes existentes.
- C: el JSON contiene las206 entradas de EDICION V14–V16 y las coordenadas efectivamente cambiadas enV18. Los listados exactos distinguen modificaciones de contenido/caché y estilo.

## Evidencias y hashes recalculados

- B · V14: `/Users/alexi/Documents/GitHub/avance_curricular/outputs/correccion_proxy_t2_2025_20261023_v14/MANIFEST_CORRECCION.json` — `4ea0af16a5494509c317f8784afcb03b376f8fb5fd74763593b4d5a39964efc0`.
- B · V15: `/Users/alexi/Documents/GitHub/avance_curricular/outputs/correccion_proxy_t3_2025_20261023_v15/MANIFEST_CORRECCION.json` — `1a82de7f94cecb8395c193546153a19cd2cf79b05a01fd9fbf130a7046ad1d62`.
- B · V16: `/Users/alexi/Documents/GitHub/avance_curricular/outputs/aclaracion_tasas_2026_20261023_v16/MANIFEST_TASAS_2026_V16.json` — `d5abc95698866c61aa2757dc5df1c0713edfd4428095d4386dd8ad4841547a2b`.
- B · V17: `/Users/alexi/Documents/GitHub/avance_curricular/outputs/pendientes_entrega_20261024_v17/QA_Y_MANIFEST.json` — `dca094f6234ecd3db711d58e30169134ea7e199887fedee02abf59f7fd45acc0`.
- B · V18: `/Users/alexi/Documents/GitHub/avance_curricular/outputs/auditoria_diccionario_sies_20261025/fase3_20261025/QA_EXCEL.json` — `1a3057e8e91b82f4586d4d948590bc553be4684226ae8f8bb6697f8db315e5b0`.

## Fuentes anuales ya inventariadas

| Año | Fuente / hoja | Filas reportadas | Alcance del corte |
|---|---|---:|---|
| 2022 | /Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/Datos DAI (RAW) - 1.1 Datos crudos/1.2.1 Datos Institucionales/1.2.1.1 SIES/Enviados/Matrícula Unificada/2022/2022.csv / CSV | 1038 | B/E: inventario previo; fecha efectiva no acreditada aquí. |
| 2023 | /Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/Datos DAI (RAW) - 1.1 Datos crudos/1.2.1 Datos Institucionales/1.2.1.1 SIES/Enviados/Matrícula Unificada/2023/2023.csv / CSV | 1145 | B/E: inventario previo; fecha efectiva no acreditada aquí. |
| 2024 | /Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/Datos DAI (RAW) - 1.1 Datos crudos/1.2.1 Datos Institucionales/1.2.1.1 SIES/Enviados/Matrícula Unificada/2024/08-05-2024_18-31-54_Matrícula_Pregrado_2024.csv / CSV | 1541 | B/E: inventario previo; fecha efectiva no acreditada aquí. |
| 2025 | /Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/Datos DAI (RAW) - 1.1 Datos crudos/1.2.1 Datos Institucionales/1.2.1.1 SIES/Enviados/Matrícula Unificada/2025/2025.xlsx / 08-05-2025_22-26-22_Matrícula_P | 2371 | B/E: inventario previo; fecha efectiva no acreditada aquí. |
| 2026 | /Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/Datos DAI (RAW) - 1.1 Datos crudos/1.2.1 Datos Institucionales/1.2.1.1 SIES/Enviados/Matrícula Unificada/2026/REPORTE JULIO 2026/MATRICULA_UNIFICADA_PREGRADO_2026_CONSOLIDADA_FINAL_CON_ENCABEZADOS.xlsx / CONSOLIDADO | 4105 | B/E: inventario previo; fecha efectiva no acreditada aquí. |

B/C — El esquema conserva COD_SED, COD_CAR, JOR y VERSION. La conciliación por código completo se puede apoyar en estos componentes; no requiere suponer que COD_CAR solo es el código completo.
E — La carpeta Enviados y el nombre de un archivo no acreditan por sí solos aceptación SIES. Los cortes y cadenas envío/retorno deben quedar conectados por proceso/año. Matrícula total, retención elegible y titulaciones no comparten automáticamente universo.
