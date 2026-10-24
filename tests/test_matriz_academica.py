import unittest
from common.matriz_academica import estado_contexto,comparar_evidencias
class TestMatriz(unittest.TestCase):
    def test_estados(self):
        self.assertEqual(estado_contexto(set(),False,False),'SIN_EVIDENCIA')
        self.assertEqual(estado_contexto(set(),True,False),'SOLO_EVIDENCIA_AMBIGUA')
        self.assertEqual(estado_contexto({'a'},False,False),'DESTINO_UNICO_OBSERVADO')
        self.assertEqual(estado_contexto({'a','b'},False,False),'MULTIPLES_DESTINOS')
        self.assertEqual(estado_contexto({'a'},False,True),'CONTRADICCION_ENTRE_EVIDENCIAS')
    def test_unico_no_oculta_ambiguedad(self):
        self.assertEqual(estado_contexto({'a'},True,False),'DESTINO_UNICO_CON_EVIDENCIA_AMBIGUA')
    def test_ausencia_no_contradiccion(self):
        self.assertFalse(comparar_evidencias({'a'},set()))
        self.assertTrue(comparar_evidencias({'a'},{'b'}))
        self.assertFalse(comparar_evidencias({'a','b'},{'b'}))
if __name__=='__main__':unittest.main()
