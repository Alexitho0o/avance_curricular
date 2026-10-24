# Fase 1 — Inventario para versiones históricas SIES y UMAS

Fecha de revisión: 2026-10-15. Institución: IP San Sebastián, código SIES 162.
Solicitud: iniciar la primera fase del plan de reconstrucción 2007–2026.

## Alcance y criterio de cierre H1

Inventariar las fuentes que permiten explicar el código único SIES y el plan
UMAS: disponibilidad efectiva, procedencia, hash SHA-256, esquema/localizador,
grano, claves candidatas, cobertura observada y limitaciones. Incluir versiones
sin matrícula observada o sin oferta 2026. La cobertura de un archivo no se
considera cobertura completa del universo institucional sin respaldo adicional.

H1 se cumple cuando cada fuente seleccionada tiene estos atributos o un estado
explícito de no verificado/ausente, y cada brecha tiene evidencia y una acción
para la fase correspondiente. H1 no exige que todas las brechas históricas estén
resueltas; tampoco certifica una equivalencia curricular.

Las lecturas proyectan metadatos, dimensiones académicas y controles agregados.
No se incorporan identificadores de personas a los entregables del inventario.
Los archivos fuente, motores, puentes, catálogos y libros entregados se preservan.
No se ejecuta el pipeline oficial ni se reconstruyen trayectorias en esta fase.

## Distinciones obligatorias

- Código único y VERSION SIES: identidad informada en oferta/matrícula.
- CODCARPR/Codcarr: código interno, sin equivalencia automática con CODIGO_CARRERA.
- CODPESTUD/PLAN_DE_ESTUDIO: identificador de plan UMAS cuando esté acreditado.
- PLAN_ESTUDIOS_SIES: campo propio del proceso de avance; no equivale por nombre
  a VERSION SIES ni a CODPESTUD.
- Año observado, ingreso original, ingreso actual y vigencia del plan son
  dimensiones distintas. El primer año observado no determina la vigencia.
- Jornada y modalidad permanecen separadas. MODALIDAD de DatosAlumnos es escolar.
- Nombre de carrera 2026: literal de la oferta señalada por el usuario para el
  mismo código; nombre histórico y NOMBRE_L UMAS se conservan separadamente.

## Entregables y comprobación prevista

Inventario estructurado JSON, índice TSV, matriz de uniones y registro de brechas
en `data/versiones_historicas_sies_umas/fase_1_20261015/`. Registrar originales,
derivados y evidencias de reglas por separado. Verificar hashes antes/después,
coherencia de los índices, cobertura de años y ausencia de valores personales.
Los conteos de programas/filas de evidencia no se publican como estudiantes.

Se usarán las auditorías previas solo si coinciden los hashes de sus fuentes.
La fecha de verificación no se presenta como fecha de extracción ni corte real.
Los resultados del cierre se detallan a continuación.

## Cierre H1

Inventario completado con brechas explícitas: 70 referencias seleccionadas,
63 con bytes y SHA-256 comprobados y siete rutas declaradas no localizadas.
Incluye fuentes primarias, derivados, documentación y código; no son 70 bases
independientes. Las referencias 2027 solo acreditan separación de consumidores.
La búsqueda fue acotada a los repositorios, worktrees y carpetas institucionales
registrados en el JSON; no demuestra ausencia universal de otras fuentes.

| Fuente principal | Cobertura acreditada | Límite para el cruce histórico |
|---|---|---|
| MRUN institucional | Años observados 2007–2026; 106 códigos | Cuatro filas sin MRUN y dos códigos heredados sin componentes modernos. No aporta RUT/CODCLI. |
| Oferta histórica SIES | 2010–2026; 747 filas institucionales, 139 códigos | Oferta 2007–2009 no localizada; modalidad ausente en 2010. |
| Oferta 2026 del usuario | 124 códigos, coincidentes con histórico 2026 en código, nombre, versión y duraciones comparados | No contiene plan UMAS ni historial anual. |
| DatosAlumnos 11998 | Años de matrícula observados 2013–2027; 67 columnas | Sin plan/version/MRUN; un CODCLI repetido. 2027 queda fuera del análisis. |
| PROMEDIOS 7804 de Descargas | Hoja1: años válidos 2019–2026; 197 planes observados | 4.211 filas tienen NULL literal en claves académicas. Un plan por CODCLI en el corte no prueba vigencia histórica. |
| Listado de planes RE+CO | BBDD Bruta: 223 planes, 127 códigos internos, 11.438 filas | Sin fechas de vigencia ni versión SIES; incluye programas que aún deben delimitarse frente al universo SIES. |

El listado de planes se encontró en OneDrive, `SIES/Enviados/Avance Curricular/2026/`.
Su hash es `fb3a6847dca0745a197867090a9d7d12e8bb7e53e6b421f96826ea0c5657d049`;
difiere del original fechado citado por la auditoría antigua. Se conserva como
fuente distinta: iguales métricas agregadas no acreditan iguales celdas.

La unión de los códigos de fuentes SIES seleccionadas contiene 141 identificadores:
139 modernos y dos heredados. De los 139 de oferta histórica, 35 no aparecen en MRUN.
Estas cifras describen códigos; no son carreras únicas ni estudiantes.

Quedaron ocho uniones descritas y nueve brechas con fase y acción siguientes.
Las centrales son: oferta 2007–2009, historial de asignación/vigencia del plan,
puente individual MRUN–UMAS no acreditado y ausencia de condiciones temporales
en las 15 columnas previstas por el puente operativo 2026. El motor MU2026,
las reglas manuales FCU y el resolvedor anual son mecanismos diferentes.

Las fases 2, 3 y 4 pueden comenzar con las fuentes disponibles y esos límites.
El maestro determinista de equivalencias sigue siendo el objetivo de la fase 5.

## Archivos y validación realizada

- [Inventario completo](../data/versiones_historicas_sies_umas/fase_1_20261015/inventario.json).
- [Índice de fuentes](../data/versiones_historicas_sies_umas/fase_1_20261015/fuentes.tsv).
- [Matriz de uniones](../data/versiones_historicas_sies_umas/fase_1_20261015/uniones.tsv).
- [Brechas y acciones](../data/versiones_historicas_sies_umas/fase_1_20261015/brechas.tsv).
- [Alcance de códigos](../data/versiones_historicas_sies_umas/fase_1_20261015/alcance_codigos.tsv).
- [Verificación](../data/versiones_historicas_sies_umas/fase_1_20261015/verificacion.json).

Se comprobaron huellas de los 63 archivos legibles al consolidar y al cerrar;
las siete ausencias se conservan declaradas. El libro de matrícula mantiene
su hash anterior. El diccionario tiene un hash distinto por partes auxiliares
del ZIP, pero sus siete hojas y estilos son idénticos a la entrega anterior:
cero cambios de valores, fórmulas o cachés. No se atribuye el cambio de metadatos
a una aplicación ni persona. Ninguno de los libros se modificó en esta fase.

Comprobación reproducible de integridad, sin ejecutar cruces:

```bash
python3 scripts/verificar_inventario_versiones.py data/versiones_historicas_sies_umas/fase_1_20261015/inventario.json
```

El verificador comprueba metadatos y bytes; no regenera perfiles ni acredita
equivalencias curriculares. Los perfiles agregados se conservan junto al inventario.

Al cerrar la fase 2 se detectaron cambios posteriores en dos referencias
documentales de Caracterización: `AGENTS.md` y `ANALISIS_ANUAL_INTEGRADO_2026.md`.
Se releyeron y documentan recuperación de la consolidación anual; no cambian el
insumo MRUN ni las reglas usadas en esta reconstrucción. Se conserva H1 como
instantánea, con sus huellas originales, y el [control posterior](../data/versiones_historicas_sies_umas/fase_2_20261015/control_fuentes_al_cierre.json)
registra las nuevas. Ejecutar el verificador H1 contra el estado posterior
señala esas diferencias documentales; no se silencian actualizando su referencia.
