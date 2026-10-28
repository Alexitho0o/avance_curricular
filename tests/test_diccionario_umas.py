"""Pruebas sintéticas de lectura: privacidad, DV0 y períodos etiquetados."""
import unittest
from common.diccionario_umas import (texto,clave,dv_modulo11,rut_validado,cabeceras_unicas,
    etiqueta_inscripcion,periodo_umas,comparacion_univoca,sensibilidad,semantica,patron_tokens_privados)

class DiccionarioUmasTests(unittest.TestCase):
    def test_dv0_separado_y_pegado(self):
        self.assertEqual(texto(0),'0')
        self.assertEqual(dv_modulo11('14'),'0')
        self.assertEqual(rut_validado(14,0)['estado'],'VALIDO')
        self.assertEqual(rut_validado('140')['dv'],'0')
        self.assertEqual(rut_validado('140')['estado'],'VALIDO')
    def test_dv_k_y_error_no_se_corrige(self):
        self.assertEqual(rut_validado('6-K')['estado'],'VALIDO')
        self.assertEqual(rut_validado('6-0')['estado'],'DV_NO_VALIDADO')
        self.assertEqual(rut_validado('DOC_SINTETICO')['estado'],'NO_COMPARABLE')
    def test_cuerpo_no_se_parte_como_si_tuviera_dv(self):
        r=rut_validado('140',formato='cuerpo')
        self.assertEqual(r['cuerpo'],'140')
        self.assertIsNone(r['dv'])
        self.assertEqual(r['estado'],'SIN_DV')
    def test_etiquetas_mandan_sobre_columna(self):
        self.assertEqual(etiqueta_inscripcion('2026-3|SI TOMO RAMOS'),(2026,3,True))
        self.assertEqual(etiqueta_inscripcion('2026-1|NO TOMO RAMOS'),(2026,1,False))
        self.assertIsNone(etiqueta_inscripcion(0))
    def test_periodo_no_se_convierte_a_semestre(self):
        self.assertEqual(periodo_umas('2022-5'),('2022','5'))
        self.assertIsNone(periodo_umas('2022'))
    def test_duplicados_por_bloque(self):
        h=['Fecha_Academia','Comentario','Medio','Quien','Fecha_Finanzas','Comentario','Medio','Quien']
        names=cabeceras_unicas(h,True)
        self.assertEqual(names[1],'Comentario_ACADEMIA')
        self.assertEqual(names[5],'Comentario_FINANZAS')
        self.assertEqual(len(set(names)),len(names))
        self.assertEqual(h[1],'Comentario')
    def test_ambiguos_no_eligen_primera_fila(self):
        self.assertEqual(comparacion_univoca({'O','V'},'O'),'ambiguos')
        self.assertEqual(comparacion_univoca({'O'},'O'),'concordantes')
        self.assertEqual(comparacion_univoca(set(),'O'),'sin_dato')
    def test_privados_nunca_analiticos(self):
        for h in ('RUT','CODCLI','MAIL','FONOACT','MONTO MOROSIDAD','Comentario_FINANZAS','R-CANT.CUOTAS MOROSAS'):
            self.assertEqual(sensibilidad(h,'PERMANENCIA'),'privada',h)
        self.assertEqual(sensibilidad('NOMBRE','PERMANENCIA'),'analítica')
        self.assertEqual(sensibilidad('NOMBRE','DATOS_ALUMNOS'),'privada')
    def test_niveles_y_estados_no_se_confunden(self):
        self.assertIn('asignatura',semantica('NIVEL','PROMEDIOS',{})[0])
        self.assertIn('administrativo',semantica('NIVEL','PERMANENCIA',{})[0])
        self.assertIn('asignatura',semantica('ESTADO','PROMEDIOS',{})[0])
        self.assertIn('extracto',semantica('ESTADO_ACADEMICO','PROMEDIOS',{})[0])
    def test_escaneo_exacto_comprimido(self):
        tokens={'TOKEN_SINTETICO','TOKEN_SINTETICO_LARGO','NOMBRE DE PRUEBA'}
        p=patron_tokens_privados(tokens)
        self.assertEqual(p.findall('TOKEN_SINTETICO y TOKEN_SINTETICO_LARGO, NOMBRE DE PRUEBA'),['TOKEN_SINTETICO','TOKEN_SINTETICO_LARGO','NOMBRE DE PRUEBA'])
        self.assertIsNone(p.search('XTOKEN_SINTETICOX'))

if __name__=='__main__':unittest.main()
