# H011 · código de seguimiento por duración total y T1

**CANDIDATA.** Alexi retiró la premisa que atribuía un tipo de plan a RE o CO. Son sedes. Para los 22 planes REOL del residual, H002 acredita modalidad no presencial. El régimen S/A del listado corresponde a la asignatura. El plan ADMP20251 tiene 65 filas S en el listado y actividad trimestral en PROMEDIOS. El Paso 1c queda acreditado por esa diferencia de grano. La distribución literal de 277 filas CO dejó de intervenir en el control.

**D5.** Primero se consulta el perfil v2 por carrera, plan y sede. Para un perfil faltante se toma el máximo NIVEL por CODPESTUD y el régimen observado en PROMEDIOS. En bimestral se aplica 2/5 por nivel, en semestral se conserva el nivel y en trimestral se aplica ceil(2n/3) de docs/SEGUIMIENTO_RUT_Y_CONVERSION_PERIODOS_20261023.md. La zona inclusiva de 0,1 alrededor de x,5 queda E. Se exige igualdad entera con DURACIÓN TOTAL anual. El código compatible aporta el tipo. Si dos perfiles de igual duración tienen tipos distintos, queda E. Los nombres y las sedes por sí solos no seleccionan el tipo.

**B/C.** TABLA_22_REOL.md contiene los 22 planes con candidatos por año, duración total, tipo y elección o E. El catálogo candidato está en data/paridad_codigo_sies/tipo_plan_h011_20261030/TIPO_PLAN_v3_CANDIDATO.json. El período nativo y la clasificación documental previa se conservan. La asignación individual candidata está únicamente en almacenamiento privado.

| Universo | Antes | Después | Residual E |
|---|---:|---:|---:|
| 3.049 contextos | 2.085 | 2.872 | 177 |
| 99 posiciones | 99 | 99 | 0 |

| Decisión de entrada | Nivel resultante | Nuevas |
|---|---|---|
| D4 | ARRASTRE_ULTIMO_T1 | 42 |
| D5 | CAMBIO_PLAN_SEDE_CATALOGO_D3 | 51 |
| D5 | NUNCA_INFORMADO | 74 |
| D5 | PRIMER_T1_POSTERIOR | 92 |
| D6 | ARRASTRE_ULTIMO_T1 | 14 |
| D6 | HERENCIA_T1_MISMO_AÑO | 6 |
| D6 | NUNCA_INFORMADO | 208 |
| D6 | PRIMER_T1_POSTERIOR | 300 |

Cada alta se cuenta una vez. Las filas nativas 4/5 entran por D6, incluso cuando su código proviene del último T1. El nivel ARRASTRE_ULTIMO_T1 recoge esos casos y los antiguos de D4. Un T1 no compatible con la oferta del año queda E.

## Residual histórico

| Motivo | Contextos | Requisito de cierre |
|---|---|---|
| AMBIGUEDAD_ANUAL_PERSISTENTE | 15 | Distinguir las versiones anuales compatibles con respaldo de expediente/plan. |
| PERIODO_45_SIN_REOL_BIMESTRAL_ACREDITADO | 6 | Definición y decisión específica de período para esos tres contextos semestrales y tres trimestrales. |
| PRIMER_T1_POSTERIOR_AMBIGUO_O_DIMENSIONES_DISTINTAS | 6 | Acreditar versión única y sede/jornada del primer T1 de ese expediente. |
| SIN_CALCE_DURACION_TOTAL_TIPO_MODALIDAD | 16 | Corregir o acreditar perfil formal y duración total de la versión anual. |
| SIN_CODIGO_ANUAL_COMPATIBLE | 2 | Acreditar un código anual compatible con el plan. |
| SIN_FAMILIA_H002_U_OFERTA_ANUAL | 5 | Acreditar familia exacta y presencia en oferta del año. |
| SIN_VIGENCIA_1_COMPATIBLE | 28 | Versión VIGENCIA 1 del tipo compatible o decisión explícita para la excepción. |
| T1_NO_COMPATIBLE_CON_OFERTA_CONTEXTO | 5 | Acreditar equivalencia del código del T1 con el tipo/duración y oferta del año del contexto. |
| VARIAS_VIGENCIA_1_COMPATIBLES | 94 | Documento que determine cuál de varias versiones con VIGENCIA 1 corresponde al expediente. |

El residual es 5,81 % frente a la meta ≤0,1 %. Los requisitos de cada grupo están en REQUISITOS_E_H011.json y el desglose por plan, año, período, sede y jornada en RESIDUAL_H011.json. La revisión de 99 posiciones mantiene residual cero.

## Controles

R01–R04 y R19 tienen 0,00 pp de cambio por conservación de las fuentes. Se verificaron por SHA-256. v20 activo y v21 candidata. La reproducción y la privacidad se documentan en QA_H011.json. FUENTES_H011.json fija las entradas, incluida la conversión trimestral. La reproducción usa aplicar_h011.py seguido de cerrar_h011.py.
