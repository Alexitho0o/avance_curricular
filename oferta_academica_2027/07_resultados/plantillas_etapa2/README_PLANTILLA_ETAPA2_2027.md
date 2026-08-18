# Plantilla preliminar — Etapa 2 Oferta Académica Nueva 2027

## Estado

- Estado: PRELIMINAR.
- Destino: solicitud y consolidación de antecedentes desde Docencia.
- No constituye el formato oficial SIES de Etapa 2.
- No debe exportarse ni cargarse a SIES sin comparar primero contra el archivo oficial que entregue SIES para Etapa 2 2027.

## Archivo principal

- `PLANTILLA_TRABAJO_ETAPA2_OFERTA_NUEVA_2027_20260817_211914.xlsx`
- SHA-256: `4ac13398d7cfcf6e9c2d0fdb6edfb93786eb6869c0f4b82c6059ba55fb19b11e`

## Estructura del libro

1. `Etapa 2 - Oferta nueva`
   - Hoja de trabajo para Docencia.
   - Contiene 48 campos potenciales de carga y 2 columnas internas:
     - `ESTADO_VALIDACION_INTERNA`
     - `OBSERVACIONES_DOCENCIA`
   - Las dos columnas internas nunca se exportan al CSV SIES.

2. `Diccionario de columnas`
   - Define propósito, tipo de dato, regla base, responsable y observaciones por columna.

3. `Reglas de carga`
   - Resume condiciones de vigencia, valores admisibles, uso de ceros, campos obligatorios y reglas de exportación.

## Reglas operativas

- El CSV final deberá generarse solo una vez que exista el formato oficial de Etapa 2.
- El CSV final deberá respetar el orden, columnas, codificación, delimitador y reglas del formato oficial recibido.
- Para registros con `VIGENCIA_CARRERA = 1`, se deben completar los campos condicionados por el manual, como fecha de admisión, enlace de programa, correo de difusión, antecedentes de admisión y valores.
- Para registros con `VIGENCIA_CARRERA = 2`, la fecha de admisión debe permanecer vacía.
- Los códigos institucionales, códigos de sede, códigos de carrera, versión, nivel, plan y clasificación deben ser validados por DAI/SIES antes de carga.
- Los valores monetarios deben informarse como enteros sin símbolo de moneda ni separadores de miles.

## Fuentes de diseño

- Instructivo Oferta Académica-Acceso 2027.
- Estructura histórica de Etapa 2 2026.
- Reglas de validación observadas durante la carga de Etapa 1 2027.

## Pendiente obligatorio

Cuando SIES entregue la estructura oficial de Etapa 2 2027, se debe:

1. Comparar campos y orden con esta plantilla.
2. Actualizar el diccionario de columnas.
3. Ajustar las reglas de validación.
4. Generar una versión nueva identificada como `FORMATO_OFICIAL_VALIDADO`.
5. Conservar esta plantilla como antecedente de trabajo, sin reemplazarla.
