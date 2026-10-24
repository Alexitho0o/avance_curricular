# Publicación saneada V17 — 2026-10-24

- **D:** autorización del usuario para preparar historial publicable sin datos individuales, con respaldo local de originales y cambios pendientes.
- **B:** el historial local previo contiene cargas FCU, matrícula individual y excepciones por identificadores en código. No corresponde publicar esos commits completos.
- **C:** se construye un nuevo commit sobre la entrega ya publicada `fab392d`, conservando solo archivos publicables. No se añade un commit de borrado sobre los commits sensibles, porque sus objetos seguirían siendo accesibles.
- **C:** el manifiesto adjunto registra cada archivo reservado, hash y motivo. Sus originales no se editan ni eliminan; siguen disponibles localmente e ignorados por Git. El respaldo del historial completo está fuera del repositorio y en una referencia exclusivamente local.
- **E:** los binarios, volcados y respaldos no certificados se reservan en local; no se afirma que todos sean sensibles. Podrán publicarse individualmente tras su revisión. El CSV agregado LFS requiere resolver su disponibilidad antes de publicar su puntero.
- **C:** no se modifican reglas, denominadores ni la V17. Los procesos que dependan del código histórico reservado siguen necesitando sus componentes privados; un clon de GitHub por sí solo no reproduce esos procesos. La V17 agregada permanece publicada e idéntica.
- **B:** el alcance del QA es privacidad del nuevo historial, integridad de entrega y preservación local. No equivale a una validación de nuevos resultados académicos ni a una auditoría completa de commits que ya estaban publicados.
