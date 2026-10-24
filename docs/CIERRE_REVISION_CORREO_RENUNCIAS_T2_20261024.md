# Retención intertrimestral · respaldo de 66 renuncias T2-2026

Fecha de registro: 2026-10-24. Proceso: seguimiento interno IPSS162, ingresos
2026/P2. Acción autorizada: documentar investigación y pendientes de entrega;
no editar bases, denominadores, reglas ni libro V16.

## Correo y adjuntos — B

Lectura directa en Outlook, buzón institucional: «Análisis para Comité de
Rectoría / JD», María Paz Sandoval Sepúlveda, 20-oct-2026, 20:18 (hora mostrada
por Outlook). El cuerpo pide revisar retención intermedia de cohortes 2024 y
2025 con los cierres T2/T3 del año siguiente. Describe los adjuntos como bases
de estudiantes vigentes al cierre. No menciona las 66 renuncias, su criterio,
fecha de extracción ni una nómina específica. Esto es comunicación interna B,
no definición oficial SIES A.

Tiene exactamente cuatro adjuntos, inspeccionados en todas sus hojas:

| Archivo | SHA-256 del adjunto local |
|---|---|
| Matrícula T_2_13_07_2026.xlsx | 7926a9cabcc67ed19abb50459132fd74ebb323bff9f5cb53e9116378c21a6769 |
| Matrícula T2_2025 2.xlsx | ed5de007202df0780bb3396ad88307f4096d7c8b729005486a20d1123096d5b3 |
| Matrícula T3_2025 2.xlsx | 68a1cd54ee48c1e6a679c1dbb3999e12d491543e9425e81f3d0508fefdc8d6cc |
| Matrícula_T3_02_10_2026.xlsx | de4e73ee7d27779cdc531c6816f745d412e1021cbd61e4fceb8ab0459cbda4ae |

Ubicación de los adjuntos leídos: `/Users/alexi/Library/Group Containers/UBF8T346G9.Office/Outlook/Outlook 15 Profiles/Main Profile/Files/S0/2/Attachments/0/`,
archivos locales con sufijos [121028], [121029], [121030] y [121031], respectivamente.
No se exportó el correo ni sus datos individuales al repositorio. La búsqueda
«renuncias» en el buzón mostró este envío y una conversación de 2025; la búsqueda
«13_07_2026» no produjo resultados. No se acredita una búsqueda exhaustiva de
todos los correos ni la inexistencia universal de otro respaldo.

## Contraste y conclusión — B/C/E

El adjunto T2 es idéntico por hash a la fuente ya auditada. Hoja2!C32:C50 contiene
cantidades literales por carrera que suman 66; Hoja1 tiene 528 CODCLI distintos,
527 personas y no incluye estado académico ni una marca individual de renuncia.
Los otros adjuntos no aportaron una nómina atribuible a esas 66 renuncias. El
cruce exacto de los 528 CODCLI con las hojas con encabezado CODCLI de los otros
adjuntos (Hoja1 T2-2025, T3_2025 y T3 de T3-2025, Base y 2026_3 de T3-2026)
dio cero coincidencias. No se interpretó esa ausencia como deserción.

Se conserva la conciliación previa documentada en
`outputs/conciliacion_14_carreras_t2_20261024/INFORME.md` y su evidencia agregada:
462 VIGENTE, 63 ELIMINADO, 1 SUSPENDIDO y 2 CODCLI no localizados en 12159.
Los 63 ELIMINADO son 56 situación 11, tres situación 23 y cuatro situación 24.
La suma complementaria 63+1+2=66 no identifica las 66 renuncias originales.
Hay diferencias de distribución en 14 carreras, aunque se compensen en total.

**E — Estado: 66 renuncias pendientes de respaldo individual.** Hace falta la
nómina o consulta que alimentó Hoja2!C32:C50: CODCLI o identidad verificable,
carrera, estado/situación considerados y fecha de referencia. No sustituirla
por ELIMINADO + SUSPENDIDO + ausentes ni imputar casos para cuadrar totales.
Se preserva 462/528=87,50% por matrículas; no es una tasa de personas verificada.

## Qué puede entregarse y qué no está cerrado

B/C: V16 está disponible para revisión como resultado interno con limitaciones
explícitas. SHA-256 verificado nuevamente:
`aa4309934a0ed34740913bfdf2314e97a1a4cb51cbe36b830266df13df4cb37c`.
Ruta: `outputs/aclaracion_tasas_2026_20261023_v16/RETENCION_IPSS_SEGUIMIENTO_T1_T2_T3_20261023_V16.xlsx`.
El QA persistente registra apertura nativa sin reparación, 54 hojas, 13 gráficos,
35 tablas y preservación de bases y denominadores. Su alcance es la corrección
y conservación declaradas: no certifica de nuevo las 54 hojas completas.

- B/C/D: auxiliares internos PROMEDIOS 2025: T2 611/1.150=53,13%; T3
  546/1.150=47,48%. Foto de matrícula T3: 1.023/1.150=88,96%. Son medidas distintas.
  No se reabre la exigencia de fecha exacta del estado para el auxiliar aceptado.
- B/C/D: 2026, T1 al cierre T3: 1.360/1.467=92,71%; total único T3:
  2.290/2.519=90,91%. Conservan las cuatro exclusiones internas de titulados
  documentadas en V16; no se presentan como regla oficial SIES.
- E: respaldar individualmente las 66 es necesario para cerrar su conciliación
  y decidir una eventual tasa por personas. No bloquea entregar el agregado
  original con su advertencia; sí impide presentarlo como individualmente validado.
- E: las celdas «Sin foto completa» / «Sin foto» de hoja 18 siguen visibles.
  Los auxiliares de actividad no las convierten en fotografías de matrícula.
- E: hoja18!B84 mantiene pendiente la tasa anual comparable de los tres períodos.
  No debe sustituirse por un promedio de porcentajes ni por actividad académica.
- E: hoja52 conserva 104 contextos con código pendiente, incluidos 24 del foco
  multiversión, y 13 correspondencias internas con atribución documental pendiente.
  No se eliminan estudiantes del seguimiento por esa condición ni se declara
  completa la comparabilidad por código SIES. Son cifras del libro, no una
  reevaluación del diccionario en este registro.

## Control y reanudación

D: documentado por solicitud de Alexi; ejecución Codex. Solo se agrega este
registro de cierre en docs/. No se modifican bases, Excel, denominadores,
diccionario ni documentos anteriores. No se envían correos ni se solicitan datos
a terceros. Sin staging, commit ni push. Registro local, no publicación en GitHub.

B: rama feature/ire-2026; HEAD de referencia
80ca13a5a249a1a2bd53a699f5f73689b1f53040.
Reanudar desde la nómina/consulta de las 66 si aparece; reutilizar los cruces
exactos ya auditados. No repetirlos por una coincidencia solamente numérica.
