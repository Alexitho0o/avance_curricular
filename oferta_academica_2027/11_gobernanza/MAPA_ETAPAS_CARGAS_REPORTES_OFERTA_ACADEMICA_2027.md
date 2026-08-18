# Mapa de etapas, cargas y reportes - Oferta Academica 2027 (Proceso 2026)

**Institucion:** Codigo IES 162 | **Adscrita al Sistema de Acceso** | Ultima actualizacion: 28/08/2026

Documento de referencia obligatoria. Antes de responder cualquier pregunta sobre "en que etapa
estamos", "cual es el archivo validado", "que reporte descargo" o "cual es el plazo", consultar
este mapa. Fuente: `01_fuentes_oficiales/Instructivo_Oferta_Academica-Acceso_CFT-IP 2027.txt`
(Anexos 1, 2 y 3) y pantalla de Cargas/Reportes Asociados del sistema (captura 28/08/2026).

---

## 1. Las tres etapas

| Etapa | Nombre oficial | Ventana | ID Carga | Que se informa |
|---|---|---|---|---|
| **1** | Oferta Academica Vigente Editada TP Adscritas | **13 al 19 de agosto 2026** (CERRADA) | **17449** | Confirmar vigencia 2027 de los programas ya existentes y editar sus campos modificables |
| **2** | Oferta Academica Nueva TP Adscritas | **21 al 28 de agosto 2026** | **17451** | Programas o versiones NUEVAS, sin historial previo en el sistema |
| **3** | Definicion de Arancel TP | **07 al 11 de septiembre 2026** | **17454** | Arancel anual, valor matricula, costo titulacion, costo certificado y formato valor |

Tipo de carga de Etapa 2 segun el sistema: "Captura IES Incremental", Ano 2026, nombre
"Oferta Academica TP Nueva 2027".

**Las cargas son acumulativas** (instructivo, pags. 31 y 34): cada archivo cargado "Finalizado"
cuenta y no elimina la carga anterior. Los campos que actuan como llave principal, al repetirse
de una carga a otra, actualizan la informacion en lugar de generar un programa nuevo. Por lo
tanto NO hay que re-subir lo ya cargado correctamente.

---

## 2. Los cinco reportes

| ID | Nombre | Etapa | Que contiene | En el proyecto |
|---|---|---|---|---|
| **5913** | Oferta Academica Vigente Inicial 2026 TP Adscritas | 1 | Punto de partida: programas vigentes segun el consolidado final de Oferta Academica 2026. Solo consulta, siempre muestra los datos iniciales | SI - `02_precarga_pes/reporte_dinamico_5913_2026-08-12_08:22:23.csv` |
| **5912** | Oferta Academica Vigente Validada 2027 TP Adscritas | 1 | Resultado validado por Mineduc de la Etapa 1. Incluye vigencia 1 y 2, excluye los puestos como No Vigente (3) | SI - `09_respaldo/reportes_pes_validados/20260824_reporte_5912_etapa1/` (desc. 24/08/2026) |
| **5911** | Oferta Academica Nueva Validada 2027 TP Adscritas | 2 | Resultado validado de la Etapa 2. Solo programas Vigentes con estudiantes nuevos | **NO descargado - PENDIENTE** |
| **5910** | Oferta Academica Vigente y Nueva Validada 2027 TP Adscritas | 1 + 2 | Consolidado de ambas etapas. Es el archivo base recomendado para trabajar la Etapa 3 | **NO descargado - PENDIENTE** |
| **5909** | Oferta Academica Consolidada con Aranceles 2027 TP Adscritas | 3 | Consolidado final con los montos ya declarados | **NO descargado** (corresponde despues de Etapa 3) |

> **Regla de uso:** hablar siempre por numero de reporte. "El validado de Etapa 1" es el **5912**;
> "el validado de Etapa 2" es el **5911**; "el consolidado para aranceles" es el **5910**.
> Un archivo generado por el proyecto NUNCA sustituye a un reporte: acredita lo que se envio,
> no lo que el sistema acepto.

---

## 3. Estructura de archivo por etapa

Las tres etapas usan las **mismas 48 columnas oficiales**, en el mismo orden
(`COD_SEDE` ... `VIGENCIA_CARRERA`). Ver `11_gobernanza/CONTRATO_CAMPOS_ETAPA1_OFERTA_ACADEMICA_2027.tsv`.

Formato de carga verificado empiricamente contra los CSV que genera el propio sistema:

- Delimitador **punto y coma (`;`)**, no coma. El texto del instructivo dice "delimitado por
  comas" (pag. 31), pero los archivos reales del sistema usan `;`. **Discrepancia conocida:
  manda el comportamiento real.**
- Codificacion UTF-8, salto de linea simple (`\n`), sin CRLF.
- **Sin fila de encabezado** y **sin linea final vacia**.
- Antes de cargar se elimina la columna codigo de institucion, las de cantidad de matricula y
  cantidad de beneficios, y los encabezados.
- `FECHA_ADMISION_INICIAL`: el instructivo especifica DD/MM/AAAA; los reportes del sistema la
  exportan como DD-MM-AAAA. **Segunda discrepancia conocida**, misma fecha.

---

## 4. Que va en cada etapa (regla confirmada por SIES el 28/08/2026)

**Un programa es NUEVO (va en Etapa 2) solo si cambia `DURACION_ESTUDIOS` o `DURACION_TOTAL`.**

Textual de SIES: *"Los cambios en la duracion de regimen no afectan la version del programa, por
ende, no son un programa nuevo. Los cambios en duracion de estudios y duracion total si afectan."*

Confirmado empiricamente sobre las 49 filas del archivo institucional, sin una sola excepcion:

- 6 registros con cambio en duracion de estudios/total -> **aceptados** en Etapa 2 como version nueva.
- 12 registros sin cambio en duracion de estudios/total -> **rechazados** con "La Carrera o Programa
  que esta ingresando como nueva, ya existe en la Oferta Vigente Validada."

Cambios que **NO** convierten un programa en nuevo (van por Etapa 1): regimen, duracion de
regimen, anio de inicio, vacantes, arancel, matricula, enlace, fecha de admision, reconocimiento
de aprendizajes previos, y la propia vigencia.

**`VIGENCIA_CARRERA=2 no significa programa cerrado.** Significa "vigente sin estudiantes nuevos"
(con estudiantes antiguos). La validacion de "ya existe" opera igual con vigencia 1 que con 2.
Valores: 1 = Vigente con Estudiantes Nuevos, 2 = Vigente sin Estudiantes Nuevos, 3 = No Vigente.

---

## 5. Rectificacion (cuando la ventana de una etapa ya cerro)

Segun el instructivo (Anexo 1, pag. 19), si se necesita modificar algo fuera de las columnas
permitidas o fuera de plazo, se solicita **Rectificacion por oficio**:

- **Destinatario:** Mauricio Cornejo, Jefe de Division de Informacion y Acceso -
  `mauricio.cornejo@mineduc.cl`
- **Con copia a:** `consultas.sies@mineduc.cl` y `rodrigo.rolando@mineduc.cl`
- **Adjunto:** archivo Excel (.xlsx) con **todos los atributos** solo de los programas a
  rectificar, con los datos ya rectificados, **las celdas con cambios marcadas con color** y
  **con encabezados**. Misma estructura de la Oferta Vigente Editada.
- El instructivo indica hacerlo antes del cierre de la etapa correspondiente.

---

## 6. Historial real de cargas de Etapa 2 (ID 17451)

| Hora (28/08/2026) | Contenido | Resultado |
|---|---|---|
| 13:12:33 | 49 registros (archivo completo) | Rechazadas 12 filas con "ya existe" |
| **13:17:17** | **37 registros** (49 menos las 12 conflictivas) | **ACEPTADA - es la carga vigente** |
| 13:55:59 | 4 registros (prueba aislada Grupo A) | Rechazada, las 4 con "ya existe" |

> **Cuidado al leer la pantalla del sistema:** la columna "Ultima Carga" muestra la fecha del
> **ultimo intento** (13:55:59), no de la ultima carga exitosa. El "N. Registros = 37" corresponde
> a la carga aceptada de las 13:17:17. Un intento rechazado no altera lo ya cargado.

Archivo congelado de la carga vigente:
`09_respaldo/cargas_congeladas/20260828_etapa2_carga_17451/28-08-2026_13-17-17_Oferta-Académica-TP-Nueva-2027.csv`
SHA-256 `afa38755cb5e449011ab226588505238aa41c07acdb65acf31452abc6eb3d38f`, 12.548 bytes.

---

## 7. Estado y pendientes al 28/08/2026

| Item | Estado |
|---|---|
| Etapa 1 (17449) | Ventana cerrada el 19/08. Resultado validado en reporte 5912 |
| Etapa 2 (17451) | 37 registros cargados y aceptados. Ventana cierra hoy 28/08 |
| 12 registros rechazados | No son programas nuevos. Se tramitan por Rectificacion de Etapa 1 con oficio. Excel listo: `07_resultados/borradores_prueba_no_oficiales/RECTIFICACION_ETAPA1_12_PROGRAMAS_20260828.xlsx`. Falta el oficio (pendiente definir firmante) |
| Reporte 5911 | **Descargar y gobernar** en `09_respaldo/reportes_pes_validados/` para acreditar que acepto el sistema en Etapa 2 |
| Reporte 5910 | **Descargar** antes de la Etapa 3; es la base recomendada para armar el archivo de aranceles |
| Etapa 3 (17454) | Del 07 al 11 de septiembre. Los 37 programas nuevos tienen arancel y matricula en -1 y costo de titulacion y certificado en 0: **sin la Etapa 3 quedan sin arancel**, lo que afecta gratuidad, becas y creditos |
