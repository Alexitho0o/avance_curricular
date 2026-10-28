# Retención de 1er año · corrección de procedencia

Este informe se corrige el 28-10-2026. La matriz `Retencion_ipss_2022_2024_GRANULAR.xlsx` es un cálculo interno previo (C): su manifiesto acredita autoría institucional y no la identifica como publicación SIES. Las comparaciones anteriores con 338/531/715 son consistencia con ese cálculo, no validación externa. Detalle por código y limitaciones: `outputs/retencion_discriminacion_codigo_20261028/INFORME.md`.

Corrección del correo SIES para la cohorte 2025: la fila `Total general` registra 677 retenidos, 486 no retenidos, 1.163 casos y 92 no considerar. El conteo 2.326/1.354/184 era un error de doble suma: se sumaron los códigos y luego se añadió nuevamente su total. `no_considerar` no integra los 1.163 casos. El archivo tiene 36 filas de códigos más la fila de total; no son 37 códigos. La metodología y el universo definitivo aún deben verificarse (E).

La referencia externa por cohorte 2022–2025 se documenta en `outputs/retencion_validacion_oficial_20261028/INFORME.md`, mediante los libros SIES 2025/2026 y el correo SIES 2025. Los libros publicados muestran tasas institucionales, pero no numeradores ni denominadores para IPSS en la hoja por institución; no se infieren cantidades desde ellas.

El algoritmo permanece en `BORRADOR_NO_ACTIVO`. La condición de continuidad oficial requiere misma institución y cohorte de origen; el prototipo solo comprueba presencia y debe corregirse y validar universo, VIG y exclusiones antes de reproducir SIES (E). La cohorte 2025 se bloquea en el código por defecto y no se calcula en esta auditoría.
