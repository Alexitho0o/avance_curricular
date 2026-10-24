# Reglas del archivo de instrumentos

- Las fuentes XML y cada carpeta de version son snapshots inmutables. No editar,
  renombrar ni reemplazar su contenido para resolver comparaciones posteriores.
- Usar REGISTRO.json para localizar el ano/periodo real. 2026 P1 sigue pendiente
  hasta recibir fuentes propias. No reconstruirlo a partir de otros periodos.
- Nuevas versiones se generan con scripts/exportar_instrumento_limesurvey.py y
  --registrar; no sobrescribir una entrega anterior. Registrar fuentes y hashes.
- No alojar aqui respuestas, tokens, listas de participantes ni datos personales.
- La comparabilidad exige revisar textos, codigos, tipos y opciones; conservar
  respuestas historicas originales y crear cruces en un proceso independiente.
- No alterar los procesos cerrados en gobernanza/FCU/2026.
