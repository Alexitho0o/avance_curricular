# Incidente Git y recuperacion del proyecto CARACTERIZACION - 2026-05-06

## 1. Resumen ejecutivo
El proyecto sufrio un incidente durante una limpieza Git en la que se removieron del indice y de la estructura versionada multiples archivos. Esto genero riesgo de perdida aparente de componentes criticos. Se ejecuto una recuperacion completa de estructura y publicacion en GitHub, manteniendo intacto el archivo principal de procesamiento.

## 2. Causa del incidente
La limpieza intento retirar dependencias locales, caches y archivos residuales, pero impacto tambien contenido versionado del proyecto. Como consecuencia, se produjo una perdida aparente de archivos operativos y de gobernanza, obligando a una restauracion selectiva controlada.

## 3. Archivos criticos protegidos
- caracterizacion.py
- scripts/generar_fcu_pes_final.py

## 4. Validacion de integridad de caracterizacion.py
- Hash SHA256 final: f4308e65af3f7f3ad550e7c213f8a9f265b0a8a7fb02e285a3e572083cf30212
- Lineas: 26382
- Compilacion: OK
- Observacion: el archivo no fue modificado durante la restauracion selectiva ni durante git filter-repo.

## 5. Restauracion de estructura
Se aplico una restauracion selectiva desde respaldo/rama de rescate backup_antes_squash_fcu_2026_p1, excluyendo explicitamente:
- caracterizacion.py
- .git/
- .deps_local/
- .venv/
- .vscode/
- __pycache__/
- *.pyc
- .DS_Store
- *.log

## 6. Limpieza Git aplicada
Se excluyeron del control de versiones:
- .deps_local/
- .vscode/
- __pycache__/
- *.pyc
- .DS_Store
- backups/
- CSV grandes de extraccion SIES

## 7. Problema con GitHub
El push fue rechazado inicialmente porque el archivo:

EXTRACCION_MATRICULA_SIES _2007_2025/Matricula_Ed_Superior_2023_PUBL_MRUN.csv

pesaba aproximadamente 827 MB y excedia el limite de 100 MB de GitHub.

## 8. Solucion aplicada al CSV grande
- Primero se retiro del indice con git rm --cached.
- Luego se detecto que seguia presente en commits anteriores.
- Se aplico git filter-repo para eliminarlo de toda la historia Git.
- El CSV fisico quedo intacto en disco.
- El archivo ya no quedo en la historia Git.

## 9. Respaldos creados
- Bundle Git: ~/Desktop/BUNDLE_CARACTERIZACION_PREFILTER_20260506_001359.bundle
- Respaldo fisico: ~/Desktop/RESPALDO_FISICO_PREFILTER_20260506_001406

## 10. Publicacion final
- Repositorio GitHub: https://github.com/Alexitho0o/CARACTERIZACION
- Rama publicada: main
- HEAD publicado: 5b97e7a
- Push realizado sin --force
- Working tree final limpio

## 11. Reglas preventivas futuras
- Nunca versionar .deps_local/, .venv/, __pycache__/, .DS_Store, .vscode/ ni backups historicos.
- Nunca versionar CSV/XLSX pesados de datos fuente.
- Antes de cualquier limpieza Git, congelar hash y lineas de caracterizacion.py.
- Antes de comandos Git destructivos, crear bundle y respaldo fisico.
- No usar git rm -r --cached . sin plan de restauracion selectiva.
- No aplicar git filter-repo sin bundle previo.
- No tocar caracterizacion.py si el objetivo es solo ordenamiento, limpieza Git o publicacion.

## 12. Checklist de cierre
- [x] caracterizacion.py intacto
- [x] script PES compila
- [x] basura fuera de Git
- [x] CSV grande fuera de historia Git
- [x] repositorio publicado
- [x] respaldo fisico creado
- [x] bundle creado
- [x] working tree limpio
