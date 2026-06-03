# Aplicación resolución dudosos CNED/ÍNDICES 2025

## Fecha y hora

- Fecha y hora local: 2026-06-04 09:05:11

## Archivos

- Archivo original del Escritorio: `/Users/alexi/Desktop/CNED_PROGRAMAS_FALTANTES_PARA_CREAR_INDICES.xlsx`
- Archivo final creado en el Escritorio: `/Users/alexi/Desktop/CNED_PROGRAMAS_FALTANTES_PARA_CREAR_INDICES_RESUELTO.xlsx`
- Excel de resolución usado: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/CNED_RESOLUCION_DUDOSOS_4_CASOS_20260604_084306.xlsx`
- Markdown de resolución usado: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/CNED_RESOLUCION_DUDOSOS_4_CASOS_20260604_084306.md`

## Hashes SHA256

- Hash del archivo original antes: `df601492efe1e74b4d7cbf2c9f39dd63c550e64fb38c2eb668276d8b3dc8e508`
- Hash del archivo original después: `df601492efe1e74b4d7cbf2c9f39dd63c550e64fb38c2eb668276d8b3dc8e508`
- Confirmación de que el original no cambió: `SI`
- Hash del archivo final resuelto: `c50424cf14580f3d464ba4dc571db2097221652d93aa621f518065b2aeb5dfcc`

## Dictamen y acción aplicada

| CODIGO_UNICO | DICTAMEN_RECOMENDADO | ACCION_EXCEL | MOTIVO_DICTAMEN |
|---|---|---|---|
| I162S2C1J4V1 | MANTENER_EN_DUDOSOS_REVISAR_MANUAL | crear hoja REQUIERE_DECISION_INSTITUCIONAL | Registro vigente de IP CIISA con version posterior estructural I162S2C1J4V2 bajo IP SAN SEBASTIAN. La cobertura historica no debe decidirse automaticamente dentro del universo actual de IP SAN SEBASTIAN. La referencia contiene I162S2C1J4V2 pero con descripcion 'Ingeniería en Informática (P.E.)' y tipo 'Programa Especial', mientras matriz lo documenta como 'INGENIERIA EN INFORMATICA' y tipo 'Programa Regular'. |
| I162S2C3J1V1 | NO_CREAR_YA_CUBIERTO_POR_VERSION_POSTERIOR | crear hoja NO_CREAR_CUBIERTO | Existe version posterior estructural I162S2C3J1V2 con mismo nombre, sede, jornada, modalidad, tipo plan, duracion, nivel global y nivel carrera; ademas dicha version posterior aparece en la referencia CNED/INDICES. |
| I162S2C3J2V1 | NO_CREAR_YA_CUBIERTO_POR_VERSION_POSTERIOR | crear hoja NO_CREAR_CUBIERTO | Existe version posterior estructural I162S2C3J2V4 con mismo nombre, sede, jornada, modalidad, tipo plan, duracion, nivel global y nivel carrera; ademas dicha version posterior aparece en la referencia CNED/INDICES. |
| I162S2C3J4V1 | MANTENER_EN_DUDOSOS_REVISAR_MANUAL | crear hoja REQUIERE_DECISION_INSTITUCIONAL | Registro vigente de IP CIISA con version posterior estructural I162S2C3J4V2 bajo IP SAN SEBASTIAN. La cobertura historica no debe decidirse automaticamente dentro del universo actual de IP SAN SEBASTIAN. |

## Conteos de filas

- PROGRAMAS_FALTANTES_PARA_CREAR: 71
- DUDOSOS_REVISAR_MANUAL: 4
- DUDOSOS_REVISAR_MANUAL_RESUELTOS: 4
- NO_CREAR_CUBIERTO: 2
- REQUIERE_DECISION_INSTITUCIONAL: 2
- DUDOSOS_REVISAR_MANUAL_ACTUALIZADO: 0

## Validaciones ejecutadas

- Los 4 códigos existen en DUDOSOS_REVISAR_MANUAL original: OK
- NO_CREAR_CUBIERTO contiene exactamente los 2 códigos esperados: OK
- REQUIERE_DECISION_INSTITUCIONAL contiene exactamente los 2 códigos esperados: OK
- Ninguno de los 4 códigos queda en DUDOSOS_REVISAR_MANUAL_ACTUALIZADO: OK
- Ninguno de los 4 códigos está en PROGRAMAS_FALTANTES_PARA_CREAR: OK
- PROGRAMAS_FALTANTES_PARA_CREAR mantiene la misma cantidad de filas: OK
- No hay CODIGO_UNICO vacío en DUDOSOS_REVISAR_MANUAL_RESUELTOS: OK
- No hay CODIGO_UNICO vacío en NO_CREAR_CUBIERTO: OK
- No hay CODIGO_UNICO vacío en REQUIERE_DECISION_INSTITUCIONAL: OK
- No hay CODIGO_UNICO vacío en DUDOSOS_REVISAR_MANUAL_ACTUALIZADO: OK
- No hay códigos duplicados dentro de NO_CREAR_CUBIERTO: OK
- No hay códigos duplicados dentro de REQUIERE_DECISION_INSTITUCIONAL: OK
- La suma de NO_CREAR_CUBIERTO más REQUIERE_DECISION_INSTITUCIONAL es 4: OK

## Riesgos residuales

- La decisión institucional sigue pendiente para `I162S2C1J4V1` e `I162S2C3J4V1`.
- La rama local y `origin/clean/pes-ready-final` están divergidas; no se intentó resolver la divergencia.
- No se modificó `PROGRAMAS_FALTANTES_PARA_CREAR`; la aplicación se limitó a hojas nuevas de trazabilidad y clasificación.

## Estado Git final

- Rama: `clean/pes-ready-final`
- HEAD local: `ee64fe2`
- origin/clean/pes-ready-final: `4caf70b`
- status --short:

```text
?? indices_2025/cned/resultados/CNED_APLICACION_RESOLUCION_DUDOSOS_4_CASOS_20260604_090511.md
```

- status:

```text
On branch clean/pes-ready-final
Your branch and 'origin/clean/pes-ready-final' have diverged,
and have 1 and 1 different commits each, respectively.
  (use "git pull" if you want to integrate the remote branch with yours)

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	indices_2025/cned/resultados/CNED_APLICACION_RESOLUCION_DUDOSOS_4_CASOS_20260604_090511.md

nothing added to commit but untracked files present (use "git add" to track)
```

- Divergencia HEAD...origin/clean/pes-ready-final:

```text
< ee64fe2 fix: canonicalize clean CNED materializer script
> 4caf70b fix: canonicalize clean CNED materializer script
```

## Dictamen final

`DICTAMEN_FINAL: RESOLUCION_DUDOSOS_APLICADA_EN_COPIA_OPERATIVA`
