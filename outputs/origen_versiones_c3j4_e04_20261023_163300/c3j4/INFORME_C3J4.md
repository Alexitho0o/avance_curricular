# C3/J4: origen observable de 50 cambios V1→V2 (2021–2022)

## Resultado

- **B/C** Se reprodujeron exactamente 50 personas y 50 contextos persona/CODCLI/plan IETMREOL20211 del diccionario v7. No se modificó el diccionario ni los denominadores.
- **B** Las 50 tienen V1 en MAT_2021 y V2 en cuatro fuentes 2022 contrastadas: CSV enviado, respaldo Excel, publicado y matrícula de ambos semestres. Las seis fuentes tienen 50/50 coincidencias por identidad; no se generaron uniones muchos-a-muchos. Las listas exactas de filas están en PRIMARY.json.
- **B** VERSION/código único son valores literales en esas celdas: ninguna contiene fórmula. El CSV 2022 ya contiene V2 antes de la consolidación de 2026.
- **C** construir_base_retencion_mu_2022_2026.py selecciona RAW2022 (línea33), mapea encabezados (235) y copia el campo mediante typed_value (264–265; función189–206). VERSION sólo se tipa como entero: este código no crea el cambio V1→V2.

## Variable separadora observada

| Transición 2021→2022 | Personas comunes en familia C3/J4 | FECH_CAR RAW2022 | Clase |
|---|---:|---|---|
| V1→V2 | 58 (incluye las 50) | 06/05/2022 16:14 | B/C |
| V1→V1 | 2 | 06/05/2022 0:11 | B/C |
| V2→V2 | 15 | 06/05/2022 16:14 | B/C |

- **B** Familia completa 2022: V1=3 filas, todas lote00:11; V2=155 filas,153 lote16:14 y2 lote16:38. No se encontraron duplicados de persona en la familia comparada:2021 = 139 filas/personas,2022 = 158 filas/personas, 75 comunes.
- **B** Los 2 conservados V1 comparten con las 50 foco ingreso actual2021-1, VIG1, modalidad3, FOR_ING_ACT1, perfil regular8 semestres. También tienen contexto IETMREOL20211 en el diccionario. Estas variables no separan las versiones.
- **B** De las 58 transiciones,50 tienen ingreso actual2021-1 y8 ingreso2020-2, conservado entre fuentes. En 11 de las 50 cambia el año de origen de un valor anterior a2021 a2021. No se afirma que ese cambio haya causado la versión.
- **E** FECH_CAR discrimina perfectamente los lotes observados, pero no es una regla académica documentada ni acredita el motivo de la asignación. Puede señalar el punto de preparación/carga donde buscar; no permite decidir que un lote está equivocado.

## Límite de la evidencia

- **B/E** Los informes primarios no conservan CODCLI ni PLAN_DE_ESTUDIO. La identidad es contrastable, y el diccionario atribuye el contexto; no se ha localizado aquí un registro con fecha efectiva de migración del plan para esas 50 personas.
- **B** Los metadatos de MAT_2021 y MAT_2022 señalan creación en agosto2023; el respaldo2022.xlsx fue creado en abril2024. Son fechas de los archivos observados, no fechas de la decisión funcional2022. FECH_CAR es un campo del registro, no prueba de autoría de la regla.
- **E** Sigue sin acreditarse la consulta/script que produjo VERSION=2 en el lote06/05/2022 16:14, ni la regla/decisión que dejó tres filas en el lote00:11. Root realiza en paralelo el contraste de Git. No corresponde inventar una migración por año/plan ni aplicar corrección.

## Trazabilidad y reproducción

- Script de auditoría de sólo lectura: `/Users/alexi/Documents/GitHub/avance_curricular/scripts/origen_versiones_c3j4_e04_20261023/c3j4/rastrear_transiciones_c3j4_2021_2022.py`. Fija DB v7 explícitamente; no depende del puntero activo.
- Resultados agregados: `PRIMARY.json`, `PATRONES.json`, `SEPARACION.json`, `LOTES.json`.
- QA ejecutado: 50 personas / 50 contextos,50 filas por cada fuente,0 fórmulas código y cardinalidad fuente sin duplicados. Ningún identificador individual escrito en los resultados.
- Sin escritura sobre originales, Excel, diccionario, bases o Git. No commit/push.

## Fuentes y hashes

- **B** `/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/RESPALDO SIES ENVIADO POR CARLOS ARAVENA EL 24-9/Matricula/2022.xlsx`; hoja `2022`; SHA-256 `ed4e2552e791848d4392066edd54de7ef2ab7d4603957d62ada5aa5174797038`; 50 filas foco (localizadores completos en JSON).

- **B** `/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/Datos DAI (RAW) - 1.1 Datos crudos/1.2.1 Datos Institucionales/1.2.1.1 SIES/Publicados/Matrícula Unificada/MAT_IP_CIISA_2021.xlsx`; hoja `MAT_2021`; SHA-256 `8f14b670f00f725412d9dadffea5db9ad2de97b536c88dad992d4370252c401e`; 50 filas foco (localizadores completos en JSON).

- **B** `/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/Datos DAI (RAW) - 1.1 Datos crudos/1.2.1 Datos Institucionales/1.2.1.1 SIES/Publicados/Matrícula Unificada/2022 - 1098/MAT_IP_CIISA_2022.xlsx`; hoja `MAT_2022`; SHA-256 `28c826e409e50c482749c1e6cbb6426da86acbbd27e758d80355356a3367fb71`; 50 filas foco (localizadores completos en JSON).

- **B** `/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/Datos DAI (RAW) - 1.1 Datos crudos/1.2.1 Datos Institucionales/1.2.1.5 Otros/Matrícula 1er y 2do semestre/MAT_IP_CIISA_2021_1er y2do semestre.xlsx`; hoja `MAT_2021`; SHA-256 `21174b560957fcc94f00459f8f4c0c44cbaf0beab548aab570f078ee01dbd36b`; 50 filas foco (localizadores completos en JSON).

- **B** `/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/Datos DAI (RAW) - 1.1 Datos crudos/1.2.1 Datos Institucionales/1.2.1.5 Otros/Matrícula 1er y 2do semestre/MAT_IP_CIISA_2022_1ro y 2do semestre.xlsx`; hoja `MAT_2022`; SHA-256 `b1297a66881d5f3f8fb2bd7bda90ccad03144a350dcd1fcbd5152b1554e4ac25`; 50 filas foco (localizadores completos en JSON).

- **B** `/Users/alexi/Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/Datos DAI (RAW) - 1.1 Datos crudos/1.2.1 Datos Institucionales/1.2.1.1 SIES/Enviados/Matrícula Unificada/2022/2022.csv`; hoja `CSV con encabezados`; SHA-256 `08ee0b7973f4a2705b388c73413f2ce5402b849f8c3c09c3843d5c2f8c060a4f`; 50 filas foco (localizadores completos en JSON).

- **C** `/Users/alexi/Documents/GitHub/avance_curricular/scripts/construir_base_retencion_mu_2022_2026.py`; SHA-256 `edcade5f199443517ce6ec88a7c43a58cf52ee80a671ab0b9eddec0f1e6de19e`.

## QA de identidad y cardinalidad

- **B/C** 50 personas = 50 CODCLI distintos = 50 contextos. Las 75 personas comunes en la familia tienen exactamente una fila y un código en cada año; también las 50 del foco. No hubo colapso de códigos múltiples.
- **B** RAW 2022 declara TIPO_DOC=R para 50/50 del foco y 75/75 comunes. MAT_2021 no contiene TIPO_DOC; se cruzó MM_N_DOCUMENTO + MM_DV. El pasaporte está vacío para las 50; no se inventó un tipo documental para 2021.
