from __future__ import annotations

from datetime import datetime
from pathlib import Path
import gc
import hashlib
import importlib.util
import json
import sys
import time

import pandas as pd


RAIZ = Path("/Users/alexi/Documents/GitHub/avance_curricular")
SCRIPT_PRINCIPAL = RAIZ / "scripts" / "consolidar_mu2026_por_codcli.py"

CARPETA_RECONSTRUIDA = (
    RAIZ
    / "resultados"
    / "auditoria_multicodcli_mu2026_reconstruida_desde_cero"
)

SALIDA_DIR = (
    CARPETA_RECONSTRUIDA
    / "03_archivos_rectificacion"
    / "consolidacion_codcli"
)

CATALOGO_PARQUET = SALIDA_DIR / "CATALOGO_CODCLI_COMPLETO.parquet"
CATALOGO_CSV_GZ = SALIDA_DIR / "CATALOGO_CODCLI_COMPLETO.csv.gz"
MANIFIESTO_CATALOGO = SALIDA_DIR / "MANIFIESTO_CATALOGO_CODCLI.json"
INVENTARIO_CATALOGO = (
    SALIDA_DIR / "INVENTARIO_FUENTES_CATALOGO_CODCLI.csv"
)
RESUMEN_EXCEL = (
    SALIDA_DIR / "RESUMEN_PERSISTENCIA_CATALOGO_CODCLI.xlsx"
)
LOG_FASE1 = SALIDA_DIR / "LOG_FASE1_PERSISTENCIA_CATALOGO_CODCLI.txt"
ESTADO_FASE1 = (
    SALIDA_DIR / "ESTADO_FASE1_PERSISTENCIA_CATALOGO_CODCLI.txt"
)
CONFLICTOS_RECUPERADOS = SALIDA_DIR / "CONFLICTOS_ASIGNACION_CODCLI.xlsx"

COLUMNAS_REQUERIDAS_CATALOGO = [
    "CODCLI",
    "RUT_NORM",
    "OFERTA_SIES",
    "ARCHIVO_CODCLI",
    "HOJA_CODCLI",
    "FILA_CODCLI",
    "COLUMNA_CODCLI",
    "COLUMNA_RUT",
    "COLUMNA_OFERTA",
]

MAX_FILAS_EXCEL = 1_048_576
MAX_COLUMNAS_EXCEL = 16_384

MENSAJES_LOG: list[str] = []


def log(texto: str = "") -> None:
    texto = str(texto)
    print(texto, flush=True)
    MENSAJES_LOG.append(texto)
    try:
        SALIDA_DIR.mkdir(parents=True, exist_ok=True)
        LOG_FASE1.write_text(
            "\n".join(MENSAJES_LOG) + "\n",
            encoding="utf-8",
        )
    except Exception:
        pass


def sha256(ruta: Path) -> str:
    h = hashlib.sha256()
    with ruta.open("rb") as archivo:
        for bloque in iter(lambda: archivo.read(1024 * 1024), b""):
            h.update(bloque)
    return h.hexdigest()


def cargar_nucleo_script_principal() -> dict:
    texto = SCRIPT_PRINCIPAL.read_text(encoding="utf-8")
    marcador = "# INICIO"
    posicion = texto.find(marcador)
    if posicion == -1:
        raise RuntimeError(
            "No se encontro el marcador '# INICIO' en el script principal."
        )

    prefijo = texto[:posicion]
    espacio: dict = {
        "__file__": str(SCRIPT_PRINCIPAL),
        "__name__": "fase1_core_consolidar_mu2026",
    }
    exec(compile(prefijo, str(SCRIPT_PRINCIPAL), "exec"), espacio)
    espacio["log"] = log
    espacio["MENSAJES_LOG"] = MENSAJES_LOG
    return espacio


def formato_catalogo_preferido() -> tuple[str, Path]:
    if importlib.util.find_spec("pyarrow") is not None:
        return "parquet", CATALOGO_PARQUET
    if importlib.util.find_spec("fastparquet") is not None:
        return "parquet", CATALOGO_PARQUET
    return "csv_gzip", CATALOGO_CSV_GZ


def normalizar_catalogo_para_persistencia(df: pd.DataFrame) -> pd.DataFrame:
    catalogo = df.copy()

    for columna in catalogo.columns:
        catalogo[columna] = (
            catalogo[columna]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    return catalogo.reset_index(drop=True)


def metricas_catalogo(df: pd.DataFrame) -> dict:
    return {
        "filas": int(len(df)),
        "columnas": int(df.shape[1]),
        "nombres_columnas": list(df.columns),
        "codcli_distintos": int(df["CODCLI"].nunique()),
        "rut_distintos": int(
            df.loc[df["RUT_NORM"].ne(""), "RUT_NORM"].nunique()
        ),
        "ofertas_distintas": int(
            df.loc[df["OFERTA_SIES"].ne(""), "OFERTA_SIES"].nunique()
        ),
        "duplicados_fila_completa": int(df.duplicated().sum()),
    }


def guardar_catalogo(df: pd.DataFrame, formato: str, ruta: Path) -> None:
    tmp = Path(str(ruta) + ".tmp")
    if tmp.exists():
        tmp.unlink()

    if formato == "parquet":
        df.to_parquet(tmp, index=False)
    elif formato == "csv_gzip":
        df.to_csv(
            tmp,
            sep=";",
            index=False,
            encoding="utf-8",
            compression="gzip",
            lineterminator="\n",
        )
    else:
        raise ValueError(f"Formato no soportado: {formato}")

    tmp.replace(ruta)


def cargar_catalogo(ruta: Path, formato: str) -> pd.DataFrame:
    if formato == "parquet":
        df = pd.read_parquet(ruta)
    elif formato == "csv_gzip":
        df = pd.read_csv(
            ruta,
            sep=";",
            dtype=str,
            encoding="utf-8",
            compression="gzip",
            keep_default_na=False,
            na_filter=False,
            low_memory=False,
        )
    else:
        raise ValueError(f"Formato no soportado: {formato}")

    return normalizar_catalogo_para_persistencia(df)


def diferencias_dataframe(a: pd.DataFrame, b: pd.DataFrame) -> int:
    if list(a.columns) != list(b.columns):
        return -1
    if a.shape != b.shape:
        return -1
    return int((a.ne(b)).to_numpy().sum())


def cargar_manifiesto() -> tuple[dict | None, str]:
    if not MANIFIESTO_CATALOGO.exists():
        return None, "NO_EXISTE_MANIFIESTO"

    try:
        return (
            json.loads(MANIFIESTO_CATALOGO.read_text(encoding="utf-8")),
            "OK",
        )
    except Exception as exc:
        return None, f"MANIFIESTO_ILEGIBLE: {type(exc).__name__}: {exc}"


def validar_catalogo_persistido(
    cargar_datos: bool = True,
) -> tuple[bool, pd.DataFrame | None, dict]:
    inicio = time.perf_counter()
    manifiesto, estado_manifiesto = cargar_manifiesto()

    validacion: dict = {
        "estado_manifiesto": estado_manifiesto,
        "catalogo_leido": False,
        "hash_validado": False,
        "metricas_validadas": False,
        "columnas_requeridas_validadas": False,
        "formato_compatible": False,
        "estado": "INVALIDO",
        "motivos": [],
    }

    if manifiesto is None:
        validacion["motivos"].append(estado_manifiesto)
        validacion["tiempo_validacion_segundos"] = round(
            time.perf_counter() - inicio,
            3,
        )
        return False, None, validacion

    catalogo_info = manifiesto.get("catalogo", {})
    formato = catalogo_info.get("formato", "")
    ruta_catalogo = Path(catalogo_info.get("ruta", ""))

    if formato not in {"parquet", "csv_gzip"}:
        validacion["motivos"].append("FORMATO_NO_COMPATIBLE")
        validacion["tiempo_validacion_segundos"] = round(
            time.perf_counter() - inicio,
            3,
        )
        return False, None, validacion

    validacion["formato_compatible"] = True

    if not ruta_catalogo.exists():
        validacion["motivos"].append("NO_EXISTE_CATALOGO")
        validacion["tiempo_validacion_segundos"] = round(
            time.perf_counter() - inicio,
            3,
        )
        return False, None, validacion

    hash_real = sha256(ruta_catalogo)
    hash_esperado = catalogo_info.get("sha256", "")
    validacion["hash_real"] = hash_real
    validacion["hash_esperado"] = hash_esperado

    if hash_real != hash_esperado:
        validacion["motivos"].append("HASH_NO_COINCIDE")
        validacion["tiempo_validacion_segundos"] = round(
            time.perf_counter() - inicio,
            3,
        )
        return False, None, validacion

    validacion["hash_validado"] = True

    try:
        catalogo = cargar_catalogo(ruta_catalogo, formato)
        validacion["catalogo_leido"] = True
    except Exception as exc:
        validacion["motivos"].append(
            f"LECTURA_FALLIDA: {type(exc).__name__}: {exc}"
        )
        validacion["tiempo_validacion_segundos"] = round(
            time.perf_counter() - inicio,
            3,
        )
        return False, None, validacion

    faltantes = [
        columna
        for columna in COLUMNAS_REQUERIDAS_CATALOGO
        if columna not in catalogo.columns
    ]
    if faltantes:
        validacion["motivos"].append(
            "COLUMNAS_REQUERIDAS_FALTANTES: " + ",".join(faltantes)
        )
        validacion["tiempo_validacion_segundos"] = round(
            time.perf_counter() - inicio,
            3,
        )
        return False, None, validacion

    validacion["columnas_requeridas_validadas"] = True

    metricas_reales = metricas_catalogo(catalogo)
    metricas_esperadas = manifiesto.get("metricas", {})
    validacion["metricas_reales"] = metricas_reales
    validacion["metricas_esperadas"] = metricas_esperadas

    claves_metricas = [
        "filas",
        "columnas",
        "nombres_columnas",
        "codcli_distintos",
        "rut_distintos",
        "ofertas_distintas",
    ]
    diferencias = [
        clave
        for clave in claves_metricas
        if metricas_reales.get(clave) != metricas_esperadas.get(clave)
    ]

    if diferencias:
        validacion["motivos"].append(
            "METRICAS_NO_COINCIDEN: " + ",".join(diferencias)
        )
        validacion["tiempo_validacion_segundos"] = round(
            time.perf_counter() - inicio,
            3,
        )
        return False, None, validacion

    validacion["metricas_validadas"] = True
    validacion["estado"] = "VALIDO"
    validacion["motivos"] = []
    validacion["tiempo_validacion_segundos"] = round(
        time.perf_counter() - inicio,
        3,
    )

    if cargar_datos:
        return True, catalogo, validacion

    del catalogo
    gc.collect()
    return True, None, validacion


def metadatos_fuentes(fuentes: list[Path]) -> list[dict]:
    registros = []
    for numero, ruta in enumerate(fuentes, start=1):
        stat = ruta.stat()
        registros.append(
            {
                "numero": numero,
                "ruta": str(ruta),
                "sufijo": ruta.suffix.lower(),
                "bytes": int(stat.st_size),
                "mtime_ns": int(stat.st_mtime_ns),
            }
        )
    return registros


def escribir_estado(contenido: dict) -> None:
    lineas = []
    for clave, valor in contenido.items():
        lineas.append(f"{clave}: {valor}")
    ESTADO_FASE1.write_text("\n".join(lineas) + "\n", encoding="utf-8")


def tabla_dict(datos: dict, prefijo: str = "") -> pd.DataFrame:
    filas = []

    def visitar(valor, ruta: str) -> None:
        if isinstance(valor, dict):
            for subclave, subvalor in valor.items():
                visitar(subvalor, f"{ruta}.{subclave}" if ruta else subclave)
        elif isinstance(valor, list):
            filas.append(
                {
                    "CAMPO": ruta,
                    "VALOR": f"[lista con {len(valor)} elementos]",
                }
            )
        else:
            filas.append({"CAMPO": ruta, "VALOR": valor})

    visitar(datos, prefijo)
    return pd.DataFrame(filas)


def escribir_hoja_segura(
    writer: pd.ExcelWriter,
    df: pd.DataFrame,
    nombre_hoja: str,
    referencia: str,
) -> None:
    if df.shape[0] <= MAX_FILAS_EXCEL and df.shape[1] <= MAX_COLUMNAS_EXCEL:
        df.to_excel(writer, sheet_name=nombre_hoja, index=False)
        return

    pd.DataFrame(
        [
            {
                "HOJA_SOLICITADA": nombre_hoja,
                "FILAS": int(df.shape[0]),
                "COLUMNAS": int(df.shape[1]),
                "RESULTADO": "NO_ESCRITA_SUPERA_LIMITE_EXCEL",
                "REFERENCIA": referencia,
            }
        ]
    ).to_excel(writer, sheet_name=nombre_hoja[:31], index=False)


def leer_conflictos_recuperados() -> pd.DataFrame:
    if not CONFLICTOS_RECUPERADOS.exists():
        return pd.DataFrame()

    try:
        return pd.read_excel(
            CONFLICTOS_RECUPERADOS,
            sheet_name="CONFLICTOS",
            dtype=str,
            engine="openpyxl",
        ).fillna("")
    except Exception as exc:
        return pd.DataFrame(
            [
                {
                    "ERROR": (
                        "No fue posible leer conflictos recuperados: "
                        f"{type(exc).__name__}: {exc}"
                    )
                }
            ]
        )


def construir_subconjunto_relevante(
    core: dict,
    catalogo: pd.DataFrame,
) -> pd.DataFrame:
    leer_csv_32 = core["leer_csv_32"]
    archivo_95 = (
        RAIZ
        / "control"
        / "auditoria_mu2026_punto0_complemento95"
        / "archivos_congelados"
        / "complemento_95"
        / "matricula_unificada_2026_COMPLEMENTO_95_CODCLI_PARA_SUBIR.csv"
    )
    archivo_30 = (
        CARPETA_RECONSTRUIDA
        / "03_archivos_rectificacion"
        / "RECTIFICACION_MU2026_RECONSTRUIDA_DESDE_CERO.csv"
    )

    df_95, _ = leer_csv_32(archivo_95)
    df_30, _ = leer_csv_32(archivo_30)

    ruts = set(df_95["RUT_NORM"].astype(str)) | set(
        df_30["RUT_NORM"].astype(str)
    )
    ruts.discard("")

    ofertas = set(df_95["OFERTA_SIES"].astype(str)) | set(
        df_30["OFERTA_SIES"].astype(str)
    )
    ofertas.discard("")

    subconjunto = catalogo.loc[
        catalogo["RUT_NORM"].isin(ruts)
        | (
            catalogo["RUT_NORM"].ne("")
            & catalogo["OFERTA_SIES"].isin(ofertas)
        )
    ].copy()

    subconjunto.insert(0, "SUBCONJUNTO", "RUT_95_30_O_OFERTA_RELACIONADA")
    return subconjunto


def escribir_resumen_excel(
    resumen: dict,
    inventario: pd.DataFrame,
    subconjunto: pd.DataFrame,
    conflictos: pd.DataFrame,
) -> None:
    referencias = pd.DataFrame(
        [
            {"TIPO": "CATALOGO", "RUTA": resumen["catalogo"]["ruta"]},
            {"TIPO": "MANIFIESTO", "RUTA": str(MANIFIESTO_CATALOGO)},
            {"TIPO": "INVENTARIO", "RUTA": str(INVENTARIO_CATALOGO)},
            {"TIPO": "LOG", "RUTA": str(LOG_FASE1)},
            {"TIPO": "ESTADO", "RUTA": str(ESTADO_FASE1)},
            {
                "TIPO": "CONFLICTOS_RECUPERADOS",
                "RUTA": str(CONFLICTOS_RECUPERADOS),
            },
        ]
    )

    with pd.ExcelWriter(RESUMEN_EXCEL, engine="openpyxl") as writer:
        tabla_dict(resumen).to_excel(
            writer,
            sheet_name="00_RESUMEN",
            index=False,
        )
        referencias.to_excel(
            writer,
            sheet_name="01_REFERENCIAS",
            index=False,
        )
        escribir_hoja_segura(
            writer,
            inventario,
            "02_INVENTARIO",
            str(INVENTARIO_CATALOGO),
        )
        escribir_hoja_segura(
            writer,
            subconjunto,
            "03_SUBCONJUNTO_95_30",
            str(MANIFIESTO_CATALOGO),
        )
        escribir_hoja_segura(
            writer,
            conflictos,
            "04_CONFLICTOS_RECUPERADOS",
            str(CONFLICTOS_RECUPERADOS),
        )


def main() -> int:
    inicio_total = time.perf_counter()
    inicio_iso = datetime.now().isoformat(timespec="seconds")

    SALIDA_DIR.mkdir(parents=True, exist_ok=True)
    if LOG_FASE1.exists():
        LOG_FASE1.unlink()

    log("=" * 100)
    log("FASE 1 - PERSISTENCIA DEL CATALOGO CODCLI")
    log("=" * 100)
    log(f"Inicio: {inicio_iso}")
    log(f"Repositorio: {RAIZ}")
    log(f"Script principal: {SCRIPT_PRINCIPAL}")

    formato_preferido, ruta_catalogo_preferida = formato_catalogo_preferido()
    log(f"Formato preferido disponible: {formato_preferido}")
    log(f"Ruta esperada catalogo: {ruta_catalogo_preferida}")

    core = cargar_nucleo_script_principal()

    valido_inicial, catalogo, validacion_inicial = validar_catalogo_persistido(
        cargar_datos=True
    )
    construido_en_esta_ejecucion = False
    diferencias_memoria_relectura = None
    tiempo_construccion = 0.0
    tiempo_recarga = 0.0
    fuentes_codcli: list[Path] = []
    inventario_fuentes = pd.DataFrame()

    if valido_inicial and catalogo is not None:
        log("Catalogo persistido valido detectado.")
        log("No se recorrera nuevamente el universo de fuentes CODCLI.")
        manifiesto = json.loads(
            MANIFIESTO_CATALOGO.read_text(encoding="utf-8")
        )
        formato = manifiesto["catalogo"]["formato"]
        ruta_catalogo = Path(manifiesto["catalogo"]["ruta"])
        tiempo_recarga = validacion_inicial["tiempo_validacion_segundos"]

        if INVENTARIO_CATALOGO.exists():
            inventario_fuentes = pd.read_csv(
                INVENTARIO_CATALOGO,
                sep=";",
                dtype=str,
                encoding="utf-8",
                keep_default_na=False,
                na_filter=False,
                low_memory=False,
            )
    else:
        log(
            "No existe catalogo persistido valido. "
            "Se construira una vez con la metodologia actual."
        )
        log(
            "Motivos validacion inicial: "
            + " | ".join(validacion_inicial.get("motivos", []))
        )

        formato, ruta_catalogo = formato_preferido, ruta_catalogo_preferida

        log("Descubriendo fuentes activas para reconstruir CODCLI...")
        fuentes_codcli = core["descubrir_fuentes_codcli"]()
        log(f"Archivos candidatos para catalogo CODCLI: {len(fuentes_codcli)}")

        t0 = time.perf_counter()
        catalogo, inventario_fuentes = core["construir_catalogo_codcli"](
            fuentes_codcli
        )
        tiempo_construccion = round(time.perf_counter() - t0, 3)
        construido_en_esta_ejecucion = True

        catalogo = normalizar_catalogo_para_persistencia(catalogo)
        inventario_fuentes = normalizar_catalogo_para_persistencia(
            inventario_fuentes
        )

        log(f"Registros de evidencia CODCLI encontrados: {len(catalogo)}")
        log(f"CODCLI distintos en catalogo: {catalogo['CODCLI'].nunique()}")
        log(
            "RUT distintos con evidencia CODCLI: "
            f"{catalogo.loc[catalogo['RUT_NORM'].ne(''), 'RUT_NORM'].nunique()}"
        )

        log(f"Persistiendo catalogo completo como {formato}...")
        guardar_catalogo(catalogo, formato, ruta_catalogo)
        hash_catalogo = sha256(ruta_catalogo)
        metricas = metricas_catalogo(catalogo)

        inventario_fuentes.to_csv(
            INVENTARIO_CATALOGO,
            sep=";",
            index=False,
            encoding="utf-8",
            lineterminator="\n",
        )

        metadata = metadatos_fuentes(fuentes_codcli)
        rutas_con_codcli = sorted(
            inventario_fuentes.loc[
                inventario_fuentes["TIENE_CODCLI"].eq("SI"),
                "ARCHIVO",
            ]
            .drop_duplicates()
            .astype(str)
            .tolist()
        )

        manifiesto = {
            "fase": "FASE1_PERSISTENCIA_CATALOGO_CODCLI",
            "creado_en": datetime.now().isoformat(timespec="seconds"),
            "script_creador": str(Path(__file__).resolve()),
            "script_creador_sha256": sha256(Path(__file__).resolve()),
            "script_principal": str(SCRIPT_PRINCIPAL),
            "script_principal_sha256": sha256(SCRIPT_PRINCIPAL),
            "catalogo": {
                "ruta": str(ruta_catalogo),
                "formato": formato,
                "sha256": hash_catalogo,
                "bytes": int(ruta_catalogo.stat().st_size),
            },
            "metricas": metricas,
            "fuentes": {
                "cantidad_fuentes_revisadas": len(fuentes_codcli),
                "cantidad_fuentes_con_codcli": len(rutas_con_codcli),
                "rutas_fuentes_revisadas": [
                    str(ruta) for ruta in fuentes_codcli
                ],
                "rutas_fuentes_con_codcli": rutas_con_codcli,
                "metadatos_fuentes_revisadas": metadata,
            },
            "inventario": {
                "ruta": str(INVENTARIO_CATALOGO),
                "filas": int(len(inventario_fuentes)),
                "columnas": int(inventario_fuentes.shape[1]),
                "sha256": sha256(INVENTARIO_CATALOGO),
            },
            "validacion": {
                "estado": "PENDIENTE_RELECTURA",
            },
        }

        MANIFIESTO_CATALOGO.write_text(
            json.dumps(manifiesto, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        log("Releyendo catalogo persistido para comparacion fisica...")
        t1 = time.perf_counter()
        catalogo_releido = cargar_catalogo(ruta_catalogo, formato)
        tiempo_recarga = round(time.perf_counter() - t1, 3)
        diferencias_memoria_relectura = diferencias_dataframe(
            catalogo,
            catalogo_releido,
        )

        if diferencias_memoria_relectura != 0:
            raise RuntimeError(
                "La comparacion memoria vs relectura no dio cero "
                f"diferencias: {diferencias_memoria_relectura}"
            )

        validacion_ok, _, validacion_relectura = validar_catalogo_persistido(
            cargar_datos=False
        )
        if not validacion_ok:
            raise RuntimeError(
                "El catalogo persistido no paso validacion posterior: "
                + " | ".join(validacion_relectura.get("motivos", []))
            )

        manifiesto["validacion"] = {
            "estado": "VALIDO",
            "diferencias_memoria_relectura": diferencias_memoria_relectura,
            "validacion_relectura": validacion_relectura,
        }
        MANIFIESTO_CATALOGO.write_text(
            json.dumps(manifiesto, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        del catalogo_releido
        gc.collect()

    log("Preparando resumen auditable de Fase 1...")

    if catalogo is None:
        raise RuntimeError("Catalogo no disponible para resumen auditable.")

    resumen_metricas = metricas_catalogo(catalogo)
    catalogo_info = {
        "ruta": str(ruta_catalogo),
        "formato": formato,
        "sha256": sha256(ruta_catalogo),
        "bytes": int(ruta_catalogo.stat().st_size),
    }

    subconjunto = construir_subconjunto_relevante(core, catalogo)
    conflictos = leer_conflictos_recuperados()

    resumen = {
        "fase": "FASE1_PERSISTENCIA_CATALOGO_CODCLI",
        "inicio": inicio_iso,
        "fin": datetime.now().isoformat(timespec="seconds"),
        "catalogo": catalogo_info,
        "metricas": resumen_metricas,
        "fuentes_revisadas": (
            len(fuentes_codcli)
            if fuentes_codcli
            else json.loads(
                MANIFIESTO_CATALOGO.read_text(encoding="utf-8")
            )
            .get("fuentes", {})
            .get("cantidad_fuentes_revisadas", "")
        ),
        "inventario": {
            "ruta": str(INVENTARIO_CATALOGO),
            "filas": int(len(inventario_fuentes)),
            "columnas": int(inventario_fuentes.shape[1])
            if not inventario_fuentes.empty
            else 0,
        },
        "subconjunto_95_30": {
            "filas": int(len(subconjunto)),
            "columnas": int(subconjunto.shape[1]),
        },
        "conflictos_recuperados": {
            "filas": int(len(conflictos)),
            "columnas": int(conflictos.shape[1]),
        },
        "ejecucion": {
            "construido_en_esta_ejecucion": construido_en_esta_ejecucion,
            "tiempo_construccion_segundos": tiempo_construccion,
            "tiempo_recarga_segundos": tiempo_recarga,
            "diferencias_memoria_relectura": diferencias_memoria_relectura
            if diferencias_memoria_relectura is not None
            else "NO_APLICA_CATALOGO_REUTILIZADO",
            "estado_validacion_inicial": validacion_inicial["estado"],
        },
    }

    escribir_resumen_excel(
        resumen,
        inventario_fuentes,
        subconjunto,
        conflictos,
    )

    log("Cerrando referencias en memoria para prueba de reutilizacion...")
    del catalogo
    del subconjunto
    gc.collect()

    log(
        "Prueba de reutilizacion: validacion directa desde manifiesto "
        "y catalogo persistido."
    )
    t2 = time.perf_counter()
    valido_reuso, catalogo_reuso, validacion_reuso = (
        validar_catalogo_persistido(cargar_datos=True)
    )
    tiempo_reuso = round(time.perf_counter() - t2, 3)

    if not valido_reuso or catalogo_reuso is None:
        raise RuntimeError(
            "Prueba de reutilizacion fallida: "
            + " | ".join(validacion_reuso.get("motivos", []))
        )

    metricas_reuso = metricas_catalogo(catalogo_reuso)
    del catalogo_reuso
    gc.collect()

    estado_final = {
        "estado": "FASE1_COMPLETADA_CATALOGO_VALIDO_REUTILIZABLE",
        "formato": catalogo_info["formato"],
        "ruta_catalogo": catalogo_info["ruta"],
        "sha256": catalogo_info["sha256"],
        "bytes": catalogo_info["bytes"],
        "filas": metricas_reuso["filas"],
        "columnas": metricas_reuso["columnas"],
        "codcli_distintos": metricas_reuso["codcli_distintos"],
        "rut_distintos": metricas_reuso["rut_distintos"],
        "ofertas_distintas": metricas_reuso["ofertas_distintas"],
        "fuentes_revisadas": resumen["fuentes_revisadas"],
        "diferencias_memoria_relectura": resumen["ejecucion"][
            "diferencias_memoria_relectura"
        ],
        "tiempo_construccion_segundos": tiempo_construccion,
        "tiempo_recarga_segundos": tiempo_recarga,
        "tiempo_prueba_reutilizacion_segundos": tiempo_reuso,
        "recorrido_fuentes_en_prueba_reutilizacion": 0,
        "fin": datetime.now().isoformat(timespec="seconds"),
    }
    escribir_estado(estado_final)

    log("=" * 100)
    log("FASE 1 COMPLETADA")
    log("=" * 100)
    log(f"Formato utilizado: {estado_final['formato']}")
    log(f"Catalogo: {estado_final['ruta_catalogo']}")
    log(f"SHA-256: {estado_final['sha256']}")
    log(f"Tamaño fisico bytes: {estado_final['bytes']}")
    log(f"Filas: {estado_final['filas']}")
    log(f"Columnas: {estado_final['columnas']}")
    log(f"CODCLI distintos: {estado_final['codcli_distintos']}")
    log(f"RUT distintos: {estado_final['rut_distintos']}")
    log(f"Ofertas distintas: {estado_final['ofertas_distintas']}")
    log(f"Fuentes revisadas: {estado_final['fuentes_revisadas']}")
    log(
        "Diferencias memoria vs relectura: "
        f"{estado_final['diferencias_memoria_relectura']}"
    )
    log(
        "Tiempo construccion segundos: "
        f"{estado_final['tiempo_construccion_segundos']}"
    )
    log(
        "Tiempo recarga segundos: "
        f"{estado_final['tiempo_recarga_segundos']}"
    )
    log(
        "Tiempo prueba reutilizacion segundos: "
        f"{estado_final['tiempo_prueba_reutilizacion_segundos']}"
    )
    log("Recorrido de fuentes en prueba de reutilizacion: 0")
    log(f"Estado final: {estado_final['estado']}")
    log(f"Tiempo total segundos: {round(time.perf_counter() - inicio_total, 3)}")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        log("=" * 100)
        log("FASE 1 CON ERROR O BLOQUEO")
        log("=" * 100)
        log(f"{type(exc).__name__}: {exc}")
        escribir_estado(
            {
                "estado": "FASE1_CON_ERROR_O_BLOQUEO",
                "error_tipo": type(exc).__name__,
                "error": str(exc),
                "fin": datetime.now().isoformat(timespec="seconds"),
            }
        )
        raise
