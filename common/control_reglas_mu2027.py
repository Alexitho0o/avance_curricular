"""Registro versionado de decisiones internas VIG. No exporta cargas SIES.

Autoridad funcional: docs/control_cambios_vig_mu2027.md. Los responsables son
declarados, no autenticados. Todas las consultas validan la cadena de hashes.
"""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib
import json
import re
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
REGISTRO = ROOT / 'data/reglas_negocio/mu2027'


class Bloqueo(ValueError):
    """Fallo explícito de integridad, contexto o autorización."""


def ahora():
    return datetime.now(ZoneInfo('America/Santiago')).isoformat()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def leer(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def guardar(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write('\n')


def exigir(condicion, mensaje):
    if not condicion:
        raise Bloqueo(mensaje)


def identidad(valor):
    exigir(isinstance(valor, str) and len(valor.strip()) >= 3,
           'Falta responsable/ejecutor humano o técnico declarado')
    exigir(valor.strip().upper() not in {'PENDIENTE', 'DESCONOCIDO', 'N/A'},
           'Responsable no identificado')
    return valor.strip()


def version_valida(version):
    exigir(isinstance(version, str) and re.fullmatch(r'[A-Za-z0-9_-]{1,80}', version),
           'Versión inválida')


def validar_reglas(reglas):
    exigir(reglas.get('proceso') == 'MU' and reglas.get('anio') == 2027,
           'Proceso/año diferente a MU2027')
    exigir(reglas.get('modo') == 'REVISION_INTERNA', 'Solo revisión interna, no carga SIES')
    pares = set()
    exigir(bool(reglas.get('equivalencias')), 'Catálogo vacío')
    for r in reglas['equivalencias']:
        k = (r['estado_umas'], r['situacion_umas'])
        exigir(all(isinstance(x, str) and x.strip() for x in k), 'Pareja incompleta')
        exigir(k not in pares, 'Pareja duplicada o ambigua')
        pares.add(k)
        exigir(r['resultado'] in (0, 1, 2, 'NO APLICA', 'PENDIENTE'), 'Resultado inválido')
        clase = 'E' if r['resultado'] == 'PENDIENTE' else 'D'
        exigir(r.get('clasificacion') == clase, 'Decisión interna no es norma oficial')
    return reglas


def alerta(registro, tipo, detalle):
    event = {'clasificacion': 'C', 'fecha_hora': ahora(), 'tipo': tipo, 'detalle': detalle}
    path = Path(registro) / 'alertas' / (uuid.uuid4().hex + '.json')
    guardar(path, event)
    print(f'ALERTA MU2027: {tipo}. {detalle}', file=sys.stderr)
    return path


def _verificar(registro, version=None, esperado=None):
    registro = Path(registro)
    if version is None:
        activo = leer(registro / 'activo.json')
        version, esperado = activo['version'], activo['manifest_sha256']
    exigir(bool(esperado) and re.fullmatch('[0-9a-f]{64}', esperado), 'Falta hash fijado de manifiesto')
    vista = set()
    primera = None
    while version is not None:
        version_valida(version)
        exigir(version not in vista, 'Cadena cíclica')
        vista.add(version)
        folder = registro / 'versiones' / version
        exigir(sha(folder / 'manifest.json') == esperado, 'Manifiesto alterado')
        m = leer(folder / 'manifest.json')
        exigir(m['version'] == version, 'Identidad de versión alterada')
        for nombre, digest in m['archivos_sha256'].items():
            exigir(Path(nombre).name == nombre, 'Ruta de versión inválida')
            exigir(sha(folder / nombre) == digest, 'Contenido congelado alterado: ' + nombre)
        exigir({'reglas.json', 'autorizacion.json', 'alerta.json'} <= set(m['archivos_sha256']),
               'Manifiesto incompleto')
        rules = validar_reglas(leer(folder / 'reglas.json'))
        auth = leer(folder / 'autorizacion.json')
        identidad(m['responsable_decision'])
        exigir(auth['responsable'] == m['responsable_decision'], 'Responsable no coincide')
        if primera is None:
            primera = (rules, m, esperado)
        anterior = m['anterior']
        version = anterior['version'] if anterior else None
        esperado = anterior['manifest_sha256'] if anterior else None
    return primera


def verificar(registro=REGISTRO, version=None, esperado=None, carga_sies=False):
    try:
        r = _verificar(registro, version, esperado)
        exigir(not carga_sies,
               'Carga SIES bloqueada: falta validar manual MU2027 y habilitar consumidor aprobado')
        return r
    except (KeyError, OSError, ValueError, TypeError) as e:
        # No se escriben datos de estudiantes ni contenido de archivos en alertas.
        alerta(registro, 'BLOQUEO', f'{type(e).__name__}: {e}')
        raise Bloqueo(str(e)) from e


def registrar(registro, version, reglas, autorizacion, ejecutor, anterior_esperado=None):
    """Promueve una versión nueva sin sobrescribir la anterior. Emite alerta."""
    registro = Path(registro)
    try:
        version_valida(version)
        validar_reglas(reglas)
        responsable = identidad(autorizacion.get('responsable'))
        identidad(ejecutor)
        for campo in ('motivo', 'referencia_autorizacion', 'decision_textual'):
            exigir(bool(str(autorizacion.get(campo, '')).strip()), 'Falta ' + campo)
        fecha = datetime.fromisoformat(autorizacion['fecha_registro'])
        exigir(fecha.tzinfo is not None, 'Fecha de autorización sin zona horaria')
        anterior, old = None, []
        if (registro / 'activo.json').exists():
            prev_rules, pm, ph = _verificar(registro)
            exigir(anterior_esperado == ph, 'Hash anterior no coincide; cambio concurrente/no autorizado')
            anterior = {'version': pm['version'], 'manifest_sha256': ph}
            old = prev_rules['equivalencias']
        else:
            exigir(anterior_esperado is None, 'No existe versión anterior')
        def index(rows):
            return {(r['estado_umas'], r['situacion_umas']): r for r in rows}
        before, after = index(old), index(reglas['equivalencias'])
        diff = [{'pareja': list(k), 'antes': before.get(k), 'despues': after.get(k)}
                for k in sorted(set(before) | set(after)) if before.get(k) != after.get(k)]
        folder = registro / 'versiones' / version
        folder.mkdir(parents=True, exist_ok=False)
        timestamp = ahora()
        guardar(folder / 'reglas.json', reglas)
        guardar(folder / 'autorizacion.json', autorizacion)
        guardar(folder / 'alerta.json', {'clasificacion': 'C', 'tipo': 'ALTA' if not anterior else 'CAMBIO_REGLAS',
            'fecha_hora': timestamp, 'responsable': responsable, 'ejecutor': ejecutor,
            'anterior': anterior, 'version_nueva': version, 'diferencias': diff})
        m = {'clasificacion': 'C', 'proceso': 'MU', 'anio': 2027, 'version': version,
             'fecha_hora': timestamp, 'responsable_decision': responsable,
             'ejecutor': ejecutor, 'anterior': anterior,
             'archivos_sha256': {n: sha(folder / n) for n in ['reglas.json', 'autorizacion.json', 'alerta.json']},
             'politica': 'D interno. Sin sustitución de MU2026 ni habilitación de carga SIES2027.'}
        guardar(folder / 'manifest.json', m)
        descriptor = {'version': version, 'manifest_sha256': sha(folder / 'manifest.json')}
        tmp = registro / ('.activo_' + uuid.uuid4().hex + '.json')
        guardar(tmp, descriptor)
        tmp.replace(registro / 'activo.json')
        alerta(registro, 'VERSION_REGISTRADA', version + '; responsable: ' + responsable)
        return descriptor
    except (KeyError, OSError, ValueError, TypeError) as e:
        alerta(registro, 'CAMBIO_RECHAZADO', f'{type(e).__name__}: {e}')
        raise Bloqueo(str(e)) from e


def consultar(estado, situacion, registro=REGISTRO, version=None, esperado=None):
    rules, m, mh = verificar(registro, version, esperado)
    # Comparación exacta: no asume equivalencias entre códigos, procesos ni personas.
    matches = [r for r in rules['equivalencias']
               if r['estado_umas'] == estado and r['situacion_umas'] == situacion]
    resultado = matches[0].copy() if matches else {'resultado': 'PENDIENTE', 'clasificacion': 'E'}
    if not matches:
        alerta(registro, 'PAREJA_SIN_REGLA', 'Pareja no catalogada; no se asigna VIG')
    return {**resultado, 'version': m['version'], 'manifest_sha256': mh,
            'aplicacion': 'REVISION_INTERNA; requiere estado/situación de la misma matrícula y corte'}


def ejecucion(destino, entradas, salidas, responsable, parametros,
              registro=REGISTRO, version=None, esperado=None):
    """Sella archivos ya producidos; no certifica corrección de su cálculo."""
    _, m, mh = verificar(registro, version, esperado)
    identidad(responsable)
    exigir(set(parametros) <= {'anio', 'periodo', 'fecha_referencia', 'alcance'}, 'Parámetro no permitido')
    exigir(parametros.get('anio') == 2027, 'Ejecución fuera de MU2027')
    exigir(bool(entradas) and bool(salidas), 'Faltan entradas/salidas')
    files = lambda paths: [{'ruta': str(Path(p).resolve()), 'sha256': sha(p)} for p in paths]
    record = {'clasificacion': 'C', 'fecha_hora': ahora(), 'responsable': responsable,
              'version_reglas': m['version'], 'manifest_sha256': mh,
              'controlador_sha256': sha(__file__), 'parametros': parametros,
              'entradas': files(entradas), 'salidas': files(salidas),
              'git_head': subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip(),
              'limite': 'Registro de integridad; no acredita aceptación SIES ni ejecución de un motor.'}
    guardar(destino, record)
    return record
