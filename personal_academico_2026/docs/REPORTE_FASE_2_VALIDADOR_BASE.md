# Reporte Fase 2 - Validador Base Personal Academico SIES 2026

Fecha: 2026-06-08.

## 1. Objetivo De La Fase

Construir la base tecnica del validador y exportador controlado para Personal Academico SIES 2026, manteniendo todo el trabajo dentro de `personal_academico_2026/` y sin generar archivos oficiales definitivos con datos reales.

## 2. Archivos Creados

- `bitacoras/BITACORA_FASE_2_VALIDADOR_BASE.md`
- `scripts/config_personal_academico_2026.py`
- `scripts/validaciones_personal_academico_2026.py`
- `scripts/validar_archivo_personal_academico_2026.py`
- `scripts/exportar_personal_academico_2026.py`
- `tests/fixtures/en_institucion_valido_minimo.csv`
- `tests/fixtures/fuera_institucion_valido_minimo.csv`
- `tests/fixtures/en_institucion_columnas_mal_orden.csv`
- `tests/fixtures/fuera_institucion_columna_extra.csv`
- `tests/fixtures/en_institucion_duplicado_documento.csv`
- `tests/test_validaciones_personal_academico_2026.py`
- `docs/REPORTE_FASE_2_VALIDADOR_BASE.md`

## 3. Archivos Modificados

- `README.md`
- `INSTRUCCIONES_PERSONAL_ACADEMICO_2026.md`
- `docs/DICCIONARIO_PERSONAL_ACADEMICO_2026.md`

## 4. Archivos No Tocados Fuera Del Modulo

No se modificaron archivos fuera de `personal_academico_2026/`. No se tocaron `Makefile`, `scripts/`, `src/`, `core/`, `cned/`, `control/`, `data/`, `resultados/`, `archive/` ni carpetas historicas.

## 5. Decisiones Tecnicas Tomadas

- Se centralizaron rutas, nombres oficiales y columnas en `config_personal_academico_2026.py`.
- Se uso `;` para leer estructuras y fixtures porque las estructuras observadas lo usan.
- Se dejo coma como delimitador de salida por defecto en el exportador porque el instructivo menciona CSV delimitado por comas.
- La decision de delimitador final queda **PENDIENTE DE CONFIRMACION** y registrada en auditoria.
- El exportador queda bloqueado por defecto mediante `--permitir-exportacion-final false`.
- Las auditorias se escriben en `personal_academico_2026/auditorias/`.
- Las pruebas usan datos ficticios y no datos reales.

## 6. Reglas Normativas Utilizadas

- Carga en PES como medio oficial.
- Archivo completado en formato CSV.
- Plazo instructivo: 2026-06-12.
- Corte referencial: personal contratado durante mayo de 2026.
- Evitar duplicidades de academicos.
- Validar estructura exacta segun CSV oficiales.
- Validar formato de fechas declarado como `DD-MM-AAAA`.
- Validar DV de RUT chileno cuando `TIPO_DOCUMENTO` sea `R`.
- Validar horas numericas segun campos de horas oficiales.

## 7. Validaciones Tecnicas Preventivas Implementadas

- Normalizacion basica de texto: espacios, mayusculas y tildes, preservando `Ñ`.
- Limpieza de numero de documento sin asumir que todo documento sea RUT.
- Campos obligatorios basicos preventivos: `TIPO_DOCUMENTO`, `NUM_DOCUMENTO`, `DV`, `PRIMER_APELLIDO`, `NOMBRES`, `SEXO`, `FECHA_NACIMIENTO`, `NACIONALIDAD`, `NIVEL_FORMACION_ACADEMICO`, `VIGENCIA`.
- Deteccion de horas negativas.
- Deteccion de valores basicos vacios sin aplicar catalogos no materializados.
- Tolerancia documentada a fechas `AAAA-MM-DD`, marcada como advertencia tecnica.

## 8. Pendientes De Confirmacion

- Delimitador final: estructura observada con `;` versus instructivo que menciona coma.
- Encabezado final: estructuras con encabezado versus instruccion de eliminar encabezado antes de subir.
- `TIPO_ESPECIALIDAD`: tension entre anexos y mensajes de error.
- Catalogo materializado de paises y otros codigos, si se decide convertir tablas del instructivo a catalogos verificables.
- Archivo fuente real institucional de personal academico.
- Mapeo de columnas internas hacia estructuras oficiales.

## 9. Como Ejecutar Validacion

```bash
cd /Users/alexi/Documents/GitHub/avance_curricular

python personal_academico_2026/scripts/validar_archivo_personal_academico_2026.py \
  --tipo en_institucion \
  --input personal_academico_2026/tests/fixtures/en_institucion_valido_minimo.csv

python personal_academico_2026/scripts/validar_archivo_personal_academico_2026.py \
  --tipo fuera_institucion \
  --input personal_academico_2026/tests/fixtures/fuera_institucion_valido_minimo.csv
```

## 10. Como Ejecutar Pruebas

```bash
cd /Users/alexi/Documents/GitHub/avance_curricular
python -m pytest personal_academico_2026/tests/
```

Nota: en el entorno revisado `pytest` no estaba instalado. No se agregaron ni modificaron dependencias globales.

## 11. Estado Final Del Modulo

El modulo queda con validador base funcional, exportador controlado y bloqueado por seguridad, fixtures sinteticos, pruebas preparadas y documentacion de fase. No se genero carga oficial definitiva.

Verificacion ejecutada:

- `python3 -m py_compile` sobre scripts y pruebas: OK.
- Validador sobre fixture en institucion: 1 fila, 34 columnas, 0 errores, auditoria generada.
- Validador sobre fixture fuera institucion: 1 fila, 27 columnas, 0 errores, auditoria generada.
- Exportador bloqueado: OK, no genero archivo PES_READY real.
- Pruebas manuales equivalentes a `pytest`: 10 pruebas OK.
- `python -m pytest personal_academico_2026/tests/`: no ejecutable en este entorno porque `pytest` no esta instalado.

## 12. Proxima Fase Recomendada

- Incorporar archivo fuente real de personal academico institucional.
- Mapear columnas internas a columnas oficiales.
- Construir normalizador de carga.
- Ejecutar auditoria con datos reales.
- Recien despues habilitar exportacion final PES_READY.
