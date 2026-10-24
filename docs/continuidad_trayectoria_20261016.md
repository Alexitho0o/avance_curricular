# Continuidad: ingreso a la carrera y trayectoria por persona

Especificación previa, 2026-10-16. Regla interna declarada por Alexi: al pasar de
técnico a continuidad, UMAS puede conservar ANOINGRESO del técnico. Por tanto,
ANOINGRESO no identifica necesariamente la cohorte de la carrera de continuidad.

## Decisiones

- Conservar ANOINGRESO original. No corregirlo ni reemplazarlo en las fuentes.
- Identidad persona: RUT normalizado con el helper ya gobernado de Caracterización;
  CODCLI distingue matrículas/expedientes. Vacíos no se enlazan. Un mismo CODCLI
  asociado a RUT distintos queda bloqueado por conflicto de identidad.
- Conservar las agrupaciones carrera/sede/jornada y duración ya construidas.
  Continuidad se identifica por tipo de plan 3 del perfil gobernado; técnico
  por NIVEL_CARRERA=1 del catálogo, con unanimidad dentro de la agrupación.
- Antecedente interno: misma persona, otro CODCLI y carrera técnica identificada.
  Más de un CODCLI no demuestra por sí solo una carrera técnica ni su titulación.
  Registrar si existe observación del técnico anterior a la de continuidad;
  no decidir precedencia con el ANOINGRESO heredado.
- Sin técnico localizado no equivale a procedencia externa confirmada: se
  necesita evidencia de admisión/convalidación o antecedente externo. La ausencia
  puede corresponder a cobertura incompleta. No interpretar automáticamente
  cualquier homologación como estudio previo externo.
- Primer año observado de la carrera específica: mínimo de las matrículas
  observadas y actividad del mismo CODCLI/CODCARPR; notas homologadas o convalidadas
  se excluyen como evidencia de inicio. No heredar el año de otro CODCLI técnico.
  Unir además la misma carrera de la persona cuando haya varios CODCLI, sin unir
  carreras distintas. Sede y jornada se conservan para el destino SIES.
- El extracto DatosAlumnos es un corte, no un historial certificado de todos los
  ingresos. El mínimo observado se etiqueta como tal; no acredita fecha efectiva
  de ingreso. Se puede ensayar una versión con esa fecha, separada de una
  asignación oficial. Si falta historial/evento de admisión, el año cero efectivo
  permanece pendiente; no usar ANOMATRICULA del corte como fecha confirmada.

## Implementación y aceptación

Capa nueva aislada en common/ y scripts/, con resultados agregados en
data/continuidad_trayectoria/20261016/. Los XLSX se leen con hash verificado,
proyectando solo campos necesarios. RUT/CODCLI se usan en memoria; no se exportan
identificadores, hashes personales ni detalles individuales al repositorio.
No modificar el módulo operativo de trayectorias 2027 ni congelados.

La regla anterior por ANOINGRESO queda como ensayo histórico. Para continuidad,
su salida no debe consumirse como asignación de versión sin reconstruir primero
el ingreso a la carrera. Esta especificación prevalece para ese caso.

Pruebas: año heredado, dos CODCLI sin técnico, ausencia de antecedente no prueba
origen externo, varias matrículas de la misma carrera, identidad vacía/conflictiva,
exclusión de homologaciones y no certificar mínimos de una fuente parcial.

## Resultado de la comprobación

Se evaluaron 641 filas de DatosAlumnos de perfiles de continuidad identificados
por las agrupaciones existentes, dentro del corte hasta 2026. No son personas
únicas ni un total de matrícula SIES. En 157 filas se localizó otro CODCLI técnico
del mismo RUT con observación anterior; en 6 existe el antecedente técnico pero
queda pendiente su precedencia temporal; en 478 no se localizó técnico interno.
Ninguno de estos últimos casos acredita por sí solo procedencia externa.

En 11 filas la primera observación de la carrera difiere de ANOINGRESO. No se
certifica todavía ningún ingreso efectivo ni se activa una asignación oficial.
En CILOG persisten observaciones de 2024 anteriores a la oferta 2025 del perfil
de continuidad: la regla del año heredado no basta para explicar esos registros.
Debe comprobarse la historia del expediente y la atribución de su actividad.

El resolutor `resolver_version_trayectoria` exige fecha propia de la carrera
para continuidad; sin ella devuelve pendiente y nunca recurre a ANOINGRESO.
Las fechas observadas y confirmadas llevan procedencia distinta. Diez pruebas
unitarias verifican la identidad, la trayectoria y esta barrera de asignación.

Los resultados agregados y las fuentes con sus hashes quedan en
`data/continuidad_trayectoria/20261016/`. Se leyeron 15.045 filas de DatosAlumnos
y 129.493 de Promedios. Para Promedios se utilizó el respaldo de hash idéntico
ya registrado en H6, pues la copia de Descargas había cambiado. No se copiaron
identificadores personales al resultado ni se modificaron los archivos fuente.
