# Revisión de respaldos de segunda carga · 26-10-2026

## PROMEDIOS de respaldo

**[B/C]** Se leyó `promedio alumnos enviado por alvaro.xlsx`, `Hoja1`, SHA-256 `46c13bb910a9f43071583a5bc9c022be90c73188a7c29789f38f8a6f6ce3f89c`, y se comparó con `PROMEDIOSDEALUMNOS_7804.xlsx` de la carpeta consolidada, SHA-256 `83a0ba72b21d25dd0d151b75fb0182a1f55bbe3f5efba06d088c994067262fca`. Se compararon los 21 pares carrera–plan–ramo por RUT+DV+CODCLI+carrera+plan+año+período+ramo+sección, sin exportar identificadores.

**[B/C]** Cada archivo tiene 33 llaves distintas para los 21 pares; las 33 son comunes, sin llaves exclusivas. En las llaves comunes no hay diferencias en `ESTADO`, `DESCRIPCION_ESTADO`, `CONVALIDADO` ni `RAMOEQUIV`. La ausencia de nuevas llaves en este grupo no demuestra que los libros completos sean idénticos; sus hashes son distintos. La cobertura y fechas de extracción siguen pendientes **[E]**.

## Libro auxiliar de matrícula

**[B/C]** `enviar.xlsx`, SHA-256 `1abd4c4c77d1e665796a59129c28b159323bb638c8528b6b04106e02452acf07`, tiene una `Hoja2` con `N_DOC`, `DV`, `CODCLI`, `PLAN_DE_ESTUDIO` y `CODIGO_CARRERA_SIES_FINAL`. No tiene campo de título o fecha de titulación en esa cabecera. Ninguno de los cuatro RUT+DV se encontró mediante la lectura normalizada de `Hoja2`; tampoco se localizó su cuerpo por separado en `Hoja1` o `Hoja2`. En `Hoja2`, 2.993 de 28.933 filas no presentaron cuerpo numérico y DV simple bajo el control aplicado; por tanto no se descartan otras representaciones de documento ni fuentes no examinadas **[E]**. No se presenta la ausencia de coincidencia como inexistencia del expediente en toda la institución.

**[E]** El libro no permite atribuir el título de estos cuatro casos al plan. Tampoco se localizó la implementación del puntaje 2130 en los archivos técnicos examinados; el libro de titulación conserva las razones como valores, no fórmulas.

## Resultado

**[E]** Para estos casos no surgieron nuevas llaves de actividad ni un vínculo formal título–CODCLI–plan. Se conserva la evidencia previa de reconocimiento en 15 pares y se mantienen las equivalencias y atribuciones no acreditadas como pendientes. `analizar.py` registra fuentes y hashes y compara solo en memoria; `RESULTADO_AGREGADO.json` no incluye identificadores individuales. No se cambiaron bases, diccionario, tasas o denominadores; sin commit ni push.
