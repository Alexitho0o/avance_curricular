# Hito 2c · Continuación: detenido por umbral

[B/C] 32 reglas del commit 09314ca coinciden en valores con hoja 21 tras quitar un espacio final en una situación. Se implementó prioridad de vigencia por cuerpo y año de ingreso en fotos 2025/2026, conservando alternativas en privado.

[C] En T1-2025 P y R difieren para 37 de 1.150 personas (3,22 %); Q no difiere. En agregado V24 indica «Sin matrícula de ingreso en el corte» y R=1, mientras la implementación construida indica «Sin foto» y R=0. Esto revela una diferencia de manejo de la ausencia, pero no se modifica ni concluye cuál tratamiento debe adoptarse en esta ejecución; detener antes de casos individuales por regla de umbral.

[C/E] El padrón previo produce 1.476 frente a 1.471 en T1-2026; cinco adicionales (0,34 %), causa pendiente. La comparación de P/Q/R coincide en los otros grupos comparados, pero no se compararon todos los campos ni agregados. No se valida la regla ni se activa.

[C] Clasificación agregada: error del código nuevo para el caso sin coincidencia en la foto de 2025. 20!P564 asigna «Sin matrícula de ingreso en el corte» y 20!R564 asigna 1 a esa etiqueta; el prototipo asignó «Sin foto» y 0. La inspección fue por fórmula y recuento agregado, sin investigación individual. Aún no se corrigió debido a la detención por umbral.
