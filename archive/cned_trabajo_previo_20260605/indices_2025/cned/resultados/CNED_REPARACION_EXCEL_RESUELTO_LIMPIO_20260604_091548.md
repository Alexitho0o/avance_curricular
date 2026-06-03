# Reparación Excel resuelto limpio CNED/ÍNDICES

## Problema detectado

Excel reparó contenido al abrir `CNED_PROGRAMAS_FALTANTES_PARA_CREAR_INDICES_RESUELTO.xlsx`. No se debe usar ese archivo como final porque Microsoft Excel pudo haber quitado contenido no legible durante la reparación.

## Criterio de reparación

Se reconstruyó un workbook nuevo desde cero, usando solo valores tabulares leídos desde el archivo operativo original y el Excel de resolución de dudosos. El archivo problemático se registró por existencia y hash, pero no se usó como base de reconstrucción.

## Archivos

- Archivo original operativo usado: `/Users/alexi/Desktop/CNED_PROGRAMAS_FALTANTES_PARA_CREAR_INDICES.xlsx`
- Archivo resuelto problemático no usado como base: `/Users/alexi/Desktop/CNED_PROGRAMAS_FALTANTES_PARA_CREAR_INDICES_RESUELTO.xlsx`
- Archivo de resolución usado: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/CNED_RESOLUCION_DUDOSOS_4_CASOS_20260604_084306.xlsx`
- Markdown de resolución usado: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/CNED_RESOLUCION_DUDOSOS_4_CASOS_20260604_084306.md`
- Informe anterior registrado: `/Users/alexi/Documents/GitHub/avance_curricular/indices_2025/cned/resultados/CNED_APLICACION_RESOLUCION_DUDOSOS_4_CASOS_20260604_090511.md`
- Archivo limpio generado: `/Users/alexi/Desktop/CNED_PROGRAMAS_FALTANTES_PARA_CREAR_INDICES_RESUELTO_LIMPIO.xlsx`

## Hashes SHA256

- Original operativo inicial: `df601492efe1e74b4d7cbf2c9f39dd63c550e64fb38c2eb668276d8b3dc8e508`
- Original operativo final: `df601492efe1e74b4d7cbf2c9f39dd63c550e64fb38c2eb668276d8b3dc8e508`
- Resuelto problemático inicial: `c50424cf14580f3d464ba4dc571db2097221652d93aa621f518065b2aeb5dfcc`
- Resuelto problemático final: `c50424cf14580f3d464ba4dc571db2097221652d93aa621f518065b2aeb5dfcc`
- Excel de resolución inicial: `9a23b41451a3511e4f2b0f3a8e7c82df2af2c309150f5c7f669be84b90ed76ca`
- Excel de resolución final: `9a23b41451a3511e4f2b0f3a8e7c82df2af2c309150f5c7f669be84b90ed76ca`
- Informe anterior inicial: `3ebbd9f7ce64b3316290c3fce28a8993db43703659c1134393e23ad4d0acf211`
- Informe anterior final: `3ebbd9f7ce64b3316290c3fce28a8993db43703659c1134393e23ad4d0acf211`
- Markdown de resolución inicial: `b4d2c1c2bf7698d313edbfce15834802580a6080b2a1b25b720e489fb8386696`
- Markdown de resolución final: `b4d2c1c2bf7698d313edbfce15834802580a6080b2a1b25b720e489fb8386696`
- Archivo limpio generado: `ed363f3e1626b3c1d3a2138ef5eb8580738f687a41fa7b796feae5f61187969b`

## Hojas creadas

- `RESUMEN_EJECUTIVO` (lógica: `RESUMEN_EJECUTIVO`)
- `PROGRAMAS_FALTANTES_PARA_CREAR` (lógica: `PROGRAMAS_FALTANTES_PARA_CREAR`)
- `DUDOSOS_REVISAR_MANUAL_ORIGINAL` (lógica: `DUDOSOS_REVISAR_MANUAL_ORIGINAL`)
- `DUDOSOS_REV_MANUAL_RESUELTOS` (lógica: `DUDOSOS_REVISAR_MANUAL_RESUELTOS`)
- `NO_CREAR_CUBIERTO` (lógica: `NO_CREAR_CUBIERTO`)
- `REQUIERE_DECISION_INSTITUCIONAL` (lógica: `REQUIERE_DECISION_INSTITUCIONAL`)
- `DUDOSOS_REV_MANUAL_ACTUALIZADO` (lógica: `DUDOSOS_REVISAR_MANUAL_ACTUALIZADO`)
- `AUDITORIA_CODIGOS_ESPERADOS` (lógica: `AUDITORIA_CODIGOS_ESPERADOS`)
- `DICTAMEN_FINAL_DUDOSOS` (lógica: `DICTAMEN_FINAL_DUDOSOS`)
- `ACCION_RECOMENDADA_DUDOSOS` (lógica: `ACCION_RECOMENDADA_DUDOSOS`)
- `CONTROL_REPARACION` (lógica: `CONTROL_REPARACION`)

Nota: dos nombres lógicos solicitados superaban 31 caracteres. Se usaron alias compatibles con Microsoft Excel para evitar el mismo riesgo de reparación.

## Conteos

- PROGRAMAS_FALTANTES_PARA_CREAR: 71
- DUDOSOS_REVISAR_MANUAL_RESUELTOS: 4
- NO_CREAR_CUBIERTO: 2
- REQUIERE_DECISION_INSTITUCIONAL: 2
- DUDOSOS_REVISAR_MANUAL_ACTUALIZADO: 0

## Dictamen por código

| CODIGO_UNICO | DICTAMEN_RECOMENDADO | ACCION_EXCEL | REQUIERE_DECISION_INSTITUCIONAL | MOTIVO_DICTAMEN |
|---|---|---|---|---|
| I162S2C1J4V1 | MANTENER_EN_DUDOSOS_REVISAR_MANUAL | crear hoja REQUIERE_DECISION_INSTITUCIONAL | SI | Registro vigente de IP CIISA con version posterior estructural I162S2C1J4V2 bajo IP SAN SEBASTIAN. La cobertura historica no debe decidirse automaticamente dentro del universo actual de IP SAN SEBASTIAN. La referencia contiene I162S2C1J4V2 pero con descripcion 'Ingeniería en Informática (P.E.)' y tipo 'Programa Especial', mientras matriz lo documenta como 'INGENIERIA EN INFORMATICA' y tipo 'Programa Regular'. |
| I162S2C3J1V1 | NO_CREAR_YA_CUBIERTO_POR_VERSION_POSTERIOR | crear hoja NO_CREAR_CUBIERTO | NO | Existe version posterior estructural I162S2C3J1V2 con mismo nombre, sede, jornada, modalidad, tipo plan, duracion, nivel global y nivel carrera; ademas dicha version posterior aparece en la referencia CNED/INDICES. |
| I162S2C3J2V1 | NO_CREAR_YA_CUBIERTO_POR_VERSION_POSTERIOR | crear hoja NO_CREAR_CUBIERTO | NO | Existe version posterior estructural I162S2C3J2V4 con mismo nombre, sede, jornada, modalidad, tipo plan, duracion, nivel global y nivel carrera; ademas dicha version posterior aparece en la referencia CNED/INDICES. |
| I162S2C3J4V1 | MANTENER_EN_DUDOSOS_REVISAR_MANUAL | crear hoja REQUIERE_DECISION_INSTITUCIONAL | SI | Registro vigente de IP CIISA con version posterior estructural I162S2C3J4V2 bajo IP SAN SEBASTIAN. La cobertura historica no debe decidirse automaticamente dentro del universo actual de IP SAN SEBASTIAN. |

## Validaciones ejecutadas

- DICTAMEN_FINAL contiene las columnas requeridas: OK
- DICTAMEN_FINAL contiene exactamente 4 filas: OK
- DICTAMEN_FINAL contiene exactamente los 4 códigos esperados: OK
- DICTAMEN_FINAL no tiene códigos duplicados: OK
- DUDOSOS_REVISAR_MANUAL original contiene los 4 códigos esperados: OK
- PROGRAMAS_FALTANTES_PARA_CREAR tiene 71 filas: OK
- PROGRAMAS_FALTANTES_PARA_CREAR no tiene CODIGO_UNICO vacío: OK
- PROGRAMAS_FALTANTES_PARA_CREAR no tiene CODIGO_UNICO duplicado: OK
- Se extrajeron 4 filas dudosas originales para resolver: OK
- df_programas_faltantes tiene 71 filas: OK
- df_programas_faltantes mantiene sus columnas originales: OK
- df_programas_faltantes no tiene CODIGO_UNICO vacío: OK
- df_programas_faltantes no tiene CODIGO_UNICO duplicado: OK
- df_dudosos_resueltos tiene exactamente 4 filas: OK
- df_no_crear_cubierto tiene exactamente 2 filas: OK
- df_requiere_decision tiene exactamente 2 filas: OK
- df_dudosos_actualizado no contiene los 4 códigos resueltos: OK
- df_no_crear_cubierto contiene exactamente los códigos esperados: OK
- df_requiere_decision contiene exactamente los códigos esperados: OK
- df_dudosos_resueltos contiene exactamente los 4 códigos esperados: OK
- No hay DICTAMEN_RECOMENDADO vacío en df_dudosos_resueltos: OK
- No hay ACCION_EXCEL vacío en df_dudosos_resueltos: OK
- No hay REQUIERE_DECISION_INSTITUCIONAL vacío en df_dudosos_resueltos: OK
- Nombre de hoja compatible <=31: RESUMEN_EJECUTIVO: OK
- Nombre de hoja sin caracteres inválidos: RESUMEN_EJECUTIVO: OK
- Nombre de hoja compatible <=31: PROGRAMAS_FALTANTES_PARA_CREAR: OK
- Nombre de hoja sin caracteres inválidos: PROGRAMAS_FALTANTES_PARA_CREAR: OK
- Nombre de hoja compatible <=31: DUDOSOS_REVISAR_MANUAL_ORIGINAL: OK
- Nombre de hoja sin caracteres inválidos: DUDOSOS_REVISAR_MANUAL_ORIGINAL: OK
- Nombre de hoja compatible <=31: DUDOSOS_REV_MANUAL_RESUELTOS: OK
- Nombre de hoja sin caracteres inválidos: DUDOSOS_REV_MANUAL_RESUELTOS: OK
- Nombre de hoja compatible <=31: NO_CREAR_CUBIERTO: OK
- Nombre de hoja sin caracteres inválidos: NO_CREAR_CUBIERTO: OK
- Nombre de hoja compatible <=31: REQUIERE_DECISION_INSTITUCIONAL: OK
- Nombre de hoja sin caracteres inválidos: REQUIERE_DECISION_INSTITUCIONAL: OK
- Nombre de hoja compatible <=31: DUDOSOS_REV_MANUAL_ACTUALIZADO: OK
- Nombre de hoja sin caracteres inválidos: DUDOSOS_REV_MANUAL_ACTUALIZADO: OK
- Nombre de hoja compatible <=31: AUDITORIA_CODIGOS_ESPERADOS: OK
- Nombre de hoja sin caracteres inválidos: AUDITORIA_CODIGOS_ESPERADOS: OK
- Nombre de hoja compatible <=31: DICTAMEN_FINAL_DUDOSOS: OK
- Nombre de hoja sin caracteres inválidos: DICTAMEN_FINAL_DUDOSOS: OK
- Nombre de hoja compatible <=31: ACCION_RECOMENDADA_DUDOSOS: OK
- Nombre de hoja sin caracteres inválidos: ACCION_RECOMENDADA_DUDOSOS: OK
- Nombre de hoja compatible <=31: CONTROL_REPARACION: OK
- Nombre de hoja sin caracteres inválidos: CONTROL_REPARACION: OK
- No hay nombres de hoja duplicados en el workbook limpio: OK
- El archivo limpio existe: OK
- El archivo limpio tiene tamaño mayor que 0: OK
- El archivo limpio es ZIP OOXML válido: OK
- El OOXML limpio no contiene tablas, dibujos, gráficos, macros, conexiones ni vínculos externos: OK
- El OOXML limpio no contiene fórmulas: OK
- El OOXML limpio no contiene validaciones de datos: OK
- El archivo limpio contiene exactamente las 11 hojas esperadas y en orden: OK
- Validación post-guardado: PROGRAMAS_FALTANTES_PARA_CREAR tiene 71 filas: OK
- Validación post-guardado: NO_CREAR_CUBIERTO tiene 2 filas: OK
- Validación post-guardado: REQUIERE_DECISION_INSTITUCIONAL tiene 2 filas: OK
- Validación post-guardado: DUDOSOS resueltos tiene 4 filas: OK
- Validación post-guardado: dudosos actualizado está vacío y sin los 4 códigos resueltos: OK
- Hash del archivo original operativo idéntico antes/después: OK
- Hash del archivo resuelto problemático idéntico antes/después: OK
- Hash del Excel de resolución idéntico antes/después: OK
- Hash del informe anterior idéntico antes/después: OK
- Hash del Markdown de resolución idéntico antes/después: OK
- Revalidación final: 11 hojas esperadas y en orden: OK
- Revalidación final: ZIP OOXML válido: OK
- Revalidación final: sin partes OOXML prohibidas: OK
- Revalidación final: sin fórmulas: OK
- Revalidación final: sin validaciones de datos: OK

## Apertura

- ARCHIVO_ABIERTO: `SI`

## Estado Git final

- Rama actual: `clean/pes-ready-final`
- HEAD local: `fcc44bb`
- origin/clean/pes-ready-final: `4caf70b`

### git status --short

```text
?? indices_2025/cned/resultados/CNED_REPARACION_EXCEL_RESUELTO_LIMPIO_20260604_091548.md
```

### git status

```text
On branch clean/pes-ready-final
Your branch and 'origin/clean/pes-ready-final' have diverged,
and have 1 and 1 different commits each, respectively.
  (use "git pull" if you want to integrate the remote branch with yours)

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	indices_2025/cned/resultados/CNED_REPARACION_EXCEL_RESUELTO_LIMPIO_20260604_091548.md

nothing added to commit but untracked files present (use "git add" to track)
```

### git branch -vv

```text
backup/antes_limpieza_pes_ready_20260507        e790958 docs: close MU2026 PES_READY validation
  backup/pre-align-clean-pes-ready-final-20260603 8d24713 feat: materialize clean CNED operational artifact
  backup/pre-sync-fix-20260410-avance             d9c0e32 MU2026: agregar auditoría de activación gitignore DURACION
  backup/pre_cierre_pes_ready_20260507_134145     1d07eb8 test: add optional MU2026 cross-validation fixture
  backup/rebase_fallido_pes_ready_20260507        3dd107a chore: remove generated MU2026 audit artifacts
  clean/pes-ready                                 1d07eb8 [origin/main: ahead 1, behind 1] test: add optional MU2026 cross-validation fixture
* clean/pes-ready-final                           fcc44bb [origin/clean/pes-ready-final: ahead 1, behind 1] fix: canonicalize clean CNED materializer script
  fix/fase4-y-z                                   649ba4d [origin/fix/fase4-y-z: behind 6] MU2026 aprobado: gate final 32 OK 0 pendientes
  main                                            3dd107a [origin/main: ahead 4, behind 1] chore: remove generated MU2026 audit artifacts
```

### git log --oneline --left-right HEAD...origin/clean/pes-ready-final

```text
< fcc44bb fix: canonicalize clean CNED materializer script
> 4caf70b fix: canonicalize clean CNED materializer script
```

## Dictamen final

`DICTAMEN_FINAL: EXCEL_RESUELTO_LIMPIO_GENERADO_Y_VALIDADO`
