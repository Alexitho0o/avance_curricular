#!/usr/bin/env python3
"""Materializa solo evidencia y decisiones aprobadas; ninguna nueva adjudicación."""
import collections
import datetime
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common.diccionario_sies_seguimiento import aplicar_adjudicaciones, rut_normalizado, sha256

R = Path(__file__).resolve().parents[1]
VERSION = 'v1_20261023'
PUBLIC = R / 'data/diccionario_sies_seguimiento' / VERSION
CLOSURE = R / 'outputs/cierre_cinco_v1_programacion_20261023_111235/MANIFEST.json'
BASE = Path.home() / '.local/share/ipss/reproduccion_puente_20261023_004044/OBSERVACIONES_PRIVADAS.json'
MU = R / 'outputs/base_retencion_matricula_unificada_2022_2026/20260901_142342/BASE_RETENCION_MATRICULA_UNIFICADA_INFORMADA_SIES_2022_2026_20260901_142342.xlsx'
COMPONENTS = ['common/diccionario_sies_seguimiento.py', 'scripts/consultar_diccionario_sies_seguimiento.py',
              'scripts/retencion_intermedia_t2_t3/consultar_codigos_sies.py',
              'procesos/caracterizacion/scripts/consultar_diccionario_sies_seguimiento.py']


def write(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')


def main():
    import openpyxl
    if PUBLIC.exists():
        raise ValueError('Edición existente: no sobrescribir; crear otra edición explícita')
    now = datetime.datetime.now(ZoneInfo('America/Santiago'))
    private = Path.home() / '.local/share/ipss' / ('diccionario_sies_seguimiento_' + now.strftime('%Y%m%d_%H%M%S'))
    if subprocess.run(['git', '-C', str(private.parent), 'rev-parse', '--show-toplevel'], capture_output=True).returncode == 0:
        raise ValueError('Destino privado dentro de Git')
    if private.resolve().is_relative_to(R):
        raise ValueError('Destino privado dentro del proyecto')
    os.umask(0o077)
    manifest = json.loads(CLOSURE.read_text())
    inputs = dict(manifest['fuentes_hashes'])
    inputs[str(CLOSURE)] = sha256(CLOSURE)
    inputs[str(MU)] = '19cf33ae4925a7c13ec4745394141a297f4f64be4052a240cb0d2c42ffeb53bd'
    for name, h in manifest['privados_hashes'].items():
        inputs[str(Path(manifest['privado']) / name)] = h
    mu_manifest = MU.parent / 'MANIFEST_BASE_RETENCION_MU_2022_2026.json'
    inputs[str(mu_manifest)] = sha256(mu_manifest)
    for p, h in inputs.items():
        if sha256(p) != h:
            raise ValueError('Fuente alterada: ' + p)
    base = json.loads(BASE.read_text())
    changes_path = Path(manifest['privado']) / 'ADJUDICACIONES_ACUMULADAS.json'
    changes = json.loads(changes_path.read_text())['adjudicaciones']
    rows = aplicar_adjudicaciones(base, changes)
    def pending(field):
        missing = [r for r in rows if not r[field]]
        return {'observaciones': len(missing), 'personas': len({r['persona'] for r in missing})}
    assert len(rows) == 24774 and len({r['persona'] for r in rows}) == 5901
    assert len({(r['carrera'], r['CODCLI']) for r in rows}) == 6622
    assert pending('codigo_interno_adoptado') == {'observaciones': 3076, 'personas': 1750}
    assert pending('codigo_documental_atribuible') == {'observaciones': 3213, 'personas': 1838}
    private.mkdir(mode=0o700)
    database = private / 'DICCIONARIO_SIES.sqlite'
    db = sqlite3.connect(database)
    db.executescript('''
      CREATE TABLE observaciones (id INTEGER PRIMARY KEY, persona TEXT, codcli TEXT,
        plan TEXT, anio TEXT, periodo TEXT, carrera TEXT, sede TEXT, jornada TEXT, payload TEXT);
      CREATE UNIQUE INDEX contexto ON observaciones(persona,codcli,plan,anio,periodo,carrera,sede,jornada);
      CREATE INDEX expediente ON observaciones(codcli,persona);
      CREATE TABLE mu_anual (persona TEXT, anio TEXT, codigo TEXT, fuente TEXT, hoja TEXT, fila INTEGER, payload TEXT,
        UNIQUE(persona,anio,codigo,fuente,hoja,fila));
      CREATE INDEX identidad_anual ON mu_anual(persona,anio);
    ''')
    for r in rows:
        db.execute('INSERT INTO observaciones VALUES (?,?,?,?,?,?,?,?,?,?)', (
            r['observacion_id'], r['persona'], r['CODCLI'], r['plan'], r['ano'], r['periodo'],
            r['carrera'], r['sede_dimension'], r['jornada_sies'], json.dumps(r, ensure_ascii=False)))
        for e in r['evidencias_matricula']:
            db.execute('INSERT OR IGNORE INTO mu_anual VALUES (?,?,?,?,?,?,?)', (
                r['persona'], e['anio'], e['codigo'], e['fuente'], e['hoja'], e['fila'], json.dumps(e, ensure_ascii=False)))
    # Indexar toda la base anual, sin filtrar VIG, primer año ni carrera: no es denominador.
    wb = openpyxl.load_workbook(MU, read_only=True, data_only=True)
    ws = wb['BASE_RETENCION_MU']; it = iter(ws.values); heads = next(it)
    count_mu = collections.Counter(); without_key = collections.Counter()
    def val(x):
        return '' if x is None else str(int(x)) if isinstance(x, float) and x.is_integer() else str(x).strip()
    for rn, values in enumerate(it, 2):
        d = dict(zip(heads, values)); year = val(d['ANIO_INFORMADO']); count_mu[year] += 1
        if val(d['TIPO_DOC']).upper() not in ('R', '1', 'RUT', ''):
            without_key['TIPO_DOCUMENTO_NO_RUT'] += 1
            continue
        try:
            person = rut_normalizado(val(d['N_DOC']) + '-' + val(d['DV']))
        except ValueError:
            without_key['FORMATO_SIN_LLAVE_RUT'] += 1
            continue
        parts = [val(d[k]) for k in ['COD_SED', 'COD_CAR', 'JOR', 'VERSION']]
        if not all(x.isdigit() for x in parts):
            without_key['COMPONENTE_SIES_INCOMPLETO'] += 1
            continue
        code = 'I162S%sC%sJ%sV%s' % tuple(parts)
        e = {'codigo': code, 'anio': year, 'fuente': str(MU), 'hoja': ws.title, 'fila': rn,
             'tipo_doc_original': val(d['TIPO_DOC']), 'documento_original': val(d['N_DOC']),
             'dv_original': val(d['DV']), 'VIG': val(d['VIG']),
             'alcance': 'Base derivada anual; procedencia primaria en MANIFEST_BASE_RETENCION_MU_2022_2026.json'}
        db.execute('INSERT OR IGNORE INTO mu_anual VALUES (?,?,?,?,?,?,?)',
                   (person, year, code, str(MU), ws.title, rn, json.dumps(e, ensure_ascii=False)))
    wb.close()
    db.commit()
    assert db.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
    family_codes = collections.defaultdict(set)
    for (code,) in db.execute('SELECT DISTINCT codigo FROM mu_anual'):
        family_codes[code.rsplit('V', 1)[0]].add(code)
    multi = {f for f, codes in family_codes.items() if len(codes) > 1}
    focus = [r for r in rows if any(c.rsplit('V', 1)[0] in multi for c in
             r['codigos_anuales_documentados'] + r['candidatos_calculados'] if isinstance(c, str))]
    counts = {'universo_observaciones': len(rows), 'personas': 5901, 'expedientes_carrera_codcli': 6622,
              'codigo_documental_reutilizado': sum(bool(r['codigo_documental_atribuible']) for r in rows),
              'solo_correspondencia_interna_aprobada': sum(bool(r['codigo_interno_adoptado']) and not r['codigo_documental_atribuible'] for r in rows),
              'pendientes_internos': pending('codigo_interno_adoptado'), 'pendientes_documentales': pending('codigo_documental_atribuible'),
              'operaciones_aprobadas_integradas': len(changes), 'nuevas_asignaciones': 0,
              'filas_mu_por_anio_sin_filtrar_no_denominador': dict(count_mu),
              'filas_mu_sin_llave_rut_en_indice': dict(without_key),
              'familias_con_varias_versiones_en_evidencias': len(multi),
              'foco_versiones_multiples': {'observaciones': len(focus),
                  'codigo_reutilizable': sum(bool(r['codigo_interno_adoptado']) for r in focus),
                  'pendientes': sum(not r['codigo_interno_adoptado'] for r in focus)},
              'excepciones_por_estado': dict(collections.Counter(r['estado_interno'] for r in rows if not r['codigo_interno_adoptado']))}
    db.close()
    database.chmod(0o600)
    # Decisiones privadas y contexto completo quedan en el mismo paquete, no en Git.
    write(private / 'ADJUDICACIONES_INTEGRADAS.json', json.loads(changes_path.read_text()))
    for p, h in inputs.items():
        assert sha256(p) == h
    PUBLIC.mkdir(parents=True)
    write(PUBLIC / 'RESUMEN.json', counts)
    desc = {'edicion': VERSION, 'fecha_hora': now.isoformat(),
            'clasificacion': 'B fuentes; C integración; D decisiones ya aprobadas; E excepciones',
            'base_privada': {'ruta': str(database), 'sha256': sha256(database)},
            'componentes_sha256': {p: sha256(R / p) for p in COMPONENTS},
            'entradas_sha256': inputs,
            'procedencia_primaria_mu': str(mu_manifest),
            'reglas': ['REUTILIZAR_DOCUMENTAL_ANUAL_ATRIBUIDO', 'APLICAR_SOLO_ADJUDICACION_EXACTA_APROBADA',
                       'NO_PROPAGAR_VERSION_ENTRE_CONTEXTOS', 'CONSERVAR_CODIGO_COHORTE_SEPARADO_DEL_DESTINO'],
            'mutaciones_fuentes_denominadores': False, 'autoriza_carga_sies': False,
            'publicacion_remota': False, 'resumen': counts}
    write(PUBLIC / 'descriptor.json', desc)
    secrets = {r['persona'] for r in rows} | {r['CODCLI'] for r in rows}
    for f in PUBLIC.iterdir():
        text = f.read_text()
        assert not any(v and v in text for v in secrets)
    print(json.dumps({'descriptor': str(PUBLIC / 'descriptor.json'), 'resumen': counts}, ensure_ascii=False))


if __name__ == '__main__':
    main()
