# Glosario operativo

| Término | Definición operativa | Unidad | Clase | Fuente exacta |
|---|---|---|---|---|
| Cohorte de 1er año | Personas que ingresan por primera vez al programa/institución en el año de cohorte del cálculo | Persona/cohorte | A | `procesos/caracterizacion/gobernanza/sies/RETENCION/REGLA_RETENCION_1ER_ANIO_CORREO_20260909.txt` |
| Fecha de referencia | Corte oficial de matrícula usado para determinar permanencia: 30 de abril | Fecha/corte | A | Regla oficial SIES; `docs/ESPECIFICACION_BASES_TASAS_2026_V16_20261023.md` |
| t+1 | Año académico siguiente al año de ingreso de la cohorte | Persona/cohorte | A/C | Regla oficial SIES; especificación del indicador |
| Retención de 1er año | `personas retenidas en t+1 / personas elegibles de la cohorte`; se calcula como suma de numeradores dividida por suma de denominadores, nunca como promedio de porcentajes | Persona/cohorte | A/C | Regla oficial SIES; `docs/ESPECIFICACION_RETENCION_INTERMEDIA_T2_T3_20261021.md` |
| Salida de IPSS | Persona no matriculada en IPSS en la MU de t+1 al 30 de abril; no prueba por sí sola deserción | Persona/cohorte | D | Decisión del subproyecto; regla oficial para el corte |
| Cambio de carrera dentro de IPSS | Persona que aparece en otra carrera de IPSS en t+1; cuenta como retenida institucional, aunque no necesariamente retenida en la carrera de origen | Persona/cohorte | D | Decisión del subproyecto; regla oficial de institución |
| Salida entre períodos | No observación en el siguiente corte intertrimestral; pertenece al componente 2 y no se presenta como retención oficial SIES | Persona/período | D/C | `data/reglas_negocio/indicador_intertrimestral/REGLA.json` |
| Cambio de institución | Persona matriculada en otra institución en t+1; requiere vínculo verificable RUT–MRUN | Persona/cohorte | E | Componente 3; `data/catalogo_datos/CATALOGO_DATOS_IPSS.json` y fuentes MRUN |
| Deserción del sistema | Persona sin matrícula en ninguna institución en t+1; requiere vínculo verificable RUT–MRUN | Persona/cohorte | E | Componente 3; fuentes MRUN |
| Interrupción/reincorporación | Persona que no aparece en el corte inmediato y vuelve a observarse en t+2 o después; no se etiqueta como deserción automáticamente | Persona/cohorte | D/E | Decisión del subproyecto; evidencia longitudinal |
| Titulado/egresado | Persona con titulación o egreso acreditado; se excluye del denominador solo si así lo establece la regla oficial aplicable | Persona/cohorte | A/E | Regla oficial SIES; fuente institucional de titulados |
| Sin determinar | No existe evidencia suficiente para clasificar la trayectoria o el destino | Persona/cohorte | D | Principio no inferencial del subproyecto |
| No aplica | Caso fuera del alcance definido; no equivale a cero, salida ni deserción | Persona/cohorte | D | Decisiones vigentes y reglas del componente |
| Numerador | Personas retenidas, cada persona una vez por cohorte | Persona | C | Regla de agregación del subproyecto |
| Denominador | Personas elegibles, cada persona una vez por cohorte | Persona | C | Regla de agregación del subproyecto |
