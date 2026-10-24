# Versiones por cohorte sobre agrupaciones existentes

Especificación previa, 2026-10-16. Corrección del usuario: conservar las carreras
ya agrupadas y la distinción por duración; completar la versión con primera
oferta frente a ANOINGRESO de DatosAlumnos. La comparación de nombres de fase B
no es una condición para este cruce.

## Contrato

- Reutilizar las 257 equivalencias de programa H5, sus sedes y jornadas. Ignorar
  diferencias entre NOMBRE_L y nombre SIES como criterio de admisión. No buscar
  carreras por semejanza ni quitar prefijos. La familia I/S/C/J existente permite
  consultar todas sus versiones históricas, incluidas las ausentes en 2026.
- Conservar los perfiles de duración total y tipo de plan respaldados por las
  equivalencias manuales FCU2026 y por CODCARPR_CANONICO en DURACION_ESTUDIOS.
  Las manuales específicas tienen precedencia. Si no hay una referencia de esas
  clases, usar el perfil del grupo solo cuando todos sus candidatos coincidan.
  No asignar continuidad por nombre, prefijo o por ser la menor duración global.
- La duración total se compara en semestres formales SIES, sin convertir NIVEL
  ni duración de estudios en duración total. El perfil interno procede del puente
  ya gobernado; DatosAlumnos no contiene una duración total propia.
- Año de entrada = ANOINGRESO; conservar PERIODOINGRESO sin convertirlo. No usar
  ANOMATRICULA, año de notas, año del nombre CODPESTUD ni mínimo institucional de
  una persona. Fuente: proyección académica completa de combinaciones de
  DATOSDEALUMNOS_11998, con hash y fila de origen, ya conservada en el proyecto.
- Inicio SIES = mínimo año de oferta del código completo. Identificar códigos
  observados desde 2010 como censurados por cobertura; no inventar oferta previa.
- Comparar primero tipo de plan y duración total. Usar el perfil anual del año de
  ingreso cuando exista; conservar el de primera oferta como referencia si falta
  aquel año, señalándolo. No usar oferta 2027 para reinterpretar una cohorte anterior.
- Resultado por coincidencia exacta: año de primera oferta = ANOINGRESO y único
  destino dentro del perfil. Para años posteriores, evaluar separadamente la
  hipótesis de intervalos: inicio más reciente no posterior a la cohorte dentro
  del mismo perfil. Un empate entre códigos queda ambiguo; no elegir V máxima.
  El intervalo no prueba que la versión anterior haya cerrado ni que todo alumno
  haya sido migrado. Diferenciar coincidencia de inicio e intervalo propuesto.
- El resultado es una regla interna de propuesta por cohorte, no acreditación
  de CODPESTUD ni del plan individual. No bloquear este análisis exigiendo ese
  vínculo: es una pregunta distinta que las salidas deben distinguir.

## Entregables y controles

Capa aislada `common/versiones_por_cohorte.py`, generador/consulta en `scripts/`,
siguiendo el layout autorizado, y datos en `data/versiones_por_cohorte/20261016/`.
Conservar grupos sin estudiantes, todas las combinaciones de DatosAlumnos y
todos los códigos históricos. Congelados H5, FCU/MU2026 y Excel no se modifican.
Las fuentes originales se fijan por hashes; el resultado conserva identificadores
de grupo y localizadores sin identidades personales. Las 257 equivalencias no
se reescriben. Contrastar las propuestas con MRUN por código/cohorte cuando haya
observación, sin exigir matrícula para que exista una oferta.

Pruebas: independencia del nombre, duración regular/continuidad, primer ingreso
distinto de matrícula, empates de inicio, no V máxima, oferta anterior a 2010
desconocida, campos ausentes, cambios anuales de duración, reproducción y
preservación de universos. La cobertura se mide en combinaciones académicas,
no en personas. Las fechas de inicio no se convierten en fechas efectivas de malla.
