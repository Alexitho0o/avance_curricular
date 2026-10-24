import unittest
from common.capa_demografica import sexo,nacimiento,comparar,puerta

class TestCapa(unittest.TestCase):
    def test_sexo_segun_fuente(self):
        self.assertEqual(sexo('M','UMAS')[0],'HOMBRE')
        self.assertEqual(sexo('M','REPORTE')[0],'MUJER')
        self.assertEqual(sexo('2','MRUN')[0],'MUJER')
    def test_no_homologar_nb(self):
        self.assertEqual(sexo('NB','UMAS'),(None,'NO_HOMOLOGADO'))
    def test_mes_no_dia(self):
        self.assertEqual(nacimiento('15/06/1990')[0],nacimiento('199006')[0])
        self.assertEqual(nacimiento('190001'),(None,'SIN_DATO'))
        self.assertEqual(nacimiento('199013')[1],'INVALIDO')
    def test_contradiccion_no_vacio(self):
        self.assertEqual(comparar({'199001'},{'199002'}),'CONTRADICE')
        self.assertEqual(comparar({None},{'199002'}),'SIN_DATO_UMAS')
    def test_conflicto_aunque_exista_coincidencia(self):
        self.assertEqual(comparar({'199001','199002'},{'199001'}),'CONFLICTO_INTERNO')
    def test_no_contraste_no_es_validacion(self):
        self.assertEqual(puerta(True),'SIN_CONTRASTE_DOCUMENTAL')
        self.assertEqual(puerta(True,['COINCIDE','CONTRADICE']),'RETENIDO_CONTRADICCION_DOCUMENTAL')

if __name__=='__main__':unittest.main()
