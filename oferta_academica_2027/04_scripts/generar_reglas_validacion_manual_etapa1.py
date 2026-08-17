#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "11_gobernanza" / "reglas_validacion_etapa1_manual"


def rules() -> list[dict[str, object]]:
    return [
        {
            "id": "OA1-001",
            "severidad": "BLOQUEANTE",
            "categoria": "estructura",
            "alcance": "Etapa 1 Vigente Editada",
            "validacion": "estructura_48_columnas_sin_campos_excluidos",
            "campos": ["CODIGO_IES_NUM", "CANTIDAD_MATRICULA_DFE", "CANTIDAD_BENEFICIO_DFE"],
            "regla_manual": "Antes de cargar se debe eliminar código de institución, cantidad matrícula DFE y cantidad beneficio DFE; CSV sin encabezados al cargar.",
            "fuente_lineas": "523-525, 545-548",
            "automatizable": True,
        },
        {
            "id": "OA1-002",
            "severidad": "BLOQUEANTE",
            "categoria": "estructura",
            "alcance": "Etapa 1 Vigente Editada",
            "validacion": "no_agregar_programas_y_mantener_programas_presentados",
            "campos": ["COD_SEDE", "COD_CARRERA", "NOMBRE_CARRERA", "VERSION"],
            "regla_manual": "Solo se deben cargar programas de pregrado presentados en vigencia inicial; no agregar programas nuevos o faltantes.",
            "fuente_lineas": "541-548",
            "automatizable": True,
        },
        {
            "id": "OA1-003",
            "severidad": "BLOQUEANTE",
            "categoria": "estructura",
            "alcance": "Etapa 1 Vigente Editada",
            "validacion": "solo_campos_modificables_pueden_cambiar",
            "campos": "todos_los_no_modificables",
            "regla_manual": "La oferta vigente TP adscritas no podrá modificarse excepto en las columnas permitidas.",
            "fuente_lineas": "568-607",
            "automatizable": True,
        },
        {
            "id": "OA1-004",
            "severidad": "BLOQUEANTE",
            "categoria": "dominio",
            "alcance": "Etapa 1 Vigente Editada",
            "validacion": "cod_nivel_global_pregrado_y_nivel_carrera_0_4",
            "campos": ["COD_NIVEL_GLOBAL", "COD_NIVEL_CARRERA"],
            "regla_manual": "COD_NIVEL_GLOBAL considera valor 1: Pregrado; COD_NIVEL_CARRERA puede ser 0, 1, 2, 3 o 4.",
            "fuente_lineas": "1867, 1938-1941",
            "automatizable": True,
        },
        {
            "id": "OA1-005",
            "severidad": "BLOQUEANTE",
            "categoria": "dominio",
            "alcance": "Etapa 1 Vigente Editada",
            "validacion": "modalidad_jornada_compatibles",
            "campos": ["MODALIDAD", "COD_JORNADA"],
            "regla_manual": "Jornada y modalidad deben ser compatibles: diurna/vespertina no pueden ser no presencial; a distancia exige no presencial; no presencial exige a distancia.",
            "fuente_lineas": "1773-1779, 1872-1877",
            "automatizable": True,
        },
        {
            "id": "OA1-006",
            "severidad": "BLOQUEANTE",
            "categoria": "dominio",
            "alcance": "Etapa 1 Vigente Editada",
            "validacion": "dominios_numericos_basicos",
            "campos": [
                "MODALIDAD",
                "COD_JORNADA",
                "COD_TIPO_PLAN_CARRERA",
                "REGIMEN",
                "ACREDITACION",
                "REQUISITO_INGRESO",
                "FORMATO_VALOR",
                "VIGENCIA_CARRERA",
            ],
            "regla_manual": "Campos de catálogo deben respetar valores permitidos descritos por el instructivo.",
            "fuente_lineas": "1936-1947, 1958-1959, 1979, 2006-2010",
            "automatizable": True,
        },
        {
            "id": "OA1-007",
            "severidad": "BLOQUEANTE",
            "categoria": "areas",
            "alcance": "Etapa 1 Vigente Editada",
            "validacion": "area_actual_y_destino_valores",
            "campos": [
                "AREA_ACTUAL",
                "AREA_ADMIN_DERECHO",
                "AREA_AGRI_SILVI_PESCA_VET",
                "AREA_ARTES_HUMANIDADES",
                "AREA_CIENCIAS_NAT_MAT_ESTAD",
                "AREA_CS_SOCIAL_PERIODISMO_INFO",
                "AREA_EDUCACION",
                "AREA_INGE_INDUSTRIA_CONSTRUC",
                "AREA_SALUD_BIENESTAR",
                "AREA_SERVICIOS",
                "AREA_TECNO_INFO_COMUNICA",
            ],
            "regla_manual": "AREA_ACTUAL considera valores 1 a 10; áreas de destino consideran 0 o 1.",
            "fuente_lineas": "1917-1930",
            "automatizable": True,
        },
        {
            "id": "OA1-008",
            "severidad": "BLOQUEANTE",
            "categoria": "areas",
            "alcance": "Etapa 1 Vigente Editada",
            "validacion": "reglas_area_por_nivel_carrera",
            "campos": ["COD_NIVEL_CARRERA", "AREA_ACTUAL", "areas_destino"],
            "regla_manual": "Para nivel 1 el área destino debe incluir el área actual y no superar 5 áreas; para nivel 2 y 4 las áreas destino deben ser 0; nivel 3 exige Educación=1 y resto 0.",
            "fuente_lineas": "1810-1866",
            "automatizable": True,
        },
        {
            "id": "OA1-009",
            "severidad": "BLOQUEANTE",
            "categoria": "plan",
            "alcance": "Etapa 1 Vigente Editada",
            "validacion": "plan_regular_semestres_reconocidos_cero",
            "campos": ["COD_TIPO_PLAN_CARRERA", "SEMESTRES_RECONOCIDOS"],
            "regla_manual": "Cuando COD_TIPO_PLAN_CARRERA es 1 Plan Regular, SEMESTRES_RECONOCIDOS debe ser 0.",
            "fuente_lineas": "1868-1869",
            "automatizable": True,
        },
        {
            "id": "OA1-010",
            "severidad": "BLOQUEANTE",
            "categoria": "duraciones",
            "alcance": "Etapa 1 Vigente Editada",
            "validacion": "duraciones_coherentes",
            "campos": ["DURACION_ESTUDIOS", "DURACION_TITULACION", "DURACION_TOTAL", "DURACION_REGIMEN", "REGIMEN"],
            "regla_manual": "Duraciones deben ser coherentes: total >= estudios, estudios + titulación >= total, estudios <=14 y duraciones dentro de rango.",
            "fuente_lineas": "1721-1733, 1742-1748, 1870-1871, 1983-1990",
            "automatizable": True,
        },
        {
            "id": "OA1-011",
            "severidad": "BLOQUEANTE",
            "categoria": "vigencia",
            "alcance": "Etapa 1 Vigente Editada",
            "validacion": "vigencia_1_obligatorios",
            "campos": [
                "ARANCEL_ANUAL",
                "COSTO_TITULACION",
                "FORMATO_VALOR",
                "RECONOCIMIENTOS_APREN_PREVIOS",
                "VALOR_CERTIFICADO_DIPLOMA",
                "VALOR_MATRICULA_ANUAL",
                "EXPERIENCIA_LABORAL",
                "FECHA_ADMISION_INICIAL",
                "LICENCIA_ENS_MEDIA",
                "MAIL_DIFUSION_CARRERA",
                "NOTAS_ENS_MEDIA",
                "PROMEDIO_MIN_ENS_MEDIA",
            ],
            "regla_manual": "Cuando VIGENCIA_CARRERA es 1 se deben completar campos obligatorios de admisión, requisitos, mail y valores.",
            "fuente_lineas": "1878-1902",
            "automatizable": True,
        },
        {
            "id": "OA1-012",
            "severidad": "BLOQUEANTE",
            "categoria": "vigencia",
            "alcance": "Etapa 1 Vigente Editada",
            "validacion": "vigencia_1_vacantes_no_cero",
            "campos": ["VACANTES_PRIMER_SEMESTRE", "VACANTES_SEGUNDO_SEMESTRE"],
            "regla_manual": "Cuando la vigencia es 1, las vacantes semestrales no pueden ser 0.",
            "fuente_lineas": "1878",
            "automatizable": True,
        },
        {
            "id": "OA1-013",
            "severidad": "BLOQUEANTE",
            "categoria": "vigencia",
            "alcance": "Etapa 1 Vigente Editada",
            "validacion": "vigencia_2_fecha_vacia_y_vacantes_cero",
            "campos": ["VIGENCIA_CARRERA", "FECHA_ADMISION_INICIAL", "VACANTES_PRIMER_SEMESTRE", "VACANTES_SEGUNDO_SEMESTRE"],
            "regla_manual": "Cuando VIGENCIA_CARRERA es 2, FECHA_ADMISION_INICIAL no se debe completar y las vacantes deben ser 0.",
            "fuente_lineas": "1903-1906",
            "automatizable": True,
        },
        {
            "id": "OA1-014",
            "severidad": "BLOQUEANTE",
            "categoria": "notas",
            "alcance": "Etapa 1 Vigente Editada",
            "validacion": "notas_promedio_coherentes",
            "campos": ["NOTAS_ENS_MEDIA", "PROMEDIO_MIN_ENS_MEDIA"],
            "regla_manual": "Si NOTAS_ENS_MEDIA es NO, PROMEDIO_MIN_ENS_MEDIA debe ser 0; si es SI, debe completarse y estar entre 4,00 y 7,00.",
            "fuente_lineas": "1907-1913, 1953, 2007",
            "automatizable": True,
        },
        {
            "id": "OA1-015",
            "severidad": "BLOQUEANTE",
            "categoria": "formato",
            "alcance": "Etapa 1 Vigente Editada",
            "validacion": "mail_y_url_validos",
            "campos": ["ENLACE_INFO_PROGRAMA", "MAIL_DIFUSION_CARRERA"],
            "regla_manual": "El enlace debe ser completo; debe ingresar un mail correcto.",
            "fuente_lineas": "949-951, 1915",
            "automatizable": True,
        },
        {
            "id": "OA1-016",
            "severidad": "BLOQUEANTE",
            "categoria": "valores",
            "alcance": "Etapa 1 Vigente Editada",
            "validacion": "valores_monetarios_no_negativos_o_menos_uno",
            "campos": ["ARANCEL_ANUAL", "VALOR_MATRICULA_ANUAL", "COSTO_TITULACION", "VALOR_CERTIFICADO_DIPLOMA"],
            "regla_manual": "Arancel y valor matrícula deben ser >=0 o -1; costo titulación y certificado/diploma deben ser >=0.",
            "fuente_lineas": "1916, 1946, 1977-1978",
            "automatizable": True,
        },
        {
            "id": "OA1-017",
            "severidad": "BLOQUEANTE",
            "categoria": "fechas",
            "alcance": "Etapa 1 Vigente Editada",
            "validacion": "fecha_admision_inicial_rango",
            "campos": ["FECHA_ADMISION_INICIAL"],
            "regla_manual": "FECHA_ADMISION_INICIAL no puede ser anterior al 02/10/2025 ni posterior al 03/04/2026 o 04/04/2026 según regla extraída.",
            "fuente_lineas": "1992-2004",
            "automatizable": True,
        },
        {
            "id": "OA1-018",
            "severidad": "BLOQUEANTE",
            "categoria": "anio_inicio",
            "alcance": "Etapa 1 Vigente Editada",
            "validacion": "anio_inicio_no_posterior_2025",
            "campos": ["ANIO_INICIO"],
            "regla_manual": "ANIO_INICIO no puede ser posterior a 2025 para Oferta Académica Vigente Editada.",
            "fuente_lineas": "1931-1932",
            "automatizable": True,
        },
        {
            "id": "OA1-019",
            "severidad": "BLOQUEANTE",
            "categoria": "beneficios",
            "alcance": "Etapa 1 Vigente Editada",
            "validacion": "programas_protegidos_no_vigencia_3",
            "campos": ["VIGENCIA_CARRERA", "CANTIDAD_MATRICULA_DFE", "CANTIDAD_BENEFICIO_DFE"],
            "regla_manual": "No eliminar programas protegidos por matrícula o beneficio DFE; si no resulta posible dar de baja, usar vigencia 2.",
            "fuente_lineas": "553-567, 1735-1741",
            "automatizable": True,
        },
        {
            "id": "OA1-020",
            "severidad": "REVISION",
            "categoria": "estructura",
            "alcance": "Etapa 1 Vigente Editada",
            "validacion": "campos_malla_perfil_mencionados_no_presentes_en_estructura_48",
            "campos": ["MALLA_CURRICULAR", "PERFIL_EGRESO"],
            "regla_manual": "El bloque de errores menciona MALLA_CURRICULAR y PERFIL_EGRESO, pero la estructura PES Etapa 1 Vigente Editada descargada tiene 48 columnas y no contiene esos campos.",
            "fuente_lineas": "1895, 1897, estructura PES 20260810_34992",
            "automatizable": False,
        },
        {
            "id": "OA1-021",
            "severidad": "REVISION",
            "categoria": "correo_docencia",
            "alcance": "Entrega Docencia 02",
            "validacion": "revision_naranjo_rap_vacantes_online",
            "campos": ["VACANTES_PRIMER_SEMESTRE", "VACANTES_SEGUNDO_SEMESTRE", "VIGENCIA_CARRERA"],
            "regla_manual": "Correo de Docencia deja en naranjo carreras en actualización; RAP/vacantes online quedan pendientes de confirmación.",
            "fuente_lineas": "Nota gobernanza Entrega Docencia 02",
            "automatizable": True,
        },
    ]


def main() -> None:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    data = {
        "proceso": "SIES Oferta Academica-Acceso 2027",
        "etapa": "Etapa 1 - Oferta Academica Vigente Editada",
        "timestamp": ts,
        "fuente_manual": str(ROOT / "01_fuentes_oficiales" / "Instructivo_Oferta_Academica-Acceso_CFT-IP 2027.txt"),
        "nota": "Reglas extraidas del bloque de validaciones de Oferta Academica Vigente Editada y reglas operativas asociadas a Etapa 1.",
        "reglas": rules(),
    }

    json_path = OUT_DIR / "REGLAS_MANUAL_ETAPA1_OFERTA_ACADEMICA_2027.json"
    tsv_path = OUT_DIR / "REGLAS_MANUAL_ETAPA1_OFERTA_ACADEMICA_2027.tsv"
    md_path = OUT_DIR / "REGLAS_MANUAL_ETAPA1_OFERTA_ACADEMICA_2027.md"
    command_path = OUT_DIR / "VALIDAR_PREFINAL_ETAPA1_DOCENCIA02.command"

    json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    with tsv_path.open("w", encoding="utf-8", newline="") as f:
        fieldnames = ["id", "severidad", "categoria", "alcance", "validacion", "campos", "fuente_lineas", "automatizable", "regla_manual"]
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for rule in data["reglas"]:
            row = dict(rule)
            row["campos"] = ",".join(row["campos"]) if isinstance(row["campos"], list) else row["campos"]
            writer.writerow({key: row.get(key, "") for key in fieldnames})

    lines = [
        "# Reglas Manual Etapa 1 Oferta Académica 2027",
        "",
        "Fuente: Instructivo_Oferta_Academica-Acceso_CFT-IP 2027.txt",
        "",
        "| ID | Severidad | Categoría | Validación | Líneas | Regla |",
        "|---|---|---|---|---|---|",
    ]
    for rule in data["reglas"]:
        lines.append(
            f"| {rule['id']} | {rule['severidad']} | {rule['categoria']} | {rule['validacion']} | {rule['fuente_lineas']} | {rule['regla_manual']} |"
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    command_path.write_text(
        "#!/bin/zsh\n"
        "cd /Users/alexi/Documents/GitHub/avance_curricular\n"
        "python3 oferta_academica_2027/04_scripts/validar_prefinal_etapa1_reglas_manual.py\n",
        encoding="utf-8",
    )

    print(json.dumps({
        "json": str(json_path),
        "tsv": str(tsv_path),
        "md": str(md_path),
        "command": str(command_path),
        "reglas": len(data["reglas"]),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
