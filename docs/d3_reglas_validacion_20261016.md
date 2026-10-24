# D3 — Reglas de uso, abstención y validación

Especificación previa. H7 fija condiciones deterministas por contexto B4 y clave
B5; H8 contrasta cobertura y límites; H9 verifica reproducibilidad y consumo común.
La implementación aislada en common/, scripts/ y tests/ conserva C2, los motores
congelados y la edición C1. No se requieren nuevos microdatos para aplicar los
hallazgos D2 ya documentados. No se atribuye validación independiente a la reserva
B5 ni al extracto adicional D2, que no aporta etiquetas SIES nuevas.

## Contrato previsto

- El año observado es obligatorio; no se extrapola ni se convierte primera
  observación/ANOINGRESO en ingreso efectivo. Plan ausente es explícito.
- La vigencia se consulta en la oferta exacta del año. Solo antiguos permite
  coexistencia, no prueba por sí mismo contradicción. La discrepancia de admisión
  debe provenir de un contraste documentado de ingreso, como D2, sin atribuirlo
  a todos los estudiantes de un contexto ni a una identidad inferida MRUN.
- Tipo y duración distinguen perfiles. Se comparan con el perfil de referencia
  ya gobernado, cuya vigencia histórica no se presume. Se conservan todos los
  candidatos originales; una compatibilidad descriptiva no acredita equivalencia.
- Precedencia del dictamen de contexto: conflicto; evidencia ambigua; ausencia
  de evidencia; corroboración K0 sin conflicto; observación K0 sin reserva;
  evidencia sin regla K0. Todos conservan motivos y alcance programa/malla.
- K0 es la base descriptiva fijada en B5, no un modelo seleccionado para cargas.
  K1–K3 preservan sus resultados. Datos posteriores, conflictos y contradicciones
  de cada variante tienen su propia abstención; no se cambia de modelo para
  superar un impedimento del contexto.
- No hay nuevo documento de vigencia curricular por episodio que permita
  acreditar malla. Por ello codigo_asignado=null y habilitación productiva=false
  en esta edición. Uso analítico corroborado significa describir evidencia en
  ese contexto; no asignar código a una persona ni convertirlo en verdad formal.

El paquete contendrá los 1.986 contextos, 141 códigos y 236 planes completos;
referencias y nombres/sectores de C1, con modalidad separada; estados de B5 y
D2; reglas identificadas y fuentes. Los dos módulos consumen una misma edición
fijada por hash, con rechazo de rutas externas, componentes alterados y entradas
ajenas al contrato. La interfaz nueva es reversible sin editar C2.

Validación prevista: igualdad de las 2.349 consultas B5 originales y paridad de
los 1.986 dictámenes entre comandos; comprobación de 141 códigos/236 planes;
casos de límites anuales, perfiles CILOG/ILOG, conflictos, dato posterior, plan
no observado, integridad, mutabilidad y portabilidad. El cierre informa métricas
por denominador, diferencias frente a B5/C1/C2 y ausencia de contraste nuevo.

## H7 — Resultado gobernado

Se construyó una edición D3 separada, con nueve reglas internas identificadas.
Cada contexto conserva sus códigos observados, candidaturas H5 (ámbito 2026),
planes, oferta anual literal y comparación de perfil, más las causas de abstención.
Las candidaturas incompatibles con el perfil de referencia no se borran: se
señala la diferencia, sin afirmar que ese perfil actual rigiera en todo el pasado.

| Dictamen de contexto | Cantidad | Uso permitido |
|---|---:|---|
| Uso analítico corroborado | 169 | Describir la relación observada en la clave exacta, con sus límites |
| Observación sin contraste | 204 | Presentar la evidencia y la falta de reserva |
| Evidencia sin regla K0 | 37 | Investigar el vínculo observado, sin selección automática |
| Abstención por conflicto | 16 | Mostrar destinos y discrepancias, sin elegir uno |
| Abstención por ambigüedad | 40 | Mostrar atribución no unívoca y evidencia restante |
| Sin evidencia atribuible | 1.520 | Mostrar candidatos y brechas; ausencia no prueba inexistencia |
| **Total** | **1.986** | Todos los contextos conservados |

El conjunto de 169 involucra 41 códigos observados y 49 planes distintos. Estos
son universos separados; no sumar coberturas por estado, pues un código/plan puede
aparecer en más de un estado. Hay 916 contextos sin plan observado y 1.070 con
plan(es) observado(s) cuya vigencia curricular no está acreditada.

Las 197 reglas K0 corroboradas permanecen exactamente iguales a B5: 169 pertenecen
a contextos sin ambigüedad adicional y 28 a contextos que también contienen
atribución ambigua. D3 añade una condición de alcance del contexto, no cambia
retroactivamente el resultado de reserva. Los 16 conflictos D2 siguen pendientes;
las cinco discrepancias de admisión se señalan solo en los subconjuntos documentados.

Todos los dictámenes mantienen `codigo_asignado=null` y
`habilitada_para_resolver=false`. Falta sustento de episodio y/o vigencia de malla;
ninguna condición permite elegir la primera versión, la más frecuente o la mayor.
Las referencias por código y plan reciben `DICTAMEN_D3_CON_BRECHAS`, conservando
su estado D1 como antecedente, sin dejarlos como pendientes de una fase ya ejecutada.

## H8 — Qué quedó validado y qué no

La clasificación se aplica a todos los contextos, no a una nueva muestra elegida
por su resultado. La evidencia de D2 no aportó nuevas etiquetas independientes
para validar una asignación curricular. Se conserva por tanto la evaluación K0
B5 como referencia: 560 consultas de reserva coincidentes, una contradictoria,
17 con clave conflictiva y 42 sin regla (620 consultas, no personas distintas).
No se recalculan como rendimiento D3 ni se usa de nuevo esa reserva para seleccionar
un modelo y afirmar validación independiente.

K1–K3 conservan sus salidas C2 completas. Un dato posterior recibe
`ABSTENCION_DATO_POSTERIOR`; un conflicto de variante recibe su propio control.
Una variante corroborada no puede eliminar la ambigüedad o conflicto del contexto.

Se verificaron los casos de D2:

- CILOG 2024: el perfil regular V1 no sustituye a continuidad por ser el código
  disponible ese año. La compatibilidad con el perfil de referencia es falsa.
- CILOG 2026: V2 tiene perfil compatible y declara solo antiguos. Eso no permite
  atribuir individualmente los 21 registros MRUN con ingreso 2026 a estudiantes
  UMAS; la incidencia agregada acompaña la consulta con su límite explícito.
- Contextos con dato actual UMAS posterior: no se interpreta como condición que
  estuviera disponible en el año observado.
- SIES sin oferta en un año: se conserva la ausencia; no se prolonga hacia atrás
  una oferta posterior. La primera observación en carrera tampoco se transforma
  en fecha de ingreso efectivo.

## H9 — Consumo común y reproducción

Los dos módulos usan una sola implementación y un descriptor D3 con hash fijado.
El paquete de consulta incluye resultados académicos, reglas y manifiesto; puede
consultarse en otra ubicación sin abrir Descargas ni OneDrive. Esto no equivale
a portabilidad de toda la reconstrucción analítica de B4/D2, que usa fuentes
personales externas. No se ejecutaron pipelines reales ni se publicó el paquete.

Desde avance_curricular:

```sh
python3 scripts/consultar_dictamen_d3.py --lote data/validacion_d3/20261016/ejemplo_lote.json
```

Desde procesos/caracterizacion:

```sh
python3 scripts/consultar_dictamen_d3.py --lote ../../data/validacion_d3/20261016/ejemplo_lote.json
```

El lote admite `{modelo, entrada}` del contrato B5, o `{tipo, id}` con tipos
CONTEXTO, CODIGO_SIES y PLAN_UMAS. No acepta registros personales. La respuesta
académica preserva C2 íntegro y añade dictamen/controles D3; el estado de ejecución
0 no significa equivalencia acreditada. Las consultas por código conservan nombres
literales de oferta 2026, jornada y modalidad separadas, y sectores editados de C1.
Si no existe nombre 2026, no se rellena silenciosamente con el histórico.

Reproducción y controles:

```sh
python3 scripts/construir_dictamen_d3.py
python3 scripts/validar_dictamen_d3.py
```

La revisión D3 es aditiva: para revertir su uso basta volver al comando C2.
Los archivos C2, su descriptor y resultados permanecen intactos; no hubo cambio
de las rutas o configuración de los pipelines operativos. C1 no se regeneró.

## Entregables y transición

- [Reglas internas](../data/validacion_d3/20261016/reglas.json).
- [Dictámenes completos](../data/validacion_d3/20261016/dictamenes.json).
- [Cobertura y límites](../data/validacion_d3/20261016/resumen.json).
- [Pruebas y preservación](../data/validacion_d3/20261016/qa.json).

D3 cierra el registro determinista y su verificación técnica, con validación
independiente nueva no disponible y cero asignaciones productivas. D4 debe emitir
las conclusiones por hipótesis, consolidar la entrega final y separar las acciones
que pueden realizarse con esta evidencia de las que requieren una fuente adicional.

Cierre verificado: siete pruebas aprobadas, paridad de 4.712 consultas completas
(2.349 B5, 1.986 contextos, 141 códigos, 236 planes), cinco archivos reproducidos
idénticos, 137 referencias protegidas y 51 archivos FCU2026 intactos. Los nombres
y sectores de los 141 códigos se compararon contra la copia Excel original C1.
No se comprobó ejecución en Windows ni se reestimó precisión independiente.
