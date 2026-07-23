# Bitácora de cargas — IRE 2026

Registro de cada intento de carga a la plataforma PES (`http://pes.mineduc.cl`) y de las
verificaciones internas del pipeline. Los `.txt` de error que devuelve la plataforma se guardan en
`docs/errores_pes/`.

| Fecha | Archivo / acción | Resultado | Errores devueltos | Acción tomada |
|---|---|---|---|---|
| 2026-07-22 | `make ire-test` (40 tests) | Finalizado | — | Ninguna; suite completa en verde |
| 2026-07-22 | `make ire-generar` (config real, `parametros_2026.yaml` sin llenar) | Detenido por diseño (no es una falla) | Pipeline exige completar 4 claves bloqueantes: `matricula_jornada_principal_2026`, `tenencia.fecha_inicio`, `tenencia.fecha_termino`, `uso_restringido_uss_vigente` | Pendiente: completar `config/parametros_2026.yaml` con los valores 2026 confirmados por la institución |
| 2026-07-22 | `make ire-generar` (config de prueba temporal, valores 2025 reutilizados solo para verificar el pipeline) | Finalizado | — | Verificación interna únicamente; los 3 entregables se generaron y se descartaron. No se subió nada a PES |

## Nota sobre el delimitador

El instructivo de MINEDUC indica "delimitado por comas", pero la estructura oficial
(`data/estructura/20260706_89535_Estructura_IRE_ID_16770.csv`) viene con `;`. El generador produce
ambas variantes (`_puntoycoma.csv` y `_coma.csv`). Registrar aquí cuál acepta la plataforma en el
primer intento real de carga.
