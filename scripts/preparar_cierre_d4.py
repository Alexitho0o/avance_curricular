#!/usr/bin/env python3
"""Prepara conclusiones y matrices D4; no modifica fuentes ni escribe Excel."""
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'data/cierre_d4/20261016'
D3 = 'data/validacion_d3/20261016/'
D2 = 'data/cierre_d2/20261016/'
D1 = 'data/cierre_d1/20261016/'


def load(p):
    return json.loads((ROOT / p).read_text())


def save(name, value):
    (BASE / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def lines(xs):
    return '\n'.join(str(x) for x in xs)


def main():
    BASE.mkdir(parents=True, exist_ok=True)
    d3 = load(D3 + 'dictamenes.json')
    inv = {(x['universo'], x['id']): x for x in load(D1 + 'inventario.json')}
    breaches = load(D2 + 'brechas_por_categoria.json')
    hypotheses = [
        ['H-D4-01', 'Primera oferta del Código Único completo define el inicio del diccionario.', 'REGLA_INTERNA_SUSTENTADA_CON_LIMITE_DE_COBERTURA',
         'Se aplica por código, sin exigir matrícula o quórum. Hay oferta para 139 de 141 códigos; ocho aparecen ya en 2010.',
         '2010 es límite de la fuente, no nacimiento probado. Dos códigos sin oferta mantienen inicio vacío. No sustituye Año Inicio formal.',
         'docs/unificacion_proyectos_y_reglas_negocio_20261015.md; data/reglas_negocio/20261015/inicios_por_codigo.json'],
        ['H-D4-02', 'Regular y continuidad se pueden separar por perfil, tipo y duración.', 'SUSTENTADA_EN_PERFILES_GOBERNADOS',
         'Logística J4 V1 regular: 8 semestres, primera oferta 2024; V2 continuidad: 4 semestres, primera oferta 2025.',
         'Son programas distintos aunque el nombre literal coincida. La referencia 2026 no acredita por sí sola el perfil histórico.', D2 + 'logistica_oferta_anual.json'],
        ['H-D4-03', 'Cada versión SIES equivale obligatoriamente a una malla UMAS.', 'REFUTADA_COMO_REGLA_GENERAL',
         'Manual Oferta-Acceso 2027, Anexo 5, pp. 65–66, permite cambios curriculares sin alterar los atributos protegidos del código.',
         'No igualar V, orden de primera oferta y número de malla. Requiere catálogo y vigencia curricular por episodio; no aplicar manual 2027 retroactivamente.',
         'docs/unificacion_proyectos_y_reglas_negocio_20261015.md; data/reglas_negocio/20261015/fuentes.json'],
        ['H-D4-04', 'Cambiar solo régimen semestral a trimestral exige siempre nuevo código.', 'REFUTADA_COMO_REGLA_GENERAL',
         '34 de 103 códigos comunes 2026–2027 cambian régimen manteniendo código y duraciones formales. Manuales distinguen régimen y duración en semestres.',
         'No deducir conversión universal. I162S2C35J4V1 cambia duración 2018–2019 sin código nuevo: causa histórica pendiente.',
         'data/reglas_negocio/20261015/comparacion_regimen_2026_2027.json; docs/unificacion_proyectos_y_reglas_negocio_20261015.md'],
        ['H-D4-05', 'Solo antiguos permite ordenar admisión y delimitar automáticamente cada cohorte UMAS.', 'UTILIDAD_ANUAL_SUSTENTADA_ASIGNACION_AUTOMATICA_NO_DEMOSTRADA',
         '14 de 16 conflictos presentan coexistencia nuevos/antiguos; dos solo antiguos. Cinco contienen discrepancias de ingreso documentadas.',
         'Se consulta el año exacto; I162S2C1J4V1 declara solo antiguos en 2020 y nuevos en 2022. No es cierre irreversible ni fecha de ingreso UMAS.', D2 + 'expedientes_16.json'],
        ['H-D4-06', 'ANOINGRESO o la primera presencia disponible identifica el ingreso a continuidad.', 'INSUFICIENTE_COMO_REGLA_UNICA',
         'La regla interna advierte ingreso heredado del técnico. CILOG contiene episodios nuevos con presencia anterior de la misma persona/carrera.',
         'Separar persona, expediente, carrera e ingreso del episodio. Ausencia de técnico en un extracto no demuestra procedencia externa.', D2 + 'cilog.json'],
        ['H-D4-07', 'MRUN y demografía permiten certificar identidad y versión usando sexo, nacimiento y totales.', 'UTILIDAD_PARA_CANDIDATURAS_SIN_CERTIFICACION',
         'La capa demográfica acota candidatos y permite contraste conjunto; B5 reserva personas separadas de construcción.',
         'No existe certificación individual ni nueva validación independiente D3. Igualdad de totales no obliga una biyección ni demuestra vigencia de malla.',
         'docs/capa_demografica_20261016.md; docs/b5_reglas_historicas_20261016.md; ' + D3 + 'resumen.json'],
        ['H-D4-08', 'Una regla corroborada puede transportarse automáticamente a otros años.', 'REFUTADA_POR_EL_ENSAYO_DE_TRANSPORTE',
         'Ensayo 2018–2020 hacia 2022: 152 coincidencias, 59 contradicciones, seis conflictos y 720 sin regla sobre 937 consultas.',
         'Conservar año exacto y condiciones completas. No escoger K1–K3 caso a caso para superar un conflicto K0.', 'docs/b5_reglas_historicas_20261016.md'],
        ['H-D4-09', 'Las discrepancias de admisión se explican porque los estudiantes fueron eliminados.', 'NO_DEMOSTRADA',
         'En cinco contextos hay seis observaciones persona/estrato: cuatro con estado actual eliminado y dos titulado.',
         'El estado actual no prueba el estado al informar SIES ni explica la causa. No sumar observaciones como personas únicas.', D2 + 'cierre.json'],
    ]
    hh = ['ID', 'Hipótesis', 'Conclusión', 'Evidencia', 'Límite de uso', 'Fuente en proyecto']
    save('hipotesis.json', [dict(zip(hh, h)) for h in hypotheses])

    curricular = {'SIN_PLAN_OBSERVADO', 'VARIOS_PLANES_OBSERVADOS', 'VIGENCIA_MALLA_NO_ACREDITADA', 'SIN_RELACION_PLAN', 'CORROBORACION_NO_ACREDITACION'}
    oferta = {'SIN_OFERTA', 'OFERTA_EN_LIMITE_2010', 'SOLO_CANDIDATURA_H5', 'SIN_RELACION_UMAS'}
    agenda = []
    for b in breaches:
        category = b['causa']
        role = ('Gestión curricular y Registro Académico' if category in curricular else
                'Responsable institucional de Oferta SIES y DAI' if category in oferta else
                'Registro Académico, responsable de Matrícula SIES y DAI')
        row = {**b, 'id_agenda': 'D4-' + category, 'responsable_funcional_propuesto': role,
               'responsable_designado': None, 'prioridad': 1 if category == 'CONFLICTO' else 2 if category in curricular else 3,
               'condicion_reapertura': 'Incorporar la fuente faltante con corte, esquema y hash; cumplir: ' + b['criterio_salida'],
               'estado_d4': 'ANALISIS_CERRADO_CON_BRECHA; REAPERTURA_CON_EVIDENCIA',
               'origen_conteos': 'Inventario D1 investigado en D2; categorías se superponen, no sumar.'}
        agenda.append(row)
    save('agenda.json', agenda)
    by_cause = {x['causa']: x for x in agenda}
    matrix = {'edicion': 'D4_20261016', 'estado': 'ANALISIS_CERRADO_CON_BRECHAS',
              'fuente_dictamen': D3 + 'dictamenes.json', 'asignaciones_activadas': 0,
              'universos': {}, 'incidencias_cilog_d3': d3['incidencias_cilog']}
    for key, universe, idfield in [('contextos', 'CONTEXTO', 'contexto'), ('codigos_sies', 'CODIGO_SIES', 'id'), ('planes_umas', 'PLAN_UMAS', 'id')]:
        rows = []
        for r in d3[key]:
            original = inv[(universe, r[idfield])]
            causes = original['causas_pendientes']
            assert causes and all(x in by_cause for x in causes)
            rows.append({**r, 'cierre_d4': {'estado': 'ANALISIS_CERRADO_CON_BRECHAS',
                         'agenda': ['D4-' + x for x in causes],
                         'limite': 'Resultado académico observacional, sin asignación ni acreditación de malla.'}})
        matrix['universos'][key] = rows
    save('matriz_resultados.json', matrix)

    examples = [
        ['E01', 'CILOG frente a ILOG', 'I162S2C77J4V1 / I162S2C77J4V2', '2024–2026',
         'V1 regular, 8 semestres, oferta desde 2024. V2 continuidad, 4 semestres, desde 2025.',
         'Usar el nombre literal INGENIERIA EN LOGISTICA y separar tipo de plan/modalidad. No trasladar el inicio regular a continuidad.', D2 + 'logistica_oferta_anual.json'],
        ['E02', 'CILOG antes de primera oferta', 'B4-00138 a B4-00145; estrato 2024', '2024',
         'Tres filas UMAS eliminadas por retiro/retracto, sin actividad verificada ni plan observado.',
         'No acreditan una malla impartida en 2024 ni autorizan asignar V1 regular.', D2 + 'cilog.json'],
        ['E03', 'CILOG y admisión', 'I162S2C77J4V2', '2026',
         'Oferta declara solo antiguos; MRUN contiene 11 registros con ingreso actual 2025 y 21 con ingreso actual 2026.',
         'Conciliar oferta y matrícula declarada por corte. Los 21 registros MRUN no se atribuyen individualmente a UMAS.', D2 + 'logistica_mrun_cohortes.json'],
        ['E04', 'CILOG: episodio y estado', '49 expedientes, 47 personas en corte ANOMATRICULA ≤ 2026', 'Corte D2',
         '37 filas vigentes, 11 eliminadas y una suspendida. El nombre del plan CILOG20241 no acredita vigencia inicial 2024.',
         'Revisar ingreso por expediente; ausencia de técnico interno localizado no acredita origen externo.', D2 + 'cilog.json'],
        ['E05', 'Informática regular', 'B4-00362 / IECIRE / RE / D', '2019',
         'V1 solo antiguos y V2 nuevos coexisten con el mismo ingreso SIES 2018; se observa IECIRE20191.',
         'Año de ingreso y plan observado no separan los destinos. Mantener conflicto.', D2 + 'expedientes_16.json'],
        ['E06', 'IETMREOL: campos SIES distintos', 'B4-00844', '2020',
         'Ingreso original SIES 2013 frente a 2019 distingue destinos; el contexto UMAS conserva ingreso original 2019.',
         'No trasladar el campo SIES como si fuera una entrada UMAS equivalente ya disponible.', D2 + 'expedientes_16.json'],
        ['E07', 'TPCREOL: ambos códigos solo antiguos', 'B4-01748', '2020',
         'Los dos destinos declaran solo antiguos; hay ingreso actual 2020 en V1 e ingreso 2016 en V2 sin oferta localizada ese año.',
         'La columna de admisión ayuda a detectar discrepancias, pero no elige el código correcto.', D2 + 'expedientes_16.json'],
    ]
    save('ejemplos.json', examples)
    sheets = []
    def sheet(name, headers, rows, widths, note):
        assert len(headers) == len(widths) and all(len(r) == len(headers) for r in rows)
        # Compactar listas de IDs conserva todo el contenido sin exceder la altura de Excel.
        for header in ('Contextos observados', 'IDs de contextos'):
            if header in headers:
                j = headers.index(header)
                for row in rows:
                    if isinstance(row[j], str):
                        row[j] = row[j].replace('\n', ', ')
        sheets.append({'name': name, 'headers': headers, 'rows': rows, 'widths': widths, 'note': note})
    rows = []
    for r in matrix['universos']['contextos']:
        k = json.loads(r['clave']); of = r['comparacion_oferta_perfil']
        details = []
        for o in of:
            a = o['oferta_anio_observado']
            details.append(o['codigo'] + ': ' + o['vigencia'] + ('; ' + a['nombre_carrera'] + '; ' + str(a['tipo_plan_sies']) + '; duración total=' + str(a['duracion_total']) if a else '; sin oferta del año'))
        rows.append([r['contexto'], r['estado'], *k[:6], lines(k[6]), r['alcance'], lines(r['codigos_observados']), lines(r['codigos_ambiguos']),
                     lines(r['candidatos_h5_ambito_2026']), lines(r['causas_abstencion_asignacion']), lines(r['reglas_aplicadas']),
                     json.dumps(r['reglas_k0'], ensure_ascii=False), r['expediente_d2'], lines(r['cierre_d4']['agenda']), lines(details),
                     'No habilitada', D3 + 'dictamenes.json#' + r['contexto']])
    sheet('Dictámenes D3', ['Contexto', 'Dictamen', 'Carrera UMAS', 'Sede UMAS', 'Jornada UMAS', 'Año observado', 'Ingreso original', 'Primera observación', 'Planes observados', 'Alcance', 'Códigos observados', 'Códigos ambiguos', 'Candidatos H5 · 2026', 'Causas de abstención', 'Reglas D3', 'Reglas K0', 'Expediente D2', 'Agenda D4', 'Oferta del año observado', 'Asignación productiva', 'Fuente'], rows,
          [18, 43, 20, 13, 15, 14, 15, 18, 27, 48, 26, 26, 26, 58, 22, 55, 18, 59, 95, 25, 55], 'Fuentes: dictámenes D3 y matriz_resultados.json. Perfil de referencia 2026 no acredita vigencia histórica.')
    rows = []
    for r in matrix['universos']['codigos_sies']:
        a = r['atributos_c1_referencia_2026']; i = r['fuente_original']['inicio']; c = r['fuente_original']['cobertura']
        rows.append([r['id'], a['nombre_oficial_2026'], a['ultimo_nombre_historico'], a['jornada_2026'], a['modalidad_2026'], a['tipo_plan_2026'], a['sector_ipss_2026'], a['estado_sector'], a['evidencia_sector'], i['anio_inicio_diccionario'], i['estado'], lines(i['anios_ofertados']), c['estado_cobertura'], json.dumps(r['estados_contextos_observados'], ensure_ascii=False), lines(r['vinculos']['contextos_observados']), lines(r['causas_pendientes']), lines(r['cierre_d4']['agenda']), 'No habilitada'])
    sheet('Códigos D3', ['Código Único', 'Nombre oficial 2026', 'Último nombre histórico', 'Jornada 2026', 'Modalidad 2026', 'Tipo de plan 2026', 'Sector IPSS 2026', 'Estado sector', 'Evidencia sector', 'Primera oferta observada', 'Estado inicio', 'Años ofertados', 'Cobertura B4 conservada', 'Dictámenes de contextos', 'Contextos observados', 'Brechas D1', 'Agenda D4', 'Asignación productiva'], rows,
          [25, 48, 48, 22, 24, 35, 30, 48, 70, 20, 40, 23, 42, 58, 30, 48, 55, 25], 'Fuentes: D3, C1 e inicio por Código Único. Nombre histórico separado; vacío 2026 no se inventa.')
    rows = []
    for r in matrix['universos']['planes_umas']:
        a = r['fuente_original']
        rows.append([r['id'], a['estado_cobertura'], lines(a['codigos_con_evidencia_b4']), lines(a['codigos_candidatos_h5']), a['contextos_observados_b4'], json.dumps(r['estados_contextos_observados'], ensure_ascii=False), lines(r['vinculos']['contextos_observados']), lines(r['causas_pendientes']), lines(r['cierre_d4']['agenda']), 'Vigencia no acreditada', 'No habilitada'])
    sheet('Planes D3', ['Plan UMAS', 'Cobertura B4 conservada', 'Códigos con evidencia', 'Candidatos H5', 'Contextos observados', 'Dictámenes de contextos', 'IDs de contextos', 'Brechas D1', 'Agenda D4', 'Vigencia curricular', 'Asignación productiva'], rows,
          [25, 42, 27, 27, 20, 60, 32, 55, 60, 30, 25], 'Fuente: D3. Se conservan los 236 planes, tengan o no actividad observada; no se infiere vigencia del nombre.')
    sheet('Hipótesis D4', hh, hypotheses, [16, 52, 53, 80, 80, 65], 'Conclusiones de H10. Fuentes y límites por hipótesis; reglas internas y formales conservan su ámbito.')
    sheet('Agenda D4', ['ID agenda', 'Prioridad', 'Causa', 'Contextos D1', 'Códigos D1', 'Planes D1', 'Hallazgo D2', 'Siguiente acción', 'Fuente faltante', 'Rol propuesto · por designar', 'Criterio de reapertura', 'Estado'],
          [[a['id_agenda'], a['prioridad'], a['causa'], a['conteos_por_universo'].get('CONTEXTO', 0), a['conteos_por_universo'].get('CODIGO_SIES', 0), a['conteos_por_universo'].get('PLAN_UMAS', 0), a['hallazgo_d2'], a['siguiente_accion'], a['fuente_faltante'], a['responsable_funcional_propuesto'], a['condicion_reapertura'], a['estado_d4']] for a in agenda],
          [56, 12, 48, 16, 16, 16, 85, 70, 75, 55, 90, 57], 'Fuente: brechas D1 investigadas en D2. Categorías superpuestas; no sumar. Roles propuestos, sin asignación personal.')
    sheet('Ejemplos D4', ['ID', 'Mecanismo', 'Referencia académica', 'Año o corte', 'Hallazgo', 'Interpretación y acción', 'Fuente en proyecto'], examples, [12, 36, 55, 20, 85, 85, 60], 'Ejemplos agregados. Estado UMAS actual no equivale a estado histórico; no contiene identidades personales.')
    source = 'outputs/diccionario_c1_20261016/DICCIONARIO_CRUCE_SIES_UMAS_2007_2026_C1.xlsx'
    payload = {'source': str(ROOT / source), 'output': str(ROOT / 'outputs/diccionario_d4_20261016/DICCIONARIO_CRUCE_SIES_UMAS_2007_2026_D4.xlsx'),
               'sheets': sheets, 'resumen': load(D3 + 'resumen.json')}
    save('libro_d4.json', payload)
    sources = [D3 + 'dictamenes.json', D3 + 'resumen.json', D3 + 'entrega.json', D1 + 'inventario.json', D1 + 'criterios.json', D2 + 'brechas_por_categoria.json', D2 + 'cilog.json', D2 + 'expedientes_16.json', source]
    sources += [x for h in hypotheses for x in h[-1].split('; ')]
    sources += [x[-1] for x in examples]
    save('fuentes.json', {'archivos_sha256': {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in sorted(set(sources))}, 'edicion': 'D4', 'fuentes_personales_nuevas': 0})
    print(json.dumps({'hojas_nuevas_datos': len(sheets), 'universos': {k: len(v) for k, v in matrix['universos'].items()}, 'hipotesis': len(hypotheses), 'agenda': len(agenda)}))


if __name__ == '__main__':
    main()
