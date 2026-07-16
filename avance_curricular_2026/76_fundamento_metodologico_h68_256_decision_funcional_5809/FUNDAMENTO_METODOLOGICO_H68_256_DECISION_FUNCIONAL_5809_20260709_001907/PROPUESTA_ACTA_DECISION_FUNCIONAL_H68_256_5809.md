# Propuesta de decisión funcional — Cierre H68 256 casos 16-19

## Proceso

Avance Curricular SIES 2026.

## Subproyecto

Archivo 5809 Matrícula Avance Curricular, columnas 16-19.

## Año referencia datos

2025.

## Antecedente

H68 consolidó 256 casos cerrables solo con decisión funcional:

- 218 casos COLUMNA_19_SOLO_A.
- 21 casos ESTADO_ACADEMICO_SIN_REGISTROS_2025.
- 17 casos PERIODO_NO_1_2.

## Fundamento metodológico

### 218 COLUMNA_19_SOLO_A

Se propone validar el cierre sin cambio porque H61 mostró que los 218 casos calzan con el escenario SOLO_A, y H66 vinculó ese tratamiento con el instructivo oficial de Avance: las unidades aprobadas anuales excluyen validación/reconocimiento. E/I son datos observados en PROMEDIOS, no regla oficial.

### 21 SIN REGISTROS 2025

Se propone validar el cierre sin cambio porque H63 mostró ausencia de registros académicos 2025 para CODCLI_LISTA y H66 corrigió la interpretación de estados observados: ELIMINADO 20 y ELIMINADO | VIGENTE 1. No se usa “inactivo” como estado.

### 17 PERIODO_NO_1_2

Se propone validar el cierre sin cambio solo con decisión explícita porque H67 no encontró regla oficial para PERIODO raw 1-5. El escenario que calza con 5809 es mantener sin cambio 17/17, pero no aplicar mapeo automático de período.

## Decisión propuesta

Registrar como decisión funcional:

1. Cerrar los 256 casos H68 sin corrección de datos.
2. Mantener los valores originales del archivo 5809 para esos 256 casos.
3. No aplicar mapeos no oficiales.
4. No modificar fuentes originales.
5. No generar archivo de carga.
6. No generar SIES_READY.
7. Mantener 167 casos H72 bloqueados por evidencia faltante.
8. Mantener 20-21 como frente separado.

## Dictamen post decisión propuesta

Si esta decisión se registra, el estado quedaría:

- 256 cerrados sin cambio por decisión funcional.
- 167 bloqueados por evidencia faltante.
- 0 corregibles por terminal.
- NO_LISTO_PARA_CARGA.
- NO_APTO_PARA_CARGA.
