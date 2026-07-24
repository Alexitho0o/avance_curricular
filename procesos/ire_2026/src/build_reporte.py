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
        "La institución cambió de nombre en 2024",
        "Hasta 2023 la institución se llamaba Instituto Profesional CIISA. "
        "Desde 2024 opera como Instituto Profesional San Sebastián. "
        "Por este motivo, los datos de 2023 corresponden a una institución "
        "con distinto nombre, lo que limita la comparación directa con años posteriores.",
    ),
    (
        "Cambio de recinto en 2026",
        "Hasta 2025 la institución funcionaba en Av. Libertador Bernardo O'Higgins 2221, "
        "Santiago. Desde 2026 opera en Miguel Claro 337, Providencia. "
        "Los datos de 2026 corresponden exclusivamente al nuevo recinto, "
        "que tiene mayor superficie construida (1.952 m²) y más talleres. "
        "La comparación con años anteriores refleja este cambio de instalaciones.",
    ),
    (
        "Los m² por estudiante bajaron respecto de 2025",
        "En 2025 había 5,49 m² construidos por estudiante. En 2026 son 2,83 m². "
        "Esta baja no significa que el recinto sea más pequeño: el nuevo edificio "
        "tiene más metros cuadrados (1.952 vs 1.362). Lo que cambió es que la "
        "matrícula presencial creció de 248 a 690 estudiantes, principalmente "
        "porque se distinguió entre estudiantes presenciales y en línea por primera vez.",
    ),
    (
        "¿Por qué la matrícula subió tanto de 2025 a 2026?",
        "Los años anteriores (220 en 2023, 160 en 2024, 248 en 2025) incluían "
        "a todos los estudiantes vigentes sin distinguir si asistían presencialmente "
        "o estudiaban en línea. En 2026 se contaron solo los estudiantes que "
        "efectivamente usan las instalaciones físicas: 690 de jornada diurna y "
        "vespertina. Los estudiantes en línea (2.420 personas) no fueron incluidos "
        "porque no ocupan salas, talleres ni equipamiento del recinto.",
    ),
    (
        "Datos pendientes de confirmar",
        "Al momento de generar este informe, algunos datos de 2026 se informaron "
        "con los valores del año anterior porque aún no se disponía de la "
        "información actualizada. Estos son: datos de biblioteca (títulos, "
        "volúmenes, personal), colección digital (e-books, bases de datos) y "
        "plataformas tecnológicas (versión del sistema LMS). Deben confirmarse "
        "y actualizarse antes de la próxima revisión.",
    ),
]


MESES_ES = {
    1: "enero", 2: "febrero", 3: "marzo", 4: "abril", 5: "mayo", 6: "junio",
    7: "julio", 8: "agosto", 9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre",
}


def _fecha_espanol(fecha_iso: str) -> str:
    """Convertir 'AAAA-MM-DD' a '30 de junio de 2026'."""
    anio, mes, dia = fecha_iso.split("-")
    return f"{int(dia)} de {MESES_ES[int(mes)]} de {anio}"


def _fecha_hora_espanol_actual() -> str:
    """Fecha y hora actuales en formato natural: '24 de julio de 2026, 12:30'."""
    ahora = datetime.now()
    return f"{ahora.day} de {MESES_ES[ahora.month]} de {ahora.year}, {ahora.strftime('%H:%M')}"


def construir_ficha(institucion: Dict) -> List[tuple]:
    """Ficha institucional en lenguaje natural, compartida entre .md y .docx."""
    # El nombre se almacena en MAYUSCULAS sin tildes (requisito ASCII de la carga
    # regulatoria); aqui se muestra con grafia correcta ya que este reporte es
    # de gestion interna y no se sube a PES.
    return [
        ("Institución", "Instituto Profesional San Sebastián"),
        ("Código institución", str(institucion["cod_ies"])),
        ("Proceso", "Declaración anual de infraestructura al Ministerio de Educación"),
        ("Fecha de los datos", _fecha_espanol(str(institucion["fecha_corte"]))),
        ("Generado el", _fecha_hora_espanol_actual()),
    ]


def _acumular(actual, nuevo):
    """Sumar acumulando; None significa 'aun sin dato', no 'cero'."""
    if nuevo is None:
        return actual
    return nuevo if actual is None else actual + nuevo


def _num(fila: Dict, campo: str):
    v = fila.get(campo, "").strip()
    try:
        return float(v) if v else None
    except ValueError:
        return None


def extraer_datos_2026(filas: List[Dict], matricula_2026: int) -> Dict:
    """
    Extraer del dataset 2026 ya construido las magnitudes necesarias para KPI.

    Ignora filas con VIGENCIA=0 (registros marcados para eliminacion, no forman
    parte de la infraestructura vigente al corte). Si hay mas de una fila
    vigente del mismo TIPO (p. ej. dos inmuebles TIPO 1 simultaneos), los
    valores se suman en vez de sobrescribirse.
    """
    datos = {
        "matricula": matricula_2026,
        "m2_edificados": None,
        "m2_areas_verdes": None,
        "m2_talleres": None,
        "m2_laboratorios": None,
        "total_pc_nb_disponible": None,
        "capacidad_salas_clases": None,
        "total_volumenes_disponibles": None,
        "horas_personal_biblioteca": None,
        "total_titulos_libros_digitales": None,
    }

    for fila in filas:
        if fila.get("VIGENCIA", "").strip() != "1":
            continue

        tipo = fila.get("TIPO_INFRAESTRUCTURA", "").strip()

        if tipo == "1":
            datos["m2_edificados"] = _acumular(datos["m2_edificados"], _num(fila, "TOTAL_M2_EDIFICADOS"))
            datos["m2_areas_verdes"] = _acumular(datos["m2_areas_verdes"], _num(fila, "TOTAL_M2_AREAS_VERDES"))
            datos["m2_talleres"] = _acumular(datos["m2_talleres"], _num(fila, "TOTAL_M2_TALLERES"))
            datos["m2_laboratorios"] = _acumular(datos["m2_laboratorios"], _num(fila, "TOTAL_M2_LABORATORIOS"))
            datos["total_pc_nb_disponible"] = _acumular(datos["total_pc_nb_disponible"], _num(fila, "TOTAL_PC_NB_DISPONIBLE"))
            datos["capacidad_salas_clases"] = _acumular(datos["capacidad_salas_clases"], _num(fila, "CAPACIDAD_SALAS_CLASES"))

        elif tipo == "3":
            datos["total_volumenes_disponibles"] = _acumular(datos["total_volumenes_disponibles"], _num(fila, "TOTAL_VOLUMENES_DISPONIBLES"))
            datos["horas_personal_biblioteca"] = _acumular(datos["horas_personal_biblioteca"], _num(fila, "HORAS_PERSONAL_BIBLIOTECA"))

        elif tipo == "4":
            datos["total_titulos_libros_digitales"] = _acumular(
                datos["total_titulos_libros_digitales"], _num(fila, "TOTAL_TITULOS_LIBROS_DIGITALES")
            )

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


INTRO_INDICADORES_BASE = (
    "La siguiente tabla muestra los espacios físicos y recursos con que contaba "
    "la institución al 30 de junio de cada año. El 2026 corresponde al nuevo "
    "recinto de Miguel Claro 337 (Providencia), desde donde opera la institución "
    "desde 2026. Los años anteriores corresponden al recinto de Av. Libertador "
    "Bernardo O'Higgins 2221 (Santiago)."
)

INTRO_INDICADORES_DERIVADOS = (
    "Estos indicadores muestran cuántos recursos tiene disponible cada estudiante "
    "de jornada presencial. Se calculan dividiendo el total de la infraestructura "
    "por la matrícula de jornada presencial (690 estudiantes en 2026). No incluye "
    "a los estudiantes de modalidad en línea, ya que ellos no utilizan las "
    "dependencias físicas de la institución."
)

INTRO_GRAFICOS = (
    "Los siguientes gráficos muestran cómo han cambiado los principales "
    "indicadores entre 2023 y 2026. El cambio de recinto y el nuevo criterio "
    "de matrícula explican los saltos visibles entre 2025 y 2026."
)


def generar_reporte_md(
    institucion: Dict,
    serie_extendida: Dict,
    indicadores_por_anio: Dict,
    filas: List[Dict],
    mensajes_validacion: List[str],
    log_herencias: List[str],
    fecha_sufijo: str,
) -> str:
    """Construir el reporte completo en Markdown (version tecnica, con anexo)."""
    metadata = dict(construir_ficha(institucion))

    secciones = []

    secciones.append({
        "titulo": "¿Cuánta infraestructura tiene la institución?",
        "contenido": INTRO_INDICADORES_BASE + "\n\n" + construir_tabla_base(serie_extendida),
    })

    secciones.append({
        "titulo": "¿Cuánto hay por estudiante?",
        "contenido": INTRO_INDICADORES_DERIVADOS + "\n\n" + construir_tabla_derivados(indicadores_por_anio),
    })

    secciones.append({
        "titulo": "Evolución en el tiempo",
        "contenido": (
            INTRO_GRAFICOS + "\n\n"
            "![Evolución de matrícula](grafico_matricula.png)\n\n"
            "![M² construidos por estudiante](grafico_m2_construidos_por_estudiante.png)\n\n"
            "![Computadores por estudiante](grafico_pcs_por_estudiante.png)"
        ),
    })

    anomalias_texto = "\n\n".join(f"**{titulo}**\n\n{detalle}" for titulo, detalle in ANOMALIAS)
    secciones.append({
        "titulo": "Notas importantes para interpretar los datos",
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
        titulo="Informe de Infraestructura y Recursos Educacionales 2026",
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
    """Construir el reporte completo en .docx, en lenguaje simple para lectores sin contexto tecnico."""
    doc = Document()

    doc.add_heading("Informe de Infraestructura y Recursos Educacionales 2026", level=0)

    doc.add_heading("Ficha", level=1)
    ficha = doc.add_table(rows=0, cols=2)
    for etiqueta, valor in construir_ficha(institucion):
        fila = ficha.add_row()
        fila.cells[0].text = etiqueta
        fila.cells[1].text = valor

    doc.add_heading("¿Cuánta infraestructura tiene la institución?", level=1)
    doc.add_paragraph(INTRO_INDICADORES_BASE)
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
            fila[i].text = _formatear_valor(valor)

    doc.add_heading("¿Cuánto hay por estudiante?", level=1)
    doc.add_paragraph(INTRO_INDICADORES_DERIVADOS)
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

    doc.add_heading("Evolución en el tiempo", level=1)
    doc.add_paragraph(INTRO_GRAFICOS)
    for ruta_grafico in rutas_graficos:
        if ruta_grafico.exists():
            doc.add_picture(str(ruta_grafico), width=Inches(5.5))

    doc.add_heading("Notas importantes para interpretar los datos", level=1)
    for titulo, detalle in ANOMALIAS:
        p = doc.add_paragraph()
        run = p.add_run(titulo)
        run.bold = True
        doc.add_paragraph(detalle)

    doc.add_heading("Información técnica adicional", level=1)
    doc.add_paragraph(
        "Para el equipo técnico: el detalle de las filas cargadas, el resultado "
        "de las validaciones y el registro de herencias de datos está disponible "
        "en el archivo Reporte_KPI_Infraestructura_2026.md (versión técnica)."
    )

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
