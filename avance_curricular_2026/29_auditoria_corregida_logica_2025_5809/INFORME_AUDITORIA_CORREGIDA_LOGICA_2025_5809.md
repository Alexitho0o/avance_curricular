# Informe Auditoria Corregida Logica 2025 5809

## Alcance

- Proceso: Avance Curricular SIES 2026.
- Subproyecto: validacion fila a fila de columnas 16-21 del archivo 5809.
- Prioridad: responder si columnas 16-19 fueron calculadas con registros `ANO=2025`.
- Regla operacional: no se modificaron fuentes originales ni el CSV 5809.

## Dictamen global

- DICTAMEN_ANUAL_2025: `BLOQUEO_SIN_CODCLI`
- DICTAMEN_ACUMULADO_2025: `REVISAR_LOGICA_ACUMULADA`

## Resumen de consola requerido

1. Total filas 5809: 2371
2. Filas con CODCLI asociado: 2345
3. Filas sin CODCLI: 26
4. Filas con evidencia 2025: 2225
5. Filas con evidencia 2026 mismo CODCLI: 1172
6. Filas OK columnas 16-19: 1943
7. Filas con diferencia columnas 16-19: 274
8. Filas con estados no clasificados: 8
9. Dictamen anual 2025: BLOQUEO_SIN_CODCLI
10. Dictamen acumulado 2025: REVISAR_LOGICA_ACUMULADA
11. Rutas: Excel `/Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/29_auditoria_corregida_logica_2025_5809/AUDITORIA_CORREGIDA_LOGICA_2025_5809.xlsx`; informe `/Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/29_auditoria_corregida_logica_2025_5809/INFORME_AUDITORIA_CORREGIDA_LOGICA_2025_5809.md`; manifest `/Users/alexi/Documents/GitHub/avance_curricular/avance_curricular_2026/29_auditoria_corregida_logica_2025_5809/manifest_auditoria_corregida_logica_2025_5809.json`; carpeta Escritorio `/Users/alexi/Desktop/AVANCE_CURRICULAR_2026_AUDITORIA_LOGICA_2025_5809_20260707_181435`

## Columnas detectadas en Hoja1

- CODCLI: `CODCLI`
- RUT: `RUT`
- DV: `DIG`
- ANO: `ANO`
- PERIODO: `PERIODO`
- CODRAMO/asignatura: `CODRAMO`
- ESTADO usado para clasificar: `DESCRIPCION_ESTADO`
- NOTA valida: `NOTA_FINAL`
- Motivo NOTA: Valores compatibles con escala 1 a 7; umbral interno >=80%

## Proteccion contra error previo de NOTA

La auditoria invalida como NOTA cualquier columna llamada o equivalente a `CODCLI`, `RUT`, `NUM_DOCUMENTO`, `DV`, `ANO` o `PERIODO`. Tambien invalida candidatos donde mas del 80% de valores parecen identificadores. Por esta regla, `CODCLI` no puede volver a ser usado como nota.

## Catalogo de estado

La clasificacion usa solo patrones explicitos permitidos: APROB/APR/CONVALID/HOMOLOG/RECONOC para aprobado; REPROB/REP/NO APROB/NCR para no aprobado. Senales contradictorias quedan como NO_CLASIFICADO.

- Valores NO_CLASIFICADO en catalogo: 1

## Acumulado B2

- Estado B2: NO_EJECUTABLE
- Motivo: No existe llave plan/carrera directa compatible entre 5809 y Hoja1. CODIGO_UNICO no existe en Hoja1; PLAN_ESTUDIOS del 5809 no intersecta con PLAN_DE_ESTUDIO de Hoja1.

## No listo para carga

No se declara listo para carga: el dictamen global exige revisar o bloquea al menos una parte del proceso, segun las reglas solicitadas.

## Comando reproducible

```bash
cd /Users/alexi/Documents/GitHub/avance_curricular
python3 avance_curricular_2026/29_auditoria_corregida_logica_2025_5809/auditoria_corregida_logica_2025_5809.py
```
