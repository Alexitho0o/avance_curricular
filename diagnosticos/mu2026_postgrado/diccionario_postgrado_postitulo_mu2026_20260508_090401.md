# Diccionario gobernado postgrado/postítulo MU2026

Fecha ejecución: Fri May  8 09:04:01 -04 2026
Archivo creado: control/diccionarios/diccionario_postgrado_postitulo_mu2026.tsv

## 1. Archivo creado
```
-rw-r--r--@ 1 alexi  staff   4.3K May  8 09:04 control/diccionarios/diccionario_postgrado_postitulo_mu2026.tsv
```

## 2. Resumen por ESTADO_GOBERNANZA
```
 8
MATCH_EXACTO_NOMBRE 8
MATCH_MANUAL_GOBERNADO 2
MATCH_NORMALIZADO_NOMBRE 4
POSIBLE_MATCH_REVISION_MANUAL 1
```

## 3. Resumen por ACCION_CARGA
```
 8
EXCLUIR_HASTA_VALIDAR 1
INCLUIR 14
```

## 4. Validación de registros INCLUIR con campos críticos completos
```
INCLUIR_total=14
INCLUIR_incompletos=0
```

## 5. Vista tabular
```
CODCARPR  CODIGOCARRERA  NOMBRE_L_FUENTE                                                   NOMBRE_CARRERA_OFERTA                                             CODIGO_UNICO           COD_SED                                                          COD_CAR  MODALIDAD  JOR  VERSION  NIVEL_GLOBAL  NIVEL_CARRERA  VIGENCIA_OFERTA  ESTADO_GOBERNANZA              ACCION_CARGA           OBSERVACION
DCSARE    DCSARE         DIPLOMADO EN CIBERSEGURIDAD APLICADA                              DIPLOMADO EN CIBERSEGURIDAD APLICADA                              I162S2C53J3V1          2                                                                53       2          3    1        3             5              1                MATCH_EXACTO_NOMBRE            INCLUIR                Detectado por nombre en DatosAlumnos y oferta/matriz.
DCBS      DCBS           DIPLOMADO EN CIBERSEGURIDAD                                       DIPLOMADO EN CIBERSEGURIDAD APLICADA                              I162S2C53J3V1          2                                                                53       2          3    1        3             5              1                MATCH_MANUAL_GOBERNADO         INCLUIR                Nombre fuente abreviado respecto de oferta; se gobierna contra COD_CAR 53.
DREIN     DREIN          DIPLOMADO EN REDES INDUSTRIALES                                   DIPLOMADO REDES INDUSTRIALES                                      I162S2C70J4V1          2                                                                70       3          4    1        3             5              1                MATCH_NORMALIZADO_NOMBRE       INCLUIR                Diferencia menor por uso de EN.
DRID      DRID           DIPLOMADO EN REDES INDUSTRIALES                                   DIPLOMADO REDES INDUSTRIALES                                      I162S2C70J4V1          2                                                                70       3          4    1        3             5              1                MATCH_NORMALIZADO_NOMBRE       INCLUIR                Diferencia menor por uso de EN.
DFSCK     DFSCK          DIPLOMADO EN FULL STACK                                           DIPLOMADO EN FULLSTACK                                            I162S2C66J4V1          2                                                                66       3          4    1        3             5              1                MATCH_NORMALIZADO_NOMBRE       INCLUIR                Diferencia FULL STACK/FULLSTACK.
DICD      DICD           DIPLOMADO EN INFRAESTRUCTURA CLOUD                                DIPLOMADO INFRAESTRUCTURA CLOUD                                   I162S2C69J4V1          2                                                                69       3          4    1        3             5              1                MATCH_NORMALIZADO_NOMBRE       INCLUIR                Diferencia menor por uso de EN.
DHDS      DHDS           DIPLOMADOS EN HABILIDADES DIRECTIVAS                              DIPLOMADO EN HABILIDADES DIRECTIVAS PARA PROFESIONALES STEM       I162S2C98J4V1          2                                                                98       3          4    1        3             5              1                MATCH_MANUAL_GOBERNADO         INCLUIR                Nombre fuente resumido respecto de oferta; se gobierna contra COD_CAR 98.
DACD      DACD           DIPLOMADO EN ARQUITECTURA CLOUD                                   DIPLOMADO EN ARQUITECTURA CLOUD                                   I162S2C63J4V1          2                                                                63       3          4    1        3             5              1                MATCH_EXACTO_NOMBRE            INCLUIR                Detectado explícitamente en matriz.
DFSTK     DFSTK          DIPLOMADO EN FULLSTACK                                            DIPLOMADO EN FULLSTACK                                            I162S2C66J4V1          2                                                                66       3          4    1        3             5              1                MATCH_EXACTO_NOMBRE            INCLUIR                Equivalencia directa si aparece como FULLSTACK.
DQA       DQA            DIPLOMADO EN QUALITY ASSURANCE                                    DIPLOMADO EN QUALITY ASSURANCE                                    I162S2C67J4V1          2                                                                67       3          4    1        3             5              1                MATCH_EXACTO_NOMBRE            INCLUIR                Detectado explícitamente en matriz.
DIA       DIA            DIPLOMADO EN INTELIGENCIA ARTIFICIAL                              DIPLOMADO EN INTELIGENCIA ARTIFICIAL                              I162S2C95J4V1          2                                                                95       3          4    1        3             5              1                MATCH_EXACTO_NOMBRE            INCLUIR                Detectado explícitamente en matriz.
DGD       DGD            DIPLOMADO EN GOBERNANZA DE DATOS                                  DIPLOMADO EN GOBERNANZA DE DATOS                                  I162S2C96J4V1          2                                                                96       3          4    1        3             5              1                MATCH_EXACTO_NOMBRE            INCLUIR                Detectado explícitamente en matriz.
DSCMR     DSCMR          DIPLOMADO EN SUPPLY CHAIN MANAGEMENT Y MINERIA DE REQUERIMIENTOS  DIPLOMADO EN SUPPLY CHAIN MANAGEMENT Y MINERIA DE REQUERIMIENTOS  I162S2C97J4V1          2                                                                97       3          4    1        3             5              1                MATCH_EXACTO_NOMBRE            INCLUIR                Detectado explícitamente en matriz.
DSFEC     DSFEC          DIPLOMADO EN SALUD FAMILIAR CON ENFOQUE COMUNITARIO               DIPLOMADO EN SALUD FAMILIAR CON ENFOQUE COMUNITARIO               I162S2C101J4V1         2                                                                101      3          4    1        3             5              1                MATCH_EXACTO_NOMBRE            INCLUIR                Detectado explícitamente en matriz.
DCSI      DCSI           DIPLOMADO EN CIBERSEGURUDAD INDUSTRIAL                            DIPLOMADO EN CIBERSEGURIDAD APLICADA                              I162S2C53J3V1          2                                                                53       2          3    1        3             5              1                POSIBLE_MATCH_REVISION_MANUAL  EXCLUIR_HASTA_VALIDAR  Nombre fuente no coincide; posible error ortográfico o programa distinto. No incluir sin validación.
ECCURYDP  ECCURYDP       EC CURSOS Y DIPLOMADOS                                            NO_MAPEAR_GENERICO                                                EXCLUIR                Nombre genérico; no permite asignar CODIGO_UNICO único.
DDSC      DDSC           DIPLOMADO EN DATA SCIENCE                                         PENDIENTE_REVISION                                                EXCLUIR_HASTA_VALIDAR  No se encontró equivalente explícito en oferta/matriz revisada.
DDASC     DDASC          DIPLOMADO EN DATA SCIENCE                                         PENDIENTE_REVISION                                                EXCLUIR_HASTA_VALIDAR  No se encontró equivalente explícito en oferta/matriz revisada.
DHIAD     DHIAD          DIPLOMADO HERRAMIENTAS DE IA PARA EL APOYO DOCENTE                PENDIENTE_REVISION                                                EXCLUIR_HASTA_VALIDAR  No se encontró equivalente explícito en oferta/matriz revisada.
DDSS      DDSS           DIPLOMADO DESARROLLO SEGURO DE SOFTWARE                           PENDIENTE_REVISION                                                EXCLUIR_HASTA_VALIDAR  No se encontró equivalente explícito en oferta/matriz revisada.
DAPB      DAPB           DIPLOMADO EN ANALYTICS Y VISUALIZACIÓN DE DATOS CON POWER BI      PENDIENTE_REVISION                                                EXCLUIR_HASTA_VALIDAR  No se encontró equivalente explícito en oferta/matriz revisada.
DGAS      DGAS           DIPLOMADO EN GESTIÓN ÁGIL CON SCRUM                               PENDIENTE_REVISION                                                EXCLUIR_HASTA_VALIDAR  No se encontró equivalente explícito en oferta/matriz revisada.
DLEMS     DLEMS          DIPLOMADO LIDERAZGO ESTRATÉGICO Y MANAGEMENT 4.0                  PENDIENTE_REVISION                                                EXCLUIR_HASTA_VALIDAR  No se encontró equivalente explícito en oferta/matriz revisada.
```

## 6. Regla de uso

- Solo registros con ACCION_CARGA=INCLUIR pueden alimentar el CSV PES-ready.
- Registros con EXCLUIR_HASTA_VALIDAR deben quedar en trazabilidad, no en archivo final.
- Registros NO_MAPEAR_GENERICO no deben mapearse a un único COD_CAR.
- Este diccionario no modifica el flujo pregrado.
