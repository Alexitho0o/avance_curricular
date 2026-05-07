# RESTAURACIÓN · MU2026 PUNTO 0 Y COMPLEMENTO 95 CODCLI

> **Fecha de generación**: 2026-05-09T00:34:54
> **Carpeta de auditoría**: `control/auditoria_mu2026_punto0_complemento95`
> **ADVERTENCIA**: Estos comandos restauran archivos desde las copias congeladas.
> Solo ejecutar si los archivos originales fueron eliminados o modificados.
> Verificar siempre el hash SHA256 antes y después de restaurar.

---

## 1. Restaurar Carga Principal PES_READY al repositorio

```bash
# Desde la raíz del repositorio:
cp "control/auditoria_mu2026_punto0_complemento95/archivos_congelados/carga_principal/matricula_unificada_2026_pregrado_PES_READY.csv" \
   "resultados/matricula_unificada_2026_pregrado_PES_READY.csv"

# Verificar hash SHA256 esperado:
# 8ac3d58613d000534bf4053a5b9e42d13eee5db488f00d62d3f6d035c4df2704
shasum -a 256 resultados/matricula_unificada_2026_pregrado_PES_READY.csv
```

---

## 2. Restaurar Carga Principal al Escritorio

```bash
cp "/Users/alexi/Documents/GitHub/avance_curricular/control/auditoria_mu2026_punto0_complemento95/archivos_congelados/carga_principal/matricula_unificada_2026_pregrado_PARA_SUBIR.csv" \
   "/Users/alexi/Desktop/matricula_unificada_2026_pregrado_PARA_SUBIR.csv"

# Verificar hash SHA256 esperado:
# 8ac3d58613d000534bf4053a5b9e42d13eee5db488f00d62d3f6d035c4df2704
shasum -a 256 "/Users/alexi/Desktop/matricula_unificada_2026_pregrado_PARA_SUBIR.csv"
```

---

## 3. Restaurar Complemento 95 al repositorio

```bash
# Desde la raíz del repositorio:
cp "control/auditoria_mu2026_punto0_complemento95/archivos_congelados/complemento_95/matricula_unificada_2026_COMPLEMENTO_95_CODCLI_PARA_SUBIR.csv" \
   "resultados/complemento_95_codcli/matricula_unificada_2026_COMPLEMENTO_95_CODCLI_PARA_SUBIR.csv"

# Verificar hash SHA256 esperado:
# 9a6bc998c19282da421d6e9aa51606d94d886a87bcf958f74efb40109be62c6d
shasum -a 256 resultados/complemento_95_codcli/matricula_unificada_2026_COMPLEMENTO_95_CODCLI_PARA_SUBIR.csv
```

---

## 4. Restaurar Complemento 95 al Escritorio

```bash
cp "/Users/alexi/Documents/GitHub/avance_curricular/control/auditoria_mu2026_punto0_complemento95/archivos_congelados/complemento_95/matricula_unificada_2026_COMPLEMENTO_95_CODCLI_PARA_SUBIR.csv" \
   "/Users/alexi/Desktop/matricula_unificada_2026_COMPLEMENTO_95_CODCLI_PARA_SUBIR.csv"

# Verificar hash SHA256 esperado:
# 9a6bc998c19282da421d6e9aa51606d94d886a87bcf958f74efb40109be62c6d
shasum -a 256 "/Users/alexi/Desktop/matricula_unificada_2026_COMPLEMENTO_95_CODCLI_PARA_SUBIR.csv"
```

---

## 5. Restaurar Script del Complemento 95

```bash
cp "control/auditoria_mu2026_punto0_complemento95/archivos_congelados/scripts/mu2026_complemento_95_codcli.py" \
   "scripts/mu2026_complemento_95_codcli.py"
```

---

## 6. Restaurar Punto 0 (carpeta de control completa)

```bash
cp -r "control/auditoria_mu2026_punto0_complemento95/evidencia/punto_0/punto_0_carga_principal_mu2026" \
      "control/punto_0_carga_principal_mu2026"
```

---

## 7. Verificación post-restauración

```bash
# Contar filas y verificar estructura carga principal
python3 -c "
import csv
with open('resultados/matricula_unificada_2026_pregrado_PES_READY.csv') as f:
    rows = list(csv.reader(f, delimiter=';'))
print(f'Filas: {len(rows)} | Cols: {len(rows[0])}')
assert len(rows) == 4070, 'ERROR: filas esperadas 4070'
assert len(rows[0]) == 32, 'ERROR: columnas esperadas 32'
print('OK: 4070x32')
"

# Contar filas y verificar estructura complemento 95
python3 -c "
import csv
with open('resultados/complemento_95_codcli/matricula_unificada_2026_COMPLEMENTO_95_CODCLI_PARA_SUBIR.csv') as f:
    rows = list(csv.reader(f, delimiter=';'))
print(f'Filas: {len(rows)} | Cols: {len(rows[0])}')
assert len(rows) == 95, 'ERROR: filas esperadas 95'
assert len(rows[0]) == 32, 'ERROR: columnas esperadas 32'
print('OK: 95x32')
"
```

---

## Notas

- Este archivo fue generado automáticamente por `scripts/auditoria_mu2026_punto0_complemento95.py`
- La carpeta `archivos_congelados/` contiene las copias verificadas con hash SHA256.
- La carpeta `evidencia/` contiene copias completas de directorios de control.
- Consultar `MANIFEST_AUDITORIA_MU2026.json` para los hashes completos.
- Consultar `COMPARACION_HASHES.tsv` para verificación cruzada.
