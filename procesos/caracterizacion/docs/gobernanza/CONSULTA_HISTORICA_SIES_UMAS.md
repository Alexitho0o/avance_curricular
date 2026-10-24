# Consulta histórica SIES–UMAS 2007–2026

Integración H7 autorizada el 2026-10-15. CARACTERIZACIÓN consume una copia
local verificada del maestro H5 y del resolvedor de avance_curricular.
La consulta funciona sin tener instalado el repositorio de origen.

## Alcance

La nueva interfaz es `common/consulta_sies_historica.py`, utilizada por
`scripts/consultar_sies_historico.py`. El descriptor gobernado está en
`gobernanza/sies/historico/ACTIVO_2007_2026.json`; su versión inicial es
`2007_2026_h5_20261015`. Cliente, comando, maestro y resolvedor son idénticos
a los distribuidos en avance_curricular.

El paquete conserva 141 códigos SIES y 236 planes UMAS, con y sin actividad.
La oferta reconstruida cubre 2010–2026; la observación MRUN conserva 2007–2026.
La falta de oferta en 2007–2009 se mantiene explícita. El maestro todavía
contiene cero reglas efectivas acreditadas de plan/período a Código Único.
Por ello, un candidato único o múltiple permanece pendiente de evidencia.

Esta interfaz atiende consultas históricas. No reemplaza el catálogo anual
2027, el cierre FCU2026 ni el enriquecimiento anual integrado 2026. No cambia
elegibilidad, sector, modalidad escolar ni resultados anteriores. No se conecta
a la asignación automática de mallas: faltan las reglas efectivas y la evidencia
individual. El Excel del diccionario corresponde a la fase 8.

## Uso

Desde la raíz del proyecto, en Mac (en Windows, usar `python`):

```bash
python3 scripts/consultar_sies_historico.py --anio 2026 --codigo-unico I162S2C77J4V2
python3 scripts/consultar_sies_historico.py --anio 2026 --codcarpr CILOG --nombre-interno "CONTINUIDAD INGENIERIA LOGISTICA" --plan-umas CILOG20241 --sede-umas RE --jornada-umas O --periodo 1 --regimen TRIMESTRAL
```

El primer comando consulta la oferta anual exacta. El segundo conserva los
candidatos V1 y V2 pendientes. El nombre interno de continuidad es un parámetro
de trazabilidad UMAS; no se añade al nombre oficial de la oferta.

La consulta exige año explícito. UMAS utiliza los ocho parámetros: año,
período, régimen, código interno, nombre interno, plan, sede y jornada.
No se deduce versión desde año de ingreso, nombre de plan o primera aparición
MRUN. Tampoco se convierte la jornada J3 en O/J4.

La API conserva el resultado completo de H5:

```python
from common.consulta_sies_historica import ConsultaHistorica
consulta = ConsultaHistorica()
resultado = consulta.consultar_sies(anio=2026, codigo_unico="I162S2C77J4V2")
trazabilidad = consulta.trazabilidad()
```

`consultar_lote` recibe una lista de objetos con `tipo` (UMAS/SIES) y
`parametros`; conserva orden y repeticiones. El CLI equivalente es
`--lote /ruta/consultas_academicas.json`. No pasar nóminas o columnas personales.
El comando imprime JSON con resultado y hashes; no escribe sobre entregas.

Código de salida 0: oferta localizada o equivalencia acreditada, según el
estado específico. Código 2: al menos una consulta pendiente, incompleta o
fuera del ámbito. Código 1: paquete, lectura o contrato rechazados.
Un error de integridad no se convierte en ausencia de cobertura.

## Conservación y actualización

El cliente fija el hash del descriptor y comprueba los cuatro componentes
del paquete antes de ejecutar código. No consulta Descargas ni rutas del
repositorio de origen. Las rutas de procedencia contenidas en el maestro son
metadatos históricos; no se abren durante la consulta.

No editar el maestro ni el resolvedor distribuido. La misma edición se
reinstala desde `scripts/exportar_consulta_historica.py` en avance_curricular,
con `--destino /ruta/CARACTERIZACION`. Una diferencia existente bloquea la
instalación antes de escribir. Nuevas reglas requieren otra edición gobernada
y evidencia documental, no reemplazar los hashes de esta edición.

Las pruebas y la paridad del universo se conservan en avance_curricular,
`data/versiones_historicas_sies_umas/fase_7_20261015/`. La validación compara
objetos completos de ambos consumidores con H5 y contrasta sus resultados
con H6. No implica que las equivalencias pendientes estén certificadas.
