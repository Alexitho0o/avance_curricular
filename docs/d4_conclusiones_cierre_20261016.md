# D4 — Conclusiones y cierre del análisis SIES–UMAS

Fecha: 2026-10-16. H10–H12 ejecutados: análisis cerrado con brechas explícitas.
La especificación siguiente se registró antes de construir la entrega.

## Alcance de la entrega

H10 emitirá un dictamen por hipótesis con evidencia y límites. H11 entregará una
edición separada del Excel C1, incorporando los resultados D3 y ejemplos D2.
H12 vinculará cada uno de los 1.986 contextos, 141 códigos y 236 planes a las
brechas D1 investigadas en D2 y a una agenda con fuente y criterio de reapertura.
No se reinician agrupaciones, no se modifican reglas B5/D3 ni se habilitan cargas.

La matriz JSON conservará íntegros los registros D3 y añadirá referencias de
agenda. El Excel mostrará todos los elementos con columnas de consulta, estados,
fuentes y motivos; las estructuras anidadas completas quedan en la matriz JSON.
Las 14 hojas C1 se preservarán; las hojas D4 se añadirán, con navegación desde
Consulta y Guía. Nombres literales de oferta, modalidad y sectores son campos
separados. Los códigos sin oferta 2026 conservan vacíos y nombre histórico aparte.

La autoría se realizará con Artifact Tool; Python leerá las fuentes y verificará
el archivo sin escribir XLSX. Se compararán datos, fórmulas, formatos, tablas,
filtros, paneles y sectores contra C1, las referencias congeladas y los hashes
de las entregas anteriores. Se probará la consulta de cada estado y las entradas
vacía/desconocida. La revisión visual y de cachés no acredita Excel nativo.

Los scripts aislados de preparación y verificación se ubican justificadamente en
`scripts/`, conforme al layout operativo: no cambian motores ni consumidores.
El paquete estará en `data/cierre_d4/20261016/` y el libro en
`outputs/diccionario_d4_20261016/`. No se modifica `PROYECTO_IPSS.json`, congelado
en las entregas anteriores. No se realiza commit ni publicación remota.

## H10 — Conclusión del análisis

El análisis permite gobernar la primera oferta, conservar las agrupaciones y
consultar evidencia histórica con reglas deterministas. **Todavía no acredita
una equivalencia de malla para cada Código Único.** La fecha de primera oferta
y la declaración de admisión ayudan a ordenar la historia SIES; el enlace con
UMAS requiere identificar el episodio de la carrera y la vigencia del plan.

| Hipótesis | Dictamen y consecuencia |
|---|---|
| Primera oferta = inicio del diccionario | Regla interna sustentada para el Código Único completo, sin condicionar a matrícula o quórum. Hay oferta para 139/141 códigos; ocho ya están en el límite 2010 y dos carecen de oferta. No confundir inicio observado con primera declaración real fuera de cobertura ni con el campo formal Año Inicio. |
| Regular y continuidad son programas diferentes | Se conserva la separación por perfiles ya gobernados. Logística regular J4 V1: ocho semestres y oferta desde 2024; continuidad V2: cuatro semestres y desde 2025. No se mezclan sus inicios ni se añade «Continuidad» al nombre literal de oferta. |
| Cada V SIES equivale a una malla UMAS | Refutada como regla general: el manual permite cambios curriculares sin cambiar los atributos protegidos. El ordinal V no es un número de malla UMAS. Hace falta evidencia curricular específica. |
| Semestre → trimestre exige siempre otro código | Refutada como regla general para los casos y manuales revisados: 34 de 103 códigos comunes 2026–2027 cambian régimen manteniendo código y duraciones formales. Esto no establece una conversión universal. |
| Solo antiguos determina automáticamente el destino de cada cohorte | Su utilidad anual está sustentada; la asignación automática no. 14/16 contextos conflictivos contienen nuevos y antiguos y dos solo antiguos. I162S2C1J4V1 pasa de solo antiguos en 2020 a nuevos en 2022; no imponer cierre irreversible. |
| ANOINGRESO o primera presencia basta para continuidad | Insuficiente: puede existir ingreso heredado del técnico o presencia en un expediente anterior de la misma carrera. La unidad es el episodio por carrera/expediente, con cobertura y fecha verificables. |
| Demografía y totales certifican MRUN–UMAS | Sirven para acotar y contrastar candidatos; no certifican identidad, episodio ni vigencia curricular. D3 no dispone de nueva validación independiente. No forzar igualdad de totales como prueba individual. |
| Una regla de un año se puede transportar automáticamente | Refutada por el ensayo: 152 coincidencias, 59 contradicciones, seis conflictos y 720 sin regla sobre 937 consultas de 2022. Mantener año y clave completos. |
| Las discrepancias son solo estudiantes eliminados | No demostrado: las seis observaciones persona/estrato de cinco contextos incluyen cuatro eliminados y dos titulados en el extracto actual. Ese estado no prueba su situación al informar el año histórico. |

Las reglas formales mantienen la edición que las sustenta. El Anexo 5 del manual
Oferta-Acceso 2027, pp. 65–66, no justifica retroactivamente la variación 2018–2019
de duración de `I162S2C35J4V1`; esa incidencia conserva su brecha de fuente.

Evidencia por hipótesis: [registro D4](../data/cierre_d4/20261016/hipotesis.json).
Las conclusiones reutilizan la [auditoría de manuales e inicio](unificacion_proyectos_y_reglas_negocio_20261015.md),
los [expedientes D2](d2_excepciones_20261016.md) y el [contraste B5](b5_reglas_historicas_20261016.md).
No se reinterpretan las fuentes de una edición como normas universales del período.

## H11 — Balance y diferencias de la entrega

| Dictamen D3 incorporado en D4 | Contextos |
|---|---:|
| Uso analítico corroborado | 169 |
| Observación sin contraste | 204 |
| Evidencia sin regla K0 | 37 |
| Abstención por conflicto | 16 |
| Abstención por ambigüedad | 40 |
| Sin evidencia atribuible | 1.520 |
| **Total** | **1.986** |

Los 169 contextos corroborados involucran 41 códigos y 49 planes distintos: son
denominadores separados, no una tasa de versiones resueltas. Los 141 códigos y
236 planes tienen resultado y agenda. Hay 916 contextos sin plan observado y
1.070 con plan observado sin vigencia acreditada. Todas las asignaciones D3
continúan vacías y no habilitadas.

Las 197 reglas K0 corroboradas B5 permanecen iguales: 169 corresponden a contextos
sin ambigüedad adicional y 28 a contextos ambiguos. D4 conserva la precedencia D3
sin recalcular el rendimiento B5 ni presentar su reserva ya revisada como prueba
independiente. Los 1.520 contextos sin evidencia incluyen 153 dentro de los años
evaluados por el enlace personal y 1.367 fuera; falta de evidencia no equivale a
que una carrera nunca se impartió.

La edición D4 incorpora siete hojas a las 14 de C1: Cierre D4, Dictámenes D3,
Códigos D3, Planes D3, Hipótesis D4, Agenda D4 y Ejemplos D4. Se mantienen Consulta
y Consulta B5 con sus contratos previos. Desde Cierre D4 se consulta un contexto
B4 y se ven dictamen, carrera, año, planes, códigos observados, alcance y brechas.
La búsqueda previa por Código Único sigue disponible en Consulta; Códigos D3
completa el estado y las referencias a contextos. La selección por ID B4 evita
volver a decidir qué combinación usar en cada caso.

El Excel preserva nombres literales 2026, modalidad, jornada, tipo de plan y los
sectores editados. Cuando no existe nombre 2026 mantiene el vacío y muestra el
último nombre histórico en otra columna. No oculta planes sin actividad ni
códigos sin relación UMAS. Las listas completas de estructuras anidadas, oferta
y evidencia se conservan en la [matriz íntegra](../data/cierre_d4/20261016/matriz_resultados.json);
el libro presenta columnas de consulta y todos los elementos del universo.

### Ejemplos que explican el límite

- **CILOG, oferta:** V2 continuidad comienza en la oferta observada de 2025;
  V1 regular de 2024 no es un sustituto. En 2026 V2 declara solo antiguos,
  mientras MRUN tiene 11 registros con ingreso actual 2025 y 21 con ingreso
  actual 2026. Se necesita conciliar lo declarado, sin atribuir esos 21 a
  identidades UMAS mediante una inferencia no acreditada.
- **CILOG, UMAS:** el corte D2 contiene 49 expedientes de 47 personas hasta
  ANOMATRICULA 2026, con 37 filas vigentes, 11 eliminadas y una suspendida.
  Las tres filas de ingreso 2024 están eliminadas por retiro/retracto, sin
  actividad verificada. No prueban impartición de continuidad en 2024.
- **CILOG, malla:** el catálogo contiene CILOG20241 y 47 filas de asignaturas,
  sin fecha explícita de vigencia. El año del identificador no acredita apertura.
  Un episodio 2025 tiene primera presencia por persona/carrera en 2024 y otro
  de 2026 la tiene en 2025: el mínimo observado puede pertenecer a otro expediente.
- **IECIRE, B4-00362:** en 2019 coexisten V1 solo antiguos y V2 nuevos;
  ingreso SIES 2018 y plan observado IECIRE20191 no separan destinos. Permanece
  conflicto, aunque la coexistencia sea compatible con cohortes antiguas.
- **IETMREOL, B4-00844:** el ingreso original SIES 2013/2019 distingue destinos,
  pero UMAS agrupa el contexto con ingreso original 2019. No es lícito usar
  aquella distinción como si fuera un campo UMAS equivalente ya disponible.
- **TPCREOL, B4-01748:** ambos destinos son solo antiguos en 2020; V1 incluye
  ingreso actual 2020 y V2 ingreso 2016 sin oferta localizada de ese año.
  La admisión detecta discrepancias, pero no resuelve cuál código asignar.

Detalle y localizadores: [ejemplos D4](../data/cierre_d4/20261016/ejemplos.json),
[CILOG D2](../data/cierre_d2/20261016/cilog.json) y
[16 expedientes](../data/cierre_d2/20261016/expedientes_16.json).
Son conteos del análisis y de sus extractos, no matrícula institucional actual.

## H12 — Agenda posterior y criterio de reapertura

Las 18 categorías conservan todos los elementos afectados, acción, fuente
faltante y criterio de salida en la [agenda D4](../data/cierre_d4/20261016/agenda.json).
Cada registro de la matriz enlaza sus categorías. Estas se superponen: no sumar
los conteos como casos únicos. Los responsables funcionales son propuestas por
designar, no asignaciones a personas ni solicitudes enviadas.

| Orden | Acción concreta y producto esperado | Rol propuesto, por designar | Condición para avanzar |
|---|---|---|---|
| 1 | Conciliar los 16 conflictos y las discrepancias de admisión CILOG 2026 con oferta, reporte enviado y corte. Documentar rectificación o explicación por código/año. | Responsable institucional de Oferta/Matrícula SIES, Registro Académico y DAI | Evidencia fechada que explique la discrepancia; no basta estado actual ni mayoría de observaciones. |
| 2 | Reconstruir ingreso a la carrera y cambios de plan por expediente; distinguir antecedentes internos y externos con evidencia. Obtener vigencias y actos curriculares, empezando por CILOG20241. | Registro Académico y Gestión Curricular | Episodio, CODCARPR, plan, sede/jornada y vigencia respaldados. Conservar ingreso original aparte. |
| 3 | Completar oferta anterior a 2010 y cortes UMAS faltantes, documentando también búsquedas infructuosas. Ratificar relaciones de códigos/planes sin evidencia. | Responsable de Oferta SIES, Registro Académico y DAI | Fuente completa con procedencia, corte, esquema y hash; nueva edición que no sustituya silenciosamente la anterior. |
| 4 | Proponer un piloto operativo acotado solo para relaciones ratificadas. Fijar regla y cohorte antes de contrastar con evidencia adicional. | Responsables funcionales de ambos módulos y DAI | Reproducción en ambos módulos, ausencia de conflictos ocultos, límites explícitos, revisión funcional y mecanismo de reversión antes de una carga real. |

Mientras tanto, el uso permitido es consultar, describir y revisar evidencia
con su estado. Una relación corroborada permite análisis del contexto exacto;
no permite certificar persona ni activar una equivalencia de malla. Retención,
titulación oportuna y vigencia/eliminación de estudiantes requieren sus propios
contratos y no quedan validados por este cierre.

**D4 termina el plan D1–D4. No hay una D5 automática.** El siguiente trabajo es
la agenda de ratificación y evidencia; solo se reabre una relación cuando aparece
una fuente pertinente o una decisión funcional documentada. Cerrar el análisis
no equivale a resolver el 100 % de equivalencias.

## Reproducción, ubicación y preservación

Preparación determinista: `python3 scripts/preparar_cierre_d4.py`.
Autoría: `node data/cierre_d4/20261016/autor/generar_d4.mjs`, después de habilitar
la dependencia externa Artifact Tool según la habilidad de hojas de cálculo.
Verificación solo lectura del XLSX: `python3 scripts/verificar_cierre_d4.py`.
El autor admite `--preview` para revisar C1 sin modificarlo.

La consulta y los resultados agregados están en el repositorio único; no hay
nueva dependencia entre repositorios. Algunas fuentes personales de reconstrucción
siguen externas y verificadas por hash, como ya se declaró en D2. Por tanto,
gobernanza del resultado no significa respaldo remoto de todos los microdatos,
reconstrucción integral desde otra máquina ni publicación en GitHub. D4 no
añade fuentes personales ni afirma haber resuelto esa deuda de portabilidad.

El cierre de QA se registra en `data/cierre_d4/20261016/qa.json` y la entrega
con huellas en `data/cierre_d4/20261016/entrega.json`. El recálculo se verifica
en Artifact Tool y en las cachés exportadas, no en Excel nativo.

### Resultado de verificación

- 2.363 registros D3 íntegros en la matriz: 1.986 contextos, 141 códigos y
  236 planes; todos enlazados con agenda. Nueve hipótesis y 18 categorías.
- 113.604 celdas C1 preservadas y 47.159 celdas nuevas verificadas. Sin
  diferencias en los formatos comparados, tablas, filtros, validaciones,
  paneles ni columnas/filas ocultas de las hojas anteriores.
- Atributos de los 141 códigos cotejados por identificador: nombres, jornada,
  modalidad, tipo y sectores/estados/evidencia. El Excel original del usuario
  y las entregas C1, C2, D2 y D3 conservan sus huellas.
- Seis estados de consulta y dos fronteras aprobados; balance conciliado en
  fórmulas; ningún error Excel detectado en la caché exportada. Siete pruebas
  de regresión D3 aprobadas, incluida paridad de ambos módulos.
- Seis archivos JSON reproducidos idénticamente; 137 referencias protegidas
  y 51 archivos FCU2026 intactos. Cero asignaciones activadas.
- Revisión visual de las siete hojas nuevas y de la navegación añadida;
  listas extensas de contextos compactadas sin eliminar identificadores.

Los conteos de Agenda D4 corresponden a categorías D1 investigadas en D2, que
pueden superponerse. No sustituyen los seis estados excluyentes D3 del balance:
por ejemplo, 211 reglas K0 sin reserva no equivalen a 204 contextos cuyo dictamen
final es observación sin contraste, pues D3 da precedencia a conflictos/ambigüedad.
