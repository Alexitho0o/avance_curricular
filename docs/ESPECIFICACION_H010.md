# H010 · candidata por primer T1 informado

D · Alexi, 30-10-2026. Seguimiento interno 2019–2026, SIES 162. Base Git 6505cae.
No es una regla oficial de reporte ni acredita aceptación SIES. Se conserva v20 activo.

Se reutilizan R01–R27, auditoría v7, enlaces de contexto v20 y catálogo anual.
Universos separados: pendientes históricos v7 (3.049), posiciones V24 (99) y
contextos actuales v20. No sumarlos. Períodos nativos 2/3, sin homologar 4/5.

Un ancla exige contexto nativo 1 con código documental atribuido en v20 y línea
MU de esa persona/año/código, o enlace anual MU–expediente–plan ya gobernado
en H002g con respaldo ANUAL. Este último no exige actividad en el período 1;
no prueba fecha efectiva de un cambio de plan dentro del año. Identidad, expediente y plan deben ser exactos;
la jornada/sede del contexto de destino debe coincidir con la del ancla elegida.
No convierte códigos internos D en evidencia T1 ni usa MRUN. El primer T1
posterior se busca por expediente y plan; un cambio de dimensión queda visible.
La ausencia de ancla es E, no prueba de que nunca se informó. El nivel 5 sólo
puede describir ausencia en el universo documental disponible, no inexistencia
histórica en SIES. El cierre futuro está censurado en 2026.

Nivel 3 requiere tipo y duración compatibles con el perfil v2 y oferta del año
del T1 fuente. Ausencia o contradicción bloquea la asignación. No se retrotrae
la tabla H002 2026/2027 para acreditar vigencia de un plan en años anteriores.
Los candidatos anuales se contrastan con oferta del propio año; sin respaldo
único quedan E. MU2027 usa el consumidor activo, en simulación separada, nunca
crea una fila MU ni acredita continuidad futura.

La base candidata conserva columnas y códigos v20, y agrega campos H010
separados: nivel, código candidato, año fuente, desfase, regla, evidencia y clase.
No es consumible como activo hasta aprobación, integración y QA de consumidores.
No abre Excel, no altera libros ni indicadores. Los controles de tasas reutilizan
resultados congelados y verifican hashes; 0,00 pp significa ausencia de cambios,
no recálculo de H001/R19 ni validación de hipotéticos desgloses nuevos.

Parada: una clasificación por contexto y causa exacta para cada E; meta residual
0,1 % no permite forzar asignaciones. Documentar límites sin otra iteración.

## H010b · extensión autorizada, 30-10-2026

D1: T1 sin línea y actividad sin MU anual → primer T1 posterior del mismo expediente/plan; sin T1 localizado, código vigente anual compatible. D2: ingreso 2026 sin MU → código VIGENCIA 1 compatible del año 2026; nunca cohorte 2027. D3: cambios de carrera/plan/sede/jornada → tipo/duración y, sólo si hay empate, vigencia; ambigüedad E. No recalcular asignaciones previas.

Períodos 4/5: investigar régimen, coexistencia, fechas y documentación; no asignar. Parada: cada residual tiene motivo y requisito; no abrir otra iteración para forzar cobertura.

Reproducción sin abrir Excel:

```sh
python resolver_h010b.py --repo "$REPO_IPSS" --privado "$PRIVADO_H010"
python investigar_periodos_h010b.py --repo "$REPO_IPSS" --privado "$PRIVADO_H010"
python documentar_h010b.py --repo "$REPO_IPSS" --privado "$PRIVADO_H010" --commit-reglas "$COMMIT_REGLAS"
python qa_h010b.py --repo "$REPO_IPSS" --privado "$PRIVADO_H010"
```

Los scripts están en outputs/regla_t1_h010_20261030/. QA conserva fuentes, indicadores y 25 cambios ajenos. Publicar sólo LISTA_PUBLICACION.json si QA y privacidad pasan. v20 sigue activo; v21 candidata.
