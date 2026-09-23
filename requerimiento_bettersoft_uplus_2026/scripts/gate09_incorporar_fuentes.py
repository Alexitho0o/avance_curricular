"""Gate 09: incorpora (copia) las fuentes faltantes del requerimiento Bettersoft U+.

No mueve ni modifica originales. Copia con shutil.copy2 y registra SHA-256 de origen y
destino. Los archivos con datos personales van a .local_restricted/ (excluido de Git por
.git/info/exclude), según avance_curricular_2026/01_documentacion/POLITICA_DATOS_Y_GIT.md.
Los ya gobernados en el repositorio o excluidos por política se registran como REFERENCIADO.
"""
import csv
import hashlib
import shutil
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SUB = REPO / "requerimiento_bettersoft_uplus_2026"
OFI = SUB / "01_fuentes_oficiales"
ENV = SUB / "02_evidencia_envios_sin_datos_personales"
RES = REPO / ".local_restricted" / "requerimiento_bettersoft_uplus_2026" / "gate09_evidencia"
ENVIADOS = Path.home() / (
    "Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/"
    "Datos DAI (RAW) - 1.1 Datos crudos/1.2.1 Datos Institucionales/1.2.1.1 SIES/Enviados"
)
TEAMS = Path.home() / "Library/CloudStorage/OneDrive-InstitutoProfesionalSanSebastián/Archivos de chat de Microsoft Teams"

# (rol, proceso, anio_proceso, nivel, tipo_fuente, datos_personales, origen, destino_base | None)
FUENTES = [
    ("Instructivo oficial", "avance_curricular_2026", "2026", 1, "Instructivo SIES", "NO",
     ENVIADOS / "Avance Curricular/2026/Instructivo_Avance Curricular SIES - 2026.pdf", OFI),
    ("Instructivo oficial (texto extraído)", "avance_curricular_2026", "2026", 1, "Instructivo SIES", "NO",
     ENVIADOS / "Avance Curricular/2026/Instructivo_Avance Curricular SIES - 2026.txt", OFI),
    ("Precarga PES carreras (ID 16769, rep. 5810)", "avance_curricular_2026", "2026", 3, "Precarga PES", "NO",
     ENVIADOS / "Avance Curricular/2026/5810_Precarga Carreras Avance Curricular 20268.csv", OFI),
    ("Instructivo oficial", "estudiantes_extranjeros_2026", "2026", 1, "Instructivo SIES", "NO",
     ENVIADOS / "Matricula Extranjeros/2026/Instructivo _Estudiantes_Extranjeros_SIES.pdf", OFI),
    ("Instructivo oficial (texto extraído)", "estudiantes_extranjeros_2026", "2026", 1, "Instructivo SIES", "NO",
     ENVIADOS / "Matricula Extranjeros/2026/Instructivo _Estudiantes_Extranjeros_SIES.txt", OFI),
    ("Estructura PES Extranjeros Regulares (solo encabezado)", "estudiantes_extranjeros_2026", "2026", 3, "Plantilla PES", "NO",
     ENVIADOS / "Matricula Extranjeros/2026/20260602_97636_Estructura_Extranjeros_Regulares_2025.csv", OFI),
    ("Reporte PES carreras para Extranjeros (rep. 5769)", "estudiantes_extranjeros_2026", "2026", 3, "Precarga PES", "NO",
     ENVIADOS / "Matricula Extranjeros/2026/5769 Reporte Carreras para Extranjeros 2025.csv", OFI),
    ("Estructura PES Oferta TP Vigente Editada (solo encabezado)", "oferta_academica_2027", "2026", 3, "Plantilla PES", "NO",
     ENVIADOS / "Oferta académica/2027/dctos/20260810_34992_Estructura_OA_1_TP_VIGENTE_EDITADA.csv", OFI),
    ("Estructura PES Oferta TP Nueva (solo encabezado)", "oferta_academica_2027", "2026", 3, "Plantilla PES", "NO",
     ENVIADOS / "Oferta académica/2027/dctos/20260810_63945_Estructura_OA_1_TP_NUEVA.csv", OFI),
    ("Archivo enviado Carreras AC (ID 16769)", "avance_curricular_2026", "2026", 4, "Archivo enviado", "NO",
     ENVIADOS / "Avance Curricular/2026/Carreras Avance Curricular 2026/5810_CARRERAS_AVANCE_CURRICULAR_2026_SUBIR_SIES_ID_16769_21C_H112B_CONTROLADO.csv", ENV),
    # Con datos personales -> .local_restricted
    ("Archivo cargado en PES (copia _orig devuelta por plataforma) 08-05-2026", "matricula_unificada_2026", "2026", 4, "Archivo enviado", "SI",
     ENVIADOS / "Matrícula Unificada/2026/CUARTA SUBIDA FINAL/08-05-2026_23-21-16_Matrícula-Pregrado-2026.csv_orig.zip", RES),
    ("Archivo cargado en PES (copia _orig) complemento 95, 11-05-2026", "matricula_unificada_2026", "2026", 4, "Archivo enviado", "SI",
     ENVIADOS / "Matrícula Unificada/2026/QUINTA SUBIDA +95/11-05-2026_12-12-47_Matrícula-Pregrado-2026.csv_orig.zip", RES),
    ("Respuesta de errores PES 07-05-2026 12:19 (SIT_FON_SOL, AÑO ORIGEN 1900)", "matricula_unificada_2026", "2026", 4, "Respuesta plataforma PES", "SI",
     ENVIADOS / "Matrícula Unificada/2026/TERCERA CARGA 7-5 A LAS 1 DE LA TARDE/ERRORES/07-05-2026_12-19-13_Matrícula-Pregrado-2026.csv.txt", RES),
    ("Respuesta de errores PES 07-05-2026 12:26 (fecha de nacimiento, largo RUT)", "matricula_unificada_2026", "2026", 4, "Respuesta plataforma PES", "SI",
     ENVIADOS / "Matrícula Unificada/2026/TERCERA CARGA 7-5 A LAS 1 DE LA TARDE/ERRORES/07-05-2026_12-26-55_Matrícula-Pregrado-2026.csv.txt", RES),
    ("Respuesta de errores PES 11-05-2026 11:30 (continuidad, nivel)", "matricula_unificada_2026", "2026", 4, "Respuesta plataforma PES", "SI",
     ENVIADOS / "Matrícula Unificada/2026/QUINTA SUBIDA +95/PROBLEMAS/11-05-2026_11-30-39_Matrícula-Pregrado-2026.csv.txt", RES),
    ("Precarga PES matrícula AC (ID 16768, rep. 5809)", "avance_curricular_2026", "2026", 3, "Precarga PES", "SI",
     ENVIADOS / "Avance Curricular/2026/5809_Precarga Matrícula Avance Curricular 2026.csv", RES),
    ("Archivo enviado Matrícula AC (ID 16768) H114B", "avance_curricular_2026", "2026", 4, "Archivo enviado", "SI",
     ENVIADOS / "Avance Curricular/2026/5809_MATRICULA_AVANCE_CURRICULAR_2026_SUBIR_SIES_ID_16768_H114B_CORREGIDO_PLAN.csv", RES),
    ("Precarga PES Extranjeros Regulares (rep. 5768)", "estudiantes_extranjeros_2026", "2026", 3, "Precarga PES", "SI",
     ENVIADOS / "Matricula Extranjeros/2026/5768 Reporte Precarga del Proceso Extranjeros Regulares 2026.csv", RES),
    ("Archivo enviado Extranjeros Regulares, 1ª carga (PES_READY 26-06-2026)", "estudiantes_extranjeros_2026", "2026", 4, "Archivo enviado", "SI",
     TEAMS / "EXTRANJEROS_REGULARES_2025_PES_READY_RESIDENCIA_0_20260626_121728.csv", RES),
    ("Archivo enviado Extranjeros Regulares, 2ª carga (104 registros)", "estudiantes_extranjeros_2026", "2026", 4, "Archivo enviado", "SI",
     ENVIADOS / "Matricula Extranjeros/2026/SEGUNDA SUBIDA/FINAL_SUBIR_SIES_EXTRANJEROS_REGULARES_2025_104_VIGENCIA_0_FECHA_CORREGIDA.csv", RES),
    ("Archivo enviado Extranjeros Regulares, 3ª carga (14 registros)", "estudiantes_extranjeros_2026", "2026", 4, "Archivo enviado", "SI",
     ENVIADOS / "Matricula Extranjeros/2026/3RA CARGA/SOLO_14_NACIONALIDAD_38_VIGENCIA_0_EXTRANJEROS_REGULARES_2025.csv", RES),
    ("Archivo enviado FCU 2026 P1", "fcu_2026", "2026", 4, "Archivo enviado", "SI",
     ENVIADOS / "FCU/2026/FCU_2026_CARGA_2026_P1_20260505_LISTO_SIN_TITULOS_PES_FINAL.csv", RES),
    # Referenciados (no se copian)
    ("Archivo final MU 2026 consolidado (= FINAL_4105.csv ya en repositorio)", "matricula_unificada_2026", "2026", 4, "Archivo enviado", "SI",
     ENVIADOS / "Matrícula Unificada/2026/REPORTE JULIO 2026/MATRICULA_UNIFICADA_PREGRADO_2026_CONSOLIDADA_FINAL.csv", None),
    ("Snapshot U+ usado en la carga MU 2026 (hoja DatosAlumnos); excluido de Git por política", "matricula_unificada_2026", "2026", 5, "Fuente institucional", "SI",
     ENVIADOS / "Matrícula Unificada/2026/QUINTA SUBIDA +95/PROMEDIOSDEALUMNOS_7804.xlsx", None),
    ("Manual FCU 2026 (texto)", "fcu_2026", "2026", 1, "Manual SIES", "NO",
     ENVIADOS / "FCU/2026/Manual_de_Aplicacion_FCU_2026.txt", None),
]


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    fecha = datetime.now().isoformat(timespec="seconds")
    filas = []
    for rol, proceso, anio, nivel, tipo, personal, origen, base in FUENTES:
        fila = dict(rol=rol, proceso=proceso, anio_proceso=anio, nivel_jerarquia=nivel, tipo_fuente=tipo,
                    datos_personales=personal, archivo=origen.name, ruta_origen=str(origen), ruta_destino="",
                    bytes="", fecha_modificacion_origen="", sha256_origen="", sha256_destino="",
                    fecha_incorporacion=fecha, estado="")
        if not origen.exists():
            fila["estado"] = "BLOQUEO_ORIGEN_NO_ENCONTRADO"
            filas.append(fila)
            continue
        st = origen.stat()
        fila.update(bytes=st.st_size, fecha_modificacion_origen=datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds"),
                    sha256_origen=sha256(origen))
        if base is None:
            fila["estado"] = "REFERENCIADO_SIN_COPIA"
        else:
            destino = base / proceso / origen.name
            destino.parent.mkdir(parents=True, exist_ok=True)
            if not destino.exists():
                shutil.copy2(origen, destino)
            fila["ruta_destino"] = str(destino.relative_to(REPO))
            fila["sha256_destino"] = sha256(destino)
            fila["estado"] = "COPIADO" if fila["sha256_destino"] == fila["sha256_origen"] else "BLOQUEO_CHECKSUM_DISTINTO"
        filas.append(fila)
    OFI.mkdir(parents=True, exist_ok=True)
    out = OFI / "MANIFIESTO_FUENTES_GATE09.tsv"
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0].keys()), delimiter="\t")
        w.writeheader()
        w.writerows(filas)
    for fila in filas:
        print(fila["estado"], "|", fila["proceso"], "|", fila["archivo"])
    print("MANIFIESTO:", out)


if __name__ == "__main__":
    main()
