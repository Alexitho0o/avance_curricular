"""Entregable 3: Reporte de KPI (.md y .docx). Gestión interna, no se sube a PES."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))  # raíz del monorepo (para 'common.*')
sys.path.insert(0, str(Path(__file__).parent.parent))       # procesos/ire_2026 (para 'src.*')

from datetime import datetime
from typing import Dict, List, Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from docx import Document
from docx.shared import Inches, Pt

from common.reportes import tabla_markdown, guardar_reporte_md
from src.kpi import (
    SERIE_HISTORICA,
    calcular_indicadores,
    calcular_serie_historica,
    calcular_variacion,
    redondear_presentacion,
)
from src.config_loader import cargar_institucion, cargar_parametros

RAIZ_PROCESO = Path(__file__).parent.parent
RUTA_OUTPUT = RAIZ_PROCESO / "output"

ETIQUETAS_INDICADORES = {
    "m2_construidos_por_estudiante": "M² construidos por estudiante",
    "m2_areas_verdes_por_estudiante": "M² áreas verdes por estudiante",
    "m2_talleres_lab_por_estudiante": "M² talleres y laboratorios por estudiante",
    "computadores_por_estudiante": "Computadores por estudiante",
    "capacidad_salas_por_estudiante": "Capacidad de salas por estudiante",
    "volumenes_fisicos_por_estudiante": "Volúmenes físicos por estudiante",
    "ebooks_por_estudiante": "E-books por estudiante",
    "horas_bibliotecario_por_100_estudiantes": "Horas bibliotecario / 100 estudiantes",
    "tasa_ocupacion_salas": "Tasa de ocupación de salas (matrícula/capacidad)",
}

ANOMALIAS = [
    (
        "Cambio de razón social en 2024 (CIISA → IP San Sebastián)",
        "Rompe la comparabilidad directa de la serie 2023 vs. 2024-2025: la institución "
        "informante cambió de identidad legal, no solo de nombre.",
    ),
    (
        "Terreno 1280 → 789 m² en 2024, sin variación en m² construidos",
        "Marcado como anomalía de origen metodológico probable (no como pérdida física de "
        "terreno). Pendiente de confirmación institucional; no se suaviza ni se corrige "
        "unilateralmente en este reporte.",
    ),
    (
        "Matrícula 220 → 160 → 248 (salto en 2024)",
        "El descenso a 160 en 2024 infla artificialmente todos los indicadores per cápita "
        "de ese año (denominador más pequeño). Los máximos de 2024 en la tabla de KPI son "
        "artefactos del denominador, no mejoras reales de infraestructura.",
    ),
    (
        "Registro TIPO 2 (convenio USS Los Leones) aparece recién en 2025",
        "No hay serie histórica 2023-2024 para este convenio; se reporta desde su primera "
        "aparición en la carga.",
    ),
    (
        "Denominador de los indicadores: matricula presencial, no matricula total",
        "Los indicadores por estudiante usan como denominador la matricula vigente "
        "de modalidad presencial (jornadas diurna y vespertina), excluyendo la "
        "matricula de modalidad a distancia. Criterio: el indicador mide uso de "
        "infraestructura fisica, y la matricula online no ocupa salas, laboratorios "
        "ni equipamiento del recinto. De los 3110 estudiantes vigentes al corte, "
        "2420 son de modalidad a distancia y quedan fuera del calculo; el "
        "denominador aplicado es 690 (193 diurno + 497 vespertino). Cualquier "
        "comparacion contra ratios calculados sobre matricula total arrojara "
        "valores sustancialmente menores.",
    ),
    (
        "Comparabilidad de la serie 2023-2025 con el criterio 2026",
        "El denominador 2026 se calculo explicitamente sobre matricula presencial "
        "(690). Los valores historicos 2023=220, 2024=160 y 2025=248 provienen del "
        "archivo institucional de indicadores y no consta si excluian o no la "
        "modalidad a distancia. El salto de 248 a 690 es coherente con un "
        "crecimiento de matricula, pero la variacion interanual no debe usarse con "
        "fines comparativos externos hasta confirmar el criterio de los anios "
        "anteriores con la direccion academica.",
    ),
]


def extraer_datos_2026(filas: List[Dict], matricula_2026: int) -> Dict:
    """Extraer del dataset 2026 ya construido las magnitudes necesarias para KPI."""
    datos = {"matricula": matricula_2026}

    for fila in filas:
        tipo = fila.get("TIPO_INFRAESTRUCTURA", "").strip()

        if tipo == "1":
            def num(campo):
                v = fila.get(campo, "").strip()
                try:
                    return float(v) if v else None
                except ValueError:
                    return None

            datos["m2_edificados"] = num("TOTAL_M2_EDIFICADOS")
            datos["m2_areas_verdes"] = num("TOTAL_M2_AREAS_VERDES")
            datos["m2_talleres"] = num("TOTAL_M2_TALLERES")
            datos["m2_laboratorios"] = num("TOTAL_M2_LABORATORIOS")
            datos["total_pc_nb_disponible"] = num("TOTAL_PC_NB_DISPONIBLE")
            datos["capacidad_salas_clases"] = num("CAPACIDAD_SALAS_CLASES")

        elif tipo == "3":
            def num3(campo):
                v = fila.get(campo, "").strip()
                try:
                    return float(v) if v else None
                except ValueError:
                    return None

            datos["total_volumenes_disponibles"] = num3("TOTAL_VOLUMENES_DISPONIBLES")
            datos["horas_personal_biblioteca"] = num3("HORAS_PERSONAL_BIBLIOTECA")

        elif tipo == "4":
            v = fila.get("TOTAL_TITULOS_LIBROS_DIGITALES", "").strip()
            datos["total_titulos_libros_digitales"] = float(v) if v else None

    return datos


def construir_tabla_base(serie_extendida: Dict) -> str:
    """Tabla de indicadores base 2023-2026."""
    filas_tabla = []
    conceptos = [
        ("Matrícula jornada principal", "matricula"),
        ("M² de terreno", "m2_terreno"),
        ("M² construidos", "m2_edificados"),
        ("M² áreas verdes y esparcimiento", "m2_areas_verdes"),
        ("M² talleres", "m2_talleres"),
        ("Nº auditorios", "total_auditorios"),
        ("Nº computadores", "total_pc_nb_disponible"),
        ("Nº talleres", "total_talleres"),
        ("Nº salas", "total_salas_clases"),
        ("Nº laboratorios", "total_laboratorios"),
        ("Libros digitales (e-books)", "total_titulos_libros_digitales"),
        ("LMS", "lms"),
        ("Videoconferencia", "videoconferencia"),
        ("Razón social informada", "razon_social"),
    ]

    for etiqueta, clave in conceptos:
        fila = [etiqueta]
        for anio in (2023, 2024, 2025, 2026):
            valor = serie_extendida.get(anio, {}).get(clave, "—")
            fila.append(_formatear_valor(valor))
        filas_tabla.append(fila)

    return tabla_markdown(["Concepto", "2023", "2024", "2025", "2026"], filas_tabla)


def _formatear_valor(valor) -> str:
    """Formatear un valor para tabla: enteros sin '.0', None/faltante como '—'."""
    if valor is None:
        return "—"
    if isinstance(valor, float) and valor == int(valor):
        return str(int(valor))
    return str(valor)


def construir_tabla_derivados(indicadores_por_anio: Dict) -> str:
    """Tabla de indicadores derivados con variación interanual 2025→2026."""
    filas_tabla = []

    for clave, etiqueta in ETIQUETAS_INDICADORES.items():
        v2025 = indicadores_por_anio.get(2025, {}).get(clave)
        v2026 = indicadores_por_anio.get(2026, {}).get(clave)
        variacion = calcular_variacion(v2026, v2025)

        v2025_fmt = redondear_presentacion(v2025) if v2025 is not None else "—"
        v2026_fmt = redondear_presentacion(v2026) if v2026 is not None else "—"
        abs_fmt = redondear_presentacion(variacion["absoluta"]) if variacion["absoluta"] is not None else "—"
        pct_fmt = redondear_presentacion(variacion["porcentual"]) if variacion["porcentual"] is not None else "—"
        pct_fmt = f"{pct_fmt}%" if pct_fmt != "—" else "—"

        filas_tabla.append([etiqueta, v2025_fmt, v2026_fmt, abs_fmt, pct_fmt])

    return tabla_markdown(
        ["Indicador", "2025", "2026", "Var. absoluta", "Var. %"],
        filas_tabla,
    )


def generar_graficos(serie_extendida: Dict, indicadores_por_anio: Dict, ruta_dir: Path) -> List[Path]:
    """Generar 3 gráficos: matrícula, m² construidos/est, PCs/est."""
    ruta_dir.mkdir(parents=True, exist_ok=True)
    rutas = []

    anios = [a for a in (2023, 2024, 2025, 2026) if a in serie_extendida]

    # Gráfico 1: matrícula
    matriculas = [serie_extendida[a].get("matricula") for a in anios]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(anios, matriculas, marker='o', color='#2563eb')
    ax.set_title("Evolución de matrícula jornada principal")
    ax.set_xlabel("Año")
    ax.set_ylabel("Matrícula")
    ax.set_xticks(anios)
    ax.grid(alpha=0.3)
    ruta1 = ruta_dir / "grafico_matricula.png"
    fig.savefig(ruta1, dpi=120, bbox_inches='tight')
    plt.close(fig)
    rutas.append(ruta1)

    # Gráfico 2: m² construidos por estudiante
    m2_est = [indicadores_por_anio.get(a, {}).get("m2_construidos_por_estudiante") for a in anios]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(anios, m2_est, marker='o', color='#16a34a')
    ax.set_title("M² construidos por estudiante")
    ax.set_xlabel("Año")
    ax.set_ylabel("m² / estudiante")
    ax.set_xticks(anios)
    ax.grid(alpha=0.3)
    ruta2 = ruta_dir / "grafico_m2_construidos_por_estudiante.png"
    fig.savefig(ruta2, dpi=120, bbox_inches='tight')
    plt.close(fig)
    rutas.append(ruta2)

    # Gráfico 3: computadores por estudiante
    pc_est = [indicadores_por_anio.get(a, {}).get("computadores_por_estudiante") for a in anios]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(anios, pc_est, marker='o', color='#dc2626')
    ax.set_title("Computadores por estudiante")
    ax.set_xlabel("Año")
    ax.set_ylabel("PCs / estudiante")
    ax.set_xticks(anios)
    ax.grid(alpha=0.3)
    ruta3 = ruta_dir / "grafico_pcs_por_estudiante.png"
    fig.savefig(ruta3, dpi=120, bbox_inches='tight')
    plt.close(fig)
    rutas.append(ruta3)

    return rutas


def generar_reporte_md(
    institucion: Dict,
    serie_extendida: Dict,
    indicadores_por_anio: Dict,
    filas: List[Dict],
    mensajes_validacion: List[str],
    log_herencias: List[str],
    fecha_sufijo: str,
) -> str:
    """Construir el reporte completo en Markdown."""
    metadata = {
        "Institución": institucion["razon_social"],
        "COD_IES": institucion["cod_ies"],
        "Fecha de corte": institucion["fecha_corte"],
        "Fecha de generación": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Responsable": "Generado automáticamente por pipeline IRE 2026",
        "ID de carga": institucion["id_carga"],
    }

    secciones = []

    secciones.append({
        "titulo": "2. Indicadores base 2023-2026",
        "contenido": construir_tabla_base(serie_extendida),
    })

    secciones.append({
        "titulo": "3. Indicadores derivados (variación 2025 → 2026)",
        "contenido": construir_tabla_derivados(indicadores_por_anio),
    })

    secciones.append({
        "titulo": "4. Gráficos de evolución",
        "contenido": (
            "![Evolución de matrícula](grafico_matricula.png)\n\n"
            "![M² construidos por estudiante](grafico_m2_construidos_por_estudiante.png)\n\n"
            "![Computadores por estudiante](grafico_pcs_por_estudiante.png)"
        ),
    })

    anomalias_texto = "\n\n".join(f"**{titulo}**\n\n{detalle}" for titulo, detalle in ANOMALIAS)
    secciones.append({
        "titulo": "5. Anomalías y notas metodológicas",
        "contenido": anomalias_texto,
    })

    if log_herencias:
        herencias_texto = "\n".join(f"- {h}" for h in log_herencias)
    else:
        herencias_texto = "Sin herencias aplicadas (todos los valores 2026 fueron confirmados explícitamente)."

    filas_texto = "\n".join(
        f"- Fila {i} — TIPO {f.get('TIPO_INFRAESTRUCTURA')}: {f.get('NOMBRE_IDENTIFICACION')} "
        f"({f.get('COMUNA')}, {f.get('DIRECCION_INMUEBLE')})"
        for i, f in enumerate(filas)
    )

    if mensajes_validacion:
        validacion_texto = "\n".join(f"- {m}" for m in mensajes_validacion)
    else:
        validacion_texto = "Sin errores. Todas las filas pasaron las reglas del Anexo III."

    secciones.append({
        "titulo": "6. Anexo: detalle de filas cargadas, validaciones y herencias",
        "contenido": (
            f"### Filas cargadas ({len(filas)})\n\n{filas_texto}\n\n"
            f"### Resultado de validaciones\n\n{validacion_texto}\n\n"
            f"### Herencias de configuración aplicadas\n\n{herencias_texto}"
        ),
    })

    from common.reportes import crear_reporte_md
    return crear_reporte_md(
        titulo="Reporte KPI — Infraestructura y Recursos Educacionales 2026",
        secciones=secciones,
        metadata=metadata,
    )


def generar_reporte_docx(
    institucion: Dict,
    serie_extendida: Dict,
    indicadores_por_anio: Dict,
    rutas_graficos: List[Path],
    ruta_salida: Path,
) -> None:
    """Construir el reporte completo en .docx."""
    doc = Document()

    doc.add_heading("Reporte KPI — Infraestructura y Recursos Educacionales 2026", level=0)

    doc.add_heading("1. Ficha", level=1)
    ficha = doc.add_table(rows=0, cols=2)
    for etiqueta, valor in [
        ("Institución", institucion["razon_social"]),
        ("COD_IES", str(institucion["cod_ies"])),
        ("Fecha de corte", str(institucion["fecha_corte"])),
        ("Fecha de generación", datetime.now().strftime("%Y-%m-%d %H:%M")),
        ("ID de carga", str(institucion["id_carga"])),
    ]:
        fila = ficha.add_row()
        fila.cells[0].text = etiqueta
        fila.cells[1].text = valor

    doc.add_heading("2. Indicadores base 2023-2026", level=1)
    conceptos = [
        ("Matrícula jornada principal", "matricula"),
        ("M² construidos", "m2_edificados"),
        ("M² áreas verdes", "m2_areas_verdes"),
        ("Libros digitales (e-books)", "total_titulos_libros_digitales"),
    ]
    tabla = doc.add_table(rows=1, cols=5)
    hdr = tabla.rows[0].cells
    for i, h in enumerate(["Concepto", "2023", "2024", "2025", "2026"]):
        hdr[i].text = h
    for etiqueta, clave in conceptos:
        fila = tabla.add_row().cells
        fila[0].text = etiqueta
        for i, anio in enumerate((2023, 2024, 2025, 2026), start=1):
            valor = serie_extendida.get(anio, {}).get(clave)
            fila[i].text = str(valor) if valor is not None else "—"

    doc.add_heading("3. Indicadores derivados", level=1)
    tabla2 = doc.add_table(rows=1, cols=3)
    hdr2 = tabla2.rows[0].cells
    for i, h in enumerate(["Indicador", "2025", "2026"]):
        hdr2[i].text = h
    for clave, etiqueta in ETIQUETAS_INDICADORES.items():
        fila = tabla2.add_row().cells
        fila[0].text = etiqueta
        v2025 = indicadores_por_anio.get(2025, {}).get(clave)
        v2026 = indicadores_por_anio.get(2026, {}).get(clave)
        fila[1].text = str(redondear_presentacion(v2025)) if v2025 is not None else "—"
        fila[2].text = str(redondear_presentacion(v2026)) if v2026 is not None else "—"

    doc.add_heading("4. Gráficos de evolución", level=1)
    for ruta_grafico in rutas_graficos:
        if ruta_grafico.exists():
            doc.add_picture(str(ruta_grafico), width=Inches(5.5))

    doc.add_heading("5. Anomalías y notas metodológicas", level=1)
    for titulo, detalle in ANOMALIAS:
        p = doc.add_paragraph()
        run = p.add_run(titulo)
        run.bold = True
        doc.add_paragraph(detalle)

    doc.save(str(ruta_salida))


def main():
    from src.build_csv import construir_dataset, validar_dataset_completo, ValidacionFallida
    from src.config_loader import ConfiguracionIncompleta

    print("=" * 70)
    print("IRE 2026 — Generación del Reporte de KPI")
    print("=" * 70)

    log_herencias = []
    try:
        filas = construir_dataset(log_herencias)
    except ConfiguracionIncompleta as e:
        print("\n✗ PIPELINE DETENIDO — configuración incompleta\n")
        print(str(e))
        sys.exit(1)

    es_valido, mensajes = validar_dataset_completo(filas)
    if not es_valido:
        print(f"\n✗ VALIDACIÓN FALLIDA — {len(mensajes)} error(es), el reporte no se genera.\n")
        for m in mensajes:
            print(f"  - {m}")
        raise ValidacionFallida(f"{len(mensajes)} error(es) de validación")

    institucion = cargar_institucion()
    parametros = cargar_parametros()
    matricula_2026 = parametros["matricula_jornada_principal_2026"]

    datos_2026 = extraer_datos_2026(filas, matricula_2026)

    serie_extendida = dict(SERIE_HISTORICA)
    serie_extendida[2026] = datos_2026

    indicadores_por_anio = calcular_serie_historica()
    indicadores_por_anio[2026] = calcular_indicadores(datos_2026)

    fecha_sufijo = datetime.now().strftime('%Y%m%d')
    RUTA_OUTPUT.mkdir(parents=True, exist_ok=True)

    rutas_graficos = generar_graficos(serie_extendida, indicadores_por_anio, RUTA_OUTPUT)

    contenido_md = generar_reporte_md(
        institucion, serie_extendida, indicadores_por_anio, filas, mensajes, log_herencias, fecha_sufijo
    )
    ruta_md = RUTA_OUTPUT / "Reporte_KPI_Infraestructura_2026.md"
    guardar_reporte_md(contenido_md, str(ruta_md))
    print(f"\n✓ Generado: {ruta_md}")

    ruta_docx = RUTA_OUTPUT / "Reporte_KPI_Infraestructura_2026.docx"
    generar_reporte_docx(institucion, serie_extendida, indicadores_por_anio, rutas_graficos, ruta_docx)
    print(f"✓ Generado: {ruta_docx}")


if __name__ == '__main__':
    main()
