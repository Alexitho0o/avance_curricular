# AUDITORÍA MU2026 · PUNTO 0 Y COMPLEMENTO 95 CODCLI

> **Fecha de creación**: 2026-05-09T00:34:54
> **Estado**: AUDITORIA_COMPLETA_VERIFICADA
> **Carpeta**: `control/auditoria_mu2026_punto0_complemento95`
> ⚠ **NO BORRAR ESTA CARPETA. Es el respaldo digital auditable principal de MU2026.**

---

## 1. Objetivo

Crear un Punto de Control Digital Auditable dentro del repositorio que:
- Resguarde la carga principal MU2026 (4.070 filas × 32 cols).
- Resguarde el complemento 95 CODCLI (95 filas × 32 cols, VIG=1).
- Sea auditable, legible, versionable y comparable mediante Git.
- No dependa de un archivo ZIP como respaldo principal.

---

## 2. Alcance

Este punto de control cubre:
- **Carga principal MU2026** (`matricula_unificada_2026_pregrado_PARA_SUBIR.csv` y `PES_READY.csv`)
- **Complemento 95 CODCLI** (proceso paralelo e independiente)
- **Scripts** que generaron los archivos
- **Punto 0** previo de la carga principal
- **Auditorías previas** relacionadas

No modifica ningún archivo original. No ejecuta el pipeline. No regenera datos.

---

## 3. Qué es el Punto 0

El **Punto 0** es el estado congelado de la carga principal MU2026 al momento de su envío:
- 4.070 filas
- 32 campos (sin encabezado, delimitador `;`)
- SHA256 del desktop: `8ac3d58613d000534bf4053a5b9e42d13eee5db488f00d62d3f6d035c4df2704`
- SHA256 del PES_READY repo: `8ac3d58613d000534bf4053a5b9e42d13eee5db488f00d62d3f6d035c4df2704`
- Ambos archivos son idénticos (hashes coinciden): **True**
- **No incluye** el complemento 95 (proceso separado)

---

## 4. Qué es el Complemento 95

El **Complemento 95** es un proceso paralelo e independiente que agrega 95 CODCLI:
- 95 filas
- 32 campos (sin encabezado, delimitador `;`)
- `VIG = 1` para los 95 registros
- 0 celdas vacías
- SHA256 del desktop: `9a6bc998c19282da421d6e9aa51606d94d886a87bcf958f74efb40109be62c6d`
- SHA256 del repo CSV: `9a6bc998c19282da421d6e9aa51606d94d886a87bcf958f74efb40109be62c6d`
- Archivos idénticos (hashes coinciden): **True**
- **No modifica** la carga principal

---

## 5. Rutas originales

| Archivo | Ruta |
|---------|------|
| Desktop (carga principal) | `/Users/alexi/Desktop/matricula_unificada_2026_pregrado_PARA_SUBIR.csv` |
| PES_READY (repo) | `resultados/matricula_unificada_2026_pregrado_PES_READY.csv` |
| Matrícula completa (repo) | `resultados/matricula_unificada_2026_pregrado.csv` |
| Desktop (complemento 95) | `/Users/alexi/Desktop/matricula_unificada_2026_COMPLEMENTO_95_CODCLI_PARA_SUBIR.csv` |
| Complemento 95 dir (repo) | `resultados/complemento_95_codcli/` |
| Punto 0 (repo) | `control/punto_0_carga_principal_mu2026/` |
| Script complemento 95 | `scripts/mu2026_complemento_95_codcli.py` |
| Script respaldo | `scripts/respaldo_mu2026_punto0_complemento95.py` |

---

## 6. Rutas congeladas (dentro de esta auditoría)

```
control/auditoria_mu2026_punto0_complemento95/
├── archivos_congelados/
│   ├── carga_principal/       ← copias de carga principal
│   ├── complemento_95/        ← copias del complemento 95
│   ├── scripts/               ← copias de scripts
│   └── auditorias_previas/    ← auditorías opcionales copiadas
└── evidencia/
    ├── punto_0/               ← copia completa de control/punto_0_carga_principal_mu2026/
    └── complemento_95/        ← copia completa de resultados/complemento_95_codcli/
```

---

## 7. Validaciones realizadas

| Validación | Resultado |
|------------|-----------|
| Carga principal 4070×32 | VALIDADO |
| Complemento 95 × 32 | VALIDADO |
| Hashes originales == copias | 19/19 coinciden |
| Originales intactos post-copia | SÍ |
| Complemento VIG = 1 (todos) | SÍ |
| Complemento celdas vacías | 0 |

---

## 8. Hashes principales

| Archivo | SHA256 |
|---------|--------|
| Desktop PARA_SUBIR | `8ac3d58613d000534bf4053a5b9e42d13eee5db488f00d62d3f6d035c4df2704` |
| PES_READY (repo) | `8ac3d58613d000534bf4053a5b9e42d13eee5db488f00d62d3f6d035c4df2704` |
| Complemento 95 Desktop | `9a6bc998c19282da421d6e9aa51606d94d886a87bcf958f74efb40109be62c6d` |
| Complemento 95 Repo CSV | `9a6bc998c19282da421d6e9aa51606d94d886a87bcf958f74efb40109be62c6d` |

---

## 9. Estado final

```
Estado                : AUDITORIA_COMPLETA_VERIFICADA
Archivos auditados    : 19
Hashes coincidentes   : 19/19
Carga principal       : VALIDADO (4070×32)
Complemento 95        : VALIDADO (95×32, VIG=1, vacias=0)
Originales modificados: NO
```

---

## 10. Cómo comparar en el futuro

```bash
# Comparar hash de un archivo actual vs el congelado:
shasum -a 256 resultados/matricula_unificada_2026_pregrado_PES_READY.csv
# Comparar con SHA256 registrado en HASHES_ORIGINALES.tsv o MANIFEST_AUDITORIA_MU2026.json

# Comparar con Git (si se creó el tag):
git diff --stat mu2026-punto0-complemento95-20260509..HEAD
```

---

## 11. Cómo restaurar

Ver instrucciones completas en `RESTAURACION.md`.

Resumen rápido:
```bash
# Restaurar PES_READY desde copia congelada:
cp "control/auditoria_mu2026_punto0_complemento95/archivos_congelados/carga_principal/matricula_unificada_2026_pregrado_PES_READY.csv" \
   "resultados/matricula_unificada_2026_pregrado_PES_READY.csv"
```

---

## 12. Comandos Git sugeridos

Ver `COMANDOS_GIT_SUGERIDOS.md` para los comandos completos.

```bash
git add control/auditoria_mu2026_punto0_complemento95
git commit -m "audit: freeze MU2026 punto 0 and complemento 95"
git tag mu2026-punto0-complemento95-20260509
```
> ⚠ **NO ejecutar sin autorización explícita.**

---

## 13. Advertencias

1. **NO BORRAR** esta carpeta. Es el respaldo digital auditable principal.
2. No depende de ZIP. El ZIP en el Escritorio es un respaldo auxiliar externo.
3. Los archivos en `archivos_congelados/` son copias verificadas. No modificar.
4. Si se necesita restaurar, usar `RESTAURACION.md` y verificar hashes.
5. Para versionar, usar los comandos de `COMANDOS_GIT_SUGERIDOS.md` con autorización explícita.
6. Este archivo fue generado automáticamente el 2026-05-09T00:34:54.
