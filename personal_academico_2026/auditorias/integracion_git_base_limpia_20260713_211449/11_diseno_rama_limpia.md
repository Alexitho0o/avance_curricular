# Diseno de rama limpia

Rama propuesta: `feature/personal-academico-kpi-rotacion-v1`

Comando futuro, no ejecutado:

```bash
git switch -c feature/personal-academico-kpi-rotacion-v1 6e15e063b85ee4b8b8d8937db5dc050a1833253b
```

## Validacion previa

- AUTORIZACION_USUARIO_REQUERIDA para fetch futuro.
- Confirmar que `6e15e063b85ee4b8b8d8937db5dc050a1833253b` sigue siendo la base deseada.
- Confirmar working tree limpio.
- Confirmar que no hay operaciones Git incompletas.

## Validacion posterior

- `git rev-parse HEAD` debe devolver `6e15e063b85ee4b8b8d8937db5dc050a1833253b` inmediatamente tras crear la rama.
- `git status --short` debe estar limpio.
- No deben existir rutas de otros subproyectos en los commits futuros.

## Rollback

Cerrar o borrar la rama limpia solo con autorizacion expresa posterior. No usar reset destructivo.
