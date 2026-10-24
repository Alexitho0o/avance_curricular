"""Pruebas del constructor H5: límites de evidencia y preservación de claves."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from scripts.construir_maestro_equivalencias import (
    key, make_offers, plan_candidates, program_relations, verify_sources,
    write_immutable, sha, ROOT, operational_differences)


def offer(**changes):
    row = dict(ANO='OFE_2026',CODIGO_UNICO='I162S2C77J4V1',CODIGO_IES='162',
        CODIGO_SEDE='2',CODIGO_CARRERA='77',VERSION='1',NOMBRE_CARRERA='INGENIERIA EN LOGISTICA',
        JORNADA='A Distancia',MODALIDAD='No Presencial',TIPO_CARRERA='Plan Regular',
        PLAN_ESPECIAL='NO APLICA',DURACION_ESTUDIOS='8',DURACION_TOTAL='8',
        VIGENCIA='Vigente con estudiantes nuevos',NIVEL_GLOBAL='Pregrado',
        fila_origen='100',hoja_origen='in')
    return {**row,**changes}


def relation(**changes):
    return dict(id='EP-test',codcarpr='ILOG',sede_umas='RE',jornada_umas='O',
        nombre_interno='INGENIERIA EN LOGISTICA',codigo_unico='I162S2C77J4V1',
        componentes_sies=dict(institucion='162',sede='2',carrera='77',jornada='4',version='1'),
        presencia_oferta_2026=True,**changes)


def plan(**changes):
    return {**dict(CODPESTUD='ILOG20241',carreras_internas=['ILOG'],sedes=['RE'],
        nombres_carrera=['INGENIERIA EN LOGISTICA'],filas_fuente=[2,3]),**changes}


class ConstructorH5Test(unittest.TestCase):
    def test_clave_no_colisiona_delimitadores(self):
        self.assertNotEqual(key('a|b','c'),key('a','b|c'))
        self.assertNotEqual(key('a',None),key('a','None'))

    def test_nombre_anual_y_nombre_2026_son_distintos(self):
        rows=make_offers([offer(ANO='OFE_2024',NOMBRE_CARRERA='NOMBRE HISTORICO'),offer()])
        self.assertEqual(rows[0]['nombre_carrera'],'NOMBRE HISTORICO')
        self.assertEqual(rows[0]['nombre_oferta_2026'],'INGENIERIA EN LOGISTICA')
        self.assertNotIn('Continuidad',rows[0]['nombre_oferta_2026'])

    def test_no_inventa_nombre_2026_de_codigo_ausente(self):
        self.assertIsNone(make_offers([offer(ANO='OFE_2024')])[0]['nombre_oferta_2026'])

    def test_rechaza_oferta_duplicada_incoherente_o_2027(self):
        for rows in ([offer(),offer()], [offer(CODIGO_SEDE='3')], [offer(ANO='OFE_2027')]):
            with self.assertRaises(ValueError):make_offers(rows)

    def test_sede_y_carrera_exactas(self):
        p=plan()
        wrong_sede={**relation(),'sede_umas':'CO'}
        wrong_career={**relation(),'codcarpr':'CILOG'}
        self.assertEqual(plan_candidates([p],[wrong_sede,wrong_career],[]),[])

    def test_nombre_distinto_se_conserva_pendiente_sin_alias(self):
        r={**relation(),'nombre_interno':'INGENIERIA EN LOGISTICA (CONTINUIDAD)'}
        c=plan_candidates([plan()],[r],[])[0]
        self.assertEqual(c['estado_nombre_catalogo'],'DIFERENTE_SIN_ALIAS')
        self.assertFalse(c['habilitada_para_resolver'])
        self.assertEqual(c['nombre_plan_catalogo'],['INGENIERIA EN LOGISTICA'])

    def test_anio_textual_y_actividad_no_crean_periodos_efectivos(self):
        obs=[dict(PLAN_DE_ESTUDIO='ILOG20241',CODCARR='ILOG',JORNADA='O',ANO='2019',
            PERIODO='1',REGIMEN='SEMESTRAL',estado_observacion='OBSERVACION_CON_ANIO',filas_reporte='3')]
        c=plan_candidates([plan()],[relation()],obs)[0]
        self.assertEqual(c['anios_actividad_observada_jornada'],[2019])
        self.assertEqual(c['periodos_acreditados'],[])
        self.assertEqual(c['ambito_candidato'],2026)

    def test_jornada_sin_mapa_y_planes_sin_actividad_se_conservan(self):
        r={**relation(),'jornada_umas':None,'codigo_unico':'I162S2C77J3V1'}
        c=plan_candidates([plan()],[r],[])[0]
        self.assertIsNone(c['jornada_umas'])
        self.assertEqual(c['anios_actividad_observada_jornada'],[])

    def test_contexto_plan_ambiguo_no_se_escoge(self):
        self.assertEqual(plan_candidates([plan(sedes=['RE','CO'])],[relation()],[]),[])

    def test_relacion_operativa_hereda_fuente_y_no_cubre_ano_efectivo(self):
        source={'duracion':{'path':str(ROOT/'DURACION_ESTUDIOS.tsv'),'sha256':'a'*64}}
        s=dict(anio=2026,sedes_internas={'RE':'2','CO':'3'},oferta=[dict(
            codigo_unico='I162S2C77J3V1',sede='2',carrera='77',jornada='3',version='1',plan='1',
            equivalencias=[dict(codcarpr='ILOG',nombre_interno='NOMBRE OPERATIVO',
                fuente={'path':'DURACION_ESTUDIOS.tsv','sha256':'a'*64},metodo='CATALOGO_MU2026',fila_fuente=2)])])
        row=program_relations(s,source,set())[0]
        self.assertIsNone(row['jornada_umas'])
        self.assertFalse(row['presencia_oferta_2026'])
        self.assertEqual(row['estado'],'RELACION_OPERATIVA_SIN_PLAN_NI_VIGENCIA')
        bad=deepcopy(s);bad['oferta'][0]['equivalencias'][0]['fuente']['sha256']='b'*64
        with self.assertRaises(ValueError):program_relations(bad,source,set())

    def test_preflight_salida_impide_escritura_parcial(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'b.json').write_bytes(b'original')
            with self.assertRaises(ValueError):write_immutable(p,{'a.json':b'new','b.json':b'changed'})
            self.assertFalse((p/'a.json').exists())
            self.assertEqual((p/'b.json').read_bytes(),b'original')

    def test_sha_fuente_alterada_se_rechaza(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'source';p.write_text('original');expected=sha(p);p.write_text('changed')
            c=dict(schema_version=1,periodo_objetivo=[2007,2026],
                sources={'x':{'path':str(p),'sha256':expected}},referencias_congeladas=[])
            with self.assertRaises(ValueError):verify_sources(c)

    def test_comparacion_categorica_no_confunde_caja_con_modalidad(self):
        snapshot={'oferta':[dict(codigo_unico='I162S2C77J4V1',vigencia='1',plan='1',
            modalidad='No presencial',modalidad_codigo='3',duracion_estudios='8',duracion_total='8')]}
        offers=make_offers([offer()])
        self.assertEqual(operational_differences(snapshot,offers),[])
        offers[0]['vigencia']='Vigente sin estudiantes nuevos'
        differences=operational_differences(snapshot,offers)
        self.assertEqual([d['campo'] for d in differences],['vigencia'])


if __name__=='__main__':unittest.main()
