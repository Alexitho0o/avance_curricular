# D2 — Investigación de excepciones y cobertura

Especificación previa. Reutilizar B4/B5 y la carga congelada de fuentes; no
reconstruir agrupaciones nominales ni modificar reglas o entregas anteriores.
H4 revisa los 16 contextos por Código Único, oferta/admision anual, campos de
origen/ingreso actual del reporte y estado/situación UMAS disponibles. Separar
estado actual de estado histórico. La vigencia en el año de observación permite
coexistencia; solo se contrasta admisión con el año de ingreso al episodio, cuya
semántica/cobertura debe quedar explícita. No eliminar destinos por mayoría.

H5 relee CILOG en el extracto 12023 usado en B4/B5 y contrasta la muestra previa
11998, que es otro corte. Actividad por misma carrera/expediente y documento
verificado; antecedente técnico por catálogo existente y episodios observados.
No atribuir procedencia externa por ausencia ni usar ANOINGRESO heredado como
inicio real. No exportar identidades, documentos, CODCLI ni hashes personales.

H6 registra búsqueda acotada de fuentes de oferta anterior a 2010, cortes UMAS
y catálogos curriculares en ambos proyectos y las carpetas institucionales
señaladas por el usuario. Una fuente localizada no equivale a evidencia leída.
Conservar originales y registrar límites de búsqueda, accesibilidad y cobertura.

Entregables: expediente agregado por cada contexto, CILOG por mecanismo,
contraste de cohortes/admisión, registro de búsquedas y brechas por categoría D1.
Los dictámenes pueden cerrar la investigación de esta edición como no determinable;
no implican resolver las equivalencias. Scripts/pruebas aislados conforme al layout.

## H4 — Resultados de los 16 expedientes

Se releyeron las fuentes B5 verificadas por sus hashes y se reprodujo en memoria
la atribución por documento/familia y la presencia UMAS. Se publican solo estratos
académicos, sin RUT, CODCLI, MRUN ni hashes personales. La atribución documental
es parcial en cinco contextos; el expediente explicita cuántas personas del
contexto tienen reporte atribuible. No se extrapola el detalle a las restantes.

En 14 contextos hay coexistencia de códigos con nuevos estudiantes y solo
antiguos en el año observado. En los otros dos, todos los destinos observados
están declarados solo con antiguos. Coexistencia no equivale a error ni resuelve
la correspondencia con una malla UMAS. El año de ingreso actual SIES por sí solo
separa los destinos en uno de los 16 contextos; combinar ingreso original y
actual los separa en dos. Es una partición descriptiva sobre la misma evidencia,
no una regla nueva validada ni una conversión de campos SIES a UMAS.

| Contexto | Carrera UMAS | Año | Personas del contexto con reporte atribuible / total | Declaración anual observada | Ingreso declarado en año solo antiguos¹ |
|---|---|---:|---:|---|---:|
| B4-00362 | IECIRE | 2019 | 3/3 | Nuevos y antiguos | 0 |
| B4-00465 | IECIRE | 2019 | 3/3 | Nuevos y antiguos | 0 |
| B4-00480 | IECIRE | 2020 | 3/5 | Nuevos y antiguos | 2 |
| B4-00575 | IECIREOL | 2022 | 9/9 | Nuevos y antiguos | 1 |
| B4-00778 | IETMRE | 2019 | 2/2 | Nuevos y antiguos | 0 |
| B4-00783 | IETMRE | 2019 | 7/7 | Nuevos y antiguos | 0 |
| B4-00788 | IETMRE | 2020 | 2/2 | Nuevos y antiguos | 0 |
| B4-00793 | IETMRE | 2020 | 5/5 | Nuevos y antiguos | 0 |
| B4-00844 | IETMREOL | 2020 | 3/4 | Nuevos y antiguos | 1 |
| B4-00866 | IETMREOL | 2022 | 62/64 | Nuevos y antiguos | 0 |
| B4-01646 | TPCRE | 2019 | 5/5 | Nuevos y antiguos | 0 |
| B4-01654 | TPCRE | 2020 | 2/3 | Solo antiguos | 1 |
| B4-01712 | TPCRE | 2019 | 2/3 | Nuevos y antiguos | 0 |
| B4-01716 | TPCRE | 2019 | 4/4 | Nuevos y antiguos | 0 |
| B4-01738 | TPCREOL | 2019 | 2/2 | Nuevos y antiguos | 0 |
| B4-01748 | TPCREOL | 2020 | 4/4 | Solo antiguos | 1 |

¹ Conteo de observaciones persona/estrato, no personas únicas entre contextos.
Son seis observaciones en cinco contextos: tres con estado actual ELIMINADO /
3 - ELIMINACION AUTOMATICA; una ELIMINADO / 24 - CAMBIO DE CARRERA; dos TITULADO /
31 - TITULADO APROBADO. Por tanto, no son exclusivamente eliminados. El estado
actual no determina su estado en el año histórico ni explica por sí solo la
incidencia de admisión. Se requieren antecedentes del episodio y corte reportado.

Ejemplos que delimitan el resultado:

- B4-00362, IECIRE, 2019: V1 solo antiguos y V2 con nuevos. Los mismos años de
  ingreso del reporte no separan los códigos. Permanece indeterminada la selección
  UMAS aunque la coexistencia sea compatible con mantener cohortes antiguas.
- B4-00844, IETMREOL, 2020: el ingreso original SIES distingue un antecedente 2013
  de otro 2019, pero UMAS agrupa el contexto con ingreso original 2019. La
  distinción SIES no se puede trasladar como si UMAS tuviera ese mismo dato.
- B4-01748, TPCREOL, 2020: ambos códigos son solo antiguos. V2 tiene ingreso actual
  2016 sin oferta localizada para ese código/año; V1 incluye un ingreso actual
  2020 cuando declaraba solo antiguos. Separar los años no sanea esas incidencias.
- I162S2C1J4V1 aparece solo antiguos en 2020 y con nuevos en 2022. La vigencia debe
  consultarse año por año: una primera marca solo antiguos no permite imponer
  automáticamente un cierre permanente de admisión.

**Dictamen H4:** se aporta explicación de coexistencia y se localizan discrepancias;
ninguno de los 16 expedientes acredita todavía una selección unívoca de malla.
La causa institucional de cada discrepancia permanece no determinable con las
fuentes disponibles. [Detalle completo](../data/cierre_d2/20261016/expedientes_16.json).

## H5 — Continuidad y CILOG

Se conservó la agrupación existente: CILOG / RE / O tiene perfil de continuidad,
tipo 3 y duración total de cuatro semestres; ILOG online corresponde al perfil
regular, tipo 1 y ocho semestres. I162S2C77J4V1 y V2 no se trataron como dos mallas
sucesivas de un mismo programa: V1 corresponde al perfil regular; V2 al de continuidad.

| Evidencia | Resultado | Alcance |
|---|---|---|
| UMAS 12023 | 56 filas CILOG; 49 con ANOMATRICULA hasta 2026, 49 expedientes y 47 personas | Muestra completa de ese extracto y filtro, no matrícula SIES al corte |
| Estados actuales de las 49 filas | 37 vigentes, 11 eliminadas, una suspendida | No reconstruyen el estado histórico |
| Antecedente técnico interno | No localizado en las 49 filas mediante el catálogo y trayectorias disponibles | No demuestra procedencia externa |
| Tres filas con ingreso 2024 | Eliminadas, retiro/retracto y sin actividad verificada | No acreditan inicio efectivo de continuidad en 2024 |
| Oferta continuidad V2 | Primera observación 2025; con nuevos en 2025 y solo antiguos en 2026 | Primera oferta por código y perfil separados del regular |
| MRUN V2 en 2026 | 11 registros con ingreso actual 2025 y 21 con ingreso actual 2026 | Los 21 requieren aclaración frente a oferta solo antiguos; no son identidades UMAS asignadas |
| Listado curricular | Un plan CILOG20241, 47 filas de asignaturas, sin campo de vigencia | No demuestra apertura en 2024 ni fecha efectiva por expediente |

En los estratos UMAS hay un expediente con ingreso 2025 cuya primera presencia
por persona/carrera es 2024, y otro con ingreso 2026 cuya primera presencia es
2025. El mínimo de presencia puede arrastrar un expediente anterior de la misma
carrera, incluso sin cursado. D3 debe conservar separado el episodio de ingreso
real de la primera observación disponible; ANOINGRESO o el año del plan no resuelven
por sí solos esa diferencia.

Como contraste adicional, DATOSDEALUMNOS_11248 aporta 49 filas CILOG coincidentes
por documento/expediente/carrera con 12023, sin cambios en ANOINGRESO o ANOMATRICULA.
Contiene matrícula 2026 aunque esté en una carpeta llamada 2025: el nombre no
acredita un corte histórico 2025. Esta comparación no certifica ingreso efectivo.

El esquema MRUN 2007–2026, página 2, define ANIO_ING_CARR_ACT como ingreso a la
carrera; ANIO_ING_CARR_ORI admite 1900 para otro programa desde otra institución.
Los 14 registros V2 de 2025 declaran ingreso original 1900 e ingreso actual 2025.
Eso describe lo informado en MRUN y no permite concluir que las 49 filas UMAS
sean externas, ni identificar personas por esa coincidencia.

**Dictamen H5:** perfiles regular/continuidad preservados; incidencias de inicio
y admisión identificadas; ingreso efectivo y asignación individual pendientes.
[UMAS agregado](../data/cierre_d2/20261016/cilog.json),
[oferta anual](../data/cierre_d2/20261016/logistica_oferta_anual.json),
[cohortes MRUN](../data/cierre_d2/20261016/logistica_mrun_cohortes.json).

## H6 — Búsqueda y evaluación de fuentes

Búsqueda acotada por nombres en seis directorios: ambos repositorios, Descargas,
la carpeta institucional de oferta, SIES y Avance Curricular 2025. Se listaron
4.652 archivos y 277 candidatos. No apareció un archivo candidato de oferta
2007–2009 con esos patrones; no se afirma inexistencia fuera del alcance ni se
confunden los archivos localizados con fuentes verificadas.

Se inspeccionaron las fuentes más pertinentes:

- Listado_Planes_estudio_Sedes RE+CO: ya usado en H4, mismo hash. Relectura completa
  de 11.438 filas y 29 columnas; es catálogo de asignaturas, sin fechas de vigencia.
  Se conservó el XLSX completo en el proyecto, sin sustituir el original.
- Reporte 4262 matrícula 2025: 2.535 filas leídas en memoria; contiene documento
  y estados de carga, pero no código de carrera ni plan. No permite atribuir
  matrícula a CILOG ni resolver una versión.
- DATOSDEALUMNOS_11248: 14.637 filas leídas para los campos de contraste; comparación
  CILOG descrita en H5. No aporta etiqueta SIES ni fecha de corte acreditada.
- Mallas/perfiles de oferta 2027 se localizaron, pero su ubicación/edición no
  acredita vigencia 2007–2026. No se usaron para retroproyectar una equivalencia.

Las 211 reglas sin reserva conservan ese estado; estas fuentes adicionales no
aportaron un contraste académico nuevo adecuado para validarlas. Tampoco se
reclasifican los 108 planes sin actividad como planes nunca impartidos. Todas
las categorías D1 tienen hallazgo, elementos afectados, fuente faltante y acción
siguiente en el [registro de brechas](../data/cierre_d2/20261016/brechas_por_categoria.json).

[Registro de búsqueda](../data/cierre_d2/20261016/busqueda_fuentes.json) y
[lecturas y hashes](../data/cierre_d2/20261016/revision_fuentes_candidatas.json).
Las fuentes personales siguen externas y verificadas por hash; la gobernanza de
código/agregados no equivale a respaldo remoto ni a portabilidad de microdatos.

## Cierre y transición a D3

H4–H6 ejecutados con brechas explícitas. Se conservan los 16 expedientes y los
ocho contextos CILOG. No se habilitan reglas ni se modifican B4, B5, C1, C2 o D1.
D3 debe convertir los hallazgos en condiciones verificables de uso/abstención,
con vigencia anual, perfiles separados y estados de discrepancia; no forzar una
asignación cuando falta evidencia del episodio o de la malla.

Reproducción: `scripts/investigar_excepciones_d2.py`, `scripts/buscar_fuentes_d2.py`,
`scripts/completar_fuentes_d2.py`, `scripts/cerrar_investigacion_d2.py` (Python 3).
Pruebas: `python3 -m unittest discover -s tests -p 'test_excepciones_d2.py' -v`.
Evidencia de cierre: [resumen](../data/cierre_d2/20261016/cierre.json),
[manifiesto](../data/cierre_d2/20261016/manifest_cierre.json) y
[QA](../data/cierre_d2/20261016/qa.json).
