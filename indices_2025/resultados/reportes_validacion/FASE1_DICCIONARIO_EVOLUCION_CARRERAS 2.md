# FASE 1 — Diccionario técnico CSV Evolución de Carreras

## 1. Fuente oficial utilizada
- Ruta del manual: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/docs/Manual_INDICES_2025.txt`
- Artefactos de FASE 0 usados:
  - `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/reportes_validacion/FASE0_DIAGNOSTICO_MANUAL_INDICES_2025.md`
  - `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/diccionarios/fase0_indice_secciones_manual.json`
  - `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/resultados/diccionarios/fase0_reglas_detectadas_manual.json`
- Fecha/hora de ejecución: `2026-05-18T18:36:40-04:00`

## 2. Ubicación del bloque en el manual
- Sección detectada: `18. CARGA DE ARCHIVO CSV DE EVOLUCIÓN DE CARRERAS`
- Líneas aproximadas: `2183` a `2927`
- Tabla detectada desde línea: `2207`
- Fragmento/resumen fiel: 18. CARGA DE ARCHIVO CSV DE EVOLUCIÓN DE CARRERAS Las instrucciones para la correcta carga de archivo CSV de evolución de carreras son las siguientes: i. Ingresar a la sección “Evolución Pregrado (CSV)” o “Evolución Posgrado (CSV)” según corresponda. ii. Descargue el archivo haciendo clic en el botón "Módulo CSV", luego seleccione “Descargar CSV”. Guarde el archivo en formato CSV: separado por ";" (Punto y coma) iii. Cuando complete la información, diríjase al botón “Examinar” e importe el archivo indicando que es un archivo separado por ";" (Punto y coma). Presione el botón “Subir”. iv. Revise el reporte. Posteriormente, podrían suceder tres cosas al cargar cada carrera: i. Carga sin pro...

## 3. Resultado del diccionario técnico
| Orden | Campo manual | Campo normalizado | Tipo dato | Formato | Obligatoriedad | Valores válidos | Nivel de confianza | Requiere revisión manual |
|---:|---|---|---|---|---|---|---|---|
| 1 | Idsede | IDSEDE | entero | N° Entero Positivo | no informado | no informado | alto | no |
| 2 | AnioInicioActividades | ANIOINICIOACTIVIDADES | entero | N° Entero Positivo | no informado | no informado | medio | no |
| 3 | Codcarr | CODCARR | entero | N° Entero Positivo | no informado | no informado | alto | no |
| 4 | Nombre | NOMBRE | texto | Texto | no informado | no informado | alto | no |
| 5 | TipoCarrera | TIPOCARRERA | texto | Texto | no informado | no informado | alto | no |
| 6 | NombreSede | NOMBRESEDE | texto | Texto | no informado | no informado | alto | no |
| 7 | nombreCampus | NOMBRECAMPUS | texto | Texto | no informado | no informado | alto | no |
| 8 | NombreDependencia | NOMBREDEPENDENCIA | no informado | no informado | no informado | no informado | bajo | sí |
| 9 | Horario | HORARIO | texto | Texto | no informado | no informado | alto | no |
| 10 | EspecialidadOMencion | ESPECIALIDADOMENCION | no informado | no informado | no informado | no informado | bajo | sí |
| 11 | idEstadoCarrera | IDESTADOCARRERA | entero | N° Entero Positivo | no informado | Funciona Normalmente=1; Nuevo=5; No recibe Estudiantes Nuevos=4; Inactivos=2 | alto | no |
| 12 | Anioinfo | ANIOINFO | entero | N° Entero Positivo | no informado | no informado | alto | no |
| 13 | CodigoSIES | CODIGOSIES | texto | Texto | no informado | no informado | alto | no |
| 14 | valorMatAnual | VALORMATANUAL | entero | N° Entero Positivo | no informado | no informado | alto | no |
| 15 | valorArancelAnual | VALORARANCELANUAL | entero | N° Entero Positivo | no informado | no informado | medio | no |
| 16 | valorTitulo | VALORTITULO | entero | N° Entero Positivo | no informado | no informado | alto | no |
| 17 | TipoMoneda | TIPOMONEDA | texto | Texto | no informado | UF; Pesos | alto | no |
| 18 | VacantesSemestre1 | VACANTESSEMESTRE1 | entero | N° Entero Positivo | no informado | no informado | medio | no |
| 19 | VacantesSemestre2 | VACANTESSEMESTRE2 | entero | N° Entero Positivo | no informado | no informado | medio | no |
| 20 | MatPrimerAnioHombres | MATPRIMERANIOHOMBRES | entero | N° Entero Positivo | no informado | no informado | medio | no |
| 21 | MatPrimerAnioMujeres | MATPRIMERANIOMUJERES | entero | N° Entero Positivo | no informado | no informado | medio | no |
| 22 | MatPrimerAnioExtranjeros_as | MATPRIMERANIOEXTRANJEROS_AS | entero | N° Entero Positivo | no informado | no informado | medio | no |
| 23 | MatTotalHombres | MATTOTALHOMBRES | entero | N° Entero Positivo | no informado | no informado | medio | no |
| 24 | MatTotalMujeres | MATTOTALMUJERES | entero | N° Entero Positivo | no informado | no informado | alto | no |
| 25 | MatTotalExtranjeros_as | MATTOTALEXTRANJEROS_AS | entero | N° Entero Positivo | no informado | no informado | medio | no |
| 26 | AlumnosRindieronPSU | ALUMNOSRINDIERONPSU | entero | N° Entero Positivo | no informado | no informado | medio | no |
| 27 | intAlumOtraVia | INTALUMOTRAVIA | entero | N° Entero Positivo | no informado | no informado | alto | no |
| 28 | PAESmin | PAESMIN | entero | N° Entero Positivo | no informado | no informado | alto | no |
| 29 | PAESprom | PAESPROM | entero | N° Entero Positivo | no informado | no informado | alto | no |
| 30 | PAESmax | PAESMAX | entero | N° Entero Positivo | no informado | no informado | alto | no |
| 31 | PAESPonderadoMin | PAESPONDERADOMIN | entero | N° Entero Positivo | no informado | no informado | medio | no |
| 32 | PAESPonderadoProm | PAESPONDERADOPROM | entero | N° Entero Positivo | no informado | no informado | medio | no |
| 33 | PAESPonderadoMax | PAESPONDERADOMAX | entero | N° Entero Positivo | no informado | no informado | bajo | sí |
| 34 | IntNemMin | INTNEMMIN | entero | N° Entero Positivo | no informado | no informado | alto | no |
| 35 | IntNemProm | INTNEMPROM | entero | N° Entero Positivo | no informado | no informado | alto | no |
| 36 | intNemMax | INTNEMMAX | entero | N° Entero Positivo | no informado | no informado | bajo | sí |
| 37 | intPRMin | INTPRMIN | entero | N° Entero Positivo | no informado | no informado | alto | no |
| 38 | intPRPro | INTPRPRO | entero | N° Entero Positivo | no informado | no informado | alto | no |
| 39 | intPRMax | INTPRMAX | entero | N° Entero Positivo | no informado | no informado | bajo | sí |
| 40 | MatTotalCohorteAnioAnt | MATTOTALCOHORTEANIOANT | texto | Texto | no informado | no informado | medio | no |
| 41 | NumDocentesPorPrograma | NUMDOCENTESPORPROGRAMA | entero | N° Entero Positivo | no informado | no informado | medio | no |
| 42 | MatPrimerAnioOriginarioH | MATPRIMERANIOORIGINARIOH | entero | N° Entero Positivo | no informado | no informado | medio | no |
| 43 | MatPrimerAnioOriginarioM | MATPRIMERANIOORIGINARIOM | entero | N° Entero Positivo | no informado | no informado | medio | no |
| 44 | MatTotalOriginarioH | MATTOTALORIGINARIOH | entero | N° Entero Positivo | no informado | no informado | medio | no |
| 45 | MatTotalOriginarioM | MATTOTALORIGINARIOM | entero | N° Entero Positivo | no informado | no informado | medio | no |
| 46 | Matricula total estudiantes no binarios | MATRICULA_TOTAL_ESTUDIANTES_NO_BINARIOS | entero | N° Entero Positivo | no informado | no informado | bajo | sí |
| 47 | Matricula primer año estudiantes no binarios | MATRICULA_PRIMER_ANO_ESTUDIANTES_NO_BINARIOS | entero | N° Entero Positivo | no informado | no informado | bajo | sí |

## 4. Reglas programables detectadas
| Campo | Regla explícita del manual | Regla programable propuesta | Nivel de confianza |
|---|---|---|---|
| Anioinfo | N° entero positivo mayor que o igual que cero | Anioinfo >= 0 | alto |
| valorMatAnual | Se debe programa por cumplir: concepto de N° entero N valorMatAnual Si matrícula o arancel Valor de la positivo. básico. Si la Matrícula<= matrícula es Valor arancel semestral o por anual cuotas, debe sumar todos los pagos parciales exigidos durante el año. | valorMatAnual <= valorArancelAnual | alto |
| valorArancelAnual | Se debe arancel anual que cumplir: el estudiante de valorArancelAnu N° entero O Si primer año debe Valor de la al positivo. pagar a la Matrícula<= institución a Valor arancel propósito de la anual suscripción de un contrato de prestación de servicios educacionales para este programa (excluida la matrícula). | valorMatAnual <= valorArancelAnual | medio |
| MatPrimerAnioHombres | Se debe cumplir: N° de hombres Matrícula matriculados en el primer año MatPrimerAnioH primer año al 30 de hombres <= N° entero T Si ombres abril de cada año. Matrícula total positivo. Incluye estudiantes hombres. extranjeros. Debe ser cero si el estado de la carrera es “Inactivo” o “No recibe nuevos estudiantes.” | MatPrimerAnioHombres <= MatTotalHombres; MatPrimerAnioHombres == 0 si estado de carrera es "Inactivo" o "No recibe nuevos estudiantes" | medio |
| MatPrimerAnioMujeres | Se debe cumplir: Matrícula primer año N° de mujeres mujeres <= matriculadas en el Matrícula total MatPrimerAnioM primer año al 30 de mujeres. N° entero U Si ujeres abril de cada año. positivo. Incluye estudiantes Debe ser cero extranjeros si el estado de la carrera es “Inactivo” o “No recibe nuevos estudiantes”. | MatPrimerAnioMujeres <= MatTotalMujeres; MatPrimerAnioMujeres == 0 si estado de carrera es "Inactivo" o "No recibe nuevos estudiantes" | medio |
| MatPrimerAnioExtranjeros_as | Se debe cumplir: N° de estudiantes extranjeros MatPrimerAnioE Matricula en N° entero V Si matriculados en el xtranjeros_as primer año positivo. primer año al 30 de extranjeros <= abril de cada año. Matrícula p rimer año. | MatPrimerAnioExtranjeros_as <= matricula primer año | medio |
| MatTotalHombres | Se debe cumplir: N° total de Matrícula hombres primer año matriculados en el hombres <= programa al 30 de Matrícula total MatTotalHombre abril de cada año. hombres. N° entero W Si s Esta matrícula es positivo. igual a la suma de Debe ser cero estudiantes si el estado de hombres nuevos y la carrera es antiguos. “Inactivo”. Incluye los extranjeros. | MatPrimerAnioHombres <= MatTotalHombres; MatTotalHombres == 0 si estado de carrera es "Inactivo" | medio |
| MatTotalMujeres | N° total de mujeres Se debe matriculadas en el cumplir: programa al 30 de N° entero X MatTotalMujeres Si abril de cada año. Matrícula positivo. Esta matrícula es primer año igual a la suma de mujeres <= alumnas nuevas y Matrícula total antiguas. mujeres. Debe ser cero si el estado de la carrera es “Inactivo”. Incluye los extranjeros. | MatPrimerAnioMujeres <= MatTotalMujeres; MatTotalMujeres == 0 si estado de carrera es "Inactivo" | alto |
| MatTotalExtranjeros_as | Se debe N° total de cumplir: estudiantes MatTotalExtranje extranjeros Matricula en N° entero Y Si ros_as matriculados el total positivo. programa al 30 de extranjeros <= abril de cada año. Matrícula t otal. | MatTotalExtranjeros_as <= matricula total | medio |
| AlumnosRindieronPSU | Se debe cumplir que: N.º de Estudiantes matriculados N° de estudiantes en primer año matriculados en que primer año que ingresaron vía ingresaron vía PAES + N.º AlumnosRindier PAES. En caso de N° entero Z Si de onPSU que ningún positivo. Estudiantes estudiante rindiera matriculados la prueba PAES se en primer año puede dejar en que cero. ingresaron por ot... | AlumnosRindieronPSU + intAlumOtraVia = matricula primer año | medio |
| intAlumOtraVia | Se debe cumplir que: N.º de Estudiantes matriculados en primer año que N° de estudiantes ingresaron vía matriculados en PAES + N.º primer año de N° entero AA intAlumOtraVia Si ingresaron por una Estudiantes positivo. vía distinta a la matriculados PAES en primer año que ingresaron por otra vía distinta a PAES = Matrícula de primer año. | AlumnosRindieronPSU + intAlumOtraVia = matricula primer año | alto |
| PAESmin | Se debe programa- del cumplir que: promedio de las pruebas “Puntaje Competencia mínimo Matemática y promedio Competencia PAES <= N° Entero AB PAESmin Si Lectora Puntaje Positivo. ponderadas en un promedio 50%. Considerar PAES <= sólo estudiantes Puntaje matriculados en máximo primer año y que promedio ingresaron vía PAES”. PAES. | PAESmin <= PAESprom <= PAESmax | alto |
| PAESprom | Se debe Valor promedio - cumplir que: por programa- del promedio de las “Puntaje pruebas mínimo Competencia promedio Matemática y PAES <= N° Entero AC PAESprom Si Competencia Puntaje Positivo. Lectora promedio ponderadas en un PAES <= 50%. Considerar Puntaje sólo estudiantes máximo matriculados en promedio primer año y que PAES”. ingresaron vía PAES. | PAESmin <= PAESprom <= PAESmax | alto |
| PAESmax | Se debe programa- del cumplir que: promedio de las pruebas “Mínimo del Competencia Puntaje Matemática y ponderado Competencia PAES <= N° Entero AD PAESmax Si Lectora Promedio del Positivo. ponderadas en un Puntaje 50%. Considerar ponderado sólo estudiantes PAES <= matriculados en Máximo del primer año y que Puntaje ingresaron vía ponderado PAES. PAES”. | PAESmin <= PAESprom <= PAESmax | alto |
| PAESPonderadoMin | Se debe Valor mínimo -por cumplir que: programa- del puntaje ponderado “Mínimo del de selección o Puntaje corte que exige ponderado esta carrera como PAES <= PAESPonderado requisito de N° Entero AE Si Promedio del Min ingreso. Positivo. Puntaje Considerar sólo ponderado estudiantes PAES <= matriculados en Máximo del primer año y que Puntaje ingresaron vía... | PAESPonderadoMin <= PAESPonderadoProm <= PAESPonderadoMax | medio |
| PAESPonderadoProm | Se debe Valor promedio - cumplir que: por programa- del puntaje ponderado “Mínimo del de selección o Puntaje corte que exige ponderado esta carrera como PAES <= PAESPonderado requisito de N° Entero AF Si Promedio del Prom ingreso. Positivo. Puntaje Considerar sólo ponderado estudiantes PAES <= matriculados en Máximo del primer año y que Puntaje ingresaron... | PAESPonderadoMin <= PAESPonderadoProm <= PAESPonderadoMax | medio |
| PAESPonderadoMax | Se debe PAESPonderado N° Entero AG Si programa- del cumplir que: Max Positivo. puntaje ponderado de selección o Mínimo corte que exige Puntaje esta carrera como NEM<= requisito de Promedio ingreso. Puntaje NEM Considerar sólo <= Máximo estudiantes Puntaje NEM matriculados en primer año y que ingresaron vía PAES. | requiere revision manual por inconsistencia entre nombre del campo y regla visible | bajo |
| IntNemMin | Se debe Puntaje PAES cumplir que: correspondiente a las notas de Mínimo enseñanza media. Puntaje N° Entero AH IntNemMin Si Considerar sólo NEM<= Positivo. estudiantes Promedio matriculados en Puntaje NEM primer año y que <= Máximo ingresaron vía Puntaje NEM PAES. | IntNemMin <= IntNemProm <= intNemMax | alto |
| IntNemProm | Se debe Puntaje PAES cumplir que: correspondiente a las notas de Mínimo enseñanza media. Puntaje N° Entero AI IntNemProm Si Considerar sólo NEM<= Positivo. estudiantes Promedio matriculados en Puntaje NEM primer año y que <= Máximo ingresaron vía Puntaje NEM PAES. | IntNemMin <= IntNemProm <= intNemMax | alto |
| intNemMax | Se debe Valor máximo -por cumplir que: programa- del Puntaje PAES Mínimo correspondiente al Puntaje ranking de notas. Ranking<= N° Entero AJ intNemMax Si Considerar sólo Promedio Positivo. estudiantes Puntaje matriculados en Ranking <= primer año y que Máximo ingresaron vía Puntaje PAES. Ranking | requiere revision manual por inconsistencia entre nombre del campo y descripcion visible | bajo |
| intPRMin | Se debe N° Entero AK intPRMin Si programa- del cumplir que: Positivo. Puntaje PAES correspondiente al Mínimo ranking de notas. Puntaje Considerar sólo Ranking<= estudiantes Promedio matriculados en Puntaje primer año y que Ranking <= ingresaron vía Máximo PAES. Puntaje Ranking | intPRMin <= intPRPro <= intPRMax | alto |
| intPRPro | Se debe Valor promedio - cumplir que: por programa- del Puntaje PAES Mínimo correspondiente al Puntaje ranking de notas. Ranking<= N° Entero AL intPRPro Si Considerar sólo Promedio Positivo. estudiantes Puntaje matriculados en Ranking <= primer año y que Máximo ingresaron vía Puntaje PAES. Ranking | intPRMin <= intPRPro <= intPRMax | alto |
| intPRMax | Se debe programa- del cumplir que: promedio de las pruebas de “Puntaje Matemáticas y mínimo Lenguaje y promedio Comunicación PSU <= N° Entero AM intPRMax Si ponderadas en un Puntaje Positivo. 50%. Considerar promedio sólo estudiantes PSU <= matriculados en Puntaje primer año y que máximo ingresaron vía promedio PAES. PSU”. | requiere revision manual por inconsistencia entre campo intPRMax y regla visible de promedio PSU | bajo |
| MatTotalCohorteAnioAnt | Se debe cumplir que: N° N° total de matriculados MatTotalCohort estudiantes de la cohorte AN eAnioAnt Si matriculados de la Texto. anterior<= cohorte del año “Matrícula de anterior. primer año” del año anterior. | MatTotalCohorteAnioAnt <= matrícula de primer año del año anterior | medio |
| MatPrimerAnioOriginarioH | Matricula en Se debe N° Entero riginarioH primer año cumplir: Positivo. estudiantes Matricula en provenientes primer año pueblos originarios estudiantes AP H provenientes pueblos originarios <= Matrícula primer año. | MatPrimerAnioOriginarioH <= matrícula primer año | medio |
| MatPrimerAnioOriginarioM | Se debe cumplir: Matricula en Matricula en primer año primer año MatPrimerAnioO estudiantes estudiantes N° Entero AQ SI riginarioM provenientes provenientes Positivo. pueblos originarios pueblos H originarios <= Matrícula primer año. | MatPrimerAnioOriginarioM <= matrícula primer año | medio |
| MatTotalOriginarioH | Se debe cumplir: Matricula Matricula Total total estudiantes MatTotalOrigina estudiantes N° Entero AR SI provenientes rioH provenientes Positivo. pueblos originarios pueblos H originarios <= Matrícula total. | MatTotalOriginarioH <= matrícula total | medio |
| MatTotalOriginarioM | Se debe cumplir: Matricula Matricula Total total estudiantes MatTotalOrigina estudiantes N° Entero AS SI provenientes rioM provenientes Positivo. pueblos originarios pueblos H originarios <= Matrícula total. | MatTotalOriginarioM <= matrícula total | medio |
| Matricula total estudiantes no binarios | Matricula total SI Corresponde al N° Se debe N° Entero estudiantes no total de cumplir: Positivo binarios estudiantes no Matricula binarios total AT matriculados al 30 estudiantes de abril de cada no binarios <= año. Matrícula primer año. | Matricula total estudiantes no binarios <= matrícula primer año | bajo |
| Matricula primer año estudiantes no binarios | Matricula primer SI Corresponde al N° Se debe N° Entero año estudiantes total de cumplir: Positivo no binarios estudiantes no Matricula binarios total AU matriculados en estudiantes primer año al 30 de no binarios <= abril de cada año. Matrícula primer año. | Matricula primer año estudiantes no binarios <= matrícula primer año | bajo |

## 5. Reglas no programables o ambiguas
- `NombreDependencia`: El manual muestra letra 'F' nuevamente para NombreDependencia; por orden despues de G y antes de I requiere revision manual. Formato no identificado explicitamente en el fragmento extraido.
- `EspecialidadOMencion`: Nombre reconstruido desde 'EspecialidadOM' + 'encion'; el formato no queda visible en el fragmento. Formato no identificado explicitamente en el fragmento extraido.
- `PAESPonderadoMax`: La regla visible menciona Puntaje NEM pese a que el campo es PAESPonderadoMax.
- `intNemMax`: El campo se llama intNemMax, pero la descripcion visible habla de ranking de notas.
- `intPRMax`: El campo intPRMax queda asociado en el fragmento a una regla de promedio PSU; requiere revision.
- `Matricula total estudiantes no binarios`: El nombre del campo aparece como texto descriptivo, no como identificador tecnico compacto.
- `Matricula primer año estudiantes no binarios`: El nombre del campo aparece como texto descriptivo, no como identificador tecnico compacto.

## 6. Catálogos externos o dependencias detectadas
- `Idsede`: catálogo externo `sí`; dependencias `no informado`.
- `Codcarr`: catálogo externo `sí`; dependencias `no informado`.
- `CodigoSIES`: catálogo externo `sí`; dependencias `no informado`.
- `valorMatAnual`: catálogo externo `no`; dependencias `valorArancelAnual`.
- `valorArancelAnual`: catálogo externo `no`; dependencias `valorMatAnual`.
- `MatPrimerAnioHombres`: catálogo externo `no`; dependencias `MatTotalHombres; idEstadoCarrera`.
- `MatPrimerAnioMujeres`: catálogo externo `no`; dependencias `MatTotalMujeres; idEstadoCarrera`.
- `MatPrimerAnioExtranjeros_as`: catálogo externo `no`; dependencias `Matrícula primer año`.
- `MatTotalHombres`: catálogo externo `no`; dependencias `MatPrimerAnioHombres; idEstadoCarrera`.
- `MatTotalMujeres`: catálogo externo `no`; dependencias `MatPrimerAnioMujeres; idEstadoCarrera`.
- `MatTotalExtranjeros_as`: catálogo externo `no`; dependencias `Matrícula total`.
- `AlumnosRindieronPSU`: catálogo externo `no`; dependencias `intAlumOtraVia; Matrícula primer año`.
- `intAlumOtraVia`: catálogo externo `no`; dependencias `AlumnosRindieronPSU; Matrícula primer año`.
- `PAESmin`: catálogo externo `no`; dependencias `PAESprom; PAESmax`.
- `PAESprom`: catálogo externo `no`; dependencias `PAESmin; PAESmax`.
- `PAESmax`: catálogo externo `no`; dependencias `PAESmin; PAESprom`.
- `PAESPonderadoMin`: catálogo externo `no`; dependencias `PAESPonderadoProm; PAESPonderadoMax`.
- `PAESPonderadoProm`: catálogo externo `no`; dependencias `PAESPonderadoMin; PAESPonderadoMax`.
- `PAESPonderadoMax`: catálogo externo `no`; dependencias `PAESPonderadoMin; PAESPonderadoProm`.
- `IntNemMin`: catálogo externo `no`; dependencias `IntNemProm; intNemMax`.
- `IntNemProm`: catálogo externo `no`; dependencias `IntNemMin; intNemMax`.
- `intNemMax`: catálogo externo `no`; dependencias `IntNemMin; IntNemProm`.
- `intPRMin`: catálogo externo `no`; dependencias `intPRPro; intPRMax`.
- `intPRPro`: catálogo externo `no`; dependencias `intPRMin; intPRMax`.
- `intPRMax`: catálogo externo `no`; dependencias `intPRMin; intPRPro`.
- `MatTotalCohorteAnioAnt`: catálogo externo `no`; dependencias `Matrícula de primer año del año anterior`.
- `MatPrimerAnioOriginarioH`: catálogo externo `no`; dependencias `Matrícula primer año`.
- `MatPrimerAnioOriginarioM`: catálogo externo `no`; dependencias `Matrícula primer año`.
- `MatTotalOriginarioH`: catálogo externo `no`; dependencias `Matrícula total`.
- `MatTotalOriginarioM`: catálogo externo `no`; dependencias `Matrícula total`.
- `Matricula total estudiantes no binarios`: catálogo externo `no`; dependencias `Matrícula primer año`.
- `Matricula primer año estudiantes no binarios`: catálogo externo `no`; dependencias `Matrícula primer año`.

## 7. Riesgos técnicos para FASE 2
- La Tabla 25 esta fragmentada por saltos de pagina y columnas, lo que puede afectar nombres y descripciones.
- La fila NombreDependencia aparece con letra F duplicada y no se observa una letra H explicita para esa posicion.
- Algunas reglas de puntajes muestran inconsistencias entre nombre de campo y texto visible; requieren revision antes de validacion bloqueante.
- Se necesita un archivo CSV real de prueba para confirmar encabezados, separador y tipos efectivos.
- Idsede, Codcarr y CodigoSIES dependen de codigos CNED/SIES mencionados en el manual.

## 8. Recomendación de FASE 2
Se recomienda pasar a FASE 2 con cautela: construir el validador automatico del CSV Evolucion de Carreras usando el diccionario generado y dejando las filas marcadas para revision como controles no bloqueantes hasta confirmarlas.

## 9. Punto exacto para reanudar
PUNTO EXACTO PARA REANUDAR:
FASE 2 — Construcción del validador automático del CSV Evolución de Carreras usando el diccionario técnico generado en FASE 1.
