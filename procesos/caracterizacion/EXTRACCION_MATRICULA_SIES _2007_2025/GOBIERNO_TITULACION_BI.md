# Gobierno de Titulación BI

## Alcance

Este flujo procesa la fuente oficial de titulados SIES `TITULADO_2025_web_27_05_2026_E.xlsx`, hoja `in`, y conserva exclusivamente los registros de la institución `162` (Instituto Profesional San Sebastián).

## Componentes

- `procesar_titulados_ipss.py`: lectura, detección de columnas, filtro IPSS 162, limpieza de años y exportación tabular.
- `matrices_titulacion_bi.py`: agrega matrices prefacturadas por año, sede, carrera y programa.
- `docs/glosarios_oficiales/titulados/GLOSARIO_DE_TITULADO_2007_2025_E.txt`: glosario técnico SIES utilizado como referencia de nombres y significado.

## Modelo tabular

La salida no contiene gráficos ni columnas ocultas. Los años se almacenan como enteros. Las métricas de titulaciones se mantienen como conteos numéricos para permitir agregación en Power BI.

Tablas secundarias generadas:

- `Matriz_Titulados_Anual`
- `Matriz_Titulados_Sede`
- `Matriz_Titulados_Carrera`
- `Matriz_Titulados_Programa`

## Diccionario mínimo

| Concepto | Regla |
|---|---|
| Año del Proceso | Año en que ocurre el proceso de titulación. |
| Código de Institución | Se filtra exactamente por `162`. |
| Total de Titulaciones | Suma total de titulaciones del registro. |
| Titulaciones Mujeres | Suma de titulaciones de mujeres. |
| Titulaciones Hombres | Suma de titulaciones de hombres. |
| Titulaciones NB e Indefinido | Suma de titulaciones no binarias o indefinidas. |
| Programa | Llave de agrupación del programa/carrera según la fuente oficial. |

## Reglas de calidad

1. No se inventan columnas ausentes: el script detiene la ejecución y enumera las columnas faltantes.
2. Los valores vacíos de contadores se tratan como cero al agregar.
3. Los años no reciben formato de miles.
4. La fuente original no se modifica.
5. La fuente concreta debe estar disponible localmente antes de ejecutar el flujo.

## Ejecución

```bash
python3 procesar_titulados_ipss.py --entrada /ruta/TITULADO_2025_web_27_05_2026_E.xlsx
python3 matrices_titulacion_bi.py
```