# Respaldo gobernado en Git · Fase 1/5 (26-10-2026)

Rama `feature/ire-2026`, HEAD de partida `8e2fb85`. Siete commits locales, uno por tema, cada uno
con su lista exacta de archivos (`lista_X.nul`). Sin push salvo autorización.

| Commit | Archivos | Contenido |
|---|---:|---|
| A | 42 | Diccionario v9 activo, decisiones y alertas v1–v9, errata, catálogo de fuentes, PROYECTO_IPSS.json, documentación del diccionario |
| B | 257 | Auditoría y conciliación 24–26 oct: decisión A, candidata y promoción v9, regla T1, procedencia, consolidación, este respaldo |
| C | 104 | Scripts y procesos |
| D | 63 | Datos y reglas de negocio |
| E | 44 | Documentación |
| F | 90 | Oferta académica 2027 |
| G | 822 | Resultados históricos 21–24 oct (opcional: `--sin-historicos`) |

**Controles del script:** rama y HEAD esperados; nada preparado de antes; sin `.lock`; un tema por
commit; si un tema no tiene nada nuevo, se salta.
**Identificadores:** revisión en INVENTARIO_CAMBIOS.json; Excel, CSV y bases privadas no entran.

```
bash ~/Documents/GitHub/avance_curricular/outputs/respaldo_git_20261026/commits.sh --revisar
bash ~/Documents/GitHub/avance_curricular/outputs/respaldo_git_20261026/commits.sh --ejecutar
```
