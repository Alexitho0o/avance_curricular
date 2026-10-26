# Coordinación

Propósito: análisis y comunicación con evidencia. Hay diecisiete habilidades (dieciséis anteriores más la habilidad estadística transversal), y ningún activador general que obligue a cargarlas todas.

Identifica resultado pedido y proyecto con el encargo y sus fuentes, no solo con nombres. Las reglas de IPSS y PNM no se aplican a otras instituciones. Carga la habilidad dueña del resultado y sus dependencias pertinentes.

## Integración del método estadístico — siete niveles

`metodologia-estadistica-7-niveles` es **transversal a proyectos**, no una skill de IPSS. Activarla si se requiere explorar distribuciones, comparar grupos, formular hipótesis, calcular incertidumbre, ajustar modelos, detectar anomalías/fraude potencial, diseñar controles de calidad o generar código analítico Python/R/SQL/Excel/DAX. Elegir solo el nivel y técnica adecuados, no los siete mecánicamente. Calidad (nivel 6) es un control transversal al flujo y debe preceder a la inferencia; innovación (nivel 7) es opcional. No activarla por un cambio de forma, copia fiel o edición técnica sin análisis estadístico.

**Orden de autoridad:** primero la fuente y reglas propietarias del proyecto (por ejemplo, SIES para IPSS; llaves y anonimato en encuestas; gobernanza PBIR para PNM); luego el protocolo estadístico para perfilado, inferencia o modelado; finalmente el formato y comunicación. La skill estadística no tiene autoridad para cambiar universos, denominadores, fuentes, llaves, indicadores gobernados o totales congelados. Un control de calidad informa un problema y su impacto antes de proponer cambios.

| Encargo | Secuencia mínima | Entrega entre etapas |
|---|---|---|
| CSV a dos hojas idénticas | csv-a-excel-limpia | XLSX fiel; no cruce, limpieza ni dashboard automático |
| Estadística descriptiva, hipótesis o modelos con datos externos a IPSS | metodologia-estadistica-7-niveles | Fuente, grano, QA, método, ejecución o propuesta y limitaciones; no activar reglas IPSS |
| Encuestas IPSS → PPT | Cruce → estadística solo si se pide contraste/modelo → verificación IPSS solo si cita matrícula/retención → presentación | Agregados reconciliados, denominadores, fuentes/ubicaciones y límites; sin RUT/tokens en PPT |
| Inducción de personal | Inducción + secciones comunes pertinentes del cruce → estadística si se pide prueba/modelado | Libro de inducción/Buk, controles y bitácora; no segundo libro general |
| Mejorar prosa → contar historia | Humanización → storytelling solo solicitado | Canon, anclas/QA, hallazgos resueltos y evidencia |
| Nueva historia PNM | Storytelling si se pide mensaje nuevo → bookmarks + gobernanza + especialistas de objetos modificados | Guion con evidencia → storyboard → PBIR y pruebas |
| Diagnosticar visuales PNM | Rediseño + gobernanza → especialista de las fichas seleccionadas | Inventario, campos reales, ficha y alcance aprobado |
| Cifra SIES IPSS → contraste/IC/modelado → DAX/PPT | Verificación IPSS → estadística cuando procede → DAX o presentación | Definición, total/técnico/profesional, cohorte/observación, denominador, estimación e incertidumbre reales |
| Corregir un objeto PNM | Gobernanza + habilidad de ese objeto | Cambio acotado, controles; no diagnóstico global ni narrativa nueva |
| Predicción o anomalías en logística/compras | metodologia-estadistica-7-niveles | Unidad/fecha, reglas de negocio, métricas de errores, validación temporal y alertas no acusatorias |

Ficha de traspaso: proyecto, fuente, ubicación, fecha de consulta, indicador, población, período, valor original, unidad, denominador, cálculo, estado y limitaciones. Si hay inferencia/modelado, añadir n analítico, técnica, supuestos, estimación, incertidumbre, diagnósticos y estado de ejecución. Si un dato no está publicado, registrarlo así; no reconstruir denominadores invirtiendo tasas redondeadas.

## Dueños de reglas y conflictos resueltos

- IPSS posee cotejo SIES y plantilla IPSS; gobernanza PNM posee bindings, clasificación A–E y entrega Git; el humanizador posee los gates de fidelidad y storytelling importa ese módulo.
- Estadística proporciona métodos y QA sin reescribir los datos canónicos. El procedimiento específico del proyecto prevalece si hay conflicto de claves, anonimato, población o indicador; proponer cambios para revisión, no alterarlos silenciosamente.
- En inducción, población = invitados y unión Buk = email; sustituye llaves/población/período del cruce. No solicitar planificación ni trimestre académico si no corresponden.
- Un CSV dentro de otro trabajo no activa el conversor. «Limpia» no autoriza transformar datos. La skill estadística no se activa para una copia fiel.
- Humanización conserva fondo; storytelling crea narrativa trazable; bookmarks implementa navegación. Un diagnóstico narrativo no autoriza una nueva etapa. Sin bitácora, storytelling requiere solo inventario/canon/contraste del humanizador, no reescritura.
- Crear PPT ejecutivo permite síntesis respaldada en fuentes; añadir storytelling completo solo si se pide construir/revisar mensaje central. Respetar guion aprobado si existe.
- La prohibición de completar fuentes no impide el cotejo oficial IPSS solicitado: registrar la fuente nueva y no ocultar discrepancias.
- Mover/colorizar un objeto PNM sin citar/recalcular cifras no exige descargar SIES ni crear DAX. Un cambio visual no autoriza alterar modelo, grano, categorías o fuentes.
- Patrones PNM son convenciones del repositorio; verificar versiones/excepciones. Los ejemplos no son leyes universales de Power BI.
- Reutilizar autorizaciones vigentes; preguntar solo por decisiones materiales abiertas. NO VALIDADO y NO APROBADO se rotulan así; el silencio no equivale a aprobación.
- Nunca convertir faltantes en cero, promedios simples en tasas sectoriales, ni series descriptivas en causas.

Fuera del complemento: auditoría de compras UC y guiones de notas docentes. Permanecen como habilidades personales separadas; no son requisitos de un informe institucional. **El análisis estadístico de compras/logística, sin embargo, sí es compatible con la nueva skill transversal**, que no modifica esas habilidades docentes.

Para cargar una dependencia nombrada, abre `skills/<nombre>/SKILL.md` desde la raíz real del complemento. No dependas de que una habilidad local homónima esté instalada. Los módulos compartidos están en `skills/humanizar-documentos-gobernados/scripts/`; el módulo de storytelling calcula su ruta relativa.

## Diccionario personal de seguimiento IPSS

Consultar [el servicio común UMAS–SIES](diccionario-sies-seguimiento.md). Las skills comparten el puntero del proyecto; no mantienen otra tabla de equivalencias. El complemento no obtiene acceso automático a la base privada ni sustituye el QA de una edición.
