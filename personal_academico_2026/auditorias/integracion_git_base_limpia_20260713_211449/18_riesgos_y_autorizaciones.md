# Riesgos y autorizaciones

## Riesgos

- HEAD actual movido respecto de 3B-A.
- Rama actual backup con divergencia `ahead 1, behind 1`.
- Commit local ahead mezcla otros subproyectos.
- La base remota local puede estar desactualizada porque no se ejecuto fetch.
- Cinco archivos publicos CSV/TSV requieren excepcion especifica si se desean versionar.

## Autorizaciones requeridas

- AUTORIZACION_USUARIO_REQUERIDA para fetch futuro.
- AUTORIZACION_USUARIO_REQUERIDA para crear rama limpia.
- AUTORIZACION_USUARIO_REQUERIDA para modificar `.gitignore`.
- AUTORIZACION_USUARIO_REQUERIDA para copiar/restaurar rutas.
- AUTORIZACION_USUARIO_REQUERIDA para staging, commit, push, PR, tag o merge.
