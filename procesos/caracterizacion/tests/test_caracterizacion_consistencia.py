from __future__ import annotations

import unittest

import pandas as pd

from caracterizacion_limesurvey import normalize_cross_value
from caracterizacion_consistencia import (
    ADVERTENCIA_ELIMINADOS_MATRICULA_VENTANA,
    CATEGORIA_CONFLICTO_MATRICULA,
    CATEGORIA_TOKEN_DUPLICADO,
    CATEGORIA_TOKEN_SIN_MATRICULA,
    CATEGORIA_VIGENTE_CON_TOKEN,
    CATEGORIA_VIGENTE_SIN_TOKEN,
    ErrorParticionKPI,
    LEYENDA_ELIMINADOS_MATRICULA_VENTANA,
    PRECEDENCIA_CATEGORIAS,
    RegistroParticionesKPI,
    conciliar_matricula_tokens,
    describir_eliminados_matricula_ventana,
    validar_particion_kpi,
)


class ConciliacionMatriculaTokensTests(unittest.TestCase):
    def escenario_cinco_categorias(self):
        matricula = pd.DataFrame(
            {
                "CODCLI": ["A", "B", "C", "D"],
                "token": ["tok-a", None, "tok-conflicto", "tok-conflicto"],
            },
            index=[10, 10, 30, 40],  # El índice tampoco se supone único.
        )
        tokens = pd.DataFrame(
            {
                "token_encuesta": [
                    "tok-a",
                    "tok-sin-matricula",
                    "tok-duplicado",
                    "tok-duplicado",
                    "tok-conflicto",
                    None,
                ]
            },
            index=[1, 2, 2, 4, 5, 6],
        )
        return matricula, tokens

    def test_cada_componente_recibe_exactamente_una_de_las_cinco_categorias(self):
        matricula, tokens = self.escenario_cinco_categorias()
        resultado = conciliar_matricula_tokens(
            matricula,
            tokens,
            columna_token_fuente="token_encuesta",
        )

        self.assertEqual(
            set(resultado.detalle["categoria"]),
            {
                CATEGORIA_VIGENTE_CON_TOKEN,
                CATEGORIA_VIGENTE_SIN_TOKEN,
                CATEGORIA_TOKEN_SIN_MATRICULA,
                CATEGORIA_TOKEN_DUPLICADO,
                CATEGORIA_CONFLICTO_MATRICULA,
            },
        )
        self.assertFalse(resultado.detalle["categoria"].isna().any())
        self.assertTrue(resultado.detalle["componente_id"].is_unique)
        self.assertEqual(len(resultado.detalle), 6)
        precedencia = dict(zip(PRECEDENCIA_CATEGORIAS, range(1, 6)))
        for fila in resultado.detalle.itertuples(index=False):
            self.assertEqual(fila.precedencia_categoria, precedencia[fila.categoria])

    def test_conflicto_de_matricula_precede_a_token_duplicado(self):
        matricula = pd.DataFrame(
            {
                "CODCLI": ["A", "B"],
                "token": ["mismo", "mismo"],
            }
        )
        tokens = pd.DataFrame({"token": ["mismo", "mismo"]})

        resultado = conciliar_matricula_tokens(matricula, tokens)

        self.assertEqual(len(resultado.detalle), 1)
        componente = resultado.detalle.iloc[0]
        self.assertEqual(componente["categoria"], CATEGORIA_CONFLICTO_MATRICULA)
        self.assertTrue(componente["conflicto_matricula"])
        self.assertTrue(componente["token_duplicado"])
        self.assertEqual(componente["cantidad_filas_matricula"], 2)
        self.assertEqual(componente["cantidad_filas_tokens"], 2)

    def test_duplicados_y_nulos_no_se_descartan_y_reconstruyen_ambas_fuentes(self):
        matricula, tokens = self.escenario_cinco_categorias()
        # Agrega una matrícula sin llave institucional y un segundo token nulo.
        matricula.loc[50] = [None, "tok-llave-nula"]
        tokens.loc[7] = [None]
        resultado = conciliar_matricula_tokens(
            matricula,
            tokens,
            columna_token_fuente="token_encuesta",
        )

        audit_m = resultado.auditoria.query("fuente == 'MATRICULA'")
        audit_t = resultado.auditoria.query("fuente == 'TOKENS'")
        self.assertEqual(len(audit_m), len(matricula))
        self.assertEqual(len(audit_t), len(tokens))
        self.assertEqual(set(audit_m["posicion_origen"]), set(range(len(matricula))))
        self.assertEqual(set(audit_t["posicion_origen"]), set(range(len(tokens))))
        self.assertTrue(resultado.auditoria["fila_origen"].is_unique)

        # Los dos nulos de tokens son dos filas y dos componentes, no un
        # drop_duplicates ni una falsa agrupación por NA.
        tokens_nulos = audit_t[audit_t["token_nulo"]]
        self.assertEqual(len(tokens_nulos), 2)
        self.assertEqual(tokens_nulos["componente_id"].nunique(), 2)
        self.assertTrue(
            (tokens_nulos["categoria"] == CATEGORIA_TOKEN_SIN_MATRICULA).all()
        )

        duplicado = resultado.detalle[
            resultado.detalle["categoria"] == CATEGORIA_TOKEN_DUPLICADO
        ].iloc[0]
        self.assertEqual(duplicado["cantidad_filas_tokens"], 2)
        self.assertEqual(len(duplicado["filas_tokens_origen"]), 2)

        metricas = resultado.resumen.set_index("metrica")
        self.assertEqual(
            metricas.loc["filas_matricula_reconstruidas", "valor"], len(matricula)
        )
        self.assertEqual(
            metricas.loc["filas_tokens_reconstruidas", "valor"], len(tokens)
        )
        self.assertEqual(
            metricas.loc["filas_matricula_reconstruidas", "resultado"], "OK"
        )
        self.assertEqual(
            metricas.loc["filas_tokens_reconstruidas", "resultado"], "OK"
        )

    def test_columnas_y_normalizadores_son_parametrizables(self):
        matricula = pd.DataFrame(
            {"alumno": [" 001 "], "llave_encuesta": [" TOKEN-X "]}
        )
        tokens = pd.DataFrame({"participante": ["token-x"]})

        resultado = conciliar_matricula_tokens(
            matricula,
            tokens,
            columna_llave_estudiante="alumno",
            columna_token_matricula="llave_encuesta",
            columna_token_fuente="participante",
            normalizador_llave_estudiante=lambda value: str(value).strip().lstrip("0"),
            normalizador_token=lambda value: str(value).strip().upper(),
        )

        self.assertEqual(len(resultado.detalle), 1)
        componente = resultado.detalle.iloc[0]
        self.assertEqual(componente["categoria"], CATEGORIA_VIGENTE_CON_TOKEN)
        self.assertEqual(componente["llaves_estudiante"], ("1",))
        self.assertEqual(componente["tokens_union_canonica"], ("TOKEN-X",))
        metricas = resultado.resumen.set_index("metrica")["valor"]
        self.assertEqual(metricas["nodos_estudiante_canonicos"], 1)
        self.assertEqual(metricas["nodos_token_canonicos"], 1)
        self.assertEqual(metricas["componentes_union_canonica"], 1)

    def test_conciliacion_por_email_usa_la_llave_canonica_sin_forzar_rut(self):
        matricula = pd.DataFrame(
            {
                "CODCLI": ["A", "B"],
                "_token_match": [
                    " Alumna.Uno@Instituto.CL ",
                    "alumno.dos@instituto.cl",
                ],
                # Esta columna reproduce el RUT institucional y no debe ser la
                # llave elegida cuando LimeSurvey seleccionó email.
                "_token_norm": ["11111111", "22222222"],
            }
        )
        tokens = pd.DataFrame(
            {
                "_token_norm": [
                    "alumna.uno@instituto.cl",
                    "ALUMNO.DOS@INSTITUTO.CL",
                ]
            }
        )
        resultado = conciliar_matricula_tokens(
            matricula,
            tokens,
            columna_token_matricula="_token_match",
            columna_token_fuente="_token_norm",
            normalizador_token=lambda value: normalize_cross_value(value, "email"),
        )

        self.assertEqual(len(resultado.detalle), 2)
        self.assertTrue(
            resultado.detalle["categoria"].eq(CATEGORIA_VIGENTE_CON_TOKEN).all()
        )
        self.assertEqual(
            set(resultado.detalle["tokens_union_canonica"].explode()),
            {"alumna.uno@instituto.cl", "alumno.dos@instituto.cl"},
        )


class ParticionesKPITests(unittest.TestCase):
    def test_diferencia_positiva_agrega_otros_y_audita_explicacion(self):
        auditoria = validar_particion_kpi(
            total=10,
            componentes={"SI": 3, "NO": 5},
            salida="panel.xlsx",
            hoja="PANEL",
            identidad="TOTAL = SI + NO + OTROS",
            unidad="estudiante vigente",
            llave="CODCLI",
            explicacion_residual="Estados institucionales no expuestos en el panel.",
        )

        componentes = auditoria.query("tipo_registro == 'COMPONENTE'")
        otros = componentes[componentes["componente"] == "OTROS"].iloc[0]
        resumen = auditoria.query("tipo_registro == 'RESUMEN'").iloc[0]
        self.assertEqual(otros["valor"], 2)
        self.assertEqual(otros["origen_componente"], "RESIDUAL_AUTOMATICO")
        self.assertEqual(resumen["suma_componentes_declarados"], 8)
        self.assertEqual(resumen["diferencia_inicial"], 2)
        self.assertEqual(resumen["suma_componentes_validada"], 10)
        self.assertEqual(resumen["diferencia_final"], 0)
        self.assertEqual(resumen["resultado"], "OK_CON_OTROS")
        self.assertEqual(
            resumen["explicacion"],
            "Estados institucionales no expuestos en el panel.",
        )

    def test_solapamiento_negativo_lanza_error_y_conserva_auditoria(self):
        registro = RegistroParticionesKPI()
        with self.assertRaises(ErrorParticionKPI) as contexto:
            registro.registrar(
                total=5,
                componentes={"A": 3, "B": 4},
                salida="informe.docx",
                identidad="TOTAL = A + B",
            )

        error = contexto.exception
        resumen_error = error.auditoria.query("tipo_registro == 'RESUMEN'").iloc[0]
        self.assertEqual(resumen_error["diferencia_inicial"], -2)
        self.assertEqual(resumen_error["resultado"], "ERROR_SOLAPAMIENTO")
        self.assertIn("solapamiento", resumen_error["explicacion"])
        self.assertEqual(len(registro.auditoria), len(error.auditoria))
        self.assertEqual(
            registro.auditoria.iloc[0]["registro_id"], "PARTICION:000000001"
        )

    def test_registro_acumula_particiones_exitosas(self):
        registro = RegistroParticionesKPI()
        registro.registrar(total=2, componentes={"SI": 2}, identidad="respuestas")
        registro.registrar(total=3, componentes={"A": 1}, identidad="estados")
        auditoria = registro.to_frame()

        self.assertEqual(auditoria["registro_id"].nunique(), 2)
        resultados = set(
            auditoria.query("tipo_registro == 'RESUMEN'")["resultado"]
        )
        self.assertEqual(resultados, {"OK", "OK_CON_OTROS"})


class SemanticaEliminadosTests(unittest.TestCase):
    def test_leyenda_declara_fecha_de_matricula_y_no_fecha_de_eliminacion(self):
        auditoria = describir_eliminados_matricula_ventana(
            fecha_inicio="2026-07-14",
            fecha_fin="2026-07-15",
        )
        fila = auditoria.iloc[0]
        self.assertEqual(
            LEYENDA_ELIMINADOS_MATRICULA_VENTANA,
            "Estudiantes actualmente eliminados cuya fecha de matrícula "
            "pertenece a la ventana evaluada.",
        )
        self.assertEqual(fila["leyenda"], LEYENDA_ELIMINADOS_MATRICULA_VENTANA)
        self.assertEqual(
            fila["advertencia"], ADVERTENCIA_ELIMINADOS_MATRICULA_VENTANA
        )
        self.assertEqual(fila["advertencia"], "NO_ES_FECHA_ELIMINACION")
        self.assertEqual(fila["columna_fecha"], "FECHAMATRICULA")


if __name__ == "__main__":
    unittest.main()
