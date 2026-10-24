"""Interfaz H7 portable: mismo H5 y estados en ambos consumidores.

La edición inicial no acredita reglas efectivas. No importa motores, no lee
fuentes personales y no consulta los catálogos operativos 2026/2027.
Contrato: docs/fase_7_integracion_consumidores.md en el repositorio de origen.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from types import ModuleType

VERSION = '2007_2026_h5_20261015'
DESCRIPTOR_SHA256 = '434559ec19d1809a8beb9b78919888b0218ba778ec4841d18dec5e3d6971ae47'
DIRECTORY = Path(__file__).resolve().parents[1] / 'gobernanza/sies/historico'
DESCRIPTOR = 'ACTIVO_2007_2026.json'
FILES = {'maestro.json', 'manifest_h5.json', 'resolutor.py', 'aceptacion_h6.json'}
UMAS_FIELDS = {'anio', 'periodo', 'regimen', 'codcarpr', 'nombre_interno',
               'plan_umas', 'sede_umas', 'jornada_umas'}
SIES_FIELDS = {'anio', 'codigo_unico'}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def verificar_paquete(directory=DIRECTORY):
    """Verifica bytes antes de ejecutar código; nunca carga un pyc alternativo."""
    directory = Path(directory).resolve()
    pointer = directory / DESCRIPTOR
    if pointer.is_symlink():
        raise ValueError('Descriptor simbólico no permitido')
    raw = pointer.read_bytes()
    if digest(raw) != DESCRIPTOR_SHA256:
        raise ValueError('SHA-256 del descriptor histórico distinto de la edición gobernada')
    descriptor = json.loads(raw)
    if (descriptor['schema_version'] != 1 or descriptor['version'] != VERSION
            or descriptor['periodo_objetivo'] != [2007, 2026]
            or descriptor['reglas_efectivas_acreditadas'] != 0
            or descriptor['asignacion_individual_habilitada'] is not False
            or set(descriptor['archivos']) != FILES):
        raise ValueError('Contrato histórico incompatible')
    blobs = {}
    for name, meta in descriptor['archivos'].items():
        relative = Path(meta['path'])
        path = directory / relative
        if (relative.is_absolute() or '..' in relative.parts or path.is_symlink()
                or not path.resolve().is_relative_to(directory)):
            raise ValueError('Ruta fuera del paquete histórico: ' + name)
        blobs[name] = path.read_bytes()
        if digest(blobs[name]) != meta['sha256']:
            raise ValueError('SHA-256 del componente histórico distinto: ' + name)
    manifest = json.loads(blobs['manifest_h5.json'])
    if (manifest['outputs']['maestro.json'] != digest(blobs['maestro.json'])
            or manifest['scripts_sha256']['common/equivalencias_historicas.py'] != digest(blobs['resolutor.py'])):
        raise ValueError('Maestro o resolvedor no corresponden a H5')
    acceptance = json.loads(blobs['aceptacion_h6.json'])
    if (acceptance['validacion_tecnica'] != 'APROBADA'
            or acceptance['asignacion_historica_automatica_habilitada'] is not False):
        raise ValueError('Aceptación H6 incompatible')
    return descriptor, blobs


class ConsultaHistorica:
    """Sesión sobre un snapshot verificado; devuelve copias, no el maestro mutable."""

    def __init__(self, directory=DIRECTORY):
        self._descriptor, blobs = verificar_paquete(directory)
        self._runtime = ModuleType('sies_historico_h5_verificado')
        # Ejecutar exactamente los bytes comprobados; sin importar otro repositorio.
        exec(compile(blobs['resolutor.py'], 'resolutor_h5_verificado.py', 'exec'),
             self._runtime.__dict__)
        maestro = json.loads(blobs['maestro.json'])
        if maestro.get('reglas_efectivas') != []:
            raise ValueError('Esta edición no admite reglas efectivas nuevas')
        self._maestro = self._runtime.validar_maestro(maestro)

    def trazabilidad(self):
        return {'version_paquete': VERSION, 'descriptor_sha256': DESCRIPTOR_SHA256,
                'maestro_sha256': self._descriptor['archivos']['maestro.json']['sha256'],
                'resolutor_sha256': self._descriptor['archivos']['resolutor.py']['sha256'],
                'periodo_objetivo': [2007, 2026],
                'asignacion_individual_habilitada': False}

    def consultar_umas(self, *, anio, periodo=None, regimen=None, codcarpr=None,
                       nombre_interno=None, plan_umas=None, sede_umas=None, jornada_umas=None):
        """Pasa las ocho claves a H5 sin completar ni reinterpretar parámetros."""
        result = self._runtime.resolver_umas(
            self._maestro, anio=anio, periodo=periodo, regimen=regimen,
            codcarpr=codcarpr, nombre_interno=nombre_interno, plan_umas=plan_umas,
            sede_umas=sede_umas, jornada_umas=jornada_umas)
        return copy.deepcopy(result)

    def consultar_sies(self, *, anio, codigo_unico=None):
        return copy.deepcopy(self._runtime.consultar_sies(
            self._maestro, anio=anio, codigo_unico=codigo_unico))

    def consultar_lote(self, consultas):
        """Lista de {tipo, parametros}; preserva orden y repetidos sin recibir nóminas."""
        if not isinstance(consultas, list):
            raise ValueError('Se exige una lista de consultas académicas')
        # Validar el lote completo antes de resolver cualquier consulta.
        for item in consultas:
            if not isinstance(item, dict) or set(item) != {'tipo', 'parametros'}:
                raise ValueError('Consulta debe contener solo tipo y parametros')
            kind, params = item['tipo'], item['parametros']
            if kind not in {'UMAS', 'SIES'} or not isinstance(params, dict):
                raise ValueError('Tipo o parámetros de consulta inválidos')
            allowed = UMAS_FIELDS if kind == 'UMAS' else SIES_FIELDS
            if 'anio' not in params or not set(params).issubset(allowed):
                raise ValueError('Año explícito y solo parámetros académicos autorizados')
        results = []
        for item in consultas:
            method = self.consultar_umas if item['tipo'] == 'UMAS' else self.consultar_sies
            results.append({'consulta': copy.deepcopy(item),
                            'resultado': method(**item['parametros'])})
        return {'trazabilidad': self.trazabilidad(), 'consultas': results,
                'cantidad_consultas': len(results)}
