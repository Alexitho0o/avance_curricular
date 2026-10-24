# Módulo Caracterización del repositorio único

Ubicación activa: `avance_curricular/procesos/caracterizacion/`.
La estructura y los comandos propios se conservan. Ejecutarlos desde esta carpeta
o con `python3 scripts/proceso_ipss.py caracterizacion -- <comando> ...` desde la
raíz del repositorio. `--listar` muestra los módulos sin ejecutar procesos.

Los catálogos anual 2026, anual 2027 y el cliente histórico H7 se consumen desde
el repositorio contenedor. No se necesita el repositorio hermano CARACTERIZACIÓN.
Las copias anteriores dentro de este módulo son evidencia de la migración y no
las fuentes activas de esas tres consultas. No se deben actualizar mediante los
antiguos exportadores entre repositorios.

El cierre FCU2026, la política anual y las fuentes históricas conservan sus
versiones. No trasladar una regla a otro año/proceso al unificar carpetas.

El inventario de incorporación está en
`../../data/unificacion_proyectos/20261015/importacion.json`. El repositorio de
origen no fue borrado. Su historia Git permanece allí; no se afirma que se haya
fusionado con la historia del contenedor. Los archivos ignorados, las fuentes
personales externas y los entornos locales no se copiaron. Un puntero LFS sigue
siendo un puntero: requiere recuperar el objeto para procesos que utilicen esa base.

## Consulta de evidencia histórica C2

El comando `scripts/consultar_diccionario_c2.py --lote <archivo.json>` consume
el registro B5 común del contenedor, sin duplicarlo. Contrato y ejemplo en
[Consumo C2](../../docs/c2_consumo_comun_20261016.md). Conserva candidatos y
estados; no asigna códigos a estudiantes ni modifica los procesos anuales.
