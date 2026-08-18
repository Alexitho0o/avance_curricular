# Carga congelada — Oferta Académica Acceso 2027 — Etapa 1

## Estado

Carga preparada para la subida a SIES.

- Estado de congelamiento: LISTA PARA SUBIR.
- Fecha y hora de congelamiento: 20260817_155153.
- Fuente institucional: 20260815 Etapa 1 excel_kmg.xlsx.
- Fuente de VERSION: reporte dinámico SIES 5913.
- Total de registros: 103.
- Total de filas CSV: 103.
- Total de columnas por fila: 48.
- Encabezados en CSV: No.
- Codificación CSV: UTF-8.
- Delimitador CSV: punto y coma (;).

## Reglas aplicadas

1. Se mantuvieron las 103 filas de la fuente; no se eliminó ni resumió ningún registro.
2. Se aplicaron 6 correcciones confirmadas:
   - Campo: AREA_INGE_INDUSTRIA_CONSTRUC.
   - Valor final: 0.
3. Para VIGENCIA_CARRERA = 1:
   - FECHA_ADMISION_INICIAL es obligatoria.
   - Debe estar entre 02/10/2026 y 04/04/2027.
   - Se corrigieron 44 fechas inválidas al valor 02/10/2026.
4. Para VIGENCIA_CARRERA = 2:
   - FECHA_ADMISION_INICIAL debe estar vacía.
5. Validación final de reglas VIGENCIA_CARRERA / FECHA_ADMISION_INICIAL:
   - Errores restantes: 0.

## Archivos congelados

| Archivo | Uso | SHA-256 |
|---|---|---|
| CARGA_ETAPA1_OFERTA_ACADEMICA_2027_FINAL_VIGENCIA_Y_FECHA_CORRECTAS.csv | Archivo sin encabezados para cargar en SIES | 8e5207cf1d54357af1cb2b7c144c4ba0ca3477569a97a887a6f686f2f76ec743 |
| CONTROL_CARGA_ETAPA1_2027_VIGENCIA_Y_FECHA_CORRECTAS.xlsx | Evidencia, control y trazabilidad de modificaciones | e3d74ea8f82d4ba27cede375d23521b8b8a9c43f6f85899f90a19f799821cf3f |

## Resultado de validación

```text
Filas procesadas: 103
Filas CSV generadas: 103
Filas omitidas: 0
Columnas por cada fila CSV: 48
Correcciones AREA_INGE aplicadas: 6
Fechas vaciadas porque VIGENCIA_CARRERA=2: 0
Fechas corregidas porque VIGENCIA_CARRERA=1: 44
Errores restantes de vigencia/fecha: 0
Estado final: APTO PARA SUBIR
```
