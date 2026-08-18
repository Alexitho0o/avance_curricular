# Contrato de columnas - Etapa 2 (Oferta Academica Nueva TP Adscritas)

Proceso: SIES Oferta Academica-Acceso 2027. Etapa 2 - Oferta Academica Nueva TP Adscritas.
Fuente primaria: Instructivo_Oferta_Academica-Acceso_CFT-IP 2027.txt (paginas 35-41: estructura; paginas 57-64: Anexo 4 validaciones y advertencias)

Columnas oficiales (estructura Anexo 2, pag. 35-41): **48**
Columnas del archivo institucional recibido: **49**
Clasificacion estructural del archivo: **FUENTE_INSTITUCIONAL_PENDIENTE_DE_CONFIRMACION_ESTRUCTURAL**

## Motivo de la clasificacion

Las columnas 1-48 del archivo recibido coinciden EXACTAMENTE en nombre y orden con la tabla de estructura oficial del instructivo (pag. 35-41). Sin embargo: (a) no existe un archivo de estructura oficial descargado independientemente de PES contra el cual confirmar de forma cruzada; (b) el archivo recibido tiene una columna 49 (SECTOR IPSS) ajena a esa estructura; (c) existen contradicciones internas no resueltas en el propio instructivo sobre el tratamiento de VERSION y sobre el rango de fechas aplicable a 2027. Por estas razones no se declara el archivo listo para carga.

## Contradicciones internas detectadas en el propio instructivo (no resueltas)

### VERSION

La tabla de estructura de Etapa 2 (pagina 35, linea 1203) declara VERSION como 'Obligatorio. Modificable', campo numerico correlativo. El Anexo 4 (pagina 59, linea 2008 y pagina 64, linea 2256) declara textualmente 'La VERSION no corresponde.' dentro del mismo instructivo y aplicable al bloque de Oferta Academica Nueva.

Resolucion: NO_RESUELTA. No se aplica tratamiento automatico (ni carga, ni vaciado, ni eliminacion de la columna). Requiere consulta formal a SIES antes de definir el tratamiento de VERSION en el CSV final.

### FECHA_ADMISION_INICIAL / ANIO_INICIO

El Anexo 4 cita reiteradamente (paginas 58-59 y 63-64) el rango 'no anterior al 02/10/2025 ni posterior al 03/04/2026 o 04/04/2026' para FECHA_ADMISION_INICIAL, y 'no puede ser posterior a 2026' para ANIO_INICIO (pagina 62). El proceso vigente corresponde a admision 2027. No se encontro en ningun punto del instructivo un rango de fechas explicito para 2027.

Resolucion: NO_RESUELTA. Se marca FECHA_ADMISION_INICIAL y ANIO_INICIO como PENDIENTES_DE_CONFIRMACION. No se traslada por analogia el rango 2025-2026 ni el limite 2026.

### MALLA_CURRICULAR / PERFIL_EGRESO

El Anexo 4, bloque especifico de Oferta Academica Nueva (pagina 61-62), incluye las reglas 'Cuando la VIGENCIA_CARRERA es 1, se debe completar la MALLA_CURRICULAR' y '...se debe completar la PERFIL_EGRESO', pero ninguno de los dos campos aparece en la tabla de estructura de columnas de Etapa 2 (pag. 35-41, 48 columnas) ni en el archivo institucional recibido.

Resolucion: NO_RESUELTA. No se agregan estas columnas a la carga (regla de no agregar columnas por cuenta propia). Se registra como pendiente de confirmacion si corresponden a enlaces/antecedentes fuera del CSV (posiblemente cubiertos por el archivo institucional separado 'Mallas y perfiles de egreso.xlsx', que es solo antecedente, no fuente oficial) o si el instructivo esta usando texto no actualizado de otra etapa.

## Resumen de columnas (ver TSV/JSON para el detalle completo por campo)

- **01 (A) COD_SEDE** - Obligatorio. Modificable - pag.35 lin.1169
- **02 (B) NOMBRE_SEDE** - Obligatorio. Modificable - pag.35 lin.1174
- **03 (C) COD_CARRERA** - Dejar en blanco (regla explicita del manual, pagina 32 y 35) - pag.35 lin.1180
- **04 (D) NOMBRE_CARRERA** - Obligatorio. Modificable - pag.35 lin.1186
- **05 (E) MODALIDAD** - Obligatorio. Modificable - pag.35 lin.1193
- **06 (F) COD_JORNADA** - Obligatorio. Modificable - pag.35 lin.1199
- **07 (G) VERSION** - CONTRADICTORIO: pag.35 lo declara 'Obligatorio. Modificable'; Anexo4 pag.59 y pag.64 declaran 'La VERSION no corresponde.' dentro del mismo instructivo. - pag.35 lin.1203 [CONTRADICCION_INTERNA_MANUAL_PENDIENTE_CONFIRMACION]
- **08 (H) COD_TIPO_PLAN_CARRERA** - Obligatorio. Modificable - pag.35 lin.1207
- **09 (I) CARACTERISTICAS_TIPO_PLAN** - Obligatorio. Modificable - pag.36 lin.1216
- **10 (J) DURACION_ESTUDIOS** - Obligatorio. Modificable - pag.36 lin.1224
- **11 (K) DURACION_TITULACION** - Obligatorio. Modificable - pag.36 lin.1231
- **12 (L) DURACION_TOTAL** - Obligatorio. Modificable - pag.36 lin.1237
- **13 (M) REGIMEN** - Obligatorio. Modificable - pag.36 lin.1243
- **14 (N) DURACION_REGIMEN** - Obligatorio. Modificable - pag.36 lin.1248
- **15 (O) NOMBRE_TITULO** - Obligatorio. Modificable - pag.36 lin.1254
- **16 (P) COD_NIVEL_GLOBAL** - Obligatorio. Modificable - pag.37 lin.1260
- **17 (Q) COD_NIVEL_CARRERA** - Obligatorio. Modificable - pag.37 lin.1265
- **18 (R) ANIO_INICIO** - Obligatorio. Modificable - pag.37 lin.1272 [LIMITE_FECHA_SIN_CONFIRMAR_2027]
- **19 (S) ACREDITACION** - Obligatorio. Modificable - pag.37 lin.1276 [DOMINIO_CON_DISCREPANCIA_MENOR_ENTRE_SECCIONES]
- **20 (T) REQUISITO_INGRESO** - Obligatorio. Modificable - pag.37 lin.1282
- **21 (U) SEMESTRES_RECONOCIDOS** - Obligatorio. Modificable - pag.37 lin.1289
- **22 (V) AREA_ACTUAL** - Obligatorio. Modificable - pag.37 lin.1300
- **23 (W) AREA_ADMIN_DERECHO** - Obligatorio. Modificable - pag.37 lin.1312
- **24 (X) AREA_AGRI_SILVI_PESCA_VET** - Obligatorio. Modificable - pag.38 lin.1324
- **25 (Y) AREA_ARTES_HUMANIDADES** - Obligatorio. Modificable - pag.38 lin.1333
- **26 (Z) AREA_CIENCIAS_NAT_MAT_ESTAD** - Obligatorio. Modificable - pag.38 lin.1344
- **27 (AA) AREA_CS_SOCIAL_PERIODISMO_INFO** - Obligatorio. Modificable - pag.38 lin.1355
- **28 (AB) AREA_EDUCACION** - Obligatorio. Modificable - pag.38 lin.1363
- **29 (AC) AREA_INGE_INDUSTRIA_CONSTRUC** - Obligatorio. Modificable - pag.38 lin.1372
- **30 (AD) AREA_SALUD_BIENESTAR** - Obligatorio. Modificable - pag.39 lin.1384
- **31 (AE) AREA_SERVICIOS** - Obligatorio. Modificable - pag.39 lin.1391
- **32 (AF) AREA_TECNO_INFO_COMUNICA** - Obligatorio. Modificable - pag.39 lin.1399
- **33 (AG) VACANTES_PRIMER_SEMESTRE** - Obligatorio. Modificable - pag.39 lin.1406 [TEXTO_ESTRUCTURA_MENCIONA_2026_REVISAR]
- **34 (AH) VACANTES_SEGUNDO_SEMESTRE** - Obligatorio. Modificable - pag.39 lin.1411 [TEXTO_ESTRUCTURA_MENCIONA_2026_REVISAR]
- **35 (AI) FECHA_ADMISION_INICIAL** - Obligatorio si VIGENCIA_CARRERA=1 (Anexo4 pag.61) - pag.39 lin.1415 [CONTRADICCION_FECHA_PENDIENTE_CONFIRMACION]
- **36 (AJ) ENLACE_INFO_PROGRAMA** - Obligatorio. Modificable - pag.39 lin.1422
- **37 (AK) LICENCIA_ENS_MEDIA** - Obligatorio. Modificable - pag.39 lin.1429 [DOMINIO_INCOMPLETO_EN_MANUAL_SOLO_CITA_SI]
- **38 (AL) NOTAS_ENS_MEDIA** - Obligatorio. Modificable - pag.40 lin.1436
- **39 (AM) PROMEDIO_MIN_ENS_MEDIA** - Obligatorio. Modificable - pag.40 lin.1442
- **40 (AN) RECONOCIMIENTOS_APREN_PREVIOS** - Obligatorio si VIGENCIA_CARRERA=1 (Anexo4 pag.61: 'Cuando la VIGENCIA_CARRERA es 1, se debe completar el RECONOCIMIENTOS_APREN_PREVIOS') - pag.40 lin.1449 [RESPALDADO_ESTRUCTURA_Y_ANEXO4_OBLIGATORIO_SI_VIGENTE]
- **41 (AO) EXPERIENCIA_LABORAL** - Obligatorio. Modificable - pag.40 lin.1455
- **42 (AP) MAIL_DIFUSION_CARRERA** - Obligatorio. Modificable - pag.40 lin.1459
- **43 (AQ) FORMATO_VALOR** - Obligatorio. Modificable - pag.40 lin.1463
- **44 (AR) VALOR_MATRICULA_ANUAL** - Obligatorio. Modificable - pag.40 lin.1468 [EXCEPCION_MENOS1_DOCUMENTADA_SOLO_PARA_ETAPA_ARANCELES]
- **45 (AS) COSTO_TITULACION** - Obligatorio. Modificable - pag.40 lin.1473
- **46 (AT) VALOR_CERTIFICADO_DIPLOMA** - Obligatorio. Modificable - pag.40 lin.1478
- **47 (AU) ARANCEL_ANUAL** - Obligatorio. Modificable - pag.41 lin.1485
- **48 (AV) VIGENCIA_CARRERA** - Obligatorio. Modificable - pag.41 lin.1489
- **49 (AW) SECTOR IPSS** - NO CORRESPONDE A LA ESTRUCTURA OFICIAL DE CARGA ETAPA 2 - pag.35-41 (ausente) lin.N/A [COLUMNA_NO_RECONOCIDA_EN_ESTRUCTURA_OFICIAL]

## Archivos de esta fase

- JSON completo: 11_gobernanza/REGLAS_MANUAL_ETAPA2_OFERTA_NUEVA_2027_20260827.json
- TSV: 11_gobernanza/REGLAS_MANUAL_ETAPA2_OFERTA_NUEVA_2027_20260827.tsv
- Markdown ejecutivo: 11_gobernanza/REGLAS_MANUAL_ETAPA2_OFERTA_NUEVA_2027_20260827.md (este archivo)