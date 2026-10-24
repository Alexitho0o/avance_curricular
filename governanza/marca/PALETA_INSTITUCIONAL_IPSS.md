# Paleta institucional IPSS — gobernanza de color y marca

**Estado:** GOBERNADO desde 2026-09-30. No existía ningún archivo de gobernanza de marca/color
en este repositorio antes de esta fecha — se verificó con búsqueda exhaustiva
(`grep -ril "color"` en todo el repo) y no se encontró ninguno. Este archivo es ahora la fuente
única de verdad para colores institucionales en todo documento generado a partir de este proyecto
(Excel, Power BI, PPTX, etc.).

**Fuente:** `Manual_de_Marca_IP_San_Sebastian.pdf` (copia en esta misma carpeta), sección 7 "Colores"
(páginas 10). Entregado por el usuario, 2026-09-30.

## A. Paleta oficial (clasificación A — definición oficial del manual de marca)

### Paleta principal

| Nombre | HEX | RGB | CMYK |
|---|---|---|---|
| Azul Institucional | `#102B42` | 16, 43, 66 | 100, 78, 45, 50 |
| Dorado Institucional | `#CFB47C` | 207, 180, 124 | 17, 25, 55, 8 |
| Azul Oscuro | `#0E4273` | 14, 66, 115 | 88, 43, 0, 55 |

### Paleta secundaria

| Nombre | HEX | RGB | CMYK |
|---|---|---|---|
| Azul Medio | `#0077B6` | 0, 119, 182 | 100, 35, 0, 29 |
| Celeste | `#0096C7` | 0, 150, 199 | 100, 25, 0, 22 |
| Gris Oscuro | `#3A3A3A` | 58, 58, 58 | 0, 0, 0, 77 |
| Gris Claro | `#F2F2F2` | 242, 242, 242 | 0, 0, 0, 5 |

Nota de corrección (dato observado, 2026-09-30): el color `#1E2761` usado como "navy" aproximado
en versiones anteriores de `RETENCION_IPSS_ANALISIS_2022_2026.xlsx` (menú de navegación, títulos,
color de pestaña) **no es** ninguno de los colores oficiales de arriba. Se reemplazó en todo el
libro por Azul Institucional `#102B42`.

## B. Asignación de color por dimensión analítica (clasificación D — decisión interna)

Esta asignación es la **primera vez** que se define qué color institucional representa cada
categoría de estas dimensiones (no existía antes). Queda documentada aquí para que todo gráfico —
en este Excel, en el Power BI de matrícula, o en cualquier otro documento del proyecto — use
siempre los mismos colores para los mismos valores. Si el usuario pide cambiarla, se actualiza este
archivo primero y luego los documentos que la usan.

### Sector IPSS

| Categoría | HEX |
|---|---|
| Tecnologías | `#102B42` (Azul Institucional) |
| Administración y Comercio | `#CFB47C` (Dorado Institucional) |
| Salud | `#0077B6` (Azul Medio) |

### Modalidad

Se evitó el rojo (connota "malo/error" y ninguna modalidad es intrínsecamente negativa) y el azul
genérico no institucional usado antes.

| Categoría | HEX |
|---|---|
| Presencial | `#0E4273` (Azul Oscuro) |
| A distancia | `#CFB47C` (Dorado Institucional) |

### Sexo

| Categoría | HEX |
|---|---|
| Hombre | `#0E4273` (Azul Oscuro) |
| Mujer | `#0096C7` (Celeste) |
| No binario | `#3A3A3A` (Gris Oscuro) — uso mínimo, n=1 en la base actual |

### Tramo de edad (escala, de menor a mayor edad)

| Categoría | HEX |
|---|---|
| Menos de 20 | `#0096C7` (Celeste) |
| 20-24 | `#0077B6` (Azul Medio) |
| 25-29 | `#0E4273` (Azul Oscuro) |
| 30-39 | `#102B42` (Azul Institucional) |
| 40+ | `#CFB47C` (Dorado Institucional) |

## C. Tipografía (clasificación A, referencia — no aplicable a Excel)

El manual define Montserrat (principal, digital), Gotham (uso institucional formal) y Suiza
Condensed (uso funcional/espacio limitado). Excel no permite incrustar estas fuentes de forma
portable entre equipos sin que estén instaladas localmente, así que los libros Excel de este
proyecto usan Calibri/Cambria (fuentes estándar de Office, garantizado que se ven igual en
cualquier equipo) — deviación documentada, no un incumplimiento silencioso.

## D. Archivos relacionados en esta carpeta

- `Manual_de_Marca_IP_San_Sebastian.pdf` — manual completo, fuente A.
- `logo_ipss_horizontal.png` — imagotipo institucional horizontal (versión positiva), entregado
  por el usuario 2026-09-30, usado en la Portada de `RETENCION_IPSS_ANALISIS_2022_2026.xlsx`.

Verificado por: Claude, 2026-09-30.
