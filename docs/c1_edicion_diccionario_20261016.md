# C1 — Nueva edición del diccionario

Especificación previa. Edición separada dentro del proyecto, sin sobrescribir el
Excel del usuario ni activar reglas en motores. Importar el libro H8 actualmente
editado, preservar sus nueve hojas, datos, fórmulas y sectores por Código Único.
Conservar copia exacta por hash. Añadir consulta B5, registro completo K0–K3,
matriz B4 y cobertura académica. No sustituir cero reglas H5 por reglas observadas.

Consulta B5 exige clave completa según modelo, devuelve estado, candidatos y
soportes; nunca un código acreditado. Datos posteriores y conflictos quedan
visibles. Nombre oficial según oferta, jornada y modalidad siguen separados.
No omitir los 141 códigos, 236 planes, 513 candidatos ni relaciones pendientes.
Añadir guía de edición y referencias a archivos del proyecto. B5 usa instantáneas;
las fórmulas de consulta se recalculan, no reconstruyen el análisis desde alumnos.

Generación con Artifact Tool; verificar todas las celdas originales con fórmula,
sectores por clave, tablas nuevas completas y consultas de estados/fronteras.
Inspección visual de vistas nuevas y dependencias alteradas. Archivo final único
en outputs/diccionario_c1_20261016/, junto a controles gobernados en data/.
No afirmar recálculo nativo Excel si solo se comprobó el motor de autoría.

## Cierre verificado

Entrega: `outputs/diccionario_c1_20261016/DICCIONARIO_CRUCE_SIES_UMAS_2007_2026_C1.xlsx`.
Son 14 hojas: las nueve originales y cinco nuevas. El original del usuario y su
copia exacta permanecen intactos. El libro conserva las 39.721 celdas originales
con sus fórmulas y formatos, tablas, filtros, filas ocultas y paneles inmovilizados.
Se preservaron Sector IPSS 2026 y Estado sector por los 141 códigos, incluida
la evidencia en las celdas originales. En cuatro hojas se reinició únicamente
la posición de desplazamiento de la ventana; está registrada en el control.

Se incorporaron las 2.349 reglas de los cuatro modelos (no son 2.349 versiones
distintas), los 1.986 contextos B4 y coberturas completas de 141 códigos y 236
planes. Se cotejaron 80.701 celdas nuevas con la instantánea de autoría. Pasaron
18 consultas representativas de modelo/estado, dos casos de frontera y los
conteos K0: 197 corroboradas, 211 sin reserva, 15 conflictivas y una contradictoria.
No hay errores de fórmula detectados. Se revisaron visualmente las vistas nuevas
y las áreas modificadas. La prueba usa el motor Artifact Tool; no se comprobó
el recálculo en Excel nativo. Las 137 referencias protegidas mantienen su hash.

La consulta no promueve reglas ni cambia H5. Los estados y códigos candidatos
se presentan explícitamente; las brechas históricas continúan pendientes.

## Reproducción y trazabilidad

- Instantánea de autoría: `data/diccionario_c1/20261016/libro_c1.json`.
- Fuente preservada: `data/diccionario_c1/20261016/fuente_usuario.xlsx`.
- Constructor: `data/diccionario_c1/20261016/autor/generar_c1.mjs`.
- Verificador: `python3 scripts/verificar_diccionario_c1.py`.
- Resultados: `qa_formulas.json`, `qa_xlsx.json` y `entrega.json` en la carpeta C1.
- `entrega.json` registra hashes de fuentes, manifiestos B4/B5, constructor,
  controles y resultado. Reejecutar el verificador requiere que el original del
  usuario conserve el corte registrado; una edición posterior exige nuevo corte.

C2 es el siguiente hito: integrar el recurso versionado en ambos módulos y
comprobar paridad, reproducción y reversión, sin activar hipótesis como certezas.
