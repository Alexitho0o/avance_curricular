# Notas académicas al corte

## Regla vigente

En el análisis anual, la ausencia de notas válidas al corte es un estado
informativo: se presenta como **Sin notas disponibles al corte**. No es un error,
no se convierte en cero y no se incorpora al promedio.

Esto aplica especialmente a períodos cuyas clases comenzaron recientemente,
pero la regla es general: solo se incorporan notas finales válidas del año y
períodos definidos en la política anual. Las observaciones fuera de escala,
transferidas, contradictorias o sin claves siguen siendo controles de calidad
separados y no se silencian con esta etiqueta.

## Efecto numérico

`PROMEDIO_AC_REFERENCIA` queda vacío cuando la matrícula no tiene notas válidas.
Las columnas auxiliares mantienen la suma de promedios y el denominador de
matrículas con notas en cero para esa fila. Por tanto:

- el promedio general y los promedios filtrados se calculan solo con notas válidas;
- la cobertura sigue siendo `matrículas con notas / matrículas seleccionadas`;
- las matrículas sin notas no desaparecen del universo ni se cuentan como nota cero;
- si el denominador de notas es cero, la salida muestra la etiqueta definida y no
  un valor numérico.

No se cambia el cierre FCU 2026, sus inventarios, fuentes, resultados ni archivos
históricos. La modificación pertenece únicamente al generador del análisis anual
y a su presentación.
