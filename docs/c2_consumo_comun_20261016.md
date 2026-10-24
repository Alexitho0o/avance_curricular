# C2 — Consumo común del diccionario

Especificación previa a la implementación. Ambos módulos consultarán una única
edición B5 mediante una interfaz común, sin copiar registros al módulo integrado.
Se añaden cliente, comandos y pruebas en common/, scripts/ y tests/, conforme al
layout autorizado. H5, H7 y catálogos anuales mantienen sus contratos y archivos.

El descriptor C2 fija por SHA-256 registro B5, motor, manifiesto B5 y entrega C1.
El cliente fija el descriptor y comprueba rutas interiores al repositorio antes
de leer componentes. La consulta no necesita Descargas ni OneDrive. C1 es una
vista de las mismas reglas, no una nueva fuente de equivalencias.

Entrada: modelo explícito K0–K3 y parámetros académicos completos según B5.
Se rechazan campos ajenos, tipos incorrectos, planes duplicados/desordenados y
modelos desconocidos; no se infieren años ni se cambia de modelo para lograr
una coincidencia. Campos ausentes conservan ENTRADA_INCOMPLETA. Lotes mantienen
orden y multiplicidad. Salida conserva estado, candidatos y habilitación falsa,
y añade trazabilidad de la edición y evidencia de la regla. No admite RUT/MRUN.

Validación: paridad completa de las 2.349 claves entre los dos comandos y B5;
comparación con instantánea C1; errores, ausencia de extrapolación, aislamiento
mutable, integridad, rutas, copia portable y reversión. Conservar 137 referencias
protegidas, entrega C1 y controles FCU2026. No ejecutar pipelines reales.

La reversión retira únicamente la nueva interfaz C2 y su referencia en el
registro del proyecto; las consultas H7, B5 anteriores y las entregas quedan
operativas. No reemplazar ni borrar snapshots. Esta fase cierra integración
técnica; no acredita todas las versiones históricas.

## Uso desde ambos módulos

Desde la raíz de avance_curricular:

```sh
python3 scripts/consultar_diccionario_c2.py --lote data/consumo_comun_c2/20261016/ejemplo_consulta.json
```

Desde procesos/caracterizacion:

```sh
python3 scripts/consultar_diccionario_c2.py --lote ../../data/consumo_comun_c2/20261016/ejemplo_consulta.json
```

Ambos comandos ejecutan el mismo cliente y descriptor, sin copias de reglas.
Cada elemento del lote contiene `modelo` y `entrada`. El ejemplo completo está
versionado en la carpeta C2. La API Python es
`common.diccionario_c2.DiccionarioC2().consultar(entrada, modelo)`.
Salida CLI 0 significa consulta ejecutada, incluso pendiente; salida 1 significa
contrato o integridad rechazados. Leer siempre `resultado.estado` y
`habilitada_para_resolver`, que continúa en falso. La consulta SIES por código
conserva su entrada H7 `scripts/consultar_sies_historico.py`; C2 añade evidencia
B5 por contexto UMAS, sin cambiar el significado de la consulta H7.

## Cierre y balance

C2 completado como integración técnica de lectura. Las 2.349 claves produjeron
objetos completos idénticos en ambos comandos y en el motor B5. La instantánea
que alimentó C1 contiene el mismo registro completo. No se volvieron a generar
el Excel ni sus reglas. Se probaron orden y repetición de consultas, aislamiento
de resultados, entrada incompleta, tipos, campos ajenos y año sin regla.

Pasaron 12 pruebas: cuatro de C2, cinco del motor B5 y tres de unificación.
La copia mínima de C2 funcionó con Python aislado desde otra carpeta, sin fuentes
personales externas. Se rechazaron componentes ausentes, modificados y enlaces
que salían del repositorio. La prueba anterior de unificación ejecutó H7 y el
catálogo anual desde una copia sin C2: confirma que retirar esta capa aditiva
no elimina las capacidades anteriores. No se probó ejecución en Windows.

Las 137 referencias protegidas, todos los hashes de entrega C1 y las 51
referencias FCU2026 conservan su integridad. No hubo ejecución de pipelines,
asignación productiva, modificación de archivos originales externos ni publicación
remota. Fuentes y resultados locales gobernados no equivalen a respaldo GitHub.

Balance académico, sin sumar modelos como versiones distintas:

- Cobertura estructural: 141 códigos SIES y 236 planes UMAS, incluidos inactivos.
- B4: 1.986 contextos; 410 con destino observado único sin ambigüedad adicional,
  36 con ambigüedad adicional, 16 con varios destinos, cuatro solo ambiguos y
  1.520 sin relación observada. Evidencia incluida la ambigua para 45 códigos.
- B5 K0: 197 reglas corroboradas en reserva para 42 códigos; 211 sin reserva,
  15 conflictivas y una contradictoria. Corroboración observacional no equivale
  a acreditación formal ni validación independiente de identidad.
- Equivalencias históricas acreditadas nuevas y asignaciones activadas: cero.

La fase C queda cerrada técnicamente (edición y consumo común); el objetivo de
acreditar cada versión histórica conserva pendientes. Oferta 2007–2009, contextos
sin evidencia, conflictos y mallas sin plan observable requieren investigación
específica. No extrapolar relaciones entre años ni seleccionar otro modelo para
forzar coincidencia. La auditoría de reglas de retención, titulación y estados
académicos pertenece a sus procesos y no se declara resuelta por esta integración.

## Reproducción y reversión

Ejecutar `python3 scripts/validar_consumo_c2.py`. El control escribe
`data/consumo_comun_c2/20261016/qa.json` con resultados, hashes de implementación
y descriptor. La consulta ordinaria no escribe archivos.

Para retirar C2 del consumo: dejar de invocar sus dos comandos y retirar solo
la clave `recursos_comunes.diccionario_c2` del registro del proyecto. Conservar
los snapshots y evidencias; H7, el comando B5 anterior, C1 y catálogos anuales
siguen disponibles. Ningún pipeline fue redirigido a resultados observacionales.
Una edición futura requiere descriptor y cliente con huella nueva, preservando
la edición anterior; no actualizar hashes para silenciar una alteración.
