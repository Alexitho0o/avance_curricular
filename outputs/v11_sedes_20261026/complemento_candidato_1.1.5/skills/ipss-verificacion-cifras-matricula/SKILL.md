---
name: ipss-verificacion-cifras-matricula
description: "Verifica cifras de matrícula y retención de IP San Sebastián antes de citarlas, compararlas o calcular brechas en informes, presentaciones, análisis o indicadores. Distingue registros y estudiantes, total institucional y carreras técnicas/profesionales, cohorte y año de observación, retención y persistencia; coteja SIES/Mineduc y registra evidencia. Resuelve también la plantilla PPTX ejecutiva IPSS. No activar para otras instituciones ni para cambios visuales que no usen cifras."
---

## Estados UMAS: fuente común y precedencia

La [relación explícita UMAS–VIG](references/estados-umas/relacion-vig.md) y su
[tabla de 32 parejas](references/estados-umas/relacion-estados-situaciones.tsv)
indican las condiciones para1/2/0 y el pendiente. Consultarlas para responder
qué relación corresponde, citando evidencia y corte; no limitar la respuesta
a que falta una equivalencia. Son reglas condicionadas C basadas en A/D, sin
asignación automática por etiqueta ni aplicación a los indicadores existentes.

Antes de interpretar `ESTADOACADEMICO`, `SITUACION`, titulado/egresado o vigencia desde DATOSDEALUMNOS, leer la [referencia común gobernada](references/estados-umas/estados-umas.md). Contiene la resolución Gate09 C09-01 confirmada en Gate10 v1.0, las parejas13/EGRESADO y42/TITULADO respaldadas como clasificación interna, y16/ELIMINADO pendiente. Ningún estado U+ asigna automáticamente VIG SIES. Separar descripción B, implementación C, decisión D, definición oficial A y pendiente E; respetar proceso, edición y fecha de corte. Las implementaciones antiguas0/2 no prevalecen sobre el cierre confirmado. Mantener los denominadores aprobados y las fuentes del indicador. Esta referencia es una instantánea compartida, sin sincronización automática con GitHub.

# Verificación de matrícula y retención IPSS

Conserva el nombre histórico para no romper referencias. El alcance incluye matrícula, retención y plantilla IPSS; no redefine indicadores de otros proyectos.

## Entrada, salida y activación

Recibe afirmación/indicador, fuentes y alcance. Activar al citar/verificar matrícula o retención IPSS, comparar cohortes, calcular variaciones/brechas, posiciones o tasas de referencia, o resolver la plantilla ejecutiva IPSS. Si solo se necesita la plantilla, leer esa sección sin auditar cifras.

Entrega una ficha por cifra: institución/código; indicador/definición; total/técnico/profesional; población y grano; numerador/denominador o «no publicados»; cohorte de ingreso; año de observación; filtros/restricciones; valor original/unidad; cálculo/redondeo; archivo/URL, hoja, celda/rango o tabla, fecha de consulta; estado VERIFICADO / DISCREPANTE / NO VERIFICABLE y limitaciones. Entregar esa ficha a DAX, storytelling o presentación sin activar esas tareas por sí sola.

Lee [entorno](../../references/entorno.md). Si el entrypoint es un enlace local, resuelve su carpeta real antes de seguir enlaces.

## Matrícula: conservar el grano real

Nunca reportar filas de U+/Bettersoft, CARACTERIZACIÓN o avance_curricular como «total de estudiantes» o «matrícula total». Una extracción histórica puede repetir personas por año, período o carrera. Identificar llaves/duplicados y distinguir registros, personas únicas, matrícula total y primer año, fijando año/corte antes de contar.

Para matrícula total, primer año o evolución IPSS, cotejar SIES/Mineduc en mifuturo.cl: base histórica o panel oficial, Tipo Institución = Institutos Profesionales, Nombre = IP SAN SEBASTIAN. Comprobar código institucional y edición correspondiente al período; no congelar un año del ejemplo.

Citar «SIES/Mineduc, mifuturo.cl, consultado [fecha]», más archivo/hoja/rango o tabla y filtros. Deduplicar una extracción operativa no sustituye el cotejo. Si los universos difieren, informar ambas definiciones y la discrepancia.

El antecedente del 27-09-2026 confundió 14.204 registros 2013–2026 con estudiantes. Las cifras de matrícula conservadas en la skill original están en [antecedentes históricos](references/antecedentes-matricula.md), no como valores certificados por esta actualización. Revalidar antes de reutilizarlas.

## Retención: procedimiento

1. **Tabla y segmento.** Leer título, encabezados, bloque, notas y filtros. Buscar institución/código en el bloque correcto. Distinguir total institucional, carreras técnicas y profesionales: una fila profesional no representa el total. No confundir tipo de carrera con tipo de institución.
2. **Años.** Registrar año de ingreso de la cohorte y año de observación de continuidad. En primer año revisar la definición y seguimiento al año siguiente; el año de publicación no sustituye ninguno. El rótulo 2025 de una serie por cohortes indica ingreso, no necesariamente año observado.
3. **Definición y población.** Verificar qué cuenta como continuidad en esa edición: institución, cohorte o carrera según corresponda; numerador/denominador, elegibilidad, tipo/duración de programas, modalidad, corte, filtros y restricciones metodológicas. No mezclar definiciones internas con SIES por compartir nombre ni atribuir a SIES una decisión local.
4. **Indicadores distintos.** Retención, persistencia en la institución, persistencia en educación superior y no matrícula no son sinónimos. Comprobar si una tabla usa tasas acumuladas o categorías excluyentes antes de sumar. `100 % − retención` no es automáticamente abandono definitivo de educación superior. «No matrícula» en un año no prueba abandono permanente ni su causa.
5. **Fuente oficial.** Abrir/descargar la publicación SIES/Mineduc correspondiente. Registrar URL, nombre exacto, fecha de consulta, hoja/celda/rango o tabla, valor original y unidad; conservar SHA-256 cuando sea posible. Revalidar encabezados/código, no reutilizar coordenadas históricas a ciegas. Con una copia adjunta sin web, distinguir lectura del archivo de cotejo web pendiente.
6. **Precisión.** Calcular desde valores originales antes de redondear. Tasas 0–1: cambio/brecha en puntos porcentuales = `(A−B)×100`; valores 0–100: `A−B`. Declarar sentido A−B y unidad. Variación relativa = `(A/B−1)×100` solo si corresponde y B≠0; no llamarla puntos porcentuales. Redondear al presentar, nunca antes de restar.
7. **Faltantes.** «n/a», vacío y cero son distintos. No convertir faltantes en cero ni atribuirles causas sin respaldo. Una regla general de supresión no demuestra por sí sola la causa específica de cada celda.
8. **Comparaciones.** Diferenciar selección de instituciones de universo completo. Para posiciones/rankings, registrar integrantes, inclusión/exclusión, empates, ausencias y compatibilidad de indicador/período. Decir «entre las instituciones seleccionadas» cuando corresponda. Una tabla con publicación condicionada no demuestra posición entre todas las instituciones existentes.
9. **Sector.** Usar la tasa sectorial oficial o `Σ numeradores / Σ denominadores` compatibles, sin duplicados y con cobertura declarada. Sin esos insumos no calcular una tasa sectorial. Un promedio simple solicitado debe llamarse promedio de tasas de la selección, nunca tasa del sector.
10. **Causas.** No explicar una caída de retención solo desde una tabla histórica. Separar el hecho descriptivo de hipótesis y de la evidencia adicional necesaria; no atribuir causas pedagógicas, económicas, operativas o de composición sin respaldo.

Si falta definición, población o período compatible, marcar NO VERIFICABLE o DISCREPANTE. Continuar con lo verificable; no rellenar la brecha con supuestos.

## Referencia histórica del 09-10-2026

Ver [cohorte 2025 comprobada](references/retencion-2025-verificada.md): valores originales, ubicación, restricciones y hash. El script [verificar_retencion.py](scripts/verificar_retencion.py) verifica identidad/bloque/columna en una copia local de ese formato, sin escribir el Excel. Priorizar el procedimiento anterior; no tratar filas, tasas ni restricciones como permanentes.

## Plantilla PPTX institucional

Solo para PPT ejecutivo IPSS: una plantilla distinta indicada expresamente por el usuario tiene prioridad. En otro caso usar [presentacion-blanca-ipss.pptx](assets/presentacion-blanca-ipss.pptx), copia idéntica al 09-10-2026 de `/Users/alexi/Desktop/Presentación blanca.pptx`, plantilla definida en el Mac de Alexi. No aplicar esta identidad a otras instituciones.

La ruta Mac es procedencia y alternativa local, no requisito de la web. No preguntar por la ruta si el recurso empaquetado está accesible. Si ambos existen y difieren, identificar la versión vigente con evidencia del usuario; no elegir solo por fecha de modificación. Si ninguno está disponible, solicitar la plantilla sin reconstruirla. No sobrescribir el original.

En presentaciones ejecutivas evitar autorreferencias vacías como «dato real, no supuesto», «no una suposición» o «no es responsabilidad de U+». Exponer dato, alcance y fuente con claridad.

## DatosAlumnos: fechas, columnas e historia de cambios

Para interpretar campos de DatosAlumnos o investigar pendientes acumulados, consultar [el contrato exploratorio compartido](../../references/datos-alumnos/auditoria.md) y [las 67 columnas](../../references/datos-alumnos/contrato_columnas.json). Diferenciar fecha declarada, primera aparicion y cambio observado; no afirmar retrofechado ni creacion tardia sin bitacora. No mezclar universos RAW/Caracterizacion, CODCLI/RUT, MODALIDAD escolar/carrera ni marcas UMAS/VIG SIES. Aplicar las reglas del proceso y corte, no extrapolar recomendaciones antiguas del diccionario. Mantener fuentes y cierre FCU 2026 intactos; datos individuales solo en salidas privadas. La referencia es una instantanea versionada, no sincronizacion automatica.

## Código SIES por expediente, plan y período

Para seguimiento T1/T2/T3 o equivalencia personal UMAS–SIES, consultar primero el [punto de consulta único](../../references/diccionario-sies-seguimiento.md). Leer el puntero del repositorio y usar el consumidor común; no copiar versiones o reconstruir códigos por totales. Sin acceso local declarar la consulta pendiente. Esta instrucción no cambia vigencia, elegibilidad ni denominadores.

## Sedes UMAS–SIES

Para RE, CO y PTG y el componente de sede del código único, consultar [sedes UMAS–SIES](../../references/sedes-umas-sies.md). Equivalencia de sede, familia, versión y atribución individual son capas distintas; no asignar sede por dirección ni prefijo.
