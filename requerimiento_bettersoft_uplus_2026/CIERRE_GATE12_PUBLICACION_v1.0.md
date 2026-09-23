# Cierre Gate 12: publicación Bettersoft v1.0

```text
GATE=12
VERSION=1.0
ESTRATEGIA_PUBLICACION=B_RAMA_LIMPIA (cherry-pick sobre el head remoto 0342327)
RAMA_PUBLICADA=feature/bettersoft-uplus-sies-v1
COMMIT_LOCAL_ORIGINAL=83a55076937dbc23af23a15cdfc4c0c95c12133a
COMMIT_PUBLICADO=3e47c66e88cb0aefa466437926a791de2ce452f9
REMOTE_HEAD=3e47c66e88cb0aefa466437926a791de2ce452f9 (antes de este commit documental)

COMMIT_4C247E7_CLASIFICACION=NO_PUBLICABLE_MEZCLA
PII_COMMIT_4C247E7=POSIBLE

HASH_WORD=36bc40c5327d57df32fec8f10f4dc42b219a21b3b65480c82470a66a0ad09cc3
HASH_XLSX=7f394a121b6cb1a46d14db5f9be9849e578bfc138b9c289392520735713f5689

PII_EN_REMOTO=NO

ENTREGABLE_BETTERSOFT=
REQUERIMIENTO_BETTERSOFT_REPORTE_REGULATORIO_UPLUS_v1.0.docx

ENTREGABLE_INTERNO=
DICCIONARIO_MAESTRO_UPLUS_SIES_2026_v1.0.xlsx

ESTADO=PUBLICADO_LISTO_PARA_ENTREGA
```

## Fundamento de la estrategia

- El head remoto de `feature/ire-2026` (`0342327`) y la rama local (`4c247e7`) divergen desde `8d9f378`. `4c247e7` es una versión reescrita del mismo commit "chore: guardar cambios locales": tiene la misma fecha de autor y 59 archivos adicionales. Un push de `feature/ire-2026` habría sido rechazado sin force.
- `4c247e7` mezcla varios frentes ajenos al requerimiento: salidas de la base de retención MU 2022-2026, scripts, validaciones y respaldos de cargas PES de Oferta 2027, y symlinks `node_modules` con rutas absolutas locales. Sin RUT ni fechas de nacimiento; contiene una dirección de correo institucional @ipss.cl repetida (PII posible). No se publicó.
- `83a5507` no depende de `4c247e7`: solo agrega el subproyecto y modifica `.gitignore`, que `4c247e7` no toca. El cherry-pick produjo contenido idéntico (0 diferencias en el subproyecto y en `.gitignore`).
- `feature/ire-2026` no se reescribió ni se publicó; su situación (`4c247e7` frente a `0342327`) queda para una decisión aparte.
- La verificación en GitHub coincide: los SHA-256 del Word y del Excel descargados desde la rama publicada son iguales a los congelados. No hay `.local_restricted/`, snapshots v0.9 ni v0.9.1, auditoría XLSX, precargas, cargas PES ni CSV.
- No se hizo merge a `main` ni se creó un PR.
