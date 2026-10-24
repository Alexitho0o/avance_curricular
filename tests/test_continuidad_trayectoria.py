import unittest
from common.continuidad_trayectoria import evaluar_trayectorias, resolver_version_trayectoria


def row(index, expediente, carrera, years, *, continuity=False, technical=False, person='persona_sintetica'):
    return {'indice':index,'persona':person,'codcli':expediente,'carrera':carrera,
            'continuidad':continuity,'tecnico':technical,'anios_observados':years,'anoingreso':'2020'}


class TrayectoriaTests(unittest.TestCase):
    def test_resolutor_no_reutiliza_anoingreso_en_continuidad(self):
        group={'perfiles_duracion_tipo':[['4','3']],'familias':['I162S2C77J4']}
        result=resolver_version_trayectoria(group,[],anoingreso=2020)
        self.assertEqual(result['estado'],'REQUIERE_INICIO_EN_CARRERA_CONTINUIDAD')
        self.assertIsNone(result['codigo_propuesto'])

    def test_resolutor_usa_fecha_carrera_con_procedencia(self):
        group={'perfiles_duracion_tipo':[['4','3']],'familias':['I162S2C77J4']}
        history={'familia':'I162S2C77J4','codigo_unico':'I162S2C77J4V2','inicio_oferta':2025,
                 'anual':[{'anio':2025,'duracion_total':'4','tipo_plan':'3','registro_csv':1}]}
        result=resolver_version_trayectoria(group,[history],anoingreso=2020,anio_inicio_carrera=2025)
        self.assertEqual(result['codigo_propuesto'],'I162S2C77J4V2')
        self.assertEqual(result['fuente_fecha_version'],'PRIMERA_OBSERVACION_CARRERA')
        self.assertFalse(result['anoingreso_usado_para_version'])

    def test_anoingreso_heredado_no_fija_continuidad(self):
        data=[row(1,'tecnico','TEC',[2020,2021],technical=True),
              row(2,'profesional','CONT',[2025,2026],continuity=True)]
        result=evaluar_trayectorias(data)[0]
        self.assertEqual(result['primer_anio_observado_carrera'],2025)
        self.assertEqual(result['anoingreso_original'],'2020')
        self.assertEqual(result['origen'],'TECNICO_IPSS_OBSERVADO_ANTERIOR')
        self.assertFalse(result['anoingreso_usado_para_version'])

    def test_dos_codcli_no_prueban_tecnico(self):
        data=[row(1,'otro','OTRA',[2020]),row(2,'actual','CONT',[2025],continuity=True)]
        result=evaluar_trayectorias(data)[0]
        self.assertEqual(result['origen'],'SIN_TECNICO_INTERNO_LOCALIZADO')
        self.assertFalse(result['ingreso_externo_confirmado'])

    def test_varios_codcli_misma_carrera_preservan_primera_observacion(self):
        data=[row(1,'uno','CONT',[2024],continuity=True),row(2,'dos','CONT',[2026],continuity=True)]
        self.assertTrue(all(r['primer_anio_observado_carrera']==2024 for r in evaluar_trayectorias(data)))

    def test_otra_persona_no_aporta_antecedente(self):
        data=[row(1,'uno','TEC',[2020],technical=True,person='otra_persona'),
              row(2,'dos','CONT',[2025],continuity=True)]
        self.assertEqual(evaluar_trayectorias(data)[0]['cantidad_codcli_tecnicos'],0)

    def test_identidad_vacia_no_enlaza(self):
        result=evaluar_trayectorias([row(1,'uno','CONT',[2025],continuity=True,person='')])[0]
        self.assertEqual(result['origen'],'IDENTIDAD_INSUFICIENTE')
        self.assertIsNone(result['primer_anio_observado_carrera'])

    def test_codcli_con_dos_personas_queda_en_conflicto(self):
        data=[row(1,'uno','CONT',[2025],continuity=True),
              row(2,'uno','CONT',[2024],continuity=True,person='otra_persona')]
        self.assertTrue(all(r['origen']=='CONFLICTO_IDENTIDAD_CODCLI' for r in evaluar_trayectorias(data)))

    def test_tecnico_observado_despues_no_prueba_antecedente_anterior(self):
        data=[row(1,'uno','TEC',[2026],technical=True),row(2,'dos','CONT',[2025],continuity=True)]
        self.assertEqual(evaluar_trayectorias(data)[0]['origen'],'TECNICO_IPSS_TEMPORALIDAD_PENDIENTE')

    def test_minimo_observado_no_es_fecha_efectiva(self):
        result=evaluar_trayectorias([row(1,'uno','CONT',[2025],continuity=True)])[0]
        self.assertIsNone(result['anio_ingreso_efectivo_confirmado'])
        self.assertEqual(result['estado_fecha'],'PRIMERA_OBSERVACION_NO_INGRESO_CONFIRMADO')


if __name__=='__main__':unittest.main()
