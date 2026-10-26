"""Consolida evidencia local de Fase 1, sin adoptar códigos ni modificar fuentes.

Especificación: PLAN_CIERRE_100_POR_CIENTO.md, revisión v2.
Los insumos individuales permanecen fuera de Git; solo se exportan agregados.
La revisión documental y sus procedimientos se conservan en el directorio privado.
"""
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime
from zoneinfo import ZoneInfo
import csv
import hashlib
import json
import re
import subprocess

ROOT = Path('/Users/alexi/Documents/GitHub/avance_curricular')
AUDIT = Path(__file__).resolve().parent
PRIVATE = Path('/Users/alexi/.local/share/ipss/fase1_cierre_104_20261025')
OUT = AUDIT / 'fase1_20261025'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read(name):
    return json.loads((PRIVATE / name).read_text())

def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def main():
    assert subprocess.run(['git', '-C', str(PRIVATE), 'rev-parse', '--show-toplevel'], capture_output=True).returncode != 0
    checkpoint = json.loads((AUDIT / 'CHECKPOINT_CIERRE.json').read_text())
    assert sha(AUDIT / checkpoint['plan']['archivo']) == checkpoint['plan']['sha256']
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    assert head == checkpoint['head']
    active_path = ROOT / 'data/diccionario_sies_seguimiento/activo.json'
    active = json.loads(active_path.read_text())
    assert active['sha256'] == sha(ROOT / active['descriptor'])
    descriptor = json.loads((ROOT / active['descriptor']).read_text())
    assert descriptor['edicion'] == 'v7_20261023_inf35_03_t3'
    assert sha(descriptor['base_privada']['ruta']) == descriptor['base_privada']['sha256']

    focus = read('REVISION_104.json')
    by = {r['contexto_v17']['observacion_id']: r for r in focus}
    assert len(focus) == len(by) == 104
    journeys = read('REVISION_JORNADAS.json')
    other = read('REVISION_OTROS_CONTEXTOS.json')
    no_code = read('REVISION_SIN_CANDIDATO.json')
    repairs = read('OPERACIONES_REPARACION_CINCO_P.json')
    bridges = read('REVISION_PUENTES_DOCUMENTALES.json')
    approval = read('APROBACIONES_VERIFICADAS.json')
    annual = read('REGLA_ANUAL_CINCO_P_VERIFICADA.json')
    prom = read('PROMEDIOS_FILAS_104.json')
    da = read('DATOSALUMNOS_FILAS_104.json')
    assert len(journeys['filas']) == 63 and len(other['resultados']) == 34
    assert len(no_code['resultados']) == 2 and len(repairs['operaciones']) == 5
    assert all(r['cumple_regla_anual_vigente'] and not r['ambiguedad_de_atribucion'] for r in annual['resultados'])

    review = {}
    for r in journeys['filas']:
        status = ('PROPUESTA_INTERNA_LISTA' if r['categoria_operativa'] == 'EVIDENCIA_LISTA_PARA_PROPONER'
                  else 'CRITERIO_CONTINUIDAD_PENDIENTE' if r['categoria_operativa'] == 'CRITERIO_NUEVO_A_VALIDAR'
                  else 'PENDIENTE_EVIDENCIA_O_CRITERIO')
        review[r['observacion_id']] = (status, r['subgrupo_revision'])
        if status == 'PROPUESTA_INTERNA_LISTA':
            assert r['propuesta']['codigo'] in r['codigos_mu_anio']
            assert str(r['periodo']) == '3'
            assert r['actividad_AR_no_convalidada']
    for r in other['resultados']:
        assert r['observacion_id'] not in review
        status = 'PROPUESTA_INTERNA_LISTA' if r['categoria_operativa'] == 'propuesta_nueva' else 'PENDIENTE_EVIDENCIA_O_CRITERIO'
        review[r['observacion_id']] = (status, r.get('categoria', r.get('resultado', 'OTRO_EXPEDIENTE')))
    for r in no_code['resultados']:
        assert r['observacion_id'] not in review
        review[r['observacion_id']] = ('PENDIENTE_EVIDENCIA_O_CRITERIO', r['resultado'])
    for op in repairs['operaciones']:
        oid = op['observacion_id']
        assert oid not in review and op['estado_antes'] == by[oid]['observacion_v7']
        assert op['estado_despues_propuesto']['codigo_documental_atribuible']
        review[oid] = ('RECUPERACION_C_VALIDADA_NO_PROMOVIDA', 'PUENTE_P_RUT_Y_REGLA_ANUAL_EXISTENTE')
    assert set(review) == set(by)
    counts = Counter(v[0] for v in review.values())
    assert counts == {'RECUPERACION_C_VALIDADA_NO_PROMOVIDA': 5, 'PROPUESTA_INTERNA_LISTA': 16,
                      'CRITERIO_CONTINUIDAD_PENDIENTE': 12, 'PENDIENTE_EVIDENCIA_O_CRITERIO': 71}
    assert len({x['contexto_v17']['persona'] for x in focus}) == 58
    # La lectura compartida respalda todas las observaciones, no solo una muestra.
    assert {q['observacion_id'] for x in prom['filas'] for q in x['contextos_referencia']} == set(by)
    assert {q['observacion_id'] for x in da['filas'] for q in x['contextos_referencia']} == set(by)
    assert len(prom['filas']) == 269 and len(da['filas']) == 58

    career = defaultdict(Counter)
    for oid, (status, reason) in review.items():
        code = by[oid]['contexto_v17']['carrera_umas']
        career[code]['observaciones'] += 1
        career[code][status] += 1
    career_rows = [{'carrera_UMAS': code, **dict(c)} for code, c in sorted(career.items())]
    assert len(career_rows) == 12

    now = datetime.now(ZoneInfo('America/Santiago')).isoformat()
    result = {
        'fecha_hora': now, 'clasificacion': 'B evidencia; C revisión y reparación; D decisiones existentes; E propuestas y pendientes',
        'alcance': '104 observaciones pendientes del seguimiento V17, no una nueva cohorte',
        'observaciones': 104, 'personas': 58, 'carreras_UMAS': 12, 'resultado_exclusivo': dict(counts),
        'por_carrera': career_rows, 'por_subgrupo_jornada': dict(Counter(r['subgrupo_revision'] for r in journeys['filas'])),
        'operaciones_previas_verificadas': 46, 'cierres_previos_olvidados_en_bloque_revisado': 0,
        'puente_documental_recuperado': {'personas': 5, 'observaciones': 9, 'limite': 'No sumar a los104; cinco cumplen regla anual, cuatro requieren jornada por período.'},
        'homologaciones_anteriores_al_ingreso_declarado': 19,
        'recuperaciones_por_codigo': [{'codigo': 'I162S2C57J4V1', 'observaciones': 2}, {'codigo': 'I162S2C78J2V1', 'observaciones': 3}],
        'propuestas_internas': {'T3_foto_y_MU_del_mismo_ano': 14, 'IINF_2025_actividad_foto_y_codigo_2026': 2},
        'activo_conservado': {'edicion': descriptor['edicion'], 'V17_con_codigo': 2750, 'V17_pendientes': 104, 'historico_con_codigo': 21725, 'historico_pendientes': 3049},
        'impacto_cinco_si_se_incorporan': repairs['impacto_si_se_incorpora'],
        'sin_modificar': ['fuentes originales', 'bases', 'denominadores', 'reglas de retención', 'V17', 'diccionario activo'],
        'proxima_accion': 'Incorporar las cinco reparaciones C en edición candidata durante consolidación; decidir por separado las16 propuestas internas. Las12 T2 no comparten automáticamente ese criterio.',
        'qa': {'cobertura_revision': '104/104', 'duplicados': 0, 'observaciones_perdidas': 0, 'sumas_correctas': True,
               'filas_PROMEDIOS_compartidas': 269, 'filas_DA_compartidas': 58, 'campos_fuera_alcance_en_cinco_operaciones': 0,
               'nuevas_asignaciones_activas': 0, 'recalculo_Excel_ejecutado': False},
        'limites': ['Una foto de T3 no prueba automáticamente jornada de T2.',
                    'JORNADA de PROMEDIOS no está acreditada como historizada por asignatura.',
                    'El período de una homologación no acredita fecha de reconocimiento ni ingreso efectivo al plan destino.',
                    'No se ejecutaron nuevamente24774 consultas ni se verificó publicación remota.',
                    'Códigos anuales atribuidos no acreditan envío/aceptación SIES ni fecha efectiva de cambio.']
    }
    # Evitar filtración de identificadores a la salida compartible.
    banned = {str(v) for r in focus for v in [r['contexto_v17']['persona'], r['contexto_v17']['codcli']] if v}
    public_text = json.dumps(result, ensure_ascii=False)
    assert not any(v in public_text for v in banned)
    assert not OUT.exists(), 'No sobrescribir una entrega anterior'
    OUT.mkdir()
    dump(OUT / 'RESULTADOS_AGREGADOS.json', result)
    with (OUT / 'RESUMEN_POR_CARRERA.csv').open('w', encoding='utf-8-sig', newline='') as f:
        fields = ['carrera_UMAS', 'observaciones', *counts.keys()]
        w = csv.DictWriter(f, fieldnames=fields, delimiter=';', restval=0)
        w.writeheader(); w.writerows(career_rows)
    # Registro individual persistente fuera del repositorio.
    detail_path = PRIVATE / 'COLA_FASE1_CLASIFICADA.json'
    assert not detail_path.exists()
    dump(detail_path, [{'observacion_id': oid, 'categoria': status, 'motivo': reason,
                       'contexto': by[oid]['contexto_v17'], 'clasificacion': 'B/C; E adopción según categoría'}
                      for oid, (status, reason) in sorted(review.items())])
    detail_path.chmod(0o600)
    report = '''# Fase 1 — revisión de los104 pendientes V17

**B/C:** revisadas104 observaciones de58 personas, en12 códigos de carrera UMAS.
Se reutilizaron v7, los índices y las decisiones anteriores; no se repitió el universo histórico.

| Resultado exclusivo | Observaciones | Tratamiento |
|---|---:|---|
| Recuperación documental por regla anual existente | 5 | C: operaciones verificadas y registradas, todavía no promovidas al activo |
| Propuestas internas con evidencia concreta | 16 | E hasta aprobación de un criterio interno D acotado |
| Continuidad T2 entre anclas concordantes | 12 | E: validar/aprobar criterio separado |
| Evidencia temporal, atribución o versión pendiente | 71 | E: preguntas y fuentes precisadas |
| Total | 104 | Sin eliminaciones ni doble conteo |

## Hito1: evidencia reutilizada

**B/C:** las46 operaciones anteriores están incorporadas exactamente; una conserva
deliberadamente una homologación en plan rechazado sin código. Las119 equivalencias
FCU y45 asignaciones previas explican las164 correspondencias solo internas de v7.
No había un cierre olvidado en ese bloque que descontar otra vez.

## Hito2: hallazgos

**B/C:** nueve contextos de cinco personas usan un documento P en MU2025 y RUT en
PROMEDIOS. El puente explícito J/RUT↔BU/N_DOC de2025_carga y MU P+N_DOC es único.
BV no coincide con DV de MU, que está vacío: se conserva esa discrepancia, no se
rellena DV ni se utiliza coincidencia aproximada. Cinco contextos TPAS/TAMD cumplen
IDENTIDAD_FAMILIA_ANIO_CONTEXTO_DA_NO_MULTIPLE, implementada en
scripts/reproducir_puente_20261023.py:150–160. El lector de la línea135 omitía P.
Se comprobó identidad, familia/año, código único, contexto DA exacto y exclusividad.
Son dos recuperaciones I162S2C57J4V1 y tres I162S2C78J2V1. Los cuatro contextos
TLOG/IADM restantes requieren ubicar cambio de jornada; no se cierran por el puente.

**B/C/E:** las63 discrepancias de jornada se apoyaban en un corte DA posterior.
Las165 filas PROMEDIOS correspondientes repiten esa jornada; no está acreditado
que el campo esté historizado por asignatura. Las fotos T3 permiten separar:
14 propuestas con foto y MU del mismo año;12 T2 con anclas concordantes;10 T2 con
cambio todavía sin ubicar;8 T3 con versión corroborada solo después;2 T3 pendientes
de jornada/versión tras el puente documental;17 sin foto aplicable. Total63.

**B/C/E:** los otros34 contextos se separan en17 homologaciones anteriores al
ingreso declarado, dos propuestas IINF, seis con actividad A/R sin código del
expediente destino y nueve sin evaluación A/R. Las dos observaciones IINF20241
de2025 T2/T3 tienen actividad APROBADO, fotoT3 del mismo CODCLI/carrera/jornada,
ingreso2025P2 y código I162S2C1J4V2 documentado para el mismo contexto en2026.
La correspondencia interna propuesta no equivale a atribución documental2025.

**B/E:** las otras dos observaciones sin candidato también son homologaciones2025
de un expediente IINF con ingreso declarado2026. Junto a las17 anteriores son19;
no se demostró cuándo se reconocieron ni se eliminaron del universo.

## Hito3: cambios registrados y próximos actos

**C:** cinco operaciones de reparación quedaron registradas con estado antes/después,
evidencias y campos permitidos en el archivo privado OPERACIONES_REPARACION_CINCO_P.json.
No requieren una regla D nueva. Su incorporación al índice/edición candidata y
promoción se realizará en la consolidación, con QA específico. La función actual
aplicar_adjudicaciones permite solo cambios internos: no debe usarse sin adaptación
para esta reparación documental. No se editó el motor histórico.

**E/D:** las16 propuestas internas aún no están autorizadas:14 deT3 con foto y
código anual concordantes, y dos IINF con actividad/foto2025 y código2026. Las12
T2 necesitan un criterio adicional de continuidad; una foto posterior no descarta
por sí sola un cambio intermedio. Sus IDs y fuentes están únicamente en privado.

**B/C:** el activo sigue en2750/2854 y104 pendientes; histórico21725/24774 y3049.
Incorporar solo las cinco reparaciones llevaría a2755/2854 y99 pendientes; histórico
21730/24774 y3044. Son efectos calculados, no resultados ya promovidos ni tasas de retención.

## QA, conservación y reanudación

**C:** la clasificación cubre104/104 sin duplicados. Se reutilizaron269 filas de
PROMEDIOS,58 filas DA y las extracciones T3 compartidas. La ruta antigua DA en
Descargas ya no existe; se verificó la copia explícita de hash a0638483420324bcb2bba8bcbea426ca0a2be6162d1c8879569b507f409bdfc9.
Los cinco cambios candidatos conservan identidad, contexto, fuentes y denominadores.
No se regeneró Excel; no hubo prueba de apertura nativa ni recálculo en esta fase.

**C/E:** revisión ejecutada y resultados registrados; cobertura aún parcial.
La próxima acción es consolidar la reparación técnica y resolver las decisiones
internas concretas, sin reabrir los104 desde cero. No comenzar búsquedas nuevas
del histórico completo en este cierre de Fase1. Fuentes y preguntas por observación
permanecen en COLA_FASE1_CLASIFICADA.json y sus revisiones privadas.

**B/C:** V17, edición activa, bases y denominadores conservados. Sin commit, push
ni modificación de complementos. Los archivos compartibles no contienen identificadores.
'''
    # Solo correcciones de prosa explícitas; nunca reformatear códigos ni hashes.
    for old, new in {
        'los104':'los 104', 'revisadas104':'revisadas 104', 'de58':'de 58', 'en12':'en 12',
        'Hito1':'Hito 1', 'Hito2':'Hito 2', 'Hito3':'Hito 3', 'las46':'las 46',
        'Las119':'Las 119', 'FCU y45':'FCU y 45', 'las164':'las 164',
        'MU2025':'MU2025', 'de2025_carga':'de 2025_carga', 'línea135':'línea 135',
        'las63':'las 63', 'Las165':'Las 165', 'fotoT3':'foto T3', 'dos IINF':'dos IINF',
        '14 propuestas':'14 propuestas', ';12 T2':'; 12 T2', ';10 T2':'; 10 T2',
        ';8 T3':'; 8 T3', ';2 T3':'; 2 T3', ';17 sin':'; 17 sin', 'Total63':'Total 63',
        'otros34':'otros 34', 'en17':'en 17', 'de2025 T2/T3':'de 2025 T2/T3',
        'ingreso2025P2':'ingreso 2025-P2', 'en2026':'en 2026', 'documental2025':'documental 2025',
        'homologaciones2025':'homologaciones 2025', 'declarado2026':'declarado 2026',
        'las17':'las 17', 'son19':'son 19', 'las16':'las 16', ':14 deT3':': 14 de T3',
        'actividad/foto2025':'actividad/foto 2025', 'código2026':'código 2026',
        'Las12':'Las 12', 'en2750/2854':'en 2750/2854', 'y104':'y 104',
        'histórico21725/24774':'histórico 21725/24774', 'y3049':'y 3049',
        'a2755/2854':'a 2755/2854', 'y99':'y 99', '21730/24774 y3044':'21730/24774 y 3044',
        'cubre104/104':'cubre 104/104', 'reutilizaron269':'reutilizaron 269',
        'PROMEDIOS,58':'PROMEDIOS, 58', 'Fase1':'Fase 1',
    }.items():
        report = report.replace(old, new)
    assert not any(v in report for v in banned)
    (OUT / 'INFORME_FASE1.md').write_text(report)

    # Las fuentes privadas y sus procedimientos quedan referenciados, no copiados a Git.
    private_files = sorted(p for p in PRIVATE.iterdir() if p.is_file())
    manifest = {'fecha_hora': now, 'clasificacion': 'B/C evidencia y ejecución; E adopción pendiente',
                'plan_sha256': sha(AUDIT / 'PLAN_CIERRE_100_POR_CIENTO.md'),
                'edicion_activa': descriptor['edicion'], 'descriptor_sha256': active['sha256'],
                'entradas_privadas': [{'ruta': str(p), 'sha256': sha(p)} for p in private_files],
                'outputs': [{'archivo': p.name, 'sha256': sha(p)} for p in OUT.iterdir() if p.is_file()],
                'script': {'ruta': str(Path(__file__)), 'sha256': sha(__file__)},
                'politica': 'Solo agregados en repositorio. Identificadores y operaciones por observación exclusivamente fuera de Git.',
                'HEAD_antes': head, 'HEAD_despues': head, 'commit_push': False,
                'fuentes_y_denominadores_modificados': False, 'diccionario_activo_modificado': False}
    dump(OUT / 'MANIFEST_FASE1.json', manifest)
    print(json.dumps({'output': str(OUT), 'clasificacion': dict(counts), 'activo_conservado': True}, ensure_ascii=False))

if __name__ == '__main__':
    main()
