# COMANDOS GIT SUGERIDOS · MU2026 PUNTO 0 Y COMPLEMENTO 95

> **Fecha de generación**: 2026-05-09T00:34:54
> ⚠ **NO EJECUTAR ESTOS COMANDOS SIN AUTORIZACIÓN EXPLÍCITA DEL USUARIO.**
> Son solo una referencia documentada para cuando se decida versionar este punto de control.

---

## 1. Ver estado actual del repositorio

```bash
git -C /Users/alexi/Documents/GitHub/avance_curricular status --short
```

---

## 2. Agregar archivos al índice

```bash
cd /Users/alexi/Documents/GitHub/avance_curricular

git add control/auditoria_mu2026_punto0_complemento95 \
        scripts/mu2026_complemento_95_codcli.py \
        scripts/respaldo_mu2026_punto0_complemento95.py
```

---

## 3. Crear commit de auditoría

```bash
git commit -m "audit: freeze MU2026 punto 0 and complemento 95

- Carga principal: 4070 filas × 32 cols, SHA256=8ac3d58613d00053...
- Complemento 95 CODCLI: 95 filas × 32 cols, VIG=1, 0 vacías
- SHA256 complemento 95: 9a6bc998c19282da...
- Punto de control digital auditable creado en control/auditoria_mu2026_punto0_complemento95/
- No se modificaron originales."
```

---

## 4. Crear tag de auditoría

```bash
git tag -a mu2026-punto0-complemento95-20260509 \
        -m "MU2026 Punto 0 + Complemento 95 CODCLI verificados. Carga: 4070x32. Complemento: 95x32 VIG=1."
```

---

## 5. Verificar tag

```bash
git show --stat mu2026-punto0-complemento95-20260509
```

---

## 6. Comparar cambios posteriores al tag

```bash
git diff --stat mu2026-punto0-complemento95-20260509..HEAD
```

---

## 7. Ver archivos en el tag

```bash
git ls-tree -r --name-only mu2026-punto0-complemento95-20260509 | grep control/auditoria
```

---

## 8. Restaurar un archivo desde el tag (si se necesita)

```bash
git checkout mu2026-punto0-complemento95-20260509 -- \
    control/auditoria_mu2026_punto0_complemento95/archivos_congelados/carga_principal/matricula_unificada_2026_pregrado_PES_READY.csv
```

---

## Notas

- El tag `mu2026-punto0-complemento95-20260509` actúa como snapshot inmutable del estado del repositorio.
- Si se ejecuta `git push`, incluir `--tags` para subir el tag al remoto.
- Este archivo fue generado automáticamente por `scripts/auditoria_mu2026_punto0_complemento95.py`
