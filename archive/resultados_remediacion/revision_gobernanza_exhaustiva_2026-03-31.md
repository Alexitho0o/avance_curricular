# Revision Exhaustiva de Gobernanza

- Fecha: 2026-03-31 14:03:32
- Alcance: NAC, PAIS_EST_SEC, COD_SED, cobertura contra DatosAlumnos y estado final en ARCHIVO_LISTO_SUBIDA.

## 1) NAC
- Filas gobernanza_nac.tsv: 16
- Valores unicos en DatosAlumnos.NACIONALIDAD: 13
- Valores sin mapeo en catalogo NAC: 0

## 2) COD_SED
- Filas gobernanza_sede.tsv: 2
- Valores unicos en DatosAlumnos.SEDE: 2 -> ['CO', 'RE']
- Valores SEDE sin mapeo: 0

## 3) PAIS_EST_SEC
- Filas gobernanza_pais_est_sec.tsv: 365
- Llaves exactas COMUNA|CIUDAD en DatosAlumnos: 232
- Llaves exactas sin mapeo: 0

## 4) Estado final de salida (v2)
- NAC_STATUS: {'MAPEADO_GOB_NAC': 24607, 'SIN_INSUMO': 220}
- PAIS_EST_SEC_STATUS: {'MAPEADO_GOB_PAIS_EST_SEC': 24607, 'SIN_INSUMO': 220}
- COD_SED_STATUS: {'MAPEADO_GOB_SEDE': 24607, 'SIN_INSUMO': 220}
- DA_MATCH_MODO: {'MATCH_CODCLI': 24607, 'SIN_MATCH': 220}

## 5) Conclusion
- Mapeo completo para los insumos reales presentes en DatosAlumnos del archivo evaluado.