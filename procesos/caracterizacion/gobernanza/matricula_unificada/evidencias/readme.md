# EXTRACCION_MATRICULA_SIES_2007_2025

## 1. Propósito del proyecto

Este subproyecto tiene como objetivo extraer, filtrar y consolidar información de matrícula de Educación Superior desde archivos públicos SIES con MRUN para el período 2007-2025.

El script principal actual es:

- `codigo_extraccion_matricula.py`

Su responsabilidad esperada es:

- detectar archivos tabulares en la carpeta `datos/`
- leer columnas relevantes de matrícula
- aplicar filtros configurables
- consolidar resultados
- exportar salidas en Excel y CSV

Ruta local operativa de referencia:

`/Users/alexi/Documents/GitHub/CARACTERIZACIÓN/EXTRACCION_MATRICULA_SIES _2007_2025`

---

## 2. Estado actual del proyecto

Estado actual: **diagnóstico reproducido, corrección pendiente**.

Situación verificada al momento de este README:

- existen 19 archivos CSV en la carpeta `datos/`
- el script principal detecta correctamente el proyecto, la carpeta `datos/` y los archivos a procesar
- actualmente **ningún archivo es procesado con éxito**
- el fallo es consistente entre años y aparece antes de cualquier exportación útil
- esta etapa deja preparada la base documental y operativa para una corrección posterior del código Python

---

## 3. Descripción precisa del problema detectado

El script actual falla al intentar leer los CSV con `pandas` usando selección de columnas por índice posicional (`usecols`).

El error observado es de la forma:

```text
Defining usecols with out-of-bounds indices is not allowed
```

Esto significa que, para la lectura concreta que está ocurriendo, `pandas` interpreta que el archivo tiene menos columnas utilizables de las que el script exige por posición.

Punto importante:

- **cambiar el encoding no resuelve por sí solo este problema**
- si el parser interpreta mal el separador o la estructura real del CSV, el archivo puede quedar con menos columnas detectadas y `usecols` termina quedando fuera de rango

---

## 4. Evidencia resumida del error observado

Ejecución real observada:

- archivos detectados: `19`
- archivos procesados con éxito: `0`
- archivos fallidos: `19`

Ejemplo real del mensaje de error:

```text
utf-8-sig: Defining usecols with out-of-bounds indices is not allowed.
[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 22, 23, 24, 56, 57, 59, 61, 63] are out-of-bounds.
```

El mismo patrón se repite al probar estos encodings:

- `utf-8-sig`
- `utf-8`
- `latin-1`
- `cp1252`

Inspección rápida de archivos reales:

- al menos los CSV revisados usan `;` como separador visible
- las primeras columnas observadas son coherentes con el manual SIES, por ejemplo:
  - `cat_periodo`
  - `id`
  - `codigo_unico`
  - `mrun`
  - `gen_alu`
  - `fec_nac_alu`
- los nombres de archivo no son homogéneos en Unicode:
  - algunos aparecen como `Matrícula...`
  - otros como `Matrícula...`

---

## 5. Hipótesis técnicas del fallo

La falla actual parece originarse por una combinación de fragilidades:

### 5.1 Lectura demasiado acoplada a posiciones fijas

El script usa índices posicionales rígidos hasta columnas altas (por ejemplo 56, 57, 59, 61, 63). Si el archivo no se parsea correctamente, ese ancho deja de existir para `pandas`.

### 5.2 Detección frágil del delimitador

La lógica actual intenta detectar delimitador con `csv.Sniffer`. Si esa detección falla o queda ambigua, un CSV con `;` puede ser leído como una sola columna o con un ancho incorrecto.

### 5.3 Supuesto implícito de estructura uniforme 2007-2025

Aunque los archivos pertenecen al mismo universo SIES, no debe asumirse sin validación que todos los años tengan exactamente el mismo layout efectivo para un parser tabular.

### 5.4 Falta de validación estructural previa

El flujo intenta leer directamente solo columnas objetivo, sin una validación previa explícita de:

- separador real
- encoding funcional
- cantidad real de columnas detectadas
- coherencia básica de cabecera

---

## 6. Alcance de la corrección pendiente

La siguiente intervención sobre `codigo_extraccion_matricula.py` debería enfocarse en:

- desacoplar el diagnóstico estructural de la lectura final
- validar delimitador, encoding y ancho real antes de usar `usecols`
- encapsular una lectura robusta por archivo
- registrar trazabilidad por año/archivo
- mantener las salidas a `salida/` solo después de una lectura validada

No forma parte de esta fase:

- redefinir la lógica de negocio del proyecto
- cambiar el objetivo funcional del script
- introducir dependencias no necesarias
- rehacer el proyecto completo

---

## 7. Estrategia propuesta de solución a alto nivel

La estrategia recomendada para la próxima etapa es:

1. **Inspección previa por archivo**
   - detectar delimitador real
   - detectar encoding viable
   - leer cabecera o muestra mínima
   - medir el ancho real del archivo

2. **Validación estructural antes de `usecols`**
   - comparar el ancho detectado con el índice máximo requerido
   - abortar por archivo con un mensaje claro si no cumple mínimos

3. **Lectura robusta desacoplada**
   - leer primero el archivo de forma segura
   - seleccionar columnas solo después de confirmar estructura
   - encapsular esta lógica en una función dedicada, por ejemplo:
     - `leer_csv_sies_robusto(...)`

4. **Logging útil por archivo**
   - archivo
   - encoding utilizado
   - delimitador utilizado
   - número de columnas detectadas
   - estado de procesamiento
   - excepción final, si aplica

---

## 8. Estructura esperada del proyecto

```text
EXTRACCION_MATRICULA_SIES _2007_2025/
├── README.md
├── readme.md                    # alias legado / mismo archivo en filesystem no case-sensitive
├── MANUAL_SIES_2007_2025.md
├── codigo_extraccion_matricula.py
├── diagnostico_extraccion_matricula.sh
├── datos/
│   ├── Matrícula_Ed_Superior_2007_PUBL_MRUN.csv
│   ├── Matrícula_Ed_Superior_2008_PUBL_MRUN.csv
│   ├── ...
│   └── Matrícula_Ed_Superior_2025_PUBL_MRUN.csv
├── salida/
├── salidas/                     # carpeta heredada; no es la ruta principal del script actual
└── logs/                        # creada por el script de diagnóstico si no existe
```

---

## 9. Requisitos de ejecución

### Entorno recomendado

- macOS o Linux
- Python 3.10 o superior
- permisos de lectura sobre `datos/`
- permisos de escritura sobre `salida/` y `logs/`

### Dependencias Python esperadas

```bash
pip install pandas openpyxl
```

---

## 10. Forma de ejecutar el script

### Ejecución directa del Python actual

```bash
python3 "/Users/alexi/Documents/GitHub/CARACTERIZACIÓN/EXTRACCION_MATRICULA_SIES _2007_2025/codigo_extraccion_matricula.py"
```

### Ejecución recomendada antes de corregir el código

Usar primero el script de diagnóstico:

```bash
cd "/Users/alexi/Documents/GitHub/CARACTERIZACIÓN/EXTRACCION_MATRICULA_SIES _2007_2025"
chmod +x diagnostico_extraccion_matricula.sh
./diagnostico_extraccion_matricula.sh
```

---

## 11. Estrategia de diagnóstico recomendada antes de corregir

Antes de modificar `codigo_extraccion_matricula.py`, se recomienda este flujo:

1. validar que existe el directorio del proyecto
2. validar que existe `codigo_extraccion_matricula.py`
3. validar que existe la carpeta `datos/`
4. contar y listar los CSV detectados
5. inspeccionar las primeras líneas de cada archivo
6. ejecutar el script principal con log completo
7. revisar si el fallo es homogéneo o si hay variantes por año

El objetivo inmediato no es forzar una corrida exitosa, sino **reducir incertidumbre estructural** antes del parche.

---

## 12. Criterios de éxito de la corrección

La futura corrección del código Python debería considerarse exitosa si:

1. el script deja de fallar por `usecols out-of-bounds`
2. el delimitador deja de depender de una detección frágil no validada
3. cada archivo registra su diagnóstico estructural básico
4. el pipeline distingue entre error de lectura y error de estructura
5. el procesamiento es reproducible y trazable
6. la solución tolera nombres de archivo con espacios, tildes y normalización Unicode mixta

---

## 13. Manejo esperado de errores y logging

El comportamiento esperado del proyecto, una vez corregido, debería incluir:

- mensajes claros por archivo
- errores no silenciosos
- separación entre:
  - error de delimitador
  - error de encoding
  - error de estructura de columnas
  - error de exportación
- log suficiente para entender por qué un año falló

Mientras la corrección no exista, el script `diagnostico_extraccion_matricula.sh` cumple esa función de trazabilidad operativa inicial.

---

## 14. Próximos pasos

Siguiente etapa sugerida sobre el Python:

1. implementar una función robusta de lectura CSV
2. separar:
   - detección de delimitador
   - detección de encoding
   - validación de ancho real
   - selección de columnas
3. registrar diagnóstico por archivo antes de consolidar resultados
4. decidir si conviene mantener lectura por posiciones o migrar hacia una estrategia híbrida basada en nombres de columnas validados

**No se recomienda seguir probando encodings aisladamente** mientras el error dominante siga siendo `usecols out-of-bounds`.

---

## 15. Notas de compatibilidad sobre nombres de archivo con tildes y normalización Unicode

Este proyecto usa nombres de archivo que pueden variar por normalización Unicode:

- `Matrícula_...`
- `Matrícula_...`

Visualmente pueden verse iguales, pero no siempre son equivalentes byte a byte.

Por eso se recomienda:

- usar siempre rutas entre comillas
- evitar scripts frágiles basados en coincidencias manuales de nombres sin quoting
- usar `find`, `Path`, `glob` o listados del sistema de archivos en vez de copiar nombres a mano
- asumir que en macOS puede haber diferencias entre NFC y NFD

Esto aplica tanto al Python como a cualquier shell script de soporte.

---

## 16. Ruta local de referencia

Ruta absoluta base de trabajo:

```text
/Users/alexi/Documents/GitHub/CARACTERIZACIÓN/EXTRACCION_MATRICULA_SIES _2007_2025
```

---

## 17. Recomendación operativa inmediata

Antes de tocar `codigo_extraccion_matricula.py`, ejecutar el script de diagnóstico y revisar el log generado en `logs/`.

Ese paso deja preparado el terreno para la etapa siguiente: diseñar e implementar una lectura CSV robusta y validada, sin volver a empezar el diagnóstico desde cero.
