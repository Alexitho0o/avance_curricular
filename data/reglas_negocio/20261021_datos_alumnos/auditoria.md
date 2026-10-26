# Auditoria exploratoria de DatosAlumnos

Version 1.0.1, 2026-10-21. Capa independiente: no modifica reglas de incorporacion,
Word, CSV operativos, elegibilidad, matricula unificada ni FCU 2026 congelado.

## Preguntas que responde

1. Cuando se observo por primera vez una llave de matricula y cual era su fecha declarada.
2. Si FECHAMATRICULA cambia entre cortes comparables, hacia atras o adelante.
3. Si cambian firma, fecha de firma, estado/situacion, correo institucional, sede,
   jornada, carrera, periodo u otros campos. Se comparan todas las columnas comunes.
4. Si faltan filas, reaparecen, hay colisiones de llave, nulos, fechas futuras,
   formatos no interpretables o cambios de esquema.
5. Si los casos acumulados estaban en las entradas y propuestas previas de
   Caracterizacion. Propuesto en CSV no equivale a importado en LimeSurvey.

## Evidencia y limites

- Una fecha anterior a la primera observacion demuestra un desfase observado,
  NO prueba que alguien haya retrofechado la matricula, ni el momento de creacion.
- Fecha anterior al corte previo es evidencia mas fuerte que una diferencia de un
  dia dentro del intervalo entre extracciones. Aun asi depende del universo del extractor.
- El primer corte tiene censura izquierda: los registros podian existir desde antes.
- Saltos de dias, reapariciones y llaves ambiguas se conservan; no se inventa un
  historial continuo ni una fecha exacta de cambio.
- La fecha/hora del nombre es nominal; su zona horaria no esta confirmada. No se
  usa mtime ni fecha de descarga como fecha de matricula o creacion.
- Base Maestra no se presume equivalente a DATOSDEALUMNOS del reporte diario.
  Comparar cobertura por llave y RUT antes de interpretar ausencias. Una diferencia
  entre fuentes no se etiqueta como cambio temporal en UMAS.
- Firma, estado y correo son indicios separados. No reconstruyen solos elegibilidad:
  faltan reglas versionadas de cada corrida, exclusiones y antecedente institucional.
- La llave candidata es CODCLI + CODCARPR + ANOMATRICULA + PERIODOMATRICULA.
  Se valida en cada corte. RUT es persona, no fila. Conservar varias carreras.
  Colisiones con valores diferentes quedan fuera de comparaciones individuales;
  duplicados exactos se cuentan. No unir carreras por nombre ni elegir la primera.
- Cruce de personas 2027 P1: token = cuerpo del RUT, sin DV, conforme a
  caracterizacion.py:token_match_rut. RUT fuente literal se conserva; nunca concatenar
  DV al token ni truncar un token de longitud distinta. No extrapolar a otras encuestas.
- Ausencia de timestamp de creacion/modificacion, historial efectivo de estados y
  definicion de FECHAMATRICULA es una brecha E, no una autorizacion para inferirlos.

## Contrato de columnas compartido

`gobernanza/datos_alumnos/contrato_columnas.json` documenta 67 encabezados: 66 del
RAW y el correlativo opcional Numero del reporte diario. Contiene descripcion
heredada y su fuente/hash, interpretacion vigente, granularidad y pendientes.

Se importa sin ejecutar el generador maestro ni cambiar su v1.0 congelada:
`scripts/gobernanza/importar_contrato_datos_alumnos.py`. Fuente:
`avance_curricular/requerimiento_bettersoft_uplus_2026/scripts/generar_diccionario_maestro_uplus_sies.py`,
anotaciones ANOT; precedencia de estados en
`avance_curricular/docs/relacion_estados_umas_vig_sies_20261020.md`.

Los porcentajes/dominios de la descripcion heredada pertenecen a su antiguo corte,
no son reglas universales. No trasladar recomendaciones de excluir campos de una
carga SIES a una auditoria institucional. MODALIDAD es escolar; Mail_Inst no es
MAIL; ANOINGRESO es de carrera; estado UMAS no asigna VIG SIES automaticamente.
FECHAMATRICULA sigue pendiente de definicion primera matricula/renovacion UP-39.

## Comando reproducible

```bash
cd "/Users/alexi/Documents/GitHub/CARACTERIZACIÓN" && \
bash ./auditar_datos_alumnos.sh \
  --fuentes "/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/Shortcuts/DW_IPSS - Estudiantes/Base Maestra"
```

Opcionales: `--desde AAAA-MM-DD`, `--hasta AAAA-MM-DD`, `--casos <CSV acumulados>`,
`--fuente-actual <DatosAlumnos.xlsx> --corte-actual AAAA-MM-DD`,
`--historial-caracterizacion <0_caracterizacion>` para casos 2027 P1.
No seleccionar por comodin una corrida ni mezclar fuentes de dias diferentes.
La opcion `--corrida <carpeta exacta 2027_P1_...>` resuelve CSV acumulado, entrada
DATOS y fecha desde el manifiesto y activa historia de casos; falla ante ambiguedad.
No requiere volver a ejecutar Caracterizacion. En `TRAZA_INCORPORACION` quedan
las presencias en tokens de entrada y CSV propuestos de cada corrida, con su estado.
El Python activo requiere openpyxl; se puede fijar con CARACTERIZACION_PYTHON.

## Salidas y privacidad

Carpeta NUEVA `.local/auditoria_datos_alumnos/<ejecucion>` ignorada por Git,
permisos de directorio 700. No copia automatica al Escritorio ni ejecucion productiva.

- CORTES.csv: inventario, filas, personas, llaves, duplicados, distancia entre cortes.
- PERFIL_COLUMNAS.csv: vacios, cardinalidad, fechas no interpretables y formulas.
- CAMBIOS_PRIVADO.csv: columna y valor antes/despues, llave, RUT, cortes.
- APARICIONES_PRIVADO.csv: brecha en dias calendario y censura; no dias de atraso imputables.
- CALIDAD_PRIVADO.csv: fila de origen, llaves ambiguas, fechas futuras/no interpretables.
- HISTORIA_CASOS_PRIVADO.csv: todas las matriculas observadas de los RUT solicitados.
- RESUMEN_AGREGADO.json: conteos sin identificadores personales; no demuestra causalidad.
- manifest.json: parametros, hashes, fuentes, estado; es privado (contiene RUT/rutas).

CSV de revision UTF-8 con punto y coma y prefijos de formulas escapados; nunca
reimportarlos a UMAS. Fuentes literales intactas. Si falla, manifest ERROR_INCOMPLETO;
no anunciar auditoria completa. No publicar datos individuales en GitHub/plugins.
La instantanea compartida con skills NO sincroniza automaticamente los repositorios.

## Verificacion

Pruebas sinteticas: censura, cambio de fecha, firma posterior, duplicados, llaves
ambiguas, varias carreras, cambios de esquema, fechas no interpretables, formulas,
lectura de hojas y cobertura distinta. Verificar las 51 referencias congeladas antes
y despues. Una auditoria exploratoria no altera los promedios ni los totales operativos.
