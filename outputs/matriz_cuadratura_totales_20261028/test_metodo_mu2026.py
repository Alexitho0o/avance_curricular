"""Pruebas sintéticas; no ejecutan el contraste sobre fuentes reales 2026."""
import unittest
from metodo_mu2026 import clasificar,contrastar_fuente,codigos_con_diferencia

class PruebasMetodo2026(unittest.TestCase):
    def mu(self,n,vig):
        return {'ANIO_INFORMADO':2026,'TIPO_DOC':'R','N_DOC':str(n),'DV':0,'COD_SED':2,'COD_CAR':1,'JOR':4,'VERSION':2,'VIG':vig}
    def sies(self,n):
        return {'TIPO_DOCUMENTO':'R','NUM_DOCUMENTO':str(n),'DV':0,'CODIGO_UNICO':'I162S2C1J4V2'}
    def test_cero_y_tres_clases(self):
        s=[self.sies(i) for i in range(1,4)];m=[self.mu(1,1),self.mu(2,0)]
        r,_=clasificar(s,m,{'I162S2C1J4V2'})
        self.assertEqual(r['por_codigo'][0],{'codigo_sies':'I162S2C1J4V2','vig1_nuestra':1,'vig0_nuestra':1,'no_esta_en_nuestra_base':1})
    def test_deduplicacion_y_fuera_foco(self):
        s=self.sies(1);out=dict(s,CODIGO_UNICO='I162S2C2J4V1')
        r,_=clasificar([s,s,out],[self.mu(1,0)],{'I162S2C1J4V2'})
        self.assertEqual((r['matriculas_foco'],r['filas_duplicadas_foco'],r['filas_fuera_foco']),(1,1,1))
    def test_conflicto_no_se_fuerza(self):
        with self.assertRaises(ValueError):clasificar([self.sies(1)],[self.mu(1,0),self.mu(1,1)],{'I162S2C1J4V2'})
    def test_fuente_ausente_no_ejecuta(self):
        with self.assertRaises(FileNotFoundError):contrastar_fuente('/ruta/no_existente', 'sin_hash',[],anio_matricula=2026,campos={},encoding='latin1',detalle_privado='/Users/alexi/.local/share/ipss/no_generado.json')
    def test_foco_gobernado(self):self.assertEqual(len(codigos_con_diferencia()),48)

if __name__=='__main__':unittest.main()
