# Identificacion Matricula Oficial 2025

Fecha: 2026-06-18 10:51:06

No se encontro un archivo nombrado explicitamente como "matricula unificada 2025 congelada/oficial". La fuente principal local disponible para evidencia 2025 es `resultados/matricula_avance_curricular_2025_control.csv`, respaldada por `resultados/matricula_avance_curricular_2025_pes_ready.csv`.

## Conteos de reconstruccion

{
  "MATRICULA_OFICIAL_2025": 99,
  "OTRA_EVIDENCIA_2025": 5
}

## Jerarquia aplicada

| Prioridad | Fuente | Archivo | Estado | Decision |
|---:|---|---|---|---|
| 1 | Reporte Precarga del Proceso Extranjeros Regulares 2026 | `NO_ENCONTRADO_LOCALMENTE` | PRECARGA_NO_ENCONTRADA | No reemplazar silenciosamente; queda brecha institucional. |
| 2 | Control local avance/matricula 2025 | `resultados/matricula_avance_curricular_2025_control.csv` | PRINCIPAL_DISPONIBLE | Usar para reconstruir universo con nacionalidad cruzada; requiere confirmacion de si corresponde a entrega oficial SIES. |
| 2 | PES ready avance curricular 2025 | `resultados/matricula_avance_curricular_2025_pes_ready.csv` | COMPLEMENTARIA | No usar como fuente de campos por ausencia de encabezado; conservar como evidencia de entrega/preparacion. |
| 3 | DatosAlumnos y Hoja1 2025 | `input/PROMEDIOSDEALUMNOS_7804.xlsx` | COMPLEMENTARIA_2025 | Usar para agregar casos con ANOMATRICULA=2025 no presentes en control principal. |
| 4 | Archivo listo para SIES / MU2026 | `resultados/archivo_listo_para_sies.xlsx` | SOLO_APOYO_2026 | No usar para demostrar matricula efectiva 2025. |
